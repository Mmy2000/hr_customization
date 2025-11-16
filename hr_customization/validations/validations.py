import re
from frappe import _


def validate_password_strength(password):
    """Validate password based on required rules."""

    # Minimum length 8
    if len(password) < 8:
        return _("Password must be at least 8 characters long.")

    # Uppercase letter
    if not re.search(r"[A-Z]", password):
        return _("Password must contain at least one uppercase letter.")

    # Lowercase letter
    if not re.search(r"[a-z]", password):
        return _("Password must contain at least one lowercase letter.")

    # Number
    if not re.search(r"[0-9]", password):
        return _("Password must contain at least one number.")

    # Allowed special characters
    if not re.search(r"[~$*&#@!]", password):
        return _("Password must contain at least one special character: ~ $ * & # @ !")

    # Passed all checks
    return None
