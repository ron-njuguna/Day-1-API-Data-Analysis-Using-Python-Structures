from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import requests

API_URL = "https://jsonplaceholder.typicode.com/users"
OUTPUT_DIR = Path("output")


def get_customers(url: str = API_URL) -> list[dict]:
    """Fetch the customer list. Report failures clearly instead of crashing."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            print("Request succeeded, but the API response was not a list.")
            return []
        return data
    except requests.RequestException as exc:
        print(f"Could not retrieve customer data: {exc}")
    except ValueError as exc:
        print(f"Could not parse the API response as JSON: {exc}")
    return []


def explore(record: dict, indent: int = 0) -> None:
    """Print every key in a (possibly nested) record with its type, indented by depth."""
    if isinstance(record, dict):
        for key, value in record.items():
            print(" " * indent + f"{key}: {type(value).__name__}")
            if isinstance(value, (dict, list)):
                explore(value, indent + 2)
    elif isinstance(record, list):
        for index, value in enumerate(record):
            print(" " * indent + f"[{index}]: {type(value).__name__}")
            if isinstance(value, (dict, list)):
                explore(value, indent + 2)


def extract_attributes(customers: list[dict]) -> list[dict]:
    """Return one flat dict per customer with the attributes listed in the task."""
    rows = []
    for customer in customers:
        address = customer.get("address") or {}
        geo = address.get("geo") or {}
        email = customer.get("email", "")
        rows.append({
            "customer_id": customer.get("id"),
            "name": customer.get("name", ""),
            "username": customer.get("username", ""),
            "email": email,
            "email_domain": email.rsplit(".", 1)[-1].lower() if "." in email else "",
            "phone": customer.get("phone", ""),
            "city": address.get("city", ""),
            "zipcode": address.get("zipcode", ""),
            "latitude": float(geo["lat"]) if geo.get("lat") not in (None, "") else float("nan"),
            "longitude": float(geo["lng"]) if geo.get("lng") not in (None, "") else float("nan"),
            "company": (customer.get("company") or {}).get("name", ""),
            "website": customer.get("website", ""),
        })
    return rows


def unique_cities(customers: list[dict]) -> set[str]:
    """Return the set of distinct cities."""
    return {((customer.get("address") or {}).get("city", "")) for customer in customers}


def city_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per city using a loop and/or a dict comprehension (no Counter, no pandas)."""
    counts = {}
    for customer in customers:
        city = (customer.get("address") or {}).get("city", "")
        counts[city] = counts.get(city, 0) + 1
    return counts


def email_domain_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per email top-level domain (e.g. 'biz', 'tv')."""
    domains = [
        customer.get("email", "").rsplit(".", 1)[-1].lower()
        for customer in customers
        if "@" in customer.get("email", "")
    ]
    unique_domains = set(domains)
    return {domain: sum(1 for item in domains if item == domain) for domain in unique_domains}


def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    """Convert flattened customer rows into a pandas DataFrame."""
    return pd.DataFrame(rows)


def plot_distribution(counts: dict[str, int], path: Path) -> None:
    """Save a labelled chart of the distribution to path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    labels = [item[0] for item in ordered]
    values = [item[1] for item in ordered]
    fig_width = max(8, len(labels) * 0.8)
    fig, ax = plt.subplots(figsize=(fig_width, 5))
    ax.bar(labels, values)
    ax.set_title("Pesa Pulse: Customers by Email Domain")
    ax.set_xlabel("Email domain")
    ax.set_ylabel("Number of customers")
    ax.tick_params(axis="x", labelrotation=35)
    for label in ax.get_xticklabels():
        label.set_ha("right")
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    customers = get_customers()
    if not customers:
        print("No data was retrieved; outputs were not generated.")
        return

    print("Nested structure of the first customer:")
    explore(customers[0])

    rows = extract_attributes(customers)
    cities = unique_cities(customers)
    counts = city_counts(customers)
    domain_counts = email_domain_counts(customers)

    print(f"\nCustomers retrieved : {len(customers)}")
    print(f"Unique cities       : {len(cities)}")
    sorted_cities = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    most_common_city, most_common_count = sorted_cities[0]
    print(f"Most common city    : {most_common_city} ({most_common_count})")
    print(f"Email domains       : {dict(sorted(domain_counts.items(), key=lambda item: (-item[1], item[0])))}")

    df = to_dataframe(rows)
    df.to_csv(OUTPUT_DIR / "customers.csv", index=False)

    # Confirm pandas agrees with the plain-Python city aggregation.
    pandas_counts = df["city"].value_counts().to_dict()
    if pandas_counts != counts:
        raise AssertionError(f"City count mismatch: Python={counts}, pandas={pandas_counts}")
    city_df = pd.DataFrame(
        sorted(counts.items(), key=lambda item: (-item[1], item[0])),
        columns=["city", "customer_count"],
    )
    city_df.to_csv(OUTPUT_DIR / "city_counts.csv", index=False)

    print("\nDataFrame shape:", df.shape)
    print("DataFrame dtypes:")
    print(df.dtypes.to_string())
    print("\nPandas city counts agree with the plain-Python counts.")

    plot_distribution(domain_counts, OUTPUT_DIR / "customer_distribution.png")
    print("Chart saved to      : output/customer_distribution.png")


if __name__ == "__main__":
    main()
