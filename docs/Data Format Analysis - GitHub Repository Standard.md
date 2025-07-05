# Data Format Analysis - GitHub Repository Standard

## Expected Data Structure (from existing CSV and code)

### Core Columns (Required)
- **Applicant** - Company/entity name
- **Member** - Agency/member name  
- **RCVD** - Received date (datetime)
- **EFF DATE** - Effective date (datetime)
- **LOB** - Line of Business (standardized values)
- **SEMSEE** - SEMSEE indicator
- **Quoted/Bound $** - Premium amount
- **Policy Number** - Policy identifier
- **NOTES** - Additional notes
- **Bound With** - Carrier bound with
- **Source_Sheet** - Source sheet name (added by processing)

### Carrier Columns (Insurance Companies)
Standard carrier columns expected by the dashboard:
- AmTrust
- Bristol West  
- Chubb
- CNA
- Employers
- Guard
- Hanover
- Hartford
- Hourly
- ICW
- Kemper
- Liberty Mutual
- Markel
- Philadelphia
- Preferred
- Stillwater
- Travelers
- UFG

### LOB Standardization
The system standardizes LOB values:
- 'bop', 'BOP', 'pkg', 'PKG', 'Pkg' → 'BOP/PKG'
- 'wc', 'WC' → 'WC'
- 'ba', 'BA' → 'BA'
- 'umb', 'Umb', 'UMB' → 'UMB'

## Discrepancies Found in New Excel File

### Column Name Variations
- **APPLICANT** vs **Applicant** (varies by sheet)
- **AGENCY** vs **Member** (varies by sheet)
- **Bound With Carrier** vs **Bound With** (January sheet)

### Missing Carrier Columns in New Data
New Excel has these carriers not in standard list:
- Atlas
- Attune  
- KBIC
- Nationwide

Missing from new Excel but in standard list:
- Bristol West
- Philadelphia
- Stillwater
- UFG

### Additional Columns in New Excel
- Other (catch-all carrier column)
- Unnamed columns (data quality issue)

## Processing Strategy
1. Standardize column names to match GitHub format
2. Add missing carrier columns (set to null)
3. Map new carrier columns appropriately
4. Ensure LOB values follow standardization rules
5. Handle date format consistency
6. Add Source_Sheet column for tracking

