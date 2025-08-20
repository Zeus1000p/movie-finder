import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TMDB_KEY = os.getenv("TMDB_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"

def fetch_json(endpoint, params=None):
    if params is None:
        params = {}
    params["api_key"] = TMDB_KEY
    res = requests.get(f"{TMDB_BASE}{endpoint}", params=params)
    res.raise_for_status()
    return res.json()

@app.route("/related-movies", methods=["GET"])
def related_movies():
    title = request.args.get("title")
    if not title:
        return jsonify({"error": "Please provide a movie title (?title=...)" }), 400

    search = fetch_json("/search/movie", {"query": title})
    if not search.get("results"):
        return jsonify({"error": "Movie not found"}), 404
    movie = search["results"][0]

    credits = fetch_json(f"/movie/{movie['id']}/credits")
    director = next((m for m in credits["crew"] if m.get("job") == "Director"), None)
    actors = credits["cast"][:3]

    related_movies = set()

    if director:
        dir_movies = fetch_json(f"/person/{director['id']}/movie_credits")
        for m in dir_movies.get("crew", []):
            if m.get("job") == "Director" and m["id"] != movie["id"]:
                related_movies.add(m["title"])

    for actor in actors:
        act_movies = fetch_json(f"/person/{actor['id']}/movie_credits")
        for m in act_movies.get("cast", []):
            if m["id"] != movie["id"]:
                related_movies.add(m["title"])

    return jsonify({
        "input_movie": movie["title"],
        "related_movies": sorted(list(related_movies))
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
