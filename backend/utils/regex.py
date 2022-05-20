URL = r"^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$"  # URL format
TITLE = r"^(\w{0,25}\s?\w{0,25}){1,3}$"  # String consists of only letters, digits, and spaces
DESC = (
    r"^(\w*\s?\w*){1,50}$"  # Long string consists of only letters, digits, and spaces
)
STRING = r"^\w{1,50}$"  # Only digits and letters between 1 and 50
DIGITS = r"^\d{1,50}$"  # Only digits between 1 and 50
MSISDN = r"^\d{8,15}$"  # Only digits between 8 and 15
PASSWORD = r"^[\w.@#$%^&+=\-\s]{8,}$"  # Password format, at least 8 chars
EMAIL = r"^[\w\-?_?\.]*@[\w\-?_?\w]*\.\w*$"  # Email format
