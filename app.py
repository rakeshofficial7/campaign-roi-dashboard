import streamlit as st
import pandas as pd

# Set up the web page layout
st.set_page_config(page_title="Campaign vs University Report", layout="wide")
st.title("📊 Campaign vs University Lead Report")

# Create a sidebar for inputs
st.sidebar.header("1. Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Cache the data so it doesn't reload on every single click
    @st.cache_data
    def load_data(file):
        df = pd.read_csv(file)
        df['CreatedOn'] = pd.to_datetime(df['CreatedOn'])
        return df

    try:
        df = load_data(uploaded_file)
        
        st.sidebar.header("2. Filters")
        
        # Lead Source Filter
        lead_sources = ['All'] + sorted(df['LeadSource'].dropna().unique().tolist())
        selected_source = st.sidebar.selectbox("Lead Source:", lead_sources)
        
        # Date Filters
        min_date = df['CreatedOn'].min().date()
        max_date = df['CreatedOn'].max().date()
        
        start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
        end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
        
        # Apply Filters
        filtered_df = df.copy()
        if selected_source != 'All':
            filtered_df = filtered_df[filtered_df['LeadSource'] == selected_source]
            
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
            
            # Display the table on the webpage
            st.write(f"### Showing results for: **{selected_source}** ({start_date} to {end_date})")
            st.dataframe(styled_table, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error processing the file. Please check your CSV format. Details: {e}")
else:
    st.info("👈 Please upload your Campaign CSV file in the sidebar to generate the report.")