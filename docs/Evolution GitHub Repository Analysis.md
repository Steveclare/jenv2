# Evolution GitHub Repository Analysis

## Project Overview
- **Name**: Evolution Partners Insurance Analytics Dashboard
- **Technology**: Streamlit (Python)
- **Purpose**: Comprehensive analytics dashboard for analyzing insurance submission data and tracking carrier responses

## Key Features
- Real-time analytics of insurance submissions
- Advanced business type search functionality
- Trend analysis and visualization
- Line of Business (LOB) analysis
- Workers Compensation specific analysis
- Carrier response tracking
- Flexible date range filtering
- Source sheet filtering
- Detailed submission data view

## Project Structure
```
evolution-insurance-dashboard/
├── README.md
├── requirements.txt
├── insurance_dashboard.py    # Main dashboard application
├── combine_excel_sheets.py   # Data preprocessing script
├── insurance_analysis.py     # Analysis utilities
├── logo.png                 # Evolution Partners logo
├── evolution_logo.png
├── combined_submission_log.csv
└── render.yaml              # Deployment configuration
```

## Data Requirements
The dashboard expects an Excel file named `Evolution Master Submission Log.xlsx` with columns:
- Applicant
- LOB (Line of Business)
- RCVD (Received Date)
- Bound With
- Various carrier columns for quotes

## Current Status
- Repository has 9 commits
- Already configured for Render deployment
- Has combined CSV file for cloud deployment
- MIT licensed

