
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Customer Churn Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

CUSTOMER_FILE = DATA_DIR / "customers_with_churn.csv"
ACTIVITY_FILE = DATA_DIR / "monthly_activity.csv"
COHORT_FILE = DATA_DIR / "cohort_retention.csv"

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.8rem; padding-bottom: 2rem;}
    [data-testid="stMetric"] {
        background: rgba(128,128,128,0.08);
        padding: 16px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.18);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------
@st.cache_data
def load_data():
    customers = pd.read_csv(CUSTOMER_FILE)
    activity = pd.read_csv(ACTIVITY_FILE) if ACTIVITY_FILE.exists() else pd.DataFrame()
    cohort = pd.read_csv(COHORT_FILE) if COHORT_FILE.exists() else pd.DataFrame()

    customers["Signup_Date"] = pd.to_datetime(
        customers["Signup_Date"], errors="coerce"
    )

    for column in ["Churned", "MRR", "Churn_Probability",
                   "Customer_Lifetime_Months"]:
        if column in customers.columns:
            customers[column] = pd.to_numeric(
                customers[column], errors="coerce"
            )

    if not activity.empty:
        activity["Month"] = pd.to_datetime(
            activity["Month"], errors="coerce"
        )
        for column in ["Revenue", "Active"]:
            if column in activity.columns:
                activity[column] = pd.to_numeric(
                    activity[column], errors="coerce"
                )

    return customers, activity, cohort


st.title("📊 Customer Churn & Retention Analytics")
st.caption(
    "Explore customer churn, subscription revenue, customer segments, "
    "monthly activity and cohort retention."
)

if not CUSTOMER_FILE.exists():
    st.error(
        f"Customer dataset not found: {CUSTOMER_FILE}\n\n"
        "Ensure data/processed/customers_with_churn.csv exists."
    )
    st.stop()

try:
    customers, activity, cohort = load_data()
except Exception as error:
    st.error(f"Unable to load project data: {error}")
    st.stop()

required = {
    "Customer_ID", "Segment", "Plan", "MRR",
    "Churned", "Signup_Date",
}
missing = required - set(customers.columns)

if missing:
    st.error(f"Required columns missing from customer data: {sorted(missing)}")
    st.stop()

customers = customers.dropna(subset=["Customer_ID"]).copy()
customers["Churned"] = customers["Churned"].fillna(0).astype(int)
customers["MRR"] = customers["MRR"].fillna(0)
customers["Segment"] = customers["Segment"].fillna("Unknown")
customers["Plan"] = customers["Plan"].fillna("Unknown")

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("🔎 Dashboard Filters")

segments = sorted(customers["Segment"].astype(str).unique())
plans = sorted(customers["Plan"].astype(str).unique())

selected_segments = st.sidebar.multiselect(
    "Customer segment",
    segments,
    default=segments,
)

selected_plans = st.sidebar.multiselect(
    "Subscription plan",
    plans,
    default=plans,
)

valid_dates = customers["Signup_Date"].dropna()

if not valid_dates.empty:
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    date_range = st.sidebar.date_input(
        "Signup date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range
else:
    start_date = end_date = None

filtered = customers[
    customers["Segment"].astype(str).isin(selected_segments)
    & customers["Plan"].astype(str).isin(selected_plans)
].copy()

if start_date is not None and end_date is not None:
    filtered = filtered[
        filtered["Signup_Date"].dt.date.between(start_date, end_date)
        | filtered["Signup_Date"].isna()
    ]

if filtered.empty:
    st.warning("No customers match the selected filters.")
    st.stop()

st.sidebar.divider()
st.sidebar.caption(f"{len(filtered):,} customers match your filters.")

# --------------------------------------------------
# KPI METRICS
# --------------------------------------------------
total_customers = len(filtered)
churned_customers = int(filtered["Churned"].sum())
retained_customers = total_customers - churned_customers
churn_rate = (
    churned_customers / total_customers * 100
    if total_customers else 0
)
retention_rate = 100 - churn_rate
total_mrr = filtered["MRR"].sum()
average_mrr = filtered["MRR"].mean()

if "Churn_Probability" in filtered.columns:
    avg_risk = filtered["Churn_Probability"].mean() * 100
else:
    avg_risk = float("nan")

st.subheader("Business Overview")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Customers", f"{total_customers:,}")
k2.metric("Churned Customers", f"{churned_customers:,}")
k3.metric("Churn Rate", f"{churn_rate:.2f}%")
k4.metric("Retention Rate", f"{retention_rate:.2f}%")
k5.metric("Total MRR", f"{total_mrr:,.2f}")

k6, k7 = st.columns(2)
k6.metric("Average MRR / Customer", f"{average_mrr:,.2f}")
k7.metric(
    "Average Churn Probability",
    f"{avg_risk:.2f}%" if pd.notna(avg_risk) else "N/A",
)

st.caption(
    "MRR means monthly recurring revenue. Churn rate here is the percentage "
    "of filtered customers marked as churned in the supplied dataset. "
    "It is not necessarily a monthly churn rate."
)

st.divider()

# --------------------------------------------------
# CHURN BY SEGMENT AND PLAN
# --------------------------------------------------
st.subheader("Churn Analysis")

segment_summary = (
    filtered.groupby("Segment", dropna=False)
    .agg(
        Customers=("Customer_ID", "nunique"),
        Churned=("Churned", "sum"),
        MRR=("MRR", "sum"),
    )
    .reset_index()
)
segment_summary["Churn Rate (%)"] = (
    segment_summary["Churned"]
    / segment_summary["Customers"].replace(0, pd.NA)
    * 100
).fillna(0)

plan_summary = (
    filtered.groupby("Plan", dropna=False)
    .agg(
        Customers=("Customer_ID", "nunique"),
        Churned=("Churned", "sum"),
        MRR=("MRR", "sum"),
    )
    .reset_index()
)
plan_summary["Churn Rate (%)"] = (
    plan_summary["Churned"]
    / plan_summary["Customers"].replace(0, pd.NA)
    * 100
).fillna(0)

left, right = st.columns(2)

with left:
    fig = px.bar(
        segment_summary,
        x="Segment",
        y="Churn Rate (%)",
        color="Segment",
        text_auto=".2f",
        title="Churn Rate by Customer Segment",
    )
    fig.update_layout(showlegend=False, yaxis_title="Churn rate (%)")
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.bar(
        plan_summary,
        x="Plan",
        y="Churn Rate (%)",
        color="Plan",
        text_auto=".2f",
        title="Churn Rate by Subscription Plan",
    )
    fig.update_layout(showlegend=False, yaxis_title="Churn rate (%)")
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)

with left:
    fig = px.bar(
        segment_summary,
        x="Segment",
        y="Customers",
        color="Segment",
        title="Customer Distribution by Segment",
        text_auto=True,
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.bar(
        plan_summary,
        x="Plan",
        y="MRR",
        color="Plan",
        title="Monthly Recurring Revenue by Plan",
        text_auto=".2s",
    )
    fig.update_layout(showlegend=False, yaxis_title="MRR")
    st.plotly_chart(fig, use_container_width=True)

with st.expander("View segment and plan summary tables"):
    st.markdown("**Segment summary**")
    st.dataframe(segment_summary, use_container_width=True, hide_index=True)
    st.markdown("**Plan summary**")
    st.dataframe(plan_summary, use_container_width=True, hide_index=True)

st.divider()

# --------------------------------------------------
# MONTHLY CUSTOMER ACTIVITY
# --------------------------------------------------
st.subheader("Monthly Customer Activity")

if not activity.empty and {"Month", "Revenue"}.issubset(activity.columns):
    monthly = activity.dropna(subset=["Month"]).copy()

    if "Segment" in monthly.columns:
        monthly = monthly[
            monthly["Segment"].astype(str).isin(selected_segments)
        ]
    if "Plan" in monthly.columns:
        monthly = monthly[
            monthly["Plan"].astype(str).isin(selected_plans)
        ]

    if not monthly.empty:
        monthly_summary = (
            monthly.groupby("Month", as_index=False)
            .agg(
                Revenue=("Revenue", "sum"),
                Active_Customers=(
                    "Customer_ID", "nunique"
                ) if "Customer_ID" in monthly.columns else ("Revenue", "size"),
            )
            .sort_values("Month")
        )

        left, right = st.columns(2)

        with left:
            fig = px.line(
                monthly_summary,
                x="Month",
                y="Revenue",
                markers=True,
                title="Monthly Revenue",
            )
            fig.update_layout(yaxis_title="Revenue")
            st.plotly_chart(fig, use_container_width=True)

        with right:
            fig = px.line(
                monthly_summary,
                x="Month",
                y="Active_Customers",
                markers=True,
                title="Monthly Active Customers",
            )
            fig.update_layout(yaxis_title="Unique customers")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No monthly activity matches the selected filters.")
else:
    st.info("Monthly activity data is unavailable or lacks required columns.")

st.divider()

# --------------------------------------------------
# COHORT RETENTION
# --------------------------------------------------
st.subheader("Cohort Retention Analysis")
st.caption(
    "Each row represents a signup-month cohort; columns 0, 1, 2, etc. "
    "represent the retention periods supplied by the original analysis."
)

if not cohort.empty and "Signup_Month" in cohort.columns:
    cohort_view = cohort.copy()
    cohort_view = cohort_view[
        cohort_view["Signup_Month"].astype(str).isin(
            customers.loc[
                customers["Segment"].astype(str).isin(selected_segments)
                & customers["Plan"].astype(str).isin(selected_plans),
                "Signup_Month",
            ].dropna().astype(str).unique()
        )
    ]

    period_cols = [
        c for c in cohort_view.columns
        if c != "Signup_Month" and str(c).isdigit()
    ]

    if period_cols and not cohort_view.empty:
        heatmap_data = cohort_view.set_index("Signup_Month")[period_cols]
        heatmap_data = heatmap_data.apply(pd.to_numeric, errors="coerce")

        fig = px.imshow(
            heatmap_data,
            labels={
                "x": "Retention period",
                "y": "Signup cohort",
                "color": "Retention (%)",
            },
            aspect="auto",
            color_continuous_scale="Blues",
            title="Cohort Retention Heatmap",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.download_button(
            "Download cohort retention CSV",
            data=cohort_view.to_csv(index=False).encode("utf-8"),
            file_name="cohort_retention_filtered.csv",
            mime="text/csv",
        )
    else:
        st.info("No cohort retention rows match the current filters.")
else:
    st.info("Cohort retention data is unavailable.")

st.divider()

# --------------------------------------------------
# CUSTOMER EXPLORER AND DOWNLOAD
# --------------------------------------------------
st.subheader("Customer Explorer")

display_cols = [
    c for c in [
        "Customer_ID", "Signup_Date", "Segment", "Plan", "MRR",
        "Churn_Probability", "Churned", "Churn_Date",
        "Customer_Lifetime_Months",
    ]
    if c in filtered.columns
]

customer_view = filtered[display_cols].copy()
customer_view["Churn Status"] = customer_view["Churned"].map(
    {1: "Churned", 0: "Retained"}
)

st.dataframe(
    customer_view,
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "⬇️ Download filtered customer data",
    data=customer_view.to_csv(index=False).encode("utf-8"),
    file_name="customer_churn_filtered.csv",
    mime="text/csv",
)

st.caption(
    "Dashboard generated from the project's processed CSV files. "
    "Churn probability is displayed as supplied by the dataset; it should "
    "not be interpreted as a validated prediction unless the underlying "
    "model has been evaluated."
)
