import streamlit as st

def show_home_page():
    """Display the home page of the E-Commerce Analytics Dashboard"""
    
    # Hero Section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0;">Welcome to E-Commerce Analytics</h1>
        <p style="color: white; text-align: center; font-size: 1.2rem; margin-top: 0.5rem;">
            AI-Powered Customer Intelligence & Business Insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Features Section
    st.markdown("## 🚀 Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background-color: #f0f8ff; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #1f77b4;">
            <h3 style="color: #1f77b4;">📊 Data Visualizations</h3>
            <p>Explore comprehensive business analytics with interactive charts and insights:</p>
            <ul>
                <li>Sales trends & patterns</li>
                <li>Customer demographics</li>
                <li>Product performance</li>
                <li>Revenue analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #fff5f5; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #e74c3c;">
            <h3 style="color: #e74c3c;">🎯 Customer Predictions</h3>
            <p>AI-driven customer intelligence platform featuring:</p>
            <ul>
                <li>Next purchase predictions</li>
                <li>Product recommendations</li>
                <li>Customer segmentation</li>
                <li>Personalized offers</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background-color: #f0fff4; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #27ae60;">
            <h3 style="color: #27ae60;">📧 Smart Communication</h3>
            <p>Automated customer engagement tools:</p>
            <ul>
                <li>Email campaigns</li>
                <li>WhatsApp messaging</li>
                <li>Offer generation</li>
                <li>Personalized content</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Quick Stats Section
    st.markdown("## 📈 Dashboard Overview")
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric(
            label="📊 Analytics Tools",
            value="15+",
            help="Interactive visualization tools available"
        )
    
    with stat_col2:
        st.metric(
            label="🤖 AI Models",
            value="3",
            help="Machine learning models for predictions"
        )
    
    with stat_col3:
        st.metric(
            label="🎯 Accuracy",
            value="85%+",
            help="Average prediction accuracy"
        )
    
    with stat_col4:
        st.metric(
            label="⚡ Real-time",
            value="Yes",
            help="Real-time data processing"
        )
    
    st.divider()
    
    # How It Works Section
    st.markdown("## 🔄 How It Works")
    
    step_col1, step_col2, step_col3 = st.columns(3)
    
    with step_col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem;">📥</div>
            <h3>1. Data Collection</h3>
            <p>Import and process your customer data, purchase history, and product catalogs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step_col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem;">🧠</div>
            <h3>2. AI Analysis</h3>
            <p>Advanced algorithms analyze patterns, predict behaviors, and generate insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step_col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem;">🚀</div>
            <h3>3. Action & Results</h3>
            <p>Apply insights, send personalized offers, and track business growth</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Getting Started Section
    st.markdown("## 🎯 Getting Started")
    
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-top: 1rem;">
        <h3>Quick Start Guide:</h3>
        <ol style="font-size: 1.1rem; line-height: 1.8;">
            <li><strong>Navigate to Data Visualizations</strong> - Explore your business metrics with interactive charts</li>
            <li><strong>Apply Filters</strong> - Segment data by date, region, gender, and more</li>
            <li><strong>View Customer Predictions</strong> - Access AI-powered recommendations for each customer</li>
            <li><strong>Generate Offers</strong> - Create personalized promotional messages</li>
            <li><strong>Send Communications</strong> - Deliver offers via email or WhatsApp</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Call to Action
    st.markdown("## 🎊 Ready to Get Started?")
    
    cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])
    
    with cta_col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <p style="font-size: 1.2rem; margin-bottom: 1rem;">
                Use the navigation menu on the left to explore the dashboard features
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📊 View Analytics", use_container_width=True, type="primary"):
                st.session_state.page = "visualizations"
                st.session_state.show_filter_dialog = True
                st.rerun()
        
        with col_b:
            if st.button("🎯 Customer Predictions", use_container_width=True, type="primary"):
                st.session_state.page = "predictions"
                st.rerun()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 1rem;">
        <p>E-Commerce Business Analytics Dashboard | Powered by AI & Machine Learning</p>
    </div>
    """, unsafe_allow_html=True)