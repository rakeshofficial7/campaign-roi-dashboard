import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Campaign vs University Report", layout="wide")
st.title("📊 Campaign vs University Lead Report")

# 1. We tell the app to look for a file named exactly "data.csv"
DATA_FILENAME = "data.csv" 

@st.cache_data
def load_data(filename):
    if not os.path.exists(filename):
        return None
    df = pd.read_csv(filename)
    df['CreatedOn'] = pd.to_datetime(df['CreatedOn'])
    return df

# 2. Automatically load the data behind the scenes
df = load_data(DATA_FILENAME)

if df is not None:
    st.sidebar.header("Filters")
    
    # Lead Source Filter (Single Dropdown)
    lead_sources = ['All'] + sorted(df['LeadSource'].dropna().unique().tolist())
    selected_source = st.sidebar.selectbox("Lead Source:", lead_sources)
    
    # NEW: University Filter (Multi-Select)
    universities = sorted(df['University'].dropna().unique().tolist())
    selected_universities = st.sidebar.multiselect(
        "University:", 
        options=universities, 
        default=universities  # This makes all universities selected by default
    )
    
    # Date Filters
    min_date = df['CreatedOn'].min().date()
    max_date = df['CreatedOn'].max().date()
    
    start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    
    # --- Apply Filters ---
    filtered_df = df.copy()
    
    # 1. Apply Lead Source Filter
    if selected_source != 'All':
        filtered_df = filtered_df[filtered_df['LeadSource'] == selected_source]
        
    # 2. Apply New University Filter
    if selected_universities:
        # Keep rows where the University is IN the list of selected universities
        filtered_df = filtered_df[filtered_df['University'].isin(selected_universities)]
    else:
        # If the user clears the entire box (deselects all), empty the dataframe
        filtered_df = pd.DataFrame(columns=filtered_df.columns)
        
    # 3. Apply Date Filter
    filtered_df = filtered_df[
        (filtered_df['CreatedOn'].dt.date >= start_date) & 
        (filtered_df['CreatedOn'].dt.date <= end_date)
    ]
    
    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:
        # Create the Pivot Table
        pivot_table = pd.pivot_table(
            filtered_df, 
            index='Campaign', 
            columns='University', 
            values='LeadSource', 
            aggfunc='count', 
            fill_value=0,
            margins=True,           
            margins_name='Total'    
        )
        
        # Apply Styling
        idx = pd.IndexSlice
        styled_table = pivot_table.style\
            .background_gradient(
                cmap='Blues', 
                subset=idx[pivot_table.index[:-1], pivot_table.columns[:-1]]
            )\
            .format("{:.0f}")
        
        # Display the table
        st.write(f"### Showing results for: **{selected_source}** ({start_date} to {end_date})")
        st.dataframe(styled_table, use_container_width=True)
        
else:
    # If it can't find the file, it will show this error
    st.error(f"⚠️ Could not find '{DATA_FILENAME}'. Please make sure you uploaded the CSV file to GitHub!")