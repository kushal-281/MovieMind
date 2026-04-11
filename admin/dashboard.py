import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

from config.database import engine


def show_admin_dashboard():
    """Admin view: users, time on site, search and chatbot activity."""
    if not st.session_state.get("user") or st.session_state.user.get("role") != "admin":
        st.error("Unauthorized Access")
        return

    st.title("Admin Dashboard")
    tab_users, tab_history, tab_chat = st.tabs(["Users", "User History", "Chatbot History"])

    with engine.connect() as conn:
        with tab_users:
            st.subheader("👥 All users")
            users_df = pd.read_sql(
                text(
                    """
                    SELECT user_id, username, email, role,
                           COALESCE(total_site_seconds, 0) AS total_site_seconds
                    FROM users
                    ORDER BY created_at DESC
                    """
                ),
                conn,
            )
            if not users_df.empty:
                u2 = users_df.copy()
                u2["minutes_on_site"] = (u2["total_site_seconds"] / 60.0).round(1)
                fig = px.bar(
                    u2.sort_values("minutes_on_site", ascending=False).head(30),
                    x="username",
                    y="minutes_on_site",
                    labels={"minutes_on_site": "Minutes (approx.)", "username": "User"},
                    title="Approx. active time per user (minutes)",
                )
                st.plotly_chart(fig, use_container_width=True)
            st.dataframe(users_df, use_container_width=True, height=320)

        with tab_history:
            st.subheader("🔎 Searches per user")
            search_df = pd.read_sql(
                text(
                    """
                    SELECT u.username,
                           COUNT(*) AS total_searches
                    FROM search_history sh
                    JOIN users u ON u.user_id = sh.user_id
                    GROUP BY sh.user_id, u.username
                    ORDER BY total_searches DESC
                    """
                ),
                conn,
            )
            if not search_df.empty:
                fig2 = px.bar(
                    search_df.head(25),
                    x="username",
                    y="total_searches",
                    title="Total searches (top 25 users)",
                )
                st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(search_df, use_container_width=True, height=260)

            st.subheader("🎯 Matched industry from user searches (all users)")
            try:
                ind_df = pd.read_sql(
                    text(
                        """
                        SELECT u.username,
                               COALESCE(m.industry, 'Unknown') AS industry,
                               COUNT(*) AS cnt
                        FROM search_history sh
                        JOIN users u ON u.user_id = sh.user_id
                        JOIN movies m ON m.title LIKE CONCAT('%', sh.query, '%')
                        GROUP BY u.username, m.industry
                        ORDER BY cnt DESC
                        LIMIT 200
                        """
                    ),
                    conn,
                )
                st.dataframe(ind_df, use_container_width=True, height=320)
                if not ind_df.empty:
                    top = ind_df.groupby("industry", as_index=False)["cnt"].sum().sort_values(
                        "cnt", ascending=False
                    )
                    fig3 = px.pie(
                        top.head(10),
                        names="industry",
                        values="cnt",
                        title="Share of search-movie matches by industry (top 10)",
                    )
                    st.plotly_chart(fig3, use_container_width=True)
            except Exception as e:
                st.info(f"Industry breakdown unavailable: {e}")

        with tab_chat:
            st.subheader("💬 Chat bot logs")
            try:
                chat_df = pd.read_sql(
                    text(
                        """
                        SELECT c.user_id, u.username, c.query, c.response, c.timestamp
                        FROM chat_logs c
                        JOIN users u ON u.user_id = c.user_id
                        ORDER BY c.timestamp DESC
                        LIMIT 300
                        """
                    ),
                    conn,
                )
                st.dataframe(chat_df, use_container_width=True, height=360)
                if not chat_df.empty:
                    by_user = (
                        chat_df.groupby("username", as_index=False)["query"].count().rename(
                            columns={"query": "messages"}
                        )
                    )
                    fig4 = px.bar(
                        by_user.sort_values("messages", ascending=False).head(20),
                        x="username",
                        y="messages",
                        title="Chatbot messages by user",
                    )
                    st.plotly_chart(fig4, use_container_width=True)
            except Exception:
                st.info("No chat_logs table yet - run DB migration and generate chat activity.")
