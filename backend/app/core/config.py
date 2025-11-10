import os

class Settings:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('MARIADB_USER','irail')}:"
        f"{os.getenv('MARIADB_PASSWORD','irailpwd')}@"
        f"{os.getenv('MARIADB_HOST','db')}:3306/"
        f"{os.getenv('MARIADB_DATABASE','irail')}"
    )

settings = Settings()
