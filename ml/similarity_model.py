import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------- LOAD FILE --------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(BASE_DIR, "data", "processed_data.pkl")

df = joblib.load(file_path)

# -------- VECTORIZE --------
vectorizer = TfidfVectorizer(stop_words="english")
vectors = vectorizer.fit_transform(df["tags"])

similarity = cosine_similarity(vectors)


# -------- MAIN FUNCTION --------
def get_similar_movies(query):
    query = query.lower().strip()

    # MOVIE SEARCH
    if query in df["title"].str.lower().values:
        idx = df[df["title"].str.lower() == query].index[0]

        scores = list(enumerate(similarity[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:20]

        return [df.iloc[i[0]] for i in scores]

    # ACTOR / GENERAL SEARCH
    else:
        matched = df[df["tags"].str.contains(query, na=False)]
        return matched.head(20).to_dict(orient="records")