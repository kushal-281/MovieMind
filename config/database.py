import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


load_dotenv()

# Change these later via `.env` (recommended)
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Kushal@2004")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "movieMind")

# Localhost credentials of MySQL
#
# Note: using URL.create avoids issues with special characters in password (e.g. @)
engine = create_engine(
    URL.create(
        "mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=3306,
        database=DB_NAME,
    )
)

# If you deploy, you can also provide full URL via env:
# DATABASE_URL="mysql+pymysql://user:pass@host:3306/movieMind"
# (uncomment below if you prefer a single connection string)
# db_url = os.getenv("DATABASE_URL")
# if db_url:
#     engine = create_engine(db_url)


_schema_ready = False


def ensure_schema():
    """Add columns / tables used by the app if missing (safe to call repeatedly)."""
    global _schema_ready
    if _schema_ready:
        return
    try:
        with engine.begin() as conn:
            try:
                conn.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN total_site_seconds INT DEFAULT 0"
                    )
                )
            except Exception:
                pass
            try:
                conn.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS contact_messages (
                            message_id INT AUTO_INCREMENT PRIMARY KEY,
                            user_id INT NULL,
                            name VARCHAR(100) NOT NULL,
                            email VARCHAR(180) NOT NULL,
                            subject VARCHAR(200),
                            message TEXT NOT NULL,
                            status VARCHAR(20) DEFAULT 'new',
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
                        )
                        """
                    )
                )
            except Exception:
                pass
            try:
                conn.execute(
                    text(
                        "ALTER TABLE contact_messages ADD COLUMN admin_reply TEXT NULL"
                    )
                )
            except Exception:
                pass
            try:
                conn.execute(
                    text(
                        "ALTER TABLE contact_messages ADD COLUMN replied_at DATETIME NULL"
                    )
                )
            except Exception:
                pass
            try:
                conn.execute(
                    text(
                        "ALTER TABLE contact_messages ADD COLUMN replied_by INT NULL"
                    )
                )
            except Exception:
                pass
            try:
                conn.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS chat_logs (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            user_id INT,
                            query TEXT NOT NULL,
                            response TEXT NOT NULL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                        )
                        """
                    )
                )
            except Exception:
                pass
            try:
                conn.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS faqs (
                            faq_id INT AUTO_INCREMENT PRIMARY KEY,
                            question VARCHAR(400) NOT NULL,
                            answer TEXT NOT NULL,
                            is_active TINYINT(1) DEFAULT 1,
                            created_by INT NULL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                            FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
                        )
                        """
                    )
                )
            except Exception:
                pass
            try:
                conn.execute(
                    text(
                        "ALTER TABLE movies ADD COLUMN is_approved TINYINT(1) DEFAULT 1"
                    )
                )
            except Exception:
                pass
            try:
                conn.execute(
                    text(
                        "ALTER TABLE movies ADD COLUMN submitted_by INT NULL"
                    )
                )
            except Exception:
                pass
            try:
                conn.execute(
                    text(
                        """
                        ALTER TABLE movies
                        ADD CONSTRAINT fk_movies_submitted_by
                        FOREIGN KEY (submitted_by) REFERENCES users(user_id) ON DELETE SET NULL
                        """
                    )
                )
            except Exception:
                pass
            try:
                conn.execute(
                    text(
                        "ALTER TABLE ratings ADD UNIQUE KEY uq_user_movie_rating (user_id, movie_id)"
                    )
                )
            except Exception:
                pass
        _schema_ready = True
    except Exception as e:
        err = str(e).lower()
        if "duplicate" in err or "1060" in err:
            _schema_ready = True
