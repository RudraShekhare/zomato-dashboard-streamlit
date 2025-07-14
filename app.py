import streamlit as st
import gdown
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import folium
from streamlit_folium import folium_static

# Load the dataset

file_id = "1TeOlC5b3Bl0oMWdynuZPz767RhaTpJSp"

download_url = f"https://drive.google.com/uc?id={file_id}"

output = "zomato.csv"

import os
if not os.path.exists(output):
    gdown.download(download_url, output, quiet=False)

# Now load the CSV
df = pd.read_csv(output, encoding='latin-1')


# Data Cleaning
df.drop(columns=['address', 'phone', 'url', 'menu_item', 'dish_liked'], inplace=True, errors='ignore')
df.dropna(inplace=True)

# Convert Rating column
df['rate'] = df['rate'].astype(str).str.replace('/5', '', regex=False)
df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
df['rate'] = df['rate'].fillna(df['rate'].mean())

# Convert Cost column
df['approx_cost(for two people)'] = df['approx_cost(for two people)'].astype(str).str.replace(',', '').astype(float)
df.rename(columns={'approx_cost(for two people)': 'Cost for Two'}, inplace=True)

# Streamlit UI
st.title("🍽️ Zomato Restaurant Dashboard")
st.sidebar.header("Filter Options")

# Sidebar filters
selected_location = st.sidebar.multiselect("Select Location", df['location'].unique())
selected_cuisine = st.sidebar.multiselect("Select Cuisine", df['cuisines'].unique())

# Numeric filters
min_cost, max_cost = int(df['Cost for Two'].min()), int(df['Cost for Two'].max())
cost_range = st.sidebar.slider("Filter by Cost for Two", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost))

min_rating, max_rating = float(df['rate'].min()), float(df['rate'].max())
rating_range = st.sidebar.slider("Filter by Rating", min_value=min_rating, max_value=max_rating, value=(min_rating, max_rating))

filtered_df = df[
    (df['Cost for Two'] >= cost_range[0]) & (df['Cost for Two'] <= cost_range[1]) &
    (df['rate'] >= rating_range[0]) & (df['rate'] <= rating_range[1])
]
if selected_location:
    filtered_df = filtered_df[filtered_df['location'].isin(selected_location)]
if selected_cuisine:
    filtered_df = filtered_df[filtered_df['cuisines'].isin(selected_cuisine)]

# Metrics
st.metric("Total Restaurants", filtered_df.shape[0])
st.metric("Average Rating", round(filtered_df['rate'].mean(), 2))

# Top Locations
st.subheader("📍 Top 10 Locations with Most Restaurants")
top_locations = filtered_df['location'].value_counts().head(10).reset_index()
top_locations.columns = ['Location', 'Count']
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=top_locations, x="Location", y="Count", hue="Location", palette="coolwarm", legend=False)
plt.xticks(rotation=45)
st.pyplot(fig)

# Cost vs Rating Scatter Plot
st.subheader("💰 Cost for Two vs. Rating")
fig = px.scatter(filtered_df, x="Cost for Two", y="rate", size="votes", color="location", title="Cost vs. Rating")
st.plotly_chart(fig)

# Cuisine Distribution
st.subheader("🍲 Top 10 Cuisines")
cuisine_counts = filtered_df['cuisines'].value_counts().nlargest(10)
fig = px.pie(names=cuisine_counts.index, values=cuisine_counts.values, title="Top 10 Most Popular Cuisines", hole=0.3)
st.plotly_chart(fig)

# Restaurant Ratings Analysis
st.subheader("⭐ Rating Distribution")
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(filtered_df['rate'], bins=10, kde=True, color="blue")
plt.title("Distribution of Ratings")
st.pyplot(fig)

# Most Popular Restaurant Types
st.subheader("🏪 Most Popular Restaurant Types")
rest_type_counts = filtered_df['rest_type'].value_counts().nlargest(10)
fig = px.pie(names=rest_type_counts.index, values=rest_type_counts.values, title="Top Restaurant Types", hole=0.3)
st.plotly_chart(fig)

# Restaurant Count by City (Map)
st.subheader("🌍 Restaurant Count by City")
city_counts = df['location'].value_counts().head(10)
map_data = pd.DataFrame({'City': city_counts.index, 'Count': city_counts.values})
m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
for city, count in zip(map_data['City'], map_data['Count']):
    folium.Marker(
        location=[np.random.uniform(19, 28), np.random.uniform(72, 80)],  # Random lat-long for now
        popup=f"{city}: {count} restaurants",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)
folium_static(m)

# Download Processed Data
st.subheader("📥 Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "filtered_zomato.csv", "text/csv", key="download-csv")

# Footer
st.markdown("🚀 Built with Streamlit & Pandas | Data from Zomato")
