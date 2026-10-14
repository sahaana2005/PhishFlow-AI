
from url_features import extract_url_features
from detection_engine import detect_suspicious_patterns


def main():
    url = input("Enter a URL to analyse: ")

    try:
        features = extract_url_features(url)
        result = detect_suspicious_patterns(features)

        print("\nExtracted features:")
        for name, value in features.items():
            print(f"{name}: {value}")

        print("\nDetection result:")
        if result["suspicious"]:
            print("Warning: suspicious patterns detected.")
            for warning in result["warnings"]:
                print(f"- {warning}")
        else:
            print("No configured warning rules were triggered.")

        print("\nNote: This result does not prove whether a URL is safe or malicious.")

    except ValueError as error:
        print(f"\nInvalid input: {error}")


if __name__ == "__main__":
    main()
