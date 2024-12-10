import streamlit as st
import pandas as pd
import plotly.express as px

file_path = "fiscal_year_revenue.csv"
data = pd.read_csv(file_path)

data['State'] = data['State'].fillna('Unknown')
data['County'] = data['County'].fillna('Unknown')
data['Product'] = data['Product'].fillna('Not Specified')

data_with_unknowns = data.copy()
data_without_unknowns = data[
    (data['State'] != 'Unknown') & 
    (data['County'] != 'Unknown') & 
    (data['Product'] != 'Not Specified')
]

st.title("Natural Resources Revenue Dashboard")

st.sidebar.header("Filters")
years = st.sidebar.slider(
    "Select Year Range", 
    int(data['Fiscal Year'].min()), 
    int(data['Fiscal Year'].max()), 
    (2010, 2020)
)

revenue_range = st.sidebar.slider(
    "Select Revenue Range (in $)", 
    float(data['Revenue'].min()), 
    float(data['Revenue'].max()), 
    (float(data['Revenue'].min()), float(data['Revenue'].max()))
)

land_class = st.sidebar.multiselect(
    "Select Land Class", 
    data['Land Class'].unique(), 
    default=data['Land Class'].unique()
)

revenue_type = st.sidebar.multiselect(
    "Select Revenue Type", 
    data['Revenue Type'].unique(), 
    default=data['Revenue Type'].unique()
)

commodity = st.sidebar.multiselect(
    "Select Commodity", 
    data['Commodity'].unique(), 
    default=data['Commodity'].unique()
)

filtered_with_unknowns = data_with_unknowns[
    (data_with_unknowns['Fiscal Year'] >= years[0]) & 
    (data_with_unknowns['Fiscal Year'] <= years[1]) &
    (data_with_unknowns['Revenue'] >= revenue_range[0]) & 
    (data_with_unknowns['Revenue'] <= revenue_range[1]) &
    (data_with_unknowns['Land Class'].isin(land_class)) & 
    (data_with_unknowns['Revenue Type'].isin(revenue_type)) & 
    (data_with_unknowns['Commodity'].isin(commodity))
]

filtered_without_unknowns = data_without_unknowns[
    (data_without_unknowns['Fiscal Year'] >= years[0]) & 
    (data_without_unknowns['Fiscal Year'] <= years[1]) &
    (data_without_unknowns['Revenue'] >= revenue_range[0]) & 
    (data_without_unknowns['Revenue'] <= revenue_range[1]) &
    (data_without_unknowns['Land Class'].isin(land_class)) & 
    (data_without_unknowns['Revenue Type'].isin(revenue_type)) & 
    (data_without_unknowns['Commodity'].isin(commodity))
]

tab1, tab2, tab3 = st.tabs(["Project Overview", "With Unknowns", "Without Unknowns"])

with tab1:
    st.header("About This Project")
    st.markdown("""
    This dashboard provides insights into revenue data generated from natural resources on federal and Native American lands. 
    It aims to help users explore trends, breakdowns, and comparisons of revenue data across various dimensions like fiscal year, 
    land class, revenue type, and commodity.

    ### Key Features:
    - **Interactive Filtering**: Customize the view with sidebar filters.
    - **Visualizations**: Explore trends and breakdowns with dynamic charts.
    - **Data Exploration**: View the filtered dataset in a tabular format.

    ### Objectives:
    - Analyze revenue trends over time.
    - Identify revenue contributions by land class, commodity, and state.
    - Compare revenue from offshore and onshore activities.

    ### Technologies Used:
    - **Streamlit** for web app development.
    - **Plotly** for interactive visualizations.
    - **Pandas** for data manipulation.
    """)

def display_visualizations(dataset, title_suffix=""):
    st.subheader(f"Revenue Trends Over Time {title_suffix}")
    revenue_trend = dataset.groupby("Fiscal Year")["Revenue"].sum().reset_index()
    fig1 = px.line(revenue_trend, x="Fiscal Year", y="Revenue", title=f"Total Revenue by Year {title_suffix}")
    st.plotly_chart(fig1)

    st.subheader(f"Revenue Breakdown by Land Class {title_suffix}")
    land_class_revenue = dataset.groupby("Land Class")["Revenue"].sum().reset_index()
    fig2 = px.pie(land_class_revenue, values="Revenue", names="Land Class", title=f"Revenue by Land Class {title_suffix}")
    st.plotly_chart(fig2)

    st.subheader(f"Revenue by State {title_suffix}")
    state_revenue = dataset.groupby("State")["Revenue"].sum().reset_index()
    fig3 = px.bar(state_revenue, x="State", y="Revenue", title=f"Revenue by State {title_suffix}", labels={"Revenue": "Revenue ($)"})
    st.plotly_chart(fig3)

    st.subheader(f"Revenue by Commodity {title_suffix}")
    commodity_revenue = dataset.groupby("Commodity")["Revenue"].sum().reset_index()
    fig4 = px.bar(commodity_revenue, x="Commodity", y="Revenue", title=f"Revenue by Commodity {title_suffix}", labels={"Revenue": "Revenue ($)"})
    st.plotly_chart(fig4)

    st.subheader(f"Revenue Distribution by County (FIPS) {title_suffix}")
    fips_revenue = dataset.groupby("FIPS Code")["Revenue"].sum().reset_index()

    fips_revenue['FIPS Code'] = fips_revenue['FIPS Code'].apply(lambda x: f"{int(x):05}" if str(x).isdigit() else "Unknown")
    fips_revenue = fips_revenue[fips_revenue["FIPS Code"] != "Unknown"]

    fig_fips = px.choropleth(
        fips_revenue,
        geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
        locations="FIPS Code",
        color="Revenue",
        color_continuous_scale="Viridis",
        scope="usa",
        title=f"Revenue by County (FIPS) {title_suffix}",
    )
    fig_fips.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig_fips)

with tab2:
    st.header("Visualizations with Unknowns")
    display_visualizations(filtered_with_unknowns, title_suffix="(With Unknowns)")
    st.header("Filtered Data (With Unknowns)")
    st.dataframe(filtered_with_unknowns)

with tab3:
    st.header("Visualizations without Unknowns")
    display_visualizations(filtered_without_unknowns, title_suffix="(Without Unknowns)")
    st.header("Filtered Data (Without Unknowns)")
    st.dataframe(filtered_without_unknowns)
