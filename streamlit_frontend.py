#!/usr/bin/env python3
"""
Design Analysis System - Streamlit Frontend
Real-time step-by-step analysis with individual tabs for each step
"""

import streamlit as st
import requests
import time
import json
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Load environment variables
load_dotenv()

# Configuration - Using same environment variables as API
API_BASE_URL = os.getenv(
    'API_BASE_URL', f"http://{os.getenv('API_HOST', 'localhost')}:{os.getenv('API_PORT', '8000')}")
DYNAMODB_TABLE_NAME = os.getenv(
    'DYNAMODB_TABLE_NAME', 'design-analysis-tracking')
AWS_REGION = os.getenv('AWS_REGION', os.getenv('S3_REGION', 'us-east-1'))
STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'local')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', '')
S3_PREFIX = os.getenv('S3_PREFIX', 'design-analysis')
S3_REGION = os.getenv('S3_REGION', 'us-east-1')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# Analysis steps in order
ANALYSIS_STEPS = [
    'chunking',
    'inferring',
    'relating',
    'explaining',
    'activating'
]


def main():
    """Main Streamlit application"""

    st.set_page_config(
        page_title="Design Analysis System",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        color: #2c3e50;
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .step-tab {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .status-completed {
        color: #28a745;
        font-weight: bold;
    }
    .status-processing {
        color: #ffc107;
        font-weight: bold;
    }
    .status-failed {
        color: #dc3545;
        font-weight: bold;
    }
    .status-pending {
        color: #6c757d;
        font-weight: bold;
    }
    .upload-area {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
    }
    .result-card {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<h1 class="main-header">🔍 Design Analysis System</h1>',
                unsafe_allow_html=True)
    st.markdown(
        "Transform research data into actionable design principles using AI-powered analysis")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🚀 New Analysis", "📊 Analysis History", "⚙️ Settings"]
    )

    if page == "🚀 New Analysis":
        show_new_analysis()
    elif page == "📊 Analysis History":
        show_analysis_history()
    elif page == "⚙️ Settings":
        show_settings()


def show_new_analysis():
    """Show the new analysis form with real-time step monitoring"""
    implementation = "hybrid"
    include_metadata = True
    input_method = st.radio(
        "Choose input method:",
        ["📁 File Upload", "🔗 S3 Path"],
        horizontal=True
    )

    research_data = None
    s3_file_path = None

    if input_method == "📁 File Upload":
        uploaded_file = st.file_uploader(
            "Upload Research Data File:",
            type=['txt', 'json', 'csv', 'md'],
            help="Upload a file containing your research data"
        )

        if uploaded_file is not None:
            # Show file info
            st.info(
                f"📁 File selected: {uploaded_file.name} ({uploaded_file.size} bytes)")

            # Upload button
            if st.button("📤 Upload to S3", type="secondary"):
                with st.spinner("Uploading file to S3..."):
                    upload_result = upload_file_to_s3(uploaded_file)

                    if upload_result:
                        s3_file_path = upload_result.get('s3_path')
                        st.success(f"✅ File uploaded successfully!")
                        st.info(f"📋 File ID: {upload_result.get('file_id')}")
                        st.info(f"🔗 S3 Path: `{s3_file_path}`")
                        st.info(
                            f"📊 File Size: {upload_result.get('file_size')} bytes")
                        st.info(
                            f"⏰ Upload Time: {upload_result.get('upload_time')}")

                        # Store the S3 path for analysis
                        st.session_state['uploaded_s3_path'] = s3_file_path
                    else:
                        st.error("❌ Failed to upload file to S3")

            # Show uploaded file info if available
            if 'uploaded_s3_path' in st.session_state:
                st.success(
                    f"✅ File ready for analysis: {st.session_state['uploaded_s3_path']}")
                s3_file_path = st.session_state['uploaded_s3_path']

                # Option to clear uploaded file
                if st.button("🗑️ Clear Uploaded File", type="secondary"):
                    del st.session_state['uploaded_s3_path']
                    st.rerun()

    # elif input_method == "📝 Direct Text Input":
    #     research_data = st.text_area(
    #         "Research Data:",
    #         height=200,
    #         placeholder="Paste your interview transcripts, observations, or research notes here..."
    #     )

    elif input_method == "🔗 S3 Path":
        s3_file_path = st.text_input(
            "S3 File Path:",
            placeholder="/path/to/research-data.json",
            help="Enter the S3 path to your research data file"
        )

        if s3_file_path:
            st.info(f"📁 Using S3 path: {s3_file_path}")

    # Submit analysis
    st.markdown("### Submit Analysis")

    # Determine if we have data to analyze
    has_research_data = bool(research_data)
    has_s3_file = bool(s3_file_path) or (
        'uploaded_s3_path' in st.session_state)
    st.session_state['analysis_started'] = False
    # Get the actual S3 path for analysis
    analysis_s3_path = s3_file_path or st.session_state.get('uploaded_s3_path')

    if st.button("🚀 Start Analysis", type="primary", disabled=not (has_research_data or has_s3_file) or st.session_state['analysis_started']):
        if has_research_data or has_s3_file:
            with st.spinner("Starting analysis..."):
                result = submit_analysis(
                    research_data, analysis_s3_path, implementation, include_metadata)

                if result:
                    import time
                    msg = st.success("✅ Analysis started successfully!")
                    time.sleep(2)
                    msg.empty()

                    # Get request ID from the new response format
                    request_id = result.get('request_id')

                    if request_id:
                        # Start real-time monitoring
                        st.markdown("### 📊 Real-Time Analysis Progress")
                        st.session_state['analysis_started'] = True
                        monitor_analysis_progress(request_id)
                    else:
                        st.error("❌ No request ID received from API")
                else:
                    st.error("❌ Failed to start analysis. Please check the logs.")


def monitor_analysis_progress(request_id):
    """Monitor analysis progress in real-time with detailed step information"""

    # Create placeholder for progress bar
    progress_bar = st.progress(0)
    overall_status_text = st.empty()

    # Placeholder for results section
    results_section = st.empty()

    # Initialize session state for results
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}

    # Monitoring loop
    while True:
        try:
            # Get analysis status from DynamoDB
            analysis = get_analysis_status(request_id)

            if not analysis:
                st.error("❌ Analysis not found")
                break

            overall_status = analysis.get('overall_status', 'pending')
            steps_status = analysis.get(
                'analysis_result', {}).get('steps_status', {})

            # Calculate overall progress
            completed_steps = sum(1 for step in ANALYSIS_STEPS
                                  if steps_status.get(step, {}).get('status') == 'completed')
            progress = (completed_steps / len(ANALYSIS_STEPS)) * 100

            # Update progress bar
            progress_bar.progress(int(progress))

            # Update overall status
            status_emoji = {
                'completed': '✅',
                'processing': '🔄',
                'failed': '❌',
                'pending': '⏳'
            }.get(overall_status, '❓')

            overall_status_text.markdown(
                f"**Overall Status:** {status_emoji} {overall_status.title()} "
                f"({completed_steps}/{len(ANALYSIS_STEPS)} steps completed)"
            )
            # Check if analysis is complete
            with results_section.container():
                if overall_status == 'completed':
                    st.session_state['analysis_started'] = False
                    with st.spinner("Loading final results from S3..."):
                        results = load_analysis_results(request_id)
                        if results:
                            st.session_state.analysis_results = results
                            display_analysis_results(results)
                        else:
                            st.error("❌ Failed to load results from S3")

                        # Exit the monitoring loop
                    return
                elif overall_status == 'failed':
                    st.session_state['analysis_started'] = False
                    st.error("❌ Analysis failed")
                    return
                else:
                    st.session_state['analysis_started'] = True
                    display_analysis_results(
                        results=None,
                        steps_status=steps_status,
                        is_realtime=True
                    )

            time.sleep(2)  # Check every 2 seconds

        except Exception as e:
            st.error(f"❌ Error monitoring progress: {str(e)}")
            break


def show_analysis_history():
    """Show analysis history and details"""

    st.markdown('<h2 class="sub-header">📊 Analysis History</h2>',
                unsafe_allow_html=True)

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Filter by Status:",
            ["All", "completed", "processing", "failed", "pending"]
        )

    with col2:
        date_filter = st.date_input(
            "From Date:",
            help="Show analyses from this date onwards"
        )

    with col3:
        search_term = st.text_input(
            "Search Request ID:",
            placeholder="Enter request ID to search"
        )

    # Get analyses
    analyses = get_analysis_history(status_filter, date_filter, search_term)

    if analyses:
        st.markdown(f"### Found {len(analyses)} analyses")

        # Display as table
        df = pd.DataFrame(analyses)

        # Parse datetime columns with proper error handling for both old and new formats
        def parse_timestamp(ts_str):
            """Parse timestamp string handling both old and new formats"""
            if pd.isna(ts_str) or ts_str == '':
                return pd.NaT

            # Handle common timestamp formats
            try:
                # Try ISO8601 format first (new format with timezone)
                return pd.to_datetime(ts_str, format='ISO8601', errors='coerce')
            except:
                try:
                    # Try parsing as ISO format without timezone (old format)
                    return pd.to_datetime(ts_str, errors='coerce')
                except:
                    try:
                        # Try parsing with pandas' flexible parser
                        return pd.to_datetime(ts_str, infer_datetime_format=True, errors='coerce')
                    except:
                        # Final fallback - log warning in debug mode
                        if DEBUG:
                            st.warning(f"Could not parse timestamp: {ts_str}")
                        return pd.NaT

        # Apply parsing to both columns
        df['created_at'] = df['created_at'].apply(parse_timestamp)
        df['updated_at'] = df['updated_at'].apply(parse_timestamp)

        display_df = df[['request_id', 'overall_status',
                         'created_at', 'updated_at']].copy()
        display_df.columns = ['Request ID', 'Status', 'Created', 'Updated']

        st.dataframe(display_df, use_container_width=True)

        # Create user-friendly dropdown options with formatted timestamps
        def format_dropdown_option(row):
            """Format dropdown option with timestamp and status"""
            request_id = row['request_id']
            status = row['overall_status']
            created_at = row['created_at']

            # Format timestamp
            if pd.notna(created_at):
                try:
                    formatted_time = created_at.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_time = str(created_at)
            else:
                formatted_time = "Unknown time"

            # Create status emoji
            status_emoji = {
                'completed': '✅',
                'processing': '🔄',
                'failed': '❌',
                'pending': '⏳'
            }.get(status, '❓')

            return f"{status_emoji} {formatted_time} - {request_id[:12]}..."

        # Create dropdown options
        dropdown_options = []
        for _, row in df.iterrows():
            dropdown_options.append(format_dropdown_option(row))

        # Show details for selected analysis
        selected_option = st.selectbox(
            "Select Analysis to View Details:",
            dropdown_options,
            format_func=lambda x: x,
            help="Select an analysis to view detailed information. The dropdown shows status, timestamp, and a shortened request ID."
        )

        # Extract request_id from selected option
        if selected_option:
            try:
                # Extract request_id from the end of the option string
                selected_id = selected_option.split(
                    " - ")[-1].replace("...", "")
                # Find the full request_id that starts with this prefix
                for _, row in df.iterrows():
                    if row['request_id'].startswith(selected_id):
                        selected_id = row['request_id']
                        break
            except:
                # Fallback: try to extract from the original format
                selected_id = selected_option

        if selected_id:
            # Show the full request ID for reference
            st.info(f"📋 Full Request ID: `{selected_id}`")
            show_analysis_details(selected_id)
    else:
        st.info("No analyses found matching the criteria.")


def show_analysis_details(request_id):
    """Show detailed analysis results"""

    # Create placeholder for progress bar
    progress_bar = st.progress(0)
    overall_status_text = st.empty()

    st.markdown(
        f'<h3 class="sub-header">📊 Analysis Details: {request_id}</h3>', unsafe_allow_html=True)

    # Get analysis details
    analysis = get_analysis_details(request_id)

    if not analysis:
        st.error(f"❌ Analysis {request_id} not found")
        return

    overall_status = analysis.get('overall_status', 'pending')
    steps_status = analysis.get(
        'analysis_result', {}).get('steps_status', {})

    # Calculate overall progress
    completed_steps = sum(1 for step in ANALYSIS_STEPS
                          if steps_status.get(step, {}).get('status') == 'completed')
    progress = (completed_steps / len(ANALYSIS_STEPS)) * 100

    # Update progress bar
    progress_bar.progress(int(progress))

    status_emoji = {
        'completed': '✅',
        'processing': '🔄',
        'failed': '❌',
        'pending': '⏳'
    }.get(overall_status, '❓')

    overall_status_text.markdown(
        f"**Overall Status:** {status_emoji} {overall_status.title()} "
        f"({completed_steps}/{len(ANALYSIS_STEPS)} steps completed)"
    )

    # Results
    result_data = analysis.get('analysis_result', {}).get('result_data', '')
    if result_data:
        # Try to load and display results
        if st.button("📥 Load Results"):
            with st.spinner("Loading results from S3..."):
                results = load_analysis_results(request_id)
                if results:
                    display_analysis_results(results)
                else:
                    st.error("❌ Failed to load results from S3")


def show_settings():
    """Show application settings"""

    st.markdown('<h2 class="sub-header">⚙️ Settings</h2>',
                unsafe_allow_html=True)

    # Environment Configuration
    st.markdown("### 🌍 Environment Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Storage Type:**", STORAGE_TYPE)
        st.write("**AWS Region:**", AWS_REGION)
        st.write("**Debug Mode:**", "Enabled" if DEBUG else "Disabled")

    with col2:
        st.write("**S3 Bucket:**", S3_BUCKET_NAME or "Not configured")
        st.write("**S3 Prefix:**", S3_PREFIX)
        st.write("**DynamoDB Table:**", DYNAMODB_TABLE_NAME)

    # API Configuration
    st.markdown("### 🔌 API Configuration")

    api_url = st.text_input(
        "API Base URL:",
        value=API_BASE_URL,
        help="Base URL for the Design Analysis API"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Test API Connection"):
            if check_api_status(api_url):
                st.success("✅ API connection successful!")
            else:
                st.error("❌ API connection failed")

    with col2:
        if st.button("Test DynamoDB Connection"):
            if check_dynamodb_status():
                st.success("✅ DynamoDB connection successful!")
            else:
                st.error("❌ DynamoDB connection failed")

    # Storage Configuration
    st.markdown("### 💾 Storage Configuration")

    if STORAGE_TYPE == "s3":
        st.info("📁 Using S3 Storage")
        st.write(f"**Bucket:** {S3_BUCKET_NAME}")
        st.write(f"**Region:** {AWS_REGION}")
        st.write(f"**Prefix:** {S3_PREFIX}")

        if st.button("Test S3 Connection"):
            if check_s3_connection():
                st.success("✅ S3 connection successful!")
            else:
                st.error("❌ S3 connection failed")
    else:
        st.info("📁 Using Local Storage")
        st.write("Analysis results will be stored locally")

    # System Information
    st.markdown("### 💻 System Information")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Python Version:**", os.sys.version)
        st.write("**Streamlit Version:**", st.__version__)
        st.write("**Environment:**", "Development" if DEBUG else "Production")

    with col2:
        st.write("**API Base URL:**", API_BASE_URL)
        st.write("**Storage Type:**", STORAGE_TYPE)
        st.write("**AWS Region:**", AWS_REGION)

    # Environment Variables (Debug Mode)
    if DEBUG:
        st.markdown("### 🔍 Environment Variables (Debug)")

        env_vars = {
            "API_HOST": os.getenv('API_HOST', 'Not set'),
            "API_PORT": os.getenv('API_PORT', 'Not set'),
            "STORAGE_TYPE": os.getenv('STORAGE_TYPE', 'Not set'),
            "S3_BUCKET_NAME": os.getenv('S3_BUCKET_NAME', 'Not set'),
            "S3_REGION": os.getenv('S3_REGION', 'Not set'),
            "S3_PREFIX": os.getenv('S3_PREFIX', 'Not set'),
            "DYNAMODB_TABLE_NAME": os.getenv('DYNAMODB_TABLE_NAME', 'Not set'),
            "DYNAMODB_REGION": os.getenv('DYNAMODB_REGION', 'Not set'),
            "AWS_REGION": os.getenv('AWS_REGION', 'Not set'),
            "DEBUG": os.getenv('DEBUG', 'Not set'),
            "OPENAI_API_KEY": "***" if os.getenv('OPENAI_API_KEY') else "Not set",
            "OPENAI_MODEL": os.getenv('OPENAI_MODEL', 'Not set'),
            "TEMPERATURE": os.getenv('TEMPERATURE', 'Not set'),
        }

        for key, value in env_vars.items():
            st.write(f"**{key}:** {value}")

# Helper functions


def check_api_status(url=None):
    """Check if API is accessible"""
    try:
        response = requests.get(f"{url or API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def check_dynamodb_status(table_name=None):
    """Check if DynamoDB is accessible"""
    try:
        from dynamodb_tracker import create_dynamodb_tracker
        tracker = create_dynamodb_tracker()
        tracker.get_table_info()
        return True
    except:
        return False


def check_s3_connection():
    """Check if S3 is accessible"""
    try:
        from s3_storage import create_s3_storage
        storage = create_s3_storage(
            bucket_name=S3_BUCKET_NAME,
            region=S3_REGION,
            prefix=S3_PREFIX
        )
        storage.get_bucket_info()
        return True
    except:
        return False


def get_analysis_status(request_id):
    """Get analysis status from DynamoDB"""
    try:
        from dynamodb_tracker import create_dynamodb_tracker
        tracker = create_dynamodb_tracker()
        return tracker.get_analysis_status(request_id)
    except Exception as e:
        st.error(f"Error getting analysis status: {e}")
        return None


def get_analysis_history(status_filter="All", date_filter=None, search_term=None):
    """Get analysis history with filters"""
    try:
        from dynamodb_tracker import create_dynamodb_tracker
        tracker = create_dynamodb_tracker()
        analyses = tracker.list_analysis_requests(limit=1000)

        # Apply filters
        if status_filter != "All":
            analyses = [a for a in analyses if a.get(
                'overall_status') == status_filter]

        if date_filter:
            date_str = date_filter.strftime('%Y-%m-%d')
            # Filter by date more robustly - handle both old and new timestamp formats
            filtered_analyses = []
            for analysis in analyses:
                created_at = analysis.get('created_at', '')
                if created_at:
                    # Handle both formats: "2025-08-31T..." and "2025-08-31T...+00:00"
                    if created_at.startswith(date_str):
                        filtered_analyses.append(analysis)
            analyses = filtered_analyses

        if search_term:
            analyses = [a for a in analyses if search_term.lower()
                        in a.get('request_id', '').lower()]

        return analyses
    except Exception as e:
        st.error(f"Error getting analysis history: {e}")
        return []


def get_analysis_details(request_id):
    """Get detailed analysis information"""
    try:
        from dynamodb_tracker import create_dynamodb_tracker
        tracker = create_dynamodb_tracker()
        return tracker.get_analysis_status(request_id)
    except Exception as e:
        st.error(f"Error getting analysis details: {e}")
        return None


def upload_file_to_s3(uploaded_file):
    """Upload file to S3 via API"""
    try:
        url = f"{API_BASE_URL}/upload"

        # Prepare file for upload
        files = {
            'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }

        response = requests.post(url, files=files, timeout=60)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(
                f"Upload API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error uploading file: {e}")
        return None


def submit_analysis(research_data, s3_file_path, implementation, include_metadata):
    """Submit a new analysis request"""
    try:
        url = f"{API_BASE_URL}/analyze"

        payload = {
            "implementation": implementation,
            "include_metadata": include_metadata
        }

        if research_data:
            payload["research_data"] = research_data
        elif s3_file_path:
            payload["s3_file_path"] = s3_file_path

        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error submitting analysis: {e}")
        return None


def load_analysis_results(request_id):
    """Load analysis results from S3"""
    try:
        from s3_storage import create_s3_storage
        storage = create_s3_storage(
            bucket_name=S3_BUCKET_NAME,
            region=S3_REGION,
            prefix=S3_PREFIX
        )
        results = storage.load_analysis(request_id)
        return results
    except Exception as e:
        st.error(f"Error loading results: {e}")
        return None


def display_analysis_results(results=None, steps_status=None, is_realtime=False):
    """Display analysis results in a formatted way - works for both real-time and final results"""

    st.markdown("### 📊 Analysis Results")

    # Create tabs for different result types
    result_tabs = st.tabs(["📝 Chunks", "🔍 Inferences",
                          "🔗 Patterns", "💡 Insights", "🎯 Design Principles"])

    # Chunks tab
    with result_tabs[0]:
        if is_realtime and steps_status:
            chunk_status = steps_status.get(
                'chunking', {}).get('status', 'pending')
            if chunk_status == 'completed':
                if results and 'chunks' in results and results['chunks']:
                    # Show first 10
                    for i, chunk in enumerate(results['chunks'][:10]):
                        with st.expander(f"Pattern {i+1}"):
                            st.write(
                                f"**Content:** {chunk.get('content', '')}")
                            st.write(f"**ID:** {chunk.get('id', '')}")
                            st.write(f"**Type:** {chunk.get('type', '')}")
                            st.write(
                                f"**Confidence:** {chunk.get('confidence', '')}")
                            if 'tags' in chunk and chunk['tags']:
                                st.write(
                                    f"**Tags:** {', '.join(chunk['tags'])}")
                            if 'source' in chunk:
                                st.write(
                                    f"**Source:** {chunk.get('source', '')}")
                else:
                    st.info("✅ Chunking completed - Loading results...")
            elif chunk_status == 'processing':
                st.info("🔄 Chunking in progress...")
                with st.spinner("Breaking down research data into chunks"):
                    st.write("**Status:** Processing")
                    st.write(
                        "**Message:** Analyzing and segmenting research data")
            elif chunk_status == 'failed':
                st.error("❌ Chunking failed")
                if steps_status.get('chunking', {}).get('message'):
                    st.write(
                        f"**Error:** {steps_status['chunking']['message']}")
            else:
                st.info("⏳ Chunking pending")
        else:
            # Final results display
            if results and 'chunks' in results and results['chunks']:
                # Show first 10
                for i, chunk in enumerate(results['chunks'][:10]):
                    with st.expander(f"Chunk {i+1}"):
                        st.write(f"**Content:** {chunk.get('content', '')}")
                        st.write(f"**ID:** {chunk.get('id', '')}")
                        st.write(f"**Type:** {chunk.get('type', '')}")
                        st.write(
                            f"**Confidence:** {chunk.get('confidence', '')}")
                        if 'tags' in chunk and chunk['tags']:
                            st.write(f"**Tags:** {', '.join(chunk['tags'])}")
                        if 'source' in chunk:
                            st.write(f"**Source:** {chunk.get('source', '')}")
            else:
                st.info("No chunks available")

    # Inferences tab
    with result_tabs[1]:
        if is_realtime and steps_status:
            inference_status = steps_status.get(
                'inferring', {}).get('status', 'pending')
            if inference_status == 'completed':
                if results and 'inferences' in results and results['inferences']:
                    for i, inference in enumerate(results['inferences'][:10]):
                        with st.expander(f"Inference {i+1}"):
                            st.write(
                                f"**Chunk ID:** {inference.get('chunk_id', '')}")
                            if 'meanings' in inference and inference['meanings']:
                                st.write(f"**Meanings:**")
                                for j, meaning in enumerate(inference['meanings']):
                                    st.write(f"  {j+1}. {meaning}")
                            st.write(
                                f"**Importance:** {inference.get('importance', '')}")
                            st.write(
                                f"**Context:** {inference.get('context', '')}")
                            st.write(
                                f"**Confidence:** {inference.get('confidence', '')}")
                            st.write(
                                f"**Reasoning:** {inference.get('reasoning', '')}")
                else:
                    st.info("✅ Inferring completed - Loading results...")
            elif inference_status == 'processing':
                st.info("🔄 Inferring in progress...")
                with st.spinner("Extracting meanings from chunks"):
                    st.write("**Status:** Processing")
                    st.write("**Message:** Analyzing chunks for deeper insights")
            elif inference_status == 'failed':
                st.error("❌ Inferring failed")
                if steps_status.get('inferring', {}).get('message'):
                    st.write(
                        f"**Error:** {steps_status['inferring']['message']}")
            else:
                st.info("⏳ Inferring pending")
        else:
            # Final results display
            if results and 'inferences' in results and results['inferences']:
                for i, inference in enumerate(results['inferences'][:10]):
                    with st.expander(f"Inference {i+1}"):
                        st.write(
                            f"**Chunk ID:** {inference.get('chunk_id', '')}")
                        if 'meanings' in inference and inference['meanings']:
                            st.write(f"**Meanings:**")
                            for j, meaning in enumerate(inference['meanings']):
                                st.write(f"  {j+1}. {meaning}")
                        st.write(
                            f"**Importance:** {inference.get('importance', '')}")
                        st.write(
                            f"**Context:** {inference.get('context', '')}")
                        st.write(
                            f"**Confidence:** {inference.get('confidence', '')}")
                        st.write(
                            f"**Reasoning:** {inference.get('reasoning', '')}")
            else:
                st.info("No inferences available")

    # Patterns tab
    with result_tabs[2]:
        if is_realtime and steps_status:
            pattern_status = steps_status.get(
                'relating', {}).get('status', 'pending')
            if pattern_status == 'completed':
                if results and 'patterns' in results and results['patterns']:
                    for i, pattern in enumerate(results['patterns'][:10]):
                        with st.expander(f"Pattern: {pattern.get('name', f'{i+1}')}"):
                            st.write(f"**Name:** {pattern.get('name', '')}")
                            st.write(
                                f"**Description:** {pattern.get('description', '')}")
                            if 'related_inferences' in pattern and pattern['related_inferences']:
                                st.write(
                                    f"**Related Inferences:** {', '.join(pattern['related_inferences'])}")
                            if 'themes' in pattern and pattern['themes']:
                                st.write(
                                    f"**Themes:** {', '.join(pattern['themes'])}")
                            st.write(
                                f"**Strength:** {pattern.get('strength', '')}")
                            st.write(
                                f"**Evidence Count:** {pattern.get('evidence_count', '')}")
                else:
                    st.info(
                        "✅ Pattern identification completed - Loading results...")
            elif pattern_status == 'processing':
                st.info("🔄 Pattern identification in progress...")
                with st.spinner("Finding relationships and patterns"):
                    st.write("**Status:** Processing")
                    st.write("**Message:** Connecting insights across chunks")
            elif pattern_status == 'failed':
                st.error("❌ Pattern identification failed")
                if steps_status.get('relating', {}).get('message'):
                    st.write(
                        f"**Error:** {steps_status['relating']['message']}")
            else:
                st.info("⏳ Pattern identification pending")
        else:
            # Final results display
            if results and 'patterns' in results and results['patterns']:
                for i, pattern in enumerate(results['patterns'][:10]):
                    with st.expander(f"Pattern: {pattern.get('name', f'{i+1}')}"):
                        st.write(f"**Name:** {pattern.get('name', '')}")
                        st.write(
                            f"**Description:** {pattern.get('description', '')}")
                        if 'related_inferences' in pattern and pattern['related_inferences']:
                            st.write(
                                f"**Related Inferences:** {', '.join(pattern['related_inferences'])}")
                        if 'themes' in pattern and pattern['themes']:
                            st.write(
                                f"**Themes:** {', '.join(pattern['themes'])}")
                        st.write(
                            f"**Strength:** {pattern.get('strength', '')}")
                        st.write(
                            f"**Evidence Count:** {pattern.get('evidence_count', '')}")
            else:
                st.info("No patterns available")

    # Insights tab
    with result_tabs[3]:
        if is_realtime and steps_status:
            insight_status = steps_status.get(
                'explaining', {}).get('status', 'pending')
            if insight_status == 'completed':
                if results and 'insights' in results and results['insights']:
                    for i, insight in enumerate(results['insights'][:10]):
                        with st.expander(f"Insight: {insight.get('headline', f'{i+1}')}"):
                            st.write(
                                f"**Headline:** {insight.get('headline', '')}")
                            st.write(
                                f"**Explanation:** {insight.get('explanation', '')}")
                            st.write(
                                f"**Pattern ID:** {insight.get('pattern_id', '')}")
                            st.write(
                                f"**Non-Consensus:** {insight.get('non_consensus', '')}")
                            st.write(
                                f"**First Principles:** {insight.get('first_principles', '')}")
                            st.write(
                                f"**Impact Score:** {insight.get('impact_score', '')}")
                            if 'supporting_evidence' in insight and insight['supporting_evidence']:
                                st.write(f"**Supporting Evidence:**")
                                for j, evidence in enumerate(insight['supporting_evidence']):
                                    st.write(f"  {j+1}. {evidence}")
                else:
                    st.info("✅ Insight generation completed - Loading results...")
            elif insight_status == 'processing':
                st.info("🔄 Insight generation in progress...")
                with st.spinner("Generating insights from patterns"):
                    st.write("**Status:** Processing")
                    st.write("**Message:** Creating actionable insights")
            elif insight_status == 'failed':
                st.error("❌ Insight generation failed")
                if steps_status.get('explaining', {}).get('message'):
                    st.write(
                        f"**Error:** {steps_status['explaining']['message']}")
            else:
                st.info("⏳ Insight generation pending")
        else:
            # Final results display
            if results and 'insights' in results and results['insights']:
                for i, insight in enumerate(results['insights'][:10]):
                    with st.expander(f"Insight: {insight.get('headline', f'{i+1}')}"):
                        st.write(
                            f"**Headline:** {insight.get('headline', '')}")
                        st.write(
                            f"**Explanation:** {insight.get('explanation', '')}")
                        st.write(
                            f"**Pattern ID:** {insight.get('pattern_id', '')}")
                        st.write(
                            f"**Non-Consensus:** {insight.get('non_consensus', '')}")
                        st.write(
                            f"**First Principles:** {insight.get('first_principles', '')}")
                        st.write(
                            f"**Impact Score:** {insight.get('impact_score', '')}")
                        if 'supporting_evidence' in insight and insight['supporting_evidence']:
                            st.write(f"**Supporting Evidence:**")
                            for j, evidence in enumerate(insight['supporting_evidence']):
                                st.write(f"  {j+1}. {evidence}")
            else:
                st.info("No insights available")

    # Design Principles tab
    with result_tabs[4]:
        if is_realtime and steps_status:
            principle_status = steps_status.get(
                'activating', {}).get('status', 'pending')
            if principle_status == 'completed':
                if results and 'design_principles' in results and results['design_principles']:
                    for i, principle in enumerate(results['design_principles'][:10]):
                        with st.expander(f"Principle: {principle.get('principle', f'{i+1}')}"):
                            st.write(
                                f"**Principle:** {principle.get('principle', '')}")
                            st.write(
                                f"**Insight ID:** {principle.get('insight_id', '')}")
                            if 'action_verbs' in principle and principle['action_verbs']:
                                st.write(
                                    f"**Action Verbs:** {', '.join(principle['action_verbs'])}")
                            st.write(
                                f"**Design Direction:** {principle.get('design_direction', '')}")
                            st.write(
                                f"**Priority:** {principle.get('priority', '')}")
                            st.write(
                                f"**Feasibility:** {principle.get('feasibility', '')}")
                else:
                    st.info("✅ Design principles completed - Loading results...")
            elif principle_status == 'processing':
                st.info("🔄 Design principles in progress...")
                with st.spinner("Creating actionable design principles"):
                    st.write("**Status:** Processing")
                    st.write(
                        "**Message:** Converting insights to design guidance")
            elif principle_status == 'failed':
                st.error("❌ Design principles failed")
                if steps_status.get('activating', {}).get('message'):
                    st.write(
                        f"**Error:** {steps_status['activating']['message']}")
            else:
                st.info("⏳ Design principles pending")
        else:
            # Final results display
            if results and 'design_principles' in results and results['design_principles']:
                for i, principle in enumerate(results['design_principles'][:10]):
                    with st.expander(f"Principle: {principle.get('principle', f'{i+1}')}"):
                        st.write(
                            f"**Principle:** {principle.get('principle', '')}")
                        st.write(
                            f"**Insight ID:** {principle.get('insight_id', '')}")
                        if 'action_verbs' in principle and principle['action_verbs']:
                            st.write(
                                f"**Action Verbs:** {', '.join(principle['action_verbs'])}")
                        st.write(
                            f"**Design Direction:** {principle.get('design_direction', '')}")
                        st.write(
                            f"**Priority:** {principle.get('priority', '')}")
                        st.write(
                            f"**Feasibility:** {principle.get('feasibility', '')}")
            else:
                st.info("No design principles available")


if __name__ == "__main__":
    main()
