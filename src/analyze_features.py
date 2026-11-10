
import pandas as pd

df = pd.read_csv("data/ml_features.csv")

print("\nFEATURE ANALYSIS")
print("=" * 50)

print("\n1. HTTPS usage by class")
print(
    df.groupby("label")["uses_https"]
    .value_counts(normalize=True)
    .unstack(fill_value=0)
    .round(3)
)

print("\n2. Average URL length by class")
print(
    df.groupby("label")["url_length"]
    .agg(["mean", "median", "min", "max"])
    .round(2)
)

print("\n3. Average subdomain count by class")
print(
    df.groupby("label")["subdomain_count"]
    .agg(["mean", "median", "max"])
    .round(2)
)

print("\n4. Hyphen usage by class")
print(
    df.groupby("label")["has_hyphen_in_hostname"]
    .value_counts(normalize=True)
    .unstack(fill_value=0)
    .round(3)
)

print("\nFEATURE ANALYSIS COMPLETED!")
