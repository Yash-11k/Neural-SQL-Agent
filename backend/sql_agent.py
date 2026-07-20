import os
import json
import sqlite3
import pandas as pd
from groq import Groq
from db_setup import get_schema, DB_NAME

LOG_FILE = "agent_logs.jsonl"

# Helper function to write log line
def write_log(question, success, attempts):
    info = {
        "question": question,
        "success": success,
        "attempts": attempts
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(info) + "\n")

# Check if query is too vague
def is_query_ambiguous(user_question):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {"ambiguous": False, "question": None}

    client = Groq(api_key=api_key)
    prompt = f"""
    Is this user question ambiguous for database text-to-SQL?
    Question: "{user_question}"
    Schema: {get_schema()}

    Reply in JSON format:
    {{"ambiguous": true or false, "question": "clarification question if true, else null"}}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print("Ambiguity check error:", e)
        return {"ambiguous": False, "question": None}

# Agent 2: Critic Agent (Code Reviewer)
def critic_agent(user_question, sql_code):
    api_key = os.environ.get("GROQ_API_KEY")
    client = Groq(api_key=api_key)

    prompt = f"""
    Review this SQL code.
    User Question: {user_question}
    Generated SQL: {sql_code}
    Database Schema: {get_schema()}

    Check:
    1. Are column names correct according to schema? (e.g., cust_id instead of customer_id)
    2. Is it a SELECT query?

    Reply in JSON format:
    {{"approved": true or false, "reason": "reason if rejected, else null"}}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print("Critic review error:", e)
        return {"approved": True, "reason": None}

# Agent 1: SQL Generator Agent
def generator_agent(user_question, error_feedback=None):
    api_key = os.environ.get("GROQ_API_KEY")
    client = Groq(api_key=api_key)

    extra_msg = ""
    if error_feedback:
        extra_msg = f"Your previous SQL attempt failed with error: {error_feedback}. Please fix it!"

    system_prompt = f"""
    You are a helpful Text-to-SQL assistant.
    Generate valid SQLite queries for this schema:
    {get_schema()}

    Only return raw SQL code. Do not add markdown backticks like ```sql.
    {extra_msg}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]
    )

    raw_sql = response.choices[0].message.content.strip()
    # Simple clean up of backticks if LLM still includes them
    clean_sql = raw_sql.replace("```sql", "").replace("```", "").strip()
    return clean_sql

# Main function running the pipeline
def run_pipeline(user_question):
    result = {
        "question": user_question,
        "steps": [],
        "success": False,
        "data": None
    }

    last_error = None

    # Retry loop (Maximum 3 attempts)
    for attempt in range(1, 4):
        # 1. Generate SQL
        sql = generator_agent(user_question, error_feedback=last_error)

        # 2. Review with Critic Agent
        critic_res = critic_agent(user_question, sql)

        result["steps"].append({
            "attempt": attempt,
            "sql": sql,
            "critic": critic_res
        })

        # If critic rejects, retry
        if not critic_res.get("approved"):
            last_error = critic_res.get("reason")
            continue

        # 3. Simple safety check
        if not sql.upper().startswith("SELECT"):
            last_error = "Only SELECT queries are allowed for security."
            continue

        # 4. Try running in SQLite
        try:
            conn = sqlite3.connect(DB_NAME)
            df = pd.read_sql_query(sql, conn)
            conn.close()

            # Success!
            result["success"] = True
            result["data"] = df.to_dict(orient="records")
            break # Stop loop

        except Exception as err:
            last_error = str(err)

    # Save telemetry log
    write_log(user_question, result["success"], len(result["steps"]))
    return result
