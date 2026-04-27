import time
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed
from pdf2image import convert_from_bytes
import streamlit as st

from config import MAX_WORKERS
from .state import save_session_state

def convert_pdf_to_pages(uploaded_file):
    """Convert PDF to pages."""
    file_name = uploaded_file["name"]
    try:
        pages = convert_from_bytes(uploaded_file["data"], dpi=300)  # High DPI for quality
        return file_name, pages
    except Exception as e:
        return file_name, str(e)

def process_page(model, file_name, page, page_idx):
    """Process a single page using the provided model, returning OCR result and timing."""
    page_start_time = time.time()
    try:
        text = model.process_image(page)
    except Exception as e:
        text = f"Exception: {str(e)}"
    
    page_time = time.time() - page_start_time
    gc.collect()
    
    return file_name, page_idx, text, page_time

def process_documents(model, uploaded_files, status_placeholder, progress_bar, progress_text):
    # Update uploaded files in session state
    st.session_state.uploaded_files = [{"name": f.name, "data": f.read()} for f in uploaded_files]
    for f in uploaded_files:
        f.seek(0)  # Reset file pointers
    
    # Step 1: Convert PDFs to pages in parallel
    pdf_pages = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(convert_pdf_to_pages, uploaded_file): uploaded_file["name"] for uploaded_file in st.session_state.uploaded_files}
        for future in as_completed(futures):
            file_name = futures[future]
            try:
                fname, result = future.result()
                if isinstance(result, str):
                    st.error(f"Failed to convert {file_name}: {result}")
                else:
                    pdf_pages[fname] = result
            except Exception as e:
                st.error(f"Failed to convert {file_name}: {str(e)}")
            gc.collect()
    
    # Step 2: Process all pages in parallel
    all_pages = []
    total_pages = 0
    st.session_state.file_results = {}
    st.session_state.file_times = {}
    st.session_state.debug_info = {}
    
    for file_name, pages in pdf_pages.items():
        file_start_time = time.time()
        all_pages.extend([(file_name, page, i+1) for i, page in enumerate(pages)])
        total_pages += len(pages)
        st.session_state.file_times[file_name] = file_start_time
        st.session_state.file_results[file_name] = []
        st.session_state.debug_info[file_name] = {
            "pdf_size": len([f for f in st.session_state.uploaded_files if f["name"] == file_name][0]["data"]),
            "page_count": len(pages)
        }
    
    if all_pages:
        with status_placeholder.container():
            progress_text.text(f"Processing {total_pages} pages with {MAX_WORKERS} concurrent requests using {model.get_name()}...")
        
        processed_pages = 0
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_page = {executor.submit(process_page, model, file_name, page, page_idx): (file_name, page_idx) for file_name, page, page_idx in all_pages}
            for future in as_completed(future_to_page):
                file_name, page_idx = future_to_page[future]
                try:
                    file_name, page_idx, text, page_time = future.result()
                    processed_pages += 1
                    progress_bar.progress(processed_pages / total_pages)
                    progress_text.text(f"Processed {processed_pages}/{total_pages} pages")
                    st.session_state.file_results[file_name].append({
                        "page": page_idx,
                        "text": text,
                        "page_time": page_time
                    })
                except Exception as e:
                    st.error(f"Failed to process {file_name} - Page {page_idx}: {str(e)}")
                gc.collect()
        
        # Sort results by page number
        for file_name in st.session_state.file_results:
            st.session_state.file_results[file_name].sort(key=lambda x: x["page"])
        
        st.session_state.processed = True
        save_session_state()
