""" Application Settings """

import os
from pydantic import BaseSettings  # BaseModel,


class Settings(BaseSettings):
    """Main settings class"""

    app_name: str = "myapp"
    log_path: str = "./logs/"
    jwt_secret: str = ""
    jwt_algorithm: str = ""
    slack_webhook_url: str = ""
    slack_notify: bool = False
    listening_host: str = "0.0.0.0"
    listening_port: int = 8080
    registration_gift_offer_id: str = "2111742"
    zend_api: str = ""
    mock_zain_api: bool = False

    api_key: str = ""

    database_url: str = ""

    class Config:
        """Load config"""

        env_file = os.getenv("BACKEND_ENV", ".env")
        env_file_encoding = "utf-8"


settings = Settings()

# print(settings.dict())
