import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(page_title="Previous Jobs Dashboard", layout="centered")

# Load data
Prev_jobs = pd.read_csv('Prev_jobs.csv')
Pje = pd.read_csv('Previous_jobs_EmpStat.csv')

# Parse dates
Prev_jobs['INVITATIONDT'] = pd.to_datetime(Prev_jobs['INVITATIONDT'], errors='coerce')
Pje['INVITATIONDT'] = pd.to_datetime(Pje['INVITATIONDT'], errors='coerce')

# Drop rows with missing dates
Prev_jobs = Prev_jobs.dropna(subset=['INVITATIONDT'])
Pje = Pje.dropna(subset=['INVITATIONDT'])

# Define custom colors
colors = ["#001E44", "#F5F5F5", "#E53855", "#B4BBBE", "#2F76B9", "#3B9790", "#F5BA2E", "#6A4C93", "#F77F00"]

# --- TOP DATE RANGE FILTER ---
st.markdown("### 📅 Select Custom Date Range")
min_date = min(Prev_jobs['INVITATIONDT'].min(), Pje['INVITATIONDT'].min()).date()
max_date = max(Prev_jobs['INVITATIONDT'].max(), Pje['INVITATIONDT'].max()).date()

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
with col2:
    end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

if start_date > end_date:
    st.error("❌ Start date must be before or equal to end date.")
else:
    # --- PIE CHART SECTION ---
    st.markdown("## 📊 Pie Chart: Breakdown of Previous Jobs")
    filtered_prev_jobs = Prev_jobs[
        (Prev_jobs['INVITATIONDT'].dt.date >= start_date) &
        (Prev_jobs['INVITATIONDT'].dt.date <= end_date)
    ]

    if 'PREVIOUS_JOBS' not in filtered_prev_jobs.columns:
        st.error("Column 'PREVIOUS_JOBS' not found in Prev_jobs.csv")
    elif filtered_prev_jobs.empty:
        st.warning("⚠️ No data in selected range.")
    else:
        job_counts = filtered_prev_jobs['PREVIOUS_JOBS'].value_counts().reset_index()
        job_counts.columns = ['PREVIOUS_JOBS', 'count']
        job_counts['label'] = job_counts.apply(lambda x: f"{x['PREVIOUS_JOBS']} ({x['count']})", axis=1)

        fig_pie = px.pie(
            job_counts,
            names='label',
            values='count',
            color_discrete_sequence=colors,
            title=f"Previous Jobs Distribution ({start_date} to {end_date})"
        )
        fig_pie.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

        # Export CSV
        csv_pie = filtered_prev_jobs.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Pie Chart Data CSV",
            data=csv_pie,
            file_name=f'Filtered_Prev_Jobs_{start_date}_to_{end_date}.csv',
            mime='text/csv'
        )

          # --- STACKED BAR CHART SECTION ---
    st.markdown("## 📊 Stacked Bar: Distribution of Previous Jobs Categories by Shortlisted/Hired Status")
    filtered_pje = Pje[
        (Pje['INVITATIONDT'].dt.date >= start_date) &
        (Pje['INVITATIONDT'].dt.date <= end_date)
    ]

    if 'PREVIOUS_JOBS' not in filtered_pje.columns or 'FOLDER' not in filtered_pje.columns:
        st.error("Columns 'PREVIOUS_JOBS' and/or 'FOLDER' not found in Previous_jobs_EmpStat.csv")
    elif filtered_pje.empty:
        st.warning("⚠️ No data in selected range.")
    else:
        # Filter only 'shortlisted' and 'hired'
        filtered_pje = filtered_pje[filtered_pje['FOLDER'].str.lower().isin(['shortlisted', 'hired'])]

        # Normalize folder casing for consistency
        filtered_pje['FOLDER'] = filtered_pje['FOLDER'].str.lower().str.capitalize()

        # Group and calculate counts
        bar_data = filtered_pje.groupby(['PREVIOUS_JOBS', 'FOLDER']).size().reset_index(name='count')

        # Calculate percentage within each PREVIOUS_JOBS group
        total_per_job = bar_data.groupby('PREVIOUS_JOBS')['count'].transform('sum')
        bar_data['percentage'] = (bar_data['count'] / total_per_job) * 100
        bar_data['text'] = bar_data.apply(lambda x: f"{x['count']} ({x['percentage']:.1f}%)", axis=1)

        # Define custom color map
        color_map = {
            "Shortlisted": "#F77F00",  # Orange
            "Hired": "#001E44",        # Dark blue
        }

        fig_bar = px.bar(
            bar_data,
            x='PREVIOUS_JOBS',
            y='count',
            color='FOLDER',
            text='text',
            title="Distribution of Previous Jobs Categories by Shortlisted/Hired Status",
            color_discrete_map=color_map
        )

        fig_bar.update_layout(
            barmode='stack',
            xaxis_title='Previous Jobs',
            yaxis_title='Count',
            uniformtext_minsize=8,
            uniformtext_mode='hide'
        )

        # Improve text appearance
        fig_bar.update_traces(textposition='inside')

        st.plotly_chart(fig_bar, use_container_width=True)

        # Export filtered data
        csv_bar = filtered_pje.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Bar Chart Data CSV",
            data=csv_bar,
            file_name=f'Filtered_Pje_Shortlisted_Hired_{start_date}_to_{end_date}.csv',
            mime='text/csv'
        )
