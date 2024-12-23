import bcrypt
import base64


def hashPassword(password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return base64.b64encode(hashed_password).decode("utf-8")


def verifyPassword(stored_password, input_password):
    if isinstance(stored_password, str):
        stored_password_bytes = base64.b64decode(stored_password.encode("utf-8"))
    return bcrypt.checkpw(input_password.encode("utf-8"), stored_password_bytes)