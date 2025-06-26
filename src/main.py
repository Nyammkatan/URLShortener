from flask import Flask, request, redirect, jsonify, abort
from http import HTTPStatus
from utils import generate_code
from url_repository import URLRepository
from models import ShortenedURL
from datetime import datetime
from consts import MISSING_URL_ERROR, UNIQUE_SHORT_CODE_GENERATION_ERROR, DUPLICATE_CODE_WARNING, NOT_FOUND_WARNING
import sqlite3

MAX_CODE_GENERATION_TRIES = 3
app = Flask(__name__)
urls_repo = URLRepository()

metrics = {
    "requests_total_for_shortening": 0,
    "shortening_errors_count": 0,
}


@app.route('/api/shorten', methods=['POST'])
def shorten():
    metrics["requests_total_for_shortening"] += 1

    data = request.get_json()
    original_url = data.get('url')
    
    if not original_url:
        metrics["shortening_errors_count"] += 1
        return jsonify({"error": MISSING_URL_ERROR}), HTTPStatus.BAD_REQUEST

    for _ in range(MAX_CODE_GENERATION_TRIES):
        try:
            code = generate_code()
            shortened_url = ShortenedURL(
                code=code,
                original_url=original_url,
                created_at=datetime.now(),
                clicks=0
            )
            urls_repo.save(shortened_url)
            break
        except sqlite3.IntegrityError:
            # Code already exists — retry with a new one
            print(DUPLICATE_CODE_WARNING.format(code))
            continue
    else:
        # All attempts failed
        metrics["shortening_errors_count"] += 1
        return jsonify({'error': UNIQUE_SHORT_CODE_GENERATION_ERROR}), HTTPStatus.INTERNAL_SERVER_ERROR

    return jsonify({
        "code": code,
        "short_url": f"{request.host_url}{code}"
    }), HTTPStatus.OK

@app.route('/<code>')
def redirect_to(code: str):
    record = urls_repo.get(code)
    if not record:
        print(NOT_FOUND_WARNING.format(code))
        abort(HTTPStatus.NOT_FOUND)
    # for statistics purposes
    urls_repo.increment_clicks(code)
    # redirect
    return redirect(record.original_url, code=HTTPStatus.MOVED_PERMANENTLY)

@app.route('/api/stats/<code>')
def stats(code: str):
    record = urls_repo.get(code)
    if not record:
        print(NOT_FOUND_WARNING.format(code))
        abort(HTTPStatus.NOT_FOUND)
    return jsonify({
        "code": record.code,
        "original_url": record.original_url,
        "created_at": record.created_at.isoformat(),
        "clicks": record.clicks
    })

@app.route('/metrics')
def metrics_view():
    return jsonify(metrics), HTTPStatus.OK

if __name__ == "__main__":
    app.run()
