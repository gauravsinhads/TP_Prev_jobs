import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Set Streamlit page config
st.set_page_config(page_title="Previous Jobs Breakdown", layout="centered")

# Read CSV
Prev_jobs = pd.read_csv('Prev_jobs.csv')

# Ensure there's a datetime column for filtering (replace 'date' with actual column name if different)
Prev_jobs['date'] = pd.to_datetime(Prev_jobs['date'], errors='coerce')

# Define custom color palette
colors = ["#001E44", "#F5F5F5", "#E53855", "#B4BBBE", "#2F76B9", "#3B9790", "#F5BA2E", "#6A4C93", "#F77F00"]

# Sidebar dropdown for time filter
time_filter = st.selectbox(
    "Select Time Range",
    ["Last 6 Months", "Last 12 Months"]
)

# Filter data based on selected time period
today = datetime.today()
if time_filter == "Last 6 Months":
    start_date = today - timedelta(days=180)
elif time_filter == "Last 12 Months":
    start_date = today - timedelta(days=365)

filtered_data = Prev_jobs[Prev_jobs['date'] >= start_date]

# Check if 'previous_jobs' column exists
if 'previous_jobs' not in filtered_data.columns:
    st.error("The column 'previous_jobs' is missing in the dataset.")
else:
    # Prepare data for pie chart
    job_counts = filtered_data['previous_jobs'].value_counts().reset_index()
    job_counts.columns = ['previous_jobs', 'count']
    job_counts['label'] = job_counts.apply(lambda x: f"{x['previous_jobs']} ({x['count']})", axis=1)

    # Plotly pie chart
    fig = px.pie(
        job_counts,
        names='label',
        values='count',
        color_discrete_sequence=colors,
        title=f"Breakdown of Previous Jobs ({time_filter})"
    )
    fig.update_traces(textinfo='percent+label')

    st.plotly_chart(fig, use_container_width=True)

