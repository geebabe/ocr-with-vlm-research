import streamlit as st
from core.state import init_session_state, load_session_state
from core.pdf_processor import process_documents
from models import get_model, get_model_names
from ui.styles import apply_custom_css
from ui.components import (
    render_sidebar, 
    render_debug_info, 
    render_results, 
    render_processing_summary, 
    render_advanced_options
)

# Apply CSS
apply_custom_css()

# Initialize and load state
init_session_state()
load_session_state()

st.title("📄 Multi-VLM OCR on PDFs")

# Get available models from registry
available_models = get_model_names()

# Render sidebar
selected_model_name, uploaded_files, status_placeholder = render_sidebar(available_models)

# Initialize the selected model
try:
    model = get_model(selected_model_name)
    if not model.is_available():
        st.error(f"{selected_model_name} backend is not ready or unreachable. Please check logs.")
        st.stop()
except Exception as e:
    st.error(f"Failed to load model {selected_model_name}: {str(e)}")
    st.stop()

# Check for new uploads or reprocessing needs
uploaded_file_names = [f.name for f in uploaded_files] if uploaded_files else []
current_file_names = [f["name"] for f in st.session_state.uploaded_files]

if uploaded_files and (not st.session_state.processed or uploaded_file_names != current_file_names):
    with status_placeholder.container():
        st.info(f"Processing PDFs in parallel with {selected_model_name}...")
        progress_bar = st.progress(0)
        progress_text = st.empty()
    
    # Process the documents
    process_documents(model, uploaded_files, status_placeholder, progress_bar, progress_text)
    
    progress_text.text("Processing complete!")
    st.rerun()

# Sidebar: File selection and summary
selected_file = None
if st.session_state.file_results:
    total_pages = sum(st.session_state.debug_info[file]["page_count"] for file in st.session_state.debug_info)
    st.sidebar.write(f"Total files: {len(st.session_state.file_results)}")
    st.sidebar.write(f"Total pages: {total_pages}")
    selected_file = st.sidebar.selectbox("Select a file to preview", options=list(st.session_state.file_results.keys()), index=0)

# Render main content
render_debug_info()
render_results(selected_file)
render_processing_summary()
render_advanced_options()