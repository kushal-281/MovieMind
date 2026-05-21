import streamlit as st


def show_footer2():

    # ---------------- CSS ----------------
    st.markdown("""
    <style>

    .mm-footer {
        margin-top: 60px;
        border-radius: 24px;
        overflow: hidden;

        background:
            linear-gradient(
                135deg,
                #0f0f0f 0%,
                #181818 35%,
                #202020 100%
            );

        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 10px 35px rgba(0,0,0,0.35);

        color: white !important;
    }

    .mm-footer * {
        color: white !important;
    }

    /* TOP */

    .mm-footer-top {
        padding: 45px 40px 20px 40px;
    }

    .mm-brand {
        text-align: center;
        margin-bottom: 40px;
    }

    .mm-brand h1 {
        font-size: 38px;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }

    .mm-brand p {
        color: #d6d6d6 !important;
        max-width: 760px;
        margin: auto;
        line-height: 1.8;
        font-size: 15px;
    }

    /* GRID */

    .mm-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 22px;
    }

    .mm-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);

        border-radius: 18px;
        padding: 24px;

        transition: 0.3s ease;
        min-height: 220px;
    }

    .mm-card:hover {
        transform: translateY(-5px);

        border: 1px solid rgba(255,75,75,0.35);

        background: rgba(255,255,255,0.06);
    }

    .mm-title {
        font-size: 18px;
        font-weight: 700;

        margin-bottom: 18px;

        position: relative;
        padding-bottom: 10px;
    }

    .mm-title::after {
        content: "";

        position: absolute;
        left: 0;
        bottom: 0;

        width: 50px;
        height: 3px;

        border-radius: 20px;

        background: #ff4b4b;
    }

    .mm-text {
        color: #d8d8d8 !important;
        line-height: 1.9;
        font-size: 14px;
    }

    /* PAGE LINKS */

    div[data-testid="stPageLink"] a {
        color: #d8d8d8 !important;
        text-decoration: none !important;

        transition: 0.25s ease;
    }

    div[data-testid="stPageLink"] a:hover {
        color: #ff4b4b !important;
        padding-left: 5px;
    }

    /* SOCIAL */

    .mm-social {
        display: flex;
        gap: 14px;
        flex-wrap: wrap;
        margin-top: 16px;
    }

    .mm-social img {
        width: 42px;
        height: 42px;

        border-radius: 50%;

        background: white;
        padding: 8px;

        transition: 0.3s ease;

        box-shadow: 0 4px 14px rgba(255,255,255,0.12);
    }

    .mm-social img:hover {
        transform: translateY(-5px) scale(1.08);

        box-shadow: 0 8px 24px rgba(255,255,255,0.25);
    }

    /* BOTTOM */

    .mm-bottom {
        margin-top: 40px;

        text-align: center;

        padding: 20px;

        border-top: 1px solid rgba(255,255,255,0.08);

        background: rgba(255,255,255,0.03);

        color: #bdbdbd !important;

        font-size: 13px;
        letter-spacing: 0.6px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ---------------- MAIN WRAPPER ----------------
    st.markdown('<div class="mm-footer">', unsafe_allow_html=True)

    st.markdown('<div class="mm-footer-top">', unsafe_allow_html=True)

    # ---------------- BRAND ----------------
    st.markdown("""
    <div class="mm-brand">
        <h1>MovieMind</h1>

        <p>
            Discover trending movies, personalized recommendations,
            chatbot support, analytics, and an immersive movie
            exploration experience powered by AI.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- GRID START ----------------
    st.markdown('<div class="mm-grid">', unsafe_allow_html=True)

    # ---------------- ADDRESS CARD ----------------
    st.markdown("""
    <div class="mm-card">

        <div class="mm-title">
            Address
        </div>

        <div class="mm-text">
            MovieMind Pvt. Ltd.<br>
            Sonipat, Haryana<br>
            India - 132103<br>
            support@moviemind.com
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ---------------- QUICK LINKS CARD ----------------
    st.markdown("""
    <div class="mm-card">

        <div class="mm-title">
            Quick Links
        </div>

    """, unsafe_allow_html=True)

    st.page_link("pages/about.py", label="About Us")
    st.page_link("pages/contact.py", label="Contact Us")
    st.page_link("pages/faq.py", label="FAQ")
    st.page_link("pages/privacy.py", label="Privacy Policy")
    st.page_link("pages/terms.py", label="Terms & Conditions")

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- BROWSE MOVIES CARD ----------------
    st.markdown("""
    <div class="mm-card">

        <div class="mm-title">
            Browse Movies
        </div>

    """, unsafe_allow_html=True)

    st.page_link("pages/year.py", label="Browse by Year")
    st.page_link("pages/industry.py", label="Browse by Industry")
    st.page_link("pages/category.py", label="Browse by Category")

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- SOCIAL CARD ----------------
    st.markdown("""
    <div class="mm-card">

        <div class="mm-title">
            Follow Us
        </div>

        <div class="mm-text">
            Stay connected with MovieMind across social platforms.
        </div>

        <div class="mm-social">

            <a href="https://facebook.com" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/124/124010.png">
            </a>

            <a href="https://instagram.com" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/2111/2111463.png">
            </a>

            <a href="https://twitter.com" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/733/733579.png">
            </a>

            <a href="https://linkedin.com" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/145/145807.png">
            </a>

        </div>

    </div>
    """, unsafe_allow_html=True)

    # ---------------- GRID END ----------------
    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- BOTTOM ----------------
    st.markdown("""
    <div class="mm-bottom">
        © 2026 MovieMind. All Rights Reserved.
    </div>
    """, unsafe_allow_html=True)

    # ---------------- CLOSE ----------------
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)