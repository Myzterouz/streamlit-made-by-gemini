import streamlit as st  # Import the Streamlit library for creating web applications
import pandas as pd  # Import the Pandas library for data manipulation
import os  # Import the OS library for interacting with the operating system
from datetime import datetime  # Import the datetime object for handling dates and times

# --- File Paths ---
REQUESTS_FILE = 'requests.csv'  # Define the file path for storing request data
USERS_FILE = 'users.csv'  # Define the file path for storing user data
PENDING_REGISTRATIONS_FILE = 'pending_registrations.csv'  # Define the file path for storing pending user registrations
DELETED_REQUESTS_FILE = 'deleted_requests.csv'  # Define the file path for storing deleted request data
REQUEST_HISTORY_FILE = 'request_history.csv'  # Define the file path for storing request history data

# --- Initialize DataFrames if files don't exist ---
if not os.path.exists(REQUESTS_FILE):  # Check if the requests file exists
    pd.DataFrame(columns=['id', 'user', 'request_type', 'title', 'description', 'status', 'approver_comment']).to_csv(REQUESTS_FILE, index=False)  # Create an empty DataFrame and save it as CSV if the file doesn't exist
if not os.path.exists(USERS_FILE):  # Check if the users file exists
    pd.DataFrame(columns=['username', 'role', 'approved']).to_csv(USERS_FILE, index=False)  # Create an empty DataFrame and save it as CSV if the file doesn't exist
if not os.path.exists(PENDING_REGISTRATIONS_FILE):  # Check if the pending registrations file exists
    pd.DataFrame(columns=['username', 'requested_role']).to_csv(PENDING_REGISTRATIONS_FILE, index=False)  # Create an empty DataFrame and save it as CSV if the file doesn't exist
if not os.path.exists(DELETED_REQUESTS_FILE):  # Check if the deleted requests file exists
    pd.DataFrame(columns=['id', 'user', 'request_type', 'title', 'description', 'status', 'approver_comment', 'deleted_by', 'deleted_at']).to_csv(DELETED_REQUESTS_FILE, index=False)  # Create an empty DataFrame and save it as CSV if the file doesn't exist
if not os.path.exists(REQUEST_HISTORY_FILE):  # Check if the request history file exists
    pd.DataFrame(columns=['request_id', 'timestamp', 'action', 'user', 'details']).to_csv(REQUEST_HISTORY_FILE, index=False)  # Create an empty DataFrame and save it as CSV if the file doesn't exist

# --- Load Data ---
def load_requests():
    return pd.read_csv(REQUESTS_FILE)  # Load request data from the CSV file into a DataFrame

def load_users():
    return pd.read_csv(USERS_FILE)  # Load user data from the CSV file into a DataFrame

def load_pending_registrations():
    return pd.read_csv(PENDING_REGISTRATIONS_FILE)  # Load pending registration data from the CSV file into a DataFrame

def load_deleted_requests():
    return pd.read_csv(DELETED_REQUESTS_FILE)  # Load deleted request data from the CSV file into a DataFrame

def load_request_history():
    return pd.read_csv(REQUEST_HISTORY_FILE)  # Load request history data from the CSV file into a DataFrame

def save_requests(df):
    df.to_csv(REQUESTS_FILE, index=False)  # Save the request DataFrame to the CSV file

def save_users(df):
    df.to_csv(USERS_FILE, index=False)  # Save the user DataFrame to the CSV file

def save_pending_registrations(df):
    df.to_csv(PENDING_REGISTRATIONS_FILE, index=False)  # Save the pending registration DataFrame to the CSV file

def save_deleted_requests(df):
    df.to_csv(DELETED_REQUESTS_FILE, index=False)  # Save the deleted request DataFrame to the CSV file

def save_request_history(df):
    df.to_csv(REQUEST_HISTORY_FILE, index=False)  # Save the request history DataFrame to the CSV file

# --- User Authentication and Registration ---
def register_user():
    st.subheader("User Registration")  # Display a subheader for user registration
    new_username = st.text_input("New Username")  # Create a text input field for the new username
    if st.button("Register"):  # Create a register button
        users_df = load_users()  # Load existing user data
        pending_registrations_df = load_pending_registrations()  # Load pending registration data
        if new_username in pending_registrations_df['username'].values or new_username in users_df['username'].values:  # Check if the username already exists in pending or approved users
            st.error("Username already exists or is pending approval.")  # Display an error message
        else:
            new_registration = pd.DataFrame([{'username': new_username, 'requested_role': 'user'}])  # Create a new DataFrame for the registration request with default role 'user'
            updated_pending_registrations = pd.concat([pending_registrations_df, new_registration], ignore_index=True)  # Add the new registration to the pending registrations DataFrame
            save_pending_registrations(updated_pending_registrations)  # Save the updated pending registrations
            st.success("Registration submitted for admin approval as a regular user.")  # Display a success message

def initialize_admin():
    users_df = load_users()  # Load existing user data
    if users_df.empty:  # Check if the users DataFrame is empty (first run)
        st.subheader("Initialize First Admin User")  # Display a subheader for admin initialization
        admin_username = st.text_input("Enter username for the first admin")  # Create a text input for the admin username
        if st.button("Initialize Admin"):  # Create an initialize admin button
            if admin_username in users_df['username'].values:  # Check if the admin username already exists
                st.error("Admin username already exists.")  # Display an error message
            else:
                new_admin = pd.DataFrame([{'username': admin_username, 'role': 'admin', 'approved': True}])  # Create a new DataFrame for the admin user
                updated_users = pd.concat([users_df, new_admin], ignore_index=True)  # Add the new admin to the users DataFrame
                save_users(updated_users)  # Save the updated users data
                st.success(f"Admin user '{admin_username}' created. Please log in.")  # Display a success message
                st.session_state['first_admin_initialized'] = True  # Set a session state variable to indicate admin initialization
                st.rerun()  # Rerun the Streamlit app to reflect the changes
        return True  # Return True if admin initialization UI is shown
    return False  # Return False if admin is already initialized

def login():
    st.sidebar.subheader("Login")  # Display a subheader in the sidebar for login
    username = st.sidebar.text_input("Username")  # Create a text input field in the sidebar for the username
    if st.sidebar.button("Login"):  # Create a login button in the sidebar
        users_df = load_users()  # Load existing user data
        if username in users_df['username'].values:  # Check if the entered username exists in the users data
            user_data = users_df[users_df['username'] == username].iloc[0]  # Get the user data for the logged-in user
            if user_data['approved']:  # Check if the user's registration is approved
                st.session_state['logged_in_user'] = username  # Store the logged-in username in the session state
                st.session_state['user_role'] = user_data['role']  # Store the user's role in the session state
            else:
                st.sidebar.error("Your registration is pending admin approval.")  # Display an error message if registration is pending
        else:
            st.sidebar.error("Invalid username")  # Display an error message for invalid username

def logout():
    st.session_state.pop('logged_in_user', None)  # Remove the logged-in user from the session state
    st.session_state.pop('user_role', None)  # Remove the user role from the session state
    st.session_state.pop('editing_request_id', None)  # Clear the editing request ID from the session state
    st.session_state.pop('first_admin_initialized', None) # Clear the admin initialization flag

# --- Helper Functions ---
def generate_request_id(request_type):
    now = datetime.now()  # Get the current datetime
    month_char_map = {  # Map month numbers to characters
        1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',
        10: 'A', 11: 'B', 12: 'C'
    }
    month_char = month_char_map[now.month]  # Get the character for the current month

    increment_char_map = {  # Map increment numbers to characters
        i + 1: str(i + 1) if i < 9 else chr(ord('A') + (i - 9)) for i in range(36)
    }

    requests_df = load_requests()  # Load existing request data
    filtered_df = requests_df[(requests_df['id'].str.startswith(f'{request_type}{month_char}'))]  # Filter requests by type and month
    increment = len(filtered_df) + 1  # Calculate the next increment
    increment_str = increment_char_map.get(increment, 'Z')  # Get the character for the increment, default to 'Z' if out of range

    return f"{request_type}{month_char}{increment_str}{0}"  # Return the generated request ID

def create_request(user, request_type, title, description):
    requests_df = load_requests()  # Load existing request data
    new_id = generate_request_id(request_type)  # Generate a new request ID
    new_request = pd.DataFrame([{'id': new_id, 'user': user, 'request_type': request_type, 'title': title, 'description': description, 'status': 'Pending', 'approver_comment': None}])  # Create a new DataFrame for the request
    updated_requests = pd.concat([requests_df, new_request], ignore_index=True)  # Add the new request to the requests DataFrame
    save_requests(updated_requests)  # Save the updated requests data
    log_request_history(new_id, 'Created', user, {'request_type': request_type, 'title': title, 'description': description})  # Log the creation of the request
    st.success(f"Request submitted successfully with ID: {new_id}!")  # Display a success message with the new request ID

def update_request_status(request_id, new_status, user, comment=None):
    requests_df = load_requests()  # Load existing request data
    original_request = requests_df[requests_df['id'] == request_id].iloc[0].to_dict() # Get the original request data for logging
    requests_df.loc[requests_df['id'] == request_id, 'status'] = new_status  # Update the status of the request
    requests_df.loc[requests_df['id'] == request_id, 'approver_comment'] = comment  # Add or update the approver's comment
    save_requests(requests_df)  # Save the updated requests data
    log_request_history(request_id, new_status, user, {'comment': comment} if comment else {})  # Log the status update
    st.success(f"Request {request_id} updated to {new_status}")  # Display a success message

def log_request_history(request_id, action, user, details=None):
    history_df = load_request_history()  # Load existing request history data
    new_history = pd.DataFrame([{'request_id': request_id, 'timestamp': datetime.now(), 'action': action, 'user': user, 'details': details}])  # Create a new DataFrame for the history entry
    updated_history = pd.concat([history_df, new_history], ignore_index=True)  # Add the new history entry to the history DataFrame
    save_request_history(updated_history)  # Save the updated history data

def display_requests(df, title):
    st.subheader(title)  # Display a subheader for the list of requests
    if df.empty:  # Check if the DataFrame is empty
        st.info("No requests to display.")  # Display an info message if no requests
        return
    for index, row in df.iterrows():  # Iterate through each row of the DataFrame
        st.markdown(f"**Request ID:** {row['id']}")  # Display the request ID
        st.markdown(f"**User:** {row['user']}")  # Display the user who created the request
        st.markdown(f"**Type:** {row['request_type']}")  # Display the request type
        st.markdown(f"**Title:** {row['title']}")  # Display the request title
        st.markdown(f"**Description:** {row['description']}")  # Display the request description
        st.markdown(f"**Status:** {row['status']}")  # Display the request status
        if row['approver_comment']:  # Check if there is an approver comment
            st.markdown(f"**Comment:** {row['approver_comment']}")  # Display the approver's comment
        st.divider()  # Display a visual divider

def display_request_history(request_id):
    history_df = load_request_history()  # Load existing request history data
    request_history = history_df[history_df['request_id'] == request_id].sort_values(by='timestamp', ascending=False)  # Filter history by request ID and sort by timestamp descending
    if not request_history.empty:  # Check if history exists for the request ID
        st.subheader(f"Request History (ID: {request_id})")  # Display a subheader for the request history
        for index, row in request_history.iterrows():  # Iterate through each history entry
            st.markdown(f"**Timestamp:** {row['timestamp']}")  # Display the timestamp of the action
            st.markdown(f"**Action:** {row['action']}")  # Display the action performed
            st.markdown(f"**User:** {row['user']}")  # Display the user who performed the action
            if row['details'] is not None:  # Check if there are details for the action
                st.markdown(f"**Details:** {row['details']}")  # Display the details of the action
            st.divider()  # Display a visual divider
    else:
        st.info(f"No history found for Request ID: {request_id}")  # Display an info message if no history is found

# --- Main Application Logic ---
st.title("Approval System")  # Set the title of the Streamlit application

if 'logged_in_user' not in st.session_state:  # Check if a user is logged in
    if not initialize_admin():  # If no admin is initialized, show the login screen
        login()
elif st.sidebar.button("Logout"):  # If a user is logged in and the logout button is clicked
    logout()  # Perform logout actions

if 'logged_in_user' in st.session_state:  # If a user is logged in
    st.sidebar.write(f"Logged in as: {st.session_state['logged_in_user']} ({st.session_state['user_role']})")  # Display the logged-in user and their role in the sidebar

    # --- Request Creation and Viewing for Users and Approvers ---
    if st.session_state['user_role'] in ['user', 'approver', 'admin']:  # If the logged-in user is a user, approver, or admin
        st.subheader("Create New Request")  # Display a subheader for creating a new request
        request_type = st.selectbox("Request Type", ['A', 'B', 'C', 'D', 'E', 'F'])  # Create a selectbox for the request type
        title = st.text_input("Request Title")  # Create a text input field for the request title
        description = st.text_area("Description")  # Create a text area for the request description
        if st.button("Submit Request"):  # Create a submit request button
            create_request(st.session_state['logged_in_user'], request_type, title, description)  # Call the function to create and submit the request

        user_requests_df = load_requests()  # Load existing request data
        user_requests = user_requests_df[user_requests_df['user'] == st.session_state['logged_in_user']]  # Filter requests for the current user
        display_requests(user_requests, "Your Requests")  # Display the user's requests

        # --- Handle Returned Requests for Editing ---
        returned_requests = user_requests[user_requests['status'] == 'Returned']  # Filter requests that have been returned
        if not returned_requests.empty:  # Check if there are any returned requests
            st.subheader("Returned Requests - Edit and Resubmit")  # Display a subheader for returned requests
            for index, req in returned_requests.iterrows():  # Iterate through each returned request
                with st.expander(f"Request ID: {req['id']} - Returned"):  # Create an expander for each returned request
                    st.markdown(f"**Approver Comment:** {req['approver_comment']}")  # Display the approver's comment
                    st.markdown(f"**Type:** {req['request_type']}")  # Display the request type (non-editable)
                    st.markdown(f"**Title:** {req['title']}")  # Display the request title (non-editable)
                    edit_description = st.text_area("Edit Description", value=req['description'], key=f"edit_description_{req['id']}")  # Create a text area for editing the description
                    if st.button("Resubmit Request", key=f"resubmit_{req['id']}"):  # Create a resubmit button
                        requests_df = load_requests()  # Load existing request data
                        original_request = requests_df[requests_df['id'] == req['id']].iloc[0].to_dict() # Get the original request data for logging
                        requests_df.loc[requests_df['id'] == req['id'], 'description'] = edit_description  # Update the description with the edited value
                        requests_df.loc[requests_df['id'] == req['id'], 'status'] = 'Pending'  # Set the status back to 'Pending'
                        requests_df.loc[requests_df['id'] == req['id'], 'approver_comment'] = None  # Clear the previous approver comment
                        save_requests(requests_df)  # Save the updated requests data
                        log_request_history(req['id'], 'Edited', st.session_state['logged_in_user'], {'old_details': {'description': original_request['description']}, 'new_details': {'description': edit_description}})  # Log the edit action
                        log_request_history(req['id'], 'Resubmitted', st.session_state['logged_in_user'], {})  # Log the resubmit action
                        st.success(f"Request ID {req['id']} resubmitted.")  # Display a success message
                        st.rerun()  # Rerun the Streamlit app to reflect the changes

        st.subheader("View Request History")  # Display a subheader for viewing request history
        requests_df = load_requests()  # Load existing request data
        request_ids = requests_df['id'].unique().tolist()  # Get a list of unique request IDs
        request_id_to_view = st.selectbox("Select a Request ID to view history", request_ids)  # Create a selectbox for choosing a request ID
        display_request_history(request_id_to_view)  # Call the function to display the history of the selected request

    if st.session_state['user_role'] in ['approver', 'admin']:  # If the logged-in user is an approver or admin
        st.subheader("Pending Approvals")  # Display a subheader for pending approvals
        requests_df = load_requests()  # Load existing request data
        pending_requests = requests_df[requests_df['status'] == 'Pending']  # Filter requests with 'Pending' status
        if not pending_requests.empty:  # Check if there are any pending requests
            for index, req in pending_requests.iterrows():  # Iterate through each pending request
                st.markdown(f"**Request ID:** {req['id']}")  # Display the request ID
                st.markdown(f"**User:** {req['user']}")  # Display the user who created the request
                st.markdown(f"**Type:** {req['request_type']}")  # Display the request type
                st.markdown(f"**Title:** {req['title']}")  # Display the request title
                st.markdown(f"**Description:** {req['description']}")  # Display the request description

                col1, col2, col3 = st.columns(3)  # Create three columns for approval actions
                with col1:
                    if st.button("Approve", key=f"approve_{req['id']}"):  # Create an approve button
                        update_request_status(req['id'], 'Approved', st.session_state['logged_in_user'])  # Call the function to approve the request
                        st.rerun()  # Rerun the Streamlit app to reflect the changes
                with col2:
                    deny_comment = st.text_area("Deny Comment", key=f"deny_comment_{req['id']}")  # Create a text area for the denial comment
                    if st.button("Deny", key=f"deny_{req['id']}"):  # Create a deny button
                        update_request_status(req['id'], 'Denied', st.session_state['logged_in_user'], deny_comment)  # Call the function to deny the request
                        st.rerun()  # Rerun the Streamlit app to reflect the changes
                with col3:
                    return_comment = st.text_area("Return Comment", key=f"return_comment_{req['id']}")  # Create a text area for the return comment
                    if st.button("Return", key=f"return_{req['id']}"):  # Create a return button
                        update_request_status(req['id'], 'Returned', st.session_state['logged_in_user'], return_comment)  # Call the function to return the request
                        st.rerun()  # Rerun the Streamlit app to reflect the changes
                st.divider()  # Display a visual divider
        else:
            st.info("No pending approvals.")  # Display an info message if no pending approvals

        approved_requests = requests_df[requests_df['status'] == 'Approved']  # Filter approved requests
        denied_requests = requests_df[requests_df['status'] == 'Denied']  # Filter denied requests
        returned_requests = requests_df[requests_df['status'] == 'Returned']  # Filter returned requests

        display_requests(approved_requests, "Approved Requests")  # Display the approved requests
        display_requests(denied_requests, "Denied Requests")  # Display the denied requests
        display_requests(returned_requests, "Returned Requests")  # Display the returned requests

    if st.session_state['user_role'] == 'admin':  # If the logged-in user is an admin
        st.subheader("Admin Panel")  # Display a subheader for the admin panel

        st.subheader("Pending Registrations")  # Display a subheader for pending registrations
        pending_registrations_df = load_pending_registrations()  # Load pending registration data
        if not pending_registrations_df.empty:  # Check if there are any pending registrations
            for index, reg in pending_registrations_df.iterrows():  # Iterate through each pending registration
                st.markdown(f"**Username:** {reg['username']}")  # Display the username
                st.markdown(f"**Requested Role:** user")  # Display the requested role (always 'user' now)
                col1, col2 = st.columns(2)  # Create two columns for admin actions
                with col1:
                    approve_role = st.selectbox("Approve As", ['user', 'approver', 'admin'], key=f"approve_role_{reg['username']}")  # Create a selectbox for approving the user with a specific role
                    if st.button("Approve", key=f"approve_reg_{reg['username']}"):  # Create an approve button
                        users_df = load_users()  # Load existing user data
                        if reg['username'] not in users_df['username'].values:  # Check if the username doesn't already exist
                            new_user = pd.DataFrame([{'username': reg['username'], 'role': approve_role, 'approved': True}])  # Create a new DataFrame for the approved user
                            updated_users = pd.concat([users_df, new_user], ignore_index=True)  # Add the new user to the users DataFrame
                            save_users(updated_users)  # Save the updated users data
                            updated_pending_registrations = pending_registrations_df[pending_registrations_df['username'] != reg['username']]  # Remove the approved registration from pending
                            save_pending_registrations(updated_pending_registrations)  # Save the updated pending registrations
                            st.success(f"User '{reg['username']}' approved as '{approve_role}'.")  # Display a success message
                            st.rerun()  # Rerun the Streamlit app to reflect the changes
                        else:
                            st.error(f"User '{reg['username']}' already exists.")  # Display an error message if the user already exists
                with col2:
                    if st.button("Reject", key=f"reject_reg_{reg['username']}"):  # Create a reject button
                        updated_pending_registrations = pending_registrations_df[pending_registrations_df['username'] != reg['username']]  # Remove the rejected registration from pending
                        save_pending_registrations(updated_pending_registrations)  # Save the updated pending registrations
                        st.info(f"Registration for '{reg['username']}' rejected.")  # Display an info message
                        st.rerun()  # Rerun the Streamlit app to reflect the changes
                st.divider()  # Display a visual divider
        else:
            st.info("No pending registrations.")  # Display an info message if no pending registrations

        st.subheader("User Management")  # Display a subheader for user management
        users_df = load_users()  # Load existing user data
        st.write("Edit User Roles:")  # Display a text label
        for index, user in users_df.iterrows():  # Iterate through each user
            col1, col2 = st.columns(2)  # Create two columns for user management actions
            with col1:
                st.write(f"**{user['username']}** (Current Role: {user['role']})")  # Display the username and current role
            with col2:
                new_role = st.selectbox("New Role", ['user', 'approver', 'admin'], key=f"role_select_{user['username']}", index=['user', 'approver', 'admin'].index(user['role']))  # Create a selectbox for changing the user's role
                if st.button("Change Role", key=f"change_role_{user['username']}"):  # Create a change role button
                    users_df.loc[index, 'role'] = new_role  # Update the user's role in the DataFrame
                    save_users(users_df)  # Save the updated users data
                    st.success(f"Role of '{user['username']}' changed to '{new_role}'.")  # Display a success message
                    st.rerun()  # Rerun the Streamlit app to reflect the changes
        st.dataframe(users_df)  # Display the user DataFrame

        st.subheader("All Requests")  # Display a subheader for all requests
        all_requests_df = load_requests()  # Load all request data
        display_requests(all_requests_df, "All Requests")  # Display all requests

        st.subheader("Delete Requests")  # Display a subheader for deleting requests
        request_to_delete_id = st.number_input("Enter Request ID to Delete", min_value=1, step=1)  # Create a number input for the request ID to delete
        if st.button("Delete Request"):  # Create a delete request button
            requests_df = load_requests()  # Load existing request data
            request_to_delete = requests_df[requests_df['id'] == request_to_delete_id]  # Filter the request to be deleted
            if not request_to_delete.empty:  # Check if the request ID exists
                deleted_request = request_to_delete.iloc[0].to_dict()  # Get the data of the deleted request
                deleted_request['deleted_by'] = st.session_state['logged_in_user']  # Record who deleted the request
                deleted_request['deleted_at'] = pd.Timestamp('now')  # Record the deletion timestamp
                deleted_requests_df = load_deleted_requests()  # Load deleted requests data
                updated_deleted_requests = pd.concat([deleted_requests_df, pd.Series(deleted_request).to_frame().T], ignore_index=True)  # Add the deleted request to the deleted requests DataFrame
                save_deleted_requests(updated_deleted_requests)  # Save the updated deleted requests data

                updated_requests_df = requests_df[requests_df['id'] != request_to_delete_id]  # Filter out the deleted request from the main requests DataFrame
                save_requests(updated_requests_df)  # Save the updated requests data
                log_request_history(request_to_delete_id, 'Deleted', st.session_state['logged_in_user'], {'original_details': deleted_request})  # Log the deletion action
                st.success(f"Request ID {request_to_delete_id} deleted (still available for backtracking).")  # Display a success message
                st.rerun()  # Rerun the Streamlit app to reflect the changes
            else:
                st.error(f"Request ID {request_to_delete_id} not found.")  # Display an error message if the request ID is not found

        if not load_deleted_requests().empty:  # Check if there are any deleted requests
            st.subheader("Deleted Requests (For Backtracking)")  # Display a subheader for deleted requests
            st.dataframe(load_deleted_requests())  # Display the deleted requests DataFrame

        st.subheader("Request History")  # Display a subheader for request history
        history_df = load_request_history()  # Load request history data
        if not history_df.empty:  # Check if there is any request history
            st.subheader("View Request History")  # Display a subheader for viewing history
            request_ids = load_requests()['id'].unique().tolist()  # Get a list of unique request IDs
            request_id_to_view = st.selectbox("Select a Request ID to view history", request_ids)  # Create a selectbox for choosing a request ID
            display_request_history(request_id_to_view)  # Call the function to display the history of the selected request
        else:
            st.info("No request history available.")  # Display an info message if no history is available

    else:
        st.info("You do not have permission to access this application.")  # Display a permission error if the user doesn't have access

else:
    if 'first_admin_initialized' not in st.session_state:  # Check if the first admin has been initialized
        initialize_admin()  # If not, show the admin initialization UI
    else:
        register_user()  # If admin is initialized, show the user registration UI

