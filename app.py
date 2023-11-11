import streamlit as st
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
import xml.etree.ElementTree as ET

st.set_page_config(
    page_title="Online Book Store",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.title('Online Book Store 📚')

connector_args = { 'host': st.secrets['host'], 'port': st.secrets['port'], 'user': st.secrets['user'], 'password': st.secrets['password'], 'database': st.secrets['database'] }

@st.cache_resource
def get_cursor(connector_args):
    mydb = mysql.connector.connect(**connector_args)
    return mydb

def store_data(table, data_store):
    data_store[table.tag] = []
    for row in table:
        data = {}
        for val in row:
            data[val.tag] = val.text
        data_store[table.tag].append(data)

mydb = get_cursor(connector_args)
cursor = mydb.cursor()

# cursor.execute("SHOW TABLES")
# for x in cursor:
#     st.write(x)

def progress_bar(text: str = 'Loading...'):
    my_bar = st.progress(0, text)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text)
    time.sleep(1)
    my_bar.empty()
    # st.success('Done!')

def upload_file():
    st.header('Upload XML File 📂')
    st.markdown('Upload your XML file here to store data in the database.')
    uploaded_file = st.file_uploader("Choose a file", type=['xml'])

    if uploaded_file is not None:
        progress_bar('Uploading file...')
        st.success('File uploaded successfully!')
        tree = ET.parse(uploaded_file)
        root = tree.getroot()
        data_store = {}
        for child in root:
            store_data(child, data_store)
            # st.dataframe(pd.DataFrame(data_store[child.tag]))

        if 'data_store' not in st.session_state:
            st.session_state.data_store = data_store
            st.toast('data_store created')

            create_tables = [
                "CREATE TABLE IF NOT EXISTS books (bookid INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255) NOT NULL, author VARCHAR(255) NOT NULL, price INT NOT NULL, quantity INT NOT NULL)",
                "CREATE TABLE IF NOT EXISTS users (userid INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) NOT NULL, password VARCHAR(255) NOT NULL)",
                "CREATE TABLE IF NOT EXISTS carts (cartid INT AUTO_INCREMENT PRIMARY KEY, userid INT, bookid INT, FOREIGN KEY (userid) REFERENCES users(userid), FOREIGN KEY (bookid) REFERENCES books(bookid))"
            ]

            for query in create_tables:
                cursor.execute(query)
            mydb.commit()

            for book in st.session_state.data_store['Books']:
                cursor.executemany(
                    "INSERT INTO books (bookid, title, author, price, quantity) VALUES (%s, %s, %s, %s, %s)",
                    [(book['BookID'], book['Title'], book['Author'], book['Price'], book['Quantity'])])
            mydb.commit()

            for user in st.session_state.data_store['Users']:
                cursor.execute(
                    f"INSERT INTO users (userid, username, password) VALUES ({user['UserID']}, '{user['Username']}', '{user['Password']}')")
            mydb.commit()

            for cart in st.session_state.data_store['Carts']:
                cursor.execute(
                    f"INSERT INTO carts (cartid, userid, bookid) VALUES ({cart['CartID']},{cart['UserID']}, {cart['BookID']})")
            mydb.commit()

            cursor.execute("SHOW TABLES")
            st.dataframe(pd.DataFrame(cursor.fetchall(), columns=['Tables_in_onlinebookstore']), hide_index=True)

        else:
            st.warning('Session already exists. Please terminate the session first.')
            st.toast('Tables created successfully!', icon='✅')

def view_all():
    st.header('View All Records 📄')
    st.markdown('View all records in the database.')
    if 'data_store' in st.session_state:
        # st.write(st.session_state.data_store)

        st.info('Books table')
        # get data and show as pandas dataframe
        cursor.execute("SELECT * FROM books")
        st.dataframe(pd.DataFrame(cursor.fetchall(), columns=['bookid', 'title', 'author', 'price', 'quantity']), hide_index=True)

        st.info('Users table')
        # get data and show as pandas dataframe
        cursor.execute("SELECT * FROM users")
        st.dataframe(pd.DataFrame(cursor.fetchall(), columns=['userid', 'username', 'password']), hide_index=True)

        st.info('Carts table')
        # get data and show as pandas dataframe
        cursor.execute("SELECT * FROM carts")
        st.dataframe(pd.DataFrame(cursor.fetchall(), columns=['cartid', 'userid', 'bookid']), hide_index=True)

    else:
        st.warning('Upload XML file first to view records.')

def update_records():
    st.header('Update Records 📝')
    st.markdown('Update records in the database.')
    if 'data_store' in st.session_state:
        # st.write(st.session_state.data_store
        updated_file = st.file_uploader("Choose a file", type=['xml'])
        if updated_file is not None:
            progress_bar('Uploading file...')
            st.success('File uploaded successfully!')
            tree = ET.parse(updated_file)
            root = tree.getroot()
            data_store_updated = {}
            for child in root:
                store_data(child, data_store_updated)
                # st.dataframe(pd.DataFrame(data_store[child.tag]))

            # show current data
            cursor.execute("SELECT * FROM books")
            st.dataframe(pd.DataFrame(cursor.fetchall(), columns=['bookid', 'title', 'author', 'price', 'quantity']), hide_index=True)

            # compare data_store and data_store_updated
            # if data_store_updated is different, update the database
            # else, show a warning
            # check which table is updated
            if st.button("Update Books Table", use_container_width=True):
                progress_bar('Updating books table...')
                for book in data_store_updated['Books']:
                    cursor.execute(f"SELECT * FROM books WHERE bookid={book['BookID']}")
                    if cursor.fetchone() is None:
                        cursor.execute(
                            f"INSERT INTO books (title, author, price, quantity) VALUES ( %s, %s, %s, %s)", (book['Title'], book['Author'], book['Price'], book['Quantity']))
                    else:
                        cursor.execute(
                            f"UPDATE books SET title=%s, author=%s, price=%s, quantity=%s WHERE bookid={book['BookID']}", (book['Title'], book['Author'], book['Price'], book['Quantity']))
                mydb.commit()
                st.success('Books table updated successfully!')
                cursor.execute("SELECT * FROM books")
                st.dataframe(pd.DataFrame(cursor.fetchall(), columns=['bookid', 'title', 'author', 'price', 'quantity']), hide_index=True)

            # for cart in data_store_updated['Carts']:
            #     cursor.execute(f"SELECT * FROM carts WHERE cartid={cart['CartID']}")
            #     if cursor.fetchone() is None:
            #         cursor.execute(f"INSERT INTO carts (userid, bookid) VALUES ({cart['UserID']}, {cart['BookID']})")
            #     else:
            #         cursor.execute(f"UPDATE carts SET userid={cart['UserID']}, bookid={cart['BookID']} WHERE cartid={cart['CartID']}")
            # mydb.commit()
            # st.success('Books table updated successfully!')

    else:
        st.warning('Upload XML file first to update records.')

def delete_records():
    if 'data_store' in st.session_state:
        st.header('Delete Records 🗑️')
        st.markdown('Enter ID of cart to delete.')
        cartid = st.number_input('Cart ID', min_value=1, max_value=len(st.session_state['data_store']['Carts']))
        cursor.execute("SELECT * FROM carts")
        st.dataframe(pd.DataFrame(cursor.fetchall(), columns=['cartid', 'userid', 'bookid']), hide_index=True)

        if st.button('Delete Record'):
            progress_bar('Deleting record...')
            cursor.execute(f"SELECT * FROM carts WHERE cartid={cartid}")
            if cursor.fetchone() is None:
                st.warning('Record does not exist.')
            else:
                cursor.execute(f"DELETE FROM carts WHERE cartid={cartid}")
                mydb.commit()
                st.success('Record deleted successfully!')
                cursor.execute("SELECT * FROM carts")
                st.dataframe(pd.DataFrame(cursor.fetchall(), columns=['cartid', 'userid', 'bookid']), hide_index=True)

    else:
        st.warning('Upload XML file first to delete records.')


def terminate():
    if 'data_store' in st.session_state:
        del st.session_state.data_store
        delete_tables = [
            "DROP TABLE IF EXISTS carts",
            "DROP TABLE IF EXISTS books",
            "DROP TABLE IF EXISTS users",
        ]
        for query in delete_tables:
            cursor.execute(query)
        # mydb.commit()
        # mydb.close()

        st.success('Session terminated successfully!')
    else:
        st.warning('No session to terminate.')

nav = st.sidebar.selectbox('Go to', ['Upload XML File','View All', 'Update Records', 'Delete Records', 'Terminate'])
if nav == 'Upload XML File':
    upload_file()
elif nav == 'View All':
    view_all()
elif nav == 'Update Records':
    update_records()
elif nav == 'Delete Records':
    delete_records()
elif nav == 'Terminate':
    terminate()