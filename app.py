import os
import sqlite3

from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request

from security import hash_password, verify_password

load_dotenv()

DATABASE = "recipes.db"
JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is missing from environment variables")

app = Flask(__name__)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

# AUTHENTICATION
# --------------------------------------------------

def token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization token required"}), 401

        token = auth_header.split(" ", 1)[1].strip()

        if not token:
            return jsonify({"error": "Authorization token required"}), 401

        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=["HS256"]
            )

            user_id = int(payload["sub"])
            role = payload["role"]

            if user_id <= 0 or not isinstance(role, str):
                raise ValueError("Invalid token claims")

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401

        except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
            return jsonify({"error": "Invalid token"}), 401

        g.current_user = payload
        g.user_id = user_id
        g.role = role

        return f(*args, **kwargs)

    return decorated

def owner_or_admin_required_for_recipe(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        recipe = get_db().execute(
            "SELECT id, owner_id FROM recipes WHERE id = ?",
            (kwargs["recipe_id"],)
        ).fetchone()

        if recipe is None:
            return jsonify({"error": "Recipe not found"}), 404

        is_owner = recipe["owner_id"] == g.user_id
        is_admin = g.role == "admin"

        if not (is_owner or is_admin):
            return jsonify({"error": "Forbidden"}), 403

        g.recipe = recipe

        return f(*args, **kwargs)

    return decorated

def recipe_to_dict(row):

    return {
        "id": row["id"],
        "title": row["title"],
        "ingredients": row["ingredients"],
        "instructions": row["instructions"],
        "is_public": bool(row["is_public"]),
        "owner_id": row["owner_id"]
    }


def user_to_dict(row):

    return {
        "id": row["id"],
        "username": row["username"],
        "email": row["email"]
    }

@app.get("/")
def hello():

    return jsonify({
        "message": "Recipe Box API",
        "recipes": "/recipes"
    })

@app.get("/recipes")
def list_recipes():

    rows = get_db().execute(
        """
        SELECT id, title, ingredients, instructions, is_public, owner_id
        FROM recipes
        WHERE is_public = 1
        ORDER BY id
        """
    ).fetchall()

    return jsonify([recipe_to_dict(row) for row in rows])


@app.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):

    row = get_db().execute(
        """
        SELECT id, title, ingredients, instructions, is_public, owner_id
        FROM recipes
        WHERE id = ? AND is_public = 1
        """,
        (recipe_id,)
    ).fetchone()

    if row is None:
        return jsonify({"error": "Can't make it if we can't find it"}), 404

    return jsonify(recipe_to_dict(row))


@app.route("/recipes", methods=["POST"])
@token_required
def create_recipe():
    print("METHOD:", request.method)
    print("RAW DATA:", request.data)
    print("JSON:", request.get_json(silent=True))

    data = request.get_json(silent=True)
    print("TYPE OF JSON:", type(data), "VALUE:", data)
    

    # Body must be JSON object
    if not isinstance(data, dict):
        return jsonify({"error": " Show your JSON body"}), 400

    title = data.get("title")
    ingredients = data.get("ingredients")

    # Title required, non-empty string
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "How do we make it?"}), 400

    # Ingredients required, non-empty string
    if not isinstance(ingredients, str) or not ingredients.strip():
        return jsonify({"error": "Gotta have the fixins"}), 400

    instructions = data.get("instructions", "")
    is_public = data.get("is_public", True)

    # Extra type checks
    if not isinstance(instructions, str):
        return jsonify({"error": "Instructions must be text"}), 400

    if not isinstance(is_public, bool):
        return jsonify({"error": "is_public must be true or false"}), 400

    db = get_db()

    try:
        cur = db.execute(
            """
            INSERT INTO recipes
            (title, ingredients, instructions, is_public, owner_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                title.strip(),
                ingredients.strip(),
                instructions,
                int(is_public),
                g.user_id,
            ),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "You want to make what? NO!"}), 409

    row = db.execute(
        """
        SELECT id, title, ingredients, instructions, is_public, owner_id
        FROM recipes WHERE id = ?
        """,
        (cur.lastrowid,),
    ).fetchone()

    return jsonify(recipe_to_dict(row)), 201

@app.patch("/recipes/<int:recipe_id>")
@token_required
@owner_or_admin_required_for_recipe
def update_recipe(recipe_id):

    data = request.get_json(silent=True)
    

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "A JSON body is required"}), 400

    fields = []
    values = []

    allowed_fields = {
        "title": str,
        "ingredients": str,
        "instructions": str,
        "is_public": bool
    }

    for column, expected_type in allowed_fields.items():

        if column not in data:
            continue

        value = data[column]

        if not isinstance(value, expected_type):
            return jsonify({
                "error": f"Invalid value for {column}"
            }), 400

        if column in ("title", "ingredients") and not value.strip():
            return jsonify({
                "error": f"{column} cannot be empty"
            }), 400

        fields.append(f"{column} = ?")

        if column == "is_public":
            values.append(int(value))
        else:
            values.append(value.strip() if column in ("title", "ingredients") else value)

    if not fields:
        return jsonify({"error": "If it ain't broke don't fix it"}), 400

    values.append(g.recipe["id"])

    db = get_db()

    try:

        db.execute(
            f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?",
            values
        )

        db.commit()

    except sqlite3.IntegrityError:
        return jsonify({"error": "Can't fix that"}), 409

    row = db.execute(
        """
        SELECT id, title, ingredients, instructions, is_public, owner_id
        FROM recipes WHERE id = ?
        """,
        (g.recipe["id"],)
    ).fetchone()

    return jsonify(recipe_to_dict(row))

@app.delete("/recipes/<int:recipe_id>")
@token_required
@owner_or_admin_required_for_recipe
def delete_recipe(recipe_id):

    db = get_db()

    db.execute(
        "DELETE FROM recipes WHERE id = ?",
        (g.recipe["id"],)
    )

    db.commit()

    return "", 204

@app.post("/register")
def register():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Show your JSON body"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not isinstance(username, str) or not username.strip():
        return jsonify({"error": "Username is required"}), 400

    if len(username.strip()) > 50:
        return jsonify({"error": "Username is too long, we ran out of letters"}), 400

    if not isinstance(email, str) or "@" not in email.strip():
        return jsonify({"error": "A valid email is required"}), 400

    if not isinstance(password, str) or len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    username = username.strip()
    email = email.strip().lower()

    db = get_db()

    try:

        cur = db.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (username, email, hash_password(password))
        )

        db.commit()

    except sqlite3.IntegrityError:
        return jsonify({"error": "They are already here!"}), 409

    row = db.execute(
        "SELECT id, username, email FROM users WHERE id = ?",
        (cur.lastrowid,)
    ).fetchone()

    return jsonify(user_to_dict(row)), 201

@app.post("/login")
def login():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Where is your JSON body"}), 400

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not username.strip():
        return jsonify({"error": "Username is required"}), 400

    if not isinstance(password, str) or not password:
        return jsonify({"error": "Password is required"}), 400

    db = get_db()

    user = db.execute(
        """
        SELECT id, username, password_hash, role
        FROM users
        WHERE username = ?
        """,
        (username.strip(),)
    ).fetchone()

    auth_error = jsonify({
        "error": "Is you really who you says you is?"
    }), 401

    if user is None:
        return auth_error

    if not verify_password(user["password_hash"], password):
        return auth_error

    payload = {
        "sub": str(user["id"]),
        "role": user["role"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm="HS256"
    )

    return jsonify({
        "message": "You Freakin made it in",
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"]
        }
    }), 200

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true"
    )

