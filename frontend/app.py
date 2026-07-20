import sys
import os
import streamlit as st
import pandas as pd

# Root directory ka path add kar rahe hain taaki backend folder import ho sake
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Direct Backend functions import
from backend.sql_agent import run_pipeline, is_query_ambiguous

st.set_page_config(page_title="NeuralSQL Agent", page_icon="🤖", layout="wide")

# Sidebar
st.sidebar.title("📊 System Telemetry")

if st.sidebar.button("🔄 Refresh App"):
    st.rerun()

st.sidebar.info("Status: Direct Pipeline Active ⚡")

st.sidebar.divider()
st.sidebar.markdown("### 🗄️ Database Schema")
st.sidebar.code("""
customers (cust_id, name, city)
products  (product_id, item_name, category, price)
orders    (order_id, cust_id, product_id, amount)
""", language="sql")

# Main Page
st.title("🤖 NeuralSQL Agent")
st.caption("Natural Language to SQL Engine Powered by Groq AI")

user_question = st.text_input("Apna query likho:", placeholder="e.g. Show all products with price > 500")

if st.button("Run Query 🚀", type="primary"):
    if user_question.strip():
        with st.spinner("Executing query via AI Pipeline..."):
            try:
                # Direct function call (No FastAPI / Render needed!)
                result = run_pipeline(user_question)
                
                # Check if result is returned successfully
                if result:
                    st.success("Query Executed Successfully!")
                    
                    # Agar result pandas DataFrame hai ya list of dicts:
                    if isinstance(result, pd.DataFrame):
                        st.dataframe(result, use_container_width=True)
                    elif isinstance(result, list) and len(result) > 0:
                        df = pd.DataFrame(result)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("Query ran successfully, but returned 0 rows or plain output:")
                        st.write(result)
                else:
                    st.error("Query Execution Failed or returned empty output!")
                    
            except Exception as e:
                st.error(f"Error running pipeline: {e}")
    else:
        st.warning("Pehle question toh type karo!")