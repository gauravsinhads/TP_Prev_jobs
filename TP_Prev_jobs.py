import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set Streamlit page config
st.set_page_config(page_title="Previous Jobs Breakdown", layout="centered")

# Read CSV
Prev_jobs = pd.read_csv('Prev_jobs.csv')

# Parse 'INVITATIONDT' as datetime
Prev_jobs['INVITATIONDT'] = pd.to_datetime(Prev_jobs['INVITATIONDT'], errors='coerce')

# Drop rows with invalid or missing dates
Prev_jobs = Prev_jobs.dropna(subset=['INVITATIONDT'])

# Define custom color palette
colors = ["#001E44", "#F5F5F5", "#E53855", "#B4BBBE", "#2F76B9", "#3B9790", "#F5BA2E", "#6A4C93", "#F77F00"]

# Get min and max dates for filtering
min_date = Prev_jobs['INVITATIONDT'].min().date()
max_date = Prev_jobs['INVITATIONDT'].max().date()

# --- TOP DATE RANGE FILTER ---
st.markdown("### 📅 Select Custom Date Range")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
with col2:
    end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

# Ensure valid date range
if start_date > end_date:
    st.error("❌ Start date must be before or equal to end date.")
else:
    # Filter data based on date range
    mask = (Prev_jobs['INVITATIONDT'].dt.date >= start_date) & (Prev_jobs['INVITATIONDT'].dt.date <= end_date)
    filtered_data = Prev_jobs[mask]

    # Check column and data
    if 'PREVIOUS_JOBS' not in filtered_data.columns:
        st.error("The column 'PREVIOUS_JOBS' is missing in the dataset.")
    elif filtered_data.empty:
        st.warning("⚠️ No data available for the selected date range.")
    else:
        # Create value counts for pie chart
        job_counts = filtered_data['PREVIOUS_JOBS'].value_counts().reset_index()
        job_counts.columns = ['PREVIOUS_JOBS', 'count']
        job_counts['label'] = job_counts.apply(lambda x: f"{x['PREVIOUS_JOBS']} ({x['count']})", axis=1)

        # Plot pie chart
        fig = px.pie(
            job_counts,
            names='label',
            values='count',
            color_discrete_sequence=colors,
            title=f"Breakdown of Previous Jobs ({start_date} to {end_date})"
        )
        fig.update_traces(textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

        # Export filtered data as CSV
        st.markdown("### 📤 Export Filtered Data")
        csv = filtered_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f'Filtered_Prev_Jobs_{start_date}_to_{end_date}.csv',
            mime='text/csv'
        )
