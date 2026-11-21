from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """Generate a secure 
fpassword hash."""
    return generate_password_hash(password)


def verify_password(stored_hash: str, candidate_password: str) -> bool:
    """Verify a password against its stored hash."""
    return check_password_hash(stored_hash, candidate_password)


if __name__ == "__main__":

    hashed = hash_password("demo_password098")

    print("Hash:", hashed)

    print(
        "Correct password:",
        verify_password(hashed, "demo_password098")
    )

    print(
        "Incorrect password:",
        verify_password(hashed, "wrong_demo123")
    )



