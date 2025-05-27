import streamlit as st
import pandas as pd
import pyodbc
import sqlite3
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="Database Filter Tool", layout="wide")
st.title("🗃️ Database Column Filter Tool")

# Upload file
db_file = st.file_uploader("Upload a Microsoft Access (.mdb, .accdb) or SQLite (.db, .sql) file", type=["mdb", "accdb", "db", "sql"])

if db_file:
    file_ext = db_file.name.split('.')[-1].lower()
    conn = None
    table_names = []
    temp_path = f"temp_{db_file.name}"

    if file_ext in ["mdb", "accdb"]:
        st.info("Connecting to Microsoft Access database...")
        with open(temp_path, "wb") as f:
            f.write(db_file.read())

        access_conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={os.path.abspath(temp_path)};'
        )
        conn = pyodbc.connect(access_conn_str)
        cursor = conn.cursor()
        table_names = [row.table_name for row in cursor.tables(tableType='TABLE')]

    elif file_ext in ["db", "sql"]:
        st.info("Connecting to SQLite database...")
        with open(temp_path, "wb") as f:
            f.write(db_file.read())

        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [row[0] for row in cursor.fetchall()]

    if conn and table_names:
        table = st.selectbox("Select a table to filter", table_names)
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
        st.subheader("📊 Preview of Data")
        st.dataframe(df.head(100))

        columns = st.multiselect("Select columns to filter", df.columns)
        filters = {}
        for col in columns:
            filter_type = st.selectbox(f"Filter for '{col}'", ["Contains", "Equals", "Starts with", "Ends with"], key=col)
            user_values = st.text_input(f"Enter value(s) for '{col}' (comma-separated)", key=f"{col}_val")
            if user_values:
                filters[col] = {
                    "type": filter_type,
                    "values": [v.strip() for v in user_values.split(',') if v.strip()]
                }

        if st.button("Apply Filters"):
            # Build WHERE clause dynamically
            conditions = []
            for col, f in filters.items():
                sub = []
                for val in f["values"]:
                    val_escaped = val.replace("'", "''")
                    if f["type"] == "Contains":
                        sub.append(f"{col} LIKE '%{val_escaped}%'")
                    elif f["type"] == "Equals":
                        sub.append(f"{col} = '{val_escaped}'")
                    elif f["type"] == "Starts with":
                        sub.append(f"{col} LIKE '{val_escaped}%'")
                    elif f["type"] == "Ends with":
                        sub.append(f"{col} LIKE '%{val_escaped}'")
                if sub:
                    conditions.append(f"({' OR '.join(sub)})")

            where_clause = " AND ".join(conditions)
            query = f"SELECT * FROM {table}"
            if where_clause:
                query += f" WHERE {where_clause}"

            filtered_df = pd.read_sql(query, conn)
            st.subheader("✅ Filtered Results")
            st.dataframe(filtered_df)

            st.subheader("📈 Summary Statistics")
            st.write(filtered_df.describe(include="all"))

            # Download
            st.download_button(
                "📥 Download Filtered Data (CSV)",
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name="filtered_data.csv",
                mime="text/csv"
            )

    if conn:
        conn.close()
        if os.path.exists(temp_path):
            os.remove(temp_path)
