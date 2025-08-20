# 🎬 Movie Related API (TMDB Powered)

This is a simple Flask API that lets you input a movie and get a list of movies that share **actors or directors** in common, powered by [TMDB](https://www.themoviedb.org/).

No database is required — all data is fetched live from TMDB.

---

## ✨ Features
- Input a movie title or ID
- Fetches cast & crew (actors + directors) from TMDB
- Returns other movies that share at least one actor or director
- Lightweight (Flask + Requests)
- Ready for free deployment on [Render](https://render.com/)

---

## 🚀 Deploy on Render

1. Fork or upload this repo to your own GitHub account.
2. Create a new **Web Service** on [Render](https://render.com/).
3. Connect it to your GitHub repo.
4. Render will read the `render.yaml` file and set up everything.
5. Add an environment variable in Render:
   - **Key**: `TMDB_KEY`  
   - **Value**: your TMDB API key (get it from [TMDB Developer](https://developer.themoviedb.org/))
6. Deploy 🚀

---

## ▶️ Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/movie-related-api.git
cd movie-related-api
