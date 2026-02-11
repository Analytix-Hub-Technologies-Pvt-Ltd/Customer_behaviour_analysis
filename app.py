import streamlit as st
import pandas as pd
from datetime import datetime
import warnings

from Visualization.source_data import show_all_visualizations
from Streamlit.home_page_app import show_home_page

warnings.filterwarnings("ignore")

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="E-Commerce Business Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# LOAD DATA (CACHED)
# ==================================================
@st.cache_data
def load_data():
    """Load all CSV files"""
    try:
        customer_product_flat = pd.read_csv("Data_Set/customer_product_flat.csv")
        customer_category_features = pd.read_csv("Data_Set/customer_category_features.csv")
        customer_rfm = pd.read_csv("Data_Set/customer_rfm.csv")
        products_catalog = pd.read_csv("Data_Set/products_catalog.csv")
        customer_with_purchases = pd.read_csv("Data_Set/customer_with_purchases.csv")

        if "order_date" in customer_with_purchases.columns:
            customer_with_purchases["order_date"] = pd.to_datetime(
                customer_with_purchases["order_date"]
            )

        return (
            customer_product_flat,
            customer_category_features,
            customer_rfm,
            products_catalog,
            customer_with_purchases,
        )

    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Ensure all CSV files are present in the Data_Set directory.")
        return None, None, None, None, None


# ==================================================
# MAIN APP
# ==================================================
def main():

    # ------------------------------
    # SESSION STATE INIT
    # ------------------------------
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if "show_filter_dialog" not in st.session_state:
        st.session_state.show_filter_dialog = False

    if "filters_applied" not in st.session_state:
        st.session_state.filters_applied = False

    # ------------------------------
    # SIDEBAR NAVIGATION
    # ------------------------------
    st.sidebar.header("📍 Navigation")

    if st.sidebar.button("🏠 Home", use_container_width=True):
        st.session_state.page = "home"
        st.session_state.show_filter_dialog = False
        st.session_state.filters_applied = False
        st.rerun()

    if st.sidebar.button("📊 Data Visualizations", use_container_width=True):
        st.session_state.page = "visualizations"
        st.session_state.show_filter_dialog = True
        st.session_state.filters_applied = False
        st.rerun()

    if st.sidebar.button("🛒 Product Predictions", use_container_width=True):
        st.session_state.page = "predictions"
        st.session_state.show_filter_dialog = False
        st.session_state.filters_applied = False
        st.rerun()

    # New navigation button for Product-Based Customer Insights
    if st.sidebar.button("🎯 Product-Based Customer Insights", use_container_width=True):
        st.session_state.page = "product_customer_insights"
        st.session_state.show_filter_dialog = False
        st.session_state.filters_applied = False
        st.rerun()

    st.sidebar.divider()
    st.sidebar.info("Navigate between sections of the analytics dashboard")

    # Additional sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📌 Quick Guide")
    st.sidebar.markdown("""
    **🏠 Home**: Overview & KPIs
    
    **📊 Visualizations**: Data analytics with filters
    
    **🛒 Predictions**: Product recommendations
    
    **🎯 Customer Insights**: Product-based customer tracking & targeting
    """)

    # ------------------------------
    # PAGE ROUTING
    # ------------------------------
    if st.session_state.page == "home":
        display_home_page()

    elif st.session_state.page == "visualizations":
        display_visualizations_page()

    elif st.session_state.page == "predictions":
        display_predictions_page()

    elif st.session_state.page == "product_customer_insights":
        display_product_customer_insights_page()


# ==================================================
# HOME PAGE
# ==================================================
def display_home_page():
    st.title("📊 E-Commerce Business Analytics Dashboard")
    st.divider()
    show_home_page()


# ==================================================
# VISUALIZATIONS PAGE
# ==================================================
def display_visualizations_page():
    st.title("📊 Data Visualizations")
    st.divider()

    with st.spinner("Loading data..."):
        (
            customer_product_flat,
            customer_category_features,
            customer_rfm,
            products_catalog,
            customer_with_purchases,
        ) = load_data()

    if customer_with_purchases is None:
        st.stop()

    # ------------------------------
    # FILTERS
    # ------------------------------
    if st.session_state.show_filter_dialog and not st.session_state.filters_applied:
        st.subheader("🔍 Apply Filters")

        filtered_data = customer_with_purchases.copy()
        col1, col2, col3 = st.columns(3)

        # Date filter
        with col1:
            if "order_date" in customer_with_purchases.columns:
                min_date = customer_with_purchases["order_date"].min()
                max_date = customer_with_purchases["order_date"].max()

                date_range = st.date_input(
                    "📅 Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                )

                if len(date_range) == 2:
                    mask = (
                        (customer_with_purchases["order_date"] >= pd.Timestamp(date_range[0]))
                        & (customer_with_purchases["order_date"] <= pd.Timestamp(date_range[1]))
                    )
                    filtered_data = customer_with_purchases[mask]

        # Region filter
        with col2:
            if "region" in customer_with_purchases.columns:
                regions = ["All"] + sorted(
                    customer_with_purchases["region"].dropna().unique()
                )
                selected_region = st.selectbox("🌍 Region", regions)

                if selected_region != "All":
                    filtered_data = filtered_data[
                        filtered_data["region"] == selected_region
                    ]

        # Gender filter
        with col3:
            if "gender" in customer_with_purchases.columns:
                genders = ["All"] + sorted(
                    customer_with_purchases["gender"].dropna().unique()
                )
                selected_gender = st.selectbox("👤 Gender", genders)

                if selected_gender != "All":
                    filtered_data = filtered_data[
                        filtered_data["gender"] == selected_gender
                    ]

        st.session_state.filtered_data = filtered_data

        if st.button("✅ Apply Filters", use_container_width=True):
            st.session_state.filters_applied = True
            st.session_state.show_filter_dialog = False
            st.rerun()

        st.divider()

    # ------------------------------
    # SHOW VISUALIZATIONS
    # ------------------------------
    if st.session_state.filters_applied:
        st.info("🔍 Filters are active. Click 'Data Visualizations' to update filters.")

        show_all_visualizations(
            st.session_state.filtered_data,
            customer_product_flat,
            customer_category_features,
            customer_rfm,
            products_catalog,
        )


# ==================================================
# PREDICTIONS PAGE
# ==================================================
def display_predictions_page():
    """Display the product predictions page"""
    from Streamlit.predicted_results import show_predictions_page
    show_predictions_page()


# ==================================================
# PRODUCT-BASED CUSTOMER INSIGHTS PAGE
# ==================================================
def display_product_customer_insights_page():
    """Display the product-based customer insights dashboard"""
    from Streamlit.customer_prediction_insights import show_product_based_customer_insights
    show_product_based_customer_insights()


# ==================================================
# APP ENTRY
# ==================================================
if __name__ == "__main__":
    main()