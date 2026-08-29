"""
Safe, predefined pandas functions for sales data analysis.
The agent calls these instead of writing raw pandas code itself,
so results stay predictable, testable, and easy to debug.
"""
import pandas as pd
import config

_df = pd.read_csv(config.SALES_CSV, parse_dates=["date"])


def _filter_by_period(df: pd.DataFrame, period: str | None) -> pd.DataFrame:
    """Filter by a period string that can be a full month ('2025-01') or just a year ('2025')."""
    if period is None:
        return df
    if len(period) == 4:  # year only, e.g. "2025"
        return df[df["date"].dt.strftime("%Y") == period]
    return df[df["date"].dt.strftime("%Y-%m") == period]  # full month, e.g. "2025-01"


def monthly_revenue(month: str) -> float:
    """Total revenue for a given month or year, e.g. '2025-01' or '2025'."""
    subset = _filter_by_period(_df, month)
    return round(subset["revenue"].sum(), 2)


def top_products(n: int = 5, month: str | None = None) -> list[dict]:
    """Best-selling products by quantity, optionally filtered to a month or year."""
    subset = _filter_by_period(_df, month)
    result = (
        subset.groupby("product")["quantity"].sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )
    return result.to_dict(orient="records")


def top_products_by_revenue(n: int = 5, period: str | None = None) -> list[dict]:
    """Best-selling products by revenue (not quantity), optionally filtered to a month or year."""
    subset = _filter_by_period(_df, period)
    result = (
        subset.groupby("product")["revenue"].sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )
    return result.to_dict(orient="records")


def low_performers(n: int = 5, month: str | None = None) -> list[dict]:
    """Worst-selling products by quantity, optionally filtered to a month or year."""
    subset = _filter_by_period(_df, month)
    result = (
        subset.groupby("product")["quantity"].sum()
        .sort_values(ascending=True)
        .head(n)
        .reset_index()
    )
    return result.to_dict(orient="records")


def sales_summary(period: str) -> dict:
    """Quick summary (revenue, orders, top product) for a given month or year."""
    subset = _filter_by_period(_df, period)
    if subset.empty:
        return {"period": period, "revenue": 0, "orders": 0, "top_product": None}
    return {
        "period": period,
        "revenue": round(subset["revenue"].sum(), 2),
        "orders": len(subset),
        "top_product": subset.groupby("product")["quantity"].sum().idxmax(),
    }


def best_month(year: str) -> dict:
    """The single month with the highest total revenue within a given year."""
    subset = _df[_df["date"].dt.strftime("%Y") == year]
    if subset.empty:
        return {"year": year, "best_month": None, "revenue": 0}
    monthly = subset.groupby(subset["date"].dt.strftime("%Y-%m"))["revenue"].sum()
    best = monthly.idxmax()
    return {"year": year, "best_month": best, "revenue": round(monthly[best], 2)}