
import pandas as pd

from src.url_features import extract_url_features


DATASET_PATH = "data/phishing_dataset.xlsx"
OUTPUT_PATH = "data/ml_features.csv"


def prepare_dataset():
    # Load the original dataset
    df = pd.read_excel(DATASET_PATH)

    # Check required columns
    required_columns = {"URLs", "Labels"}

    if not required_columns.issubset(df.columns):
        raise ValueError("Dataset must contain URLs and Labels columns.")

    feature_rows = []
    skipped_urls = 0

    # Extract features from every URL
    for url in df["URLs"]:
        try:
            features = extract_url_features(url)

            # Convert features into numerical values
            row = {
                "url_length": features["url_length"],
                "uses_https": int(features["uses_https"]),
                "has_at_symbol": int(features["has_at_symbol"]),
                "host_is_ip": int(features["host_is_ip"]),
                "subdomain_count": features["subdomain_count"],
                "has_hyphen_in_hostname": int(
                    features["has_hyphen_in_hostname"]
                ),
                "uses_url_shortener": int(
                    features["uses_url_shortener"]
                ),
                "matched_keyword_count": len(
                    features["matched_keywords"]
                ),

                # Three additional features
                "hostname_length": features["hostname_length"],
                "path_length": features["path_length"],
                "hostname_digit_count": features["hostname_digit_count"],
            }

            feature_rows.append(row)

        except ValueError:
            skipped_urls += 1
            feature_rows.append(None)

    # Keep only successfully processed URLs and their labels
    valid_indices = [
        index for index, row in enumerate(feature_rows)
        if row is not None
    ]

    X = pd.DataFrame(
        [feature_rows[index] for index in valid_indices]
    )

    y = df.loc[valid_indices, "Labels"].reset_index(drop=True)

    # Combine features and labels
    prepared_df = X.copy()
    prepared_df["label"] = y

    # Save the prepared dataset
    prepared_df.to_csv(OUTPUT_PATH, index=False)

    print("Dataset preparation complete!")
    print("Original URLs:", len(df))
    print("Successfully processed:", len(X))
    print("Skipped URLs:", skipped_urls)

    print("\nPrepared dataset shape:", prepared_df.shape)

    print("\nFeatures included:")
    print(list(X.columns))

    print("\nLabel distribution:")
    print(y.value_counts())

    print("\nFirst five prepared rows:")
    print(prepared_df.head())

    print("\nSaved to:", OUTPUT_PATH)


if __name__ == "__main__":
    prepare_dataset()
