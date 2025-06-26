import sqlite3
from datetime import datetime
from models import ShortenedURL

# sqlite simple approach
# 4 columns table "urls" - 1. code, 2. original_url, 3. created_at, 4. clicks

class URLRepository:
    
    def __init__(self, db_path="urls.db"):
        self.db_path = db_path
        self.init_db()
        self.cache = {}
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def execute_create_table_query(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                code TEXT PRIMARY KEY,
                original_url TEXT NOT NULL,
                created_at TEXT NOT NULL,
                clicks INTEGER DEFAULT 0
            )
        """)

    def execute_save_doc_query(self, doc: ShortenedURL, conn):
        conn.execute("""
            INSERT INTO urls (code, original_url, created_at, clicks)
            VALUES (?, ?, ?, ?)
        """, (doc.code, doc.original_url, doc.created_at.isoformat(), doc.clicks))
    
    def init_db(self):
        with self.get_connection() as conn:
            self.execute_create_table_query(conn)
            
    def save(self, doc: ShortenedURL):
        try:
            with self.get_connection() as conn:
                self.execute_save_doc_query(doc, conn)
        except sqlite3.OperationalError as e:
            # If table/db was deleted during runtime — recreate it and retry once
            if "no such table" in str(e):
                with self.get_connection() as conn:
                    self.execute_create_table_query(conn)
                    self.execute_save_doc_query(doc, conn)

    def get(self, code: str) -> ShortenedURL | None:
        if code in self.cache:
            return self.cache[code]
        with self.get_connection() as conn:
            row = conn.execute("""
                SELECT code, original_url, created_at, clicks
                FROM urls WHERE code = ?
            """, (code,)).fetchone()
        if row:
            shortened_url  = ShortenedURL(
                code=row[0],
                original_url=row[1],
                created_at=datetime.fromisoformat(row[2]),
                clicks=row[3]
            )
            self.cache[code] = shortened_url 
            return shortened_url
        return None

    def increment_clicks(self, code: str):
        with self.get_connection() as conn:
            conn.execute("UPDATE urls SET clicks = clicks + 1 WHERE code = ?", (code,))
        if code in self.cache:
            self.cache[code].clicks += 1