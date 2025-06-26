from dataclasses import dataclass
from datetime import datetime

@dataclass
class ShortenedURL:
    code: str
    original_url: str
    created_at: datetime
    clicks: int = 0