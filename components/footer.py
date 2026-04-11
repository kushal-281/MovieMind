import streamlit as st

def show_footer():

    st.markdown("""
    <style>
    .footer {
        margin-top: 50px;
        padding: 30px 0;
        border-top: 1px solid #ddd;
        font-size: 14px;
        color: #555;
    }

    .footer-title {
        font-weight: bold;
        margin-bottom: 10px;
    }

    .social-icons img {
        width: 26px;
        margin-right: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="footer">', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    # ---------------- COLUMN 1 (ADDRESS) ----------------
    with col1:
        st.markdown('<div class="footer-title">Address</div>', unsafe_allow_html=True)
        st.write("MovieMind Pvt. Ltd.")
        st.write("Panipat, Haryana")
        st.write("India - 132103")
        st.write("Email: support@moviemind.com")

    # ---------------- COLUMN 2 (VISIT / PAGES) ----------------
    with col2:
        st.markdown('<div class="footer-title">Visit</div>', unsafe_allow_html=True)

        st.page_link("pages/about.py", label="About Us")
        st.page_link("pages/contact.py", label="Contact Us")
        st.page_link("pages/privacy.py", label="Privacy Policy")
        st.page_link("pages/terms.py", label="Terms & Conditions")

    # ---------------- COLUMN 3 (MOVIE BY) ----------------
    with col3:
        st.markdown('<div class="footer-title">Movie By</div>', unsafe_allow_html=True)

        st.page_link("pages/year.py", label="Year")
        st.page_link("pages/industry.py", label="Industry")
        st.page_link("pages/category.py", label="Category")

    # ---------------- COLUMN 4 (SOCIAL MEDIA) ----------------
    with col4:
        st.markdown('<div class="footer-title">Follow Us</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="social-icons">
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
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; color:#888;">
    © 2026 MovieMind. All Rights Reserved.
    </div>
    """, unsafe_allow_html=True)