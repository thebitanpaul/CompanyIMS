import streamlit as st
import sqlite3
import pandas as pd

# Function to create a database connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

# Function to create a table in the database
def create_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS companies
                     (id INTEGER PRIMARY KEY, 
                      company_name TEXT,
                      communication TEXT,
                      legal_information TEXT,
                      activity TEXT,
                      presentation TEXT,
                      general_information TEXT,
                      remarks TEXT)''')
    except sqlite3.Error as e:
        print(e)

# Function to insert data into the database
def insert_data(conn, company_name, communication, legal_info, activity, presentation, general_info, remarks):
    try:
        c = conn.cursor()
        c.execute('''INSERT INTO companies 
                     (company_name, communication, legal_information, activity, presentation, general_information, remarks) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (company_name, communication, legal_info, activity, presentation, general_info, remarks))
        conn.commit()
        st.success("Data inserted successfully!")
    except sqlite3.Error as e:
        print(e)
        st.error("Failed to insert data.")

# Function to insert data into the database
def insert_data_excel(conn, data):
    try:
        c = conn.cursor()
        c.executemany('''INSERT INTO companies 
                     (company_name, communication, legal_information, activity, presentation, general_information, remarks) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', data)
        conn.commit()
        st.success("Data inserted successfully!")
    except sqlite3.Error as e:
        print(e)
        st.error("Failed to insert data.")

# Function to retrieve data based on company name
def search_data(conn, company_name):
    try:
        c = conn.cursor()
        c.execute('''SELECT * FROM companies WHERE company_name=?''', (company_name,))
        rows = c.fetchall()
        return rows
    except sqlite3.Error as e:
        print(e)
        return None

# Function to update data based on company name
def update_data(conn, company_name, communication, legal_info, activity, presentation, general_info, remarks):
    try:
        c = conn.cursor()
        update_query = '''UPDATE companies SET'''
        update_params = []
        if communication:
            update_query += ''' communication=?,'''
            update_params.append(communication)
        if legal_info:
            update_query += ''' legal_information=?,'''
            update_params.append(legal_info)
        if activity:
            update_query += ''' activity=?,'''
            update_params.append(activity)
        if presentation:
            update_query += ''' presentation=?,'''
            update_params.append(presentation)
        if general_info:
            update_query += ''' general_information=?,'''
            update_params.append(general_info)
        if remarks:
            update_query += ''' remarks=?,'''
            update_params.append(remarks)

        # Remove trailing comma
        update_query = update_query.rstrip(',')

        # Add WHERE clause for company_name
        update_query += ''' WHERE company_name=?'''
        update_params.append(company_name)

        # Execute the update query
        c.execute(update_query, update_params)
        
        conn.commit()
        st.success("Data updated successfully!")
    except sqlite3.Error as e:
        print(e)
        st.error("Failed to update data.")

# Function to delete data based on company name
def delete_data(conn, company_name):
    try:
        c = conn.cursor()
        c.execute('''DELETE FROM companies WHERE company_name=?''', (company_name,))
        conn.commit()
        st.success("Data deleted successfully!")
    except sqlite3.Error as e:
        print(e)
        st.error("Failed to delete data.")

# Function to handle Excel file upload and data insertion
# def upload_excel_data(conn, file):
#     try:
#         df = pd.read_excel(file)
#         for index, row in df.iterrows():
#             insert_data(conn, row['company_name'], row['communication'], row['legal_information'], row['activity'],
#                         row['presentation'], row['general_information'], row['remarks'])
#     except Exception as e:
#         print(e)
#         st.error("Failed to upload Excel data.")


# Main function
def main():
    st.title("Company Data Management App")

    # Create a database connection
    conn = create_connection("company_data.db")
    if conn is not None:
        # Create table if not exists
        create_table(conn)

        # Sidebar for user inputs
        st.sidebar.header("Add/Update Company Data")
        company_name = st.sidebar.text_input("Company Name").lower()
        communication = st.sidebar.text_input("Communication")
        legal_info = st.sidebar.text_area("Legal Information")
        activity = st.sidebar.text_area("Activity")
        presentation = st.sidebar.text_area("Presentation")
        general_info = st.sidebar.text_area("General Information")
        remarks = st.sidebar.text_area("Remarks")

        # Insert data on button click
        if st.sidebar.button("Add/Update Data"):
            if not company_name:
                st.sidebar.warning("Please enter a company name.")
                return
            else:
                existing_data = search_data(conn, company_name)
                if existing_data:
                    update_data(conn, company_name, communication, legal_info, activity, presentation, general_info, remarks)
                else:
                    insert_data(conn, company_name, communication, legal_info, activity, presentation, general_info, remarks)

        # Search for company data
        search_name = st.text_input("Enter Company Name").lower()

        if st.button("Search", key="search"):
            if not search_name:
                st.warning("Please enter a company name.")
                return
            elif search_name:
                result = search_data(conn, search_name)
                if result:
                    st.write("Company Data:")
                    for row in result:
                        data = {
                            "Company Name": row[1],
                            "Communication": row[2],
                            "Legal Information": row[3],
                            "Activity": row[4],
                            "Presentation": row[5],
                            "General Information": row[6],
                            "Remarks": row[7]
                        }
                        st.table(data)
                else:
                    st.warning("No data found for the given company name.")

        if search_name:
            # Delete company data
            if st.button("Delete Data", key="delete"):
                delete_data(conn, search_name)

        # Allow users to upload Excel file
        uploaded_file = st.sidebar.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
                # Ensure column names match
                expected_columns = ['Company Name', 'Communication', 'Legal Information', 'Activity', 'Presentation', 'General Information', 'Remarks']
                if all(col in df.columns for col in expected_columns):
                    # Convert DataFrame to list of tuples
                    data = df.to_records(index=False).tolist()
                    # Insert data into the database
                    insert_data_excel(conn, data)
                else:
                    st.error("Column names in the uploaded file do not match the expected columns.")
            except Exception as e:
                st.error(f"Error: {e}")


        # Close connection
        conn.close()
    else:
        st.error("Failed to create database connection.")

if __name__ == '__main__':
    main()
