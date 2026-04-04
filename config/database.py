from sqlalchemy import create_engine

DB_USER = "root"
DB_PASSWORD = "Kushal%402004"   # FIXED
DB_HOST = "localhost"
DB_NAME = "movieMind"

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"
)