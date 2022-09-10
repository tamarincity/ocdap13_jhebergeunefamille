def check_email(email):
    if email and isinstance(email, str) and email.count("@") == 1:

        if "@." in email:
            return False

        if email.endswith(".") or email.endswith("@"):
            return False

        right_part = email.split("@")[-1]

        if "." in right_part:
            return True

    return False
