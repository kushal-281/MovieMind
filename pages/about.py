import streamlit as st

from components.footer import show_footer
from components.header import show_header
from components.static_page_styles import apply_static_page_styles
from components.theme import init_theme

st.set_page_config(layout="wide")
init_theme()

if "user" not in st.session_state:
    st.session_state.user = None

show_header()
apply_static_page_styles()

st.markdown(
    """
    <style>
    .main-title { text-align: center; font-size: 44px; font-weight: 700; margin-top: 20px; }
    .sub-title { text-align: center; font-size: 18px; margin-bottom: 35px; }
    .section-title { font-size: 28px; font-weight: 600; margin-top: 35px; margin-bottom: 12px; }
    .text { font-size: 16px; line-height: 1.9; }
    .team-box { text-align: center; margin-top: 25px; padding: 20px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- TITLE ----------------
st.markdown(
    '<div class="main-title">About MovieMind</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Smart Movie Discovery & Recommendation Platform</div>',
    unsafe_allow_html=True
)

# ---------------- ABOUT ----------------
st.markdown(
    """
    <div class="text" style="text-align:center; max-width:950px; margin:auto;">
    MovieMind is a modern movie discovery and recommendation platform developed to improve
    the way users search, explore, and analyze movies online. The platform combines
    intelligent search functionality, category-based browsing, and personalized
    recommendations to provide a seamless and engaging user experience.
    <br><br>
    Users can easily discover trending, popular, top-rated, and recently released movies.
    The platform is designed with a clean and responsive interface that helps users
    quickly access movie details, ratings, genres, release information, and recommendations.
    MovieMind also focuses on improving user engagement through personalized experiences
    and activity tracking.
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- MISSION ----------------
st.markdown(
    '<div class="section-title">Our Mission</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="text">
    Our mission is to simplify movie discovery by providing users with fast search,
    accurate recommendations, and a user-friendly browsing experience.
    We aim to help users save time while finding movies that match their interests
    and preferences.
    <br><br>
    MovieMind is built to create an engaging entertainment platform where users
    can explore movies effortlessly without complicated navigation or unnecessary distractions.
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- VISION ----------------
st.markdown(
    '<div class="section-title">Our Vision</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="text">
    Our vision is to build an advanced movie platform that combines modern web technologies,
    recommendation systems, analytics, and interactive user experiences.
    <br><br>
    We aim to continuously improve the platform by integrating intelligent features,
    enhancing performance, and delivering a smooth and visually appealing experience
    for movie lovers.
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- FEATURES ----------------
st.markdown(
    '<div class="section-title">Key Features</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="text">
    • Smart movie search with fast suggestions<br>
    • Browse movies by genre, category, and release year<br>
    • Personalized movie recommendations based on user activity<br>
    • Detailed movie information including ratings and genres<br>
    • Watch history and search history tracking<br>
    • Interactive and responsive user interface<br>
    • User authentication with OTP verification<br>
    • Multiple theme customization options<br>
    • Analytics for user activity and engagement
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- TECHNOLOGIES ----------------
st.markdown(
    '<div class="section-title">Technologies Used</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="text">
    MovieMind is developed using modern technologies and tools to ensure
    better performance, scalability, and user experience.
    <br><br>
    • Python<br>
    • Streamlit<br>
    • MySQL Database<br>
    • SQLAlchemy<br>
    • Pandas<br>
    • NumPy<br>
    • Scikit-learn<br>
    • Plotly
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- WHY MOVIEMIND ----------------
st.markdown(
    '<div class="section-title">Why Choose MovieMind?</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="text">
    MovieMind provides a simple yet powerful platform for discovering movies.
    Unlike traditional movie browsing platforms, MovieMind focuses on personalization,
    intelligent recommendations, and user-friendly navigation.
    <br><br>
    The platform is designed to help users quickly find movies they may enjoy,
    making entertainment discovery faster and more engaging.
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- FUTURE IMPROVEMENTS ----------------
st.markdown(
    '<div class="section-title">Future Improvements</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="text">
    Future versions of MovieMind may include advanced recommendation systems,
    AI-powered chat assistance, real-time trending analytics, social sharing,
    watchlist synchronization, and enhanced user personalization features.
    <br><br>
    Additional improvements will focus on performance optimization,
    mobile responsiveness, and integration with external movie APIs.
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- DEVELOPER ----------------
st.markdown(
    '<div class="section-title">Developer</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="team-box">
        <h3>Kushal Rohilla</h3>
        <p>Developer & Designer</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- FOOTER ----------------
st.markdown("<br><br>", unsafe_allow_html=True)

show_footer()