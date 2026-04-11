import streamlit as st
from components.header import show_header
from components.browse_grid import render_movie_grid

# ---------------- PAGE CONFIG ----------------
st.set_page_config(layout="wide")

# ---------------- SESSION ----------------
if "search_movie" not in st.session_state:
    st.session_state.search_movie = ""

# ---------------- HEADER ----------------
show_header()

# ---------------- IMPORT ----------------
from ml.recommendation_engine import recommend

st.title("Search Results")

query = st.session_state.get("search_movie", "").strip()
st.write("Search Query:", query)

if not query:
    st.info("Enter a movie name in the search bar above and click Search.")

else:
    try:
        results = recommend(query)

        if not results:
            st.warning("No movie found")

        else:
            results = [m for m in results if m.get("poster")]

            # Fix IDs
            for i, m in enumerate(results):
                if not m.get("id"):
                    m["id"] = f"temp_{i}"

            rows = [
                {
                    "movie_id": int(m["id"]),
                    "title": m.get("title"),
                    "poster_path": m.get("poster"),
                    "vote_average": m.get("rating", 0),
                    "vote_count": 0,
                    "industry": "",
                }
                for m in results
                if str(m.get("id", "")).isdigit()
            ]
            st.caption(f"Showing {len(rows)} matched movies for **{query}**.")
            render_movie_grid(rows, page_key_prefix="search")

    except Exception as e:
        st.error(f"Error while searching: {e}")