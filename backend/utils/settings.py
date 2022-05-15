""" Application Settings """

import os
from pydantic import BaseSettings  # BaseModel,
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('secrets.env')
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv('DATABASE_URL')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')

if DATABASE_URL == None:
    print('PLEASE CREATE A SECRET FILE FROM sample.env')

class Settings(BaseSettings):
    """Main settings class"""

    app_name: str = "myapp"
    log_path: str = "./logs/"
    jwt_secret: str = ""
    jwt_algorithm: str = JWT_ALGORITHM
    slack_webhook_url: str = ""
    slack_notify: bool = False
    listening_host: str = "0.0.0.0"
    listening_port: int = 8080
    registration_gift_offer_id: str = "2111742"
    zend_api: str = ""
    mock_zain_api: bool = False

    api_key: str = ""

    database_url: str = DATABASE_URL

    class Config:
        """Load config"""

        env_file = os.getenv("BACKEND_ENV", ".env")
        env_file_encoding = "utf-8"


settings = Settings()

# print(settings.dict())
