import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Sample data
df = pd.read_csv('dashboard/data_project.csv')

# Convert datetime columns
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'])

# Add delivery time analysis
df['delivery_time'] = (df['order_estimated_delivery_date'] - df['order_purchase_timestamp']).dt.days

def create_dashboard():
    # Set page title
    st.title("E-commerce Orders Dashboard")

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
    sns.barplot(x=category_revenue.index, y=category_revenue.values, palette='viridis', ax=ax)
    plt.xticks(rotation=45)
    plt.xlabel("Product Category")
    plt.ylabel("Total Revenue")
    st.pyplot(fig)

    # Display the raw data
    st.subheader("Raw Data")
    st.write(filtered_df)

    # Basic statistics
    st.subheader("Basic Statistics")
    st.write(filtered_df.describe())

    # Filter by customer state
    st.subheader("Filter by Customer State")
    selected_state = st.selectbox("Select State", df["customer_state"].unique())
    filtered_data = df[df["customer_state"] == selected_state]
    st.write(filtered_data)

    # Total sales by product category
    st.subheader("Total Sales by Product Category")
    sales_by_category = filtered_df.groupby("product_category_name_english")["payment_value"].sum().reset_index()
    st.bar_chart(sales_by_category.set_index("product_category_name_english"))

    # Average freight value by state
    st.subheader("Average Freight Value by State")
    avg_freight_by_state = filtered_df.groupby("customer_state")["freight_value"].mean().reset_index()
    st.bar_chart(avg_freight_by_state.set_index("customer_state"))

    # Payment type distribution
    st.subheader("Payment Type Distribution")
    payment_type_dist = filtered_df["payment_type"].value_counts()
    st.bar_chart(payment_type_dist)

# Run the dashboard
if __name__ == "__main__":
    create_dashboard()
