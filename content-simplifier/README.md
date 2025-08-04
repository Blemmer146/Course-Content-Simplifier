# 🎓 Content Simplification Lab

**Powered by IBM Watsonx.ai & Granite Models**

*Capstone Project for IBM SkillsBuild by Edunet Foundation 2025*

A Streamlit-based application that leverages IBM Watsonx.ai's Granite models to simplify academic content for different learning levels. Transform complex educational material into beginner, intermediate, or advanced-friendly content with AI-powered simplification.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.28+-red.svg)
![IBM Watsonx.ai](https://img.shields.io/badge/IBM-Watsonx.ai-blue.svg)
![IBM SkillsBuild](https://img.shields.io/badge/IBM-SkillsBuild-blue.svg)
![Edunet Foundation](https://img.shields.io/badge/Edunet-Foundation-green.svg)

## 🌟 Features

### 📝 Single Content Simplification
- Transform individual pieces of academic content
- Choose from beginner, intermediate, or advanced levels
- Markdown-formatted output with raw text option
- Download results in multiple formats

### 📚 Batch Processing
- Upload CSV files for bulk content processing
- Manual batch entry for multiple items
- Progress tracking and error handling
- Export results as CSV

### 📊 History & Analytics
- Track all simplification attempts
- Filter by level and subject
- Export history for analysis
- Clear history functionality

### 🔧 Template Management
- View and manage prompt templates
- Template variable inspection  
- List all available templates

*This project was developed as part of the IBM SkillsBuild by Edunet Foundation 2025 capstone program, demonstrating practical application of IBM Watsonx.ai technologies.*

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- IBM Cloud account with Watsonx.ai access
- IBM Cloud API key
- Watsonx.ai project with saved prompt templates

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/content-simplifier.git
   cd content-simplifier
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   IBM_API_KEY=your_ibm_cloud_api_key_here
   IBM_PROJECT_ID=your_watsonx_project_id_here
   IBM_REGION=us-south
   PROMPT_TEMPLATE_ASSET_ID=your_prompt_template_id_here
   ```

5. **Run the application**
   ```bash
   streamlit run src/app.py
   ```

## 🔑 Getting Your Credentials

### IBM Cloud API Key
1. Go to [IBM Cloud Console](https://cloud.ibm.com/iam/apikeys)
2. Click "Create" → "API Key"
3. Give it a descriptive name
4. Copy the generated key

### Project ID
1. Open your Watsonx.ai project
2. Navigate to "Manage" tab → "General" → "Details"
3. Copy the Project ID

### Prompt Template Asset ID
1. In your Watsonx.ai project, go to "Prompt Lab"
2. Find your saved prompt template
3. Copy the Asset ID from template details

### Supported Regions
- `us-south` (Dallas)
- `eu-gb` (London)
- `eu-de` (Frankfurt)
- `jp-tok` (Tokyo)

## 📁 Project Structure

```
content-simplifier/
├── .env                          # Environment variables (create this)
├── .gitignore                    # Git ignore file
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── data/
│   └── sample_batch.csv         # Sample CSV for testing
├── notebooks/
│   └── Course-Content-Dashboard-Main.ipynb
└── src/
    ├── app.py                   # Main Streamlit application
    └── watsonx_utils.py         # Utility functions
```

## 📊 CSV Format for Batch Processing

Your CSV file should contain these columns:

```csv
level,subject,content
beginner,biology,"Simple explanation of photosynthesis..."
intermediate,physics,"Newton's laws of motion explanation..."
advanced,chemistry,"Complex molecular orbital theory..."
```

### Required Columns:
- **level**: `beginner`, `intermediate`, or `advanced`
- **subject**: Academic subject (e.g., Biology, Physics, Mathematics)
- **content**: The content to be simplified

## 🎯 Usage Examples

### Single Content Simplification
1. Select your target learning level
2. Enter the academic subject
3. Paste your content to simplify
4. Click "Simplify Content"
5. View results in markdown format
6. Download as .md or .txt file

### Batch Processing
1. Prepare your CSV file with the required format
2. Upload via the file uploader
3. Preview your data
4. Click "Process Batch"
5. Monitor progress and download results

## ⚙️ Model Parameters

- **Max New Tokens**: Control output length (50-500)
- **Temperature**: Creativity level (0.0-1.0)
- **Decoding Method**: 
  - Greedy: Deterministic output
  - Sample: More creative variations

## 🔍 Troubleshooting

### Common Issues

**Environment variables not found:**
- Ensure `.env` file is in the project root
- Check that `python-dotenv` is installed
- Verify all required variables are set

**Authentication errors:**
- Verify your IBM Cloud API key is valid
- Check that your project ID is correct
- Ensure you have access to Watsonx.ai

**Template loading errors:**
- Confirm your prompt template Asset ID
- Verify the template exists in your project
- Check template variable names match expected format

### Debug Information
The application provides debug information in the sidebar showing:
- Configuration status
- Environment variable detection
- File path verification

## 🤝 Contributing

*This project was developed as a capstone project for IBM SkillsBuild by Edunet Foundation 2025.*

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- **IBM SkillsBuild by Edunet Foundation 2025** for providing the capstone project opportunity
- **IBM Watsonx.ai** for providing the AI foundation models
- **Streamlit** for the excellent web app framework
- **Granite Models** for powerful content processing capabilities

---

**Built with ❤️ using Streamlit and IBM Watsonx.ai**

*Capstone Project for IBM SkillsBuild by Edunet Foundation 2025*

*Transform complex content into accessible learning materials with the power of AI.*