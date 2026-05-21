import streamlit as st

from components.footer import show_footer
from components.header_without_search import header_without_search

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Terms & Conditions - MovieMind",
    layout="wide"
)

# ---------------- HEADER ----------------
header_without_search()

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

.block-container{
#     max-width: 1100px;
    padding-top: 20px;
}

/* Page */
.main {
    background-color: #0E1117;
    color: white;
}

/* Title */
.title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    color: white;
    margin-bottom: 10px;
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: #bdbdbd;
    font-size: 16px;
    margin-bottom: 40px;
}

/* Section */
.section {
    margin-bottom: 30px;
}

/* Heading */
.heading {
    font-size: 24px;
    font-weight: 600;
    color: white;
    margin-bottom: 10px;
    border-left: 4px solid #4A90E2;
    padding-left: 12px;
}

/* Text */
.text {
    font-size: 16px;
    color: #cfcfcf;
    line-height: 1.8;
}

/* List */
.text ul {
    padding-left: 22px;
}

.text li {
    margin-bottom: 8px;
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid #2a2a2a;
    margin-top: 25px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown(
    '<div class="title">Terms & Conditions</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Please read these terms carefully before using MovieMind.
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
    Welcome to MovieMind. By accessing or using our platform,
    you agree to comply with these Terms & Conditions.
    If you do not agree with any part of these terms,
    please discontinue use of the platform.
    """
)

section(
    "2. Use of the Platform",
    """
    MovieMind provides movie discovery, browsing,
    and recommendation services for users.
    You agree to use the platform responsibly and only for lawful purposes.

    <ul>
        <li>Do not attempt unauthorized access or hacking</li>
        <li>Do not misuse platform features or services</li>
        <li>Do not interfere with system functionality or security</li>
        <li>Do not upload harmful or malicious content</li>
    </ul>
    """
)

section(
    "3. User Accounts",
    """
    Users are responsible for maintaining the confidentiality
    of their login credentials and account information.

    <ul>
        <li>Keep your password secure</li>
        <li>Do not share account credentials with others</li>
        <li>Notify MovieMind if unauthorized activity is detected</li>
    </ul>

    MovieMind is not responsible for losses caused
    by negligent handling of account credentials.
    """
)

section(
    "4. Content and Movie Data",
    """
    Movie information such as ratings, posters,
    genres, and descriptions may be obtained from third-party APIs.
    While we aim to provide accurate information,
    MovieMind does not guarantee the completeness,
    reliability, or accuracy of all content displayed.
    """
)

section(
    "5. Intellectual Property",
    """
    All MovieMind branding, design elements,
    interface layouts, and custom features are protected
    by intellectual property rights.

    Users may not:
    <ul>
        <li>Copy or reproduce platform content without permission</li>
        <li>Use MovieMind branding for commercial purposes</li>
        <li>Modify or redistribute platform materials unlawfully</li>
    </ul>
    """
)

section(
    "6. User Conduct",
    """
    Users must behave responsibly while using the platform.

    Prohibited activities include:
    <ul>
        <li>Posting harmful or offensive content</li>
        <li>Using bots or automated scraping tools</li>
        <li>Attempting to exploit vulnerabilities</li>
        <li>Disrupting platform services or servers</li>
    </ul>
    """
)

section(
    "7. Privacy and Data Usage",
    """
    MovieMind may store limited user information
    such as account details, search activity,
    and usage history to improve recommendations
    and enhance the user experience.

    We do not sell personal user data to third parties.
    """
)

section(
    "8. Third-Party Services",
    """
    MovieMind relies on external APIs and services
    for movie-related data and platform functionality.

    We are not responsible for:
    <ul>
        <li>Third-party downtime or interruptions</li>
        <li>Incorrect data from external providers</li>
        <li>Changes made by third-party platforms</li>
    </ul>
    """
)

section(
    "9. Limitation of Liability",
    """
    MovieMind is provided on an "as is" and "as available" basis.

    We are not liable for:
    <ul>
        <li>Temporary unavailability of services</li>
        <li>Loss of data or interruptions</li>
        <li>Indirect damages resulting from platform usage</li>
        <li>Third-party service failures or inaccuracies</li>
    </ul>
    """
)

section(
    "10. Account Suspension and Termination",
    """
    MovieMind reserves the right to suspend or terminate accounts
    that violate these Terms & Conditions,
    engage in harmful activities,
    or misuse the platform in any way.
    """
)

section(
    "11. Recommendation Disclaimer",
    """
    Recommendations generated by MovieMind
    are based on available movie metadata,
    user preferences, browsing activity,
    and automated algorithms.

    Recommendations are suggestions only
    and may not always perfectly match user interests.
    """
)

section(
    "12. Changes to Terms",
    """
    MovieMind may update these Terms & Conditions periodically
    to reflect platform improvements,
    legal requirements, or policy updates.

    Continued use of the platform after updates
    indicates acceptance of the revised terms.
    """
)

section(
    "13. Contact Information",
    """
    If you have questions or concerns regarding these Terms & Conditions,
    you may contact MovieMind support.

    <br><br>

    Email: support@moviemind.com<br>
    Location: Panipat, Haryana, India
    """
)

# ---------------- FOOTER ----------------
show_footer()