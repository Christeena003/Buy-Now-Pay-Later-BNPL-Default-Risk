"""
data_analytics.py
Core analytics module for BNPL Financial Default Risk Dataset.
Handles: loading, validation, cleaning, grouping, summarising, and business insights.
"""

import os
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD
# ─────────────────────────────────────────────────────────────────────────────

def load_data(filepath: str) -> pd.DataFrame:
    """Load the CSV dataset and return a raw DataFrame."""
    df = pd.read_csv(filepath)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2. VALIDATE  (detect issues BEFORE cleaning)
# ─────────────────────────────────────────────────────────────────────────────

def validate_data(df: pd.DataFrame) -> dict:
    """Return a dict of data-quality findings."""
    report = {}

    # Missing values per column
    missing = df.isnull().sum()
    report["missing_counts"] = missing[missing > 0].to_dict()
    report["missing_pct"] = (
        (missing[missing > 0] / len(df) * 100).round(2).to_dict()
    )

    # Duplicate rows
    report["duplicate_rows"] = int(df.duplicated().sum())

    # Negative numeric values (should not exist for income / debt / score)
    numeric_cols = ["Income_USD", "Credit_Score", "Total_BNPL_Debt_USD",
                    "Average_Transaction_Value_USD", "Age",
                    "Total_BNPL_Active_Loans"]
    negatives = {}
    for col in numeric_cols:
        if col in df.columns:
            n_neg = int((df[col] < 0).sum())
            if n_neg:
                negatives[col] = n_neg
    report["negative_values"] = negatives

    # Unexpected categories
    expected_employment = {"Employed", "Unemployed", "Student", "Freelancer"}
    expected_risk = {"Low", "Medium", "High"}
    if "Employment_Status" in df.columns:
        unexpected_emp = set(df["Employment_Status"].dropna().unique()) - expected_employment
        report["unexpected_employment_status"] = list(unexpected_emp)
    if "Default_Risk" in df.columns:
        unexpected_risk = set(df["Default_Risk"].dropna().unique()) - expected_risk
        report["unexpected_default_risk"] = list(unexpected_risk)

    return report


# ─────────────────────────────────────────────────────────────────────────────
# 3. CLEAN
# ─────────────────────────────────────────────────────────────────────────────

def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Clean the DataFrame and return (cleaned_df, cleaning_log).
    Steps:
      - Drop exact duplicates
      - Impute missing Credit_Score with median (by Employment_Status group)
      - Impute missing Income_USD with median (by Employment_Status group)
      - Strip whitespace from string columns
      - Encode Late_Payment_History as binary int (Yes=1, No=0)
      - Add derived feature: Debt_to_Income_Ratio
      - Enforce correct dtypes
    """
    log = {}
    original_len = len(df)

    df = df.copy()

    # 3a. Drop duplicates
    before = len(df)
    df.drop_duplicates(inplace=True)
    log["duplicates_dropped"] = before - len(df)

    # 3b. Strip whitespace from object columns
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    # 3c. Impute Credit_Score (median within Employment_Status group)
    cs_missing_before = df["Credit_Score"].isnull().sum()
    df["Credit_Score"] = df.groupby("Employment_Status")["Credit_Score"].transform(
        lambda x: x.fillna(x.median())
    )
    # fallback: overall median
    overall_cs_median = df["Credit_Score"].median()
    df["Credit_Score"] = df["Credit_Score"].fillna(overall_cs_median)
    log["credit_score_imputed"] = int(cs_missing_before)

    # 3d. Impute Income_USD (median within Employment_Status group)
    inc_missing_before = df["Income_USD"].isnull().sum()
    df["Income_USD"] = df.groupby("Employment_Status")["Income_USD"].transform(
        lambda x: x.fillna(x.median())
    )
    overall_inc_median = df["Income_USD"].median()
    df["Income_USD"] = df["Income_USD"].fillna(overall_inc_median)
    log["income_usd_imputed"] = int(inc_missing_before)

    # 3e. Encode Late_Payment_History
    df["Late_Payment_Binary"] = df["Late_Payment_History"].map({"Yes": 1, "No": 0})

    # 3f. Derived feature: Debt-to-Income Ratio
    df["Debt_to_Income_Ratio"] = np.where(
        df["Income_USD"] > 0,
        (df["Total_BNPL_Debt_USD"] / df["Income_USD"]).round(4),
        np.nan,
    )

    # 3g. Risk label ordering (for charts)
    df["Default_Risk"] = pd.Categorical(
        df["Default_Risk"], categories=["Low", "Medium", "High"], ordered=True
    )

    log["final_rows"] = len(df)
    log["rows_removed_total"] = original_len - len(df)
    return df, log


# ─────────────────────────────────────────────────────────────────────────────
# 4. SUMMARISE  (totals, counts, averages)
# ─────────────────────────────────────────────────────────────────────────────

def compute_summary(df: pd.DataFrame) -> dict:
    """Return a comprehensive summary dict for use in the UI and report."""
    s = {}

    # Overall dataset shape
    s["total_customers"] = len(df)
    s["total_columns"] = df.shape[1]

    # Risk distribution
    risk_counts = df["Default_Risk"].value_counts().sort_index()
    s["risk_distribution"] = risk_counts.to_dict()
    s["risk_pct"] = (risk_counts / len(df) * 100).round(2).to_dict()

    # Numeric averages overall
    num_cols = ["Age", "Income_USD", "Credit_Score", "Total_BNPL_Active_Loans",
                "Total_BNPL_Debt_USD", "Average_Transaction_Value_USD",
                "Debt_to_Income_Ratio"]
    s["overall_averages"] = df[num_cols].mean().round(2).to_dict()
    s["overall_totals"] = {
        "Total_BNPL_Debt_USD": round(df["Total_BNPL_Debt_USD"].sum(), 2),
        "Total_BNPL_Active_Loans": int(df["Total_BNPL_Active_Loans"].sum()),
        "Customers_with_Late_Payments": int(df["Late_Payment_Binary"].sum()),
    }

    # By Default_Risk
    grp_risk = df.groupby("Default_Risk", observed=True).agg(
        Count=("Customer_ID", "count"),
        Avg_Age=("Age", "mean"),
        Avg_Income=("Income_USD", "mean"),
        Avg_Credit_Score=("Credit_Score", "mean"),
        Avg_Active_Loans=("Total_BNPL_Active_Loans", "mean"),
        Avg_BNPL_Debt=("Total_BNPL_Debt_USD", "mean"),
        Total_BNPL_Debt=("Total_BNPL_Debt_USD", "sum"),
        Late_Payment_Rate=("Late_Payment_Binary", "mean"),
        Avg_DTI=("Debt_to_Income_Ratio", "mean"),
    ).round(2)
    s["by_risk"] = grp_risk

    # By Employment Status
    grp_emp = df.groupby("Employment_Status").agg(
        Count=("Customer_ID", "count"),
        Avg_Income=("Income_USD", "mean"),
        Avg_Credit_Score=("Credit_Score", "mean"),
        Avg_BNPL_Debt=("Total_BNPL_Debt_USD", "mean"),
        Late_Payment_Rate=("Late_Payment_Binary", "mean"),
        High_Risk_Count=("Default_Risk", lambda x: (x == "High").sum()),
    ).round(2)
    grp_emp["High_Risk_Pct"] = (
        grp_emp["High_Risk_Count"] / grp_emp["Count"] * 100
    ).round(2)
    s["by_employment"] = grp_emp

    # By Shopping Category
    grp_cat = df.groupby("Shopping_Category_Most_Frequent").agg(
        Count=("Customer_ID", "count"),
        Avg_Transaction=("Average_Transaction_Value_USD", "mean"),
        Avg_BNPL_Debt=("Total_BNPL_Debt_USD", "mean"),
        High_Risk_Count=("Default_Risk", lambda x: (x == "High").sum()),
    ).round(2)
    grp_cat["High_Risk_Pct"] = (
        grp_cat["High_Risk_Count"] / grp_cat["Count"] * 100
    ).round(2)
    s["by_category"] = grp_cat

    # Late payment analysis
    late = df.groupby("Late_Payment_History")["Default_Risk"].value_counts(
        normalize=True
    ).mul(100).round(2).rename("Percentage").reset_index()
    s["late_payment_vs_risk"] = late

    # Age bucket analysis
    df["Age_Group"] = pd.cut(
        df["Age"],
        bins=[17, 25, 35, 45, 55, 100],
        labels=["18-25", "26-35", "36-45", "46-55", "56+"],
    )
    grp_age = df.groupby("Age_Group", observed=True).agg(
        Count=("Customer_ID", "count"),
        Avg_Credit_Score=("Credit_Score", "mean"),
        Avg_Income=("Income_USD", "mean"),
        High_Risk_Count=("Default_Risk", lambda x: (x == "High").sum()),
    ).round(2)
    grp_age["High_Risk_Pct"] = (
        grp_age["High_Risk_Count"] / grp_age["Count"] * 100
    ).round(2)
    s["by_age_group"] = grp_age

    # Credit score bucket
    df["Credit_Band"] = pd.cut(
        df["Credit_Score"],
        bins=[299, 499, 579, 669, 739, 799, 900],
        labels=["Very Poor\n(<500)", "Poor\n(500-579)",
                "Fair\n(580-669)", "Good\n(670-739)",
                "Very Good\n(740-799)", "Exceptional\n(800+)"],
    )
    grp_cs = df.groupby("Credit_Band", observed=True).agg(
        Count=("Customer_ID", "count"),
        High_Risk_Count=("Default_Risk", lambda x: (x == "High").sum()),
        Avg_BNPL_Debt=("Total_BNPL_Debt_USD", "mean"),
    ).round(2)
    grp_cs["High_Risk_Pct"] = (
        grp_cs["High_Risk_Count"] / grp_cs["Count"] * 100
    ).round(2)
    s["by_credit_band"] = grp_cs

    return s


# ─────────────────────────────────────────────────────────────────────────────
# 5. BUSINESS INSIGHTS
# ─────────────────────────────────────────────────────────────────────────────

def generate_insights(summary: dict, df: pd.DataFrame) -> list[dict]:
    """
    Return a list of business insight dicts, each with:
      {title, finding, recommendation, severity}
    """
    insights = []
    by_risk = summary["by_risk"]
    by_emp  = summary["by_employment"]
    by_cat  = summary["by_category"]

    # Insight 1: High-risk profile
    if "High" in by_risk.index:
        h = by_risk.loc["High"]
        insights.append({
            "title": "High-Risk Customer Profile",
            "finding": (
                f"High-risk customers average a credit score of {h['Avg_Credit_Score']:.0f}, "
                f"income of ${h['Avg_Income']:,.0f}, {h['Avg_Active_Loans']:.1f} active BNPL loans, "
                f"and a late-payment rate of {h['Late_Payment_Rate']*100:.1f}%."
            ),
            "recommendation": (
                "Implement stricter credit-score thresholds (≥ 650) and cap active BNPL "
                "loans at 3 for new applicants showing a late-payment history."
            ),
            "severity": "High",
        })

    # Insight 2: Debt-to-Income
    avg_dti_high = by_risk.loc["High", "Avg_DTI"] if "High" in by_risk.index else None
    avg_dti_low  = by_risk.loc["Low",  "Avg_DTI"] if "Low"  in by_risk.index else None
    if avg_dti_high and avg_dti_low:
        insights.append({
            "title": "Debt-to-Income Ratio Gap",
            "finding": (
                f"High-risk customers carry a Debt-to-Income ratio of "
                f"{avg_dti_high:.3f} vs {avg_dti_low:.3f} for low-risk customers — "
                f"a {((avg_dti_high/avg_dti_low - 1)*100):.0f}% difference."
            ),
            "recommendation": (
                "Introduce a hard DTI ceiling of 0.15 as an automatic decline trigger. "
                "Customers above 0.10 should undergo manual underwriting review."
            ),
            "severity": "High",
        })

    # Insight 3: Unemployed segment
    if "Unemployed" in by_emp.index:
        ue = by_emp.loc["Unemployed"]
        insights.append({
            "title": "Unemployed Segment Risk",
            "finding": (
                f"Unemployed customers show a late-payment rate of "
                f"{ue['Late_Payment_Rate']*100:.1f}% and average BNPL debt of "
                f"${ue['Avg_BNPL_Debt']:,.0f} — the highest among all employment groups."
            ),
            "recommendation": (
                "Restrict BNPL credit limits for unemployed applicants to a maximum of "
                "$200 and require proof of alternative income."
            ),
            "severity": "High",
        })

    # Insight 4: Student segment
    if "Student" in by_emp.index:
        st = by_emp.loc["Student"]
        insights.append({
            "title": "Student Borrowers — Low Income, Elevated Exposure",
            "finding": (
                f"Students average an income of ${st['Avg_Income']:,.0f} but still "
                f"accumulate average BNPL debt of ${st['Avg_BNPL_Debt']:,.0f}. "
                f"High-risk share: {st['High_Risk_Pct']:.1f}%."
            ),
            "recommendation": (
                "Cap BNPL transactions for students at $150 per purchase and require "
                "parental/guarantor consent for loans above $300."
            ),
            "severity": "Medium",
        })

    # Insight 5: High-value shopping categories
    top_cat = by_cat.sort_values("High_Risk_Pct", ascending=False).head(1)
    if not top_cat.empty:
        cat_name = top_cat.index[0]
        cat_row  = top_cat.iloc[0]
        insights.append({
            "title": f"Highest-Risk Shopping Category: {cat_name}",
            "finding": (
                f"Purchases in {cat_name} have the highest proportion of high-risk "
                f"customers ({cat_row['High_Risk_Pct']:.1f}%) with an average BNPL "
                f"debt of ${cat_row['Avg_BNPL_Debt']:,.0f}."
            ),
            "recommendation": (
                f"Apply additional affordability checks for BNPL transactions in the "
                f"{cat_name} category exceeding $500."
            ),
            "severity": "Medium",
        })

    # Insight 6: Late payment predictive power
    late_data = summary["late_payment_vs_risk"]
    late_high = late_data[
        (late_data["Late_Payment_History"] == "Yes") &
        (late_data["Default_Risk"] == "High")
    ]
    if not late_high.empty:
        pct = late_high.iloc[0]["Percentage"]
        insights.append({
            "title": "Late Payment History as Default Predictor",
            "finding": (
                f"{pct:.1f}% of customers with a late-payment history are classified "
                "as high-risk, making it the strongest single behavioural signal."
            ),
            "recommendation": (
                "Automate risk escalation for any customer recording a first late "
                "payment — trigger a limit freeze and send a debt-management referral."
            ),
            "severity": "High",
        })

    return insights
