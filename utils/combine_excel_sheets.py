import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def combine_excel_sheets(excel_file):
    """Combine all sheets from Excel file into a single DataFrame"""
    logger.info(f"Reading Excel file: {excel_file}")
    
    # Read all sheets
    xl = pd.ExcelFile(excel_file)
    logger.info(f"Found sheets: {xl.sheet_names}")
    
    all_data = []
    for sheet in xl.sheet_names:
        try:
            df = pd.read_excel(xl, sheet_name=sheet)
            logger.info(f"Sheet '{sheet}': {len(df)} rows")
            
            # Add sheet name as source
            df['Source_Sheet'] = sheet
            
            # Ensure Bound With column exists and is properly handled
            if 'Bound With' not in df.columns:
                df['Bound With'] = None
            
            # Clean up the Bound With column
            df['Bound With'] = df['Bound With'].fillna('')
            
            all_data.append(df)
            
        except Exception as e:
            logger.error(f"Error reading sheet '{sheet}': {str(e)}")
    
    # Combine all sheets
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Combined data: {len(combined_df)} total rows")
        
        # Save to CSV
        output_file = 'combined_submission_log.csv'
        combined_df.to_csv(output_file, index=False)
        logger.info(f"Saved combined data to {output_file}")
        
        # Print sample of bound entries
        bound_entries = combined_df[combined_df['Bound With'].str.strip() != '']
        if len(bound_entries) > 0:
            logger.info(f"\nFound {len(bound_entries)} bound entries. Sample:")
            print(bound_entries[['Applicant', 'Bound With']].head())
        
        return combined_df
    else:
        logger.error("No data found in Excel file")
        return None

if __name__ == "__main__":
    excel_file = "Evolution Master Submission Log.xlsx"
    df = combine_excel_sheets(excel_file)
    if df is not None:
        print("\nSample of combined data:")
        print(df.head())
        print("\nColumns in combined data:")
        print(df.columns.tolist()) 