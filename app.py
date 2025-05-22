import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt

st.set_page_config(layout='wide',page_title='StartUp Analysis')

df = pd.read_csv('Startup_cleaned_1.csv')
df['Date'] = pd.to_datetime(df['Date'],errors='coerce')
df['month'] = df['Date'].dt.month
df['year'] = df['Date'].dt.year

COMMON_SUFFIXES = [
    'brands', 'labs', 'solutions', 'ventures', 'technologies',
    'tech', 'pvt ltd', 'private limited', 'inc', 'llp'
]

def remove_suffixes(name):
    for suffix in COMMON_SUFFIXES:
        name = re.sub(rf'\b{suffix}\b', '', name)
    return name

# Cleaning function
def clean_name(name):
    if pd.isnull(name):
        return None

    name = str(name).lower()

    # Remove entries with backslashes
    if '\\' in name:
        return None

    # Remove domains
    name = re.sub(r'\.com|\.in|\.org|\.net|\.co', '', name)

    # Remove quotes and special characters
    name = re.sub(r"[\"']", '', name)
    name = re.sub(r'[^a-z0-9 ]', '', name)

    # Remove common suffixes
    name = remove_suffixes(name)

    # Normalize whitespace
    name = ' '.join(name.split())

    return name

# Data Cleaning
df['StartUp'] = df['StartUp'].apply(clean_name)
df['Investors'] = df['Investors'].apply(clean_name)


def load_overall_analysis():
    st.title("Overall Analysis")

    # Total invested amount
    total = round(df['Amount'].sum())
    # Max invested
    maxi = df.groupby('StartUp')['Amount'].max().sort_values(ascending=False).head(1).values[0]
    # Avg tickect size
    avg_ticket = df.groupby('StartUp')['Amount'].sum().mean()
    # Total funded Startup
    num_startup = df['StartUp'].nunique()

    col1,col2,col3,col4 = st.columns(4)
    with col1:
        st.metric("Total Invested",str(total)  + " Cr")
    with col2:
        st.metric("Maximum Invested",str(maxi)  + " Cr")
    with col3:
        st.metric("Average Ticket Size",str(round(avg_ticket)) + " Cr")
    with col4:
        st.metric("Funded StartUp",num_startup)

    st.header('Month On Month graph')
    selected_option = st.selectbox('Select Type',['Total','Count'])
    if selected_option == 'Total':
        temp_df = df.groupby(['year', 'month'])['Amount'].sum().reset_index()
    else:
        temp_df = df.groupby(['year', 'month'])['Amount'].count().reset_index()

    temp_df['x_axis'] = temp_df['month'].astype('str') + '-' + temp_df['year'].astype('str')

    fig3, ax3 = plt.subplots()
    ax3.plot(temp_df['x_axis'], temp_df['Amount'])

    st.pyplot(fig3)
def load_investors(investor):
    st.title(investor)

    investor_df = df[df['Investors'].str.contains(investor, na=False)]

    last5df = investor_df.head()[['Date', 'StartUp', 'Vertical', 'Location', 'Round', 'Amount']]
    st.subheader("Most Recent Investments")
    if not last5df.empty:
        st.dataframe(last5df)
    else:
        st.warning("No recent investments found.")

    col1, col2 = st.columns(2)
    with col1:
        big_series = investor_df.groupby('StartUp')['Amount'].sum()
        big_series = big_series[big_series > 0].sort_values(ascending=False).head()
        st.subheader("Biggest Investments")
        if not big_series.empty:
            fig, ax = plt.subplots()
            ax.bar(big_series.index, big_series.values)
            st.pyplot(fig)
        else:
            st.warning("No data for biggest investments.")

    with col2:
        vertical_series = investor_df.groupby('Vertical')['Amount'].sum()
        vertical_series = vertical_series[vertical_series > 0]
        st.subheader("Sectors Investments In")
        if not vertical_series.empty:
            fig1, ax1 = plt.subplots()
            ax1.pie(vertical_series, labels=vertical_series.index, autopct="%0.01f%%")
            st.pyplot(fig1)
        else:
            st.warning("No valid (non-zero) sector investments to display.")

    col3, col4 = st.columns(2)
    with col3:
        round_series = investor_df.groupby('Round')['Amount'].sum()
        round_series = round_series[round_series > 0]
        st.subheader("Stage Investments In")
        if not round_series.empty:
            fig2, ax2 = plt.subplots()
            ax2.pie(round_series, labels=round_series.index, autopct="%0.01f%%")
            st.pyplot(fig2)
        else:
            st.warning("No valid (non-zero) round-wise investments.")

    with col4:
        city_series = investor_df.groupby('Location')['Amount'].sum()
        city_series = city_series[city_series > 0]
        st.subheader("Location in which they Investments In")
        if not city_series.empty:
            fig3, ax3 = plt.subplots()
            ax3.pie(city_series, labels=city_series.index, autopct="%0.01f%%")
            st.pyplot(fig3)
        else:
            st.warning("No valid (non-zero) location-wise investments.")

    if 'year' not in df.columns:
        df['year'] = df['Date'].dt.year

    year_series = investor_df.groupby('year')['Amount'].sum()
    year_series = year_series[year_series > 0]
    st.subheader("Year On Year Investment")
    if not year_series.empty:
        fig4, ax4 = plt.subplots()
        ax4.plot(year_series.index, year_series.values, marker='o')
        ax4.set_xlabel("Year")
        ax4.set_ylabel("Investment Amount")
        st.pyplot(fig4)
    else:
        st.warning("No valid (non-zero) year-wise investment data.")


def load_startup(startup):
    st.title(startup)

    col1,col2,col3 = st.columns(3)
    with col1:
        industry_series = df[df['StartUp'] == startup]['Vertical']
        if industry_series.empty:
            st.write(f"No industry info found for startup: {startup}")
        else:
            st.subheader("Industry")
            st.text(industry_series.iloc[0])
    with col2:
        sub_industry_series = df[df['StartUp'] == startup]['Subvertical']
        if industry_series.empty:
            st.write(f"No sub-industry info found for startup: {startup}")
        else:
            st.subheader("Sub-Industry")
            st.text(sub_industry_series.iloc[0])
    with col3:
        Location_series = df[df['StartUp'] == startup]['Location']
        if industry_series.empty:
            st.write(f"Location not found: {startup}")
        else:
            st.subheader("Location")
            st.text(Location_series.iloc[0])

    funding_df = df[df['StartUp'] == startup][['Round', 'Investors', 'Date']]

    st.subheader("Funding Rounds")
    if not funding_df.empty:
        st.table(funding_df)
    else:
        st.warning("No recent investments found.")



st.sidebar.title('StartUp Funding Analysis')

st.session_state.option = st.sidebar.selectbox("Select One", ['Overall Analysis','StartUp','Investor'],key='analysis')

option = st.session_state.option

if option == 'Overall Analysis':
        load_overall_analysis()
elif option == 'StartUp':
    selected_startup = st.sidebar.selectbox("Select StartUp", sorted(df['StartUp'].dropna().unique().tolist()))
    btn1 = st.sidebar.button("Find StartUp Details")
    if btn1:
        load_startup(selected_startup)
else:
    selected_investor = st.sidebar.selectbox("Select Investor",sorted(set(df['Investors'].str.split(',').sum())))
    btn2 = st.sidebar.button("Find Investor Details")
    if btn2:
        load_investors(selected_investor)