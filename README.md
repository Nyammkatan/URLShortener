# URLShortener
Simple web service that takes a long URL and returns a short URL.

Main tech used: Python 3.10.11 with Flask for simplicity
Database: file based SQLite
Testing: pytest

# Main api:
- POST /api/shorten
Create a short URL from a long one.
- GET /[code]
Redirect to the original URL.
- GET /api/stats/[code]
Retrieve statistics for a short code (click count, creation date, etc).
- Get /metrics
Returns basic shortening metrics

# Design Choices:
- Short Code Generation - Random 5-character alphanumeric strings. Retries up to 3 times in case of duplicate.
- Caching layer stores frequently accessed short codes to reduce DB reads. In-memory dictionary-based cache (self.cache) inside the repository class. Speeds up redirection of hot URLs.
- SQLite for simplicity.
- Auto-creates table if missing during runtime (if file was deleted at runtime).

# Scalability Considerations (If this were production)
Replace SQLite with a scalable database server. (MySql for example)
Use Redis for caching shortened urls.
Add Prometheus /metrics.

# Notes:
- I chose to generate a new code for each submitted URL, even if it's identical to a previously shortened one. This keeps the implementation simple for the demo.
- In a real system, I'd consider detecting duplicates and returning existing codes, while also enforcing uniqueness at the database level.
- Base62 + auto-incremented IDs can also be used to eliminate code duplicate issue entirely.
- I used SQLite for simplicity and fast setup in this demo. While it doesn't support horizontal scalability or concurrent writes across multiple servers, it demonstrates the API logic.

# Note on OOP Practices:
While the scope of the assignment is relatively small, I applied basic OOP principles to keep the code modular and maintainable. For example:
- URLRepository class encapsulates all DB logic.
- ShortenedURL model represents the main entity.
Given the scale, heavier OOP patterns like inheritance, abstract interfaces, or service layers were not necessary for the assignment.
However, the design is extensible and it would be easy to expand this with more responsibilities like MetricsService class or CacheManager etc.

# Instructions

1. Install simple python environment and dependencies
`python -m venv env`
`pip install -r requirements.txt`

2. Run the server with commands:
`flask --app src/main run`
or 
`python -m flask --app src/main run`

3. Run tests with command:
`pytest`