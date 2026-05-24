import streamlit as st

from components.footer import show_footer
from components.header import show_header
from components.static_page_styles import apply_static_page_styles
from components.theme import init_theme

st.set_page_config(page_title="Privacy Policy - MovieMind", layout="wide")
init_theme()
show_header()
apply_static_page_styles()

st.markdown("""
<style>
.block-container { padding-top: 20px; }
.title { text-align: center; font-size: 42px; font-weight: 700; margin-bottom: 10px; }
.subtitle { text-align: center; font-size: 16px; margin-bottom: 40px; }
.section { margin-bottom: 30px; }
.heading {
    font-size: 24px; font-weight: 600; margin-bottom: 10px;
    border-left: 4px solid var(--mm-accent); padding-left: 12px;
}
.text {
    font-size: 16px;
    line-height: 1.8;
}

/* List */
.text ul {
    padding-left: 22px;
}

.text li {
    margin-bottom: 8px;
}

hr {
    border: none;
    border-top: 1px solid var(--mm-border);
    margin-top: 25px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown(
    '<div class="title">Privacy Policy</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Your privacy and data security are important to us at MovieMind.
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- SECTION FUNCTION ----------------
def section(title, content):
    st.markdown(f"""
    <div class="section">
        <div class="heading">{title}</div>
        <div class="text">{content}</div>
        <hr>
    </div>
    """, unsafe_allow_html=True)

# ---------------- CONTENT ----------------
section(
    "1. Introduction",
    """
    Welcome to MovieMind. This Privacy Policy explains how we collect,
    use, store, and protect your personal information while using our platform.
    By using MovieMind, you agree to the practices described in this policy.
    """
)

section(
    "2. Information We Collect",
    """
    We may collect the following information from users:
    <ul>
        <li>Username and email address during account registration</li>
        <li>Login credentials and authentication details</li>
        <li>Movie search history and browsing activity</li>
        <li>User preferences and watch history</li>
        <li>Technical information such as browser type and IP address</li>
        <li>Device-related information for improving compatibility and security</li>
    </ul>
    """
)

section(
    "3. How We Use Your Information",
    """
    Your information is used to improve platform functionality and provide
    a better user experience. We may use your information to:
    <ul>
        <li>Create and manage user accounts</li>
        <li>Provide personalized movie recommendations</li>
        <li>Improve search accuracy and analytics</li>
        <li>Maintain security and prevent unauthorized access</li>
        <li>Respond to support requests and feedback</li>
        <li>Enhance overall website performance and usability</li>
    </ul>
    """
)

section(
    "4. Data Protection and Security",
    """
    MovieMind uses reasonable security measures to protect user data
    from unauthorized access, misuse, or disclosure.
    While we strive to maintain strong security practices,
    no online platform can guarantee complete protection against all threats.
    """
)

section(
    "5. Sharing of Information",
    """
    We do not sell, rent, or trade your personal information.
    Information may only be shared in limited situations:
    <ul>
        <li>With trusted third-party services required for platform functionality</li>
        <li>To comply with legal obligations or government requests</li>
        <li>To protect the safety, rights, and security of MovieMind and its users</li>
    </ul>
    """
)

section(
    "6. Cookies and Tracking Technologies",
    """
    MovieMind may use cookies and similar technologies to improve
    user experience, remember preferences, analyze traffic,
    and understand platform usage patterns.
    Users can disable cookies through browser settings if preferred.
    """
)

section(
    "7. Third-Party Services",
    """
    MovieMind may integrate third-party APIs and services for movie data,
    recommendations, or analytics. These services may process limited user data
    according to their own privacy policies and terms.
    """
)

section(
    "8. User Rights",
    """
    Users have the right to:
    <ul>
        <li>Access personal information stored on the platform</li>
        <li>Request corrections to inaccurate data</li>
        <li>Request account or data deletion</li>
        <li>Stop using the platform at any time</li>
        <li>Contact support regarding privacy concerns</li>
    </ul>
    """
)

section(
    "9. Data Retention",
    """
    We retain user information only for as long as necessary
    to provide platform services, maintain security,
    improve recommendations, and comply with legal requirements.
    """
)

section(
    "10. Policy Updates",
    """
    MovieMind may update this Privacy Policy periodically
    to reflect new features, legal requirements, or service improvements.
    Continued use of the platform after updates indicates acceptance
    of the revised policy.
    """
)

section(
    "11. Contact Information",
    """
    If you have questions regarding this Privacy Policy or your data,
    you may contact us through the MovieMind support system.

    <br><br>

    Email: support@moviemind.com<br>
    Location: Panipat, Haryana, India
    """
)

# ---------------- FOOTER ----------------
show_footer()