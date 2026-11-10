
import pandas as pd

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
# 1. LOAD DATASETS
# --------------------------------------------------

FEATURES_PATH = "data/ml_features.csv"
ORIGINAL_DATASET_PATH = "data/phishing_dataset.xlsx"

features_df = pd.read_csv(FEATURES_PATH)
original_df = pd.read_excel(ORIGINAL_DATASET_PATH)

# Check that both datasets have matching rows
if len(features_df) != len(original_df):
    raise ValueError(
        "The feature dataset and original dataset "
        "have different numbers of rows. "
        "Please prepare the feature dataset again."
    )

# Check required columns
if "label" not in features_df.columns:
    raise ValueError("The feature dataset must contain a 'label' column.")

if "URLs" not in original_df.columns:
    raise ValueError("The original dataset must contain a 'URLs' column.")


# --------------------------------------------------
# 2. SEPARATE FEATURES AND LABELS
# --------------------------------------------------

X = features_df.drop(columns=["label"])
y = features_df["label"]

# Keep original URLs for error analysis
original_urls = original_df["URLs"]


# --------------------------------------------------
# 3. SPLIT DATA INTO TRAINING AND TESTING SETS
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

print("\nDATASET INFORMATION")
print("=" * 50)

print("Total samples:", len(features_df))
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

print("\nTraining label distribution:")
print(y_train.value_counts())

print("\nTesting label distribution:")
print(y_test.value_counts())


# --------------------------------------------------
# 4. DEFINE MACHINE LEARNING MODELS
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
# 5. TRAIN, PREDICT AND EVALUATE EACH MODEL
# --------------------------------------------------

model_results = {}

for name, model in models.items():

    print("\n" + "=" * 50)
    print(name.upper())
    print("=" * 50)

    # Train model
    model.fit(X_train, y_train)

    # Predict on unseen test data
    y_pred = model.predict(X_test)

    # Calculate evaluation metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(
        y_test, y_pred, zero_division=0
    )
    recall = recall_score(
        y_test, y_pred, zero_division=0
    )
    f1 = f1_score(
        y_test, y_pred, zero_division=0
    )

    model_results[name] = {
        "model": model,
        "predictions": y_pred,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
    }

    # Display metrics
    print("\nMODEL PERFORMANCE")
    print("-" * 40)

    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-score:  {f1:.4f}")

    # Display classification report
    print("\nCLASSIFICATION REPORT")
    print("-" * 40)

    print(
        classification_report(
            y_test,
            y_pred,
            labels=[0, 1],
            target_names=["Legitimate", "Phishing"],
            zero_division=0,
        )
    )

    # Display confusion matrix
    print("CONFUSION MATRIX")
    print("-" * 40)

    print(confusion_matrix(y_test, y_pred, labels=[0, 1]))

    # Display feature importance
    importance = pd.Series(
        model.feature_importances_,
        index=X.columns,
    ).sort_values(ascending=False)

    print("\nFEATURE IMPORTANCE")
    print("-" * 40)

    print(importance.round(4))


# --------------------------------------------------
# 6. COMPARE BOTH MODELS
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
# 7. SELECT RANDOM FOREST FOR ERROR ANALYSIS
# --------------------------------------------------

selected_model_name = "Random Forest"
selected_result = model_results[selected_model_name]

y_pred = selected_result["predictions"]

# Recover original URLs using the test-set row positions
test_urls = original_urls.iloc[X_test.index].to_numpy()

# Create a results table
results_df = pd.DataFrame({
    "URL": test_urls,
    "Actual": y_test.to_numpy(),
    "Predicted": y_pred,
})


# --------------------------------------------------
# 8. IDENTIFY FALSE NEGATIVES AND FALSE POSITIVES
# --------------------------------------------------

# False negatives: Actual phishing, predicted legitimate
false_negatives = results_df[
    (results_df["Actual"] == 1) &
    (results_df["Predicted"] == 0)
]

# False positives: Actual legitimate, predicted phishing
false_positives = results_df[
    (results_df["Actual"] == 0) &
    (results_df["Predicted"] == 1)
]

print("\n" + "=" * 65)
print("ERROR ANALYSIS - RANDOM FOREST")
print("=" * 65)

print("\nFALSE NEGATIVES")
print("Actual phishing URLs incorrectly classified as legitimate.")
print("Total false negatives:", len(false_negatives))

print("\nFirst 10 false negative URLs:")

if len(false_negatives) > 0:
    print(
        false_negatives["URL"]
        .head(10)
        .to_string(index=False)
    )
else:
    print("No false negatives found.")


print("\nFALSE POSITIVES")
print("Actual legitimate URLs incorrectly classified as phishing.")
print("Total false positives:", len(false_positives))

print("\nFirst 10 false positive URLs:")

if len(false_positives) > 0:
    print(
        false_positives["URL"]
        .head(10)
        .to_string(index=False)
    )
else:
    print("No false positives found.")


# --------------------------------------------------
# 9. SAVE ERROR ANALYSIS REPORT
# --------------------------------------------------

false_negatives.to_csv(
    "reports/random_forest_false_negatives.csv",
    index=False,
)

false_positives.to_csv(
    "reports/random_forest_false_positives.csv",
    index=False,
)

print("\nError analysis reports saved:")
print("reports/random_forest_false_negatives.csv")
print("reports/random_forest_false_positives.csv")


# --------------------------------------------------
# 10. FINISH
# --------------------------------------------------

print("\nTRAINING AND EVALUATION COMPLETED!")
