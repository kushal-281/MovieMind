import streamlit as st

from components.footer import show_footer
from components.header_without_search import header_without_search

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Terms & Conditions - MovieMind", layout="wide")
header_without_search()

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main {
    background-color: #0E1117;
    color: white;
}

.title {
    text-align: center;
    font-size: 40px;
    font-weight: bold;
    margin-bottom: 20px;
}

.section {
    background-color: #161B22;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 15px;
    transition: 0.3s;
}

.section:hover {
    transform: scale(1.01);
    box-shadow: 0px 0px 15px rgba(255,255,255,0.1);
}

.heading {
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 10px;
}

.text {
    font-size: 16px;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown('<div class="title">📜 Terms & Conditions – MovieMind</div>', unsafe_allow_html=True)

# ---------------- SECTIONS ----------------
def section(title, content):
    st.markdown(f"""
    <div class="section">
        <div class="heading">{title}</div>
        <div class="text">{content}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- CONTENT ----------------
section("1. Introduction",
        "Welcome to MovieMind. By using our platform, you agree to follow these Terms & Conditions. If you do not agree, please do not use our services.")

section("2. Use of the Platform",
        "MovieMind allows users to search and explore movies. You agree to use the platform only for legal purposes and not attempt hacking, misuse, or harmful activities.")

section("3. User Accounts",
        "You are responsible for maintaining your account credentials. MovieMind is not responsible for unauthorized access due to negligence.")

section("4. Content and Data",
        "Movie data such as posters, ratings, and descriptions may come from third-party APIs. We do not guarantee complete accuracy.")

section("5. Intellectual Property",
        "All branding, design, and features of MovieMind are protected. Unauthorized copying or usage is prohibited.")

section("6. User Conduct",
        "Users must not post harmful content, use bots, or attempt to disrupt the platform.")

section("7. Privacy",
        "We store limited user data such as login details and search history securely. We do not sell your data.")

section("8. Third-Party Services",
        "MovieMind depends on third-party APIs. We are not responsible for their downtime or errors.")

section("9. Limitation of Liability",
        "MovieMind is provided 'as is' without warranties. We are not responsible for any damages or losses.")

section("10. Termination",
        "We may suspend accounts that violate these terms at any time.")

section("11. Updates to Terms",
        "We may update these terms anytime. Continued use means acceptance of changes.")

section("12. Contact Information",
        "Email: support@moviemind.com<br>Location: Panipat, Haryana, India")

section("13. Recommendation Disclaimer",
        "Recommendations are generated automatically from available metadata and activity signals. They are suggestions only and may not always match your preferences.")

# ---------------- FOOTER ----------------
show_footer()