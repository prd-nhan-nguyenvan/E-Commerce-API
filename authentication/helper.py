import secrets


def custom_token_generator(length: int = 30):
    token = secrets.token_urlsafe(length)
    return token
