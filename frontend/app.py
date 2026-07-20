import sys
import os

# Root directory ko Python path me add kar rahe hain taaki backend folder import ho sake
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd

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
                result = run_pipeline(user_question)
                
                # Check if result is a dict
                if isinstance(result, dict):
                    if result.get("success") and result.get("data"):
                        st.success("Query Executed Successfully! 🎉")
                        
                        # SQL Query dikhao
                        steps = result.get("steps", [])
                        if steps:
                            last_sql = steps[-1].get("sql")
                            st.code(last_sql, language="sql")
                        
                        # Data Table dikhao
                        df = pd.DataFrame(result.get("data"))
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.error("Agent query execution complete nahi kar paya.")
                        
                        # ⚠️ EXACT FAIL REASON DIKHEGA HERE
                        steps = result.get("steps", [])
                        if steps:
                            last_reason = steps[-1].get("critic", {}).get("reason")
                            if last_reason:
                                st.warning(f"⚠️ Fail Reason: {last_reason}")
                        
                        # Debugging ke liye JSON expander me rakho
                        with st.expander("🔍 View Debug Logs (JSON)"):
                            st.json(result)
                else:
                    st.write(result)
                    
            except Exception as e:
                st.error(f"Error running pipeline: {e}")
    else:
        st.warning("Pehle question toh type karo!")