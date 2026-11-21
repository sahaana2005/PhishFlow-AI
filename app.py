
from flask import Flask, render_template, request
import joblib
import os
import sqlite3
import sys
import pandas as pd

from pathlib import Path
from datetime import datetime

# --------------------------------------------------
# 1. PROJECT SETUP
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

MODEL_PATH = BASE_DIR / "models" / "phishflow_random_forest.pkl"
DATABASE_PATH = BASE_DIR / "phishflow.db"

# Vercel's project folder may be read-only.
# Use /tmp as a fallback.
if not os.access(BASE_DIR, os.W_OK):
    DATABASE_PATH = Path("/tmp/phishflow.db")

MAX_URL_LENGTH = 2048

sys.path.insert(0, str(SRC_DIR))

from url_features import extract_url_features
from domain_checker import check_trusted_domain

app = Flask(__name__)

# --------------------------------------------------
# 2. LOAD TRAINED MODEL
# --------------------------------------------------

saved_data = joblib.load(MODEL_PATH)

model = saved_data["model"]
feature_names = saved_data["features"]


# --------------------------------------------------
# 3. DATABASE SETUP
# --------------------------------------------------

def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                scanned_at TEXT NOT NULL
            )
        """)

        connection.commit()

    finally:
        connection.close()


# --------------------------------------------------
# 4. SAVE SCAN
# --------------------------------------------------

def save_scan(url, prediction, confidence):
    connection = get_db_connection()

    try:
        connection.execute("""
            INSERT INTO scan_history
            (url, prediction, confidence, scanned_at)
            VALUES (?, ?, ?, ?)
        """, (
            url,
            prediction,
            confidence,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        connection.commit()

    finally:
        connection.close()


# --------------------------------------------------
# 5. GET SCAN HISTORY
# --------------------------------------------------

def get_scan_history():
    connection = get_db_connection()

    try:
        history = connection.execute("""
            SELECT * FROM scan_history
            ORDER BY id DESC
            LIMIT 20
        """).fetchall()

        return history

    finally:
        connection.close()


# --------------------------------------------------
# 6. GET DASHBOARD ANALYTICS
# --------------------------------------------------

def get_dashboard_stats():
    connection = get_db_connection()

    try:
        stats = connection.execute("""
            SELECT
                COUNT(*) AS total_scans,

                COALESCE(SUM(CASE
                    WHEN prediction = 'Potential Phishing'
                    THEN 1 ELSE 0
                END), 0) AS phishing_scans,

                COALESCE(SUM(CASE
                    WHEN prediction = 'Likely Legitimate'
                    THEN 1 ELSE 0
                END), 0) AS legitimate_scans

            FROM scan_history
        """).fetchone()

        total = stats["total_scans"]
        phishing = stats["phishing_scans"]
        legitimate = stats["legitimate_scans"]

        return {
            "total_scans": total,
            "phishing_scans": phishing,
            "legitimate_scans": legitimate,

            "phishing_percent": round(
                (phishing / total) * 100, 1
            ) if total else 0,

            "legitimate_percent": round(
                (legitimate / total) * 100, 1
            ) if total else 0
        }

    finally:
        connection.close()


# --------------------------------------------------
# 7. MAIN PAGE AND URL SCANNER
# --------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    error = None
    scanned_url = ""

    if request.method == "POST":

        scanned_url = request.form.get("url", "").strip()

        try:

            # Validate empty input
            if not scanned_url:
                raise ValueError("Please enter a URL.")

            # Validate URL length
            if len(scanned_url) > MAX_URL_LENGTH:
                raise ValueError(
                    "URL is too long. Maximum allowed length is 2048 characters."
                )

            # Extract URL features
            features = extract_url_features(scanned_url)

            # Arrange features in the same order as model training
            input_data = pd.DataFrame(
                [[features[name] for name in feature_names]],
                columns=feature_names
            )

            # ------------------------------------------
            # MACHINE LEARNING PREDICTION
            # ------------------------------------------

            prediction = int(model.predict(input_data)[0])

            probabilities = model.predict_proba(input_data)[0]

            phishing_index = list(model.classes_).index(1)

            phishing_score = round(
                float(probabilities[phishing_index]) * 100, 2
            )

            ml_label = (
                "Potential Phishing"
                if prediction == 1
                else "Likely Legitimate"
            )

            # ------------------------------------------
            # TRUSTED DOMAIN VERIFICATION
            # ------------------------------------------

            trusted_domain = check_trusted_domain(scanned_url)

            domain_status = (
                "Trusted domain match"
                if trusted_domain
                else "No trusted domain match"
            )

            # ------------------------------------------
            # FINAL RESULT
            # ------------------------------------------

            result = {
                # Original ML assessment
                "label": ml_label,
                "is_phishing": prediction == 1,
                "confidence": phishing_score,

                # Separate trusted-domain assessment
                "trusted_domain": trusted_domain,
                "domain_status": domain_status,

                # Extracted URL features
                "features": features,
            }

            # Save original ML prediction to scan history
            save_scan(
                scanned_url,
                ml_label,
                phishing_score
            )

        except (ValueError, TypeError, KeyError) as e:
            error = str(e)

        except Exception:
            app.logger.exception(
                "Unexpected error during URL analysis"
            )

            error = (
                "Unable to analyze this URL. "
                "Please check the input and try again."
            )

    # Fetch scan history and analytics
    history = get_scan_history()
    stats = get_dashboard_stats()

    return render_template(
        "index.html",
        result=result,
        error=error,
        scanned_url=scanned_url,
        history=history,
        stats=stats
    )


# --------------------------------------------------
# 8. START APPLICATION
# --------------------------------------------------

initialize_database()

if __name__ == "__main__":
    app.run(debug=False)
