# dashboard.py
# by: Culanggo, Kein Jake A.

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import re
import os

# 1. Render PostgreSQL connection (using environment variable for security)
RENDER_DB_URL = os.getenv('RENDER_DB_URL', "postgresql://whiplash_user:6EoohkmGo5ziA3qJMhsBYHl5P6yS9UKL@dpg-d0amg66uk2gs73busq9g-a.oregon-postgres.render.com/whiplash")

# 2. FUNCTION TO FETCH YOUR CLEANED DATA (with error handling)
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cleaned_data():
    try:
        engine = create_engine(RENDER_DB_URL)
        with engine.connect() as conn:
            query = text('SELECT * FROM "data_ETL"')
            df = pd.read_sql(query, conn)
            
            # Datetime conversions
            df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%y %H:%M', errors='coerce') 
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            # Drop rows with invalid dates
            df = df.dropna(subset=['Date', 'Order Date'])
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()  # Return empty dataframe on error

# Helper function to standardize source values
def clean_source(source):
    if isinstance(source, str):
        source_lower = source.lower()
        if 'usa' in source_lower or 'united states' in source_lower or 'us' in source_lower:
            return 'USA'
        elif 'canada' in source_lower or 'ca' in source_lower:
            return 'Canada'
    return source

# Main dashboard function
def main():
    # Set page config (important for Render deployment)
    st.set_page_config(
        layout="wide",
        page_title="USA vs Canada Sales Dashboard",
        page_icon="🦅"
    )
    
    # Custom CSS with improved mobile responsiveness
    st.markdown("""
    <style>
    /* Main app styling */
    .main {
        background-color: #121212;
        color: white;
    }
    .stApp {
        background-color: #121212;
        background-size: cover;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Sidebar styling */
    .stSidebar {
        background-color: #1e1e1e;
        border-right: 1px solid #333;
    }
    
    /* Metric cards */
    .stMetric {
        background-color: #1e1e1e !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
        transition: transform 0.2s;
    }
    .stMetric:hover {
        transform: translateY(-5px);
    }
    .stMetric > div {
        color: white !important;
    }
    .stMetric label {
        color: #3A6B35 !important;
        font-weight: bold !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: #1e1e1e !important;
    }
    
    /* Footer styling */
    .footer {
        position: fixed;
        bottom: 0;
        right: 10px;
        color: #666;
        font-size: 12px;
        padding: 5px;
        z-index: 999;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .stMetric {
            padding: 10px !important;
            margin-bottom: 10px;
        }
        .css-1v0mbdj {
            margin-bottom: 1rem;
        }
    }
    </style>
    <div class="footer">by: Culanggo, Kein Jake A.</div>
    """, unsafe_allow_html=True)
    
    # Title with improved layout
    st.markdown("""
    <div style='display: flex; align-items: center; margin-bottom: 20px;'>
        <h1 style='margin: 0;'>🦅 USA vs 🍁 Canada Sales Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data with loading indicator
    with st.spinner('Loading data...'):
        sales_data = get_cleaned_data()
    
    # Check if data loaded successfully
    if sales_data.empty:
        st.error("No data loaded. Please check your database connection.")
        return
    
    # Data processing
    sales_data['source'] = sales_data['source'].apply(clean_source)
    valid_sources = ['USA', 'Canada']
    filtered_data = sales_data[sales_data['source'].isin(valid_sources)].copy()
    
    # Add month and year columns for time analysis
    filtered_data['Month'] = filtered_data['Date'].dt.to_period('M').astype(str)
    filtered_data['Year'] = filtered_data['Date'].dt.year
    
    # Sidebar with filters
    with st.sidebar:
        st.header("Filters")
        year_filter = st.multiselect(
            "Select Years",
            options=sorted(filtered_data['Year'].unique()),
            default=sorted(filtered_data['Year'].unique())
        )
        
        st.markdown("---")
        st.header("Data Overview")
        st.write(f"Total Records: {len(filtered_data):,}")
        st.write(f"Date Range: {filtered_data['Date'].min().strftime('%b %d, %Y')} to {filtered_data['Date'].max().strftime('%b %d, %Y')}")
    
    # Apply year filter if any years selected
    if year_filter:
        filtered_data = filtered_data[filtered_data['Year'].isin(year_filter)]
    
    # Calculate metrics
    total_sales = filtered_data['Price in Dollar'].sum()
    avg_order = filtered_data['Price in Dollar'].mean()
    usa_count = len(filtered_data[filtered_data['source'] == 'USA'])
    canada_count = len(filtered_data[filtered_data['source'] == 'Canada'])
    
    # Display metrics in responsive columns
    metric_cols = st.columns(4)
    metric_style = """
    <div style="background-color:#1e1e1e; border-radius:12px; padding:15px; text-align:center; 
                box-shadow:0 4px 8px rgba(0,0,0,0.2); margin-bottom:20px; height:100%;">
        <h3 style="margin:0; color:#3A6B35; font-size:14px;">{title}</h3>
        <p style="margin:0; color:{color}; font-size:24px; font-weight:bold;">{value}</p>
    </div>
    """
    
    with metric_cols[0]:
        st.markdown(metric_style.format(
            title="Total Sales",
            color="#E3B448",
            value=f"${total_sales:,.2f}"
        ), unsafe_allow_html=True)
    
    with metric_cols[1]:
        st.markdown(metric_style.format(
            title="Avg. Order Value",
            color="#E3B448",
            value=f"${avg_order:,.2f}"
        ), unsafe_allow_html=True)
    
    with metric_cols[2]:
        st.markdown(metric_style.format(
            title="USA Orders",
            color="#E3B448",
            value=f"{usa_count:,}"
        ), unsafe_allow_html=True)
    
    with metric_cols[3]:
        st.markdown(metric_style.format(
            title="Canada Orders",
            color="#DC3912",
            value=f"{canada_count:,}"
        ), unsafe_allow_html=True)
    
    # Main content sections
    st.markdown("<hr style='border: 1px solid #333; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Section 1: Market Distribution
    st.markdown("<h2 style='color: white; margin-bottom: 20px;'>📊 Market Distribution</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Sales distribution pie chart
        country_sales = filtered_data.groupby('source')['Price in Dollar'].sum().reset_index()
        fig_pie = px.pie(
            country_sales, 
            names='source', 
            values='Price in Dollar',
            title='Sales Distribution by Country',
            color='source',
            color_discrete_map={'USA': '#E3B448', 'Canada': '#DC3912'},
            hole=0.5,
            template='plotly_dark'
        )
        fig_pie.update_traces(
            textinfo='percent+label+value',
            texttemplate='%{label}<br>%{percent} (%{value:$,.0f})',
            pull=[0.05, 0],
            textfont=dict(color='white', size=14),
            marker=dict(line=dict(color='#121212', width=2))
        fig_pie.update_layout(
            legend_title="Country",
            margin=dict(l=10, r=10, t=40, b=10),
            title_x=0.5,
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Quantity ordered by country
        quantity_by_country = filtered_data.groupby('source')['Quantity Ordered'].sum().reset_index()
        fig_quantity = px.bar(
            quantity_by_country, 
            x='source', 
            y='Quantity Ordered',
            title='Total Quantity Ordered',
            color='source',
            color_discrete_map={'USA': '#E3B448', 'Canada': '#DC3912'},
            text='Quantity Ordered',
            template='plotly_dark'
        )
        fig_quantity.update_traces(
            texttemplate='%{y:,}',
            textposition='outside',
            marker=dict(line=dict(color='#121212', width=1))
        )
        fig_quantity.update_layout(
            xaxis_title="Country", 
            yaxis_title="Total Quantity Ordered",
            margin=dict(l=10, r=10, t=40, b=10),
            title_x=0.5,
            height=400,
            showlegend=False
        )
        fig_quantity.update_xaxes(showgrid=False)
        fig_quantity.update_yaxes(showgrid=True, gridcolor='#333')
        st.plotly_chart(fig_quantity, use_container_width=True)
    
    # Section 2: Product Analysis
    st.markdown("<hr style='border: 1px solid #333; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: white; margin-bottom: 20px;'>📦 Product Analysis</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top products by country
        top_products = filtered_data.groupby(['source', 'Product'])['Quantity Ordered'].sum().reset_index()
        top_products['Product'] = top_products['Product'].apply(lambda x: x[:20] + '...' if len(x) > 20 else x)
        
        usa_top = top_products[top_products['source'] == 'USA'].nlargest(5, 'Quantity Ordered')
        canada_top = top_products[top_products['source'] == 'Canada'].nlargest(5, 'Quantity Ordered')
        
        fig_top_products = make_subplots(
            rows=1, 
            cols=2, 
            subplot_titles=("Top 5 USA Products", "Top 5 Canada Products"),
            shared_yaxes=True
        )
        
        fig_top_products.add_trace(
            go.Bar(
                x=usa_top['Quantity Ordered'],
                y=usa_top['Product'],
                orientation='h',
                marker_color='#E3B448',
                name='USA',
                text=usa_top['Quantity Ordered'],
                texttemplate='%{x:,}',
                textposition='inside',
                textfont=dict(color='black')
            ),
            row=1, col=1
        )
        
        fig_top_products.add_trace(
            go.Bar(
                x=canada_top['Quantity Ordered'],
                y=canada_top['Product'],
                orientation='h',
                marker_color='#DC3912',
                name='Canada',
                text=canada_top['Quantity Ordered'],
                texttemplate='%{x:,}',
                textposition='inside',
                textfont=dict(color='white')
            ),
            row=1, col=2
        )
        
        fig_top_products.update_layout(
            title_text="Top 5 Most Purchased Products by Country",
            height=500,
            template='plotly_dark',
            margin=dict(l=10, r=10, t=80, b=10),
            showlegend=False
        )
        fig_top_products.update_xaxes(showgrid=True, gridcolor='#333')
        st.plotly_chart(fig_top_products, use_container_width=True)
    
    with col2:
        # Most expensive products
        avg_price_by_product = filtered_data.groupby(['source', 'Product'])['Price Each'].mean().reset_index()
        avg_price_by_product['Product'] = avg_price_by_product['Product'].apply(lambda x: x[:20] + '...' if len(x) > 20 else x)
        
        usa_expensive = avg_price_by_product[avg_price_by_product['source'] == 'USA'].nlargest(3, 'Price Each')
        canada_expensive = avg_price_by_product[avg_price_by_product['source'] == 'Canada'].nlargest(3, 'Price Each')
        
        fig_expensive = make_subplots(
            rows=1, 
            cols=2, 
            subplot_titles=("Most Expensive USA Products", "Most Expensive Canada Products")
        )
        
        fig_expensive.add_trace(
            go.Bar(
                x=usa_expensive['Product'],
                y=usa_expensive['Price Each'],
                marker_color='#E3B448',
                name='USA',
                text=usa_expensive['Price Each'].apply(lambda x: f"${x:,.2f}"),
                textposition='outside',
                textfont=dict(color='white')
            ),
            row=1, col=1
        )
        
        fig_expensive.add_trace(
            go.Bar(
                x=canada_expensive['Product'],
                y=canada_expensive['Price Each'],
                marker_color='#DC3912',
                name='Canada',
                text=canada_expensive['Price Each'].apply(lambda x: f"${x:,.2f}"),
                textposition='outside',
                textfont=dict(color='white')
            ),
            row=1, col=2
        )
        
        fig_expensive.update_layout(
            title_text="Top 3 Most Expensive Products by Country",
            height=500,
            template='plotly_dark',
            margin=dict(l=10, r=10, t=80, b=10),
            showlegend=False,
            yaxis=dict(title='Price ($)'),
            yaxis2=dict(title='Price ($)')
        )
        fig_expensive.update_xaxes(tickangle=45)
        st.plotly_chart(fig_expensive, use_container_width=True)
    
    # Section 3: Time Analysis
    st.markdown("<hr style='border: 1px solid #333; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: white; margin-bottom: 20px;'>📈 Time Analysis</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly sales trend
        monthly_sales = filtered_data.groupby(['Month', 'source'])['Price in Dollar'].sum().reset_index()
        monthly_sales['Month'] = pd.to_datetime(monthly_sales['Month'])
        
        fig_time = px.line(
            monthly_sales, 
            x='Month', 
            y='Price in Dollar', 
            color='source',
            title='Monthly Sales Trend',
            color_discrete_map={'USA': '#E3B448', 'Canada': '#DC3912'},
            template='plotly_dark',
            labels={'Price in Dollar': 'Sales ($)'}
        )
        fig_time.update_layout(
            xaxis_title="Month",
            yaxis_title="Sales ($)",
            legend_title="Country",
            margin=dict(l=10, r=10, t=40, b=10),
            height=450
        )
        fig_time.update_traces(line=dict(width=3))
        st.plotly_chart(fig_time, use_container_width=True)
    
    with col2:
        # Hourly sales pattern
        filtered_data['Hour'] = filtered_data['Order Date'].dt.hour
        hourly_sales = filtered_data.groupby(['Hour', 'source'])['Price in Dollar'].sum().reset_index()
        
        fig_hourly = px.line(
            hourly_sales, 
            x='Hour', 
            y='Price in Dollar', 
            color='source',
            title='Hourly Sales Pattern',
            color_discrete_map={'USA': '#E3B448', 'Canada': '#DC3912'},
            template='plotly_dark',
            labels={'Price in Dollar': 'Sales ($)'}
        )
        fig_hourly.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Sales ($)",
            legend_title="Country",
            margin=dict(l=10, r=10, t=40, b=10),
            height=450,
            xaxis=dict(tickmode='linear', dtick=1)
        )
        fig_hourly.update_traces(line=dict(width=3))
        fig_hourly.update_xaxes(range=[0, 23])
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Data Explorer Section
    st.markdown("<hr style='border: 1px solid #333; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: white; margin-bottom: 20px;'>🔍 Data Explorer</h2>", unsafe_allow_html=True)
    
    with st.expander("Filter and Explore Raw Data", expanded=False):
        # Date range filter
        min_date = filtered_data['Date'].min().date()
        max_date = filtered_data['Date'].max().date()
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
        
        # Country filter
        selected_countries = st.multiselect(
            "Select Countries", 
            options=valid_sources,
            default=valid_sources
        )
        
        # Apply filters
        explore_data = filtered_data[
            (filtered_data['Date'].dt.date >= start_date) & 
            (filtered_data['Date'].dt.date <= end_date) &
            (filtered_data['source'].isin(selected_countries))
        
        # Show summary stats
        st.write(f"Filtered Data: {len(explore_data):,} records")
        
        # Show data table
        st.dataframe(
            explore_data.sort_values('Date', ascending=False).head(1000),
            use_container_width=True,
            hide_index=True,
            column_order=['Order Date', 'source', 'Product', 'Quantity Ordered', 'Price Each', 'Price in Dollar']
        )
        
        # Download button
        csv = explore_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name='sales_data_export.csv',
            mime='text/csv',
            use_container_width=True
        )
    
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 40px; padding: 20px; color: #666;">
        <p>Dashboard created by: Culanggo, Kein Jake A.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
