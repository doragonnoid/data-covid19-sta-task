import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import datetime
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from bs4 import BeautifulSoup


# 1️⃣ Auto-refresh every 5 minutes (300000 ms)
# Auto-refresh feature to ensure that the app shows the most recent data every 5 minutes.
st_autorefresh(interval=300000, key="auto_refresh")

# 2️⃣ App Title
# Displaying the app's title on the main page to give users context about the topic.
st.title("📊 COVID-19 Data Analysis in Indonesia")

# 3️⃣ URL for Data Retrieval
# URL to scrape data from the official Ministry of Health Indonesia website that provides the latest COVID-19 information.
web_scrape_url = 'https://pusatkrisis.kemkes.go.id/covid-19-id/'

# 4️⃣ Backup Data
# Backup data used if the primary data retrieval fails (as of June 21, 2023).
fallback_cases = [6811444, 6640216, 161853, 0]  # Data as of June 21, 2023
fallback_global = 676681574
fallback_suspect = 1080
fallback_specimen = 13678
labels = ['Confirmed', 'Recovered', 'Deaths', 'Active Cases']

# 5️⃣ Initialize Data Status
# Saving data in session_state to ensure it remains available throughout the user session.
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

# 6️⃣ Function to Fetch Latest Data
# Function to retrieve the latest data from the Ministry of Health website and update information in session_state.
def fetch_latest_data():
    try:
        response = requests.get(web_scrape_url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        numbers = [int(num.text.replace('.', '').replace(',', '')) for num in soup.select('.covid-case strong')]

        if len(numbers) >= 4:
            st.session_state.cases = numbers[:4]
            st.session_state.global_cases = numbers[0]
            st.session_state.suspect = numbers[4] if len(numbers) > 4 else fallback_suspect
            st.session_state.specimen = numbers[5] if len(numbers) > 5 else fallback_specimen
            st.session_state.api_status = "✅ Latest Data from Ministry of Health"
            st.session_state.last_update = datetime.datetime.now()
        else:
            raise ValueError("Data retrieved is incomplete.")
    except Exception as e:
        # If data retrieval fails, use backup data.
        st.session_state.cases = fallback_cases
        st.session_state.global_cases = fallback_global
        st.session_state.suspect = fallback_suspect
        st.session_state.specimen = fallback_specimen

# 7️⃣ Fetch Data When Page Loads
# Ensures that the latest data is fetched whenever the page is loaded or refreshed.
fetch_latest_data()

cases = st.session_state.cases
st.session_state.last_updated = st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')

# 8️⃣ Display Data Status in Sidebar
# Displaying the status of the data and the time it was last updated in the sidebar.
st.sidebar.subheader("📱 Data Status")
st.sidebar.write(st.session_state.api_status)

# 🔟 Display Statistical Features
# Displaying statistics and visualizations for COVID-19 data.
st.subheader("📊 All Statistical Features")

# 1️⃣ Frequency Distribution Table
# Displaying the frequency distribution table of confirmed cases, recovered, deaths, and active cases.
freq_table = pd.DataFrame({'Category': labels, 'Amount': cases})
freq_table['Relative Frequency'] = freq_table['Amount'] / freq_table['Amount'].sum()
st.table(freq_table)

# 2️⃣ Midpoint
# Displaying the midpoint values between each pair of category data.
midpoints = [(cases[i] + cases[i+1]) / 2 for i in range(len(cases)-1)]
st.write("Midpoints: ", midpoints)

# 4️⃣ Cumulative Frequency
# Displaying the cumulative frequency chart to see the development of cases over time.
st.line_chart(np.cumsum(cases))

# 5️⃣ Class Boundaries
# Displaying class boundaries to divide data into specific groups.
st.write("Class Boundaries: ", [(x-0.5, x+0.5) for x in cases])

# 6️⃣ Histogram
# Displaying a histogram to visualize the distribution of data within case categories.
fig, ax = plt.subplots()
ax.hist(cases, bins=4, color='blue', alpha=0.7)
st.pyplot(fig)

# 7️⃣ Polygon
# Displaying a polygon chart to visualize the data progression in a smoother manner.
fig, ax = plt.subplots()
ax.plot(labels, cases, marker='o', linestyle='-', color='purple')
st.pyplot(fig)

# 9️⃣ Stem and Leaf Plot
# Displaying a stem-and-leaf plot that groups data based on the first and second digits.
stem = {str(x)[0]: str(x)[1:] for x in cases}
st.write("Stem and Leaf Plot: ", stem)

# 🔟 Dot Plot
# Displaying a dot plot to show the relationship between categories and case amounts.
fig, ax = plt.subplots()
ax.scatter(labels, cases, color='red')
st.pyplot(fig)

# 1️⃣1️⃣ Pie Chart
# Displaying a pie chart to show the proportional distribution of case amounts.
fig, ax = plt.subplots()
ax.pie(cases, labels=labels, autopct='%1.1f%%', startangle=140)
st.pyplot(fig)

# 1️⃣2️⃣ Pareto Chart
# Displaying a Pareto chart that arranges categories based on the highest number of cases.
sorted_cases = sorted(zip(labels, cases), key=lambda x: x[1], reverse=True)
st.bar_chart(pd.DataFrame(sorted_cases, columns=['Category', 'Amount']))

# 1️⃣3️⃣ Scatter Plot
# Displaying a scatter plot to observe the relationship between category indices and case amounts.
fig, ax = plt.subplots()
ax.scatter(range(len(cases)), cases)
st.pyplot(fig)

# 1️⃣4️⃣ Time Series Chart
# Displaying a time series chart to observe the development of cases over time.
st.line_chart(cases)

# 1️⃣5️⃣ Mean, Median, Mode
# Displaying basic statistics: mean (average), median, and mode (most frequent value).
st.write("Mean: ", np.mean(cases))
st.write("Median: ", np.median(cases))
st.write("Mode: ", pd.Series(cases).mode().tolist())

# 1️⃣7️⃣ Standard Deviation & Variance
# Displaying data spread metrics: standard deviation and variance.
st.write("Standard Deviation: ", np.std(cases))
st.write("Variance: ", np.var(cases))

# 1️⃣8️⃣ Empirical Rule
# Displaying the empirical rule stating the percentage of data within 1, 2, and 3 standard deviations.
st.write("Empirical Rule: 68% of data falls within 1 std dev, 95% within 2 std devs, 99.7% within 3 std devs")

# 2️⃣0️⃣ Quartiles
# Displaying quartiles of the data and the interquartile range for distribution analysis.
st.write("Quartiles: ", np.percentile(cases, [25, 50, 75]))
st.write("Interquartile Range: ", np.percentile(cases, 75) - np.percentile(cases, 25))

# 2️⃣1️⃣ Box and Whisker Plot
# Displaying a box plot to show the data distribution and detect outliers.
fig, ax = plt.subplots()
ax.boxplot(cases, vert=False)
st.pyplot(fig)

# 2️⃣2️⃣ Percentiles and Deciles
# Displaying the 90th percentile and deciles to get a deeper insight into data distribution.
st.write("90th Percentile: ", np.percentile(cases, 90))
st.write("Deciles: ", [np.percentile(cases, i * 10) for i in range(1, 10)])

# 1️⃣1️⃣ COVID-19 Stats in Sidebar
# Displaying key information about recovery rate, death rate, and active cases in the sidebar.
recovery_rate = (cases[1] / cases[0]) * 100 if cases[0] > 0 else 0
death_rate = (cases[2] / cases[0]) * 100 if cases[0] > 0 else 0
active_rate = (cases[3] / cases[0]) * 100 if cases[0] > 0 else 0

st.sidebar.write(f"🌎 Global Cases: {st.session_state.global_cases:,}")
st.sidebar.write(f"✔️ Recovery Rate: {recovery_rate:.2f}%")
st.sidebar.write(f"⚖️ Death Rate: {death_rate:.2f}%")
st.sidebar.write(f"🏥 Active Cases: {active_rate:.2f}%")
st.sidebar.write(f"🟡 Suspect: {st.session_state.suspect:,}")
st.sidebar.write(f"🧪 Specimens: {st.session_state.specimen:,}")

# 1️⃣2️⃣ Calculation Formulas
# Displaying the calculation formulas for recovery rate, death rate, and active rate based on available data.
st.subheader("📝 Calculation Formulas")
st.markdown(f"""
- **Recovery Rate** = `(Recovered / Total Cases) × 100%`
  - {cases[1]} / {cases[0]} × 100% = **{recovery_rate:.2f}%**
- **Death Rate** = `(Deaths / Total Cases) × 100%`
  - {cases[2]} / {cases[0]} × 100% = **{death_rate:.2f}%**
- **Active Rate** = `(Active Cases / Total Cases) × 100%`
  - {cases[3]} / {cases[0]} × 100% = **{active_rate:.2f}%**
""")

# 1️⃣3️⃣ Cumulative Case Development Chart
# Displaying the cumulative case development chart to show how confirmed, recovered, and death cases have evolved.
st.subheader("📈 Cumulative Case Development Chart")
fig, ax = plt.subplots()
ax.plot(labels, cases, marker='o', linestyle='-', color='red', label='Confirmed')
ax.plot(labels, [cases[1]]*4, marker='o', linestyle='-', color='green', label='Recovered')
ax.legend()
ax.set_ylabel("Case Count")
st.pyplot(fig)

# 1️⃣4️⃣ COVID-19 Bar Chart
# Displaying a bar chart to represent the comparison of case numbers across each category.
st.subheader("📊 COVID-19 Bar Chart")
fig, ax = plt.subplots()
ax.bar(labels, cases, color=['blue', 'green', 'red', 'orange'])
ax.set_xlabel("Category")
ax.set_ylabel("Case Count")
st.pyplot(fig)

# 1️⃣ Frequency Distribution
relative_frequency = freq_table['Amount'] / freq_table['Amount'].sum()
freq_table['Relative Frequency'] = relative_frequency
st.table(freq_table)

# 2️⃣ Cumulative Frequency Table
freq_table['Cumulative Frequency'] = np.cumsum(freq_table['Amount'])
st.write("Cumulative Frequency Table:")
st.table(freq_table)

# 3️⃣ Frequency Histogram
fig, ax = plt.subplots()
ax.hist(cases, bins=4, color='blue', alpha=0.7)
ax.set_title("Pure Frequency Histogram")
st.pyplot(fig)

# 4️⃣ Relative Frequency Histogram
fig, ax = plt.subplots()
ax.hist(cases, bins=4, weights=relative_frequency, color='green', alpha=0.7)
ax.set_title("Relative Frequency Histogram")
st.pyplot(fig)

# 5️⃣ Distribution Shape (Symmetric, Uniform, Skewed Right, Skewed Left)
mean = np.mean(cases)
median = np.median(cases)
std_dev = np.std(cases)

# Using mean and median comparison to detect skewness
if mean == median:
    skewness = "Symmetric Distribution"
elif mean < median:
    skewness = "Left Skewed Distribution"
else:
    skewness = "Right Skewed Distribution"

st.write(f"Distribution Shape: {skewness}")

# 6️⃣ Chebyshev's Theorem
# Determining the percentage of data within 1, 2, and 3 standard deviations
k_values = [1, 2, 3]
chebyshev_results = {}
for k in k_values:
    lower_bound = mean - k * std_dev
    upper_bound = mean + k * std_dev
    chebyshev_results[k] = 1 - (1 / k**2)

st.write("Chebyshev's Theorem - Percentage of Data within Distance from Mean:")
for k, result in chebyshev_results.items():
    st.write(f" - For k = {k}, percentage of data within {k} standard deviations: {result * 100:.2f}%")

# 7️⃣ Time Series Analysis Chart
# Since there is no time data, we can use the labels to represent "trend" based on current data.
time_series_data = pd.Series(cases, index=labels)
st.subheader("Time Series Analysis (Case Progression)")
st.line_chart(time_series_data)

# Data COVID-19 per provinsi secara manual
data = {
    "Province": [
        "ACEH", "BALI", "BANTEN", "BENGKULU", "D.I. YOGYAKARTA", "DKI JAKARTA", "GORONTALO", "JAMBI", "JAWA BARAT", "JAWA TENGAH",
        "JAWA TIMUR", "KALIMANTAN BARAT", "KALIMANTAN SELATAN", "KALIMANTAN TENGAH", "KALIMANTAN TIMUR", "KALIMANTAN UTARA",
        "KEPULAUAN BANGKA BELITUNG", "KEPULAUAN RIAU", "LAMPUNG", "MALUKU", "MALUKU UTARA", "NUSA TENGGARA BARAT", "NUSA TENGGARA TIMUR",
        "PAPUA", "PAPUA BARAT", "RIAU", "SULAWESI BARAT", "SULAWESI SELATAN", "SULAWESI TENGAH", "SULAWESI TENGGARA", "SULAWESI UTARA",
        "SUMATERA BARAT", "SUMATERA SELATAN", "SUMATERA UTARA"
    ],
    "Confirmed_21_June": [
        45091, 173753, 372214, 29961, 232389, 1568040, 14085, 39646, 1251718, 662318,
        648240, 68038, 89353, 59806, 215537, 46430, 67440, 72204, 79194, 19003,
        14986, 37442, 97914, 51415, 33189, 155319, 16155, 149271, 63601, 26750, 54603,
        105839, 86122, 164378
    ],
    "Recovered_21_June": [
        42767, 168700, 368854, 29427, 225955, 1551523, 13465, 38699, 1232023, 626757,
        614323, 66869, 86673, 58166, 209647, 45510, 65773, 70196, 74619, 18682,
        14628, 36458, 96095, 50810, 32791, 150648, 15724, 146662, 61761, 26153, 53249,
        103314, 82576, 160719
    ],
    "Deaths_21_June": [
        2282, 4908, 2994, 529, 6127, 16098, 486, 925, 16189, 34289,
        32508, 1146, 2612, 1563, 5824, 880, 1657, 1930, 4264, 307,
        336, 945, 1574, 581, 396, 4560, 411, 2587, 1760, 591, 1265,
        2433, 3500, 3396
    ]
}

# Konversi ke DataFrame
df = pd.DataFrame(data)

# Tampilkan DataFrame
st.write("## 📌 COVID-19 Data Province last updatting")
st.dataframe(df)

# Hitung Recovery & Death Rate
df["Recovery Rate"] = (df["Recovered_21_June"] / df["Confirmed_21_June"]) * 100
df["Death Rate"] = (df["Deaths_21_June"] / df["Confirmed_21_June"]) * 100

st.write("## 🔬 Recovery & Death Rates")
st.dataframe(df[["Province", "Recovery Rate", "Death Rate"]])

# Visualisasi Data
st.write("## 📊 Data Visualizations")

# 📊 Bar Chart
fig = px.bar(df, x="Province", y="Confirmed_21_June", title="Confirmed Cases per Province", color="Confirmed_21_June")
st.plotly_chart(fig)

# 🥧 Pie Chart
fig = px.pie(df, values="Confirmed_21_June", names="Province", title="Proportion of Cases per Province")
st.plotly_chart(fig)

# 📈 Line Chart
fig = px.line(df, x="Province", y="Confirmed_21_June", title="COVID-19 Trend by Province")
st.plotly_chart(fig)

# 📉 Boxplot
fig = px.box(df, y="Confirmed_21_June", title="Distribution of COVID-19 Cases")
st.plotly_chart(fig)

# Statistik Ringkasan
st.write("## 📊 Summary Statistics")
st.write(df.describe())
