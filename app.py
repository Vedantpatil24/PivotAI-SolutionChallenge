import streamlit as st
import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
DB_PATH = "event_memory.db"
client = genai.Client(api_key=API_KEY)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db(force_reset=False):
    conn = get_connection()
    if force_reset:
        conn.execute("DROP TABLE IF EXISTS inventory")
        conn.execute("DROP TABLE IF EXISTS tasks")
        conn.execute("DROP TABLE IF EXISTS team")

    conn.execute("CREATE TABLE IF NOT EXISTS inventory (item_name TEXT, qty INTEGER, status TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, task_name TEXT, lead_name TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS team (name TEXT, role TEXT)")


    check = conn.execute("SELECT count(*) FROM team").fetchone()[0]
    if check == 0:
        conn.execute("INSERT INTO team VALUES ('Vrinda', 'Lead'), ('Neeva', 'Support')")
        conn.execute("INSERT INTO inventory VALUES ('Gold Paint', 5, 'In-Stock'), ('Canvas', 10, 'In-Stock')")
        conn.execute("INSERT INTO tasks VALUES (1, 'Backdrop Decor', 'Vrinda')")

    conn.commit()
    conn.close()

init_db(force_reset=False)

st.set_page_config(page_title="PivotAI Final", layout="wide", page_icon="🎨")
st.title(" PivotAI: Fine Arts Command Center")
st.caption(" Prototype Ready | SPIT Fine Arts")

col1, col2 = st.columns(2)

with col1:
    st.subheader(" Inventory")
    conn = get_connection()
   
    df_inv = pd.read_sql_query(
        "SELECT item_name AS 'Item', qty AS 'Qty', status AS 'Status' FROM inventory", conn
    )
    st.table(df_inv)
    conn.close()

with col2:
    st.subheader(" Active Tasks")
    conn = get_connection()
    df_tasks = pd.read_sql_query(
        "SELECT id AS 'ID', task_name AS 'Task', lead_name AS 'Lead' FROM tasks", conn
    )
    st.table(df_tasks)
    conn.close()

# --- 3. THE AI BRAIN (ORCHESTRATOR) ---
st.divider()
st.subheader(" Report a Problem")
report = st.text_input("Describe the issue (e.g., Paint is delayed, reassign Task 1 to Neeva)")

if st.button("Execute Pivot Plan"):
    if report:
        with st.spinner("Gemini is solving the problem..."):
            conn = get_connection()
            tasks_ctx = pd.read_sql_query("SELECT * FROM tasks", conn).to_dict()
            inv_ctx = pd.read_sql_query("SELECT * FROM inventory", conn).to_dict()
            conn.close()

            response = client.models.generate_content(
    model="gemini-1.5-flash", # Use the stable, high-performance model
    contents=f"CONTEXT:\nTasks: {tasks_ctx}\nInventory: {inv_ctx}\n\nPROBLEM: {report}",
    config=types.GenerateContentConfig(
        system_instruction="You are a logistics expert. Suggest a fix. If a task needs reassigning, mention the name.",
        thinking_config=types.ThinkingConfig(include_thoughts=True)
    )
)

            thoughts = ""
            answer = ""
            for part in response.candidates[0].content.parts:
                if hasattr(part, "thought") and part.thought:
                    thoughts += part.text
                else:
                    answer += part.text

            st.success("Plan Generated")
            st.write(answer)

            with st.expander("View AI Reasoning"):
                st.write(thoughts if thoughts else "No reasoning trace available.")