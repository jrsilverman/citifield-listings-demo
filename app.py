import streamlit as st
import pandas as pd
import json
import plotly.express as px
import gzip

@st.cache_data
def load_data(file_path):
    with gzip.open(file_path, 'rt', encoding='utf-8') as file:
        data = json.load(file)
    return pd.DataFrame(data)

# Load the data
df = load_data('normalized_listings.json.gz')

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Streamlit app layout
st.title('Citi Field Ticket Listings Analysis')

st.markdown('### Technical Demonstration')

# Add human-readable note
st.markdown("""
**Analysis of Listings: Monday, September 16th at 7:10 PM.**  
This dashboard helps you explore ticket prices, grades, and availability over time for the event.
Use the filters on the left to narrow down your search by section, row, price range, or specific ticket IDs. Built by Jonathan Silverman for the love of the game.
""")

# Sidebar for filters
st.sidebar.header('Filter Options')

# Optional filter by section
sections = sorted(df['sid'].unique())
selected_section = st.sidebar.selectbox('Select Section (Optional)', ['All'] + sections, index=sections.index('112') if '112' in sections else 0)

# Optional filter by seat row
rows = sorted(df['r'].unique())
selected_row = st.sidebar.selectbox('Select Row (Optional)', ['All'] + rows, index=0)

# Optional filter by ID
filter_id = st.sidebar.text_input('Filter by ID (Optional)', '')

# Filter by price
min_price, max_price = st.sidebar.slider(
    'Select Price Range',
    float(df['p'].min()), 1600.0,  # Set default max price to 1600
    (float(df['p'].min()), 1600.0)  # Default range
)

# Apply filters
filtered_df = df.copy()

if selected_section != 'All':
    filtered_df = filtered_df[filtered_df['sid'] == selected_section]

if selected_row != 'All':
    filtered_df = filtered_df[filtered_df['r'] == selected_row]

if filter_id:
    filtered_df = filtered_df[filtered_df['id'].str.contains(filter_id, case=False, na=False)]

filtered_df = filtered_df[(filtered_df['p'] >= min_price) & (filtered_df['p'] <= max_price)]

# Summary
st.sidebar.header('Summary Options')

st.subheader('Data Summary')
st.write(f"Number of records: {len(filtered_df)}")
st.write(f"Average Price: ${filtered_df['p'].mean():.2f}")
st.write(f"Maximum Price: ${filtered_df['p'].max():.2f}")
st.write(f"Minimum Price: ${filtered_df['p'].min():.2f}")

# Display filtered data
st.subheader('Filtered Data')
st.dataframe(filtered_df)

# Visualization
st.sidebar.header('Visualization Options')

# Sort the filtered data once
sorted_filtered_df = filtered_df.sort_values(by='timestamp')

# Price Distribution Chart
st.subheader('Price Distribution')
st.markdown('This chart shows the distribution of ticket prices, helping you quickly spot the most common price points.')

# Count the occurrences of prices and reset the index
price_distribution = filtered_df['p'].value_counts().reset_index()
price_distribution.columns = ['Price', 'Count']
price_distribution = price_distribution.sort_values('Price')

# Plot the bar chart
st.bar_chart(price_distribution.set_index('Price')['Count'])

# Scatter Plot for Grades vs Price using Plotly
st.subheader('Grades vs Price')
st.markdown('This scatter plot visualizes the relationship between the seat grade and price, helping you evaluate price points based on seat quality.')

fig = px.scatter(filtered_df, x='grade', y='p', color='id', 
                 labels={'grade': 'Grade', 'p': 'Price'},
                 title='Grades vs Price')
st.plotly_chart(fig)

# Chart for Price Changes Over Time using Plotly
st.subheader('Price Changes Over Time')
st.markdown('This line chart tracks how ticket prices have changed over time, allowing you to analyze trends in pricing as the event date approaches.')

if len(sorted_filtered_df['timestamp'].unique()) > 1:
    fig = px.line(sorted_filtered_df, x='timestamp', y='p', color='id', markers=True,
                  labels={'timestamp': 'Timestamp', 'p': 'Price'},
                  title='Price Changes Over Time by ID')
    st.plotly_chart(fig)
else:
    st.write("Not enough data to show price changes over time.")

# Chart for Grade Over Time using Plotly
st.subheader('Grade Over Time')
st.markdown('This chart tracks changes in seat grades over time, giving insight into the availability and quality of tickets as the game date nears.')

if len(sorted_filtered_df['timestamp'].unique()) > 1:
    fig = px.line(sorted_filtered_df, x='timestamp', y='grade', color='id', markers=True,
                  labels={'timestamp': 'Timestamp', 'grade': 'Grade'},
                  title='Grade Over Time by ID')
    st.plotly_chart(fig)
else:
    st.write("Not enough data to show grade changes over time.")

# Show raw data if needed
if st.checkbox('Show Raw Data'):
    st.subheader('Raw Data')
    st.write(filtered_df)

# Footer note
st.markdown("""
---
Made by Jonathan Silverman, all rights reserved.
""")