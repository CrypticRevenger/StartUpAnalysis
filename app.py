import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt

st.set_page_config(layout='wide',page_title='StartUp Analysis')

df = pd.read_csv('Startup_cleaned.csv')
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

    # load the recent 5 investments
    last5df = df[df['Investors'].str.contains(investor)].head()[['Date','StartUp','Vertical','Location','Round','Amount']]
    st.subheader("Most Recent Investments")
    st.dataframe(last5df)


    col1,col2 = st.columns(2)
    with col1:
        # Biggest investments
        big_series = df[df['Investors'].str.contains(investor)].groupby('StartUp')['Amount'].sum().sort_values(ascending=False).head()
        st.subheader("Biggest Investments")
        fig, ax = plt.subplots()
        ax.bar(big_series.index,big_series.values)
        st.pyplot(fig)

    with col2:
        vertical_series = df[df['Investors'].str.contains(investor)].groupby('Vertical')['Amount'].sum()
        st.subheader("Sectors Investments In")
        fig1, ax1 = plt.subplots()
        ax1.pie(vertical_series,labels=vertical_series.index,autopct="%0.01f%%")
        st.pyplot(fig1)

    col3,col4 = st.columns(2)
    with col3:
        round_series = df[df['Investors'].str.contains(investor)].groupby('Round')['Amount'].sum()
        st.subheader("Stage Investments In")
        fig2, ax2 = plt.subplots()
        ax2.pie(round_series,labels=round_series.index,autopct="%0.01f%%")
        st.pyplot(fig2)
    with col4:
        city_series = df[df['Investors'].str.contains(investor)].groupby('Location')['Amount'].sum()
        st.subheader("Location in which they Investments In")
        fig3, ax3 = plt.subplots()
        ax3.pie(city_series,labels=city_series.index,autopct="%0.01f%%")
        st.pyplot(fig3)
    df['year'] = df['Date'].dt.year
    year_series = df[df['Investors'].str.contains(investor)].groupby('year')['Amount'].sum()
    st.subheader("Year On Year Investment")
    fig4, ax4 = plt.subplots()
    ax4.plot(year_series.index,year_series.values)
    st.pyplot(fig4)

st.sidebar.title('StartUp Funding Analysis')

st.session_state.option = st.sidebar.selectbox("Select One", ['Overall Analysis','StartUp','Investor'],key='analysis')

option = st.session_state.option

if option == 'Overall Analysis':
        load_overall_analysis()
elif option == 'StartUp':
    st.sidebar.selectbox("Select StartUp", sorted(df['StartUp'].dropna().unique().tolist()))
    btn1 = st.sidebar.button("Find StartUp Details")
    st.title('StartUp Analysis')
else:
    selected_investor = st.sidebar.selectbox("Select Investor",sorted(set(df['Investors'].str.split(',').sum())))
    btn2 = st.sidebar.button("Find Investor Details")
    if btn2:
        load_investors(selected_investor)