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

# 1. COPY YOUR EXACT RENDER CONNECTION FROM ETL CODE
RENDER_DB_URL = "postgresql://whiplash_user:6EoohkmGo5ziA3qJMhsBYHl5P6yS9UKL@dpg-d0amg66uk2gs73busq9g-a.oregon-postgres.render.com/whiplash"

# 2. FUNCTION TO FETCH YOUR CLEANED DATA (from data_ETL table)
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cleaned_data():
    engine = create_engine(RENDER_DB_URL)
    with engine.connect() as conn:
        query = text('SELECT * FROM "data_ETL"')  # Your exact table name
        df = pd.read_sql(query, conn)
        
        # Ensure your datetime conversions match your ETL
        df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%y %H:%M') 
        df['Date'] = pd.to_datetime(df['Date'])
    return df

# Helper function to standardize source values
def clean_source(source):
    if isinstance(source, str):
        source_lower = source.lower()
        if 'usa' in source_lower or 'united states' in source_lower or 'us' in source_lower:
            return 'USA'
        elif 'canada' in source_lower or 'ca' in source_lower:
            return 'Canada'
    return source

# 3. DASHBOARD USING YOUR DATA STRUCTURE
def main():
    # Set dark theme inspired by the mobile UI
    st.set_page_config(layout="wide")
    
    # Custom CSS for dark theme styling
    st.markdown("""
    <style>
    .main {
        background-color: #121212;
        color: white;
    }
    .stApp {
        background-color: #121212;
    }
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    .stSidebar {
        background-color: #1e1e1e;
        border-right: 1px solid #333;
    }
    .stMetric {
        background-color: #1e1e1e !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }
    .stMetric > div {
        color: white !important;
    }
    .stMetric label {
        color: #3A6B35 !important;
    }
    .stDataFrame {
        background-color: #1e1e1e !important;
    }
    /* Add credit at bottom */
    .footer {
        position: fixed;
        bottom: 0;
        right: 10px;
        color: #666;
        font-size: 12px;
        padding: 5px;
        z-index: 999;
    }
    </style>
    <div class="footer">by: Culanggo, Kein Jake A.</div>
    """, unsafe_allow_html=True)
    
    st.title("🦅 USA vs 🍁 Canada Sales Dashboard")
    
    # Load data
    sales_data = get_cleaned_data()
    
    # Clean and standardize source column
    sales_data['source'] = sales_data['source'].apply(clean_source)
    
    # Filter for only USA and Canada data
    valid_sources = ['USA', 'Canada']
    filtered_data = sales_data[sales_data['source'].isin(valid_sources)]
    
    # Sidebar metrics
    st.sidebar.header("Data Overview")
    st.sidebar.write(f"Total Records: {len(filtered_data)}")
    st.sidebar.write(f"Date Range: {filtered_data['Date'].min().date()} to {filtered_data['Date'].max().date()}")
    
    # Overall metrics
    total_sales = filtered_data['Price in Dollar'].sum()
    avg_order = filtered_data['Price in Dollar'].mean()
    
    # Styled metrics with dark theme
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.markdown(f"""
        <div style="background-color:#1e1e1e; border-radius:12px; padding:15px; text-align:center; box-shadow:0 4px 8px rgba(0,0,0,0.2);">
            <h3 style="margin:0; color:#3A6B35; font-size:14px;">Total Sales</h3>
            <p style="margin:0; color:#E3B448; font-size:24px; font-weight:bold;">${total_sales:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[1]:
        st.markdown(f"""
        <div style="background-color:#1e1e1e; border-radius:12px; padding:15px; text-align:center; box-shadow:0 4px 8px rgba(0,0,0,0.2);">
            <h3 style="margin:0; color:#3A6B35; font-size:14px;">Avg. Order Value</h3>
            <p style="margin:0; color:#E3B448; font-size:24px; font-weight:bold;">${avg_order:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[2]:
        usa_count = len(filtered_data[filtered_data['source'] == 'USA'])
        st.markdown(f"""
        <div style="background-color:#1e1e1e; border-radius:12px; padding:15px; text-align:center; box-shadow:0 4px 8px rgba(0,0,0,0.2);">
            <h3 style="margin:0; color:#3A6B35; font-size:14px;">USA Orders</h3>
            <p style="margin:0; color:#E3B448; font-size:24px; font-weight:bold;">{usa_count:,}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[3]:
        canada_count = len(filtered_data[filtered_data['source'] == 'Canada'])
        st.markdown(f"""
        <div style="background-color:#1e1e1e; border-radius:12px; padding:15px; text-align:center; box-shadow:0 4px 8px rgba(0,0,0,0.2);">
            <h3 style="margin:0; color:#3A6B35; font-size:14px;">Canada Orders</h3>
            <p style="margin:0; color:#DC3912; font-size:24px; font-weight:bold;">{canada_count:,}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Create row layout for the main content
    st.markdown("<hr style='border: 1px solid #333; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Main plot - USA vs Canada Distribution (Pie Chart)
    st.markdown("<h2 style='color: white; margin-bottom: 20px;'> USA vs Canada Market Distribution</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Main pie chart - sales by country
        country_sales = filtered_data.groupby('source')['Price in Dollar'].sum().reset_index()
        fig_pie = px.pie(
            country_sales, 
            names='source', 
            values='Price in Dollar',
            title='Sales Distribution by Country',
            color='source',
            color_discrete_map={'USA': '#E3B448', 'Canada': '#DC3912'},
            hole=0.6
        )
        fig_pie.update_traces(textinfo='percent+label', pull=[0.05, 0], textfont_color='white')
        fig_pie.update_layout(
            legend_title="Country",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(color='white'),
            margin=dict(l=10, r=10, t=40, b=10),
            title_x=0.5
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Quantity ordered by country
        quantity_by_country = filtered_data.groupby('source')['Quantity Ordered'].sum().reset_index()
        fig_quantity = px.bar(
            quantity_by_country, 
            x='source', 
            y='Quantity Ordered',
            title='Total Quantity Ordered by Country',
            color='source',
            color_discrete_map={'USA': '#E3B448', 'Canada': '#DC3912'}
        )
        fig_quantity.update_layout(
            xaxis_title="Country", 
            yaxis_title="Total Quantity Ordered",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(color='white'),
            margin=dict(l=10, r=10, t=40, b=10),
            title_x=0.5
        )
        fig_quantity.update_xaxes(showgrid=False, gridcolor='#333')
        fig_quantity.update_yaxes(showgrid=True, gridcolor='#333')
        st.plotly_chart(fig_quantity, use_container_width=True)
    
    # Create the second row for more visualizations
    st.markdown("<hr style='border: 1px solid #333; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: white; margin-bottom: 20px;'>🔍 Product Analysis</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 5 most bought products by country
        top_products = filtered_data.groupby(['source', 'Product'])['Quantity Ordered'].sum().reset_index()
        usa_top = top_products[top_products['source'] == 'USA'].nlargest(5, 'Quantity Ordered')
        canada_top = top_products[top_products['source'] == 'Canada'].nlargest(5, 'Quantity Ordered')
        
        fig_top_products = make_subplots(rows=1, cols=2, subplot_titles=("Top 5 Products - USA", "Top 5 Products - Canada"))
        
        # USA Top Products
        fig_top_products.add_trace(
            go.Bar(
                x=usa_top['Product'], 
                y=usa_top['Quantity Ordered'], 
                marker_color='#E3B448',
                name='USA',
                text=usa_top['Quantity Ordered'],
                textposition='auto',
                textfont=dict(color='white')
            ),
            row=1, col=1
        )
        
        # Canada Top Products
        fig_top_products.add_trace(
            go.Bar(
                x=canada_top['Product'], 
                y=canada_top['Quantity Ordered'], 
                marker_color='#DC3912',
                name='Canada',
                text=canada_top['Quantity Ordered'],
                textposition='auto',
                textfont=dict(color='white')
            ),
            row=1, col=2
        )
        fig_top_products.update_layout(
            title="Top 5 Most Purchased Products by Country",
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(color='white'),
            title_x=0.5
        )
        fig_top_products.update_xaxes(showgrid=False, gridcolor='#333')
        fig_top_products.update_yaxes(showgrid=True, gridcolor='#333')
        st.plotly_chart(fig_top_products, use_container_width=True)
    
    with col2:
        # Top 3 most expensive products from each country
        # First get price for each product by country
        avg_price_by_product = filtered_data.groupby(['source', 'Product'])['Price Each'].mean().reset_index()
        
        usa_expensive = avg_price_by_product[avg_price_by_product['source'] == 'USA'].nlargest(3, 'Price Each')
        canada_expensive = avg_price_by_product[avg_price_by_product['source'] == 'Canada'].nlargest(3, 'Price Each')
        
        fig_expensive = make_subplots(rows=1, cols=2, subplot_titles=("Most Expensive - USA", "Most Expensive - Canada"))
        
        # USA Expensive Products
        fig_expensive.add_trace(
            go.Bar(
                x=usa_expensive['Product'], 
                y=usa_expensive['Price Each'], 
                marker_color='#E3B448',
                name='USA',
                text=usa_expensive['Price Each'].apply(lambda x: f"${x:.2f}"),
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # Canada Expensive Products
        fig_expensive.add_trace(
            go.Bar(
                x=canada_expensive['Product'], 
                y=canada_expensive['Price Each'], 
                marker_color='#DC3912',
                name='Canada',
                text=canada_expensive['Price Each'].apply(lambda x: f"${x:.2f}"),
                textposition='auto'
            ),
            row=1, col=2
        )
        fig_expensive.update_layout(
            title="Top 3 Most Expensive Products by Country",
            height=500,
            yaxis=dict(title='Price Each ($)', color='white', gridcolor='#333'),
            yaxis2=dict(title='Price Each ($)', color='white', gridcolor='#333'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(color='white'),
            title_x=0.5
        )
        fig_expensive.update_xaxes(showgrid=False, gridcolor='#333')
        st.plotly_chart(fig_expensive, use_container_width=True)
    
    # Third row
    st.markdown("<hr style='border: 1px solid #333; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: white; margin-bottom: 20px;'>📈 Time Analysis and Least Popular Products</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales over time by country
        filtered_data['Month'] = filtered_data['Date'].dt.to_period('M').astype(str)
        
        sales_over_time = filtered_data.groupby(['Month', 'source'])['Price in Dollar'].sum().reset_index()
        
        # Create proper time series for better visualization
        sales_over_time['Month'] = pd.to_datetime(sales_over_time['Month'])
        sales_over_time = sales_over_time.sort_values('Month')
        
        fig_time = px.line(
            sales_over_time, 
            x='Month', 
            y='Price in Dollar', 
            color='source',
            title='Sales Trend Over Time - USA vs Canada',
            color_discrete_map={'USA': '#E3B448', 'Canada': '#DC3912'}
        )
        fig_time.update_layout(
            xaxis_title="Month",
            yaxis_title="Sales ($)",
            legend_title="Country",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(color='white'),
            title_x=0.5
        )
        fig_time.update_xaxes(showgrid=False, gridcolor='#333')
        fig_time.update_yaxes(showgrid=True, gridcolor='#333')
        st.plotly_chart(fig_time, use_container_width=True)
    
    with col2:
        # Least ordered products by country
        least_products = filtered_data.groupby(['source', 'Product'])['Quantity Ordered'].sum().reset_index()
        
        # Get products with at least some orders
        least_products = least_products[least_products['Quantity Ordered'] > 0]
        
        usa_least = least_products[least_products['source'] == 'USA'].nsmallest(3, 'Quantity Ordered')
        canada_least = least_products[least_products['source'] == 'Canada'].nsmallest(3, 'Quantity Ordered')
        
        fig_least = make_subplots(rows=1, cols=2, subplot_titles=("Least Popular - USA", "Least Popular - Canada"))
        
        # USA Least Popular
        fig_least.add_trace(
            go.Bar(
                x=usa_least['Product'], 
                y=usa_least['Quantity Ordered'], 
                marker_color='#E3B448',
                name='USA'
            ),
            row=1, col=1
        )
        
        # Canada Least Popular
        fig_least.add_trace(
            go.Bar(
                x=canada_least['Product'], 
                y=canada_least['Quantity Ordered'], 
                marker_color='#DC3912',
                name='Canada'
            ),
            row=1, col=2
        )
        fig_least.update_layout(
            title="Least Ordered Products by Country",
            height=500,
            yaxis=dict(title='Quantity Ordered', color='white', gridcolor='#333'),
            yaxis2=dict(title='Quantity Ordered', color='white', gridcolor='#333'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(color='white'),
            title_x=0.5
        )
        fig_least.update_xaxes(showgrid=False, gridcolor='#333')
        st.plotly_chart(fig_least, use_container_width=True)
    
    # Add an interactive filter section at the bottom
    st.markdown("<hr style='border: 1px solid #333; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: white; margin-bottom: 20px;'>🔎 Interactive Data Explorer</h2>", unsafe_allow_html=True)
    
    with st.expander("Filter and Explore Data"):
        # Custom styling for the expander content
        st.markdown("""
        <style>
        .streamlit-expanderContent {
            background-color: #1e1e1e !important;
            border-radius: 8px !important;
            padding: 15px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        # Date range selector
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            start_date = st.date_input("Start Date", filtered_data['Date'].min())
        with date_col2:
            end_date = st.date_input("End Date", filtered_data['Date'].max())
        
        # Convert to datetime for filtering
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Filter data based on date range
        date_filtered = filtered_data[(filtered_data['Date'] >= start_date) & (filtered_data['Date'] <= end_date)]
        
        # Country selector
        selected_countries = st.multiselect(
            "Select Countries", 
            options=valid_sources,
            default=valid_sources
        )
        
        # Apply country filter
        final_filtered = date_filtered[date_filtered['source'].isin(selected_countries)]
        
        # Show filtered data
        st.write(f"Filtered Data: {len(final_filtered)} records")
        st.dataframe(
            final_filtered.head(100),
            use_container_width=True,
            hide_index=True
        )
        
        # Add download button for filtered data
        csv = final_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name='filtered_sales_data.csv',
            mime='text/csv',
        )
    
    # Add creator's signature with styling
    st.markdown("""
    <div style="text-align: center; margin-top: 40px; padding: 20px; color: #666;">
        <p>Dashboard by: Culanggo, Kein Jake A.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()