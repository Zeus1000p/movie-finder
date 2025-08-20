import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")  # Make sure to set this in Render/GitHub
TMDB_BASE_URL = "https://api.themoviedb.org/3"


def search_movie(title):
    """Search for a movie by title and return its details."""
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": title}
    response = requests.get(url, params=params).json()
    results = response.get("results", [])
    return results[0] if results else None


def get_movie_credits(movie_id):
    """Get cast and crew for a movie."""
    url = f"{TMDB_BASE_URL}/movie/{movie_id}/credits"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params).json()
    return response


def get_movies_by_person(person_id):
    """Get movies associated with an actor or director."""
    url = f"{TMDB_BASE_URL}/person/{person_id}/movie_credits"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params).json()
    cast = response.get("cast", [])
    crew = response.get("crew", [])
    return cast + crew


@app.route("/related-movies", methods=["GET"])
def related_movies():
    title = request.args.get("title")
    if not title:
        return jsonify({"error": "Please provide a movie title with ?title=MovieName"}), 400

    movie = search_movie(title)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404

    movie_id = movie["id"]

    credits = get_movie_credits(movie_id)

    # Director
    director = next((c["name"] for c in credits.get("crew", []) if c["job"] == "Director"), "Unknown")

    # Main 5 actors
    actors = [a["name"] for a in credits.get("cast", [])[:5]]

    # Collect related movies from director + actors
    related_movies = set()

    # Movies by director
    director_obj = next((c for c in credits.get("crew", []) if c["job"] == "Director"), None)
    if director_obj:
        for m in get_movies_by_person(director_obj["id"]):
            if m.get("title") and m["title"].lower() != title.lower():
                related_movies.add(m["title"])

    # Movies by actors
    for actor in credits.get("cast", [])[:5]:  # Limit to first 5 actors
        for m in get_movies_by_person(actor["id"]):
            if m.get("title") and m["title"].lower() != title.lower():
                related_movies.add(m["title"])

    return jsonify({
        "input_movie": title,
        "director": director,
        "actors": actors,
        "related_movies": list(related_movies)[:100]  # Limit to 100 movies
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
