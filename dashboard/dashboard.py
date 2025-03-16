import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('dashboard/data_project.csv')
    return df

df = load_data()

# Convert datetime columns
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'])

# Add delivery time analysis
df['delivery_time'] = (df['order_estimated_delivery_date'] - df['order_purchase_timestamp']).dt.days

# Streamlit App
st.title("E-commerce Dashboard :sparkles:")

# Sidebar for date range selection
st.sidebar.header("Filter Data by Date Range")
min_date = df['order_purchase_timestamp'].min()
max_date = df['order_purchase_timestamp'].max()
start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

# Filter data based on date range
filtered_df = df[(df['order_purchase_timestamp'] >= pd.to_datetime(start_date)) & 
                 (df['order_purchase_timestamp'] <= pd.to_datetime(end_date))]

# Display basic metrics
st.subheader("Basic Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Orders", value=filtered_df['order_id'].nunique())
with col2:
    st.metric("Total Revenue", value=f"${filtered_df['price'].sum():.2f}")
with col3:
    st.metric("Average Delivery Time (days)", value=f"{filtered_df['delivery_time'].mean():.1f}")

# Best Performing Product Categories
st.subheader("Best Performing Product Categories")
category_revenue = filtered_df.groupby('product_category_name_english')['price'].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=category_revenue.index, y=category_revenue.values, palette='viridis')
plt.xticks(rotation=45)
plt.xlabel("Product Category")
plt.ylabel("Total Revenue")
st.pyplot(fig)

# Price Distribution
st.subheader("Price Distribution")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(filtered_df['price'], bins=20, kde=True, color='skyblue')
plt.xlabel("Price")
plt.ylabel("Frequency")
st.pyplot(fig)

# Freight Value Distribution
st.subheader("Freight Value Distribution")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(filtered_df['freight_value'], bins=20, kde=True, color='salmon')
plt.xlabel("Freight Value")
plt.ylabel("Frequency")
st.pyplot(fig)

# Delivery Time Analysis
st.subheader("Delivery Time Analysis")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(filtered_df['delivery_time'], bins=20, kde=True, color='lightgreen')
plt.xlabel("Delivery Time (days)")
plt.ylabel("Frequency")
st.pyplot(fig)

# Customer State Analysis
st.subheader("Customer State Analysis")
state_counts = filtered_df['customer_state'].value_counts()
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=state_counts.index, y=state_counts.values, palette='magma')
plt.xlabel("Customer State")
plt.ylabel("Number of Orders")
st.pyplot(fig)