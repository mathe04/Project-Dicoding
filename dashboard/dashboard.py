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

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), gridspec_kw={'width_ratios': [2, 1]})
sns.barplot(x=top_products.values, y=top_products.index, ax=ax1)
ax1.set_title('Top 5 Products')
ax1.set_ylabel('')
sns.barplot(x=bottom_products.values, y=bottom_products.index, ax=ax2)
ax2.set_title('Bottom 5 Products')
ax2.yaxis.tick_right()
ax2.yaxis.set_label_position("right")
plt.tight_layout()
st.pyplot(fig)

# Subheader 3: Payment Type Distribution
st.subheader('💳 Payment Type Distribution')
payment_distribution = filtered_data_1['payment_type'].value_counts()
fig = px.pie(payment_distribution, values=payment_distribution.values, names=payment_distribution.index, title='Payment Type Distribution')
st.plotly_chart(fig)

# Subheader 4: Top Customers
st.subheader('👤 Top Customers')
top_customers = filtered_data_1.groupby('customer_id').agg({'order_id': 'count', 'price': 'sum'}).nlargest(3, 'price')
top_customers = top_customers.rename(columns={'customer_id': 'ID Customer', 'order_id': 'Quantity', 'price':'Total Spending'})
st.table(top_customers)

# Subheader 5: Customer Segmentation
st.subheader('📊 Customer Segmentation')

# Buat mapping dari customer_id ke ID baru
filtered_data_2['new_customer_id'], unique_customers = pd.factorize(filtered_data_2['customer_id'])

# Recency (R)
max_purchase_date = filtered_data_2['order_purchase_timestamp'].max()
filtered_data_2['Recency'] = (max_purchase_date - filtered_data_2['order_purchase_timestamp']).dt.days

# Frequency (F)
frequency_data = filtered_data_2.groupby('customer_id')['order_id'].count().reset_index()
frequency_data.rename(columns={'order_id': 'Frequency'}, inplace=True)

# Monetary (M)
monetary_data = filtered_data_2.groupby('customer_id')['payment_value'].sum().reset_index()
monetary_data.rename(columns={'payment_value': 'Monetary'}, inplace=True)

# Gabungkan data RFM
rfm_data = filtered_data_2.groupby('new_customer_id').agg({
    'Recency': 'min',
    'order_id': 'count',
    'payment_value': 'sum'
}).rename(columns={
    'order_id': 'Frequency',
    'payment_value': 'Monetary'
}).reset_index()

# Fungsi untuk mengkategorikan Recency, Frequency, dan Monetary
def RScore(x, p, d):
    if x <= d[p][0.25]:
        return 4
    elif x <= d[p][0.50]:
        return 3
    elif x <= d[p][0.75]:
        return 2
    else:
        return 1

def FMScore(x, p, d):
    if x <= d[p][0.25]:
        return 1
    elif x <= d[p][0.50]:
        return 2
    elif x <= d[p][0.75]:
        return 3
    else:
        return 4

# Membuat segmentasi berdasarkan quartile
quantiles = rfm_data.quantile(q=[0.25, 0.5, 0.75])
quantiles = quantiles.to_dict()

# Terapkan fungsi ke data
rfm_data['R_Quartile'] = rfm_data['Recency'].apply(RScore, args=('Recency', quantiles))
rfm_data['F_Quartile'] = rfm_data['Frequency'].apply(FMScore, args=('Frequency', quantiles))
rfm_data['M_Quartile'] = rfm_data['Monetary'].apply(FMScore, args=('Monetary', quantiles))

# Gabungkan quartile scores untuk mendapatkan RFM Score
rfm_data['RFM_Score'] = rfm_data['R_Quartile'].astype(str) + rfm_data['F_Quartile'].astype(str) + rfm_data['M_Quartile'].astype(str)

# Contoh segmentasi
rfm_data['Segment'] = rfm_data['RFM_Score'].apply(lambda x: 'Best Customers' if x == '444' else
                                                              'Loyal Customers' if x in ['344', '434', '443'] else
                                                              'Potential Loyalists' if x in ['334', '343', '433'] else
                                                              'Recent Customers' if x in ['244', '424', '442'] else
                                                              'Promising' if x in ['144', '414', '441'] else
                                                              'Customers Needing Attention' if x in ['233', '323', '332'] else
                                                              'About to Sleep' if x in ['133', '313', '331'] else
                                                              'At Risk' if x in ['222', '322', '232', '223'] else
                                                              'Hibernating' if x in ['111', '112', '121', '122', '211', '212', '221'] else
                                                              'Lost')

# Tampilkan hasil segmentasi
st.write(rfm_data[['new_customer_id', 'RFM_Score', 'Segment']])

# Visualisasi segmentasi
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(x='Segment', data=rfm_data, ax=ax, order=rfm_data['Segment'].value_counts().index)
plt.xticks(rotation=90)
st.pyplot(fig)
