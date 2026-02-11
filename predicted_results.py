import streamlit as st
import pandas as pd
import subprocess
import plotly.graph_objects as go
import plotly.express as px
import random

from Functionalities.email import send_offer_email
from Functionalities.whatsapp import send_whatsapp_message, format_offer_message


def show_predictions_page():
    """Customer Next Purchase Prediction Page with Advanced Filters"""

    # ==================================================
    # LOAD DATA
    # ==================================================
    @st.cache_data
    def load_prediction_data():
        return pd.read_csv(
            r"Model_Results\Collaborative_Filtering(Customer_Based).csv"
        )

    @st.cache_data
    def load_rfm_data():
        return pd.read_csv(r"Data_Set\customer_rfm.csv")

    @st.cache_data
    def load_category_features():
        return pd.read_csv(r"Data_Set\customer_category_features.csv")

    df = load_prediction_data()
    rfm = load_rfm_data()
    category_features = load_category_features()
    
    df = df.merge(rfm, on="customer_id", how="left")
    df = df.merge(category_features, on="customer_id", how="left")

    # ==================================================
    # SIDEBAR - Communication Configuration Only
    # ==================================================
    st.sidebar.title("📧 Email Configuration")
    recipient_email = st.sidebar.text_input(
        "Recipient Email", value="sathishtv923@gmail.com", placeholder="Enter email address"
    )

    st.sidebar.divider()
    st.sidebar.title("💬 WhatsApp Configuration")
    recipient_phone = st.sidebar.text_input(
        "Recipient Phone Number", value="+916379744721", placeholder="+91XXXXXXXXXX"
    )

    wait_time = st.sidebar.slider("Wait Time (seconds)", 10, 30, 15, help="Time to wait before sending message")

    # ==================================================
    # HEADER
    # ==================================================
    st.title("🎯 Customer Next Purchase Prediction")
    
    # Custom CSS for red robot buttons
    st.markdown("""
    <style>
    /* Red robot button styling */
    button[kind="secondary"] {
        background-color: #dc3545 !important;
        color: white !important;
        border: 2px solid #c82333 !important;
        font-size: 1.5em !important;
        padding: 0.5rem !important;
    }
    button[kind="secondary"]:hover {
        background-color: #c82333 !important;
        border-color: #bd2130 !important;
        transform: scale(1.05);
        transition: all 0.2s;
    }
    button[kind="secondary"]:active {
        background-color: #bd2130 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.divider()

    # ==================================================
    # FILTERS SECTION - HOME SCREEN WITH SYNCHRONIZED LOGIC
    # ==================================================
    st.subheader("🔍 Advanced Customer Filters")
    
    # Create filter columns
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    filter_col4, filter_col5, filter_col6 = st.columns(3)
    filter_col7, filter_col8 = st.columns(2)

    # Initialize session state for filters
    if 'filters_applied' not in st.session_state:
        st.session_state.filters_applied = False
    
    if 'temp_filters' not in st.session_state:
        st.session_state.temp_filters = {}

    # Initialize filtered dataframe
    filtered_df = df.copy()

    with filter_col1:
        # Customer ID Filter
        customer_ids = ["All"] + sorted(df["customer_id"].unique().tolist())
        
        # Check if we need to update from Name selection
        if 'last_selected_name' in st.session_state and st.session_state.get('last_selected_name') != st.session_state.temp_filters.get('name'):
            # Name was just changed, update customer_id accordingly
            if st.session_state.temp_filters.get('name') != "All":
                customer_data = df[df["name"] == st.session_state.temp_filters['name']].iloc[0]
                st.session_state.temp_filters['customer_id'] = customer_data['customer_id']
        
        default_customer_id = st.session_state.temp_filters.get('customer_id', "All")
        
        selected_customer_id = st.selectbox(
            "👤 Customer ID",
            customer_ids,
            index=customer_ids.index(default_customer_id) if default_customer_id in customer_ids else 0,
            help="Filter by specific Customer ID",
            key="filter_customer_id"
        )
        
        # If customer ID changed, update all related fields
        if selected_customer_id != st.session_state.temp_filters.get('customer_id'):
            st.session_state.temp_filters['customer_id'] = selected_customer_id
            
            if selected_customer_id != "All":
                customer_data = df[df["customer_id"] == selected_customer_id].iloc[0]
                st.session_state.temp_filters['name'] = customer_data['name']
                st.session_state.temp_filters['gender'] = customer_data['gender']
                if 'state' in df.columns:
                    st.session_state.temp_filters['region'] = customer_data['state']
                if 'city_name' in df.columns:
                    st.session_state.temp_filters['city'] = customer_data['city_name']
                st.session_state.last_selected_id = selected_customer_id
                st.rerun()
            else:
                # Reset all when "All" is selected
                st.session_state.temp_filters['name'] = "All"
                st.session_state.temp_filters['gender'] = "All"
                st.session_state.temp_filters['region'] = "All"
                st.session_state.temp_filters['city'] = "All"

    with filter_col2:
        # Customer Name Filter
        customer_names = ["All"] + sorted(df["name"].dropna().unique().tolist())
        
        # Check if we need to update from ID selection
        if 'last_selected_id' in st.session_state and st.session_state.get('last_selected_id') != st.session_state.temp_filters.get('customer_id'):
            # ID was just changed, update name accordingly
            if st.session_state.temp_filters.get('customer_id') != "All":
                customer_data = df[df["customer_id"] == st.session_state.temp_filters['customer_id']].iloc[0]
                st.session_state.temp_filters['name'] = customer_data['name']
        
        default_name = st.session_state.temp_filters.get('name', "All")
        
        selected_name = st.selectbox(
            "📝 Customer Name",
            customer_names,
            index=customer_names.index(default_name) if default_name in customer_names else 0,
            help="Filter by Customer Name",
            key="filter_name"
        )
        
        # If name changed, update all related fields
        if selected_name != st.session_state.temp_filters.get('name'):
            st.session_state.temp_filters['name'] = selected_name
            
            if selected_name != "All":
                customer_data = df[df["name"] == selected_name].iloc[0]
                st.session_state.temp_filters['customer_id'] = customer_data['customer_id']
                st.session_state.temp_filters['gender'] = customer_data['gender']
                if 'state' in df.columns:
                    st.session_state.temp_filters['region'] = customer_data['state']
                if 'city_name' in df.columns:
                    st.session_state.temp_filters['city'] = customer_data['city_name']
                st.session_state.last_selected_name = selected_name
                st.rerun()
            else:
                # Reset all when "All" is selected
                st.session_state.temp_filters['customer_id'] = "All"
                st.session_state.temp_filters['gender'] = "All"
                st.session_state.temp_filters['region'] = "All"
                st.session_state.temp_filters['city'] = "All"

    with filter_col3:
        # Gender Filter - Shows auto-filled value from ID/Name selection
        genders = ["All"] + sorted(df["gender"].dropna().unique().tolist())
        
        default_gender = st.session_state.temp_filters.get('gender', "All")
        
        selected_gender = st.selectbox(
            "⚥ Gender",
            genders,
            index=genders.index(default_gender) if default_gender in genders else 0,
            help="Filter by Gender",
            key="filter_gender"
        )
        
        st.session_state.temp_filters['gender'] = selected_gender

    with filter_col4:
        # Region Filter - Shows auto-filled value from ID/Name selection
        if "state" in df.columns:
            regions = ["All"] + sorted(df["state"].dropna().unique().tolist())
            
            default_region = st.session_state.temp_filters.get('region', "All")
            
            selected_region = st.selectbox(
                "🌍 Region/State",
                regions,
                index=regions.index(default_region) if default_region in regions else 0,
                help="Filter by Region or State",
                key="filter_region"
            )
            
            st.session_state.temp_filters['region'] = selected_region
        else:
            st.text("Region: N/A")

    with filter_col5:
        # City Filter - Shows auto-filled value from ID/Name selection
        if "city_name" in df.columns:
            cities = ["All"] + sorted(df["city_name"].dropna().unique().tolist())
            
            default_city = st.session_state.temp_filters.get('city', "All")
            
            selected_city = st.selectbox(
                "🏙️ City",
                cities,
                index=cities.index(default_city) if default_city in cities else 0,
                help="Filter by City",
                key="filter_city"
            )
            
            st.session_state.temp_filters['city'] = selected_city
        else:
            st.text("City: N/A")

    with filter_col6:
        # Product Filter - Multiple Selection (NO AUTO-SYNC)
        all_products = set()
        for products_str in df["purchased_products_names"].dropna():
            products = [p.strip() for p in str(products_str).split(",") if p.strip()]
            all_products.update(products)
        
        products_list = sorted(list(all_products))
        selected_products = st.multiselect(
            "🛍️ Purchased Products",
            products_list,
            default=[],
            help="Filter by purchased products (select multiple)",
            key="filter_products"
        )
        st.session_state.temp_filters['products'] = selected_products

    with filter_col7:
        # Similarity Score Range Filter
        if "Similarity_Score" in df.columns:
            valid_scores = df["Similarity_Score"].dropna()
            if len(valid_scores) > 0:
                min_similarity = float(valid_scores.min() * 100)
                max_similarity = float(valid_scores.max() * 100)
                similarity_range = st.slider(
                    "🎯 Similarity Score Range (%)",
                    min_value=min_similarity,
                    max_value=max_similarity,
                    value=(min_similarity, max_similarity),
                    format="%.1f%%",
                    help="Filter by Similarity Score percentage",
                    key="filter_similarity"
                )
                st.session_state.temp_filters['similarity'] = similarity_range
            else:
                st.text("Similarity Score: N/A")
        else:
            st.text("Similarity Score: N/A")

    with filter_col8:
        # Total Amount Spent Range Filter
        min_spent = float(df["total_spent"].min())
        max_spent = float(df["total_spent"].max())
        spent_range = st.slider(
            "💰 Total Spent Range (₹)",
            min_value=min_spent,
            max_value=max_spent,
            value=(min_spent, max_spent),
            format="₹%.0f",
            help="Filter by Total Amount Spent",
            key="filter_spent"
        )
        st.session_state.temp_filters['spent'] = spent_range

    button_col1, button_col2, button_col3 = st.columns([1, 1, 4])
    
    with button_col1:
        if st.button("✅ Apply Filters", use_container_width=True, type="primary"):
            st.session_state.filters_applied = True
            if 'page_number' in st.session_state:
                st.session_state.page_number = 1
            st.rerun()
    
    with button_col2:
        if st.button("🔄 Reset Filters", use_container_width=True, type="secondary"):
            st.session_state.filters_applied = False
            st.session_state.temp_filters = {}
            if 'page_number' in st.session_state:
                st.session_state.page_number = 1
            if 'last_selected_id' in st.session_state:
                del st.session_state.last_selected_id
            if 'last_selected_name' in st.session_state:
                del st.session_state.last_selected_name
            st.rerun()

    st.divider()

    # ==================================================
    # APPLY FILTERS ONLY IF BUTTON CLICKED
    # ==================================================
    if st.session_state.filters_applied:
        # Apply all filters
        if st.session_state.temp_filters.get('customer_id') != "All":
            filtered_df = filtered_df[filtered_df["customer_id"] == st.session_state.temp_filters['customer_id']]
        
        if st.session_state.temp_filters.get('name') != "All":
            filtered_df = filtered_df[filtered_df["name"] == st.session_state.temp_filters['name']]
        
        if st.session_state.temp_filters.get('gender') != "All":
            filtered_df = filtered_df[filtered_df["gender"] == st.session_state.temp_filters['gender']]
        
        if st.session_state.temp_filters.get('region') and st.session_state.temp_filters['region'] != "All":
            filtered_df = filtered_df[filtered_df["state"] == st.session_state.temp_filters['region']]
        
        if st.session_state.temp_filters.get('city') and st.session_state.temp_filters['city'] != "All":
            filtered_df = filtered_df[filtered_df["city_name"] == st.session_state.temp_filters['city']]
        
        if st.session_state.temp_filters.get('products'):
            mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
            for product in st.session_state.temp_filters['products']:
                mask |= filtered_df["purchased_products_names"].str.contains(
                    product, case=False, na=False
                )
            filtered_df = filtered_df[mask]
        
        if st.session_state.temp_filters.get('similarity'):
            filtered_df = filtered_df[
                (filtered_df["Similarity_Score"] * 100 >= st.session_state.temp_filters['similarity'][0]) & 
                (filtered_df["Similarity_Score"] * 100 <= st.session_state.temp_filters['similarity'][1])
            ]
        
        if st.session_state.temp_filters.get('spent'):
            filtered_df = filtered_df[
                (filtered_df["total_spent"] >= st.session_state.temp_filters['spent'][0]) & 
                (filtered_df["total_spent"] <= st.session_state.temp_filters['spent'][1])
            ]

    # ==================================================
    # SHOW RESULTS ONLY AFTER FILTERS APPLIED
    # ==================================================
    if not st.session_state.filters_applied:
        st.info("👆 Configure your filters above and click **'Apply Filters'** to see results")
        st.stop()

    if len(filtered_df) == 0:
        st.error("❌ No customers match the current filters. Please adjust your filter criteria.")
        st.stop()

    # ==================================================
    # TWO-COLUMN LAYOUT: FILTERED RESULTS (RIGHT) + DETAILED ANALYSIS (LEFT)
    # ==================================================
    detail_col, results_col = st.columns([2, 1], gap="large")

    # ==================================================
    # RIGHT COLUMN: FILTERED CUSTOMER RESULTS WITH PAGINATION
    # ==================================================
    with results_col:
        st.markdown("### 📋 Filtered Results")
        
        # Pagination settings
        if 'page_number' not in st.session_state:
            st.session_state.page_number = 1
        
        if 'page_size' not in st.session_state:
            st.session_state.page_size = 10
        
        # Sort by total_spent
        sorted_filtered = filtered_df.sort_values("total_spent", ascending=False)
        
        total_customers = len(sorted_filtered)
        page_size = st.session_state.page_size
        
        # Calculate pagination
        total_pages = max(1, (total_customers + page_size - 1) // page_size)
        
        # Ensure page number is within bounds
        if st.session_state.page_number > total_pages:
            st.session_state.page_number = total_pages
        
        # Calculate start and end indices
        start_idx = (st.session_state.page_number - 1) * page_size
        end_idx = min(start_idx + page_size, total_customers)
        
        # Get current page data
        current_page_df = sorted_filtered.iloc[start_idx:end_idx]
        
        
        # Display customers on current page
        for idx, (_, customer) in enumerate(current_page_df.iterrows(), start=start_idx + 1):
            with st.container():
                # Create a styled card
                card_color = "#f0f8ff" if idx % 2 == 0 else "#ffffff"
                
                st.markdown(f"""
                <div style="background-color: {card_color}; padding: 12px; border-radius: 8px; border-left: 4px solid #1f77b4; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: #1f77b4;">#{idx} {customer['name']}</h4>
                    <p style="margin: 5px 0; font-size: 0.9em; color: #666;">ID: {customer['customer_id']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Metrics in mini columns
                m1, m2 = st.columns(2)
                with m1:
                    st.metric("💰 Spent", f"₹{customer['total_spent']:,.0f}", label_visibility="visible")
                with m2:
                    st.metric("📅 Recency", f"{int(customer['days_since_last_visit'])}d", label_visibility="visible")
                
                # Additional info
                col_a, col_b = st.columns(2)
                with col_a:
                    st.caption(f"📍 {customer['city_name']}")
                with col_b:
                    st.caption(f"⚥ {customer['gender']}")
                
                # View Details Button
                if st.button(
                    "View Details", 
                    key=f"view_{customer['customer_id']}", 
                    use_container_width=True,
                    type="primary"
                ):
                    st.session_state.selected_customer_id = customer['customer_id']
                    st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
        
        # Bottom pagination
        st.markdown("---")
        bottom_nav_col1, bottom_nav_col2, bottom_nav_col3 = st.columns([1, 2, 1])
        
        with bottom_nav_col1:
            if st.button("Previous", disabled=(st.session_state.page_number == 1), use_container_width=True, key="bottom_prev"):
                st.session_state.page_number -= 1
                st.rerun()
        
        with bottom_nav_col2:
            st.markdown(f"<div style='text-align: center; padding: 8px;'>Showing {start_idx + 1}-{end_idx} of {total_customers}</div>", unsafe_allow_html=True)
        
        with bottom_nav_col3:
            if st.button("Next Page", disabled=(st.session_state.page_number == total_pages), use_container_width=True, key="bottom_next"):
                st.session_state.page_number += 1
                st.rerun()

    # ==================================================
    # LEFT COLUMN: DETAILED CUSTOMER ANALYSIS
    # ==================================================
    with detail_col:
        # Determine which customer to display
        if 'selected_customer_id' in st.session_state:
            selected_customer = st.session_state.selected_customer_id
        else:
            selected_customer = sorted_filtered.iloc[0]["customer_id"]

        cust_df = df[df["customer_id"] == selected_customer].iloc[0]

        # ==================================================
        # ENHANCED HEADER WITH CUSTOMER OVERVIEW
        # ==================================================
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: white; margin: 0; font-size: 2em;">👤 {cust_df['name']}</h2>
            <p style="color: #e0e0e0; margin: 5px 0 15px 0; font-size: 1.1em;">Customer ID: {cust_df['customer_id']}</p>
            <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-top: 15px;">
                <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 8px;">
                    <div style="color: #fff; font-size: 0.9em; opacity: 0.9;">Gender</div>
                    <div style="color: #fff; font-size: 1.2em; font-weight: bold;">{cust_df['gender']}</div>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 8px;">
                    <div style="color: #fff; font-size: 0.9em; opacity: 0.9;">Location</div>
                    <div style="color: #fff; font-size: 1.2em; font-weight: bold;">{cust_df['city_name']}</div>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 8px;">
                    <div style="color: #fff; font-size: 0.9em; opacity: 0.9;">Total Spent</div>
                    <div style="color: #fff; font-size: 1.2em; font-weight: bold;">₹{cust_df['total_spent']:,.0f}</div>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 8px;">
                    <div style="color: #fff; font-size: 0.9em; opacity: 0.9;">Last Visit</div>
                    <div style="color: #fff; font-size: 1.2em; font-weight: bold;">{int(cust_df['days_since_last_visit'])} days ago</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ==================================================
        # TWO COLUMN LAYOUT FOR SELECTED CUSTOMER AND SIMILAR CUSTOMER
        # ==================================================
        main_cust_col, similar_cust_col = st.columns([1.2, 0.8], gap="large")

        # ==================================================
        # LEFT: SELECTED CUSTOMER DETAILS
        # ==================================================
        with main_cust_col:
            # RFM Metrics Cards
            st.markdown("#### 📊 Customer Metrics")
            
            recency_color = "#28a745" if cust_df['days_since_last_visit'] < 30 else "#ffc107" if cust_df['days_since_last_visit'] < 90 else "#dc3545"
            
            if 'Frequency' in cust_df.index and pd.notna(cust_df['Frequency']):
                frequency = int(cust_df['Frequency'])
            else:
                frequency = 0
            
            # Display metrics in a single row using HTML
            st.markdown(f"""
            <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                <div style="flex: 1; background: linear-gradient(135deg, {recency_color} 0%, {recency_color}dd 100%); padding: 8px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="color: white; font-size: 0.85em; opacity: 0.95; margin-bottom: 5px;">RECENCY</div>
                    <div style="color: white; font-size: 1.8em; font-weight: bold;">{int(cust_df['days_since_last_visit'])}</div>
                    <div style="color: white; font-size: 0.75em; opacity: 0.9;">days ago</div>
                </div>
                <div style="flex: 1; background: linear-gradient(135deg, #17a2b8 0%, #17a2b8dd 100%); padding: 8px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="color: white; font-size: 0.85em; opacity: 0.95; margin-bottom: 5px;">FREQUENCY</div>
                    <div style="color: white; font-size: 1.8em; font-weight: bold;">{frequency}</div>
                    <div style="color: white; font-size: 0.75em; opacity: 0.9;">purchases</div>
                </div>
                <div style="flex: 1; background: linear-gradient(135deg, #6f42c1 0%, #6f42c1dd 100%); padding: 8px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="color: white; font-size: 0.85em; opacity: 0.95; margin-bottom: 5px;">MONETARY</div>
                    <div style="color: white; font-size: 1.8em; font-weight: bold;">₹{cust_df['total_spent']:,.0f}</div>
                    <div style="color: white; font-size: 0.75em; opacity: 0.9;">total value</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Purchase History FIRST
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 7px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #28a745;">
                <h4 style="color: #495057; margin: 0;">📦 Purchase History</h4>
            </div>
            """, unsafe_allow_html=True)
            
            purchased_products = [
                p.strip()
                for p in str(cust_df["purchased_products_names"]).split(",")
                if p.strip()
            ]

            if purchased_products:
                with st.expander(f"View all {len(purchased_products)} products", expanded=True):
                    for idx, p in enumerate(purchased_products, 1):
                        st.write(f"{idx}. {p}")
            else:
                st.info("No purchase history available")

            st.markdown("<br>", unsafe_allow_html=True)

            # Category Spending Pie Chart - SECOND
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 7px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #667eea;">
                <h4 style="color: #495057; margin: 0;">💰 Spending by Category</h4>
            </div>
            """, unsafe_allow_html=True)

            spend_columns = [col for col in cust_df.index if col.endswith('_spend')]
            
            if spend_columns:
                spending_data = {}
                for col in spend_columns:
                    if pd.notna(cust_df[col]) and cust_df[col] > 0:
                        category_name = col.replace('_spend', '').replace('_', ' ').title()
                        spending_data[category_name] = float(cust_df[col])
                
                if spending_data:
                    fig = px.pie(
                        values=list(spending_data.values()),
                        names=list(spending_data.keys()),
                        hole=0.5,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    
                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent',
                        hovertemplate='<b>%{label}</b><br>₹%{value:,.2f}<br>%{percent}<extra></extra>',
                        textfont_size=11
                    )
                    
                    fig.update_layout(
                        height=280,
                        showlegend=True,
                        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                        margin=dict(l=10, r=10, t=10, b=10)
                    )
                    
                    st.markdown('<div style="display: flex; gap: 20px; align-items: flex-start;">', unsafe_allow_html=True)
                    st.markdown('<div style="flex: 1.5;">', unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True, key="spending_chart")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div style="flex: 1; padding-top: 20px;">', unsafe_allow_html=True)
                else:
                    st.info("No spending data available")
            
            st.markdown("<br>", unsafe_allow_html=True)

        # ==================================================
        # NEW LAYOUT: In Cart & Recommendations | Persona & Offer (2x2 Grid)
        # MOVED OUTSIDE main_cust_col to avoid deep nesting
        # ==================================================
        
        # Define helper functions first
        def generate_persona(row):
            prompt = f"""
Return ONLY ONE label.

Allowed:
Champions
Loyal Customers
Potential Loyalists
Big Spenders
New Customers
At Risk
Hibernating

Metrics:
Recency={row['Recency']}
Frequency={row['Frequency']}
Monetary={row['Monetary']}
TotalSpent={row['total_spent']}
"""
            result = subprocess.run(
                ["ollama", "run", "llama3.2"],
                input=prompt,
                capture_output=True,
                text=True,
            )

            for p in [
                "Champions",
                "Loyal Customers",
                "Potential Loyalists",
                "Big Spenders",
                "New Customers",
                "At Risk",
                "Hibernating",
            ]:
                if p.lower() in result.stdout.lower():
                    return p
            return "Unclassified"

        def generate_offer_message(product_name):
            prompt = f"""
Generate ONE short promotional message.
Mention ONLY this product.
No explanation.

Product: {product_name}
Tone: catchy, friendly, urgency-driven.
"""
            result = subprocess.run(
                ["ollama", "run", "llama3.2"],
                input=prompt,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip().split("\n")[0]

        # Initialize session state
        if "persona" not in st.session_state:
            st.session_state.persona = None

        # Prepare data
        import re
        same_cat_cart = [
            re.sub(r"[\[\]'\"]", "", p.strip())
            for p in str(cust_df["in_cart_same_category"]).split(",")
            if p.strip() and p.strip().lower() != 'nan'
        ]
        
        other_cat_cart = [
            re.sub(r"[\[\]'\"]", "", p.strip())
            for p in str(cust_df["in_cart_other_category"]).split(",")
            if p.strip() and p.strip().lower() != 'nan'
        ]
        
        same_cat_products = [
            p.strip()
            for p in str(cust_df["Predicted_Products_from_Same_Category"]).split(",")
            if p.strip()
        ]
        
        cross_cat_products = [
            p.strip()
            for p in str(cust_df["Predicted_Products_from_Other_Categories"]).split(",")
            if p.strip()
        ]

        # First Row: In Cart | Persona Analysis
        row1_col1, row1_col2 = st.columns(2)
        
        with row1_col1:
            # Cart Details
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 7px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #17a2b8;">
                <h4 style="color: #495057; margin: 0;">🛒 In Cart</h4>
            </div>
            """, unsafe_allow_html=True)
            
            total_cart_items = len(same_cat_cart) + len(other_cat_cart)
            
            if total_cart_items > 0:
                if same_cat_cart:
                    with st.expander(f"🔵 Same Category ({len(same_cat_cart)} items)", expanded=False):
                        for idx, item in enumerate(same_cat_cart, 1):
                            st.write(f"{idx}. {item}")
                
                if other_cat_cart:
                    with st.expander(f"🟠 Cross Category ({len(other_cat_cart)} items)", expanded=False):
                        for idx, item in enumerate(other_cat_cart, 1):
                            st.write(f"{idx}. {item}")
            else:
                st.info("Cart is empty")
        
        with row1_col2:
            # Customer Persona Analysis - Create unique button key
            persona_button_key = f"persona_btn_{cust_df['customer_id']}"
            
            # Header with robot emoji in same line
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 7px 10px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #667eea;">
                <h4 style="color: #495057; margin: 0; display: inline-block;">🎭 Persona Analysis</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Red Robot Button below header
            if st.button("🤖 Analyze", use_container_width=True, type="primary", key=persona_button_key, 
                        help="Click to analyze customer persona"):
                with st.spinner("🔍 Analyzing..."):
                    st.session_state.persona = generate_persona(cust_df)
                    st.rerun()
            
            # Display persona result below - SMALLER AND MORE COMPACT
            if st.session_state.persona:
                persona_colors = {
                    "Champions": ("🏆", "#28a745", "#d4edda"),
                    "Loyal Customers": ("💎", "#17a2b8", "#d1ecf1"),
                    "Potential Loyalists": ("⭐", "#ffc107", "#fff3cd"),
                    "Big Spenders": ("💰", "#fd7e14", "#ffe5d0"),
                    "New Customers": ("🆕", "#6f42c1", "#e7d6f5"),
                    "At Risk": ("⚠️", "#dc3545", "#f8d7da"),
                    "Hibernating": ("😴", "#6c757d", "#e2e3e5")
                }
                icon, color, bg_color = persona_colors.get(st.session_state.persona, ("👤", "#007bff", "#cfe2ff"))
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%); padding: 8px 12px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 10px;">
                    <div style="color: white; margin: 0; font-size: 0.85em; font-weight: 600;">
                        <span style="font-size: 1.2em; margin-right: 6px;">{icon}</span>{st.session_state.persona}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Second Row: Recommendations | AI Offer Generation
        row2_col1, row2_col2 = st.columns(2)
        
        with row2_col1:
            # Recommendations
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 7px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #dc3545;">
                <h4 style="color: #495057; margin: 0;">🎁 Recommendations</h4>
            </div>
            """, unsafe_allow_html=True)
            
            total_recommendations = len(same_cat_products) + len(cross_cat_products)
            
            if total_recommendations > 0:
                if same_cat_products:
                    with st.expander(f"⭐ Same ({len(same_cat_products)})", expanded=False):
                        for idx, p in enumerate(same_cat_products, 1):
                            st.write(f"{idx}. {p}")
                
                if cross_cat_products:
                    with st.expander(f"🌟 Cross-Sell ({len(cross_cat_products)})", expanded=False):
                        for idx, p in enumerate(cross_cat_products, 1):
                            st.write(f"{idx}. {p}")
            else:
                st.info("No recommendations")
        
        with row2_col2:
            # AI Offer Generation - Create unique button key
            offer_button_key = f"offer_btn_{cust_df['customer_id']}"
            
            # Header
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 7px 10px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #28a745;">
                <h4 style="color: #495057; margin: 0; display: inline-block;">🎁 AI Offer</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Customer-specific product selection
            customer_key = f"product_{cust_df['customer_id']}"
            
            if customer_key not in st.session_state:
                # Select product specific to THIS customer
                if same_cat_products:
                    st.session_state[customer_key] = random.choice(same_cat_products)
                elif cross_cat_products:
                    st.session_state[customer_key] = random.choice(cross_cat_products)
                else:
                    st.session_state[customer_key] = None
            
            # Display selected product
            if st.session_state.get(customer_key):
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                    <div style="color: white; font-size: 1em; font-weight: bold;">{st.session_state[customer_key]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Red Robot Button
            if st.button("🤖 Generate", use_container_width=True, type="primary", key=offer_button_key,
                        help="Click to generate AI offer"):
                with st.spinner("🎨 Creating offer..."):
                    offer_key = f"offer_{cust_df['customer_id']}"
                    st.session_state[offer_key] = generate_offer_message(st.session_state[customer_key])
                    st.rerun()
            
            # Display generated offer message
            offer_key = f"offer_{cust_df['customer_id']}"
            if st.session_state.get(offer_key):
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); padding: 15px; border-radius: 8px; border: 2px solid #28a745; margin-top: 10px;">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <div style="background-color: #28a745; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1em; margin-right: 8px;">💬</div>
                        <strong style="color: #155724; font-size: 0.9em;">AI Generated Message</strong>
                    </div>
                    <p style="color: #155724; font-size: 0.95em; margin: 0; line-height: 1.5;">{st.session_state[offer_key]}</p>
                </div>
                """, unsafe_allow_html=True)

        # ==================================================
        # RIGHT: SIMILAR CUSTOMER DETAILS
        # ==================================================
        with similar_cust_col:
            matched_customer_id = None
            
            if "Matched_Customer_ID" in cust_df.index:
                matched_id_value = cust_df["Matched_Customer_ID"]
                if pd.notna(matched_id_value) and str(matched_id_value).strip() != "":
                    matched_customer_id = matched_id_value

            if matched_customer_id is not None:
                similar_cust_df = df[df["customer_id"] == matched_customer_id].iloc[0]
                
                similarity_text = ""
                if pd.notna(cust_df["Similarity_Score"]):
                    similarity = float(cust_df["Similarity_Score"]) * 100
                    similarity_text = f" | Similarity: {similarity:.1f}%"
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 25px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="color: white; margin: 0; font-size: 1.5em;">🔗 Similar Customer</h3>
                    <p style="color: #fff; margin: 8px 0 0 0; font-size: 1em; opacity: 0.95;">ID: {matched_customer_id}{similarity_text}</p>
                    <p style="color: #fff; margin: 5px 0 0 0; font-size: 0.95em; opacity: 0.9;">Name: {similar_cust_df['name']}</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div style="background-color: #f8f9fa; padding: 7px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #28a745;">
                    <h4 style="color: #495057; margin: 0;">📦 Their Purchases</h4>
                </div>
                """, unsafe_allow_html=True)
                
                sim_purchased = [
                    p.strip()
                    for p in str(similar_cust_df["purchased_products_names"]).split(",")
                    if p.strip()
                ]

                if sim_purchased:
                    with st.expander(f"View all {len(sim_purchased)} products", expanded=True):
                        for idx, p in enumerate(sim_purchased, 1):
                            st.write(f"{idx}. {p}")
                else:
                    st.info("No purchase history available")
            else:
                st.markdown("""
                <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center; border: 2px dashed #dee2e6;">
                    <div style="font-size: 3em; margin-bottom: 10px;">🔍</div>
                    <h4 style="color: #6c757d; margin: 10px 0;">No Similar Customer Found</h4>
                    <p style="color: #999; font-size: 0.9em;">This customer has a unique profile</p>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # ==================================================
        # MULTI-CHANNEL DISTRIBUTION (FULL WIDTH)
        # ==================================================
        offer_key = f"offer_{cust_df['customer_id']}"
        customer_key = f"product_{cust_df['customer_id']}"
        
        if st.session_state.get(offer_key):
            with st.container():
                st.markdown("""
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 12px; border-left: 5px solid #007bff; margin-bottom: 20px;">
                    <h3 style="color: #495057; margin: 0; font-size: 1.3em;">
                        <span style="background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                            📤 Multi-Channel Distribution
                        </span>
                    </h3>
                </div>
                """, unsafe_allow_html=True)
                
                send_col1, send_col2 = st.columns(2)
                
                with send_col1:
                    
                    if st.button("📨 Send Email", use_container_width=True, type="secondary", key="send_email"):
                        with st.spinner("📧 Sending..."):
                            send_offer_email(
                                to_email=recipient_email,
                                customer_name=cust_df["name"],
                                product=st.session_state[customer_key],
                                offer_msg=st.session_state[offer_key],
                            )
                        st.success("✅ Email sent!")
                        st.balloons()
                
                with send_col2:
                    
                    if st.button("📱 Send WhatsApp", use_container_width=True, type="secondary", key="send_whatsapp"):
                        with st.spinner("💬 Sending..."):
                            whatsapp_message = format_offer_message(
                                customer_name=cust_df["name"],
                                product=st.session_state[customer_key],
                                offer_msg=st.session_state[offer_key],
                            )

                            success, message = send_whatsapp_message(
                                phone_no=recipient_phone,
                                message=whatsapp_message,
                                wait_time=wait_time,
                            )

                            if success:
                                st.success(f"✅ {message}")
                                st.balloons()
                            else:
                                st.error(f"❌ {message}")