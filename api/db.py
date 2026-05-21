import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


load_dotenv()


def get_engine():
    """
    MovieMind API DB engine.

    Change these env vars later (recommended):
    - DB_USER
    - DB_PASSWORD
    - DB_HOST
    - DB_NAME
    """

    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    name = os.getenv("DB_NAME", "movieMind")

    return create_engine(
        URL.create(
            "mysql+pymysql",
            username=user,
            password=password,
            host=host,
            port=3306,
            database=name,
        )
    )


engine = get_engine()

