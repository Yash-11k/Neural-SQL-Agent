import sys
import os

# Root directory to add in python paath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import requests

# Kept as a fallback path - used only if the FastAPI server isn't reachable
# (e.g. on Streamlit Cloud, where we can only run one process).
from backend.sql_agent import run_pipeline
from backend.db_setup import load_csv_to_db, get_dynamic_schema

st.set_page_config(page_title="NeuralSQL Agent", page_icon="", layout="wide")

# Where the FastAPI backend lives when it IS running (local dev / Docker).
# Override with an env var if you deploy the API somewhere else.
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = 20  # seconds - LLM calls can take a few seconds


def run_query(question):
    """
    Tries the FastAPI backend first (real HTTP call to /ask).
    If that fails for ANY reason (server not running, network error,
    timeout), silently falls back to calling the pipeline function
    directly in-process, so the app never breaks for the end user.
    Returns (result_dict, mode) where mode is "API" or "Direct".
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/ask",
            json={"question": question},
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        return response.json(), "API"
    except requests.exceptions.RequestException:
        return run_pipeline(question), "Direct"


def upload_csv(file):
    """
    Same pattern as run_query: try the FastAPI /upload-csv endpoint first,
    fall back to loading the CSV straight into SQLite in-process.
    """
    try:
        files = {"file": (file.name, file.getvalue(), "text/csv")}
        response = requests.post(f"{API_BASE_URL}/upload-csv", files=files, timeout=API_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data["table_name"], data["columns"], "API"
    except requests.exceptions.RequestException:
        table_name, columns = load_csv_to_db(file, table_name="user_data")
        return table_name, columns, "Direct"


# Sidebar for better ui 
st.sidebar.title(" System Telemetry")

if st.sidebar.button(" Refresh App"):
    st.rerun()

# Shows which mode the LAST query actually used, so it's honest about
# whether FastAPI was really reached or the app fell back.
last_mode = st.session_state.get("last_mode")
if last_mode == "API":
    st.sidebar.success("Status: FastAPI Backend Active ")
elif last_mode == "Direct":
    st.sidebar.info("Status: Direct Pipeline (API unreachable) ")
else:
    st.sidebar.info("Status: Direct Pipeline Active ")

st.sidebar.divider()

# --- CSV Upload Section ---
st.sidebar.markdown("###  Upload Your Own Data")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type="csv")

if uploaded_file is not None:
    if st.session_state.get("last_uploaded_name") != uploaded_file.name:
        try:
            table_name, columns, mode = upload_csv(uploaded_file)
            st.session_state["last_uploaded_name"] = uploaded_file.name
            st.sidebar.success(f"Loaded '{uploaded_file.name}' as table '{table_name}' (via {mode})")
        except Exception as e:
            st.sidebar.error(f"Could not load CSV: {e}")

st.sidebar.divider()

st.sidebar.markdown("###  Database Schema")
st.sidebar.code(get_dynamic_schema(), language="sql")

# Main Page
st.title(" NeuralSQL Agent")
st.caption("Natural Language to SQL Engine Powered by Groq AI API")

user_question = st.text_input("Write your query:", placeholder="e.g. Show all products with price > 500")

if st.button("Run Query ", type="primary"):
    if user_question.strip():
        with st.spinner("Executing query via AI Pipeline..."):
            try:
                result, mode = run_query(user_question)
                st.session_state["last_mode"] = mode

                # Check if result is a dictonary
                if isinstance(result, dict):
                    if result.get("success") and result.get("data"):
                        st.success(f"Query Executed Successfully! (via {mode})")
                        
                        # SQL Query dikhao
                        steps = result.get("steps", [])
                        if steps:
                            last_sql = steps[-1].get("sql")
                            st.code(last_sql, language="sql")
                        
                        # Data Table dikhao
                        df = pd.DataFrame(result.get("data"))
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.error("Agent query can not be executed .")
                        
                        # identify reason why query is failing 
                        steps = result.get("steps", [])
                        if steps:
                            last_reason = steps[-1].get("critic", {}).get("reason")
                            if last_reason:
                                st.warning(f" Fail Reason: {last_reason}")
                        
                        # for easy debugging json exapnder 
                        with st.expander(" View Debug Logs (JSON)"):
                            st.json(result)
                else:
                    st.write(result)
                    
            except Exception as e:
                st.error(f"Error running pipeline: {e}")
    else:
        st.warning("Write your question first!")