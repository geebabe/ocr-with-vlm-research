import os
import json
import base64
import streamlit as st
from config import SESSION_FILE

def init_session_state():
    if "file_results" not in st.session_state:
        st.session_state.file_results = {}
    if "file_times" not in st.session_state:
        st.session_state.file_times = {}
    if "debug_info" not in st.session_state:
        st.session_state.debug_info = {}
    if "processed" not in st.session_state:
        st.session_state.processed = False
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

def load_session_state():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                data = json.load(f)
                st.session_state.file_results = data.get('file_results', {})
                st.session_state.file_times = {k: float(v) for k, v in data.get('file_times', {}).items()}
                st.session_state.debug_info = data.get('debug_info', {})
                st.session_state.processed = data.get('processed', False)
                st.session_state.uploaded_files = [
                    {"name": f["name"], "data": base64.b64decode(f["data"])} for f in data.get('uploaded_files', [])
                ]
        except Exception as e:
            st.error(f"Failed to load session state: {str(e)}")

def save_session_state():
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump({
                'file_results': st.session_state.file_results,
                'file_times': st.session_state.file_times,
                'debug_info': st.session_state.debug_info,
                'processed': st.session_state.processed,
                'uploaded_files': [
                    {"name": f["name"], "data": base64.b64encode(f["data"]).decode("utf-8")} for f in st.session_state.uploaded_files
                ]
            }, f)
    except Exception as e:
        st.error(f"Failed to save session state: {str(e)}")

def clear_session_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
