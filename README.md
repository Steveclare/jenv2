# Evolution Partners Insurance Analytics Dashboard

🚀 **Advanced Insurance Submission Analytics Platform**

A comprehensive Streamlit-based dashboard for analyzing insurance submission data, carrier quote patterns, and business insights across multiple lines of business.

## 📋 Overview

This analytics dashboard provides insurance professionals with powerful tools to:
- Analyze submission patterns across multiple carriers
- Track quote success rates and carrier preferences
- Perform detailed Workers Compensation analysis
- Search and analyze business types and descriptions
- Visualize submission trends over time
- Generate comprehensive reports on line of business performance

## 🌟 Features

### 📊 Core Analytics
- **Submission Tracking**: Monitor submissions across 20+ insurance carriers
- **Quote Analysis**: Track quote success rates and carrier responsiveness
- **LOB Analysis**: Detailed breakdowns by Line of Business (WC, BOP/PKG, UMB, BA)
- **Trend Visualization**: Time-series analysis of submission patterns

### 🔍 Advanced Search & Filtering
- **Business Search**: Wildcard search across business descriptions
- **Date Range Filtering**: Custom date ranges with quick presets
- **WC Class Code Analysis**: Specialized Workers Compensation insights
- **Multi-dimensional Filtering**: Source sheets, LOB, and date combinations

### 📈 Interactive Visualizations
- **Carrier Performance Charts**: Visual comparison of quote rates
- **Distribution Analysis**: LOB and submission pattern breakdowns
- **Trend Analysis**: Monthly submission volume tracking
- **Responsive Design**: Mobile-friendly interface

## 🚀 Quick Start

### Option 1: Deploy to Render.com (Recommended)

1. **Fork this repository**
2. **Connect to Render.com**:
   - Sign up at [render.com](https://render.com)
   - Connect your GitHub account
   - Select this repository

3. **Deploy with one click**:
   - Render will automatically detect the `render.yaml` configuration
   - Your app will be live in minutes

### Option 2: Run Locally

```bash
# Clone the repository
git clone https://github.com/yourusername/evolution-insurance-dashboard.git
cd evolution-insurance-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run insurance_dashboard.py
```

### Option 3: Docker Deployment

```bash
# Build the Docker image
docker build -t evolution-dashboard .

# Run the container
docker run -p 8501:8501 evolution-dashboard
```

## 📁 Project Structure

```
evolution-insurance-dashboard/
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── render.yaml                   # Render.com deployment config
├── Dockerfile                    # Container deployment
├── .gitignore                    # Git ignore patterns
├── insurance_dashboard.py        # Main Streamlit application
├── data/
│   ├── combined_submission_log.csv    # Processed data
│   └── EvolutionMasterSubmissionLog061325.xlsx  # Source data
├── utils/
│   ├── combine_excel_sheets.py   # Data processing utilities
│   └── process_excel_data.py     # Excel processing scripts
└── docs/
    ├── deployment-guide.md       # Detailed deployment instructions
    ├── data-format-guide.md      # Data format specifications
    └── user-guide.md             # User manual and features
```

## 🛠️ Configuration

### Environment Variables

Create a `.env` file (optional):

```env
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_THEME_BASE=light
```

### Data Upload

The dashboard supports multiple data input methods:
1. **File Upload**: Upload Excel or CSV files directly in the app
2. **Local Files**: Place files in the project directory
3. **Auto-detection**: Automatically loads available data files

## 📊 Supported Data Format

### Required Columns
- `Applicant`: Business name or applicant
- `Member`: Agency or member information
- `RCVD`: Received date
- `EFF DATE`: Effective date
- `LOB`: Line of Business
- `WC Class Code`: Workers Compensation class codes
- **Carrier Columns**: AmTrust, Bristol West, Chubb, CNA, Employers, Guard, Hanover, Hartford, etc.

### Lines of Business
- **WC**: Workers Compensation
- **BOP/PKG**: Business Owners Policy/Package
- **UMB**: Umbrella Policy
- **BA**: Business Auto
- **BOP/PKG/UMB**: Combined coverage

## 🔧 Technical Details

### Built With
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **Python 3.9+**: Core programming language

### Dependencies
```
streamlit==1.31.0
pandas==2.2.0
plotly==5.18.0
openpyxl==3.1.2
numpy==1.24.3
python-dateutil==2.8.2
```

## 🚀 Deployment Options

### Render.com (Recommended)
- **Automatic deployment** from GitHub
- **Free tier available**
- **Custom domain support**
- **Automatic SSL/HTTPS**

### Heroku
```bash
# Install Heroku CLI and login
heroku create your-app-name
git push heroku main
```

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "insurance_dashboard.py"]
```

## 📝 Usage Guide

### 1. Data Upload
- Use the file uploader to select your Excel or CSV file
- The app will automatically process and validate the data
- Both single-sheet and multi-sheet Excel files are supported

### 2. Business Search
- Enter business type keywords in the search box
- Use wildcards (e.g., 'plumb*' for plumbing businesses)
- Results show matching submissions and carrier preferences

### 3. Filtering Options
- **Date Range**: Select specific time periods
- **LOB Filter**: Focus on specific lines of business
- **WC Class Codes**: Filter by Workers Compensation classifications
- **Source Sheets**: Select specific data sources

### 4. Analysis Views
- **Summary Metrics**: Key performance indicators
- **Carrier Analysis**: Quote success rates by carrier
- **Trend Analysis**: Submission patterns over time
- **LOB Breakdown**: Performance by line of business

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For questions or support:
- Create an issue in this repository
- Review the documentation in the `/docs` folder
- Check the troubleshooting guide

## 🔄 Updates

- **v1.0.0**: Initial release with core analytics features
- **v1.1.0**: Added WC class code analysis
- **v1.2.0**: Enhanced business search capabilities
- **v1.3.0**: Improved UI/UX and mobile responsiveness

---

**Built with ❤️ for Evolution Partners** 