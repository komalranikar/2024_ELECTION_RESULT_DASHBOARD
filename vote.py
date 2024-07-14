import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
candidates_df = pd.read_csv('candidates_with_phase.csv')
results_df = pd.read_csv('results_2024.csv')
winners_df = pd.read_csv('results_2024_winners.csv')

# Merge datasets
merged_df1 = results_df.merge(candidates_df, 
                             left_on=['State', 'PC No', 'Candidate', 'Party'], 
                             right_on=['State', 'Constituency_No', 'Candidate Name', 'Party'])

merged_df = merged_df1.merge(winners_df, 
                             left_on=['State', 'PC No'], 
                             right_on=['State', 'PC No'])

# Selecting and renaming necessary columns to avoid confusion
merged_df = merged_df.rename(columns={
    'PC Name_x': 'PC Name',
    'Party_x': 'Party',
    'Total Votes': 'Total Votes'
})

# Convert 'Total Votes' to numeric, forcing errors to NaN, then fill NaNs with 0
merged_df['Total Votes'] = pd.to_numeric(merged_df['Total Votes'], errors='coerce').fillna(0)

# Streamlit app layout with sidebar
st.set_page_config(page_title='2024 Election Results Dashboard', layout='wide', initial_sidebar_state='expanded')

# Apply CSS styles to improve the visual appearance
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    .reportview-container {
        background: #e0e4e7;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: black;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar content
st.sidebar.title('2024 Election Results Dashboard')
st.sidebar.markdown('Explore the 2024 election results by state, constituency, party, and more.')

# Filters
states = merged_df['State'].unique()
selected_state = st.sidebar.selectbox('Select State', states)

filtered_df = merged_df[merged_df['State'] == selected_state]

# Additional Filters with Select All Option
parties = filtered_df['Party'].unique()
parties = ['Select All'] + list(parties)
selected_party = st.sidebar.multiselect('Select Party', parties, default='Select All')

if 'Select All' in selected_party:
    selected_party = filtered_df['Party'].unique()

candidates = filtered_df['Candidate Name'].unique()
candidates = ['Select All'] + list(candidates)
selected_candidate = st.sidebar.multiselect('Select Candidate', candidates, default='Select All')

if 'Select All' in selected_candidate:
    selected_candidate = filtered_df['Candidate Name'].unique()

filtered_df = filtered_df[
    (filtered_df['Party'].isin(selected_party)) &
    (filtered_df['Candidate Name'].isin(selected_candidate))
]

# Constituency-wise results
st.header('Constituency-wise Election Results')
st.markdown("#### Visualize the election results for each constituency within the selected state.")
if not filtered_df.empty:
    fig = px.bar(filtered_df, x='PC Name', y='Total Votes', color='Party', barmode='group',
                 hover_data=['Candidate Name', 'Gender', 'Age', 'Application Status'])
    st.plotly_chart(fig)
else:
    st.write("No data available for the selected filters.")

# Party performance
st.header('Party Performance Analysis')
st.markdown("#### Analyze the performance of each party based on total votes.")
if not filtered_df.empty:
    # Aggregate votes by party
    party_performance = filtered_df.groupby('Party')['Total Votes'].sum().reset_index()

    # Ensure there are no zero or missing values
    party_performance = party_performance[party_performance['Total Votes'] > 0]

    if not party_performance.empty:
        fig = px.pie(party_performance, values='Total Votes', names='Party', title='Party Performance')
        st.plotly_chart(fig)
    else:
        st.write("No votes recorded for parties in the selected filters.")
else:
    st.write("No data available for party performance in the selected filters.")

# Winning margin distribution
st.header('Winning Margin Distribution')
st.markdown("#### Explore the distribution of winning margins.")
if 'Margin Votes' in filtered_df.columns and not filtered_df['Margin Votes'].isnull().all():
    fig = px.histogram(filtered_df, x='Margin Votes', nbins=20, title='Distribution of Winning Margins')
    st.plotly_chart(fig)
else:
    st.write("No data available for winning margin distribution in the selected filters.")

# Voter turnout analysis
st.header('Voter Turnout Analysis')
st.markdown("#### Analyze voter turnout by constituency.")
if not filtered_df.empty:
    voter_turnout = filtered_df.groupby('PC Name')['Total Votes'].sum().reset_index()
    fig = px.bar(voter_turnout, x='PC Name', y='Total Votes', title='Voter Turnout by Constituency')
    st.plotly_chart(fig)
else:
    st.write("No data available for voter turnout analysis.")

# Winning candidate profile
st.header('Winning Candidate Profile')
st.markdown("#### View the profile of winning candidates.")
if not filtered_df.empty:
    winning_candidates = winners_df[['Winning Candidate', 'Winning Party', 'State', 'Margin Votes']].drop_duplicates()
    st.write(winning_candidates)
else:
    st.write("No data available for winning candidate profiles.")

# State-wise summary
st.header('State-wise Summary')
st.markdown("#### Get a summary of election results by state.")
if not filtered_df.empty:
    state_summary = filtered_df.groupby(['State', 'Party'])['Total Votes'].sum().reset_index()
    fig = px.treemap(state_summary, path=['State', 'Party'], values='Total Votes', title='State-wise Summary of Results')
    st.plotly_chart(fig)
else:
    st.write("No data available for state-wise summary.")

# Search functionality
st.sidebar.header('Search')
search_candidate = st.sidebar.text_input('Search for a candidate or constituency')
search_results = merged_df[merged_df.apply(lambda row: search_candidate.lower() in row.astype(str).str.lower().to_list(), axis=1)]

if not search_results.empty:
    st.write(search_results)
else:
    st.write("No results found.")