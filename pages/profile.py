import streamlit as st
from components.header import show_header
from cookies import cookies
from datetime import datetime
import pandas as pd
import plotly.express as px
from config.database import engine

st.set_page_config(layout="wide")

# ---------------- PROTECT PAGE ----------------
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

show_header()
user = st.session_state.user
user_id = int(user['user_id'])  # Ensure user_id is int

# ---------------- SIDEBAR / LEFT COLUMN ----------------
col1, col2 = st.columns([1, 3])

with col1:
    st.title("👤 Profile")
    st.write(f"**Username:** {user['username']}")
    st.write(f"**Role:** {user['role']}")
    st.divider()

    tab = st.radio("Menu", ["Search History", "Activity Report", "Chat Bot Logs", "Favorites", "Analytics"])

    if st.button("Logout", key="profile_logout_btn"):
        st.session_state["force_logout"] = True
        if cookies.get("user"):
            cookies.pop("user", None)
            cookies.save()
        keys = list(st.session_state.keys())
        for key in keys:
            if key != "force_logout":
                del st.session_state[key]
        st.switch_page("app.py")

# ---------------- RIGHT COLUMN / DETAILS ----------------
with col2:
    try:
        # Connect using SQLAlchemy engine
        conn = engine.connect()

        # ---------------- SEARCH HISTORY ----------------
        if tab == "Search History":
            st.subheader("🕵️ Search History")
            query = """
                SELECT query, searched_at
                FROM search_history
                WHERE user_id = %(user_id)s
                ORDER BY searched_at DESC
            """
            searches = pd.read_sql(query, conn, params={"user_id": user_id})

            if not searches.empty:
                for _, s in searches.iterrows():
                    st.write(f"- **{s['query']}** (searched at {s['searched_at']})")
            else:
                st.info("No search history found.")

        # ---------------- USER ACTIVITY ----------------
        elif tab == "Activity Report":
            st.subheader("⏱️ User Activity")
            query = """
                SELECT ua.movie_id, m.title, ua.time_spent, ua.last_viewed
                FROM user_activity ua
                JOIN movies m ON ua.movie_id = m.movie_id
                WHERE ua.user_id = %(user_id)s
                ORDER BY ua.last_viewed DESC
            """
            activities = pd.read_sql(query, conn, params={"user_id": user_id})

            if not activities.empty:
                for _, a in activities.iterrows():
                    minutes = a['time_spent'] // 60
                    seconds = a['time_spent'] % 60
                    st.write(f"- **{a['title']}** | Time spent: {minutes}m {seconds}s | Last viewed: {a['last_viewed']}")
            else:
                st.info("No activity found.")

        # ---------------- CHAT BOT LOGS ----------------
        elif tab == "Chat Bot Logs":
            st.subheader("💬 Chat Bot Logs")
            try:
                query = """
                    SELECT query, response, timestamp
                    FROM chat_logs
                    WHERE user_id = %(user_id)s
                    ORDER BY timestamp DESC
                """
                chats = pd.read_sql(query, conn, params={"user_id": user_id})
            except:
                chats = pd.DataFrame()

            if not chats.empty:
                for _, c in chats.iterrows():
                    st.write(f"- **You:** {c['query']}  \n  **Bot:** {c['response']}  \n  _{c['timestamp']}_")
            else:
                st.info("No chat history available.")

        # ---------------- FAVORITES ----------------
        elif tab == "Favorites":
            st.subheader("⭐ Favorites")
            query = """
                SELECT m.title, m.release_date, m.industry
                FROM favorites f
                JOIN movies m ON f.movie_id = m.movie_id
                WHERE f.user_id = %(user_id)s
                ORDER BY f.fav_id DESC
            """
            favs = pd.read_sql(query, conn, params={"user_id": user_id})

            if not favs.empty:
                for _, f in favs.iterrows():
                    st.write(f"- **{f['title']}** | {f['industry']} | Released: {f['release_date']}")
            else:
                st.info("No favorite movies found.")

        # ---------------- ANALYTICS ----------------
        elif tab == "Analytics":
            st.subheader("📊 Analytics")

            # Total time spent per movie
            query = """
                SELECT m.title, SUM(ua.time_spent) as total_time
                FROM user_activity ua
                JOIN movies m ON ua.movie_id = m.movie_id
                WHERE ua.user_id = %(user_id)s
                GROUP BY ua.movie_id
                ORDER BY total_time DESC
            """
            df_time = pd.read_sql(query, conn, params={"user_id": user_id})
            if not df_time.empty:
                fig = px.bar(df_time, x='title', y='total_time',
                             title='Total Time Spent per Movie',
                             labels={'total_time':'Time (seconds)'})
                st.plotly_chart(fig, use_container_width=True)

            # Search frequency over time
            query = """
                SELECT DATE(searched_at) as date, COUNT(*) as searches
                FROM search_history
                WHERE user_id = %(user_id)s
                GROUP BY DATE(searched_at)
                ORDER BY date
            """
            df_search = pd.read_sql(query, conn, params={"user_id": user_id})
            if not df_search.empty:
                fig = px.line(df_search, x='date', y='searches', title='Search Frequency Over Time')
                st.plotly_chart(fig, use_container_width=True)

            # Most searched genres
            query = """
                SELECT g.genre_name, COUNT(*) as count
                FROM search_history sh
                JOIN movies m ON m.title LIKE CONCAT('%', sh.query, '%')
                JOIN movie_genres mg ON mg.movie_id = m.movie_id
                JOIN genres g ON g.genre_id = mg.genre_id
                WHERE sh.user_id = %(user_id)s
                GROUP BY g.genre_name
                ORDER BY count DESC
                LIMIT 10
            """
            df_genre = pd.read_sql(query, conn, params={"user_id": user_id})
            if not df_genre.empty:
                fig = px.pie(df_genre, names='genre_name', values='count', title='Most Searched Genres')
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()