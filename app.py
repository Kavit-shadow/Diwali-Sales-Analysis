import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Diwali Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# CUSTOM DARK THEME CSS
# -----------------------------
bg_color = "#0f172a"
card_bg = "linear-gradient(135deg, #1e293b, #334155)"
text_color = "white"

st.markdown(f"""
<style>
.main {{
    background-color: {bg_color};
}}
html, body, [class*="css"]  {{
    color: {text_color};
}}
.metric-card {{
    background: {card_bg};
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.20);
    text-align: center;
    animation: fadeUp 0.7s ease;
}}
.metric-title {{font-size: 14px; opacity: 0.85;}}
.metric-value {{font-size: 30px; font-weight: 700; margin-top: 8px;}}
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.block-container {{
    padding-top: 1rem;
    padding-bottom: 2rem;
}}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Diwali Sales Data.csv", encoding="unicode_escape")

    # Clean columns if they exist
    for col in ["Status", "unnamed1", "Unnamed: 12"]:
        if col in df.columns:
            df.drop(columns=col, inplace=True)

    df.dropna(inplace=True)

    if "Amount" in df.columns:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df.dropna(subset=["Amount"], inplace=True)
        df["Amount"] = df["Amount"].astype(float)

    return df


df = load_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.title("🔍 Filters")

state_filter = st.sidebar.multiselect(
    "Select State",
    options=sorted(df["State"].unique()),
    default=sorted(df["State"].unique())
)

gender_filter = st.sidebar.multiselect(
    "Select Gender",
    options=sorted(df["Gender"].unique()),
    default=sorted(df["Gender"].unique())
)

age_filter = st.sidebar.multiselect(
    "Select Age Group",
    options=sorted(df["Age Group"].unique()),
    default=sorted(df["Age Group"].unique())
)

occupation_filter = st.sidebar.multiselect(
    "Select Occupation",
    options=sorted(df["Occupation"].unique()),
    default=sorted(df["Occupation"].unique())
)

category_filter = st.sidebar.multiselect(
    "Select Product Category",
    options=sorted(df["Product_Category"].unique()),
    default=sorted(df["Product_Category"].unique())
)

filtered_df = df[
    (df["State"].isin(state_filter)) &
    (df["Gender"].isin(gender_filter)) &
    (df["Age Group"].isin(age_filter)) &
    (df["Occupation"].isin(occupation_filter)) &
    (df["Product_Category"].isin(category_filter))
]

# -----------------------------
# HEADER
# -----------------------------
st.title("📊 Diwali Sales Analytics Dashboard")
st.caption("Dynamic Business Intelligence Dashboard for Diwali Sales Analysis")

# -----------------------------
# KPI METRICS (ANIMATED CARDS)
# -----------------------------
total_revenue = filtered_df["Amount"].sum()
total_orders = filtered_df["Orders"].sum() if "Orders" in filtered_df.columns else len(filtered_df)
avg_order_value = filtered_df["Amount"].mean()
unique_customers = filtered_df["User_ID"].nunique() if "User_ID" in filtered_df.columns else len(filtered_df)

k1, k2, k3, k4 = st.columns(4)

for col, title, value in [
    (k1, "💰 Total Revenue", f"₹{total_revenue:,.0f}"),
    (k2, "🛒 Total Orders", f"{int(total_orders):,}"),
    (k3, "📦 Avg Order Value", f"₹{avg_order_value:,.0f}"),
    (k4, "👥 Unique Customers", f"{unique_customers:,}"),
]:
    col.markdown(f"""
    <div class='metric-card'>
        <div class='metric-title'>{title}</div>
        <div class='metric-value'>{value}</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Dashboard",
    "Customer Insights",
    "Regional Analysis",
    "Product Insights",
    "Business Recommendations"
])

# -----------------------------
# TAB 1 - EXECUTIVE DASHBOARD
# -----------------------------
with tab1:
    st.subheader("Revenue Distribution")

    col1, col2 = st.columns(2)

    with col1:
        state_sales = filtered_df.groupby("State", as_index=False)["Amount"].sum().sort_values("Amount", ascending=False).head(10)
        fig = px.bar(state_sales, x="State", y="Amount", title="Top 10 States by Revenue")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        cat_sales = filtered_df.groupby("Product_Category", as_index=False)["Amount"].sum().sort_values("Amount", ascending=False)
        fig = px.pie(cat_sales, names="Product_Category", values="Amount", title="Revenue by Product Category")
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TAB 2 - CUSTOMER INSIGHTS
# -----------------------------
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        gender_sales = filtered_df.groupby("Gender", as_index=False)["Amount"].sum()
        fig = px.bar(gender_sales, x="Gender", y="Amount", color="Gender", title="Sales by Gender")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        age_sales = filtered_df.groupby("Age Group", as_index=False)["Amount"].sum()
        fig = px.bar(age_sales, x="Age Group", y="Amount", color="Age Group", title="Sales by Age Group")
        st.plotly_chart(fig, use_container_width=True)

    occ_sales = filtered_df.groupby("Occupation", as_index=False)["Amount"].sum().sort_values("Amount", ascending=False)
    fig = px.bar(occ_sales, x="Occupation", y="Amount", color="Occupation", title="Sales by Occupation")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TAB 3 - REGIONAL ANALYSIS
# -----------------------------
with tab3:
    state_orders = filtered_df.groupby("State", as_index=False)["Orders"].sum() if "Orders" in filtered_df.columns else filtered_df.groupby("State", as_index=False).size()

    if isinstance(state_orders, pd.Series):
        state_orders = state_orders.reset_index(name="Orders")

    fig = px.bar(
        state_orders.sort_values(state_orders.columns[-1], ascending=False),
        x="State",
        y=state_orders.columns[-1],
        title="Orders by State",
        color=state_orders.columns[-1]
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("State vs Revenue Heatmap")
    heat_df = filtered_df.groupby(["State", "Gender"])["Amount"].sum().reset_index()
    heat_fig = px.density_heatmap(
        heat_df,
        x="State",
        y="Gender",
        z="Amount",
        title="Revenue Heatmap by State and Gender"
    )
    st.plotly_chart(heat_fig, use_container_width=True)

# -----------------------------
# TAB 4 - PRODUCT INSIGHTS
# -----------------------------
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        product_sales = filtered_df.groupby("Product_ID", as_index=False)["Orders"].sum() if "Orders" in filtered_df.columns else filtered_df.groupby("Product_ID", as_index=False).size()
        if isinstance(product_sales, pd.Series):
            product_sales = product_sales.reset_index(name="Orders")
        product_sales = product_sales.sort_values(product_sales.columns[-1], ascending=False).head(10)

        fig = px.bar(
            product_sales,
            x="Product_ID",
            y=product_sales.columns[-1],
            color=product_sales.columns[-1],
            title="Top 10 Selling Products"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.treemap(
            filtered_df,
            path=["Product_Category"],
            values="Amount",
            title="Product Category Treemap"
        )
        st.plotly_chart(fig, use_container_width=True)

    bubble_fig = px.scatter(
        filtered_df,
        x="Age",
        y="Amount",
        size="Amount",
        color="Gender",
        hover_data=["Occupation", "State"],
        title="Customer Spending Bubble Analysis"
    )
    st.plotly_chart(bubble_fig, use_container_width=True)

# -----------------------------
# TAB 5 - BUSINESS RECOMMENDATIONS
# -----------------------------
with tab5:
    st.subheader("📈 AI-Style Business Insights")

    top_state = filtered_df.groupby("State")["Amount"].sum().idxmax()
    top_category = filtered_df.groupby("Product_Category")["Amount"].sum().idxmax()
    top_gender = filtered_df.groupby("Gender")["Amount"].sum().idxmax()
    top_age = filtered_df.groupby("Age Group")["Amount"].sum().idxmax()
    top_occ = filtered_df.groupby("Occupation")["Amount"].sum().idxmax()

    st.success(f"Top Revenue State: {top_state}")
    st.success(f"Top Product Category: {top_category}")
    st.success(f"Highest Spending Gender: {top_gender}")
    st.success(f"Highest Spending Age Group: {top_age}")
    st.success(f"Highest Spending Occupation: {top_occ}")

    st.info("Recommendation: Focus marketing campaigns on the highest-converting customer segment and expand inventory in top-performing categories/states.")

# -----------------------------
# EXPORT REPORTS
# -----------------------------
from io import BytesIO

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    filtered_df.to_excel(writer, index=False, sheet_name="Diwali Sales Report")
excel_data = excel_buffer.getvalue()

col_csv, col_excel = st.columns(2)

with col_csv:
    st.download_button(
        label="📥 Download CSV Report",
        data=csv_data,
        file_name="diwali_sales_report.csv",
        mime="text/csv"
    )

with col_excel:
    st.download_button(
        label="📊 Download Excel Report",
        data=excel_data,
        file_name="diwali_sales_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go

# # -----------------------------
# # PAGE CONFIG
# # -----------------------------
# st.set_page_config(
#     page_title="Diwali Sales Analytics Dashboard",
#     page_icon="📊",
#     layout="wide"
# )

# # -----------------------------
# # CUSTOM CSS
# # -----------------------------
# st.markdown("""
# <style>
# .main {
#     background-color: #0f172a;
# }
# .metric-card {
#     background: linear-gradient(135deg, #1e293b, #334155);
#     padding: 18px;
#     border-radius: 16px;
#     box-shadow: 0 4px 18px rgba(0,0,0,0.25);
#     text-align: center;
# }
# .block-container {
#     padding-top: 1rem;
#     padding-bottom: 2rem;
# }
# </style>
# """, unsafe_allow_html=True)

# # -----------------------------
# # LOAD DATA
# # -----------------------------
# @st.cache_data
# def load_data():
#     df = pd.read_csv("Diwali Sales Data.csv", encoding="unicode_escape")

#     # Clean columns if they exist
#     for col in ["Status", "unnamed1", "Unnamed: 12"]:
#         if col in df.columns:
#             df.drop(columns=col, inplace=True)

#     df.dropna(inplace=True)

#     if "Amount" in df.columns:
#         df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
#         df.dropna(subset=["Amount"], inplace=True)
#         df["Amount"] = df["Amount"].astype(float)

#     return df


# df = load_data()

# # -----------------------------
# # SIDEBAR FILTERS
# # -----------------------------
# st.sidebar.title("🔍 Filters")

# state_filter = st.sidebar.multiselect(
#     "Select State",
#     options=sorted(df["State"].unique()),
#     default=sorted(df["State"].unique())
# )

# gender_filter = st.sidebar.multiselect(
#     "Select Gender",
#     options=sorted(df["Gender"].unique()),
#     default=sorted(df["Gender"].unique())
# )

# age_filter = st.sidebar.multiselect(
#     "Select Age Group",
#     options=sorted(df["Age Group"].unique()),
#     default=sorted(df["Age Group"].unique())
# )

# occupation_filter = st.sidebar.multiselect(
#     "Select Occupation",
#     options=sorted(df["Occupation"].unique()),
#     default=sorted(df["Occupation"].unique())
# )

# category_filter = st.sidebar.multiselect(
#     "Select Product Category",
#     options=sorted(df["Product_Category"].unique()),
#     default=sorted(df["Product_Category"].unique())
# )

# filtered_df = df[
#     (df["State"].isin(state_filter)) &
#     (df["Gender"].isin(gender_filter)) &
#     (df["Age Group"].isin(age_filter)) &
#     (df["Occupation"].isin(occupation_filter)) &
#     (df["Product_Category"].isin(category_filter))
# ]

# # -----------------------------
# # HEADER
# # -----------------------------
# st.title("📊 Diwali Sales Analytics Dashboard")
# st.caption("Dynamic Business Intelligence Dashboard for Diwali Sales Analysis")

# # -----------------------------
# # KPI METRICS
# # -----------------------------
# total_revenue = filtered_df["Amount"].sum()
# total_orders = filtered_df["Orders"].sum() if "Orders" in filtered_df.columns else len(filtered_df)
# avg_order_value = filtered_df["Amount"].mean()
# unique_customers = filtered_df["User_ID"].nunique() if "User_ID" in filtered_df.columns else len(filtered_df)

# col1, col2, col3, col4 = st.columns(4)
# col1.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}")
# col2.metric("🛒 Total Orders", f"{int(total_orders):,}")
# col3.metric("📦 Avg Order Value", f"₹{avg_order_value:,.0f}")
# col4.metric("👥 Unique Customers", f"{unique_customers:,}")

# # -----------------------------
# # TABS
# # -----------------------------
# tab1, tab2, tab3, tab4, tab5 = st.tabs([
#     "Executive Dashboard",
#     "Customer Insights",
#     "Regional Analysis",
#     "Product Insights",
#     "Business Recommendations"
# ])

# # -----------------------------
# # TAB 1 - EXECUTIVE DASHBOARD
# # -----------------------------
# with tab1:
#     st.subheader("Revenue Distribution")

#     col1, col2 = st.columns(2)

#     with col1:
#         state_sales = filtered_df.groupby("State", as_index=False)["Amount"].sum().sort_values("Amount", ascending=False).head(10)
#         fig = px.bar(state_sales, x="State", y="Amount", title="Top 10 States by Revenue")
#         st.plotly_chart(fig, use_container_width=True)

#     with col2:
#         cat_sales = filtered_df.groupby("Product_Category", as_index=False)["Amount"].sum().sort_values("Amount", ascending=False)
#         fig = px.pie(cat_sales, names="Product_Category", values="Amount", title="Revenue by Product Category")
#         st.plotly_chart(fig, use_container_width=True)

# # -----------------------------
# # TAB 2 - CUSTOMER INSIGHTS
# # -----------------------------
# with tab2:
#     col1, col2 = st.columns(2)

#     with col1:
#         gender_sales = filtered_df.groupby("Gender", as_index=False)["Amount"].sum()
#         fig = px.bar(gender_sales, x="Gender", y="Amount", color="Gender", title="Sales by Gender")
#         st.plotly_chart(fig, use_container_width=True)

#     with col2:
#         age_sales = filtered_df.groupby("Age Group", as_index=False)["Amount"].sum()
#         fig = px.bar(age_sales, x="Age Group", y="Amount", color="Age Group", title="Sales by Age Group")
#         st.plotly_chart(fig, use_container_width=True)

#     occ_sales = filtered_df.groupby("Occupation", as_index=False)["Amount"].sum().sort_values("Amount", ascending=False)
#     fig = px.bar(occ_sales, x="Occupation", y="Amount", color="Occupation", title="Sales by Occupation")
#     st.plotly_chart(fig, use_container_width=True)

# # -----------------------------
# # TAB 3 - REGIONAL ANALYSIS
# # -----------------------------
# with tab3:
#     state_orders = filtered_df.groupby("State", as_index=False)["Orders"].sum() if "Orders" in filtered_df.columns else filtered_df.groupby("State", as_index=False).size()

#     if isinstance(state_orders, pd.Series):
#         state_orders = state_orders.reset_index(name="Orders")

#     fig = px.bar(state_orders.sort_values(state_orders.columns[-1], ascending=False),
#                  x="State", y=state_orders.columns[-1],
#                  title="Orders by State")
#     st.plotly_chart(fig, use_container_width=True)

# # -----------------------------
# # TAB 4 - PRODUCT INSIGHTS
# # -----------------------------
# with tab4:
#     col1, col2 = st.columns(2)

#     with col1:
#         product_sales = filtered_df.groupby("Product_ID", as_index=False)["Orders"].sum() if "Orders" in filtered_df.columns else filtered_df.groupby("Product_ID", as_index=False).size()
#         if isinstance(product_sales, pd.Series):
#             product_sales = product_sales.reset_index(name="Orders")
#         product_sales = product_sales.sort_values(product_sales.columns[-1], ascending=False).head(10)

#         fig = px.bar(product_sales,
#                      x="Product_ID",
#                      y=product_sales.columns[-1],
#                      title="Top 10 Selling Products")
#         st.plotly_chart(fig, use_container_width=True)

#     with col2:
#         fig = px.treemap(filtered_df,
#                          path=["Product_Category"],
#                          values="Amount",
#                          title="Product Category Treemap")
#         st.plotly_chart(fig, use_container_width=True)

# # -----------------------------
# # TAB 5 - BUSINESS RECOMMENDATIONS
# # -----------------------------
# with tab5:
#     st.subheader("📈 AI-Style Business Insights")

#     top_state = filtered_df.groupby("State")["Amount"].sum().idxmax()
#     top_category = filtered_df.groupby("Product_Category")["Amount"].sum().idxmax()
#     top_gender = filtered_df.groupby("Gender")["Amount"].sum().idxmax()
#     top_age = filtered_df.groupby("Age Group")["Amount"].sum().idxmax()
#     top_occ = filtered_df.groupby("Occupation")["Amount"].sum().idxmax()

#     st.success(f"Top Revenue State: {top_state}")
#     st.success(f"Top Product Category: {top_category}")
#     st.success(f"Highest Spending Gender: {top_gender}")
#     st.success(f"Highest Spending Age Group: {top_age}")
#     st.success(f"Highest Spending Occupation: {top_occ}")

#     st.info("Recommendation: Focus marketing campaigns on the highest-converting customer segment and expand inventory in top-performing categories/states.")

# # -----------------------------
# # DOWNLOAD FILTERED DATA
# # -----------------------------
# st.download_button(
#     label="📥 Download Filtered Data",
#     data=filtered_df.to_csv(index=False),
#     file_name="filtered_diwali_sales.csv",
#     mime="text/csv"
# )

