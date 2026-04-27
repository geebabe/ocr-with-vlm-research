import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        .main { background-color: #f8f9fa; padding: 30px; }
        .stButton>button { 
            background-color: #28a745; 
            color: white; 
            border-radius: 8px; 
            padding: 8px 16px; 
            font-size: 16px; 
            margin-top: 10px; 
        }
        .stTextArea>label { 
            font-weight: bold; 
            color: #1a3c34; 
            font-size: 16px; 
        }
        .stImage>img { 
            border: 1px solid #e0e0e0; 
            border-radius: 8px; 
            margin-bottom: 15px; 
        }
        .sidebar .sidebar-content { 
            background-color: #ffffff; 
            padding: 20px; 
            border-right: 1px solid #e0e0e0; 
        }
        h1, h2, h3 { 
            color: #1a3c34; 
            font-family: 'Helvetica Neue', Arial, sans-serif; 
            margin-bottom: 20px; 
        }
        .stProgress .st-bo { 
            background-color: #28a745; 
        }
        .debug-expander { 
            background-color: #e6f3fa; 
            border-radius: 8px; 
            padding: 15px; 
            margin-bottom: 15px; 
        }
        .markdown-preview { 
            background-color: #ffffff; 
            padding: 20px; 
            border: 1px solid #e0e0e0; 
            border-radius: 8px; 
            min-height: 400px; 
            font-family: 'Helvetica Neue', Arial, sans-serif; 
            font-size: 16px; 
        }
        .stContainer { 
            margin-bottom: 20px; 
            padding: 15px; 
            border-radius: 8px; 
            background-color: #ffffff; 
        }
        </style>
    """, unsafe_allow_html=True)
