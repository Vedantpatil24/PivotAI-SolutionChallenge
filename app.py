import streamlit as st
import pandas as pd
import sqlite3
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables for local testing
load_dotenv()

# --- INITIAL SETUP ---
# Branding your app for the SPIT Fine Arts department [cite: 52]
st.set_page_config(page_title="PivotAI | SPIT Orchestrator", layout="wide")
st.title("🎨 PivotAI: Fine Arts Orchestrator")
st.markdown("### Google Solution Challenge 2026 | SDG 12: Responsible Consumption")

# Initialize Gemini 3 Flash Client using the 2026 stable identifier [cite: 101]
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-3-flash-preview" 

# --- DATABASE ENGINE (SQLITE WAL MODE) ---
def get_connection():
    # check_same_thread=False is required for Streamlit's multi-threaded nature
    conn = sqlite3.connect("event_memory.db", check_same_thread=False)
    # WAL mode enables high-concurrency campus environments (multi-user writes) 
    conn.execute("PRAGMA journal_mode=WAL;") 
    return conn

def init_db():
    conn = get_connection()
    # Task table to track responsibilities [cite: 83]
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            task_name TEXT,
            assigned_to TEXT,
            status TEXT
        )
    """)
    # Inventory table for SDG 12 material tracking [cite: 62, 79]
    conn.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY,
            item_name TEXT,
            quantity INTEGER,
            procured TEXT
        )
    """)
    # Seed initial data for your SPIT Fine Arts team
    if conn.execute("SELECT COUNT(*) FROM tasks").fetchone() == 0:
        conn.execute("INSERT INTO tasks (task_name, assigned_to, status) VALUES ('Stage Backdrop', 'Neeva Mehta', 'In Progress')")
        conn.execute("INSERT INTO tasks (task_name, assigned_to, status) VALUES ('Entrance Arch', 'Vrinda Damani', 'Pending')")
        conn.execute("INSERT INTO inventory (item_name, quantity, procured) VALUES ('Acrylic Red', 10, 'Yes')")
        conn.execute("INSERT INTO inventory (item_name, quantity, procured) VALUES ('MDF Boards', 5, 'No')")
    conn.commit()
    conn.close()

init_db()

# --- UI LAYERS ---
col1, col2 = st.columns()

with col1:
    st.subheader("📋 Active Task Board")
    conn = get_connection()
    # Pandas handles data preparation for the dashboard 
    tasks_df = pd.read_sql_query("SELECT * FROM tasks", conn)
    st.dataframe(tasks_df, use_container_width=True)
    
    st.subheader("📦 Inventory Tracking (SDG 12)")
    inventory_df = pd.read_sql_query("SELECT * FROM inventory", conn)
    st.dataframe(inventory_df, use_container_width=True)
    conn.close()

with col2:
    st.subheader("🤖 AI Logistics Brain")
    st.info("Report a disruption in plain English (e.g., 'Paint is delayed') [cite: 73]")
    
    report = st.text_area("Disruption Report", placeholder="Describe the logistics lag...")
    
    if st.button("Execute Pivot Plan"):
        if report:
            with st.spinner("Gemini 3 Flash is recalculating logistics... [cite: 56]"):
                # Converting DataFrames to strings for AI context
                tasks_ctx = tasks_df.to_string()
                inv_ctx = inventory_df.to_string()
                
                # The Core "Pivot" Reasoning Call [cite: 69, 93]
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=f"CONTEXT:\nTasks:\n{tasks_ctx}\n\nInventory:\n{inv_ctx}\n\nPROBLEM: {report}",
                    config=types.GenerateContentConfig(
                        system_instruction=(
                            "You are the PivotAI Orchestrator for SPIT Fine Arts. "
                            "Analyze the event state and the reported problem. "
                            "Suggest a specific 'Pivot Plan' to ensure project continuity. "
                            "If a task needs reassigning, use available names or suggest a delay. "
                            "Prioritize material conservation (SDG 12)."
                        ),
                        # Enabling thinking allows Gemini to reason through the planning 
                        thinking_config=types.ThinkingConfig(include_thoughts=True)
                    )
                )
                
                st.success("Pivot Plan Generated")
                st.write(response.text)
                
                # Expandable section to show the 'Thought' process to judges
                with st.expander("View AI Logistics Reasoning (Thinking Trace)"):
                    for part in response.candidates.content.parts:
                        if part.thought:
                            st.markdown(f"*{part.text}*")
        else:
            st.warning("Please describe a problem to pivot.")

# --- FOOTER ---
st.divider()
st.caption("Developed by Team Pixel Paradox | Sardar Patel Institute of Technology")