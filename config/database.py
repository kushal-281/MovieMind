from sqlalchemy import create_engine, text

DB_USER = "root"
DB_PASSWORD = "Kushal%402004"   # FIXED
DB_HOST = "localhost"
DB_NAME = "movieMind"

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"
)


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
        _schema_ready = True
    except Exception as e:
        err = str(e).lower()
        if "duplicate" in err or "1060" in err:
            _schema_ready = True
