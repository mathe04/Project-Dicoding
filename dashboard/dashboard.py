!pip install streamlit pandas

import streamlit as st
import pandas as pd

# Sample data
df = pd.read_csv('data_project.csv')

def create_dashboard():
    # Set page title
    st.title("E-commerce Orders Dashboard")

    # Display the raw data
    st.subheader("Raw Data")
    st.write(df)

    # Basic statistics
    st.subheader("Basic Statistics")
    st.write(df.describe())

    # Filter by customer state
    st.subheader("Filter by Customer State")
    selected_state = st.selectbox("Select State", df["customer_state"].unique())
    filtered_data = df[df["customer_state"] == selected_state]
    st.write(filtered_data)

    # Total sales by product category
    st.subheader("Total Sales by Product Category")
    sales_by_category = df.groupby("product_category_name_english")["payment_value"].sum().reset_index()
    st.bar_chart(sales_by_category.set_index("product_category_name_english"))

    # Average freight value by state
    st.subheader("Average Freight Value by State")
    avg_freight_by_state = df.groupby("customer_state")["freight_value"].mean().reset_index()
    st.bar_chart(avg_freight_by_state.set_index("customer_state"))

    # Payment type distribution
    st.subheader("Payment Type Distribution")
    payment_type_dist = df["payment_type"].value_counts()
    st.bar_chart(payment_type_dist)

# Run the dashboard
if __name__ == "__main__":
    create_dashboard()