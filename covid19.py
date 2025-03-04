import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np
import datetime
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
from bs4 import BeautifulSoup

# ⏰ Auto-refresh every 5 minutes (300000 ms)
st_autorefresh(interval=300000, key="auto_refresh")

# 🎯 Application Title
st.title("📊 COVID-19 Data Analysis in Indonesia")

# URL source and fallback data
web_scrape_url = 'https://pusatkrisis.kemkes.go.id/covid-19-id/'

# UPDATED fallback_cases (manually computed Active Cases):
#  - Confirmed: 6,811,444
#  - Recovered: 6,640,216
#  - Deaths:    161,853
#  - Active = Confirmed - (Recovered + Deaths) = 6,811,444 - (6,640,216 + 161,853) = 9,375
fallback_cases = [6811444, 6640216, 161853, 9375]

fallback_global = 676681574
fallback_suspect = 1080
fallback_specimen = 13678
labels = ['Confirmed', 'Recovered', 'Deaths', 'Active Cases']

# Initialize data in session_state
if "cases" not in st.session_state:
    st.session_state.cases = fallback_cases
if "global_cases" not in st.session_state:
    st.session_state.global_cases = fallback_global
if "suspect" not in st.session_state:
    st.session_state.suspect = fallback_suspect
if "specimen" not in st.session_state:
    st.session_state.specimen = fallback_specimen
if "api_status" not in st.session_state:
    st.session_state.api_status = "✅ Live Data"
if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.datetime.min

def fetch_latest_data():
    """
    Fetches the latest COVID-19 data from the Ministry of Health website.
    If data retrieval fails or data is incomplete, fallback data is used.
    """
    try:
        response = requests.get(web_scrape_url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract integer values from the HTML
        numbers = [int(num.text.replace('.', '').replace(',', '')) for num in soup.select('.covid-case strong')]

        # If at least 3 numbers (Confirmed, Recovered, Deaths) are found:
        if len(numbers) >= 3:
            # Assign Confirmed, Recovered, Deaths
            st.session_state.cases[0] = numbers[0]
            st.session_state.cases[1] = numbers[1]
            st.session_state.cases[2] = numbers[2]

            # If the website also provides Active Cases as the 4th value, use it:
            if len(numbers) >= 4:
                st.session_state.cases[3] = numbers[3]
            else:
                # Otherwise, compute Active Cases manually
                st.session_state.cases[3] = (
                    st.session_state.cases[0] 
                    - (st.session_state.cases[1] + st.session_state.cases[2])
                )

            # Update global, suspect, and specimen if provided
            st.session_state.global_cases = numbers[0]  # If the site uses the 1st number as global
            if len(numbers) > 4:
                st.session_state.suspect = numbers[4]
            if len(numbers) > 5:
                st.session_state.specimen = numbers[5]

            st.session_state.api_status = "✅ Latest Data from Ministry of Health"
            st.session_state.last_update = datetime.datetime.now()
        else:
            raise ValueError("Incomplete data retrieved.")

    except Exception:
        # If anything goes wrong, revert to fallback
        st.session_state.cases = fallback_cases
        st.session_state.global_cases = fallback_global
        st.session_state.suspect = fallback_suspect
        st.session_state.specimen = fallback_specimen
        st.session_state.api_status = "❌ Using Fallback Data"

# Fetch data on page load
fetch_latest_data()
cases = st.session_state.cases
last_updated = st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')

# ------------------ SIDEBAR ------------------ #
with st.sidebar:
    st.subheader("📱 Data Status")
    st.write(st.session_state.api_status)
    st.write(f"**Last Updated:** {last_updated}")
    st.write(f"🌎 **Global Cases:** {st.session_state.global_cases:,}")

    # Calculate percentages
    recovery_rate = (cases[1] / cases[0]) * 100 if cases[0] > 0 else 0
    death_rate = (cases[2] / cases[0]) * 100 if cases[0] > 0 else 0
    active_rate = (cases[3] / cases[0]) * 100 if cases[0] > 0 else 0

    st.write(f"✔️ **Recovery Rate:** {recovery_rate:.2f}%")
    st.write(f"⚖️ **Death Rate:** {death_rate:.2f}%")
    st.write(f"🏥 **Active Cases:** {active_rate:.2f}%")
    st.write(f"🟡 **Suspect:** {st.session_state.suspect:,}")
    st.write(f"🧪 **Specimens:** {st.session_state.specimen:,}")

# ------------------ MAIN CONTENT ------------------ #
st.subheader("📊 Data Overview & Statistics")
st.markdown("""
**Data Source:** Indonesian Ministry of Health  
**Data Categories:** Confirmed, Recovered, Deaths, Active Cases  
If data retrieval fails, fallback data (as of June 21, 2023) will be used.
""")

# Frequency Distribution Table
freq_table = pd.DataFrame({'Category': labels, 'Amount': cases})
freq_table['Relative Frequency'] = freq_table['Amount'] / freq_table['Amount'].sum()

freq_table_styled = freq_table.reset_index(drop=True).style.format({
    "Amount": "{:,.0f}",
    "Relative Frequency": "{:.2%}"
})

st.markdown("#### Frequency Distribution Table")
st.dataframe(freq_table_styled, use_container_width=True)

# Calculate midpoints
midpoints = [(cases[i] + cases[i+1]) / 2 for i in range(len(cases) - 1)]
st.write("**Midpoints between categories:**", midpoints)

# Tabs for Matplotlib, Plotly, and Statistical Analysis
tab1, tab2, tab3 = st.tabs(["Matplotlib Charts", "Plotly Charts", "Statistical Analysis"])

with tab1:
    st.markdown("#### Bar Chart (Matplotlib)")
    fig, ax = plt.subplots()
    ax.bar(labels, cases, color=['blue', 'green', 'red', 'orange'])
    ax.set_ylabel("Number of Cases")
    ax.set_title("COVID-19 Case Distribution")
    st.pyplot(fig)
    
    st.markdown("#### Histogram (Matplotlib)")
    fig, ax = plt.subplots()
    ax.hist(cases, bins=4, color='blue', alpha=0.7)
    ax.set_title("Case Histogram")
    st.pyplot(fig)

with tab2:
    st.markdown("#### Bar Chart (Plotly)")
    fig = px.bar(
        x=labels,
        y=cases,
        color=labels,
        labels={'x': 'Category', 'y': 'Number of Cases'},
        title="COVID-19 Case Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### Pie Chart (Plotly)")
    fig = px.pie(
        values=cases,
        names=labels,
        title="Case Proportions"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("#### Cumulative Frequency")
    cumulative = np.cumsum(cases)
    st.line_chart(cumulative)
    
    st.markdown("#### Basic Statistics")
    mean_val = np.mean(cases)
    median_val = np.median(cases)
    std_val = np.std(cases)
    st.write(f"**Mean:** {mean_val:.2f}")
    st.write(f"**Median:** {median_val:.2f}")
    st.write(f"**Standard Deviation:** {std_val:.2f}")
    
    # Determine skewness
    if mean_val == median_val:
        skewness = "Symmetric Distribution"
    elif mean_val < median_val:
        skewness = "Left-Skewed Distribution"
    else:
        skewness = "Right-Skewed Distribution"
    st.write(f"**Distribution Shape:** {skewness}")
    
    st.markdown("#### Chebyshev's Theorem")
    for k in [1, 2, 3]:
        percentage = (1 - 1/(k**2)) * 100
        st.write(f"At least {percentage:.2f}% of data lies within {k} SD(s) of the mean.")

# Calculation Formulas
st.subheader("📝 Calculation Formulas")
st.markdown(f"""
- **Recovery Rate** = `(Recovered / Total Cases) × 100%`  
  => {cases[1]} / {cases[0]} × 100% = **{recovery_rate:.2f}%**
- **Death Rate** = `(Deaths / Total Cases) × 100%`  
  => {cases[2]} / {cases[0]} × 100% = **{death_rate:.2f}%**
- **Active Rate** = `(Active Cases / Total Cases) × 100%`  
  => {cases[3]} / {cases[0]} × 100% = **{active_rate:.2f}%**
""")

# Simple Time Series Analysis
st.subheader("📈 Time Series Analysis (Simple Example)")
st.line_chart(pd.Series(cases, index=labels))

# COVID-19 Data by Province (if file is available)
st.subheader("📌 COVID-19 Data by Province")
try:
    df = pd.read_csv("covid_19_indonesia_time_series_all.csv")
    # Filter out national data
    df_provinces = df[(df["Location"] != "Indonesia") & (df["Location ISO Code"].str.startswith("ID-"))]
    latest_date = df_provinces["Date"].max()
    
    # Select the latest data & relevant columns
    df_latest = df_provinces[df_provinces["Date"] == latest_date][
        ["Location", "Total Cases", "Total Recovered", "Total Deaths"]
    ].copy()
    
    # Rename columns for clarity
    df_latest.rename(columns={
        "Location": "Province",
        "Total Cases": "Confirmed",
        "Total Recovered": "Recovered",
        "Total Deaths": "Deaths"
    }, inplace=True)
    
    # Calculate recovery & death rates per province
    df_latest["Recovery Rate"] = (df_latest["Recovered"] / df_latest["Confirmed"]) * 100
    df_latest["Death Rate"] = (df_latest["Deaths"] / df_latest["Confirmed"]) * 100
    
    # Reset index to remove original DataFrame index
    df_latest.reset_index(drop=True, inplace=True)
    
    # Format columns (thousand separators & percentages)
    df_latest_styled = df_latest.style.format({
        "Confirmed": "{:,.0f}",
        "Recovered": "{:,.0f}",
        "Deaths": "{:,.0f}",
        "Recovery Rate": "{:.2f}%",
        "Death Rate": "{:.2f}%"
    })
    
    st.dataframe(df_latest_styled, use_container_width=True)
    
    st.markdown("#### Data Visualization by Province")
    # Bar Chart
    fig_bar = px.bar(
        df_latest,
        x="Province",
        y="Confirmed",
        title="Confirmed Cases by Province",
        color="Confirmed"
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Pie Chart
    fig_pie = px.pie(
        df_latest,
        values="Confirmed",
        names="Province",
        title="Proportion of Cases by Province"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

except FileNotFoundError:
    st.error("File 'covid_19_indonesia_time_series_all.csv' not found. Please ensure the file is located correctly.")
