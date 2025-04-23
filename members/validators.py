def validate_phone(num):
    number = num.replace(" ","")
    if not number:
        return None
    if not number.startswith('+91'):
        number=f'+91{number}'
    num_len  = len(number)
    if num_len!=13:
        return None
    return number

def has_special_char(password):
    return not password.isalnum()
def has_upper(password):
    has_capital = any(char.isupper() for char in password)
    return has_capital

def is_strong_password(psword):
    password=str(psword)
    if len(password)>=8 and has_special_char(password) and has_upper(password):
        return password
    return False
