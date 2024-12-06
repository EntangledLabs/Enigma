import secrets, string

def create_pw(length: int):
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password