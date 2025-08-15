import streamlit as st 
import pandas as pd 
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ---- set konfigurasi halaman ----
st.set_page_config(
    page_title='Dashboard Analisis Penjualan',
    # page_icon='',
    layout='wide',
    initial_sidebar_state='expanded'
)

# -- fungsi untuk memuat data --
@st.cache_data
def load_data():
    return pd.read_csv("data/ecommerce_data.csv")

df = load_data()

df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# judul dashboard 
st.title("Dashboard penjualan pada Ecommerce")
st.markdown("Ini adalah dashboard dari trend penjualan dataset Ecommerce")

st.markdown("---")

st.sidebar.header("Filter & Navigasi")

pilihan_halaman = st.sidebar.radio(
    "Pilih Halaman:",
    ("Overview Dashboard", "Prediksi Penjualan")
)

if pilihan_halaman == "Overview Dashboard":
    st.sidebar.markdown("### Filter Dashboard")
    min_date = df['InvoiceDate'].min().date()
    max_date = df['InvoiceDate'].max().date()
    date_range = st.sidebar.date_input(
        "Pilih Rentang Tanggal",
        value=(min_date,max_date),
        min_value=min_date,
        max_value=max_date
    )
    if len(date_range) == 2:
        start_date_filter = pd.to_datetime(date_range[0])
        end_date_filter = pd.to_datetime(date_range[1])
        filtered_df = df[(df['InvoiceDate'] >= start_date_filter) & 
                            (df['InvoiceDate'] <= end_date_filter)]
    else: 
        # kalau filter date-nya belum tuntas
        filtered_df = df
        
    # filter berdasarkan wilayah 
    selected_regions = st.sidebar.multiselect(
        "Pilih Negara:",
        options=df['Country'].unique().tolist(),
        default=df['Country'].unique().tolist()
    )

    filtered_df = filtered_df[filtered_df['Country'].isin(selected_regions)]
# filter kategori produk 
    selected_categories = st.sidebar.multiselect(
        "Pilih Produk:",
        options=df['Description'].unique().tolist(),
        default=df['Description'].unique().tolist()
    )
    

    filtered_df = filtered_df[filtered_df['Description'].isin(selected_categories)]
else: # kalau tidak ada filter filter 
    filtered_df = df.copy()

# --- halaman utama overview dashboard -----------------
if pilihan_halaman == "Overview Dashboard":
#   metrik utama
    st.subheader("Performa Penjualan")

    col1, col2, col3, col4 = st.columns([3, 2, 3, 2])

    total_sales = (filtered_df['UnitPrice'] * filtered_df['Quantity']).sum()
    total_orders = filtered_df['InvoiceNo'].nunique()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0 # handle kalau total order 0
    total_products_sold = filtered_df['Quantity'].sum()

    with col1:
        st.metric(label="Total Penjualan", value=f"$ {total_sales:,.2f}")
    with col2:
        st.metric(label="Jumlah Pesanan", value=f"{total_orders:,.2f}")
    with col3:
        st.metric(label="Rata-Rata Nilai Pesanan", value=f"$ {avg_order_value:,.2f}")
    with col4:
        st.metric(label="Jumlah Produk Terjual", value=f"{total_products_sold:,.2f}")
    st.markdown("---")

    filtered_df['Month'] = filtered_df['InvoiceDate'].dt.month_name()
    filtered_df['Sales'] = filtered_df['Quantity'] * filtered_df['UnitPrice']
    # tren penjualan/line chart
    st.subheader("Tren Penjualan Bulanan")
    sales_by_month = filtered_df.groupby('Month')['Sales'].sum()
    # sales_by_month['bulan'] = pd.to_datetime(sales_by_month['bulan']).dt.to_period('M')
    # sales_by_month = sales_by_month.value_counts(by='bulan')
    # sales_by_month['bulan'] = sales_by_month['bulan'].astype(str)

    fig_monthly_sales = px.line(
        sales_by_month,
        x=sales_by_month.index,
        y='Sales',
        markers=True,
        hover_name=sales_by_month.index
    )
    st.plotly_chart(fig_monthly_sales, use_container_width=True)

    st.markdown("---")
    
    col_vis1, col_vis2 = st.columns(2)

    with col_vis1:
        st.markdown("<h3 style='text-align: center;'>Top 10 Penjualan Terlaris</h3>", unsafe_allow_html=True)

        top_product_sold = filtered_df.groupby('Description')['Sales'].sum().nlargest(10).reset_index(). sort_values(by = 'Sales', ascending=True) # agregasi

        # bar chart
        fig_top_products = px.bar(  
            top_product_sold,
            x='Sales',
            y='Description',
            orientation='h'
        )

        st.plotly_chart(fig_top_products, use_container_width=True)
        

    # membuat chart negara
    sales_by_region = filtered_df.groupby('Country')['Sales'].sum().reset_index()

    fig_region = px.bar(
        sales_by_region,
        x='Country',
        y='Sales',
        title="Total Penjualan per Wilayah",
        color='Country'

    )
    st.plotly_chart(fig_region, use_container_width=True)
    

filtered_df['Sales'] = filtered_df['UnitPrice'] * filtered_df['Quantity']

# Hitung total sales per customer
top_customers = (
    filtered_df.groupby('CustomerID')['Sales']
    .sum()
    .reset_index()
    .sort_values(by='Sales', ascending=False)
    .head(5)
)

st.write(top_customers)

fig_top_customers = px.bar(
    top_customers,
    x='CustomerID',
    y='Sales',
    title='Top 5 Customer dengan Pembelian Tertinggi',
    text='Sales'
)
st.plotly_chart(fig_top_customers, use_container_width=True)