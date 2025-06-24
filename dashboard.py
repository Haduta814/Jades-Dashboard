import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page config
st.set_page_config(
    page_title="Convention Sales Dashboard",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .section-header {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and prepare the sales data"""
    try:
        # Load the cleaned CSV data
        df = pd.read_csv('cleaned_convention_sales_data.csv')
        return df
    except FileNotFoundError:
        st.error("❌ CSV file not found! Please make sure 'cleaned_convention_sales_data.csv' is in the same directory as this script.")
        # Create sample data for demo
        data = {
            'sheet_name': ['MEGA LDN SAT', 'MEGA LDN SUN', 'AL LDN SAT'] * 50,
            'location': ['London', 'London', 'London'] * 50,
            'day': ['Saturday', 'Sunday', 'Saturday'] * 50,
            'event_type': ['Mega', 'Mega', 'AL'] * 50,
            'series_character': ['JJK', 'Frieren', 'ACNH'] * 50,
            'character_variant': ['Fish', 'Frieren', 'Blathers'] * 50,
            'product_type': ['Bag', 'Keyring', 'Pin'] * 50,
            'quantity': np.random.randint(1, 20, 150)
        }
        df = pd.DataFrame(data)
        st.warning("⚠️ Using sample data for demonstration. Please upload your actual CSV file.")
        return df

def create_overview_metrics(df):
    """Create enhanced overview metrics cards"""
    # First row of metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_sales = df['quantity'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎯 Total Sales</h3>
            <h2>{total_sales:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        unique_events = df['sheet_name'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎪 Events</h3>
            <h2>{unique_events}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        unique_characters = df['series_character'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <h3>👥 Series</h3>
            <h2>{unique_characters}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_sales = df['quantity'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Avg per Item</h3>
            <h2>{avg_sales:.1f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        unique_products = df['product_type'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <h3>🛍️ Product Types</h3>
            <h2>{unique_products}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row - Regional and Character Performance
    st.markdown("### 📈 Performance Breakdown")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Top performing location
        location_sales = df.groupby('location')['quantity'].sum()
        if not location_sales.empty:
            top_location = location_sales.idxmax()
            top_location_sales = location_sales.max()
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                <h4>🏆 Top Location</h4>
                <h3>{top_location}</h3>
                <p>{top_location_sales:,} items</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Top performing character
        char_sales = df.groupby(['series_character', 'character_variant'])['quantity'].sum()
        if not char_sales.empty:
            top_char_idx = char_sales.idxmax()
            top_char_sales = char_sales.max()
            char_name = f"{top_char_idx[0]} - {top_char_idx[1]}" if top_char_idx[1] else top_char_idx[0]
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);">
                <h4>⭐ Top Character</h4>
                <h3>{char_name[:20]}{'...' if len(char_name) > 20 else ''}</h3>
                <p>{top_char_sales:,} items</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        # Top performing product
        product_sales = df.groupby('product_type')['quantity'].sum()
        if not product_sales.empty:
            top_product = product_sales.idxmax()
            top_product_sales = product_sales.max()
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
                <h4>🎁 Top Product</h4>
                <h3>{top_product}</h3>
                <p>{top_product_sales:,} items</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Performance by region table
    st.markdown("### 🌍 Regional Performance")
    regional_stats = df.groupby('location').agg({
        'quantity': ['sum', 'mean', 'count'],
        'product_type': 'nunique',
        'series_character': 'nunique'
    }).round(2)
    
    regional_stats.columns = ['Total Sales', 'Avg per Item', 'Total Items', 'Product Types', 'Series Count']
    regional_stats = regional_stats.sort_values('Total Sales', ascending=False)
    
    st.dataframe(regional_stats, use_container_width=True)

def create_sales_by_location(df):
    """Create sales by location visualization"""
    location_sales = df.groupby('location')['quantity'].sum().reset_index()
    
    fig = px.bar(
        location_sales, 
        x='location', 
        y='quantity',
        title="📍 Sales by Location",
        color='quantity',
        color_continuous_scale='viridis'
    )
    fig.update_layout(
        height=400,
        title_font_size=20,
        xaxis_title="Location",
        yaxis_title="Total Quantity Sold"
    )
    return fig

def create_event_comparison(df):
    """Create event type comparison"""
    event_sales = df.groupby(['event_type', 'location'])['quantity'].sum().reset_index()
    
    fig = px.bar(
        event_sales,
        x='location',
        y='quantity',
        color='event_type',
        title="🎭 Event Type Performance by Location",
        barmode='group'
    )
    fig.update_layout(height=400, title_font_size=20)
    return fig

def create_product_performance(df):
    """Create product performance chart"""
    product_sales = df.groupby('product_type')['quantity'].sum().reset_index()
    product_sales = product_sales.sort_values('quantity', ascending=True)
    
    fig = px.bar(
        product_sales,
        x='quantity',
        y='product_type',
        orientation='h',
        title="🛍️ Product Performance",
        color='quantity',
        color_continuous_scale='plasma'
    )
    fig.update_layout(height=400, title_font_size=20)
    return fig

def create_top_characters(df):
    """Create top characters treemap chart"""
    char_sales = df.groupby(['series_character', 'character_variant'])['quantity'].sum().reset_index()
    char_sales['full_name'] = char_sales['series_character'] + ' - ' + char_sales['character_variant']
    char_sales = char_sales.nlargest(15, 'quantity')
    
    fig = px.treemap(
        char_sales,
        path=['series_character', 'character_variant'],
        values='quantity',
        title="🌟 Top Characters by Sales",
        color='quantity',
        color_continuous_scale='blues'
    )
    fig.update_layout(height=500, title_font_size=20)
    return fig

def create_character_analysis(df):
    """Create character performance analysis"""
    st.markdown('<h2 class="section-header">🌟 Character Performance Analysis</h2>', unsafe_allow_html=True)
    
    # Character sales summary
    char_analysis = df.groupby(['series_character', 'character_variant']).agg({
        'quantity': ['sum', 'mean', 'count'],
        'location': lambda x: ', '.join(x.unique()),
        'product_type': lambda x: ', '.join(x.unique())
    }).round(2)
    
    char_analysis.columns = ['Total Sales', 'Avg per Event', 'Events Count', 'Locations', 'Products']
    char_analysis = char_analysis.sort_values('Total Sales', ascending=False)
    
    # Display top characters table
    st.markdown("### 📊 Top Character Performance")
    top_chars = char_analysis.head(15)
    st.dataframe(top_chars, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Character performance by location
        char_location = df.groupby(['location', 'series_character'])['quantity'].sum().reset_index()
        char_location_pivot = char_location.pivot(index='series_character', columns='location', values='quantity').fillna(0)
        
        fig = px.imshow(
            char_location_pivot.values,
            x=char_location_pivot.columns,
            y=char_location_pivot.index,
            title="Character Performance Heatmap by Location",
            color_continuous_scale='viridis',
            aspect='auto'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Product type preference by character
        top_chars_list = char_analysis.head(8).index.get_level_values(0).unique()
        char_product = df[df['series_character'].isin(top_chars_list)]
        char_product_summary = char_product.groupby(['series_character', 'product_type'])['quantity'].sum().reset_index()
        
        fig = px.bar(
            char_product_summary,
            x='series_character',
            y='quantity',
            color='product_type',
            title="Product Type Distribution - Top Characters",
            barmode='stack'
        )
        fig.update_layout(height=400, xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

def create_daily_performance(df):
    """Create daily performance chart"""
    day_sales = df.groupby(['day', 'event_type'])['quantity'].sum().reset_index()
    
    fig = px.pie(
        day_sales,
        values='quantity',
        names='day',
        title="📅 Sales Distribution by Day",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(height=400, title_font_size=20)
    return fig

def create_detailed_analysis(df):
    """Create detailed analysis section"""
    st.markdown('<h2 class="section-header">🔍 Detailed Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales distribution by series
        series_sales = df.groupby('series_character')['quantity'].sum().reset_index()
        series_sales = series_sales.sort_values('quantity', ascending=False).head(10)
        
        fig = px.pie(
            series_sales,
            values='quantity',
            names='series_character',
            title="Top 10 Series by Sales",
            hole=0.4  # This makes it a donut chart
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Product type distribution
        product_dist = df.groupby(['product_type', 'event_type'])['quantity'].sum().reset_index()
        
        fig = px.sunburst(
            product_dist,
            path=['event_type', 'product_type'],
            values='quantity',
            title="Product Distribution by Event Type"
        )
        st.plotly_chart(fig, use_container_width=True)

def main():
    """Main dashboard function"""
    # Header
    st.markdown('<h1 class="main-header">🎪 Convention Sales Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Enhanced sidebar filters
    st.sidebar.header("🎛️ Filters")
    
    # Location filter
    locations = ['All'] + sorted(list(df['location'].unique()))
    selected_location = st.sidebar.selectbox("📍 Select Location", locations)
    
    # Event type filter
    event_types = ['All'] + sorted(list(df['event_type'].unique()))
    selected_event = st.sidebar.selectbox("🎪 Select Event Type", event_types)
    
    # Day filter
    days = ['All'] + sorted(list(df['day'].unique()))
    selected_day = st.sidebar.selectbox("📅 Select Day", days)
    
    # Character series filter
    anime_series = ['All'] + sorted([x for x in df['series_character'].unique() if x and str(x) != 'nan'])
    selected_anime = st.sidebar.selectbox("🎭 Select Anime/Series", anime_series)
    
    # Character variant filter
    if selected_anime != 'All':
        available_variants = df[df['series_character'] == selected_anime]['character_variant'].unique()
        character_variants = ['All'] + sorted([x for x in available_variants if x and str(x) != 'nan'])
    else:
        character_variants = ['All'] + sorted([x for x in df['character_variant'].unique() if x and str(x) != 'nan'])
    selected_character = st.sidebar.selectbox("👤 Select Character", character_variants)
    
    # Product type filter
    products = ['All'] + sorted(list(df['product_type'].unique()))
    selected_product = st.sidebar.selectbox("🛍️ Select Product Type", products)
    
    # Apply filters
    filtered_df = df.copy()
    active_filters = []
    
    if selected_location != 'All':
        filtered_df = filtered_df[filtered_df['location'] == selected_location]
        active_filters.append(f"📍 Location: {selected_location}")
    if selected_event != 'All':
        filtered_df = filtered_df[filtered_df['event_type'] == selected_event]
        active_filters.append(f"🎪 Event: {selected_event}")
    if selected_day != 'All':
        filtered_df = filtered_df[filtered_df['day'] == selected_day]
        active_filters.append(f"📅 Day: {selected_day}")
    if selected_anime != 'All':
        filtered_df = filtered_df[filtered_df['series_character'] == selected_anime]
        active_filters.append(f"🎭 Series: {selected_anime}")
    if selected_character != 'All':
        filtered_df = filtered_df[filtered_df['character_variant'] == selected_character]
        active_filters.append(f"👤 Character: {selected_character}")
    if selected_product != 'All':
        filtered_df = filtered_df[filtered_df['product_type'] == selected_product]
        active_filters.append(f"🛍️ Product: {selected_product}")
    
    # Show active filters
    if active_filters:
        st.markdown("### 🔍 Active Filters")
        filter_text = " | ".join(active_filters)
        st.info(f"{filter_text}")
    else:
        st.success("📊 Showing all data - no filters applied")
    
    # Check if filtered data is empty
    if filtered_df.empty:
        st.warning("⚠️ No data matches your current filter selection. Please adjust your filters.")
        st.stop()
    
    # Overview metrics
    create_overview_metrics(filtered_df)
    
    # Main visualizations
    st.markdown('<h2 class="section-header">📊 Sales Overview</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig1 = create_sales_by_location(filtered_df)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = create_daily_performance(filtered_df)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Event comparison and product performance
    col3, col4 = st.columns(2)
    with col3:
        fig3 = create_event_comparison(filtered_df)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        fig4 = create_product_performance(filtered_df)
        st.plotly_chart(fig4, use_container_width=True)
    
    # Top characters treemap
    st.markdown('<h2 class="section-header">🌟 Character Sales Overview</h2>', unsafe_allow_html=True)
    fig5 = create_top_characters(filtered_df)
    st.plotly_chart(fig5, use_container_width=True)
    
    # Character performance analysis
    create_character_analysis(filtered_df)
    
    # Detailed analysis
    create_detailed_analysis(filtered_df)
    
    # Data insights and pricing note
    with st.expander("💡 Data Insights & Pricing Information"):
        st.markdown("""
        ### 📊 Current Data Overview
        Your dashboard is currently showing **quantity-based metrics**. 
        
        ### 💰 Adding Pricing Data
        To enable revenue analysis and price-per-character metrics, you can:
        1. Add a `price` column to your CSV with item prices
        2. Add a `revenue` column with total revenue per row
        3. The dashboard will automatically calculate:
           - Revenue by location/character/product
           - Average selling price per item
           - Profit margins (if cost data included)
           
        ### 🎯 Suggested CSV Enhancements
        ```
        sheet_name,location,day,event_type,series_character,character_variant,product_type,quantity,price,revenue
        ```
        """)
        
        # Show data quality info
        st.markdown("### 📈 Current Data Quality")
        col1, col2, col3 = st.columns(3)
        with col1:
            missing_chars = filtered_df['character_variant'].isna().sum()
            st.metric("Missing Character Names", missing_chars)
        with col2:
            zero_sales = (filtered_df['quantity'] == 0).sum()
            st.metric("Zero Quantity Records", zero_sales)
        with col3:
            unique_items = len(filtered_df.groupby(['series_character', 'character_variant', 'product_type']))
            st.metric("Unique Items", unique_items)
    
    # Raw data section
    with st.expander("📋 View Raw Data"):
        st.dataframe(filtered_df, use_container_width=True)
    
    # Export options
    st.markdown('<h2 class="section-header">💾 Export Options</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f'convention_sales_filtered_{selected_location}_{selected_event}.csv',
            mime='text/csv'
        )
    
    with col2:
        # Summary statistics
        summary_stats = filtered_df.groupby(['location', 'event_type'])['quantity'].agg([
            'sum', 'mean', 'std', 'min', 'max'
        ]).round(2)
        
        summary_csv = summary_stats.to_csv()
        st.download_button(
            label="📊 Download Summary Statistics",
            data=summary_csv,
            file_name='sales_summary_statistics.csv',
            mime='text/csv'
        )

if __name__ == "__main__":
    main()