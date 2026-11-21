
from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

from url_features import extract_url_features


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "phishing_dataset.xlsx"
MODEL_PATH = BASE_DIR / "models" / "phishflow_random_forest.pkl"
REPORT_PATH = BASE_DIR / "reports"

REPORT_PATH.mkdir(exist_ok=True)


def load_dataset():
    df = pd.read_excel(DATA_PATH)

    df = df.dropna(subset=["URLs", "Labels"]).copy()

    # Convert source labels into numeric labels
    df["label"] = df["Labels"].map({
        "Legitimate": 0,
        "Phishing": 1,
        0: 0,
        1: 1
    })

    df = df.dropna(subset=["label"])

    rows = []

    for _, row in df.iterrows():
        try:
            features = extract_url_features(row["URLs"])
            features["label"] = int(row["label"])
            rows.append(features)
        except (ValueError, TypeError):
            continue

    return pd.DataFrame(rows)


def evaluate_model(name, model, X_test, y_test):
    predictions = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(
            y_test, predictions, zero_division=0
        ),
        "recall": recall_score(
            y_test, predictions, zero_division=0
        ),
        "f1_score": f1_score(
            y_test, predictions, zero_division=0
        ),
    }

    print(f"\n{name}")
    print("-" * 40)

    for metric, value in metrics.items():
        print(f"{metric}: {value * 100:.2f}%")

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, predictions))

    print("\nClassification Report:")
    print(classification_report(
        y_test, predictions,
        target_names=["Legitimate", "Phishing"],
        zero_division=0
    ))

    return metrics


def main():
    print("Loading and extracting URL features...")

    df = load_dataset()

    if df.empty:
        raise ValueError("No valid URL records were found.")

    feature_names = [
        column for column in df.columns if column != "label"
    ]

    X = df[feature_names]
    y = df["label"]

    print(f"\nDataset size: {len(df)}")
    print(f"Number of features: {len(feature_names)}")
    print("\nClass distribution:")
    print(y.value_counts())

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    models = {
        "Decision Tree": DecisionTreeClassifier(
            max_depth=5,
            random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42,
            n_jobs=-1
        )
    }

    results = {}

    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)

        results[name] = evaluate_model(
            name, model, X_test, y_test
        )

    best_name = max(
        results,
        key=lambda name: results[name]["f1_score"]
    )

    best_model = models[best_name]

    joblib.dump(
        {
            "model": best_model,
            "features": feature_names,
            "metrics": results[best_name],
        },
        MODEL_PATH
    )

    print(f"\nBest model: {best_name}")
    print(f"Saved model to: {MODEL_PATH}")

    print("\nTop feature importances:")

    importances = pd.Series(
        best_model.feature_importances_,
        index=feature_names
    ).sort_values(ascending=False)

    print(importances.to_string())

    importances.to_csv(
        REPORT_PATH / "feature_importance.csv"
    )


if __name__ == "__main__":
    main()
