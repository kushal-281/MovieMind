import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text

from components.header import show_header
from components.auth import restore_session
from components.movie_chatbot import render_movie_chatbot
from cookies import cookies
from config.database import engine

st.set_page_config(layout="wide")

restore_session()

if not st.session_state.get("user"):
    st.switch_page("app.py")

user = st.session_state.user
if user.get("role") == "admin":
    st.switch_page("pages/admin_profile.py")

user_id = int(user["user_id"])

show_header()

col1, col2 = st.columns([1, 3])

with col1:
    st.title("👤 Profile")
    st.write(f"**Username:** {user['username']}")
    st.write(f"**Role:** {user['role']}")
    try:
        with engine.connect() as c2:
            row = c2.execute(
                text(
                    "SELECT COALESCE(total_site_seconds, 0) AS t FROM users WHERE user_id = :uid"
                ),
                {"uid": user_id},
            ).fetchone()
        if row:
            total_s = int(row[0] or 0)
            st.write(
                f"**Time on site (approx.):** {total_s // 3600}h {(total_s % 3600) // 60}m {total_s % 60}s"
            )
    except Exception:
        pass
    st.divider()

    tab = st.radio(
        "Menu", ["Chat Bot", "Chatbot History", "Search History", "Analytics"]
    )

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

with col2:
    try:
        conn = engine.connect()

        if tab == "Chat Bot":
            render_movie_chatbot(user_id)

        elif tab == "Chatbot History":
            st.subheader("🧾 Chatbot History")
            q_chat = text(
                """
                SELECT query, response, timestamp
                FROM chat_logs
                WHERE user_id = :uid
                ORDER BY timestamp DESC
                """
            )
            chat_hist = pd.read_sql(q_chat, conn, params={"uid": user_id})
            if not chat_hist.empty:
                chat_hist = chat_hist.rename(
                    columns={
                        "query": "Question",
                        "response": "Answer",
                        "timestamp": "Date Time",
                    }
                )
                st.dataframe(chat_hist, use_container_width=True, hide_index=True)
            else:
                st.info("No chatbot history found.")

        elif tab == "Search History":
            st.subheader("🕵️ Search History")
            q_sh = text(
                """
                SELECT query, searched_at
                FROM search_history
                WHERE user_id = :uid
                ORDER BY searched_at DESC
                """
            )
            searches = pd.read_sql(q_sh, conn, params={"uid": user_id})

            if not searches.empty:
                searches["searched_at"] = pd.to_datetime(
                    searches["searched_at"], errors="coerce"
                )
                searches["Search History"] = searches["query"].astype(str)
                searches["Time"] = searches["searched_at"].dt.strftime("%H-%M-%S")
                searches["Date"] = searches["searched_at"].dt.strftime("%d-%m-%Y")
                searches = searches[["Search History", "Time", "Date"]]
                st.dataframe(searches, use_container_width=True, hide_index=True)
            else:
                st.info("No search history found.")

        elif tab == "Analytics":
            st.subheader("📊 Your analytics")

            # --- Total time on site (easy to read gauge) ---
            with engine.connect() as c3:
                r2 = c3.execute(
                    text(
                        "SELECT COALESCE(total_site_seconds, 0) AS t FROM users WHERE user_id = :uid"
                    ),
                    {"uid": user_id},
                ).fetchone()
            total_s = int(r2[0] or 0) if r2 else 0
            total_min = round(total_s / 60, 1)
            cap = max(30.0, total_min * 1.25, 60.0)

            fig_g = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=total_min,
                    number={"suffix": " min", "valueformat": ".1f"},
                    title={"text": "Approx. active time on MovieMind"},
                    gauge={
                        "axis": {"range": [0, cap]},
                        "bar": {"color": "#8a2be2"},
                        "steps": [
                            {"range": [0, cap * 0.33], "color": "#f2e8ff"},
                            {"range": [cap * 0.33, cap * 0.66], "color": "#e2d1ff"},
                        ],
                    },
                )
            )
            fig_g.update_layout(height=280, margin=dict(l=30, r=30, t=50, b=30))
            st.plotly_chart(fig_g, use_container_width=True)
            st.caption(
                "Time grows when you click around the app. Long breaks without clicks are not counted."
            )

            st.markdown("#### Time spent on each movie (minutes)")
            q_movie = text(
                """
                SELECT m.title, SUM(ua.time_spent) AS total_time
                FROM user_activity ua
                JOIN movies m ON ua.movie_id = m.movie_id
                WHERE ua.user_id = :uid
                GROUP BY ua.movie_id, m.title
                ORDER BY total_time DESC
                LIMIT 15
                """
            )
            df_time = pd.read_sql(q_movie, conn, params={"uid": user_id})
            if not df_time.empty:
                df_time["minutes"] = (df_time["total_time"] / 60.0).round(2)
                fig_m = px.bar(
                    df_time,
                    x="minutes",
                    y="title",
                    orientation="h",
                    labels={"minutes": "Minutes", "title": "Movie"},
                    title="Where you spend time (detail pages)",
                    color_discrete_sequence=["#6a5acd"],
                )
                fig_m.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig_m, use_container_width=True)
            else:
                st.info("Open some movie pages to see time-per-movie here.")

            st.markdown("#### Searches matched to industry")
            try:
                q_ind = text(
                    """
                    SELECT COALESCE(m.industry, 'Unknown') AS industry, COUNT(*) AS cnt
                    FROM search_history sh
                    JOIN movies m ON m.title LIKE CONCAT('%', sh.query, '%')
                    WHERE sh.user_id = :uid
                    GROUP BY m.industry
                    ORDER BY cnt DESC
                    """
                )
                df_ind = pd.read_sql(q_ind, conn, params={"uid": user_id})
                if not df_ind.empty:
                    fig_i = px.bar(
                        df_ind,
                        x="industry",
                        y="cnt",
                        labels={"industry": "Industry", "cnt": "Matched searches"},
                        title="How often your search text matched movies in each industry",
                        color_discrete_sequence=["#20b2aa"],
                    )
                    st.plotly_chart(fig_i, use_container_width=True)
                else:
                    st.info(
                        "No industry matches yet (try searching full movie titles from the catalog)."
                    )
            except Exception:
                st.info("Industry chart skipped (no matching data or schema issue).")

            st.markdown("#### Searches matched to genre")
            try:
                q_gen = text(
                    """
                    SELECT g.genre_name AS genre_name, COUNT(*) AS cnt
                    FROM search_history sh
                    JOIN movies m ON m.title LIKE CONCAT('%', sh.query, '%')
                    JOIN movie_genres mg ON mg.movie_id = m.movie_id
                    JOIN genres g ON g.genre_id = mg.genre_id
                    WHERE sh.user_id = :uid
                    GROUP BY g.genre_name
                    ORDER BY cnt DESC
                    LIMIT 12
                    """
                )
                df_gen = pd.read_sql(q_gen, conn, params={"uid": user_id})
                if not df_gen.empty:
                    fig_g2 = px.bar(
                        df_gen,
                        x="genre_name",
                        y="cnt",
                        labels={"genre_name": "Genre", "cnt": "Matched searches"},
                        title="Genres tied to movies that matched your searches",
                        color_discrete_sequence=["#ff8c42"],
                    )
                    st.plotly_chart(fig_g2, use_container_width=True)
                else:
                    st.info("No genre matches yet.")
            except Exception:
                try:
                    q_gen2 = text(
                        """
                        SELECT g.name AS genre_name, COUNT(*) AS cnt
                        FROM search_history sh
                        JOIN movies m ON m.title LIKE CONCAT('%', sh.query, '%')
                        JOIN movie_genres mg ON mg.movie_id = m.movie_id
                        JOIN genres g ON g.genre_id = mg.genre_id
                        WHERE sh.user_id = :uid
                        GROUP BY g.name
                        ORDER BY cnt DESC
                        LIMIT 12
                        """
                    )
                    df_gen = pd.read_sql(q_gen2, conn, params={"uid": user_id})
                    if not df_gen.empty:
                        fig_g2 = px.bar(
                            df_gen,
                            x="genre_name",
                            y="cnt",
                            title="Genres tied to movies that matched your searches",
                            color_discrete_sequence=["#ff8c42"],
                        )
                        st.plotly_chart(fig_g2, use_container_width=True)
                except Exception:
                    st.info("Genre chart skipped (check genres column: genre_name vs name).")

            st.markdown("#### Search activity over time")
            q_sf = text(
                """
                SELECT DATE(searched_at) AS date, COUNT(*) AS searches
                FROM search_history
                WHERE user_id = :uid
                GROUP BY DATE(searched_at)
                ORDER BY date
                """
            )
            df_search = pd.read_sql(q_sf, conn, params={"uid": user_id})
            if not df_search.empty:
                fig_l = px.line(
                    df_search,
                    x="date",
                    y="searches",
                    markers=True,
                    title="Number of searches per day",
                )
                fig_l.update_traces(line_color="#2e8b57", marker_color="#2e8b57")
                st.plotly_chart(fig_l, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Database error: {e}")
    finally:
        if "conn" in locals():
            conn.close()
