"""
app.py  —  BNPL Financial Default Risk Dashboard
Streamlit frontend for the analytics pipeline.
Run:  streamlit run app.py
"""

import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── resolve dataset path relative to this file ────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "BNPL_Financial_Default_Risk_Dataset.csv")

sys.path.insert(0, BASE_DIR)
from data_analytics import (
    load_data, validate_data, clean_data, compute_summary, generate_insights
)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BNPL Default Risk Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main header */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1f2937;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }
    /* Metric cards */
    div[data-testid="metric-container"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 18px;
    }
    div[data-testid="metric-container"] label {
        font-size: 0.78rem !important;
        color: #64748b !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700;
        color: #1e293b;
    }
    /* Section headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e293b;
        border-left: 4px solid #3b82f6;
        padding-left: 10px;
        margin: 1.8rem 0 0.8rem 0;
    }
    /* Risk badge */
    .badge-high   { background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:700; }
    .badge-medium { background:#fef3c7; color:#92400e; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:700; }
    .badge-low    { background:#d1fae5; color:#065f46; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:700; }
    /* Insight card */
    .insight-card {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 1rem;
    }
    .insight-card.high   { border-left-color: #ef4444; }
    .insight-card.medium { border-left-color: #f59e0b; }
    .insight-card h4 { margin: 0 0 6px 0; font-size: 0.95rem; color: #1e293b; }
    .insight-card p  { margin: 0 0 6px 0; font-size: 0.87rem; color: #374151; }
    .insight-card small { font-size: 0.82rem; color: #6b7280; }
    /* Sidebar */
    section[data-testid="stSidebar"] { background: #1e293b !important; }
    section[data-testid="stSidebar"] * { color: #f1f5f9 !important; }
    section[data-testid="stSidebar"] .stSelectbox label { color: #94a3b8 !important; }
    /* Table */
    div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
    /* Hide streamlit branding */
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 BNPL Risk Analytics")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        [
            "🏠 Overview",
            "🔍 Data Quality",
            "📋 Summary Statistics",
            "📈 Risk Analysis",
            "👥 Demographic Insights",
            "🛒 Behavioural Patterns",
            "💡 Business Insights",
            "📂 Raw Data Explorer",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("**Dataset**")
    st.markdown("BNPL Financial Default Risk")
    st.markdown("`10,000 customers`")


# ─────────────────────────────────────────────────────────────────────────────
# LOAD & CACHE
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading and processing dataset…")
def get_all_data():
    raw_df    = load_data(DATASET_PATH)
    val_rep   = validate_data(raw_df)
    clean_df, clean_log = clean_data(raw_df)
    summary   = compute_summary(clean_df)
    insights  = generate_insights(summary, clean_df)
    return raw_df, val_rep, clean_df, clean_log, summary, insights

raw_df, val_rep, df, clean_log, summary, insights = get_all_data()

# colour palette for risk levels
RISK_COLORS = {"Low": "#22c55e", "Medium": "#f59e0b", "High": "#ef4444"}
RISK_ORDER  = ["Low", "Medium", "High"]

# ─────────────────────────────────────────────────────────────────────────────
# HELPER: section header
# ─────────────────────────────────────────────────────────────────────────────
def section(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
if page == "🏠 Overview":
    st.markdown('<div class="main-title">BNPL Financial Default Risk Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Buy Now Pay Later — Data Analytics & Risk Intelligence Platform</div>', unsafe_allow_html=True)

    # KPI row 1
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers",       f"{summary['total_customers']:,}")
    c2.metric("Low-Risk Customers",    f"{summary['risk_distribution'].get('Low', 0):,}",
              f"{summary['risk_pct'].get('Low', 0):.1f}%")
    c3.metric("Medium-Risk Customers", f"{summary['risk_distribution'].get('Medium', 0):,}",
              f"{summary['risk_pct'].get('Medium', 0):.1f}%")
    c4.metric("High-Risk Customers",   f"{summary['risk_distribution'].get('High', 0):,}",
              f"{summary['risk_pct'].get('High', 0):.1f}%")

    # KPI row 2
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Total BNPL Debt",       f"${summary['overall_totals']['Total_BNPL_Debt_USD']:,.0f}")
    c6.metric("Total Active Loans",    f"{summary['overall_totals']['Total_BNPL_Active_Loans']:,}")
    c7.metric("Late Payment Customers",f"{summary['overall_totals']['Customers_with_Late_Payments']:,}")
    c8.metric("Avg Credit Score",      f"{summary['overall_averages']['Credit_Score']:.0f}")

    st.markdown("---")
    col_l, col_r = st.columns([1, 1])

    with col_l:
        section("Default Risk Distribution")
        risk_dist = pd.DataFrame({
            "Risk Level": list(summary["risk_distribution"].keys()),
            "Count":      list(summary["risk_distribution"].values()),
        })
        fig = px.pie(
            risk_dist, names="Risk Level", values="Count",
            color="Risk Level",
            color_discrete_map=RISK_COLORS,
            hole=0.45,
        )
        fig.update_traces(textposition="outside", textinfo="percent+label",
                          textfont_size=13)
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20),
                          height=320)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        section("Avg Key Metrics by Risk Level")
        by_risk = summary["by_risk"].reset_index()
        fig2 = make_subplots(rows=1, cols=3,
                             subplot_titles=["Avg Credit Score", "Avg Income (USD)", "Avg BNPL Debt (USD)"])
        for i, col_name in enumerate(["Avg_Credit_Score", "Avg_Income", "Avg_BNPL_Debt"], 1):
            colors = [RISK_COLORS.get(r, "#94a3b8") for r in by_risk["Default_Risk"].astype(str)]
            fig2.add_trace(
                go.Bar(x=by_risk["Default_Risk"].astype(str),
                       y=by_risk[col_name],
                       marker_color=colors,
                       showlegend=False),
                row=1, col=i
            )
        fig2.update_layout(height=320, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig2, use_container_width=True)

    section("Dataset Description")
    desc_data = {
        "Column": ["Customer_ID", "Age", "Employment_Status", "Income_USD", "Credit_Score",
                   "Total_BNPL_Active_Loans", "Total_BNPL_Debt_USD", "Late_Payment_History",
                   "Shopping_Category_Most_Frequent", "Average_Transaction_Value_USD", "Default_Risk"],
        "Type":   ["ID", "Numeric", "Categorical", "Numeric", "Numeric",
                   "Numeric", "Numeric", "Binary", "Categorical", "Numeric", "Target"],
        "Description": [
            "Unique customer identifier",
            "Customer age in years",
            "Employment status at application",
            "Annual income in USD",
            "Credit score (300–900 scale)",
            "Number of currently active BNPL loans",
            "Total outstanding BNPL debt in USD",
            "Whether customer has late payment history",
            "Most frequent shopping category",
            "Average BNPL transaction value in USD",
            "Default risk label: Low / Medium / High",
        ],
    }
    st.dataframe(pd.DataFrame(desc_data), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: DATA QUALITY
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔍 Data Quality":
    st.markdown('<div class="main-title">Data Quality Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Validation findings before and after cleaning</div>', unsafe_allow_html=True)

    # Before cleaning
    section("Missing Values (Raw Dataset)")
    if val_rep["missing_counts"]:
        miss_df = pd.DataFrame({
            "Column":   list(val_rep["missing_counts"].keys()),
            "Missing":  list(val_rep["missing_counts"].values()),
            "% Missing": list(val_rep["missing_pct"].values()),
        })
        c1, c2 = st.columns([2, 1])
        with c1:
            fig_miss = px.bar(
                miss_df, x="Column", y="Missing",
                text="Missing",
                color="% Missing",
                color_continuous_scale="Reds",
                title="Missing Value Count per Column",
            )
            fig_miss.update_traces(textposition="outside")
            fig_miss.update_layout(height=350, margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig_miss, use_container_width=True)
        with c2:
            st.dataframe(miss_df, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No missing values detected in the raw dataset.")

    section("Other Quality Checks")
    c1, c2, c3 = st.columns(3)
    c1.metric("Duplicate Rows",             val_rep["duplicate_rows"])
    c2.metric("Negative Numeric Values",    sum(val_rep["negative_values"].values()) if val_rep["negative_values"] else 0)
    c3.metric("Unexpected Category Labels",
              len(val_rep.get("unexpected_employment_status", [])) +
              len(val_rep.get("unexpected_default_risk", [])))

    if val_rep.get("unexpected_employment_status"):
        st.warning(f"Unexpected Employment_Status values: {val_rep['unexpected_employment_status']}")
    if val_rep.get("unexpected_default_risk"):
        st.warning(f"Unexpected Default_Risk values: {val_rep['unexpected_default_risk']}")

    section("Cleaning Actions Applied")
    cleaning_items = [
        ("Duplicate rows dropped",    clean_log["duplicates_dropped"]),
        ("Credit_Score values imputed (group median)", clean_log["credit_score_imputed"]),
        ("Income_USD values imputed (group median)",   clean_log["income_usd_imputed"]),
        ("Late_Payment_History encoded as binary",    "Yes"),
        ("Debt-to-Income Ratio feature added",        "Yes"),
        ("Default_Risk encoded as ordered category",  "Yes"),
        ("Final dataset rows",        clean_log["final_rows"]),
    ]
    clog_df = pd.DataFrame(cleaning_items, columns=["Action", "Value"])
    st.dataframe(clog_df, use_container_width=True, hide_index=True)

    section("Column-level Statistics (Cleaned Dataset)")
    st.dataframe(
        df.describe(include="all").T.reset_index().rename(columns={"index": "Column"}),
        use_container_width=True,
        height=420,
    )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SUMMARY STATISTICS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📋 Summary Statistics":
    st.markdown('<div class="main-title">Summary Statistics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Aggregated totals, counts and averages across key dimensions</div>', unsafe_allow_html=True)

    section("Overall Averages")
    avg = summary["overall_averages"]
    cols = st.columns(4)
    items = [
        ("Avg Age",            f"{avg['Age']:.1f} yrs"),
        ("Avg Income",         f"${avg['Income_USD']:,.0f}"),
        ("Avg Credit Score",   f"{avg['Credit_Score']:.0f}"),
        ("Avg BNPL Loans",     f"{avg['Total_BNPL_Active_Loans']:.2f}"),
        ("Avg BNPL Debt",      f"${avg['Total_BNPL_Debt_USD']:,.0f}"),
        ("Avg Transaction",    f"${avg['Average_Transaction_Value_USD']:,.0f}"),
        ("Avg DTI Ratio",      f"{avg['Debt_to_Income_Ratio']:.4f}"),
    ]
    for i, (label, val) in enumerate(items):
        cols[i % 4].metric(label, val)

    section("Summary by Default Risk Level")
    risk_tbl = summary["by_risk"].reset_index()
    risk_tbl.columns = [c.replace("_", " ") for c in risk_tbl.columns]
    st.dataframe(risk_tbl.style.format({
        "Avg Income": "${:,.0f}", "Avg BNPL Debt": "${:,.0f}",
        "Total BNPL Debt": "${:,.0f}",
        "Late Payment Rate": "{:.2%}", "Avg DTI": "{:.4f}",
    }), use_container_width=True, hide_index=True)

    section("Summary by Employment Status")
    emp_tbl = summary["by_employment"].reset_index()
    emp_tbl.columns = [c.replace("_", " ") for c in emp_tbl.columns]
    st.dataframe(emp_tbl.style.format({
        "Avg Income": "${:,.0f}", "Avg BNPL Debt": "${:,.0f}",
        "Late Payment Rate": "{:.2%}", "High Risk Pct": "{:.1f}%",
    }), use_container_width=True, hide_index=True)

    section("Summary by Shopping Category")
    cat_tbl = summary["by_category"].reset_index()
    cat_tbl.columns = [c.replace("_", " ") for c in cat_tbl.columns]
    st.dataframe(cat_tbl.style.format({
        "Avg Transaction": "${:,.0f}", "Avg BNPL Debt": "${:,.0f}",
        "High Risk Pct": "{:.1f}%",
    }), use_container_width=True, hide_index=True)

    section("Summary by Age Group")
    age_tbl = summary["by_age_group"].reset_index()
    age_tbl.columns = [c.replace("_", " ") for c in age_tbl.columns]
    st.dataframe(age_tbl.style.format({
        "Avg Income": "${:,.0f}", "Avg Credit Score": "{:.0f}",
        "High Risk Pct": "{:.1f}%",
    }), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: RISK ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📈 Risk Analysis":
    st.markdown('<div class="main-title">Risk Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Deep-dive into default risk drivers and distributions</div>', unsafe_allow_html=True)

    # Row 1: Credit score distribution by risk
    section("Credit Score Distribution by Risk Level")
    fig_cs = px.histogram(
        df, x="Credit_Score", color="Default_Risk",
        nbins=40, barmode="overlay", opacity=0.75,
        color_discrete_map=RISK_COLORS,
        category_orders={"Default_Risk": RISK_ORDER},
        labels={"Credit_Score": "Credit Score", "Default_Risk": "Risk Level"},
    )
    fig_cs.update_layout(height=380, margin=dict(t=20, b=20))
    st.plotly_chart(fig_cs, use_container_width=True)

    # Row 2: Income vs BNPL Debt scatter
    section("Income vs BNPL Debt — Coloured by Risk Level")
    sample = df.sample(min(2000, len(df)), random_state=42)
    fig_sc = px.scatter(
        sample, x="Income_USD", y="Total_BNPL_Debt_USD",
        color="Default_Risk",
        color_discrete_map=RISK_COLORS,
        category_orders={"Default_Risk": RISK_ORDER},
        opacity=0.6, size_max=8,
        labels={"Income_USD": "Annual Income (USD)",
                "Total_BNPL_Debt_USD": "Total BNPL Debt (USD)",
                "Default_Risk": "Risk Level"},
        hover_data=["Customer_ID", "Credit_Score", "Employment_Status"],
    )
    fig_sc.update_layout(height=400, margin=dict(t=20, b=20))
    st.plotly_chart(fig_sc, use_container_width=True)

    # Row 3: Late payment vs risk
    col_l, col_r = st.columns(2)
    with col_l:
        section("Late Payment History vs Risk Level")
        late_ct = df.groupby(["Late_Payment_History", "Default_Risk"],
                             observed=True).size().reset_index(name="Count")
        fig_late = px.bar(
            late_ct, x="Late_Payment_History", y="Count",
            color="Default_Risk",
            color_discrete_map=RISK_COLORS,
            category_orders={"Default_Risk": RISK_ORDER},
            barmode="group",
            labels={"Late_Payment_History": "Late Payment History",
                    "Default_Risk": "Risk Level"},
        )
        fig_late.update_layout(height=380, margin=dict(t=20, b=20))
        st.plotly_chart(fig_late, use_container_width=True)

    with col_r:
        section("Active BNPL Loans vs Risk Level")
        loan_ct = df.groupby(["Total_BNPL_Active_Loans", "Default_Risk"],
                             observed=True).size().reset_index(name="Count")
        fig_loans = px.bar(
            loan_ct, x="Total_BNPL_Active_Loans", y="Count",
            color="Default_Risk",
            color_discrete_map=RISK_COLORS,
            category_orders={"Default_Risk": RISK_ORDER},
            barmode="stack",
            labels={"Total_BNPL_Active_Loans": "Active BNPL Loans",
                    "Default_Risk": "Risk Level"},
        )
        fig_loans.update_layout(height=380, margin=dict(t=20, b=20))
        st.plotly_chart(fig_loans, use_container_width=True)

    # Row 4: Credit band risk heatmap
    section("High-Risk Percentage by Credit Score Band")
    cs_band = summary["by_credit_band"].reset_index()
    cs_band["Credit_Band_str"] = cs_band["Credit_Band"].astype(str)
    fig_cb = px.bar(
        cs_band, x="Credit_Band_str", y="High_Risk_Pct",
        color="High_Risk_Pct",
        color_continuous_scale="Reds",
        text="High_Risk_Pct",
        labels={"Credit_Band_str": "Credit Score Band",
                "High_Risk_Pct": "High-Risk %"},
    )
    fig_cb.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_cb.update_layout(height=380, margin=dict(t=20, b=20), coloraxis_showscale=False)
    st.plotly_chart(fig_cb, use_container_width=True)

    # Row 5: DTI box plot
    section("Debt-to-Income Ratio by Risk Level")
    fig_dti = px.box(
        df, x="Default_Risk", y="Debt_to_Income_Ratio",
        color="Default_Risk",
        color_discrete_map=RISK_COLORS,
        category_orders={"Default_Risk": RISK_ORDER},
        points="outliers",
        labels={"Default_Risk": "Risk Level",
                "Debt_to_Income_Ratio": "Debt-to-Income Ratio"},
    )
    fig_dti.update_layout(height=380, margin=dict(t=20, b=20), showlegend=False)
    st.plotly_chart(fig_dti, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: DEMOGRAPHIC INSIGHTS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "👥 Demographic Insights":
    st.markdown('<div class="main-title">Demographic Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Risk patterns across age groups and employment status</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        section("Risk Level by Employment Status")
        emp_risk = df.groupby(["Employment_Status", "Default_Risk"],
                              observed=True).size().reset_index(name="Count")
        fig_emp = px.bar(
            emp_risk, x="Employment_Status", y="Count",
            color="Default_Risk",
            color_discrete_map=RISK_COLORS,
            category_orders={"Default_Risk": RISK_ORDER},
            barmode="stack",
            labels={"Employment_Status": "Employment Status",
                    "Default_Risk": "Risk Level"},
        )
        fig_emp.update_layout(height=380, margin=dict(t=20, b=20))
        st.plotly_chart(fig_emp, use_container_width=True)

    with col_r:
        section("High-Risk % by Age Group")
        age_grp = summary["by_age_group"].reset_index()
        fig_age = px.bar(
            age_grp, x="Age_Group", y="High_Risk_Pct",
            color="High_Risk_Pct",
            color_continuous_scale="Reds",
            text="High_Risk_Pct",
            labels={"Age_Group": "Age Group", "High_Risk_Pct": "High-Risk %"},
        )
        fig_age.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_age.update_layout(height=380, margin=dict(t=20, b=20), coloraxis_showscale=False)
        st.plotly_chart(fig_age, use_container_width=True)

    section("Age Distribution by Risk Level")
    fig_age_box = px.box(
        df, x="Default_Risk", y="Age",
        color="Default_Risk",
        color_discrete_map=RISK_COLORS,
        category_orders={"Default_Risk": RISK_ORDER},
        points="outliers",
        labels={"Default_Risk": "Risk Level", "Age": "Age"},
    )
    fig_age_box.update_layout(height=380, margin=dict(t=20, b=20), showlegend=False)
    st.plotly_chart(fig_age_box, use_container_width=True)

    section("Income Distribution by Employment Status")
    fig_inc = px.violin(
        df, x="Employment_Status", y="Income_USD",
        color="Employment_Status",
        box=True, points=False,
        labels={"Employment_Status": "Employment Status",
                "Income_USD": "Annual Income (USD)"},
    )
    fig_inc.update_layout(height=400, margin=dict(t=20, b=20), showlegend=False)
    st.plotly_chart(fig_inc, use_container_width=True)

    section("Credit Score vs Income — by Employment Status")
    fig_ci = px.scatter(
        df.sample(min(2000, len(df)), random_state=1),
        x="Credit_Score", y="Income_USD",
        color="Employment_Status",
        facet_col="Default_Risk",
        facet_col_order=RISK_ORDER,
        opacity=0.55,
        labels={"Credit_Score": "Credit Score",
                "Income_USD": "Annual Income (USD)"},
    )
    fig_ci.update_layout(height=400, margin=dict(t=30, b=20))
    st.plotly_chart(fig_ci, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: BEHAVIOURAL PATTERNS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🛒 Behavioural Patterns":
    st.markdown('<div class="main-title">Behavioural Patterns</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Shopping behaviour, late payments, and BNPL usage patterns</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        section("Customers by Shopping Category")
        cat_ct = df["Shopping_Category_Most_Frequent"].value_counts().reset_index()
        cat_ct.columns = ["Category", "Count"]
        fig_cat = px.bar(
            cat_ct.sort_values("Count"), x="Count", y="Category",
            orientation="h", color="Count",
            color_continuous_scale="Blues",
            text="Count",
        )
        fig_cat.update_traces(textposition="outside")
        fig_cat.update_layout(height=380, margin=dict(t=20, b=20), coloraxis_showscale=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_r:
        section("Risk Distribution by Shopping Category")
        cat_risk = df.groupby(["Shopping_Category_Most_Frequent", "Default_Risk"],
                              observed=True).size().reset_index(name="Count")
        fig_cr = px.bar(
            cat_risk, x="Shopping_Category_Most_Frequent", y="Count",
            color="Default_Risk",
            color_discrete_map=RISK_COLORS,
            category_orders={"Default_Risk": RISK_ORDER},
            barmode="stack",
            labels={"Shopping_Category_Most_Frequent": "Category",
                    "Default_Risk": "Risk Level"},
        )
        fig_cr.update_layout(height=380, margin=dict(t=20, b=20))
        st.plotly_chart(fig_cr, use_container_width=True)

    section("Average Transaction Value vs BNPL Debt by Category")
    cat_agg = summary["by_category"].reset_index()
    fig_bubble = px.scatter(
        cat_agg,
        x="Avg_Transaction", y="Avg_BNPL_Debt",
        size="Count", color="High_Risk_Pct",
        text="Shopping_Category_Most_Frequent",
        color_continuous_scale="Reds",
        labels={"Avg_Transaction": "Avg Transaction Value (USD)",
                "Avg_BNPL_Debt": "Avg BNPL Debt (USD)",
                "High_Risk_Pct": "High-Risk %"},
        size_max=60,
    )
    fig_bubble.update_traces(textposition="top center")
    fig_bubble.update_layout(height=450, margin=dict(t=20, b=20))
    st.plotly_chart(fig_bubble, use_container_width=True)

    section("Correlation Heatmap — Numeric Features")
    num_df = df[["Age", "Income_USD", "Credit_Score", "Total_BNPL_Active_Loans",
                 "Total_BNPL_Debt_USD", "Average_Transaction_Value_USD",
                 "Debt_to_Income_Ratio", "Late_Payment_Binary"]].copy()
    corr = num_df.corr().round(2)
    fig_corr = px.imshow(
        corr, text_auto=True, aspect="auto",
        color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        title="Feature Correlation Matrix",
    )
    fig_corr.update_layout(height=500, margin=dict(t=40, b=20))
    st.plotly_chart(fig_corr, use_container_width=True)

    section("Active BNPL Loans Distribution")
    fig_loans_hist = px.histogram(
        df, x="Total_BNPL_Active_Loans",
        color="Default_Risk",
        barmode="overlay",
        color_discrete_map=RISK_COLORS,
        category_orders={"Default_Risk": RISK_ORDER},
        nbins=12,
        labels={"Total_BNPL_Active_Loans": "Active BNPL Loans",
                "Default_Risk": "Risk Level"},
    )
    fig_loans_hist.update_layout(height=360, margin=dict(t=20, b=20))
    st.plotly_chart(fig_loans_hist, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: BUSINESS INSIGHTS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "💡 Business Insights":
    st.markdown('<div class="main-title">Business Insights & Recommendations</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Actionable decisions derived from the analytics</div>', unsafe_allow_html=True)

    sev_color = {"High": "#fee2e2", "Medium": "#fef3c7", "Low": "#d1fae5"}
    sev_border = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"}
    sev_badge  = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}

    for ins in insights:
        sev  = ins["severity"]
        html = f"""
        <div style="background:{sev_color.get(sev,'#f8fafc')};
                    border-left:5px solid {sev_border.get(sev,'#3b82f6')};
                    border-radius:8px; padding:16px 20px; margin-bottom:16px;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                <span style="font-size:1rem; font-weight:700; color:#1e293b;">{ins['title']}</span>
                <span class="{sev_badge.get(sev,'')}" style="
                    background:{sev_border.get(sev,'#3b82f6')}22;
                    color:{sev_border.get(sev,'#3b82f6')};
                    border:1px solid {sev_border.get(sev,'#3b82f6')};
                    padding:2px 10px; border-radius:12px; font-size:0.75rem; font-weight:700;">
                    {sev} Priority
                </span>
            </div>
            <p style="margin:0 0 8px 0; font-size:0.88rem; color:#374151;">
                <strong>Finding:</strong> {ins['finding']}
            </p>
            <p style="margin:0; font-size:0.88rem; color:#374151;">
                <strong>Recommendation:</strong> {ins['recommendation']}
            </p>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    st.markdown("---")
    section("Risk Score Summary Table")
    risk_tbl = summary["by_risk"].reset_index()
    risk_tbl["Default_Risk"] = risk_tbl["Default_Risk"].astype(str)
    st.dataframe(
        risk_tbl.rename(columns={c: c.replace("_", " ") for c in risk_tbl.columns}),
        use_container_width=True, hide_index=True,
    )

    section("Decision Framework")
    rules = pd.DataFrame({
        "Rule": [
            "Credit Score < 500",
            "Credit Score 500–649 AND Late Payment = Yes",
            "DTI Ratio > 0.15",
            "Active BNPL Loans ≥ 5",
            "Unemployed AND BNPL Debt > $200",
            "Student AND transaction > $150",
            "Credit Score ≥ 650 AND DTI < 0.10 AND No Late Payments",
        ],
        "Action": [
            "Auto Decline",
            "Manual Review",
            "Auto Decline",
            "Limit Freeze",
            "Restrict to $200 cap",
            "Require guarantor",
            "Auto Approve",
        ],
        "Priority": ["High","High","High","High","High","Medium","Low"],
    })
    st.dataframe(rules, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: RAW DATA EXPLORER
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📂 Raw Data Explorer":
    st.markdown('<div class="main-title">Raw Data Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Filter, sort and inspect the cleaned dataset</div>', unsafe_allow_html=True)

    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        risk_filter = st.multiselect(
            "Default Risk", RISK_ORDER, default=RISK_ORDER
        )
    with col2:
        emp_filter = st.multiselect(
            "Employment Status",
            df["Employment_Status"].unique().tolist(),
            default=df["Employment_Status"].unique().tolist(),
        )
    with col3:
        cat_filter = st.multiselect(
            "Shopping Category",
            df["Shopping_Category_Most_Frequent"].unique().tolist(),
            default=df["Shopping_Category_Most_Frequent"].unique().tolist(),
        )
    with col4:
        late_filter = st.multiselect(
            "Late Payment History",
            ["Yes", "No"], default=["Yes", "No"]
        )

    credit_range = st.slider(
        "Credit Score Range",
        int(df["Credit_Score"].min()), int(df["Credit_Score"].max()),
        (int(df["Credit_Score"].min()), int(df["Credit_Score"].max())),
    )

    # Apply filters
    fdf = df[
        (df["Default_Risk"].astype(str).isin(risk_filter)) &
        (df["Employment_Status"].isin(emp_filter)) &
        (df["Shopping_Category_Most_Frequent"].isin(cat_filter)) &
        (df["Late_Payment_History"].isin(late_filter)) &
        (df["Credit_Score"] >= credit_range[0]) &
        (df["Credit_Score"] <= credit_range[1])
    ]

    st.markdown(f"**Showing {len(fdf):,} of {len(df):,} customers**")

    display_cols = ["Customer_ID", "Age", "Employment_Status", "Income_USD",
                    "Credit_Score", "Total_BNPL_Active_Loans", "Total_BNPL_Debt_USD",
                    "Late_Payment_History", "Shopping_Category_Most_Frequent",
                    "Average_Transaction_Value_USD", "Debt_to_Income_Ratio", "Default_Risk"]

    st.dataframe(
        fdf[display_cols].reset_index(drop=True),
        use_container_width=True,
        height=500,
    )

    # Download
    csv_bytes = fdf[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="bnpl_filtered_data.csv",
        mime="text/csv",
    )
