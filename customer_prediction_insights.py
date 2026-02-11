import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

# Note: st.set_page_config() is already set in app.py
# Do not set it again here to avoid conflicts


# ==================================================
# LOAD ALL DATA (CACHED)
# ==================================================
@st.cache_data
def load_all_data():
    """Load all datasets"""
    try:
        # Prediction data
        predictions = pd.read_csv("Model_Results/Customer Prediction/product_customer_predictions_embeddings.csv")
        
        # Customer datasets
        customer_category_features = pd.read_csv("Data_Set/customer_category_features.csv")
        customer_product_flat = pd.read_csv("Data_Set/customer_product_flat.csv")
        customer_rfm = pd.read_csv("Data_Set/customer_rfm.csv")
        customer_with_purchases = pd.read_csv("Data_Set/customer_with_purchases.csv")
        products_catalog = pd.read_csv("Data_Set/products_catalog.csv")
        
        # Convert date column
        if "order_date" in customer_with_purchases.columns:
            customer_with_purchases["order_date"] = pd.to_datetime(customer_with_purchases["order_date"])
        
        return (
            predictions,
            customer_category_features,
            customer_product_flat,
            customer_rfm,
            customer_with_purchases,
            products_catalog
        )
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None, None


# ==================================================
# DATA PREPROCESSING
# ==================================================
def preprocess_prediction_data(df):
    """Clean and prepare prediction data"""
    df = df.copy()
    
    # Handle missing values
    df['region'] = df['region'].fillna('Unknown')
    df['city'] = df['city'].fillna('Unknown')
    df['gender'] = df['gender'].fillna('Unknown')
    
    # Create propensity categories
    df['propensity_category'] = pd.cut(
        df['propensity_score'], 
        bins=[0, 0.3, 0.6, 1.0],
        labels=['Low', 'Medium', 'High']
    )
    
    # Create spending categories
    df['spending_category'] = pd.qcut(
        df['total_spent'], 
        q=3,
        labels=['Low Spender', 'Medium Spender', 'High Spender'],
        duplicates='drop'
    )
    
    # Create engagement score
    df['engagement_score'] = (
        df['propensity_score'] * 0.4 +
        df['embedding_similarity'] * 0.3 +
        (df['total_transactions'] / df['total_transactions'].max()) * 0.3
    )
    
    return df


def merge_customer_data(predictions, customer_purchases, customer_rfm, customer_category_features):
    """Merge all customer data with predictions"""
    
    # Merge predictions with purchases
    merged = predictions.merge(
        customer_purchases[['customer_id', 'name', 'phone_number', 'order_date', 
                           'order_quarter', 'days_since_last_visit', 'state', 
                           'in_cart_same_category', 'in_cart_other_category']].drop_duplicates('customer_id'),
        on='customer_id',
        how='left',
        suffixes=('', '_purchase')
    )
    
    # Merge with RFM
    merged = merged.merge(
        customer_rfm,
        on='customer_id',
        how='left'
    )
    
    # Merge with category features
    merged = merged.merge(
        customer_category_features,
        on='customer_id',
        how='left'
    )
    
    return merged


# ==================================================
# INLINE FILTERS (TOP OF PAGE)
# ==================================================
def display_inline_filters(df, products_catalog):
    """Display filters at the top of the page in full width"""
    
    st.markdown("### 🔍 Product-Based Customer Filters")
    
    # Create filter columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        # Category filter
        categories = ['All'] + sorted(df['category'].unique().tolist())
        selected_category = st.selectbox("📦 Product Category", categories, key='category_filter')
    
    with col2:
        # Product filter based on category
        if selected_category != 'All':
            products = ['All'] + sorted(df[df['category'] == selected_category]['product'].unique().tolist())
        else:
            products = ['All'] + sorted(df['product'].unique().tolist())
        selected_product = st.selectbox("🛍️ Specific Product", products, key='product_filter')
    
    with col3:
        # Propensity range
        propensity_range = st.slider(
            "🎯 Propensity Score",
            min_value=0.0,
            max_value=1.0,
            value=(0.0, 1.0),
            step=0.05,
            key='propensity_filter'
        )
    
    with col4:
        # Region filter
        regions = ['All'] + sorted(df['region'].unique().tolist())
        selected_region = st.selectbox("🌍 Region", regions, key='region_filter')
    
    with col5:
        # Price range
        min_price = float(df['price_inr'].min())
        max_price = float(df['price_inr'].max())
        price_range = st.slider(
            "💰 Price Range (INR)",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            key='price_filter'
        )
    
    # Second row of filters
    col6, col7, col8, col9, col10 = st.columns(5)
    
    with col6:
        # Gender filter
        genders = ['All'] + sorted(df['gender'].unique().tolist())
        selected_gender = st.selectbox("👤 Gender", genders, key='gender_filter')
    
    with col7:
        # Spending category
        spending_cats = ['All', 'High Spender', 'Medium Spender', 'Low Spender']
        selected_spending = st.selectbox("💵 Spending Level", spending_cats, key='spending_filter')
    
    with col8:
        # RFM Segment (if available)
        if 'Recency' in df.columns:
            max_recency_value = int(df['Recency'].max())
            default_recency = min(365, max_recency_value)  # Use the smaller value
            recency_max = st.number_input(
                "📅 Max Days Since Visit",
                min_value=0,
                max_value=max_recency_value,
                value=default_recency,
                key='recency_filter'
            )
        else:
            recency_max = 365
    
    with col9:
        # Frequency filter
        if 'Frequency' in df.columns:
            max_frequency_value = int(df['Frequency'].max())
            min_frequency = st.number_input(
                "🔄 Min Purchase Frequency",
                min_value=0,
                max_value=max_frequency_value,
                value=0,
                key='frequency_filter'
            )
        else:
            min_frequency = 0
    
    with col10:
        # Top N customers
        top_n = st.number_input(
            "📊 Show Top N Customers",
            min_value=10,
            max_value=1000,
            value=100,
            step=10,
            key='top_n_filter'
        )
    
    st.divider()
    
    # Apply filters
    filtered_df = df.copy()
    
    # Category filter
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    # Product filter
    if selected_product != 'All':
        filtered_df = filtered_df[filtered_df['product'] == selected_product]
    
    # Propensity filter
    filtered_df = filtered_df[
        (filtered_df['propensity_score'] >= propensity_range[0]) &
        (filtered_df['propensity_score'] <= propensity_range[1])
    ]
    
    # Region filter
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
    
    # Price filter
    filtered_df = filtered_df[
        (filtered_df['price_inr'] >= price_range[0]) &
        (filtered_df['price_inr'] <= price_range[1])
    ]
    
    # Gender filter
    if selected_gender != 'All':
        filtered_df = filtered_df[filtered_df['gender'] == selected_gender]
    
    # Spending filter
    if selected_spending != 'All':
        filtered_df = filtered_df[filtered_df['spending_category'] == selected_spending]
    
    # Recency filter
    if 'Recency' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Recency'] <= recency_max]
    
    # Frequency filter
    if 'Frequency' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Frequency'] >= min_frequency]
    
    # Sort by propensity and limit to top N
    filtered_df = filtered_df.sort_values('propensity_score', ascending=False).head(top_n)
    
    return filtered_df, selected_product, selected_category


# ==================================================
# FILTER SUMMARY
# ==================================================
def display_filter_summary(original_count, filtered_count, selected_product, selected_category):
    """Display summary of applied filters"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Original Records",
            f"{original_count:,}",
            help="Total predictions before filtering"
        )
    
    with col2:
        st.metric(
            "Filtered Records",
            f"{filtered_count:,}",
            f"-{original_count - filtered_count:,}",
            delta_color="inverse",
            help="Records after applying filters"
        )
    
    with col3:
        filter_pct = (filtered_count / original_count * 100) if original_count > 0 else 0
        st.metric(
            "Filter Efficiency",
            f"{filter_pct:.1f}%",
            help="Percentage of data retained after filtering"
        )
    
    with col4:
        unique_customers = filtered_count
        st.metric(
            "Unique Customers",
            f"{unique_customers:,}",
            help="Number of unique customers in filtered results"
        )
    
    # Display active product filter
    if selected_product != 'All':
        st.info(f"🎯 **Active Product Filter:** {selected_product} ({selected_category})")
    elif selected_category != 'All':
        st.info(f"📦 **Active Category Filter:** {selected_category}")
    
    st.divider()


# ==================================================
# CUSTOMER TRACKING TABLE
# ==================================================
def display_customer_tracking_table(df):
    """Display detailed customer tracking table for selected product"""
    
    st.subheader("👥 Customer Tracking & Details")
    
    # Prepare display columns
    display_columns = [
        'customer_id', 'name', 'product', 'category', 'propensity_score',
        'embedding_similarity', 'total_spent', 'total_transactions',
        'Recency', 'Frequency', 'Monetary', 'gender', 'region', 'city',
        'phone_number', 'engagement_score'
    ]
    
    # Select available columns
    available_columns = [col for col in display_columns if col in df.columns]
    
    # Create display dataframe
    display_df = df[available_columns].copy()
    
    # Format numeric columns
    if 'propensity_score' in display_df.columns:
        display_df['propensity_score'] = display_df['propensity_score'].apply(lambda x: f"{x:.2%}")
    if 'embedding_similarity' in display_df.columns:
        display_df['embedding_similarity'] = display_df['embedding_similarity'].apply(lambda x: f"{x:.3f}")
    if 'engagement_score' in display_df.columns:
        display_df['engagement_score'] = display_df['engagement_score'].apply(lambda x: f"{x:.2%}")
    if 'total_spent' in display_df.columns:
        display_df['total_spent'] = display_df['total_spent'].apply(lambda x: f"₹{x:,.0f}")
    if 'Monetary' in display_df.columns:
        display_df['Monetary'] = display_df['Monetary'].apply(lambda x: f"₹{x:,.0f}")
    
    # Rename columns for better display
    column_rename = {
        'customer_id': 'Customer ID',
        'name': 'Name',
        'product': 'Product',
        'category': 'Category',
        'propensity_score': 'Propensity',
        'embedding_similarity': 'Similarity',
        'total_spent': 'Total Spent',
        'total_transactions': 'Transactions',
        'Recency': 'Days Since Visit',
        'Frequency': 'Purchase Freq',
        'Monetary': 'RFM Value',
        'gender': 'Gender',
        'region': 'Region',
        'city': 'City',
        'phone_number': 'Phone',
        'engagement_score': 'Engagement'
    }
    
    display_df = display_df.rename(columns={k: v for k, v in column_rename.items() if k in display_df.columns})
    
    # Display with styling
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # Export button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Customer List (CSV)",
        data=csv,
        file_name=f"customer_tracking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.divider()


# ==================================================
# CUSTOMER INSIGHTS OVERVIEW
# ==================================================
def display_customer_insights_overview(df):
    """Display key customer insights for the filtered product"""
    
    st.subheader("📊 Customer Insights Overview")
    
    # Calculate key metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        avg_propensity = df['propensity_score'].mean()
        st.metric("Avg Propensity", f"{avg_propensity:.1%}")
    
    with col2:
        high_prop_count = (df['propensity_score'] > 0.7).sum()
        st.metric("High Propensity", f"{high_prop_count}")
    
    with col3:
        if 'Monetary' in df.columns:
            avg_monetary = df['Monetary'].mean()
            st.metric("Avg RFM Value", f"₹{avg_monetary:,.0f}")
        else:
            avg_spent = df['total_spent'].mean()
            st.metric("Avg Spent", f"₹{avg_spent:,.0f}")
    
    with col4:
        if 'Recency' in df.columns:
            avg_recency = df['Recency'].mean()
            st.metric("Avg Recency", f"{avg_recency:.0f} days")
        else:
            st.metric("Avg Recency", "N/A")
    
    with col5:
        if 'Frequency' in df.columns:
            avg_frequency = df['Frequency'].mean()
            st.metric("Avg Frequency", f"{avg_frequency:.1f}")
        else:
            avg_transactions = df['total_transactions'].mean()
            st.metric("Avg Transactions", f"{avg_transactions:.1f}")
    
    with col6:
        total_revenue_potential = df['total_spent'].sum()
        st.metric("Revenue Potential", f"₹{total_revenue_potential:,.0f}")
    
    st.divider()


# ==================================================
# CUSTOMER DISTRIBUTION VISUALIZATIONS
# ==================================================
def display_customer_distributions(df):
    """Display customer distribution charts"""
    
    st.subheader("📈 Customer Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Propensity distribution
        fig = px.histogram(
            df,
            x='propensity_score',
            nbins=30,
            title='Customer Propensity Distribution',
            labels={'propensity_score': 'Propensity Score'},
            color_discrete_sequence=['#3498db']
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # RFM Scatter
        if 'Recency' in df.columns and 'Monetary' in df.columns:
            fig = px.scatter(
                df,
                x='Recency',
                y='Monetary',
                size='Frequency' if 'Frequency' in df.columns else None,
                color='propensity_score',
                title='RFM Analysis with Propensity',
                labels={
                    'Recency': 'Days Since Last Visit',
                    'Monetary': 'Customer Value (INR)',
                    'propensity_score': 'Propensity'
                },
                color_continuous_scale='RdYlGn',
                hover_data=['customer_id', 'name'] if 'name' in df.columns else ['customer_id']
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Spending distribution
            fig = px.box(
                df,
                y='total_spent',
                color='propensity_category',
                title='Spending Distribution by Propensity',
                labels={'total_spent': 'Total Spent (INR)'},
                color_discrete_map={'High': '#2ecc71', 'Medium': '#f39c12', 'Low': '#e74c3c'}
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()


# ==================================================
# CUSTOMER SEGMENTATION
# ==================================================
def display_customer_segmentation(df):
    """Display customer segmentation for the product"""
    
    st.subheader("🎯 Customer Segmentation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gender distribution
        if 'gender' in df.columns:
            gender_stats = df.groupby('gender').agg({
                'customer_id': 'count',
                'propensity_score': 'mean',
                'total_spent': 'sum'
            }).reset_index()
            gender_stats.columns = ['Gender', 'Count', 'Avg Propensity', 'Total Spent']
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Customer Count',
                x=gender_stats['Gender'],
                y=gender_stats['Count'],
                marker_color='#3498db'
            ))
            fig.update_layout(
                title='Customers by Gender',
                xaxis_title='Gender',
                yaxis_title='Number of Customers',
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Regional distribution
        if 'region' in df.columns:
            region_stats = df.groupby('region').agg({
                'customer_id': 'count',
                'propensity_score': 'mean'
            }).reset_index()
            region_stats.columns = ['Region', 'Count', 'Avg Propensity']
            region_stats = region_stats.sort_values('Count', ascending=False).head(10)
            
            fig = px.bar(
                region_stats,
                x='Count',
                y='Region',
                orientation='h',
                title='Top 10 Regions by Customer Count',
                labels={'Count': 'Number of Customers'},
                color='Avg Propensity',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()


# ==================================================
# CATEGORY SPENDING ANALYSIS
# ==================================================
def display_category_spending_analysis(df):
    """Display customer spending patterns across categories"""
    
    st.subheader("💰 Category Spending Patterns")
    
    # Get category spending columns
    spending_cols = [col for col in df.columns if col.endswith('_spend') and col != 'total_spent']
    pct_cols = [col for col in df.columns if col.endswith('_pct')]
    
    if spending_cols:
        # Calculate average spending across categories
        category_spending = {}
        for col in spending_cols:
            category_name = col.replace('_spend', '').replace('_', ' ').title()
            category_spending[category_name] = df[col].mean()
        
        # Create dataframe
        cat_df = pd.DataFrame(list(category_spending.items()), columns=['Category', 'Avg Spending'])
        cat_df = cat_df.sort_values('Avg Spending', ascending=False).head(10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart
            fig = px.bar(
                cat_df,
                x='Avg Spending',
                y='Category',
                orientation='h',
                title='Average Spending by Category',
                labels={'Avg Spending': 'Average Spending (INR)'},
                color='Avg Spending',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Pie chart for percentage
            if pct_cols:
                category_pct = {}
                for col in pct_cols[:10]:  # Top 10
                    category_name = col.replace('_pct', '').replace('_', ' ').title()
                    category_pct[category_name] = df[col].mean()
                
                pct_df = pd.DataFrame(list(category_pct.items()), columns=['Category', 'Avg Percentage'])
                pct_df = pct_df[pct_df['Avg Percentage'] > 0].sort_values('Avg Percentage', ascending=False)
                
                fig = px.pie(
                    pct_df,
                    names='Category',
                    values='Avg Percentage',
                    title='Category Purchase Distribution'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    st.divider()


# ==================================================
# CUSTOMER PURCHASE BEHAVIOR
# ==================================================
def display_purchase_behavior(df):
    """Display customer purchase behavior patterns"""
    
    st.subheader("🛒 Purchase Behavior Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Transaction frequency vs Propensity
        if 'Frequency' in df.columns:
            fig = px.scatter(
                df,
                x='Frequency',
                y='propensity_score',
                color='spending_category',
                title='Purchase Frequency vs Propensity',
                labels={
                    'Frequency': 'Purchase Frequency',
                    'propensity_score': 'Propensity Score'
                },
                color_discrete_map={
                    'Low Spender': '#e74c3c',
                    'Medium Spender': '#f39c12',
                    'High Spender': '#2ecc71'
                },
                opacity=0.6
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Cart behavior
        if 'in_cart_same_category' in df.columns and 'in_cart_other_category' in df.columns:
            cart_data = pd.DataFrame({
                'Cart Type': ['Same Category', 'Other Category'],
                'Avg Items': [
                    df['in_cart_same_category'].mean(),
                    df['in_cart_other_category'].mean()
                ]
            })
            
            fig = px.bar(
                cart_data,
                x='Cart Type',
                y='Avg Items',
                title='Average Items in Cart',
                labels={'Avg Items': 'Average Number of Items'},
                color='Cart Type',
                color_discrete_sequence=['#9b59b6', '#e67e22']
            )
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Engagement distribution
        fig = px.histogram(
            df,
            x='engagement_score',
            nbins=25,
            title='Customer Engagement Distribution',
            labels={'engagement_score': 'Engagement Score'},
            color_discrete_sequence=['#16a085']
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()


# ==================================================
# TOP CUSTOMERS LIST
# ==================================================
def display_top_customers(df):
    """Display top customers for targeted campaigns"""
    
    st.subheader("🏆 Top Priority Customers for Targeted Campaigns")
    
    # Create priority score
    df_top = df.copy()
    df_top['priority_score'] = (
        df_top['propensity_score'] * 0.5 +
        df_top['engagement_score'] * 0.3 +
        (df_top['total_spent'] / df_top['total_spent'].max()) * 0.2
    )
    
    # Sort and select top 20
    df_top = df_top.sort_values('priority_score', ascending=False).head(20)
    
    # Prepare display
    display_cols = ['customer_id', 'name', 'propensity_score', 'engagement_score', 
                   'total_spent', 'Recency', 'Frequency', 'phone_number', 'city', 'priority_score']
    available_cols = [col for col in display_cols if col in df_top.columns]
    
    top_display = df_top[available_cols].copy()
    
    # Format
    if 'propensity_score' in top_display.columns:
        top_display['propensity_score'] = top_display['propensity_score'].apply(lambda x: f"{x:.1%}")
    if 'engagement_score' in top_display.columns:
        top_display['engagement_score'] = top_display['engagement_score'].apply(lambda x: f"{x:.1%}")
    if 'priority_score' in top_display.columns:
        top_display['priority_score'] = top_display['priority_score'].apply(lambda x: f"{x:.1%}")
    if 'total_spent' in top_display.columns:
        top_display['total_spent'] = top_display['total_spent'].apply(lambda x: f"₹{x:,.0f}")
    
    # Add rank
    top_display.insert(0, 'Rank', range(1, len(top_display) + 1))
    
    # Rename
    rename_dict = {
        'customer_id': 'Customer ID',
        'name': 'Name',
        'propensity_score': 'Propensity',
        'engagement_score': 'Engagement',
        'total_spent': 'Total Spent',
        'Recency': 'Days Since Visit',
        'Frequency': 'Purchases',
        'phone_number': 'Phone',
        'city': 'City',
        'priority_score': 'Priority Score'
    }
    top_display = top_display.rename(columns={k: v for k, v in rename_dict.items() if k in top_display.columns})
    
    # Display
    st.dataframe(top_display, use_container_width=True, hide_index=True, height=500)
    
    # Campaign recommendations
    st.markdown("#### 📢 Campaign Recommendations")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success(f"""
        **🎯 Immediate Action**
        - Target top 10 customers
        - Send personalized offers
        - Expected conversion: 70%+
        """)
    
    with col2:
        st.info(f"""
        **📧 Email Campaign**
        - Include all top 20 customers
        - Highlight product benefits
        - Add time-limited offer
        """)
    
    with col3:
        st.warning(f"""
        **📱 WhatsApp Follow-up**
        - Contact high-engagement customers
        - Share product details
        - Schedule calls if needed
        """)
    
    # Export top customers
    csv = top_display.to_csv(index=False)
    st.download_button(
        label="📥 Download Top Customers List",
        data=csv,
        file_name=f"top_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.divider()


# ==================================================
# CUSTOMER JOURNEY TIMELINE
# ==================================================
def display_customer_journey(df, customer_purchases):
    """Display customer journey and order patterns"""
    
    st.subheader("🗓️ Customer Order Patterns")
    
    # Get customer IDs from filtered data
    customer_ids = df['customer_id'].unique()
    
    # Filter purchases for these customers
    customer_orders = customer_purchases[customer_purchases['customer_id'].isin(customer_ids)].copy()
    
    if len(customer_orders) > 0 and 'order_date' in customer_orders.columns:
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Orders over time
            orders_by_date = customer_orders.groupby(
                customer_orders['order_date'].dt.to_period('M')
            ).size().reset_index()
            orders_by_date.columns = ['Month', 'Orders']
            orders_by_date['Month'] = orders_by_date['Month'].astype(str)
            
            fig = px.line(
                orders_by_date,
                x='Month',
                y='Orders',
                title='Order Trend Over Time',
                labels={'Orders': 'Number of Orders', 'Month': 'Month'},
                markers=True
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Order quarters
            if 'order_quarter' in customer_orders.columns:
                quarter_orders = customer_orders['order_quarter'].value_counts().reset_index()
                quarter_orders.columns = ['Quarter', 'Orders']
                quarter_orders = quarter_orders.sort_values('Quarter')
                
                fig = px.bar(
                    quarter_orders,
                    x='Quarter',
                    y='Orders',
                    title='Orders by Quarter',
                    labels={'Orders': 'Number of Orders'},
                    color='Orders',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
    
    st.divider()


# ==================================================
# ACTIONABLE INSIGHTS
# ==================================================
def display_actionable_insights(df, selected_product):
    """Display actionable insights based on filtered data"""
    
    st.subheader("💡 Actionable Insights & Recommendations")
    
    # Calculate metrics
    high_prop = df[df['propensity_score'] > 0.7]
    medium_prop = df[(df['propensity_score'] >= 0.4) & (df['propensity_score'] <= 0.7)]
    
    if 'Recency' in df.columns:
        at_risk = df[(df['propensity_score'] < 0.4) & (df['Recency'] > 30)]
    else:
        at_risk = df[df['propensity_score'] < 0.4]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success(f"""
        ### 🎯 High Priority
        **{len(high_prop)} Customers**
        
        - Propensity: >70%
        - Revenue Potential: ₹{high_prop['total_spent'].sum():,.0f}
        - Avg Spent: ₹{high_prop['total_spent'].mean():,.0f}
        
        **Action:** Launch immediate campaign
        **Channel:** Email + WhatsApp
        **Offer:** Exclusive product access
        """)
    
    with col2:
        st.info(f"""
        ### 🔄 Medium Priority
        **{len(medium_prop)} Customers**
        
        - Propensity: 40-70%
        - Revenue Potential: ₹{medium_prop['total_spent'].sum():,.0f}
        - Avg Spent: ₹{medium_prop['total_spent'].mean():,.0f}
        
        **Action:** Nurture campaign
        **Channel:** Email series
        **Offer:** Limited-time discount
        """)
    
    with col3:
        st.warning(f"""
        ### ⚠️ Re-engagement
        **{len(at_risk)} Customers**
        
        - Propensity: <40%
        - Revenue Potential: ₹{at_risk['total_spent'].sum():,.0f}
        - Avg Spent: ₹{at_risk['total_spent'].mean():,.0f}
        
        **Action:** Win-back campaign
        **Channel:** Special offers
        **Offer:** 20% off + free shipping
        """)
    
    # Product-specific insights
    if selected_product != 'All':
        st.markdown(f"#### 📦 Product-Specific Insights: {selected_product}")
        
        col4, col5 = st.columns(2)
        
        with col4:
            st.info(f"""
            **Top Customer Segments:**
            - High Spenders: {(df['spending_category'] == 'High Spender').sum()} customers
            - Active Buyers: {(df['Frequency'] > df['Frequency'].median()).sum() if 'Frequency' in df.columns else 'N/A'} customers
            - Recent Visitors: {(df['Recency'] < 30).sum() if 'Recency' in df.columns else 'N/A'} customers
            """)
        
        with col5:
            st.info(f"""
            **Cross-Sell Opportunities:**
            - Same Category Interest: {df['in_cart_same_category'].mean():.1f} items avg
            - Cross-Category Interest: {df['in_cart_other_category'].mean():.1f} items avg
            - Bundle Potential: High
            """)


# ==================================================
# MAIN DASHBOARD
# ==================================================
def show_product_based_customer_insights():
    """Main function to display product-based customer insights"""
    
    # Custom CSS for full screen
    st.markdown("""
        <style>
        .main > div {
            padding-top: 2rem;
        }
        .stPlotlyChart {
            background-color: white;
            border-radius: 5px;
            padding: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("🎯 Product-Based Customer Prediction & Tracking Dashboard")
    st.markdown("### Track customers by product selection with comprehensive insights")
    st.divider()
    
    # Load all data
    with st.spinner("Loading datasets..."):
        (predictions, customer_category_features, customer_product_flat,
         customer_rfm, customer_with_purchases, products_catalog) = load_all_data()
    
    if predictions is None:
        st.error("Failed to load data. Please check file paths.")
        return
    
    # Preprocess prediction data
    predictions = preprocess_prediction_data(predictions)
    
    # Merge all customer data
    full_data = merge_customer_data(
        predictions,
        customer_with_purchases,
        customer_rfm,
        customer_category_features
    )
    
    st.success(f"✅ Loaded {len(full_data):,} customer predictions with complete profiles")
    st.divider()
    
    # Display inline filters
    filtered_data, selected_product, selected_category = display_inline_filters(full_data, products_catalog)
    
    # Filter summary
    display_filter_summary(len(full_data), len(filtered_data), selected_product, selected_category)
    
    # Check if data available after filtering
    if len(filtered_data) == 0:
        st.warning("⚠️ No customers found matching the selected filters. Please adjust your criteria.")
        return
    
    # Display only essential sections focused on customer details
    display_customer_insights_overview(filtered_data)
    display_customer_tracking_table(filtered_data)
    display_top_customers(filtered_data)
    display_actionable_insights(filtered_data, selected_product)
    
    # Optional: Add expandable sections for detailed analysis
    with st.expander("📊 View Additional Analytics", expanded=False):
        st.markdown("#### Customer Distribution Analysis")
        display_customer_distributions(filtered_data)
        
        st.markdown("#### Customer Segmentation")
        display_customer_segmentation(filtered_data)
        
        st.markdown("#### Purchase Behavior Patterns")
        display_purchase_behavior(filtered_data)
        
        if 'order_date' in customer_with_purchases.columns:
            st.markdown("#### Order Timeline")
            display_customer_journey(filtered_data, customer_with_purchases)
        
        st.markdown("#### Category Spending Analysis")
        display_category_spending_analysis(filtered_data)
    
    # Footer
    st.divider()
    st.markdown(f"""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Product-Based Customer Tracking Dashboard</strong></p>
        <p>Showing {len(filtered_data):,} customers | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)


# ==================================================
# RUN DASHBOARD
# ==================================================
if __name__ == "__main__":
    show_product_based_customer_insights()