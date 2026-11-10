
import pandas as pd

from urllib.parse import urlsplit
from sklearn.model_selection import train_test_split


# 1. Load original dataset
df = pd.read_excel("data/phishing_dataset.xlsx")

# 2. Check exact duplicate URLs
duplicate_urls = df["URLs"].duplicated().sum()

print("\nDATASET DUPLICATE AUDIT")
print("=" * 45)

print("Total URLs:", len(df))
print("Exact duplicate URLs:", duplicate_urls)

# 3. Extract hostnames
def get_hostname(url):
    try:
        return urlsplit(url).hostname.lower().rstrip(".")
    except (ValueError, AttributeError):
        return None


df["hostname"] = df["URLs"].apply(get_hostname)

print(
    "Unique hostnames:",
    df["hostname"].nunique()
)

# 4. Recreate the same train/test split
indices = df.index

train_indices, test_indices = train_test_split(
    indices,
    test_size=0.20,
    random_state=42,
    stratify=df["Labels"],
)

train_hosts = set(
    df.loc[train_indices, "hostname"].dropna()
)

test_hosts = set(
    df.loc[test_indices, "hostname"].dropna()
)

# 5. Find hostname overlap
overlapping_hosts = train_hosts.intersection(test_hosts)

print("\nHOSTNAME OVERLAP AUDIT")
print("=" * 45)

print("Unique training hostnames:", len(train_hosts))
print("Unique testing hostnames:", len(test_hosts))
print("Hostnames appearing in both:", len(overlapping_hosts))

if test_hosts:
    overlap_percentage = (
        len(overlapping_hosts) / len(test_hosts)
    ) * 100

    print(
        "Percentage of test hostnames also in training:",
        round(overlap_percentage, 2),
        "%"
    )

# 6. Show some overlapping hostnames
print("\nSAMPLE OVERLAPPING HOSTNAMES:")

for hostname in list(sorted(overlapping_hosts))[:15]:
    print(hostname)

print("\nAUDIT COMPLETED!")
