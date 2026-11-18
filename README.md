# SmartAttend AI — Facial Recognition Attendance System (v2)

A modern, authenticated Python & Streamlit web portal for biometric institutional attendance management.

## Default Login Credentials
* **Administrator:** `admin` / `admin123` (Full access: Dashboard, Live Scanner, Enroll Profile, Attendance Logs)
* **Lecturer / Staff:** `lecturer` / `staff123` (Access: Dashboard, Live Scanner, Attendance Logs)

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Upload `app.py`, `database.py`, `requirements.txt`, and `README.md` to the root of your GitHub repository.
2. On [share.streamlit.io](https://share.streamlit.io), select your repository, set **Branch** to `main` and **Main file path** to `app.py`, and click **Deploy**.
