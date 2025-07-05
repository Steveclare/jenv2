import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging
import os

## SECTION: Configuration and Setup
## Purpose: Initialize Streamlit page and configure logging
st.set_page_config(
    page_title="Evolution Partners - Insurance Analytics",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(to right, #1e3c72, #2a5298);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 30px;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
        .stButton>button {
            width: 100%;
        }
        .chart-container {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .help-box {
            background-color: #e8f4f9;
            padding: 10px;
            border-radius: 5px;
            border-left: 5px solid #2196F3;
            margin: 10px 0;
        }
        .sidebar-logo {
            background-color: white;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .sidebar-logo h2 {
            color: #1e3c72;
            margin: 0;
            padding: 10px 0;
        }
        .upload-section {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='insurance_analysis.log'
)
logger = logging.getLogger(__name__)

## SECTION: Constants
## Purpose: Define carrier names and other constants
CARRIER_COLUMNS = [
    'AmTrust', 'Atlas', 'Attune', 'Bristol West', 'Chubb', 'CNA', 'Employers', 'Guard',
    'Hanover', 'Hartford', 'Hourly', 'ICW', 'KBIC', 'Kemper', 'Liberty Mutual',
    'Markel', 'Nationwide', 'Philadelphia', 'Preferred', 'Stillwater', 'Travelers', 'UFG', 'Other'
]

## SECTION: Data Loading
## Purpose: Load and cache the data
@st.cache_data
def process_excel_file(file_input):
    """Process Excel file and return DataFrame. Works with both file paths and uploaded files."""
    try:
        # Handle both string file paths and uploaded files
        if isinstance(file_input, str):
            xl = pd.ExcelFile(file_input)
        else:
            xl = pd.ExcelFile(file_input)
            
        # Print sheet names for debugging
        st.write(f"Found sheets: {xl.sheet_names}")
        
        all_data = []
        for sheet in xl.sheet_names:
            try:
                df = pd.read_excel(xl, sheet_name=sheet)
                df['Source_Sheet'] = sheet
                st.write(f"Processed sheet {sheet} with {len(df)} rows")
                all_data.append(df)
            except Exception as sheet_error:
                st.warning(f"Error processing sheet {sheet}: {str(sheet_error)}")
                continue
        
        # Combine all sheets
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            st.write(f"Combined {len(all_data)} sheets, total {len(combined_df)} rows")
            return combined_df
        return None
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return None

@st.cache_data
def process_data(df):
    """Process and clean the DataFrame"""
    try:
        # Convert date columns to datetime with better error handling
        date_columns = ['RCVD', 'EFF DATE', 'Effective Date']
        for col in date_columns:
            if col in df.columns:
                # First, ensure the column exists and has data
                if not df[col].empty:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    
                    # Handle invalid dates by setting them to a reasonable default
                    # For records with invalid dates, use the EFF DATE if available, or set to today
                    if col == 'RCVD' and df[col].isna().any():
                        # If RCVD is missing but EFF DATE exists, use EFF DATE
                        if 'EFF DATE' in df.columns and not df['EFF DATE'].empty:
                            mask = df[col].isna() & df['EFF DATE'].notna()
                            df.loc[mask, col] = df.loc[mask, 'EFF DATE']
                        
                        # For remaining invalid dates, set to a reasonable default (today)
                        remaining_invalid = df[col].isna()
                        if remaining_invalid.any():
                            df.loc[remaining_invalid, col] = pd.Timestamp.now()
                else:
                    # If column is empty, create with today's date
                    df[col] = pd.Timestamp.now()
        
        # Clean up and standardize LOB column
        df['LOB'] = df['LOB'].fillna('Unknown').astype(str)
        
        # Create standardization mapping for LOB values
        lob_mapping = {
            'bop': 'BOP/PKG', 'BOP': 'BOP/PKG', 'pkg': 'BOP/PKG',
            'PKG': 'BOP/PKG', 'Pkg': 'BOP/PKG', 'BOP/Pkg': 'BOP/PKG',
            'BOP/PKG': 'BOP/PKG', 'pkg/umb': 'BOP/PKG/UMB',
            'BOP / Umb': 'BOP/PKG/UMB', 'umb': 'UMB', 'Umb': 'UMB',
            'UMB': 'UMB', 'wc': 'WC', 'WC': 'WC', 'ba': 'BA', 'BA': 'BA'
        }
        
        # Apply standardization
        df['LOB'] = df['LOB'].apply(lambda x: lob_mapping.get(x.strip(), x.strip()))
        df.loc[df['LOB'] == 'nan', 'LOB'] = 'Unknown'
        
        # Standardize WC Class Code columns
        wc_code_columns = ['WC Class Code', 'Workers Comp Class Code', 'Work Comp Class']
        df['WC_Class_Code'] = None
        for col in wc_code_columns:
            if col in df.columns:
                mask = df['WC_Class_Code'].isnull() & df[col].notna()
                df.loc[mask, 'WC_Class_Code'] = df.loc[mask, col]
        
        # Clean up WC_Class_Code
        df['WC_Class_Code'] = df['WC_Class_Code'].fillna('Unknown')
        
        # Add month-year column for trending
        try:
            if 'RCVD' in df.columns and not df['RCVD'].empty:
                # Ensure RCVD is datetime before using .dt accessor
                df['RCVD'] = pd.to_datetime(df['RCVD'], errors='coerce')
                df['Month_Year'] = df['RCVD'].dt.to_period('M')
            else:
                df['Month_Year'] = pd.Period.now('M')
        except Exception as e:
            # Fallback: create Month_Year with current month
            df['Month_Year'] = pd.Period.now('M')
        
        return df
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return None

## SECTION: Analysis Functions
def analyze_carrier_responses(df):
    """Analyze carrier quote patterns"""
    results = {}
    for carrier in CARRIER_COLUMNS:
        if carrier in df.columns:
            quote_count = df[carrier].notna().sum()
            total_submissions = len(df)
            quote_percentage = (quote_count / total_submissions) * 100 if total_submissions > 0 else 0
            results[carrier] = {
                'total_quotes': quote_count,
                'quote_percentage': round(quote_percentage, 2),
                'total_submissions': total_submissions
            }
    return results

def analyze_lob_patterns(df):
    """Analyze patterns by Line of Business"""
    results = {}
    for lob in df['LOB'].unique():
        lob_data = df[df['LOB'] == lob]
        carrier_responses = {}
        for carrier in CARRIER_COLUMNS:
            if carrier in df.columns:
                quote_count = lob_data[carrier].notna().sum()
                if quote_count > 0:
                    carrier_responses[carrier] = quote_count
        results[lob] = {
            'total_submissions': len(lob_data),
            'carrier_responses': carrier_responses
        }
    return results

def analyze_wc_data(df):
    """Analyze Workers Compensation specific patterns"""
    if 'WC' not in df['LOB'].unique():
        return None
    
    wc_data = df[df['LOB'] == 'WC']
    
    results = {
        'total_wc_submissions': len(wc_data),
        'class_codes': wc_data['WC Class Code'].value_counts().to_dict() if 'WC Class Code' in wc_data.columns else {},
        'carrier_responses': {}
    }
    
    for carrier in CARRIER_COLUMNS:
        if carrier in df.columns:
            quote_count = wc_data[carrier].notna().sum()
            if quote_count > 0:
                results['carrier_responses'][carrier] = quote_count
    
    return results

def analyze_business_type(df, search_term):
    """Analyze submissions and quotes for specific business types"""
    # Search in all relevant columns
    search_cols = [
        'Desc of Ops', 'Description of Operations', 'Applicant', 
        'Description', 'Business Description', 'Notes',
        'Comments', 'Business Type'
    ]
    
    # Create mask for search term
    mask = pd.Series(False, index=df.index)
    for col in search_cols:
        if col in df.columns:
            # Support wildcards by replacing * with .* for regex
            search_pattern = search_term.replace('*', '.*')
            mask = mask | df[col].fillna('').astype(str).str.lower().str.contains(search_pattern.lower(), regex=True)
    
    # Filter data
    matched_data = df[mask]
    
    if len(matched_data) == 0:
        return None
    
    # Get all unique LOB patterns
    all_lobs = matched_data['LOB'].unique().tolist()
    
    # Get carrier quote information and bound information
    carrier_info = []
    for _, row in matched_data.iterrows():
        quotes = {}
        for carrier in CARRIER_COLUMNS:
            if carrier in row and pd.notna(row[carrier]):
                quotes[carrier] = row[carrier]
        
        # Check for bound status in Bound With column
        bound_info = ''
        if pd.notna(row.get('Bound With', '')):
            bound_carrier = str(row['Bound With']).strip()
            if bound_carrier:
                bound_info = f"Bound: {bound_carrier}"
        
        # If no bound info in Bound With, check Notes
        if not bound_info and 'Notes' in row and pd.notna(row['Notes']):
            notes = str(row['Notes']).lower()
            if 'bound' in notes:
                if 'lm' in notes or 'liberty mutual' in notes:
                    bound_info = 'Bound: Liberty Mutual'
                elif 'amtrust' in notes:
                    bound_info = 'Bound: AmTrust'
                else:
                    bound_info = 'Bound'
        
        carrier_info.append({
            'quotes': quotes,
            'bound': bound_info,
            'bound_carrier': row.get('Bound With', '') if pd.notna(row.get('Bound With', '')) else ''
        })
    
    # Analyze results
    results = {
        'total_matches': len(matched_data),
        'lob_distribution': matched_data['LOB'].value_counts().to_dict(),
        'carrier_responses': {},
        'bound_distribution': {},
        'submissions': [],
        'all_lobs': all_lobs
    }
    
    # Track bound policies by carrier
    bound_counts = {}
    
    # Combine submission data with carrier info
    for (_, row), carrier_data in zip(matched_data.iterrows(), carrier_info):
        submission = {
            'Applicant': row['Applicant'],
            'LOB': row['LOB'],
            'RCVD': row['RCVD'],
            'Source_Sheet': row['Source_Sheet'],
            'quotes': carrier_data['quotes'],
            'bound': carrier_data['bound'],
            'bound_carrier': carrier_data['bound_carrier']
        }
        results['submissions'].append(submission)
        
        # Track bound carriers
        if carrier_data['bound_carrier']:
            carrier = carrier_data['bound_carrier']
            bound_counts[carrier] = bound_counts.get(carrier, 0) + 1
    
    results['bound_distribution'] = bound_counts
    
    return results

def create_wc_analysis_section(df):
    """Create Workers Compensation analysis section"""
    wc_data = analyze_wc_data(df)
    
    if wc_data and wc_data['total_wc_submissions'] > 0:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("👷 Workers Compensation Analysis")
        
        # WC Overview metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total WC Submissions", wc_data['total_wc_submissions'])
            st.metric("Active Carriers for WC", len(wc_data['carrier_responses']))
        
        with col2:
            if wc_data['class_codes']:
                st.write("Top Class Codes:")
                for code, count in dict(sorted(wc_data['class_codes'].items(), 
                                            key=lambda x: x[1], 
                                            reverse=True)[:5]).items():
                    st.write(f"- Code {code}: {count} submissions")
        
        # Carrier response chart for WC
        if wc_data['carrier_responses']:
            carrier_df = pd.DataFrame([
                {'Carrier': k, 'Quotes': v}
                for k, v in wc_data['carrier_responses'].items()
            ])
            
            fig = px.bar(
                carrier_df,
                x='Carrier',
                y='Quotes',
                title='WC Quotes by Carrier',
                color='Quotes',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                xaxis_tickangle=-45,
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(t=50, l=50, r=20, b=50)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def create_business_search_section(df, search_term):
    """Create analysis section for business type search"""
    results = analyze_business_type(df, search_term)
    
    if results is None:
        st.warning("No matches found for your search term.")
        return
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader(f"🔍 Business Type Analysis: '{search_term}'")
    
    # Sort LOBs by frequency and create dropdown
    lob_counts = pd.Series(results['lob_distribution'])
    sorted_lobs = lob_counts.sort_values(ascending=False)
    
    # Create a dropdown for LOB filtering
    selected_lob = st.selectbox(
        "Filter by Line of Business",
        ["All Lines"] + [f"{lob} ({count} submissions)" for lob, count in sorted_lobs.items()],
        help="Select a specific line of business to analyze. LOBs are sorted by frequency."
    )
    
    # Extract the LOB name without the count
    selected_lob_name = selected_lob.split(" (")[0] if selected_lob != "All Lines" else None
    
    # Filter submissions based on selected LOB
    filtered_submissions = results['submissions']
    if selected_lob_name:
        filtered_submissions = [s for s in results['submissions'] if s['LOB'] == selected_lob_name]
    
    # Collect all carrier quotes for summary
    all_quotes = {}
    quote_amounts = {}  # Track actual quote amounts
    bound_info = {}  # Track bound policies
    
    for submission in filtered_submissions:
        # Track quotes
        for carrier, amount in submission['quotes'].items():
            if carrier not in all_quotes:
                all_quotes[carrier] = []
                quote_amounts[carrier] = []
            all_quotes[carrier].append(submission)
            if isinstance(amount, (int, float)):
                quote_amounts[carrier].append(amount)
        
        # Track bound policies
        if submission['bound_carrier']:
            carrier = submission['bound_carrier']
            if carrier not in bound_info:
                bound_info[carrier] = []
            bound_info[carrier].append(submission)
    
    # Display carrier quote summary
    if all_quotes:
        st.write(f"### 🏛️ Carrier Analysis {f'for {selected_lob_name}' if selected_lob_name else ''}")
        
        # Create metrics
        cols = st.columns(4)
        with cols[0]:
            st.metric("Total Matching Submissions", len(filtered_submissions))
        with cols[1]:
            st.metric("Carriers Providing Quotes", len(all_quotes))
        with cols[2]:
            total_quotes = sum(len(quotes) for quotes in all_quotes.values())
            st.metric("Total Quotes Provided", total_quotes)
        with cols[3]:
            total_bound = sum(len(policies) for policies in bound_info.values())
            st.metric("Total Bound Policies", total_bound)
        
        # Create carrier quote visualization
        carrier_data = []
        for carrier, submissions in all_quotes.items():
            avg_quote = None
            if quote_amounts[carrier]:
                avg_quote = sum(quote_amounts[carrier]) / len(quote_amounts[carrier])
            
            bound_count = len(bound_info.get(carrier, []))
            
            carrier_data.append({
                'Carrier': carrier,
                'Number of Quotes': len(submissions),
                'Average Quote': avg_quote if avg_quote else 0,
                'Quote Rate': (len(submissions) / len(filtered_submissions)) * 100,
                'Bound Policies': bound_count,
                'Win Rate': (bound_count / len(submissions) * 100) if len(submissions) > 0 else 0
            })
        
        if carrier_data:
            carrier_df = pd.DataFrame(carrier_data)
            
            # Create three columns for charts
            chart_cols = st.columns(2)
            
            with chart_cols[0]:
                # Quote frequency chart
                fig1 = px.bar(
                    carrier_df.sort_values('Number of Quotes', ascending=False),
                    x='Carrier',
                    y='Number of Quotes',
                    title=f'Carrier Quote Frequency for {search_term}',
                    color='Quote Rate',
                    color_continuous_scale='Viridis',
                    labels={'Quote Rate': 'Quote Rate (%)'}
                )
                fig1.update_layout(
                    xaxis_tickangle=-45,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(t=50, l=50, r=20, b=50)
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with chart_cols[1]:
                # Win rate chart for carriers with bound policies
                win_rate_df = carrier_df[carrier_df['Bound Policies'] > 0].sort_values('Win Rate', ascending=False)
                if not win_rate_df.empty:
                    fig2 = px.bar(
                        win_rate_df,
                        x='Carrier',
                        y='Win Rate',
                        title=f'Carrier Win Rates for {search_term}',
                        color='Win Rate',
                        color_continuous_scale='Viridis',
                        labels={'Win Rate': 'Win Rate (%)'},
                        hover_data=['Number of Quotes', 'Bound Policies']
                    )
                    fig2.update_layout(
                        xaxis_tickangle=-45,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        margin=dict(t=50, l=50, r=20, b=50),
                        yaxis_tickformat='.1f'
                    )
                    st.plotly_chart(fig2, use_container_width=True)
    
    # Lines of Business Distribution
    if not selected_lob_name:
        st.write("### 📊 Lines of Business Distribution")
        
        # Create pie chart for LOB distribution
        lob_data = pd.DataFrame(
            list(results['lob_distribution'].items()),
            columns=['LOB', 'Count']
        ).sort_values('Count', ascending=False)
        
        # Create two columns
        lob_cols = st.columns([2, 1])
        
        with lob_cols[0]:
            fig_lob = px.pie(
                lob_data,
                values='Count',
                names='LOB',
                title=f'Distribution of Lines of Business for {search_term}',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_lob, use_container_width=True)
        
        with lob_cols[1]:
            st.write("#### LOB Breakdown:")
            for lob, count in lob_data.iterrows():
                st.write(f"- **{count['LOB']}**: {count['Count']} submissions ({(count['Count']/len(results['submissions'])*100):.1f}%)")
    
    # Detailed matches with quote information
    st.write("### 📋 Matching Submissions")
    
    # Group submissions by LOB for better organization
    lob_grouped = {}
    for submission in filtered_submissions:
        lob = submission['LOB']
        if lob not in lob_grouped:
            lob_grouped[lob] = []
        lob_grouped[lob].append(submission)
    
    # Display submissions grouped by LOB
    for lob, submissions in sorted(lob_grouped.items(), key=lambda x: len(x[1]), reverse=True):
        st.write(f"\n#### {lob} ({len(submissions)} submissions)")
        
        # Add a summary for this LOB
        lob_carriers = {}
        bound_carriers = {}
        for submission in submissions:
            # Track quotes
            for carrier, amount in submission['quotes'].items():
                if carrier not in lob_carriers:
                    lob_carriers[carrier] = {'count': 0, 'amounts': [], 'bound': 0}
                lob_carriers[carrier]['count'] += 1
                if isinstance(amount, (int, float)):
                    lob_carriers[carrier]['amounts'].append(amount)
            
            # Track bound policies
            if submission['bound_carrier']:
                carrier = submission['bound_carrier']
                if carrier not in bound_carriers:
                    bound_carriers[carrier] = 0
                bound_carriers[carrier] += 1
                if carrier in lob_carriers:
                    lob_carriers[carrier]['bound'] += 1
        
        # Display LOB summary
        st.write("**Carrier Summary:**")
        for carrier, data in sorted(lob_carriers.items(), key=lambda x: x[1]['count'], reverse=True):
            avg_amount = f", Avg: ${sum(data['amounts'])/len(data['amounts']):,.2f}" if data['amounts'] else ""
            bound_info = f", Bound: {data['bound']}" if data['bound'] > 0 else ""
            st.write(f"- {carrier}: {data['count']} quotes{avg_amount}{bound_info}")
        
        if bound_carriers:
            st.write("\n**Bound Policies:**")
            for carrier, count in sorted(bound_carriers.items(), key=lambda x: x[1], reverse=True):
                st.write(f"- {carrier}: {count} bound")
        
        # Display individual submissions
        for submission in submissions:
            with st.expander(f"**{submission['Applicant']}**"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**📅 Submission Details:**")
                    st.write(f"- Received: {pd.to_datetime(submission['RCVD']).strftime('%Y-%m-%d')}")
                    st.write(f"- Source: {submission['Source_Sheet']}")
                
                with col2:
                    if submission['bound']:
                        st.markdown(f"**🎯 {submission['bound']}**")
                
                if submission['quotes']:
                    st.write("**💰 Carrier Quotes:**")
                    quote_items = []
                    for carrier, amount in submission['quotes'].items():
                        if isinstance(amount, (int, float)):
                            quote_items.append(f"- {carrier}: ${amount:,.2f}")
                        else:
                            quote_items.append(f"- {carrier}: {amount}")
                    
                    # Display quotes in columns for better organization
                    cols = st.columns(2)
                    half = len(quote_items) // 2
                    cols[0].write("\n".join(quote_items[:half]))
                    cols[1].write("\n".join(quote_items[half:]))
                else:
                    st.write("❌ No quotes received")
                
                st.write("---")
    
    st.markdown('</div>', unsafe_allow_html=True)

## SECTION: Visualization Functions
def create_carrier_quote_chart(carrier_data):
    """Create bar chart for carrier quote patterns"""
    df_chart = pd.DataFrame([
        {'Carrier': carrier, 'Quote Rate': data['quote_percentage'], 'Total Quotes': data['total_quotes']}
        for carrier, data in carrier_data.items()
    ])
    
    fig = px.bar(
        df_chart,
        x='Carrier',
        y='Quote Rate',
        title='Carrier Quote Rates (%)',
        labels={'Quote Rate': 'Quote Rate (%)', 'Total Quotes': 'Total Quotes'},
        color='Quote Rate',
        color_continuous_scale='Viridis',
        hover_data=['Total Quotes']
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=50, l=50, r=20, b=50)
    )
    return fig

def create_lob_distribution_chart(df):
    """Create pie chart for LOB distribution"""
    lob_counts = df['LOB'].value_counts()
    fig = px.pie(
        values=lob_counts.values,
        names=lob_counts.index,
        title='Distribution of Lines of Business',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig

def create_trend_chart(df):
    """Create trend chart showing submissions over time"""
    # Convert Period to string for plotting
    monthly_counts = df.groupby('Month_Year').size().reset_index()
    monthly_counts['Month_Year'] = monthly_counts['Month_Year'].astype(str)
    monthly_counts.columns = ['Month_Year', 'Count']
    
    # Sort by date
    monthly_counts = monthly_counts.sort_values('Month_Year')
    
    fig = px.line(
        monthly_counts,
        x='Month_Year',
        y='Count',
        title='Submission Trends Over Time',
        labels={'Count': 'Number of Submissions', 'Month_Year': 'Month'},
        markers=True
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=50, l=50, r=20, b=50)
    )
    return fig

## SECTION: Main Dashboard
def main():
    # Header with Evolution Partners branding
    st.markdown("""
        <div class="main-header">
            <h1>🚀 Evolution Partners</h1>
            <h2>Insurance Analytics Dashboard</h2>
            <p>Empowering Better Insurance Decisions</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for DataFrame if it doesn't exist
    if 'df' not in st.session_state:
        st.session_state.df = None
        # Try to load local files first
        if os.path.exists('data/combined_submission_log.csv'):
            try:
                st.info("Found local CSV file, attempting to load...")
                df = pd.read_csv('data/combined_submission_log.csv')
                st.session_state.df = process_data(df)
                st.success("Loaded local CSV file successfully!")
            except Exception as e:
                st.error(f"Error loading local CSV: {str(e)}")
        elif os.path.exists('data/EvolutionMasterSubmissionLog061325.xlsx'):
            try:
                st.info("Found local Excel file, attempting to load...")
                df = process_excel_file('data/EvolutionMasterSubmissionLog061325.xlsx')
                if df is not None:
                    st.session_state.df = process_data(df)
                    st.success("Loaded local Excel file successfully!")
            except Exception as e:
                st.error(f"Error loading local Excel: {str(e)}")
    
    # File uploader section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Data File", type=['xlsx', 'csv'], 
                                   help="Upload either the Excel file or the combined CSV file")
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.xlsx'):
                # Process Excel file
                st.info("Processing uploaded Excel file...")
                df = process_excel_file(uploaded_file)
                if df is not None:
                    st.success("Excel file processed successfully!")
                    st.session_state.df = process_data(df)
            
            elif uploaded_file.name.endswith('.csv'):
                # Read CSV directly into DataFrame
                st.info("Processing uploaded CSV file...")
                df = pd.read_csv(uploaded_file)
                st.success("CSV file uploaded successfully!")
                st.session_state.df = process_data(df)
            
            if st.session_state.df is None:
                st.error("Error processing the uploaded file.")
                return
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return
    
    # Check if we have data to display
    if st.session_state.df is None:
        st.info("Please upload either an Excel file or the combined CSV file to begin analysis.")
        return
    
    # Use the DataFrame from session state for all analysis
    df = st.session_state.df
    
    # Business Type Search - Moved to top
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("🔍 Quick Business Search")
    search_term = st.text_input(
        "Search by Business Type/Description",
        help="Enter keywords to search in business descriptions and names (e.g., 'plumb*' for plumbing)",
        placeholder="Type business description (e.g., plumb*, restaurant*, etc.)"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Help Box
    with st.expander("ℹ️ How to Use This Dashboard"):
        st.markdown("""
        <div class="help-box">
        <h4>Quick Start Guide:</h4>
        
        1. 🔍 **Business Search**:
           - Type a business description in the search box above
           - Use * for wildcard searches (e.g., 'plumb*' for plumbing)
           - Results will show matching submissions and carrier preferences
        
        2. 📅 **Date Range Selection**:
           - Use the sidebar to select a specific date range
           - Default view is last 3 years of data
        
        3. 🏢 **Line of Business Filter**:
           - Select one or multiple lines of business to analyze
           - Use the search box to quickly find specific business lines
        
        4. 📊 **Analysis Views**:
           - Top cards show key metrics
           - Charts display quote patterns and distributions
           - Expand sections for detailed breakdowns
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar Configuration
    try:
        st.sidebar.image("logo.png", width=150)
    except Exception as e:
        st.sidebar.markdown("""
            <div class="sidebar-logo">
                <h2>Evolution</h2>
                <div style="height: 5px; 
                            background: linear-gradient(to right, #ff4b1f, #ff9068); 
                            margin: 10px 0;
                            border-radius: 2px;"></div>
            </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.title("Analysis Controls")
    
    # Quick Date Range Selector
    st.sidebar.subheader("📅 Quick Date Range")
    date_options = {
        "All Time": None,
        "Last 3 Years": timedelta(days=1095),
        "Last 180 Days": timedelta(days=180),
        "Last 1 Year": timedelta(days=365),
        "Custom Range": "custom"
    }
    
    selected_range = st.sidebar.radio("Select Time Period", 
                                    list(date_options.keys()),
                                    index=0)  # Default to "All Time"
    
    # Ensure RCVD is datetime for date range calculations
    try:
        df['RCVD'] = pd.to_datetime(df['RCVD'], errors='coerce')
        min_date = df['RCVD'].min()
        max_date = df['RCVD'].max()
        
        # If dates are invalid, use default range
        if pd.isna(min_date) or pd.isna(max_date):
            min_date = pd.Timestamp.now() - pd.Timedelta(days=365)
            max_date = pd.Timestamp.now()
    except Exception as e:
        # Default date range if there's an error
        min_date = pd.Timestamp.now() - pd.Timedelta(days=365)
        max_date = pd.Timestamp.now()
    
    if selected_range == "Custom Range":
        date_range = st.sidebar.date_input(
            "Select Custom Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    elif selected_range == "All Time":
        date_range = (min_date, max_date)
    else:
        end_date = max_date
        start_date = end_date - date_options[selected_range]
        date_range = (start_date, end_date)
    
    # Source Sheet Filter
    with st.sidebar.expander("📑 Data Source", expanded=False):
        all_sheets = sorted(df['Source_Sheet'].unique())
        selected_sheets = st.multiselect(
            "Select Source Sheets",
            options=all_sheets,
            default=all_sheets,
            key="source_sheets"
        )
    
    # LOB Filter with WC prominence
    with st.sidebar.expander("🏢 Line of Business Selection", expanded=False):
        # Special WC filter
        show_wc_only = st.checkbox("Show Workers Compensation Only", value=False, key="wc_only")
        
        if show_wc_only:
            selected_lobs = ['WC']
        else:
            all_lobs = sorted(df['LOB'].unique())
            selected_lobs = st.multiselect(
                "Select Lines of Business",
                options=all_lobs,
                default=all_lobs,
                key="lobs"
            )
    
    # WC Class Code filter (only show if WC is selected)
    if 'WC' in selected_lobs:
        with st.sidebar.expander("👷 WC Class Codes", expanded=True):
            # Get WC class codes from the correct column name
            wc_data = df[df['LOB'] == 'WC']
            wc_codes = wc_data['WC Class Code'].dropna()
            
            # Convert to strings and clean up
            wc_codes_clean = []
            for code in wc_codes:
                if pd.notna(code):
                    # Handle both single codes and comma-separated codes
                    code_str = str(code).strip()
                    if ',' in code_str:
                        # Split comma-separated codes
                        individual_codes = [c.strip() for c in code_str.split(',')]
                        wc_codes_clean.extend(individual_codes)
                    else:
                        wc_codes_clean.append(code_str)
            
            # Remove duplicates and sort
            available_class_codes = sorted(list(set(wc_codes_clean)))
            
            # Add "All" option and "Unknown" if there are records without class codes
            options = ["All"] + available_class_codes
            if len(wc_data) > len(wc_codes):
                options.append("Unknown")
            
            selected_class_codes = st.multiselect(
                "Select WC Class Codes",
                options=options,
                default=["All"],
                key="wc_class_codes"
            )
        
        # Apply filters including class codes
        try:
            # Ensure RCVD is datetime before filtering
            df['RCVD'] = pd.to_datetime(df['RCVD'], errors='coerce')
            mask = (
                (df['RCVD'].dt.date >= pd.to_datetime(date_range[0]).date()) &
                (df['RCVD'].dt.date <= pd.to_datetime(date_range[1]).date()) &
                (df['LOB'].isin(selected_lobs)) &
                (df['Source_Sheet'].isin(selected_sheets))
            )
        except Exception as e:
            # Fallback: just filter by LOB and Source_Sheet
            mask = (
                (df['LOB'].isin(selected_lobs)) &
                (df['Source_Sheet'].isin(selected_sheets))
            )
        
        # Apply WC class code filter if specific codes are selected
        if 'WC' in selected_lobs and "All" not in selected_class_codes:
            wc_mask = pd.Series(False, index=df.index)
            
            for _, row in df.iterrows():
                if row['LOB'] == 'WC':
                    row_class_code = str(row['WC Class Code']) if pd.notna(row['WC Class Code']) else 'Unknown'
                    
                    # Check if any selected class code matches this row
                    if 'Unknown' in selected_class_codes and pd.isna(row['WC Class Code']):
                        wc_mask.iloc[row.name] = True
                    else:
                        # Handle comma-separated codes
                        if ',' in row_class_code:
                            row_codes = [c.strip() for c in row_class_code.split(',')]
                            if any(code in selected_class_codes for code in row_codes):
                                wc_mask.iloc[row.name] = True
                        else:
                            if row_class_code in selected_class_codes:
                                wc_mask.iloc[row.name] = True
                else:
                    # Non-WC records are always included
                    wc_mask.iloc[row.name] = True
            
            mask = mask & wc_mask
    else:
        # Apply filters without class codes
        try:
            # Ensure RCVD is datetime before filtering
            df['RCVD'] = pd.to_datetime(df['RCVD'], errors='coerce')
            mask = (
                (df['RCVD'].dt.date >= pd.to_datetime(date_range[0]).date()) &
                (df['RCVD'].dt.date <= pd.to_datetime(date_range[1]).date()) &
                (df['LOB'].isin(selected_lobs)) &
                (df['Source_Sheet'].isin(selected_sheets))
            )
        except Exception as e:
            # Fallback: just filter by LOB and Source_Sheet
            mask = (
                (df['LOB'].isin(selected_lobs)) &
                (df['Source_Sheet'].isin(selected_sheets))
            )
    
    filtered_df = df[mask]
    
    # If there's a search term, show the business search analysis first
    if search_term:
        create_business_search_section(filtered_df, search_term)
    
    # Key Metrics
    st.markdown('<div style="margin-bottom: 30px;">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <h3>📊 Total Submissions</h3>
                <h2 style="color: #1e3c72;">{len(filtered_df)}</h2>
                <p>From {len(selected_sheets)} sheets</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <h3>🏢 Lines of Business</h3>
                <h2 style="color: #1e3c72;">{len(filtered_df['LOB'].unique())}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        active_carriers = sum(1 for c in CARRIER_COLUMNS if filtered_df[c].notna().sum() > 0)
        st.markdown(f"""
            <div class="metric-card">
                <h3>🏛️ Active Carriers</h3>
                <h2 style="color: #1e3c72;">{active_carriers}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_quotes = sum(filtered_df[c].notna().sum() for c in CARRIER_COLUMNS) / len(filtered_df) if len(filtered_df) > 0 else 0
        st.markdown(f"""
            <div class="metric-card">
                <h3>📈 Avg Quotes/Submission</h3>
                <h2 style="color: #1e3c72;">{avg_quotes:.1f}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Trend Analysis
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("📈 Submission Trends")
    trend_chart = create_trend_chart(filtered_df)
    st.plotly_chart(trend_chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Carrier Analysis
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("🏛️ Carrier Quote Analysis")
    carrier_data = analyze_carrier_responses(filtered_df)
    carrier_chart = create_carrier_quote_chart(carrier_data)
    st.plotly_chart(carrier_chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # LOB Analysis
    st.subheader("🏢 Line of Business Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        if len(filtered_df) > 0:
            lob_chart = create_lob_distribution_chart(filtered_df)
            st.plotly_chart(lob_chart)
        else:
            st.warning("No data available for selected filters")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        lob_patterns = analyze_lob_patterns(filtered_df)
        st.write("📋 Detailed LOB Breakdown")
        for lob, data in lob_patterns.items():
            with st.expander(f"📌 {lob} - {data['total_submissions']} submissions"):
                if data['carrier_responses']:
                    for carrier, count in data['carrier_responses'].items():
                        st.write(f"🏛️ {carrier}: {count} quotes")
                else:
                    st.write("❌ No quotes received yet")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Workers Compensation specific analysis
    if 'WC' in selected_lobs:
        create_wc_analysis_section(filtered_df)
    
    # Detailed Data View
    st.subheader("🔍 Detailed Submission Data")
    show_data = st.checkbox("Show Raw Data Analysis")
    if show_data:
        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "RCVD": st.column_config.DateColumn("Received Date"),
                "EFF DATE": st.column_config.DateColumn("Effective Date"),
                "LOB": st.column_config.TextColumn("Line of Business"),
                "WC_Class_Code": st.column_config.TextColumn("WC Class Code"),
            }
        )

if __name__ == "__main__":
    main() 