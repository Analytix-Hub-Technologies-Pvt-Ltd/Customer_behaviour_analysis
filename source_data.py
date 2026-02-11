import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def show_all_visualizations(data, product_flat, category_features, rfm_data, products_catalog):
    """Display all visualizations in a single view"""
    
    # Overview Section
    st.header("📈 Business Overview")
    show_overview(data, products_catalog)
    st.markdown("---")
    
    # Customer Analysis Section
    st.header("👥 Customer Analysis")
    show_customer_analysis(data, category_features)
    st.markdown("---")
    
    # Product Analysis Section
    st.header("🛍️ Product Analysis")
    show_product_analysis(data, products_catalog, product_flat)
    st.markdown("---")
    
    # RFM Segmentation Section
    st.header("📊 RFM Segmentation Analysis")
    show_rfm_analysis(rfm_data)
    st.markdown("---")
    
    # Geographic Analysis Section
    st.header("🗺️ Geographic Analysis")
    show_geographic_analysis(data)
    st.markdown("---")
    
    # Time Series Analysis Section
    st.header("📅 Time Series Analysis")
    show_time_series_analysis(data)

def show_overview(data, products_catalog):
    """Display overview metrics and KPIs"""
    
    # Key Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_customers = data['customer_id'].nunique()
        st.metric("Total Customers", f"{total_customers:,}")
    
    with col2:
        total_revenue = data['total_spent'].sum()
        st.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    
    with col3:
        total_orders = len(data)
        st.metric("Total Orders", f"{total_orders:,}")
    
    with col4:
        avg_order_value = data['total_spent'].mean()
        st.metric("Avg Order Value", f"₹{avg_order_value:,.0f}")
    
    with col5:
        if not products_catalog.empty:
            total_products = len(products_catalog)
            st.metric("Total Products", f"{total_products:,}")
        else:
            st.metric("Total Products", "N/A")
    
    st.markdown("###")
    
    # Two column layout for charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue trend over time
        if 'order_date' in data.columns:
            st.subheader("Revenue Trend")
            daily_revenue = data.groupby(data['order_date'].dt.date)['total_spent'].sum().reset_index()
            daily_revenue.columns = ['Date', 'Revenue']
            fig = px.line(daily_revenue, x='Date', y='Revenue', 
                         title='Daily Revenue Trend',
                         labels={'Revenue': 'Revenue (₹)'})
            fig.update_traces(line_color='#1f77b4', line_width=2)
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
        
        # Payment mode distribution
        if 'mode_of_payment' in data.columns:
            st.subheader("Payment Methods Distribution")
            payment_dist = data['mode_of_payment'].value_counts()
            fig = px.pie(values=payment_dist.values, names=payment_dist.index,
                        title='Payment Method Split',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top spending customers
        st.subheader("Top 10 Customers by Revenue")
        top_customers = data.groupby('customer_id')['total_spent'].sum().nlargest(10).reset_index()
        top_customers.columns = ['Customer ID', 'Total Spent']
        fig = px.bar(top_customers, x='Customer ID', y='Total Spent',
                    title='Top 10 Customers',
                    labels={'Total Spent': 'Total Spent (₹)'},
                    color='Total Spent',
                    color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
        
        # Gender distribution
        if 'gender' in data.columns:
            st.subheader("Customer Gender Distribution")
            gender_dist = data.groupby('gender')['customer_id'].nunique()
            fig = px.bar(x=gender_dist.index, y=gender_dist.values,
                        title='Customers by Gender',
                        labels={'x': 'Gender', 'y': 'Number of Customers'},
                        color=gender_dist.values,
                        color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)

def show_customer_analysis(data, category_features):
    """Display customer segmentation and behavior analysis"""
    
    # Category spending analysis
    if not category_features.empty:
        st.subheader("Category Spending Patterns")
        
        # Get spending columns
        spend_cols = [col for col in category_features.columns if col.endswith('_spend')]
        
        if spend_cols:
            # Average spending by category
            avg_spending = category_features[spend_cols].mean().sort_values(ascending=False)
            avg_spending.index = [col.replace('_spend', '').replace('_', ' ').title() for col in avg_spending.index]
            
            fig = px.bar(x=avg_spending.index, y=avg_spending.values,
                        title='Average Customer Spending by Category',
                        labels={'x': 'Category', 'y': 'Average Spending (₹)'},
                        color=avg_spending.values,
                        color_continuous_scale='Sunset')
            fig.update_layout(xaxis_tickangle=-45, height=500)
            st.plotly_chart(fig, use_container_width=True)

def show_product_analysis(data, products_catalog, product_flat):
    """Display product performance and catalog analysis"""
    
    # Category-wise revenue
    if not products_catalog.empty:
        st.subheader("Revenue by Category")
        category_revenue = products_catalog.groupby('category')['price_inr'].sum().sort_values(ascending=False).head(15)
        fig = px.bar(x=category_revenue.index, y=category_revenue.values,
                    title='Top 15 Categories by Total Product Value',
                    labels={'x': 'Category', 'y': 'Total Value (₹)'},
                    color=category_revenue.values,
                    color_continuous_scale='Teal')
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 1: Product Performance Metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Average product price by category
        if not products_catalog.empty:
            st.subheader("Average Product Price by Category")
            avg_price = products_catalog.groupby('category')['price_inr'].mean().sort_values(ascending=False).head(15)
            fig = px.bar(x=avg_price.index, y=avg_price.values,
                        title='Top 15 Categories by Average Price',
                        labels={'x': 'Category', 'y': 'Average Price (₹)'},
                        color=avg_price.values,
                        color_continuous_scale='Oranges')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Product diversity by category
        if not products_catalog.empty:
            st.subheader("Product Variety by Category")
            product_count = products_catalog.groupby('category')['product'].count().sort_values(ascending=False).head(15)
            fig = px.bar(x=product_count.index, y=product_count.values,
                        title='Top 15 Categories by Product Count',
                        labels={'x': 'Category', 'y': 'Number of Products'},
                        color=product_count.values,
                        color_continuous_scale='Purples')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: Customer Purchase Patterns
    col1, col2 = st.columns(2)
    
    with col1:
        # Order size distribution (items per order)
        if not product_flat.empty:
            st.subheader("Order Size Distribution")
            items_per_order = product_flat.groupby('customer_id').size()
            fig = px.histogram(x=items_per_order.values, nbins=20,
                              title='Number of Items per Order',
                              labels={'x': 'Items per Order', 'y': 'Frequency'},
                              color_discrete_sequence=['#16a085'])
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Product repurchase rate
        if not product_flat.empty:
            st.subheader("Top Products by Repurchase Rate")
            # Get products purchased by multiple customers
            product_purchase_count = product_flat.groupby('product')['customer_id'].nunique()
            product_total_purchases = product_flat['product'].value_counts()
            
            repurchase_rate = (product_total_purchases / product_purchase_count).sort_values(ascending=False).head(15)
            
            fig = px.bar(x=repurchase_rate.index, y=repurchase_rate.values,
                        title='Top 15 Products by Average Purchases per Customer',
                        labels={'x': 'Product', 'y': 'Avg Purchases per Customer'},
                        color=repurchase_rate.values,
                        color_continuous_scale='Reds')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Most popular products - WordCloud
    if not product_flat.empty:
        st.subheader("Most Popular Products - Word Cloud")
        
        try:
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
            
            # Get product frequency
            product_text = ' '.join(product_flat['product'].tolist())
            
            # Generate word cloud
            wordcloud = WordCloud(width=1200, height=600, 
                                background_color='white',
                                colormap='viridis',
                                relative_scaling=0.5,
                                min_font_size=10).generate(product_text)
            
            # Display using matplotlib
            fig, ax = plt.subplots(figsize=(15, 8))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            plt.tight_layout(pad=0)
            st.pyplot(fig)
            plt.close()
            
        except ImportError:
            st.warning("WordCloud library not installed. Showing bar chart instead.")
            # Fallback to bar chart
            product_popularity = product_flat['product'].value_counts().head(20)
            fig = px.bar(x=product_popularity.values, y=product_popularity.index,
                        orientation='h',
                        title='Top 20 Most Popular Products',
                        labels={'x': 'Purchase Count', 'y': 'Product'},
                        color=product_popularity.values,
                        color_continuous_scale='Purp')
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)

def show_rfm_analysis(rfm_data):
    """Display RFM segmentation analysis"""
    
    if rfm_data.empty:
        st.warning("RFM data not available")
        return
    
    # Create RFM scores
    rfm_data_copy = rfm_data.copy()
    rfm_data_copy['R_Score'] = pd.qcut(rfm_data_copy['Recency'], 4, labels=[4, 3, 2, 1])
    rfm_data_copy['F_Score'] = pd.qcut(rfm_data_copy['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
    rfm_data_copy['M_Score'] = pd.qcut(rfm_data_copy['Monetary'], 4, labels=[1, 2, 3, 4])
    
    rfm_data_copy['RFM_Score'] = (rfm_data_copy['R_Score'].astype(int) + 
                                   rfm_data_copy['F_Score'].astype(int) + 
                                   rfm_data_copy['M_Score'].astype(int))
    
    # Segment customers
    def segment_customer(score):
        if score >= 10:
            return 'Champions'
        elif score >= 8:
            return 'Loyal Customers'
        elif score >= 6:
            return 'Potential Loyalists'
        elif score >= 5:
            return 'At Risk'
        else:
            return 'Lost'
    
    rfm_data_copy['Segment'] = rfm_data_copy['RFM_Score'].apply(segment_customer)
    
    # 3D RFM scatter plot
    st.subheader("RFM 3D Visualization")
    fig = px.scatter_3d(rfm_data_copy, x='Recency', y='Frequency', z='Monetary',
                       color='Segment',
                       title='3D RFM Customer Segmentation',
                       labels={'Recency': 'Recency (days)', 
                              'Frequency': 'Frequency', 
                              'Monetary': 'Monetary (₹)'},
                       color_discrete_sequence=px.colors.qualitative.Bold,
                       height=700)
    fig.update_traces(marker=dict(size=5))
    st.plotly_chart(fig, use_container_width=True)

def show_geographic_analysis(data):
    """Display geographic distribution and insights"""
    
    if 'region' not in data.columns and 'state' not in data.columns:
        st.warning("Geographic data not available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by region
        if 'region' in data.columns:
            st.subheader("Revenue by Region")
            region_revenue = data.groupby('region')['total_spent'].sum().sort_values(ascending=False)
            fig = px.bar(x=region_revenue.index, y=region_revenue.values,
                        title='Total Revenue by Region',
                        labels={'x': 'Region', 'y': 'Revenue (₹)'},
                        color=region_revenue.values,
                        color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top cities
        if 'city_name' in data.columns:
            st.subheader("Top 20 Cities by Revenue")
            city_revenue = data.groupby('city_name')['total_spent'].sum().nlargest(20)
            fig = px.bar(x=city_revenue.values, y=city_revenue.index,
                        orientation='h',
                        title='Top 20 Cities',
                        labels={'x': 'Revenue (₹)', 'y': 'City'},
                        color=city_revenue.values,
                        color_continuous_scale='Teal')
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)

def show_time_series_analysis(data):
    """Display time-based trends and patterns"""
    
    if 'order_date' not in data.columns:
        st.warning("Date information not available")
        return
    
    # Daily data aggregation
    daily_data = data.groupby(data['order_date'].dt.date).agg({
        'total_spent': 'sum',
        'transaction_id': 'count'
    }).reset_index()
    daily_data.columns = ['Date', 'Revenue', 'Orders']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Daily Orders Trend")
        fig = px.line(daily_data, x='Date', y='Orders',
                     title='Daily Order Count',
                     labels={'Orders': 'Number of Orders'})
        fig.update_traces(line_color='#2ecc71', line_width=2)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Monthly trend
        st.subheader("Monthly Revenue Trend")
        data['year_month'] = data['order_date'].dt.to_period('M').astype(str)
        monthly_revenue = data.groupby('year_month')['total_spent'].sum().reset_index()
        monthly_revenue.columns = ['Month', 'Revenue']
        fig = px.bar(monthly_revenue, x='Month', y='Revenue',
                    title='Monthly Revenue',
                    labels={'Revenue': 'Revenue (₹)'},
                    color='Revenue',
                    color_continuous_scale='Sunset')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Hour of day analysis (if time data available)
        if data['order_date'].dt.hour.nunique() > 1:
            st.subheader("Orders by Hour of Day")
            data['hour'] = data['order_date'].dt.hour
            hourly_orders = data.groupby('hour').size().reset_index(name='Orders')
            fig = px.line(hourly_orders, x='hour', y='Orders',
                         title='Order Distribution by Hour',
                         labels={'hour': 'Hour of Day', 'Orders': 'Number of Orders'},
                         markers=True)
            fig.update_traces(line_color='#9b59b6', line_width=2)
            st.plotly_chart(fig, use_container_width=True)
    
    # Revenue vs Orders Dual Axis Chart
    st.subheader("Revenue vs Orders Correlation")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(name='Revenue', x=daily_data['Date'], y=daily_data['Revenue'],
                  mode='lines', line=dict(color='#3498db', width=2)),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(name='Orders', x=daily_data['Date'], y=daily_data['Orders'],
                  mode='lines', line=dict(color='#e74c3c', width=2)),
        secondary_y=True
    )
    
    fig.update_layout(
        title_text='Daily Revenue vs Order Volume',
        xaxis_title='Date',
        height=450
    )
    fig.update_yaxes(title_text='Revenue (₹)', secondary_y=False)
    fig.update_yaxes(title_text='Number of Orders', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)