import streamlit as st

from components.footer import show_footer
from components.header_without_search import header_without_search
# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Privacy Policy - MovieMind", layout="wide")

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
st.markdown('<div class="title">🔐 Privacy Policy – MovieMind</div>', unsafe_allow_html=True)

# ---------------- SECTION FUNCTION ----------------
def section(title, content):
    st.markdown(f"""
    <div class="section">
        <div class="heading">{title}</div>
        <div class="text">{content}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- CONTENT ----------------
section("1. Introduction",
        "Welcome to MovieMind. Your privacy is important to us. This Privacy Policy explains how we collect, use, and protect your information.")

section("2. Information We Collect",
        """
        We may collect the following data:
        <ul>
            <li>Account information (name, email)</li>
            <li>Login details</li>
            <li>Search history and user activity</li>
            <li>Technical data (IP address, browser type)</li>
        </ul>
        """)

section("3. How We Use Your Information",
        """
        We use your data to:
        <ul>
            <li>Provide and improve our services</li>
            <li>Personalize your experience</li>
            <li>Store search history for better recommendations</li>
            <li>Ensure platform security</li>
        </ul>
        """)

section("4. Data Protection",
        "We implement security measures to protect your personal data. However, no system is completely secure, and we cannot guarantee absolute security.")

section("5. Sharing of Information",
        """
        We do NOT sell your personal data. We may share data only:
        <ul>
            <li>With trusted third-party services (APIs)</li>
            <li>If required by law</li>
        </ul>
        """)

section("6. Cookies and Tracking",
        "MovieMind may use cookies to enhance user experience and analyze usage patterns.")

section("7. Third-Party Services",
        "We use third-party APIs for movie data. These services may collect limited information as per their own policies.")

section("8. User Rights",
        """
        You have the right to:
        <ul>
            <li>Access your data</li>
            <li>Request correction or deletion</li>
            <li>Stop using the platform anytime</li>
        </ul>
        """)

section("9. Changes to Privacy Policy",
        "We may update this policy from time to time. Continued use of MovieMind means you accept the updated policy.")

section("10. Contact Us",
        "Email: support@moviemind.com<br>Location: Panipat, Haryana, India")

section("11. Data Retention",
        "We keep essential account and activity records only as long as required to provide recommendations, maintain security, and support users.")

# ---------------- FOOTER ----------------
show_footer()