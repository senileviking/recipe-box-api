import sqlite3

USERNAME = "Pepper"

conn = sqlite3.connect("recipes.db")
cur = conn.execute(
    """
    INSERT INTO recipes (title, ingredients, instructions, is_public, owner_id)
    SELECT 'I did it burrito', 'tortilla, beans, cheese', 'roll it', 1, id
    FROM users
    WHERE username = ?
    """,
    (USERNAME,),
)
conn.commit()
print("Inserted recipe ID:", cur.lastrowid if cur.rowcount else None)
conn.close()