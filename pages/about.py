import streamlit as st
from components.footer import show_footer
from components.header_without_search import header_without_search

# ---------------- PAGE CONFIG ----------------
st.set_page_config(layout="wide")

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- HEADER ----------------
header_without_search()

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

/* Page background */
body {
    background-color: #0e1117;
}

/* Title */
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: white;
    margin-top: 20px;
    animation: fadeIn 1s ease-in-out;
}

/* Subtitle */
.sub-title {
    text-align: center;
    font-size: 18px;
    color: #bbbbbb;
    margin-bottom: 40px;
    animation: fadeIn 1.5s ease-in-out;
}

/* Card container */
.card {
    background: #161b22;
    padding: 25px;
    border-radius: 15px;
    transition: 0.3s;
    height: 100%;
}

/* Hover effect */
.card:hover {
    transform: translateY(-10px);
    box-shadow: 0px 10px 25px rgba(255,255,255,0.1);
}

/* Section title */
.section-title {
    font-size: 22px;
    font-weight: bold;
    color: white;
    margin-bottom: 10px;
}

/* Text */
.text {
    color: #cccccc;
    font-size: 15px;
    line-height: 1.6;
}

/* Team card */
.team-card {
    text-align: center;
    padding: 20px;
    background: #161b22;
    border-radius: 15px;
    transition: 0.3s;
}

.team-card:hover {
    transform: scale(1.05);
    box-shadow: 0px 10px 25px rgba(255,255,255,0.1);
}

/* Animation */
@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown('<div class="main-title">About MovieMind</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Smart Movie Discovery & Recommendation Platform</div>', unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#bcbcbc;'>MovieMind helps you discover movies faster using smart search, browsing by category, and recommendations based on your activity.</p>",
    unsafe_allow_html=True,
)

# ---------------- ABOUT SECTION ----------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card">
        <div class="section-title">Our Mission</div>
        <div class="text">
        MovieMind is designed to simplify the way users discover movies.
        Our goal is to provide intelligent recommendations based on user preferences,
        helping users find the perfect movie effortlessly.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <div class="section-title">Our Vision</div>
        <div class="text">
        We aim to build a powerful movie platform that combines data analytics,
        machine learning, and modern UI to create a seamless and engaging user experience.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- FEATURES ----------------
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-title">Key Features</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
        <div class="section-title">Smart Search</div>
        <div class="text">
        Search and discover movies instantly with intelligent suggestions.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <div class="section-title">Personalized Recommendations</div>
        <div class="text">
        Get movie suggestions based on your interests and preferences.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <div class="section-title">Detailed Insights</div>
        <div class="text">
        View ratings, genres, release dates, and complete movie details.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- TEAM SECTION ----------------
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown('<div class="section-title">Our Team</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col2:
    st.markdown("""
    <div class="team-card">
        <h3 style="color:white;">Kushal Rohilla</h3>
        <p style="color:#bbbbbb;">Developer & Designer</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("<br><br>", unsafe_allow_html=True)

show_footer()
