from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import brentq, fsolve


# ---------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
DATA_PATH = REPO_DIR / "Yields" / "treasury_quotes_2025-04-30.xlsx"
OUTPUT_DIR = SCRIPT_DIR / "yields_outputs"

FACE_VALUE = 100.0
PAYMENTS_PER_YEAR = 2


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def print_section(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def standardize_columns(df):
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace("-", "_", regex=False)
    )
    return df


def to_decimal_rate(series):
    """
    Converts rates such as 5.0 into 0.05.
    Rates already stored as decimals are unchanged.
    """
    values = pd.to_numeric(series, errors="coerce")
    return pd.Series(
        np.where(values.abs() > 1, values / 100, values),
        index=series.index,
        dtype=float,
    )


def bond_price(
    ytm,
    ttm,
    coupon_rate,
    face_value=FACE_VALUE,
    payments_per_year=PAYMENTS_PER_YEAR,
):
    """
    Price a coupon bond using approximately semiannual cash flows.

    ytm and coupon_rate must be decimals.
    """
    if pd.isna(ytm) or pd.isna(ttm) or pd.isna(coupon_rate):
        return np.nan

    if ttm <= 0:
        return np.nan

    n_periods = max(1, int(round(ttm * payments_per_year)))
    coupon_payment = face_value * coupon_rate / payments_per_year
    periodic_yield = ytm / payments_per_year

    if 1 + periodic_yield <= 0:
        return np.nan

    periods = np.arange(1, n_periods + 1)

    coupon_pv = np.sum(
        coupon_payment / (1 + periodic_yield) ** periods
    )
    face_pv = (
        face_value / (1 + periodic_yield) ** n_periods
    )

    return float(coupon_pv + face_pv)


def calculate_ytm(
    price,
    ttm,
    coupon_rate,
    face_value=FACE_VALUE,
    payments_per_year=PAYMENTS_PER_YEAR,
):
    """
    Solve for annual YTM.

    For Treasury bills, use the zero-coupon semiannual bond-equivalent yield.
    For coupon securities, solve the nonlinear bond-pricing equation.
    """
    if pd.isna(price) or pd.isna(ttm) or pd.isna(coupon_rate):
        return np.nan

    if price <= 0 or ttm <= 0:
        return np.nan

    # Exact zero-coupon solution for Treasury bills.
    if np.isclose(coupon_rate, 0):
        return payments_per_year * (
            (face_value / price)
            ** (1 / (payments_per_year * ttm))
            - 1
        )

    def pricing_error(ytm):
        return (
            bond_price(
                ytm=ytm,
                ttm=ttm,
                coupon_rate=coupon_rate,
                face_value=face_value,
                payments_per_year=payments_per_year,
            )
            - price
        )

    try:
        return float(
            brentq(
                pricing_error,
                -0.99,
                2.00,
                maxiter=1000,
            )
        )
    except (ValueError, RuntimeError):
        try:
            solution = fsolve(pricing_error, x0=0.05)
            answer = float(solution[0])
            return answer if np.isfinite(answer) else np.nan
        except Exception:
            return np.nan


def prepare_sheet(sheet_name):
    """
    Load one worksheet and create standardized fields.
    """
    df = pd.read_excel(DATA_PATH, sheet_name=sheet_name)
    df = standardize_columns(df)

    required = [
        "type",
        "maturity_date",
        "ttm",
        "cpn_rate",
        "price",
        "ytm",
    ]

    missing = [column for column in required if column not in df.columns]
    if missing:
        raise KeyError(
            f"Missing columns in '{sheet_name}': {missing}\n"
            f"Available columns: {df.columns.tolist()}"
        )

    df["maturity_date"] = pd.to_datetime(
        df["maturity_date"],
        errors="coerce",
    )
    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce",
    )
    df["ttm"] = pd.to_numeric(
        df["ttm"],
        errors="coerce",
    )
    df["cpn_rate"] = pd.to_numeric(
        df["cpn_rate"],
        errors="coerce",
    )
    df["ytm"] = pd.to_numeric(
        df["ytm"],
        errors="coerce",
    )

    df["coupon_decimal"] = to_decimal_rate(df["cpn_rate"])
    df["reported_ytm_decimal"] = to_decimal_rate(df["ytm"])

    df["type_clean"] = (
        df["type"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df = df.loc[df["ttm"] > 0].copy()

    return df


def add_calculated_ytm(df):
    result = df.copy()

    result["calculated_ytm"] = result.apply(
        lambda row: calculate_ytm(
            price=row["price"],
            ttm=row["ttm"],
            coupon_rate=row["coupon_decimal"],
        ),
        axis=1,
    )

    result["ytm_difference"] = (
        result["calculated_ytm"]
        - result["reported_ytm_decimal"]
    )
    result["ytm_difference_bps"] = (
        result["ytm_difference"] * 10_000
    )

    return result


# ---------------------------------------------------------------------
# 1.1
# ---------------------------------------------------------------------

def exercise_1_1():
    print_section("1.1 — Stylized Semiannual Bond")

    ttm = 30
    coupon_rate = 0.03
    assumed_ytm = 0.05

    price = bond_price(
        ytm=assumed_ytm,
        ttm=ttm,
        coupon_rate=coupon_rate,
    )

    print("A. Price when YTM is 5%")
    print(f"Calculated price: ${price:.4f}")

    observed_price = 87

    solved_ytm = calculate_ytm(
        price=observed_price,
        ttm=ttm,
        coupon_rate=coupon_rate,
    )

    print("\nB. YTM when price is $87")
    print(f"Calculated YTM: {solved_ytm:.6f}")
    print(f"Calculated YTM: {solved_ytm:.4%}")


# ---------------------------------------------------------------------
# 1.2
# ---------------------------------------------------------------------

def exercise_1_2():
    print_section("1.2 — Selected Quotes: Calculated YTM")

    selected = prepare_sheet("selected quotes")
    selected = add_calculated_ytm(selected)

    table = selected[
        [
            "kytreasno",
            "type",
            "maturity_date",
            "ttm",
            "cpn_rate",
            "price",
            "reported_ytm_decimal",
            "calculated_ytm",
            "ytm_difference_bps",
        ]
    ].copy()

    table["reported_ytm_percent"] = (
        table["reported_ytm_decimal"] * 100
    )
    table["calculated_ytm_percent"] = (
        table["calculated_ytm"] * 100
    )

    display_columns = [
        "kytreasno",
        "type",
        "maturity_date",
        "ttm",
        "cpn_rate",
        "price",
        "reported_ytm_percent",
        "calculated_ytm_percent",
        "ytm_difference_bps",
    ]

    print(
        table[display_columns]
        .round(
            {
                "ttm": 4,
                "price": 6,
                "reported_ytm_percent": 6,
                "calculated_ytm_percent": 6,
                "ytm_difference_bps": 4,
            }
        )
        .to_string(index=False)
    )

    valid = selected.dropna(
        subset=["reported_ytm_decimal", "calculated_ytm"]
    )
    errors = valid["ytm_difference_bps"].abs()

    print("\nError summary")
    print(f"Number compared: {len(valid)}")
    print(f"Mean absolute difference: {errors.mean():.4f} bps")
    print(f"Median absolute difference: {errors.median():.4f} bps")
    print(f"Maximum absolute difference: {errors.max():.4f} bps")

    table[display_columns].to_csv(
        OUTPUT_DIR / "1_2_selected_quotes_ytm.csv",
        index=False,
    )

    plot_data = selected.dropna(
        subset=["ttm", "calculated_ytm"]
    ).sort_values("ttm")

    plt.figure(figsize=(10, 6))
    plt.scatter(
        plot_data["ttm"],
        plot_data["calculated_ytm"] * 100,
    )
    plt.plot(
        plot_data["ttm"],
        plot_data["calculated_ytm"] * 100,
        linewidth=1,
    )
    plt.title("Calculated YTM — Selected Treasury Quotes")
    plt.xlabel("Time to Maturity (Years)")
    plt.ylabel("Calculated YTM (%)")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / "1_2_calculated_ytm.png",
        dpi=200,
    )
    plt.close()


# ---------------------------------------------------------------------
# 2.1
# ---------------------------------------------------------------------

def exercise_2_1(nominal):
    print_section("2.1 — Provided YTM Across Nominal Maturities")

    plot_data = nominal.dropna(
        subset=["ttm", "reported_ytm_decimal"]
    ).sort_values("ttm")

    plt.figure(figsize=(10, 6))
    plt.scatter(
        plot_data["ttm"],
        plot_data["reported_ytm_decimal"] * 100,
        s=18,
    )
    plt.plot(
        plot_data["ttm"],
        plot_data["reported_ytm_decimal"] * 100,
        linewidth=0.8,
    )
    plt.title("Provided YTM Across Nominal Treasury Maturities")
    plt.xlabel("Time to Maturity (Years)")
    plt.ylabel("Provided YTM (%)")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / "2_1_provided_nominal_ytm.png",
        dpi=200,
    )
    plt.close()

    print(f"Nominal securities included: {len(nominal)}")
    print("Excluded all TIPS notes and TIPS bonds.")
    print("Saved plot: 2_1_provided_nominal_ytm.png")


# ---------------------------------------------------------------------
# 2.2
# ---------------------------------------------------------------------

def exercise_2_2(nominal):
    print_section("2.2 — Calculated YTM for Nominal Issues")

    result = add_calculated_ytm(nominal)

    compared = result.dropna(
        subset=["reported_ytm_decimal", "calculated_ytm"]
    ).copy()

    compared["reported_ytm_percent"] = (
        compared["reported_ytm_decimal"] * 100
    )
    compared["calculated_ytm_percent"] = (
        compared["calculated_ytm"] * 100
    )

    comparison_columns = [
        "kytreasno",
        "type",
        "maturity_date",
        "ttm",
        "cpn_rate",
        "price",
        "reported_ytm_percent",
        "calculated_ytm_percent",
        "ytm_difference_bps",
    ]

    print("Comparison of reported and calculated YTMs:\n")
    print(
        compared[comparison_columns]
        .sort_values("ttm")
        .round(
            {
                "ttm": 4,
                "price": 6,
                "reported_ytm_percent": 6,
                "calculated_ytm_percent": 6,
                "ytm_difference_bps": 4,
            }
        )
        .to_string(index=False)
    )

    errors = compared["ytm_difference_bps"].abs()

    print("\nError summary")
    print(f"Number compared: {len(compared)}")
    print(f"Mean absolute error: {errors.mean():.4f} bps")
    print(f"Median absolute error: {errors.median():.4f} bps")
    print(f"Maximum absolute error: {errors.max():.4f} bps")

    missing = result.loc[
        result["reported_ytm_decimal"].isna()
        & result["calculated_ytm"].notna()
    ].copy()

    missing["calculated_ytm_percent"] = (
        missing["calculated_ytm"] * 100
    )

    missing_columns = [
        "kytreasno",
        "type",
        "maturity_date",
        "ttm",
        "cpn_rate",
        "price",
        "calculated_ytm_percent",
    ]

    print("\nCalculated YTM where reported YTM is missing:\n")

    if missing.empty:
        print("No nominal securities have a missing reported YTM.")
    else:
        print(
            missing[missing_columns]
            .sort_values("ttm")
            .round(
                {
                    "ttm": 4,
                    "price": 6,
                    "calculated_ytm_percent": 6,
                }
            )
            .to_string(index=False)
        )

    compared[comparison_columns].to_csv(
        OUTPUT_DIR / "2_2_reported_vs_calculated.csv",
        index=False,
    )
    missing[missing_columns].to_csv(
        OUTPUT_DIR / "2_2_missing_reported_ytm.csv",
        index=False,
    )

    return result


# ---------------------------------------------------------------------
# 2.3
# ---------------------------------------------------------------------

def exercise_2_3(nominal_results):
    print_section("2.3 — Treasury-Bill Discount Yields")

    bills = nominal_results.loc[
        nominal_results["type_clean"].eq("bill")
        | nominal_results["coupon_decimal"].fillna(0).eq(0)
    ].copy()

    quote_dates = pd.to_datetime(
        bills["quote_date"],
        errors="coerce",
    )
    maturity_dates = pd.to_datetime(
        bills["maturity_date"],
        errors="coerce",
    )

    bills["days_to_maturity"] = (
        maturity_dates - quote_dates
    ).dt.days

    bills = bills.loc[
        bills["days_to_maturity"] > 0
    ].copy()

    bills["discount_yield"] = (
        (FACE_VALUE - bills["price"])
        / FACE_VALUE
        * 360
        / bills["days_to_maturity"]
    )
    bills["discount_yield_percent"] = (
        bills["discount_yield"] * 100
    )

    bill_columns = [
        "kytreasno",
        "type",
        "quote_date",
        "maturity_date",
        "days_to_maturity",
        "price",
        "discount_yield_percent",
    ]

    print(
        bills[bill_columns]
        .sort_values("days_to_maturity")
        .round(
            {
                "price": 6,
                "discount_yield_percent": 6,
            }
        )
        .to_string(index=False)
    )

    bills[bill_columns].to_csv(
        OUTPUT_DIR / "2_3_tbill_discount_yields.csv",
        index=False,
    )


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Data file not found:\n{DATA_PATH}\n\n"
            "Expected it in the repository's data folder."
        )

    print(f"Using data file: {DATA_PATH}")

    exercise_1_1()
    exercise_1_2()

    # Section 2 needs the full quotes tab because it contains notes,
    # bonds, bills, TIPS notes, and TIPS bonds.
    all_quotes = prepare_sheet("quotes")

    nominal = all_quotes.loc[
        ~all_quotes["type_clean"].str.contains(
            "tips",
            na=False,
        )
    ].copy()

    exercise_2_1(nominal)
    nominal_results = exercise_2_2(nominal)
    exercise_2_3(nominal_results)

    print_section("Finished")
    print(f"Outputs saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
