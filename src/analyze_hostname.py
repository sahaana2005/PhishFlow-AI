
import pandas as pd
from urllib.parse import urlsplit

df = pd.read_excel("data/phishing_dataset.xlsx")


def get_hostname(url):
    try:
        return urlsplit(url).hostname or ""
    except ValueError:
        return ""


df["hostname"] = df["URLs"].apply(get_hostname)

df["hostname_length"] = df["hostname"].str.len()

df["path_length"] = df["URLs"].apply(
    lambda url: len(urlsplit(url).path)
)

df["hostname_digit_count"] = df["hostname"].apply(
    lambda host: sum(char.isdigit() for char in host)
)

print("\nHOSTNAME FEATURE ANALYSIS")
print("=" * 50)

for feature in [
    "hostname_length",
    "path_length",
    "hostname_digit_count",
]:
    print(f"\n{feature}")
    print(
        df.groupby("Labels")[feature]
        .agg(["mean", "median", "max"])
        .round(2)
    )

print("\nANALYSIS COMPLETED!")
