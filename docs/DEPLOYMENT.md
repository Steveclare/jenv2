# Deployment Guide

## Evolution Partners Insurance Analytics Dashboard

This guide covers various deployment options for the Evolution Partners Insurance Analytics Dashboard.

## 🚀 Render.com Deployment (Recommended)

### Prerequisites
- GitHub account
- Render.com account (free tier available)

### Steps

1. **Fork the Repository**
   - Click "Fork" on the GitHub repository
   - Clone your forked repository locally

2. **Connect to Render.com**
   - Sign up at [render.com](https://render.com)
   - Connect your GitHub account
   - Click "New" → "Web Service"
   - Select your forked repository

3. **Configure Deployment**
   - Render will automatically detect the `render.yaml` file
   - Review the configuration settings
   - Click "Deploy"

4. **Custom Domain (Optional)**
   - In your Render dashboard, go to your app settings
   - Add your custom domain under "Custom Domains"
   - Update your DNS settings

### Environment Variables
The following environment variables are automatically configured:
- `STREAMLIT_SERVER_PORT`: Set to `$PORT` (Render's dynamic port)
- `STREAMLIT_SERVER_ADDRESS`: Set to `0.0.0.0`
- `STREAMLIT_SERVER_HEADLESS`: Set to `true`
- `PYTHON_VERSION`: Set to `3.9.18`

## 🐳 Docker Deployment

### Local Docker Build
```bash
# Build the image
docker build -t evolution-dashboard .

# Run the container
docker run -p 8501:8501 evolution-dashboard
```

### Docker Compose
Create a `docker-compose.yml` file:
```yaml
version: '3.8'
services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

Run with:
```bash
docker-compose up -d
```

## 🌐 Heroku Deployment

### Prerequisites
- Heroku CLI installed
- Heroku account

### Steps
1. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

2. **Add Procfile**
   Create a `Procfile` in your root directory:
   ```
   web: streamlit run insurance_dashboard.py --server.port=$PORT --server.address=0.0.0.0
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

## 🏠 Local Development

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Steps
1. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/evolution-insurance-dashboard.git
   cd evolution-insurance-dashboard
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Application**
   ```bash
   streamlit run insurance_dashboard.py
   ```

## 📊 Data Configuration

### File Upload
The dashboard supports two data input methods:
1. **File Upload**: Upload Excel or CSV files directly through the web interface
2. **Local Files**: Place data files in the `data/` directory

### Supported Formats
- Excel files (`.xlsx`, `.xls`)
- CSV files (`.csv`)
- Multi-sheet Excel files are automatically processed

### Data Structure
Ensure your data includes these columns:
- `Applicant`: Business name
- `Member`: Agency information
- `RCVD`: Received date
- `EFF DATE`: Effective date
- `LOB`: Line of Business
- `WC Class Code`: Workers Compensation codes
- Carrier columns: AmTrust, Bristol West, Chubb, etc.

## 🔧 Configuration

### Environment Variables
Copy `env.template` to `.env` and update values:
```bash
cp env.template .env
```

### Streamlit Configuration
The `.streamlit/config.toml` file contains optimized settings for production deployment.

## 🔍 Monitoring and Logging

### Health Checks
The application includes a health check endpoint at `/_stcore/health`.

### Logging
Logs are written to `insurance_analysis.log` in the application directory.

### Performance Monitoring
Monitor these metrics:
- Response time
- Memory usage
- CPU utilization
- File upload sizes

## 🛡️ Security Considerations

### Data Protection
- Ensure sensitive data is not committed to version control
- Use environment variables for sensitive configuration
- Implement proper access controls if needed

### Network Security
- Use HTTPS in production
- Configure proper CORS settings
- Implement rate limiting if needed

## 📈 Scaling

### Horizontal Scaling
For high-traffic deployments:
- Use a load balancer
- Deploy multiple instances
- Consider using a CDN for static assets

### Database Integration
For larger datasets:
- Consider moving data to a database
- Implement data caching
- Use connection pooling

## 🔄 Updates and Maintenance

### Automated Deployment
Set up automatic deployment from your main branch:
1. Configure webhooks in Render/Heroku
2. Ensure tests pass before deployment
3. Monitor deployment logs

### Backup Strategy
- Regular backups of data files
- Version control for configuration
- Document recovery procedures

## 📞 Support

For deployment issues:
1. Check the logs first
2. Review the configuration
3. Consult the troubleshooting guide
4. Create an issue in the GitHub repository

## 🎯 Best Practices

1. **Use version control** for all configuration files
2. **Test deployments** in a staging environment first
3. **Monitor performance** regularly
4. **Keep dependencies updated**
5. **Document custom configurations**
6. **Implement proper error handling**
7. **Use environment-specific settings** 