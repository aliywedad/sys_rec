import re
import pandas as pd


def _parse_price(raw: str) -> float | None:
    digits = re.sub(r"[^\d]", "", str(raw))
    if not digits:
        return None
    val = float(digits)
    return None if val <= 1 else val


def _parse_days_ago(date_str: str) -> int | None:
    s = str(date_str).lower().strip()
    m = re.search(r"(\d+)\s*(day|hour|minute|month|year)", s)
    if not m:
        return None
    n, unit = int(m.group(1)), m.group(2)
    mapping = {"minute": 0, "hour": 0, "day": n, "month": n * 30, "year": n * 365}
    return mapping[unit]


def _main_location(loc: str) -> str:
    """Extract the primary city/district from a composite location string."""
    if not loc or pd.isna(loc):
        return "Unknown"
    known = [
        "Tevragh Zeina", "Ksar", "Arafat", "Teyarett", "Dar Naim",
        "Toujounine", "Sebkha", "El Mina", "Riyad",
        "Nouadhibou", "Nouakchott", "Rosso", "Zouerate", "Atar",
        "Kiffa", "Kaédi", "Néma",
    ]
    for city in known:
        if city.lower() in loc.lower():
            return city
    first = loc.strip().split()[0] if loc.strip() else "Unknown"
    return first


def load_and_clean(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8")
    df = df.rename(columns={"Location+Name": "Location"})

    df["Price_MRU"] = df["Price"].apply(_parse_price)
    df["Days_Ago"] = df["Date_Posted"].apply(_parse_days_ago)
    df["Main_Location"] = df["Location"].apply(_main_location)

    # Remove rows with no usable price or no title
    df = df.dropna(subset=["Price_MRU", "Title"])
    df["Title"] = df["Title"].str.strip()
    df = df[df["Title"] != ""]

    # Remove extreme price outliers (keep 1st–99th percentile per category)
    keep_mask = pd.Series(False, index=df.index)
    for cat, group in df.groupby("Category"):
        lo = group["Price_MRU"].quantile(0.01)
        hi = group["Price_MRU"].quantile(0.99)
        keep_mask.loc[group[(group["Price_MRU"] >= lo) & (group["Price_MRU"] <= hi)].index] = True
    df = df[keep_mask]

    # Drop near-duplicates (same title + price + location)
    df = df.drop_duplicates(subset=["Title", "Price_MRU", "Main_Location"])

    df["Views"] = pd.to_numeric(df["Views"], errors="coerce").fillna(0).astype(int)
    df["Is_Available"] = df["Status"] == "Available"
    df = df.reset_index(drop=True)
    return df
