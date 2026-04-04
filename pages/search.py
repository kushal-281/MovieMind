import streamlit as st
from components.header import show_header

# ---------------- PAGE CONFIG ----------------
st.set_page_config(layout="wide")

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if "search_movie" not in st.session_state:
    st.session_state.search_movie = ""

# ---------------- HEADER ----------------
show_header()

# ---------------- IMPORT ----------------
from ml.recommendation_engine import recommend

st.title("Search Results")

query = st.session_state.get("search_movie", "").strip()
st.write("Search Query:", query)

# ---------------- CUSTOM CSS (REMOVE BUTTON UI) ----------------
st.markdown("""
<style>
div.stButton > button {
    background: transparent;
    border: none;
    padding: 0;
}
</style>
""", unsafe_allow_html=True)

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

            results = results[:10]

            for i in range(0, len(results), 5):
                cols = st.columns(5)

                for j in range(5):
                    if i + j < len(results):
                        movie = results[i + j]
                        movie_id = movie["id"]

                        with cols[j]:
                            # ✅ Invisible clickable poster
                            if st.button("", key=f"btn_{i}_{j}_{movie_id}"):
                                st.query_params["id"] = movie_id
                                st.switch_page("pages/movie_detail.py")

                            st.image(
                                "https://image.tmdb.org/t/p/w500" + movie["poster"],
                                use_container_width=True
                            )

                            # Title
                            st.markdown(
                                f"<p style='text-align:center; font-weight:bold;'>"
                                f"{movie.get('title')}</p>",
                                unsafe_allow_html=True
                            )

                            # Rating
                            rating = movie.get("rating", 0)
                            if rating >= 7.5:
                                color = "green"
                            elif rating >= 5:
                                color = "orange"
                            else:
                                color = "red"

                            st.markdown(
                                f"<p style='text-align:center; color:{color};'>⭐ {rating}</p>",
                                unsafe_allow_html=True
                            )

    except Exception as e:
        st.error(f"Error while searching: {e}")