import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Campaign vs University Report", layout="wide")
st.title("📊 Campaign vs University Lead Report")

DATA_FILENAME = "data.csv" 

# Added ttl=60 so the cache refreshes automatically when you upload new data!
@st.cache_data(ttl=60)
def load_data(filename):
    if not os.path.exists(filename):
        return None
    df = pd.read_csv(filename)
    df['CreatedOn'] = pd.to_datetime(df['CreatedOn'])
    return df

df = load_data(DATA_FILENAME)

if df is not None:
    st.sidebar.header("Filters")
    
    # 1. Lead Source Filter (NEW: Multi-Select)
    lead_sources = sorted(df['LeadSource'].dropna().unique().tolist())
    selected_sources = st.sidebar.multiselect(
        "Lead Source:", 
        options=lead_sources,
        default=lead_sources # Selects all by default
    )
    
    # 2. University Filter (Multi-Select)
    universities = sorted(df['University'].dropna().unique().tolist())
    selected_universities = st.sidebar.multiselect(
        "University:", 
        options=universities, 
        default=universities
    )
    
    # Date Filters
    min_date = df['CreatedOn'].min().date()
    max_date = df['CreatedOn'].max().date()
    
    start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    
    # --- SAFETY CHECK: Make sure boxes aren't empty BEFORE filtering ---
    if not selected_sources:
        st.warning("👈 Please select at least one **Lead Source** from the sidebar.")
    elif not selected_universities:
        st.warning("👈 Please select at least one **University** from the sidebar.")
    else:
        # --- Apply Filters ---
        filtered_df = df.copy()
        
        # Apply Lead Source Filter (Now uses .isin because it's a list)
        filtered_df = filtered_df[filtered_df['LeadSource'].isin(selected_sources)]
            
        # Apply University Filter
        filtered_df = filtered_df[filtered_df['University'].isin(selected_universities)]
            
        # Apply Date Filter
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
            st.write(f"### Showing results for selected filters ({start_date} to {end_date})")
            st.dataframe(styled_table, use_container_width=True)
            
else:
    st.error(f"⚠️ Could not find '{DATA_FILENAME}'. Please make sure you uploaded the CSV file to GitHub!")