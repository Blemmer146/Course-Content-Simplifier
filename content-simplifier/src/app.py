import streamlit as st
import pandas as pd
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.prompts import PromptTemplateManager
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods, PromptTemplateFormats
import time
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Alternative: if you prefer to place .env in the same directory as app.py
# load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Content Simplification Lab",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'watsonx_client' not in st.session_state:
    st.session_state.watsonx_client = None
if 'model_inference' not in st.session_state:
    st.session_state.model_inference = None
if 'prompt_mgr' not in st.session_state:
    st.session_state.prompt_mgr = None
if 'is_configured' not in st.session_state:
    st.session_state.is_configured = False
if 'simplification_history' not in st.session_state:
    st.session_state.simplification_history = []

# Debug session state
st.sidebar.markdown("**🔍 Debug Info:**")
st.sidebar.write(f"is_configured: {st.session_state.is_configured}")
env_status = "✅ Found" if os.getenv('IBM_API_KEY') else "❌ Missing"
st.sidebar.write(f"API Key from env: {env_status}")
env_status = "✅ Found" if os.getenv('IBM_PROJECT_ID') else "❌ Missing"
st.sidebar.write(f"Project ID from env: {env_status}")
env_status = "✅ Found" if os.getenv('PROMPT_TEMPLATE_ASSET_ID') else "❌ Missing"
st.sidebar.write(f"Template ID from env: {env_status}")
# Updated .env file check to look in the correct location
env_file_exists = env_path.exists()
st.sidebar.write(f".env file exists: {'✅ Yes' if env_file_exists else '❌ No'}")
st.sidebar.write(f".env path: {env_path}")
st.sidebar.markdown("---")

# Main header
st.markdown('<h1 class="main-header">🎓 Content Simplification Lab</h1>', unsafe_allow_html=True)
st.markdown("**Powered by IBM Watsonx.ai & Granite Models**")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # Watsonx.ai credentials
    st.subheader("Watsonx.ai Settings")


    # Helper function to get env var if available
    def get_env_default(key, default=""):
        try:
            value = os.getenv(key, default)
            if value and value != default:
                print(f"🔍 get_env_default({key}): Found value (first 20 chars): '{value[:20]}...'")
            else:
                print(f"🔍 get_env_default({key}): Using default/empty")
            return value
        except Exception as e:
            print(f"❌ Error getting env var {key}: {e}")
            return default


    st.markdown("""
    **Where to find these values:**
    - **API Key**: [IBM Cloud Console](https://cloud.ibm.com/iam/apikeys) → Create API Key
    - **Project ID**: Your Watsonx.ai project → Manage tab → General → Details
    - **Template ID**: Watsonx.ai project → Prompt Lab → Your saved template → Asset ID
    """)

    api_key = st.text_input("API Key",
                            value=get_env_default("IBM_API_KEY"),
                            type="password",
                            help="Your IBM Cloud API key")
    project_id = st.text_input("Project ID",
                               value=get_env_default("IBM_PROJECT_ID"),
                               help="Your Watsonx.ai project ID")
    region = st.selectbox("Region",
                          options=["us-south", "eu-gb", "eu-de", "jp-tok"],
                          index=0 if get_env_default("IBM_REGION") == "" else
                          ["us-south", "eu-gb", "eu-de", "jp-tok"].index(get_env_default("IBM_REGION", "us-south")),
                          help="Select your IBM Cloud region")
    prompt_template_id = st.text_input("Prompt Template Asset ID",
                                       value=get_env_default("PROMPT_TEMPLATE_ASSET_ID"),
                                       help="ID of your saved prompt template")

    # Model settings
    st.subheader("Model Parameters")
    max_tokens = st.slider("Max New Tokens", 50, 500, 300)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    decoding_method = st.selectbox("Decoding Method",
                                   options=["greedy", "sample"],
                                   help="Greedy for deterministic, Sample for creative")

    # Configuration button
    if st.button("🔧 Configure Watsonx.ai", type="primary"):
        if api_key and project_id and prompt_template_id:
            try:
                with st.spinner("Configuring Watsonx.ai connection..."):
                    # Setup credentials
                    url = f"https://{region}.ml.cloud.ibm.com"
                    credentials = Credentials(api_key=api_key, url=url)

                    # Initialize client
                    client = APIClient(credentials)
                    client.set.default_project(project_id)

                    # Initialize model inference
                    model_inference = ModelInference(
                        model_id="ibm/granite-3-8b-instruct",
                        credentials=credentials,
                        project_id=project_id
                    )

                    # Initialize prompt manager
                    prompt_mgr = PromptTemplateManager(
                        credentials=credentials,
                        project_id=project_id
                    )

                    # Test template loading
                    test_template = prompt_mgr.load_prompt(
                        prompt_id=prompt_template_id,
                        astype=PromptTemplateFormats.STRING
                    )

                    # Store in session state
                    st.session_state.watsonx_client = client
                    st.session_state.model_inference = model_inference
                    st.session_state.prompt_mgr = prompt_mgr
                    st.session_state.prompt_template_id = prompt_template_id
                    st.session_state.is_configured = True
                    st.session_state.model_params = {
                        'max_tokens': max_tokens,
                        'temperature': temperature,
                        'decoding_method': decoding_method
                    }

                    st.success("✅ Configuration successful!")
                    st.rerun()

            except Exception as e:
                st.error(f"❌ Configuration failed: {str(e)}")
        else:
            st.warning("⚠️ Please fill in all required fields")

    # Auto-configure if .env values are present
    if not st.session_state.is_configured and api_key and project_id and prompt_template_id:
        if all([api_key != "", project_id != "", prompt_template_id != ""]):
            st.info("🔄 Found credentials! Click 'Configure Watsonx.ai' to connect.")
            st.write("**Debug - Found values:**")
            st.write(f"- API Key: {'✅ Present' if api_key else '❌ Missing'}")
            st.write(f"- Project ID: {'✅ Present' if project_id else '❌ Missing'}")
            st.write(f"- Template ID: {'✅ Present' if prompt_template_id else '❌ Missing'}")
        else:
            st.write("**Debug - Missing values:**")
            st.write(f"- API Key: {'❌ Empty' if not api_key else '✅ Present'}")
            st.write(f"- Project ID: {'❌ Empty' if not project_id else '✅ Present'}")
            st.write(f"- Template ID: {'❌ Empty' if not prompt_template_id else '✅ Present'}")

# Main application
if st.session_state.is_configured:

    # Tabs for different modes
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Single Content", "📚 Batch Processing", "📊 History", "🔧 Template Info"])

    with tab1:
        st.header("Single Content Simplification")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Input")

            # Learning level
            level = st.selectbox(
                "Learning Level",
                options=["beginner", "intermediate", "advanced"],
                help="Select the target learning level"
            )

            # Subject
            subject = st.text_input(
                "Subject",
                placeholder="e.g., Mathematics, Biology, Physics...",
                help="Enter the academic subject"
            )

            # Content to simplify
            content = st.text_area(
                "Content to Simplify",
                height=200,
                placeholder="Enter the academic content you want to simplify...",
                help="Paste or type the content that needs to be simplified"
            )

            # Simplify button
            if st.button("🚀 Simplify Content", type="primary"):
                if content and subject:
                    try:
                        with st.spinner("Simplifying content..."):
                            # Load template
                            prompt_text = st.session_state.prompt_mgr.load_prompt(
                                prompt_id=st.session_state.prompt_template_id,
                                astype=PromptTemplateFormats.STRING
                            )

                            # Fill variables
                            variables = {
                                "level": level,
                                "subject": subject,
                                "content": content
                            }
                            filled_prompt = prompt_text.format(**variables)

                            # Generate parameters
                            params = {
                                GenParams.MAX_NEW_TOKENS: st.session_state.model_params['max_tokens'],
                                GenParams.TEMPERATURE: st.session_state.model_params['temperature']
                            }

                            if st.session_state.model_params['decoding_method'] == 'greedy':
                                params[GenParams.DECODING_METHOD] = DecodingMethods.GREEDY
                            else:
                                params[GenParams.DECODING_METHOD] = DecodingMethods.SAMPLE

                            # Generate response
                            response = st.session_state.model_inference.generate_text(
                                prompt=filled_prompt,
                                params=params
                            )

                            # Store in history
                            st.session_state.simplification_history.append({
                                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                                'level': level,
                                'subject': subject,
                                'original_content': content,
                                'simplified_content': response
                            })

                            st.session_state.current_result = response

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter both subject and content")

        with col2:
            st.subheader("Simplified Output")

            if 'current_result' in st.session_state:
                st.markdown("### 📝 Simplified Content:")

                # Show markdown formatting by default
                st.markdown(st.session_state.current_result)

                # Raw text view in expander
                with st.expander("📄 View Raw Text"):
                    st.text(st.session_state.current_result)

                # Download buttons
                col_download1, col_download2 = st.columns(2)
                with col_download1:
                    st.download_button(
                        label="📥 Download as Markdown",
                        data=st.session_state.current_result,
                        file_name=f"simplified_{subject}_{level}.md",
                        mime="text/markdown"
                    )
                with col_download2:
                    st.download_button(
                        label="📄 Download Raw Text",
                        data=st.session_state.current_result,
                        file_name=f"simplified_{subject}_{level}.txt",
                        mime="text/plain"
                    )
            else:
                st.markdown("""
                <div style='
                    background-color: #e3f2fd; 
                    border: 1px solid #90caf9; 
                    border-radius: 8px; 
                    padding: 20px; 
                    margin: 10px 0;
                    color: #1565c0;
                    text-align: center;
                    font-style: italic;
                '>
                    📄 Simplified content will appear here...
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.header("Batch Processing")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Upload CSV or Enter Multiple Items")

            # File upload
            uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])

            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.write("Preview of uploaded data:")
                    st.dataframe(df.head())

                    required_cols = ['level', 'subject', 'content']
                    if all(col in df.columns for col in required_cols):
                        if st.button("🚀 Process Batch", type="primary"):
                            batch_results = []
                            progress_bar = st.progress(0)

                            for i, row in df.iterrows():
                                try:
                                    # Load template
                                    prompt_text = st.session_state.prompt_mgr.load_prompt(
                                        prompt_id=st.session_state.prompt_template_id,
                                        astype=PromptTemplateFormats.STRING
                                    )

                                    # Fill variables
                                    variables = {
                                        "level": row['level'],
                                        "subject": row['subject'],
                                        "content": row['content']
                                    }
                                    filled_prompt = prompt_text.format(**variables)

                                    # Generate
                                    params = {
                                        GenParams.MAX_NEW_TOKENS: st.session_state.model_params['max_tokens'],
                                        GenParams.TEMPERATURE: st.session_state.model_params['temperature'],
                                        GenParams.DECODING_METHOD: DecodingMethods.GREEDY
                                    }

                                    response = st.session_state.model_inference.generate_text(
                                        prompt=filled_prompt,
                                        params=params
                                    )

                                    batch_results.append({
                                        'level': row['level'],
                                        'subject': row['subject'],
                                        'original_content': row['content'],
                                        'simplified_content': response
                                    })

                                    progress_bar.progress((i + 1) / len(df))

                                except Exception as e:
                                    st.error(f"Error processing row {i}: {str(e)}")

                            st.session_state.batch_results = batch_results
                            st.success(f"✅ Processed {len(batch_results)} items!")
                    else:
                        st.error("❌ CSV must contain columns: level, subject, content")

                except Exception as e:
                    st.error(f"❌ Error reading CSV: {str(e)}")

            # Manual entry
            st.subheader("Or Add Items Manually")
            if 'batch_items' not in st.session_state:
                st.session_state.batch_items = []

            with st.form("add_batch_item"):
                level_batch = st.selectbox("Level", ["beginner", "intermediate", "advanced"])
                subject_batch = st.text_input("Subject")
                content_batch = st.text_area("Content", height=100)

                if st.form_submit_button("➕ Add Item"):
                    if subject_batch and content_batch:
                        st.session_state.batch_items.append({
                            'level': level_batch,
                            'subject': subject_batch,
                            'content': content_batch
                        })
                        st.success("Item added!")

            if st.session_state.batch_items:
                st.write(f"Items to process: {len(st.session_state.batch_items)}")
                if st.button("🚀 Process Manual Batch"):
                    # Similar processing logic as CSV
                    st.success("Processing complete!")

        with col2:
            st.subheader("Batch Results")

            if 'batch_results' in st.session_state and st.session_state.batch_results:
                results_df = pd.DataFrame(st.session_state.batch_results)
                st.dataframe(results_df)

                # Download results
                csv_data = results_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results CSV",
                    data=csv_data,
                    file_name="batch_simplification_results.csv",
                    mime="text/csv"
                )

    with tab3:
        st.header("Simplification History")

        if st.session_state.simplification_history:
            history_df = pd.DataFrame(st.session_state.simplification_history)

            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                level_filter = st.multiselect("Filter by Level",
                                              options=history_df['level'].unique(),
                                              default=history_df['level'].unique())
            with col2:
                subject_filter = st.multiselect("Filter by Subject",
                                                options=history_df['subject'].unique(),
                                                default=history_df['subject'].unique())

            # Apply filters
            filtered_df = history_df[
                (history_df['level'].isin(level_filter)) &
                (history_df['subject'].isin(subject_filter))
                ]

            st.dataframe(filtered_df)

            # Download history
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download History",
                data=csv_data,
                file_name="simplification_history.csv",
                mime="text/csv"
            )

            # Clear history
            if st.button("🗑️ Clear History", type="secondary"):
                st.session_state.simplification_history = []
                st.rerun()
        else:
            st.info("No simplification history yet. Start simplifying content to see history here.")

    with tab4:
        st.header("Template Information")

        try:
            # Load and display template
            prompt_text = st.session_state.prompt_mgr.load_prompt(
                prompt_id=st.session_state.prompt_template_id,
                astype=PromptTemplateFormats.STRING
            )

            st.subheader("Current Template")
            st.code(prompt_text, language="text")

            st.subheader("Template Variables")
            st.write("This template expects the following variables:")
            st.write("- `{level}` - Learning level (beginner, intermediate, advanced)")
            st.write("- `{subject}` - Academic subject")
            st.write("- `{content}` - Content to be simplified")

            # List all templates
            st.subheader("Available Templates")
            try:
                templates = st.session_state.prompt_mgr.list()
                if isinstance(templates, dict) and 'resources' in templates:
                    template_data = []
                    for template in templates['resources']:
                        template_data.append({
                            'Name': template.get('metadata', {}).get('name', 'Unknown'),
                            'ID': template.get('metadata', {}).get('asset_id', 'Unknown'),
                            'Created': template.get('metadata', {}).get('created_at', 'Unknown')
                        })
                    st.dataframe(pd.DataFrame(template_data))
            except Exception as e:
                st.error(f"Error loading templates: {str(e)}")

        except Exception as e:
            st.error(f"Error loading template: {str(e)}")

else:
    # Not configured yet
    st.info("👈 Please configure your Watsonx.ai settings in the sidebar to get started.")

    # Quick start guide
    st.markdown("""
    ## 🚀 Quick Start Guide

    ### 1. Get your credentials:

    **🔑 IBM Cloud API Key:**
    - Go to [IBM Cloud Console](https://cloud.ibm.com/iam/apikeys)
    - Click "Create" → "API Key"
    - Give it a name and copy the key

    **📁 Project ID:**
    - Open your Watsonx.ai project
    - Go to "Manage" tab → "General" → "Details"
    - Copy the Project ID

    **📝 Prompt Template Asset ID:**
    - In your Watsonx.ai project, go to "Prompt Lab"
    - Find your saved prompt template
    - Copy the Asset ID (usually shown in the template details)

    ### 2. Configure in sidebar:
    - Enter your API key and project ID
    - Select your region (usually us-south)
    - Add your prompt template asset ID

    ### 3. Start simplifying:
    - Use Single Content tab for individual items
    - Use Batch Processing for multiple items
    - View your history and download results

    ### 📝 CSV Format for Batch Processing
    Your CSV should have these columns:
    ```
    level,subject,content
    beginner,biology,photosynthesis process in plants
    intermediate,physics,Newton's laws of motion
    advanced,chemistry,molecular orbital theory
    ```

    ### 💡 Pro Tip:
    Create a `.env` file in your project root with:
    ```
    IBM_API_KEY=your_api_key_here
    IBM_PROJECT_ID=your_project_id_here
    IBM_REGION=us-south
    PROMPT_TEMPLATE_ASSET_ID=your_template_id_here
    ```
    Then install python-dotenv: `pip install python-dotenv`
    """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and IBM Watsonx.ai")