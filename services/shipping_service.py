"""
Shipping cost calculator for AurumCandles.
Ship from: L4N 6G5 (Barrie, ON) | All prices in CAD.

Calculates estimated shipping rates based on product weight using
real carrier rate tiers: Canada Post, Etsy Labels, and Chitchats
for both Canadian domestic (CA) and US cross-border shipping.
"""

# ── Default Assumptions ──────────────────────────────────────────────
DEFAULT_PACKAGING_WEIGHT_G = 200  # 0.2 kg for box, bubble wrap, etc.


# ── Rate Tables (max weight in grams → CA$ price) ───────────────────

CANADA_POST_CA = [
    (100,  10.91),
    (500,  14.50),
    (1000, 17.50),
    (1500, 20.50),
    (2000, 24.00),
]

CANADA_POST_US = [
    (100,  15.00),
    (500,  18.00),
    (1000, 22.00),
    (1500, 26.00),
    (2000, 30.00),
]

ETSY_LABEL_CA = [
    (100,   7.64),
    (500,  10.15),
    (1000, 12.25),
    (1500, 14.35),
    (2000, 16.80),
]

ETSY_LABEL_US = [
    (100,  10.50),
    (500,  12.60),
    (1000, 15.40),
    (1500, 18.20),
    (2000, 21.00),
]

CHITCHATS_CA = [
    (100,   3.83),
    (150,   5.33),
    (300,   5.70),
    (500,   6.07),
    (750,   7.50),
    (1000,  9.00),
    (1500, 11.00),
    (2000, 13.00),
]

CHITCHATS_US = [
    (100,   8.45),
    (150,   8.60),
    (300,   9.50),
    (500,  10.61),
    (750,  12.50),
    (1000, 14.50),
    (1500, 17.00),
    (2000, 20.00),
]


# ── Lookup Helper ────────────────────────────────────────────────────

def _lookup_rate(shipping_weight_g, rate_table):
    """
    Look up the rate from a tiered table based on shipping weight in grams.
    Uses VLOOKUP-style approximate match: finds the largest tier value
    that is <= the shipping weight, matching the Excel spreadsheet logic.
    If lighter than all tiers, returns the first tier rate.
    If heavier than all tiers, returns the last tier rate + linear overage.
    """
    matched_price = rate_table[0][1]  # default to first tier
    for max_g, price in rate_table:
        if shipping_weight_g >= max_g:
            matched_price = price
        else:
            break
    # If heavier than last tier, add overage
    last_max, last_price = rate_table[-1]
    if shipping_weight_g > last_max:
        overage_kg = (shipping_weight_g - last_max) / 1000.0
        return last_price + (overage_kg * 8.0)
    return matched_price


# ── Shipping Weight ──────────────────────────────────────────────────

def get_shipping_weight_g(item_weight_g, packaging_weight_g=DEFAULT_PACKAGING_WEIGHT_G):
    """Total shipping weight = item weight + packaging weight."""
    return item_weight_g + packaging_weight_g


# ── Per-Carrier Calculators ──────────────────────────────────────────

def calculate_canada_post_ca(shipping_weight_g):
    """Canada Post domestic (retail rate)."""
    return _lookup_rate(shipping_weight_g, CANADA_POST_CA)


def calculate_canada_post_us(shipping_weight_g):
    """Canada Post cross-border to US (retail rate)."""
    return _lookup_rate(shipping_weight_g, CANADA_POST_US)


def calculate_etsy_label_ca(shipping_weight_g):
    """Canada Post with ~30% Etsy shipping label discount (domestic)."""
    return _lookup_rate(shipping_weight_g, ETSY_LABEL_CA)


def calculate_etsy_label_us(shipping_weight_g):
    """Canada Post with ~30% Etsy label discount (US-bound)."""
    return _lookup_rate(shipping_weight_g, ETSY_LABEL_US)


def calculate_chitchats_ca(shipping_weight_g):
    """Chitchats domestic rate. Typically 50-75% cheaper than Canada Post retail."""
    return _lookup_rate(shipping_weight_g, CHITCHATS_CA)


def calculate_chitchats_us(shipping_weight_g):
    """Chitchats US-bound rate. Includes customs clearing."""
    return _lookup_rate(shipping_weight_g, CHITCHATS_US)


# ── All-Carrier Estimates ────────────────────────────────────────────

# Ordered list of all carriers for iteration
CARRIER_TABLE = [
    ("Chitchats",    "CA (Domestic)", CHITCHATS_CA),
    ("Chitchats",    "US (Cross-border)", CHITCHATS_US),
    ("Etsy Label",   "CA (Domestic)", ETSY_LABEL_CA),
    ("Etsy Label",   "US (Cross-border)", ETSY_LABEL_US),
    ("Canada Post",  "CA (Domestic)", CANADA_POST_CA),
    ("Canada Post",  "US (Cross-border)", CANADA_POST_US),
]


def get_all_shipping_estimates(item_weight_g, packaging_weight_g=DEFAULT_PACKAGING_WEIGHT_G):
    """
    Calculate all shipping estimates for a given item weight.

    Returns a list of dicts sorted by cost:
        {carrier, destination, cost, shipping_weight_g, note}
    """
    if item_weight_g <= 0:
        return []

    shipping_weight = get_shipping_weight_g(item_weight_g, packaging_weight_g)
    results = []

    for carrier, destination, table in CARRIER_TABLE:
        cost = _lookup_rate(shipping_weight, table)
        results.append({
            "carrier": carrier,
            "destination": destination,
            "cost": cost,
            "shipping_weight_g": shipping_weight,
            "note": f"{shipping_weight:.0f}g shipped ({item_weight_g:.0f}g + {packaging_weight_g:.0f}g pkg)",
        })

    results.sort(key=lambda x: x["cost"])
    return results


def get_ca_estimates(item_weight_g, packaging_weight_g=DEFAULT_PACKAGING_WEIGHT_G):
    """Only domestic (CA) shipping estimates, sorted by cost."""
    all_est = get_all_shipping_estimates(item_weight_g, packaging_weight_g)
    return [e for e in all_est if "CA" in e["destination"]]


def get_us_estimates(item_weight_g, packaging_weight_g=DEFAULT_PACKAGING_WEIGHT_G):
    """Only US cross-border estimates, sorted by cost."""
    all_est = get_all_shipping_estimates(item_weight_g, packaging_weight_g)
    return [e for e in all_est if "US" in e["destination"]]


def get_cheapest_shipping(item_weight_g, packaging_weight_g=DEFAULT_PACKAGING_WEIGHT_G):
    """Return the single cheapest shipping option, or None."""
    estimates = get_all_shipping_estimates(item_weight_g, packaging_weight_g)
    return estimates[0] if estimates else None


def get_cheapest_by_destination(item_weight_g, packaging_weight_g=DEFAULT_PACKAGING_WEIGHT_G):
    """Return dict with cheapest CA and cheapest US option."""
    ca = get_ca_estimates(item_weight_g, packaging_weight_g)
    us = get_us_estimates(item_weight_g, packaging_weight_g)
    return {
        "ca": ca[0] if ca else None,
        "us": us[0] if us else None,
    }


def format_shipping_summary(item_weight_g, packaging_weight_g=DEFAULT_PACKAGING_WEIGHT_G):
    """One-line summary: cheapest CA and US options."""
    best = get_cheapest_by_destination(item_weight_g, packaging_weight_g)
    parts = []
    if best["ca"]:
        parts.append(f"CA ${best['ca']['cost']:.2f} ({best['ca']['carrier']})")
    if best["us"]:
        parts.append(f"US ${best['us']['cost']:.2f} ({best['us']['carrier']})")
    return " | ".join(parts) if parts else "N/A"


# ── Savings Calculator ───────────────────────────────────────────────

def calculate_savings(item_weight_g, packaging_weight_g=DEFAULT_PACKAGING_WEIGHT_G):
    """
    Calculate how much Chitchats saves vs Etsy Labels and Canada Post.
    Returns dict with savings amounts.
    """
    sw = get_shipping_weight_g(item_weight_g, packaging_weight_g)

    cc_ca = calculate_chitchats_ca(sw)
    cc_us = calculate_chitchats_us(sw)
    etsy_ca = calculate_etsy_label_ca(sw)
    etsy_us = calculate_etsy_label_us(sw)
    cp_ca = calculate_canada_post_ca(sw)
    cp_us = calculate_canada_post_us(sw)

    return {
        "save_vs_etsy_ca": etsy_ca - cc_ca,
        "save_vs_etsy_us": etsy_us - cc_us,
        "save_vs_cp_ca": cp_ca - cc_ca,
        "save_vs_cp_us": cp_us - cc_us,
    }
