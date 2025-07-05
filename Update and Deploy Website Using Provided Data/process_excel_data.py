import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_new_excel_data(excel_file_path):
    """
    Process the new Excel file to match the GitHub repository's expected format
    """
    logger.info(f"Processing Excel file: {excel_file_path}")
    
    # Read all sheets
    xl = pd.ExcelFile(excel_file_path)
    logger.info(f"Found sheets: {xl.sheet_names}")
    
    # Standard carrier columns expected by the dashboard
    standard_carriers = [
        'AmTrust', 'Bristol West', 'Chubb', 'CNA', 'Employers', 'Guard',
        'Hanover', 'Hartford', 'Hourly', 'ICW', 'Kemper', 'Liberty Mutual',
        'Markel', 'Philadelphia', 'Preferred', 'Stillwater', 'Travelers', 'UFG'
    ]
    
    # Additional carriers found in new data
    additional_carriers = ['Atlas', 'Attune', 'KBIC', 'Nationwide', 'Other']
    
    all_carriers = standard_carriers + additional_carriers
    
    all_data = []
    
    for sheet_name in xl.sheet_names:
        if sheet_name == 'LOBs':  # Skip the LOBs reference sheet
            continue
            
        try:
            df = pd.read_excel(xl, sheet_name=sheet_name)
            logger.info(f"Processing sheet '{sheet_name}': {len(df)} rows")
            
            # Skip empty rows or header-only rows
            if len(df) == 0:
                continue
                
            # Remove rows where the first column contains month names (header rows)
            if 'APPLICANT' in df.columns:
                df = df[~df['APPLICANT'].astype(str).str.upper().isin(['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE'])]
            elif 'Applicant' in df.columns:
                df = df[~df['Applicant'].astype(str).str.upper().isin(['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE'])]
            
            # Standardize column names to match GitHub format
            column_mapping = {
                'APPLICANT': 'Applicant',
                'AGENCY': 'Member',
                'Bound With Carrier': 'Bound With'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Ensure required columns exist
            required_columns = [
                'Applicant', 'Member', 'EFF DATE', 'LOB', 'SEMSEE', 
                'Quoted/Bound $', 'Policy Number', 'Bound With', 'NOTES'
            ]
            
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
                    
            # Add RCVD column if missing (use EFF DATE as fallback)
            if 'RCVD' not in df.columns:
                df['RCVD'] = df['EFF DATE']
            
            # Handle WC Class Code column
            if 'WC Class Code' not in df.columns:
                df['WC Class Code'] = None
            
            # Ensure all carrier columns exist
            for carrier in all_carriers:
                if carrier not in df.columns:
                    df[carrier] = None
            
            # Clean up data
            df['Applicant'] = df['Applicant'].astype(str).str.strip()
            df['Member'] = df['Member'].astype(str).str.strip()
            df['LOB'] = df['LOB'].astype(str).str.strip()
            
            # Remove rows with invalid applicant names
            df = df[~df['Applicant'].isin(['nan', 'NaN', '', 'None'])]
            df = df[df['Applicant'].notna()]
            
            # Standardize LOB values according to GitHub format
            lob_mapping = {
                'bop': 'BOP/PKG', 'BOP': 'BOP/PKG', 'pkg': 'BOP/PKG',
                'PKG': 'BOP/PKG', 'Pkg': 'BOP/PKG', 'BOP/Pkg': 'BOP/PKG',
                'BOP/PKG': 'BOP/PKG', 'pkg/umb': 'BOP/PKG/UMB',
                'BOP / Umb': 'BOP/PKG/UMB', 'umb': 'UMB', 'Umb': 'UMB',
                'UMB': 'UMB', 'wc': 'WC', 'WC': 'WC', 'ba': 'BA', 'BA': 'BA'
            }
            
            df['LOB'] = df['LOB'].apply(lambda x: lob_mapping.get(x, x) if pd.notna(x) else 'Unknown')
            
            # Add source sheet information
            df['Source_Sheet'] = sheet_name
            
            # Select only the columns we want to keep (remove unnamed columns)
            final_columns = required_columns + ['WC Class Code'] + all_carriers + ['RCVD', 'Source_Sheet']
            
            # Only keep columns that exist in the dataframe
            final_columns = [col for col in final_columns if col in df.columns]
            df = df[final_columns]
            
            all_data.append(df)
            logger.info(f"Processed sheet '{sheet_name}': {len(df)} valid rows after cleaning")
            
        except Exception as e:
            logger.error(f"Error processing sheet '{sheet_name}': {str(e)}")
            continue
    
    # Combine all sheets
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Combined data: {len(combined_df)} total rows")
        
        # Convert date columns to datetime
        date_columns = ['RCVD', 'EFF DATE']
        for col in date_columns:
            if col in combined_df.columns:
                combined_df[col] = pd.to_datetime(combined_df[col], errors='coerce')
        
        # Final data quality check
        logger.info(f"Data quality summary:")
        logger.info(f"- Total rows: {len(combined_df)}")
        logger.info(f"- Unique applicants: {combined_df['Applicant'].nunique()}")
        if 'EFF DATE' in combined_df.columns and combined_df['EFF DATE'].notna().any():
            logger.info(f"- Date range: {combined_df['EFF DATE'].min()} to {combined_df['EFF DATE'].max()}")
        logger.info(f"- LOB distribution: {combined_df['LOB'].value_counts().to_dict()}")
        
        return combined_df
    else:
        logger.error("No valid data found in Excel file")
        return None

if __name__ == "__main__":
    # Process the new Excel file
    excel_path = "/home/ubuntu/upload/EvolutionMasterSubmissionLog061325.xlsx"
    processed_df = process_new_excel_data(excel_path)
    
    if processed_df is not None:
        # Save to CSV in the Evolution project directory
        output_path = "/home/ubuntu/Evolution/combined_submission_log.csv"
        processed_df.to_csv(output_path, index=False)
        print(f"Successfully processed and saved data to {output_path}")
        print(f"Total records: {len(processed_df)}")
        print("\nColumn names in final dataset:")
        print(processed_df.columns.tolist())
        print("\nSample data:")
        print(processed_df.head())
    else:
        print("Failed to process Excel file")

