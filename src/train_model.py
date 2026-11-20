
import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

FEATURES_PATH = BASE_DIR / "data" / "ml_features.csv"
ORIGINAL_DATASET_PATH = BASE_DIR / "data" / "phishing_dataset.xlsx"

MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"

MODEL_PATH = MODEL_DIR / "phishflow_random_forest.pkl"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOAD DATASETS
# --------------------------------------------------

features_df = pd.read_csv(FEATURES_PATH)
original_df = pd.read_excel(ORIGINAL_DATASET_PATH)

if len(features_df) != len(original_df):
    raise ValueError("Feature dataset and original dataset have different row counts.")

if "label" not in features_df.columns:
    raise ValueError("Missing 'label' column in feature dataset.")

if "URLs" not in original_df.columns:
    raise ValueError("Missing 'URLs' column in original dataset.")

if features_df["label"].isna().any():
    raise ValueError("Missing values found in label column.")

# Keep the original row index so URLs remain correctly aligned
features_df = features_df.copy()


# --------------------------------------------------
# 3. SEPARATE FEATURES AND LABELS
# --------------------------------------------------

X = features_df.drop(columns=["label"])
y = features_df["label"].astype(int)

original_urls = original_df["URLs"]

if X.isna().any().any():
    raise ValueError("Missing feature values found. Clean the dataset first.")

if not set(y.unique()).issubset({0, 1}):
    raise ValueError("Labels must be 0 (Legitimate) or 1 (Phishing).")

feature_names = list(X.columns)


# --------------------------------------------------
# 4. SPLIT DATA INTO TRAINING AND TESTING
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

print("\nDATASET INFORMATION")
print("=" * 55)

print("Total samples:", len(X))
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

print("\nTraining label distribution:")
print(y_train.value_counts())

print("\nTesting label distribution:")
print(y_test.value_counts())


# --------------------------------------------------
# 5. DEFINE MACHINE LEARNING MODELS
# --------------------------------------------------

models = {
    "Decision Tree": DecisionTreeClassifier(
        max_depth=5,
        random_state=42,
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
        n_jobs=-1,
    ),
}


# --------------------------------------------------
# 6. TRAIN AND EVALUATE MODELS
# --------------------------------------------------

model_results = {}

for name, model in models.items():

    print("\n" + "=" * 55)
    print(name.upper())
    print("=" * 55)

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    model_results[name] = {
        "model": model,
        "predictions": y_pred,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
    }

    print("\nMODEL PERFORMANCE")
    print("-" * 40)

    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-score:  {f1:.4f}")

    print("\nCLASSIFICATION REPORT")

    print(
        classification_report(
            y_test,
            y_pred,
            labels=[0, 1],
            target_names=["Legitimate", "Phishing"],
            zero_division=0,
        )
    )

    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, y_pred, labels=[0, 1]))

    importance = pd.Series(
        model.feature_importances_,
        index=feature_names,
    ).sort_values(ascending=False)

    print("\nFEATURE IMPORTANCE")
    print(importance.round(4))


# --------------------------------------------------
# 7. COMPARE MODELS
# --------------------------------------------------

print("\n" + "=" * 65)
print("FINAL MODEL COMPARISON")
print("=" * 65)

comparison = pd.DataFrame({
    name: {
        "Accuracy": result["accuracy"],
        "Precision": result["precision"],
        "Recall": result["recall"],
        "F1-score": result["f1_score"],
    }
    for name, result in model_results.items()
}).T

print(comparison.round(4))


# --------------------------------------------------
# 8. SELECT RANDOM FOREST
# --------------------------------------------------

selected_model_name = "Random Forest"
selected_result = model_results[selected_model_name]

y_pred = selected_result["predictions"]

test_urls = original_urls.iloc[X_test.index].to_numpy()

results_df = pd.DataFrame({
    "URL": test_urls,
    "Actual": y_test.to_numpy(),
    "Predicted": y_pred,
})


# --------------------------------------------------
# 9. FALSE POSITIVE AND FALSE NEGATIVE ANALYSIS
# --------------------------------------------------

false_negatives = results_df[
    (results_df["Actual"] == 1) &
    (results_df["Predicted"] == 0)
]

false_positives = results_df[
    (results_df["Actual"] == 0) &
    (results_df["Predicted"] == 1)
]

print("\n" + "=" * 65)
print("RANDOM FOREST ERROR ANALYSIS")
print("=" * 65)

print("\nFALSE NEGATIVES:", len(false_negatives))
print("Phishing URLs incorrectly classified as legitimate.")

print(false_negatives["URL"].head(10).to_string(index=False)
      if len(false_negatives) else "None found.")

print("\nFALSE POSITIVES:", len(false_positives))
print("Legitimate URLs incorrectly classified as phishing.")

print(false_positives["URL"].head(10).to_string(index=False)
      if len(false_positives) else "None found.")


# --------------------------------------------------
# 10. SAVE ERROR ANALYSIS REPORTS
# --------------------------------------------------

false_negatives.to_csv(
    REPORT_DIR / "random_forest_false_negatives.csv",
    index=False,
)

false_positives.to_csv(
    REPORT_DIR / "random_forest_false_positives.csv",
    index=False,
)

print("\nError reports saved in the reports folder.")


# --------------------------------------------------
# 11. SAVE TRAINED RANDOM FOREST MODEL
# --------------------------------------------------

joblib.dump(
    {
        "model": selected_result["model"],
        "features": feature_names,
        "metrics": {
            "accuracy": selected_result["accuracy"],
            "precision": selected_result["precision"],
            "recall": selected_result["recall"],
            "f1_score": selected_result["f1_score"],
        },
    },
    MODEL_PATH,
)

print("\nMODEL SAVED SUCCESSFULLY")
print("Location:", MODEL_PATH)


# --------------------------------------------------
# 12. FINISH
# --------------------------------------------------

print("\nPHISHFLOW-AI TRAINING COMPLETED!")
