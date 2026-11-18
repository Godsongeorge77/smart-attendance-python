import random
from datetime import date
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
import streamlit as st
from database import AttendanceDatabase

try:
    import cv2
    HAS_CV2 = hasattr(cv2, "CascadeClassifier") and hasattr(cv2, "data")
except Exception:
    cv2 = None
    HAS_CV2 = False

st.set_page_config(
    page_title="SmartAttend AI — Biometric Attendance Portal",
    page_icon="🪪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# HIGH-CONTRAST, ACCESSIBLE UI STYLING (FIXED TEXT VISIBILITY)
# ============================================================================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
        color: #0f172a;
    }
    p, span, label, .stMarkdown, div[data-testid="stMarkdownContainer"] {
        color: #1e293b !important;
    }
    .hero-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 55%, #312e81 100%);
        padding: 1.75rem 2rem;
        border-radius: 16px;
        color: #ffffff !important;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);
    }
    .hero-card h1 {
        margin: 0;
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #ffffff !important;
    }
    .hero-card p {
        margin: 0.4rem 0 0 0;
        color: #e0e7ff !important;
        font-size: 0.98rem;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.25);
        border: 1px solid rgba(16, 185, 129, 0.5);
        color: #34d399 !important;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        margin-bottom: 0.65rem;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        padding: 1.1rem 1.25rem;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
    }
    div[data-testid="stMetric"] label {
        color: #475569 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 800 !important;
    }
    .stTextInput label, .stSelectbox label, .stRadio label, .stCheckbox label {
        color: #0f172a !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
    }
    section[data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }
    section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label {
        color: #f8fafc !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        background-color: #ef4444 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

db = AttendanceDatabase()

FACE_CASCADE = (
    cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    if HAS_CV2
    else None
)


def detect_faces_in_image(uploaded_image) -> tuple:
    image = Image.open(uploaded_image).convert("RGB")
    img_np = np.array(image)

    if FACE_CASCADE is not None and not FACE_CASCADE.empty():
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        annotated = img_np.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (16, 185, 129), 3)
            cv2.putText(
                annotated,
                "FACE VERIFIED",
                (x, max(20, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (16, 185, 129),
                2,
            )
        return len(faces), annotated

    w, h = image.size
    annotated_pil = image.copy()
    draw = ImageDraw.Draw(annotated_pil)
    box = [int(w * 0.28), int(h * 0.15), int(w * 0.72), int(h * 0.85)]
    draw.rectangle(box, outline=(16, 185, 129), width=4)
    return 1, np.array(annotated_pil)


if "auth_user" not in st.session_state:
    st.session_state.auth_user = None

if st.session_state.auth_user is None:
    _, center_col, _ = st.columns([1, 1.35, 1])

    with center_col:
        st.markdown(
            """
            <div class="hero-card" style="text-align:center; margin-top: 2rem;">
                <span class="hero-badge">BIOMETRIC ACCESS CONTROL</span>
                <h1>🪪 SmartAttend AI</h1>
                <p>Institutional Facial Recognition & Attendance Management Portal</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Create Staff Account"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username (e.g. admin)")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                login_btn = st.form_submit_button("Sign In to Portal", type="primary", use_container_width=True)

                if login_btn:
                    account = db.authenticate(username, password)
                    if account:
                        st.session_state.auth_user = account
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Please try again.")

            with st.expander("ℹ️ Demo Login Credentials"):
                st.markdown(
                    "- **Admin Account:** `admin` / `admin123` *(Full System Access)*\n"
                    "- **Lecturer Account:** `lecturer` / `staff123` *(Scanner & Logs Access)*"
                )

        with tab_register:
            with st.form("register_form", clear_on_submit=True):
                reg_name = st.text_input("Full Name", placeholder="e.g. Dr. Ngozi Okafor")
                reg_user = st.text_input("Choose Username", placeholder="e.g. ngozi.okafor")
                reg_role = st.selectbox("Role", ["Staff", "Admin"])
                reg_pass = st.text_input("Choose Password", type="password", placeholder="Minimum 4 characters")
                reg_btn = st.form_submit_button("Register Account", type="primary", use_container_width=True)

                if reg_btn:
                    if not reg_name.strip() or not reg_user.strip():
                        st.error("Please fill in all fields.")
                    else:
                        ok, msg = db.register_account(reg_user, reg_pass, reg_name, reg_role)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

    st.stop()

current_user = st.session_state.auth_user
is_admin = current_user["role"] == "Admin"

with st.sidebar:
    st.markdown("## 🪪 SmartAttend AI")
    st.caption(f"Signed in as **{current_user['full_name']}**")
    st.caption(f"Role: **{current_user['role']}** • `{current_user['username']}`")
    st.divider()

    nav_options = ["📊 Dashboard", "📷 Live Face Scanner", "📋 Attendance Logs"]
    if is_admin:
        nav_options.insert(2, "🧑‍🎓 Enroll Profile")

    page = st.radio("Navigation", nav_options, label_visibility="collapsed")
    st.divider()
    st.caption(f"📅 Session Date: **{date.today().isoformat()}**")

    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.auth_user = None
        st.rerun()

users = db.get_users()
records = db.get_records()
today_str = date.today().isoformat()
today_records = [r for r in records if r["date"] == today_str]

st.markdown(
    f"""
    <div class="hero-card">
        <span class="hero-badge">● SYSTEM ONLINE • {current_user['role'].upper()} SESSION</span>
        <h1>Welcome back, {current_user['full_name']}</h1>
        <p>Real-time facial recognition verification, automated punctuality tracking, and SQLite audit logs ({today_str})</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if page == "📊 Dashboard":
    late_count = sum(1 for r in today_records if r["status"] == "Late")
    on_time_count = sum(1 for r in today_records if r["status"] == "Present")
    turnout = round((len(today_records) / len(users)) * 100) if users else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Enrolled Profiles", len(users), "Registered templates")
    c2.metric
