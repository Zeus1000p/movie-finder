import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"

def fetch_json(endpoint, params=None):
    if params is None:
        params = {}
    params["api_key"] = TMDB_API_KEY
    res = requests.get(f"{TMDB_BASE}{endpoint}", params=params)
    res.raise_for_status()
    return res.json()

def get_related_movies(movie_id, top_actors=3, max_movies=100):
    credits = fetch_json(f"/movie/{movie_id}/credits")
    director = next((c for c in credits["crew"] if c["job"]=="Director"), None)
    actors = credits["cast"][:top_actors]

    related = []

    # Movies by director
    if director:
        dir_movies = fetch_json(f"/person/{director['id']}/movie_credits")
        for m in dir_movies.get("crew", []):
            if m.get("job")=="Director" and m["id"] != movie_id:
                related.append({"title": m["title"], "connection": "Director"})
                if len(related) >= max_movies: break

    # Movies by actors
    for actor in actors:
        if len(related) >= max_movies: break
        act_movies = fetch_json(f"/person/{actor['id']}/movie_credits")
        for m in act_movies.get("cast", []):
            if m["id"] != movie_id:
                related.append({"title": m["title"], "connection": f"Actor: {actor['name']}"})
                if len(related) >= max_movies: break

    return related[:max_movies], director, actors

@app.route("/", methods=["GET","POST"])
def index():
    movie_info = None
    if request.method=="POST":
        movie_name = request.form.get("movie_name")
        search = fetch_json("/search/movie", {"query": movie_name})
        if search.get("results"):
            movie = search["results"][0]
            related, director, actors = get_related_movies(movie["id"])
            movie_info = {
                "input_movie": movie["title"],
                "director": director["name"] if director else "Unknown",
                "actors": actors,
                "related_movies": related
            }
    return render_template("index.html", movie_info=movie_info)

@app.route("/actor-movies/<int:actor_id>")
def actor_movies(actor_id):
    credits = fetch_json(f"/person/{actor_id}/movie_credits")
    movies = [{"title": m["title"], "release_date": m.get("release_date","")} for m in credits.get("cast", [])]
    return jsonify(movies)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
