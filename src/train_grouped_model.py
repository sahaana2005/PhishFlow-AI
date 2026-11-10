
import pandas as pd

from urllib.parse import urlsplit
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)


# 1. Load the datasets
features = pd.read_csv("data/ml_features.csv")
original = pd.read_excel("data/phishing_dataset.xlsx")

if len(features) != len(original):
    raise ValueError("Feature and original dataset row counts do not match.")

# Attach original URLs to their corresponding extracted features
df = features.copy()
df["URL"] = original["URLs"].values

print("\nGROUPED MODEL EVALUATION")
print("=" * 50)

# 2. Check for conflicting labels on duplicate URLs
conflicting_urls = (
    df.groupby("URL")["label"].nunique()
)

conflicting_count = (conflicting_urls > 1).sum()

print("Conflicting duplicate URLs:", conflicting_count)

if conflicting_count > 0:
    raise ValueError(
        "Some duplicate URLs have conflicting labels. "
        "Investigate them before continuing."
    )

# 3. Remove exact duplicate URLs
before = len(df)
df = df.drop_duplicates(subset=["URL"]).reset_index(drop=True)

print("URLs before deduplication:", before)
print("URLs after deduplication:", len(df))
print("Duplicates removed:", before - len(df))


# 4. Extract hostnames for grouping
def get_hostname(url):
    try:
        return urlsplit(url).hostname.lower().rstrip(".")
    except (ValueError, AttributeError):
        return None


df["hostname"] = df["URL"].apply(get_hostname)

if df["hostname"].isna().any():
    raise ValueError("Some URLs have missing hostnames.")

# 5. Separate features, labels and groups
X = df.drop(columns=["label", "URL", "hostname"])
y = df["label"]
groups = df["hostname"]

print("\nDataset size:", len(df))
print("Unique hostnames:", groups.nunique())
print("Overall label distribution:")
print(y.value_counts().sort_index())


# 6. Create a hostname-grouped split
splitter = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)

train_indices, test_indices = next(
    splitter.split(X, y, groups)
)

X_train = X.iloc[train_indices]
X_test = X.iloc[test_indices]

y_train = y.iloc[train_indices]
y_test = y.iloc[test_indices]

train_hosts = set(groups.iloc[train_indices])
test_hosts = set(groups.iloc[test_indices])

overlap = train_hosts.intersection(test_hosts)

print("\nTRAIN/TEST SPLIT")
print("=" * 50)

print("Training URLs:", len(X_train))
print("Testing URLs:", len(X_test))
print("Training hostnames:", len(train_hosts))
print("Testing hostnames:", len(test_hosts))
print("Overlapping hostnames:", len(overlap))

print("\nTraining label distribution:")
print(y_train.value_counts().sort_index())

print("\nTesting label distribution:")
print(y_test.value_counts().sort_index())

if overlap:
    raise ValueError("Hostname overlap detected!")

# 7. Train the Random Forest model
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    random_state=42,
    n_jobs=-1,
)

model.fit(X_train, y_train)

# 8. Evaluate the model
predictions = model.predict(X_test)

print("\nMODEL PERFORMANCE")
print("=" * 50)

print("Accuracy:", round(accuracy_score(y_test, predictions), 4))
print("Precision:", round(precision_score(y_test, predictions), 4))
print("Recall:", round(recall_score(y_test, predictions), 4))
print("F1 Score:", round(f1_score(y_test, predictions), 4))

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        target_names=["Legitimate", "Phishing"],
    )
)

print("Confusion Matrix:")
print(confusion_matrix(y_test, predictions))

# 9. Feature importance
importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_,
})

importance = importance.sort_values(
    by="Importance",
    ascending=False,
)

print("\nFEATURE IMPORTANCE")
print("=" * 50)
print(importance.to_string(index=False))
# 10. Save model errors for investigation

test_results = df.iloc[test_indices].copy()

test_results["actual_label"] = y_test.values
test_results["predicted_label"] = predictions

false_negatives = test_results[
    (test_results["actual_label"] == 1) &
    (test_results["predicted_label"] == 0)
]

false_positives = test_results[
    (test_results["actual_label"] == 0) &
    (test_results["predicted_label"] == 1)
]

false_negatives.to_csv(
    "reports/grouped_false_negatives.csv",
    index=False,
)

false_positives.to_csv(
    "reports/grouped_false_positives.csv",
    index=False,
)

print("\nERROR ANALYSIS FILES SAVED")
print("False negatives:", len(false_negatives))
print("False positives:", len(false_positives))

print("\nGROUPED EVALUATION COMPLETED!")
