"""
Safe, predefined pandas functions for sales data analysis.
The agent calls these instead of writing raw pandas code itself,
so results stay predictable, testable, and easy to debug.
"""
import pandas as pd
import config

_df = pd.read_csv(config.SALES_CSV, parse_dates=["date"])


def _filter_by_month(df: pd.DataFrame, month: str | None) -> pd.DataFrame:
    if month is None:
        return df
    return df[df["date"].dt.strftime("%Y-%m") == month]


def monthly_revenue(month: str) -> float:
    """Total revenue for a given month, e.g. month='2025-01'."""
    subset = _filter_by_month(_df, month)
    return round(subset["revenue"].sum(), 2)


def top_products(n: int = 5, month: str | None = None) -> list[dict]:
    """Best-selling products by quantity, optionally filtered to one month."""
    subset = _filter_by_month(_df, month)
    result = (
        subset.groupby("product")["quantity"].sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )
    return result.to_dict(orient="records")


def low_performers(n: int = 5, month: str | None = None) -> list[dict]:
    """Worst-selling products by quantity, optionally filtered to one month."""
    subset = _filter_by_month(_df, month)
    result = (
        subset.groupby("product")["quantity"].sum()
        .sort_values(ascending=True)
        .head(n)
        .reset_index()
    )
    return result.to_dict(orient="records")


def sales_summary(period: str) -> dict:
    """Quick summary (revenue, orders, top product) for a given month."""
    subset = _filter_by_month(_df, period)
    if subset.empty:
        return {"period": period, "revenue": 0, "orders": 0, "top_product": None}
    return {
        "period": period,
        "revenue": round(subset["revenue"].sum(), 2),
        "orders": len(subset),
        "top_product": subset.groupby("product")["quantity"].sum().idxmax(),
    }
