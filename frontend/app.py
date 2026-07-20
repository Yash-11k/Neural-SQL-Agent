import os
import streamlit as st
import requests
import pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="NeuralSQL Agent", page_icon="🤖", layout="wide")

# Sidebar Metrics & Schema
st.sidebar.title("📊 System Telemetry")

if st.sidebar.button("🔄 Refresh Stats"):
    st.rerun()

try:
    telemetry = requests.get(f"{BACKEND_URL}/analytics").json()
    st.sidebar.metric(label="Total Queries Executed", value=telemetry.get("total_queries", 0))
    st.sidebar.metric(label="Success Rate", value=f"{telemetry.get('success_rate', 0)}%")
except Exception:
    st.sidebar.error("Backend Offline")

st.sidebar.divider()
st.sidebar.markdown("### 🗄️ Database Schema")
st.sidebar.code("""
customers (cust_id, name, city)
products  (product_id, item_name, category, price)
orders    (order_id, cust_id, product_id, amount)
""", language="sql")

# Main Page
st.title("🤖 NeuralSQL Agent")
st.caption("Natural Language to SQL Engine Powered by Groq & FastAPI")

user_question = st.text_input("Apna query likho:", placeholder="e.g. Show all products with price > 500")

if st.button("Run Query 🚀", type="primary"):
    if user_question.strip():
        with st.spinner("Executing query..."):
            try:
                res = requests.post(f"{BACKEND_URL}/ask", json={"question": user_question}).json()
                
                if res.get("success"):
                    st.success("Query Executed Successfully!")
                    data = res.get("data")
                    if data:
                        df = pd.DataFrame(data)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("Query ran successfully but returned 0 rows.")
                else:
                    st.error("Query Execution Failed!")
                    
            except Exception as e:
                st.error(f"Error connecting to server: {e}")
    else:
        st.warning("Pehle question toh type karo!")