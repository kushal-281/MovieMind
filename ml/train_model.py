import pandas as pd
from sqlalchemy import create_engine
import joblib
import os

# -------- DB CONNECTION --------
engine = create_engine("mysql+pymysql://root:Kushal%402004@localhost/moviemind")

# -------- BASE PATH (IMPORTANT FIX) --------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # MovieMind folder
DATA_PATH = os.path.join(BASE_DIR, "data")

# -------- CREATE DATA FOLDER --------
os.makedirs(DATA_PATH, exist_ok=True)

# -------- FETCH DATA --------
movies = pd.read_sql("""
    SELECT movie_id, title, overview
    FROM movies
""", engine)

genres = pd.read_sql("""
    SELECT mg.movie_id, g.genre_name
    FROM movie_genres mg
    JOIN genres g ON mg.genre_id = g.genre_id
""", engine)

actors = pd.read_sql("""
    SELECT ma.movie_id, a.name
    FROM movie_actors ma
    JOIN actors a ON ma.actor_id = a.actor_id
""", engine)

# -------- GROUP GENRES --------
genres = genres.groupby("movie_id")["genre_name"] \
               .apply(lambda x: " ".join(set(x))) \
               .reset_index()

# -------- GROUP ACTORS --------
actors = actors.groupby("movie_id")["name"] \
               .apply(lambda x: " ".join(set(x))) \
               .reset_index()

# -------- MERGE ALL --------
df = movies.merge(genres, on="movie_id", how="left")
df = df.merge(actors, on="movie_id", how="left")

# -------- SAFETY --------
df["genre_name"] = df["genre_name"].fillna('')
df["name"] = df["name"].fillna('')

# -------- CREATE TAGS --------
df["tags"] = (
    df["overview"] + " " +
    df["genre_name"] + " " +
    df["name"]
).str.lower()

# -------- SAVE FILE --------
file_path = os.path.join(DATA_PATH, "processed_data.pkl")
joblib.dump(df, file_path)

print("✅ PKL file created at:", file_path)