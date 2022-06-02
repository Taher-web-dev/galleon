# URL = r"^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$"  # URL format
TITLE = r"^(\w{0,25}\s?\w{0,25}){1,3}$"  # String consists of only letters, digits, and spaces
DESC = (
    r"^(\w*\s?\w*){1,50}$"  # Long string consists of only letters, digits, and spaces
)
STRING = r"^\w{1,50}$"  # Only digits and letters between 1 and 50
DIGITS = r"^\d{1,50}$"  # Only digits between 1 and 50
MSISDN = r"^[1-9]\d{9}$"  # Exactly 10 digits, not starting with zero
PASSWORD = r"^[\w.@#$%^&+=\-\s]{8,}$"  # Password format, at least 8 chars
