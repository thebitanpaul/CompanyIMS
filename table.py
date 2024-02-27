import streamlit as st
import sqlite3

st.title("View SQL Table Data")

# Connect to SQLite database
conn = sqlite3.connect('company_data.db')
c = conn.cursor()

# Execute SQL query to fetch all rows from the table
c.execute("SELECT * FROM companies")
rows = c.fetchall()

# Display the fetched rows
if rows:
    st.write("Table Data:")
    for row in rows:
        st.write(row)
else:
    st.write("No data found in the table.")

# Close the database connection
conn.close()
