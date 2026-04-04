import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

cookies = EncryptedCookieManager(
    prefix="moviemind_",
    password="super_secret_key"
)

if not cookies.ready():
    st.stop()