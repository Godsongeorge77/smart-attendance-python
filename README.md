# SmartAttend AI — Python & Streamlit Edition

A complete Python & Streamlit rewrite of the **Smart Attendance Management System**, featuring:
- **Dashboard**: Real-time metrics (Enrolled Profiles, Present Today, Late Arrivals, Turnout %) and daily check-in overview.
- **Live Face Scanner**: Browser camera snapshot capture (`st.camera_input`) with OpenCV Haar-Cascade facial detection, confidence scoring, daily deduplication, and automatic late-arrival flagging (after 09:00 AM).
- **Enroll Profile**: Register students or staff with persistent SQLite storage.
- **Attendance Logs**: Searchable audit trail with one-click CSV report download.

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Upload `app.py`, `database.py`, `requirements.txt`, and `README.md` to the root of a GitHub repository.
2. On [share.streamlit.io](https://share.streamlit.io), select your repository, set **Branch** to `main` and **Main file path** to `app.py`, and click **Deploy**.
