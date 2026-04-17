import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText

from config.database import engine, ensure_schema


def _send_reply_email(to_email: str, subject: str, reply_text: str):
    host = os.getenv("MOVIEMIND_SMTP_HOST")
    port = int(os.getenv("MOVIEMIND_SMTP_PORT", "587"))
    sender = os.getenv("MOVIEMIND_SMTP_USER")
    password = os.getenv("MOVIEMIND_SMTP_PASS")
    if not all([host, sender, password]):
        return False, "SMTP env vars not configured (MOVIEMIND_SMTP_HOST/USER/PASS)."
    try:
        msg = MIMEText(reply_text, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, [to_email], msg.as_string())
        return True, "Reply email sent."
    except Exception as e:
        return False, str(e)


def show_admin_dashboard():
    """Admin view: users, time on site, search and chatbot activity."""
    ensure_schema()
    if not st.session_state.get("user") or st.session_state.user.get("role") != "admin":
        st.error("Unauthorized Access")
        return

    st.markdown(
        """
        <style>
        .admin-title {
            color: #d7e3ff;
            font-weight: 700;
        }
        div[data-testid="stTabs"] button {
            color: #b8c9ff;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Admin Dashboard")
    tab_users, tab_history, tab_chat, tab_contact, tab_faq = st.tabs(
        ["Users", "User History", "Chatbot History", "Contact Replies", "FAQ Manager"]
    )

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

        with tab_contact:
            st.subheader("📨 Contact Us - Reply Panel")
            contact_df = pd.read_sql(
                text(
                    """
                    SELECT message_id, name, email, subject, message, status, created_at, replied_at
                    FROM contact_messages
                    ORDER BY created_at DESC
                    LIMIT 300
                    """
                ),
                conn,
            )
            if contact_df.empty:
                st.info("No contact messages yet.")
            else:
                st.dataframe(contact_df, use_container_width=True, height=280)
                options = contact_df.apply(
                    lambda r: f"#{int(r['message_id'])} | {r['name']} | {r['email']} | {r['status']}",
                    axis=1,
                ).tolist()
                selected = st.selectbox("Select user query", options, key="contact_msg_selector")
                selected_id = int(selected.split("|")[0].replace("#", "").strip())
                row = contact_df[contact_df["message_id"] == selected_id].iloc[0]
                st.write(f"**Question:** {row['message']}")
                reply_text = st.text_area("Admin reply", key=f"reply_text_{selected_id}", height=150)
                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button("Send Reply", key=f"send_reply_{selected_id}", use_container_width=True):
                        if not str(reply_text).strip():
                            st.error("Reply cannot be empty.")
                        else:
                            email_subject = f"Re: {row['subject'] or 'Your MovieMind query'}"
                            ok, detail = _send_reply_email(row["email"], email_subject, reply_text.strip())
                            status_txt = "replied_email" if ok else "replied_saved_only"
                            with engine.begin() as c2conn:
                                c2conn.execute(
                                    text(
                                        """
                                        UPDATE contact_messages
                                        SET admin_reply = :reply,
                                            replied_at = :replied_at,
                                            replied_by = :admin_id,
                                            status = :status
                                        WHERE message_id = :mid
                                        """
                                    ),
                                    {
                                        "reply": reply_text.strip(),
                                        "replied_at": datetime.now(),
                                        "admin_id": int(st.session_state.user["user_id"]),
                                        "status": status_txt,
                                        "mid": selected_id,
                                    },
                                )
                            if ok:
                                st.success("Reply sent to user email and saved.")
                            else:
                                st.warning(f"Reply saved in DB but email failed: {detail}")
                            st.rerun()
                with c2:
                    if st.button("Mark as Closed", key=f"close_msg_{selected_id}", use_container_width=True):
                        with engine.begin() as c2conn:
                            c2conn.execute(
                                text(
                                    "UPDATE contact_messages SET status = 'closed' WHERE message_id = :mid"
                                ),
                                {"mid": selected_id},
                            )
                        st.success("Marked as closed.")
                        st.rerun()

        with tab_faq:
            st.subheader("❓ FAQ Management")
            with st.form("faq_add_form", clear_on_submit=True):
                new_q = st.text_input("FAQ Question")
                new_a = st.text_area("FAQ Answer", height=120)
                add_faq = st.form_submit_button("Add FAQ")
            if add_faq:
                if not new_q.strip() or not new_a.strip():
                    st.error("Question and answer both are required.")
                else:
                    with engine.begin() as c3conn:
                        c3conn.execute(
                            text(
                                """
                                INSERT INTO faqs (question, answer, is_active, created_by)
                                VALUES (:q, :a, 1, :uid)
                                """
                            ),
                            {"q": new_q.strip(), "a": new_a.strip(), "uid": int(st.session_state.user["user_id"])},
                        )
                    st.success("FAQ added.")
                    st.rerun()

            faq_df = pd.read_sql(
                text(
                    """
                    SELECT faq_id, question, answer, is_active, updated_at
                    FROM faqs
                    ORDER BY updated_at DESC, faq_id DESC
                    """
                ),
                conn,
            )
            if faq_df.empty:
                st.info("No FAQ in DB yet.")
            else:
                st.dataframe(faq_df, use_container_width=True, height=280)
                faq_options = faq_df["faq_id"].astype(int).tolist()
                pick = st.selectbox("Select FAQ ID", faq_options, key="faq_pick")
                faq_row = faq_df[faq_df["faq_id"] == pick].iloc[0]
                uq = st.text_input("Edit Question", value=str(faq_row["question"]), key=f"faq_q_{pick}")
                ua = st.text_area("Edit Answer", value=str(faq_row["answer"]), key=f"faq_a_{pick}", height=130)
                c3, c4 = st.columns(2)
                with c3:
                    if st.button("Update FAQ", key=f"faq_update_{pick}", use_container_width=True):
                        with engine.begin() as c3conn:
                            c3conn.execute(
                                text(
                                    """
                                    UPDATE faqs
                                    SET question = :q, answer = :a
                                    WHERE faq_id = :fid
                                    """
                                ),
                                {"q": uq.strip(), "a": ua.strip(), "fid": int(pick)},
                            )
                        st.success("FAQ updated.")
                        st.rerun()
                with c4:
                    if st.button("Deactivate FAQ", key=f"faq_deactivate_{pick}", use_container_width=True):
                        with engine.begin() as c3conn:
                            c3conn.execute(
                                text("UPDATE faqs SET is_active = 0 WHERE faq_id = :fid"),
                                {"fid": int(pick)},
                            )
                        st.success("FAQ deactivated.")
                        st.rerun()
