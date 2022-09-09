def check_email(email):
    if email and isinstance(email, str) and email.count("@") == 1:

        right_part = email.split("@")[-1]

        if "." in right_part:
            return True

    return False
