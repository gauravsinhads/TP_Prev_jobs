import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Set Streamlit page config
st.set_page_config(page_title="Previous Jobs Breakdown", layout="centered")

# Read CSV
Prev_jobs = pd.read_csv('Prev_jobs.csv')

# Parse 'INVITATIONDT' as datetime
Prev_jobs['INVITATIONDT'] = pd.to_datetime(Prev_jobs['INVITATIONDT'], errors='coerce')

# Define custom color palette
colors = ["#001E44", "#F5F5F5", "#E53855", "#B4BBBE", "#2F76B9", "#3B9790", "#F5BA2E", "#6A4C93", "#F77F00"]

# Sidebar dropdown for time filter
time_filter = st.selectbox(
    "Select Time Range",
    ["Last 6 Months", "Last 12 Months"]
)

# Filter data based on selected time period using 'INVITATIONDT'
today = datetime.today()
if time_filter == "Last 6 Months":
    start_date = today - timedelta(days=180)
elif time_filter == "Last 12 Months":
    start_date = today - timedelta(days=365)

filtered_data = Prev_jobs[Prev_jobs['INVITATIONDT'] >= start_date]

# Check if 'PREVIOUS_JOBS' column exists
if 'PREVIOUS_JOBS' not in filtered_data.columns:
    st.error("The column 'PREVIOUS_JOBS' is missing in the dataset.")
else:
    # Prepare data for pie chart
    job_counts = filtered_data['PREVIOUS_JOBS'].value_counts().reset_index()
    job_counts.columns = ['PREVIOUS_JOBS', 'count']
    job_counts['label'] = job_counts.apply(lambda x: f"{x['PREVIOUS_JOBS']} ({x['count']})", axis=1)

    # Plotly pie chart
    fig = px.pie(
        job_counts,
        names='label',
        values='count',
        color_discrete_sequence=colors,
        title=f"Breakdown of Previous Jobs ({time_filter})"
    )
    fig.update_traces(textinfo='percent+label')

    # Show chart
    st.plotly_chart(fig, use_container_width=True)
