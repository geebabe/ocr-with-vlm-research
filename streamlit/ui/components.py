import streamlit as st
import markdown2
import time
from core.state import save_session_state, clear_session_state

def render_sidebar(available_models):
    with st.sidebar:
        st.header("Settings")
        selected_model_name = st.selectbox("Select Model", options=available_models)
        
        st.header("Uploaded Files")
        uploaded_files = st.file_uploader("Upload PDFs (max 20 files, 200MB each)", type=["pdf"], accept_multiple_files=True, key="file_uploader")
        
        if uploaded_files:
            st.write(f"Files uploaded: {len(uploaded_files)}")
            if len(uploaded_files) > 20:
                st.warning("Maximum 20 files allowed. Please upload fewer files.")
        
        status_placeholder = st.empty()
        
        # File deletion
        if st.session_state.uploaded_files:
            st.subheader("Manage Files")
            for i, file in enumerate(st.session_state.uploaded_files):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(file["name"])
                with col2:
                    if st.button("Delete", key=f"delete_{i}", type="secondary"):
                        file_name = file["name"]
                        st.session_state.uploaded_files.pop(i)
                        if file_name in st.session_state.file_results:
                            del st.session_state.file_results[file_name]
                        if file_name in st.session_state.file_times:
                            del st.session_state.file_times[file_name]
                        if file_name in st.session_state.debug_info:
                            del st.session_state.debug_info[file_name]
                        st.session_state.processed = False
                        save_session_state()
                        st.rerun()
                        
        return selected_model_name, uploaded_files, status_placeholder

def render_debug_info():
    with st.expander("Debug Information"):
        for file_name, info in st.session_state.debug_info.items():
            st.write(f"PDF: {file_name}")
            st.write(f"Size: {info['pdf_size']} bytes")
            st.write(f"Pages: {info['page_count']}")
        
        st.write("Session state keys:", list(st.session_state.keys()))
        st.write("Processed status:", st.session_state.processed)

def render_results(selected_file):
    if st.session_state.file_results:
        col1, col2 = st.columns([2, 3])
        
        with col1.container():
            st.header("Page Details")
            if selected_file:
                for result in st.session_state.file_results[selected_file]:
                    with st.container():
                        st.subheader(f"Page {result['page']}")
                        
                        # Try to detect and parse JSON
                        text_content = result["text"]
                        is_json = False
                        try:
                            # Basic check for JSON
                            if text_content.strip().startswith('{') and text_content.strip().endswith('}'):
                                import json
                                data = json.loads(text_content)
                                is_json = True
                                st.success("Structured Data Detected")
                                
                                # Flatten the data for a table if it matches our ExtractedField pattern
                                table_data = []
                                for key, val in data.items():
                                    if isinstance(val, dict) and "value" in val:
                                        bbox = val.get("bounding_box", [])
                                        table_data.append({
                                            "Field": key.replace('_', ' ').title(),
                                            "Value": val["value"],
                                            "BBox": str(bbox)
                                        })
                                    else:
                                        table_data.append({
                                            "Field": key.replace('_', ' ').title(),
                                            "Value": str(val),
                                            "BBox": "-"
                                        })
                                
                                if table_data:
                                    st.table(table_data)
                                else:
                                    st.json(data)
                        except Exception:
                            pass
                        
                        if not is_json:
                            st.text_area(f"OCR Result - Page {result['page']}", text_content, height=150, key=f"text_{selected_file}_{result['page']}")
                        
                        with st.expander("Page Debug Info"):
                            st.write(f"Processing time: {result['page_time']:.2f} seconds")
                            if is_json:
                                st.code(text_content, language="json")

        with col2.container():
            st.header("Markdown Preview")
            if selected_file:
                markdown_content = f"# OCR Results for {selected_file}\n\n"
                for result in st.session_state.file_results[selected_file]:
                    markdown_content += f"## Page {result['page']}\n\n"
                    markdown_content += f"**Processing Time**: {result['page_time']:.2f} seconds\n\n"
                    markdown_content += f"```text\n{result['text']}\n```\n\n"
                html_content = markdown2.markdown(markdown_content, extras=["fenced-code-blocks", "tables"])
                st.markdown(f'<div class="markdown-preview">{html_content}</div>', unsafe_allow_html=True)
                
                st.download_button(
                    label=f"Download Markdown for {selected_file}",
                    data=markdown_content,
                    file_name=f"ocr_{selected_file}.md",
                    mime="text/markdown"
                )

def render_processing_summary():
    with st.expander("Processing Summary"):
        for file_name, start_time in st.session_state.file_times.items():
            file_time = time.time() - start_time
            st.write(f"Total processing time for {file_name}: {file_time:.2f} seconds")
        
        all_results = []
        for file_name in st.session_state.file_results:
            for result in st.session_state.file_results[file_name]:
                all_results.append(f"File: {file_name} - Page {result['page']}\n{result['text']}")
        if all_results:
            full_text = "\n\n".join(all_results)
            st.download_button(
                label="Download Combined OCR Text",
                data=full_text,
                file_name="combined_ocr_output.txt",
                mime="text/plain"
            )

def render_advanced_options():
    with st.expander("Advanced Options"):
        if st.button("Clear Session State and Start Over"):
            clear_session_state()
            st.rerun()
