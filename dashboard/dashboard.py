import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Mapping inisial ke nama negara bagian
state_mapping = {
    'RJ': 'Rio de Janeiro',
    'SP': 'São Paulo',
    'MG': 'Minas Gerais',
    'PR': 'Paraná',
    'GO': 'Goiás',
    'BA': 'Bahia',
    'AL': 'Alagoas',
    'MS': 'Mato Grosso do Sul',
    'CE': 'Ceará',
    'DF': 'Distrito Federal',
    'RS': 'Rio Grande do Sul',
    'PE': 'Pernambuco',
    'SC': 'Santa Catarina',
    'ES': 'Espírito Santo',
    'MA': 'Maranhão',
    'PA': 'Pará',
    'MT': 'Mato Grosso',
    'PB': 'Paraíba',
    'AM': 'Amazonas',
    'AP': 'Amapá',
    'PI': 'Piauí',
    'TO': 'Tocantins',
    'RO': 'Rondônia',
    'RN': 'Rio Grande do Norte',
    'SE': 'Sergipe',
    'AC': 'Acre',
    'RR': 'Roraima'
}

# Load data
@st.cache_data
def load_data():
    data = pd.read_csv('dashboard/data_project.csv')
    data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'])
    # Ganti inisial dengan nama negara bagian
    data['customer_state'] = data['customer_state'].map(state_mapping)
    return data

data = load_data()

# Sidebar
st.sidebar.header('Filter Data')
date_range = st.sidebar.date_input("Pilih Range Tanggal", [data['order_purchase_timestamp'].min(), data['order_purchase_timestamp'].max()])
customer_state = st.sidebar.selectbox("Pilih State", data['customer_state'].unique())

# Filter data based on sidebar input
filtered_data_1 = data[(data['order_purchase_timestamp'].dt.date >= date_range[0]) & (data['order_purchase_timestamp'].dt.date <= date_range[1]) & (data['customer_state'] == customer_state)]
filtered_data_2 = data[(data['order_purchase_timestamp'].dt.date >= date_range[0]) & (data['order_purchase_timestamp'].dt.date <= date_range[1])]

# Mainbar
st.title('🛍️ E-Commerce Dashboard')

# Subheader 1: Order Overview
st.subheader('📊 Order Overview')
col1, col2, col3 = st.columns(3)
col1.metric("Total Orders", filtered_data_1['order_id'].nunique())
col2.metric("Canceled Orders", filtered_data_1[filtered_data_1['order_status'] == 'canceled']['order_id'].nunique())
col3.metric("Total Revenue", f"${filtered_data_1['payment_value'].sum():,.2f}")

# Subheader 2: Product Performance
st.subheader('📈 Product Performance')
top_products = filtered_data_1['product_category_name_english'].value_counts().nlargest(5)
bottom_products = filtered_data_1['product_category_name_english'].value_counts().nsmallest(5)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
sns.barplot(x=top_products.values, y=top_products.index, ax=ax1)
ax1.set_title('Top 5 Products')
sns.barplot(x=bottom_products.values, y=bottom_products.index, ax=ax2)
ax2.set_title('Bottom 5 Products')
st.pyplot(fig)

# Subheader 3: Payment Type Distribution
st.subheader('💳 Payment Type Distribution')
payment_distribution = filtered_data_1['payment_type'].value_counts()
fig = px.pie(payment_distribution, values=payment_distribution.values, names=payment_distribution.index, title='Payment Type Distribution')
st.plotly_chart(fig)

# Subheader 4: Top Customers
st.subheader('👤 Top Customers')
top_customers = filtered_data_1.groupby('customer_id').agg({'order_id': 'count', 'price': 'sum'}).nlargest(3, 'price')
st.table(top_customers)

# Subheader 5: State-wise Revenue Map
st.subheader('🌍 State-wise Revenue')
state_revenue = filtered_data_2.groupby('customer_state')['price'].sum().reset_index()
fig = px.choropleth(state_revenue, locations='customer_state', locationmode='country names', color='price', scope='south america', title='Total Revenue by State', hover_name='customer_state')
st.plotly_chart(fig)
