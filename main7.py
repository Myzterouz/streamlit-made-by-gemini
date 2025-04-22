import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- File Paths ---
REQUESTS_FILE = 'requests.csv'
USERS_FILE = 'users.csv'
PENDING_REGISTRATIONS_FILE = 'pending_registrations.csv'
DELETED_REQUESTS_FILE = 'deleted_requests.csv'
REQUEST_HISTORY_FILE = 'request_history.csv'

# --- Initialize DataFrames if files don't exist ---
if not os.path.exists(REQUESTS_FILE):
    pd.DataFrame(columns=['id', 'user', 'request_type', 'title', 'description', 'status', 'approver_comment']).to_csv(REQUESTS_FILE, index=False)
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=['username', 'role', 'approved']).to_csv(USERS_FILE, index=False)
if not os.path.exists(PENDING_REGISTRATIONS_FILE):
    pd.DataFrame(columns=['username', 'requested_role']).to_csv(PENDING_REGISTRATIONS_FILE, index=False)
if not os.path.exists(DELETED_REQUESTS_FILE):
    pd.DataFrame(columns=['id', 'user', 'request_type', 'title', 'description', 'status', 'approver_comment', 'deleted_by', 'deleted_at']).to_csv(DELETED_REQUESTS_FILE, index=False)
if not os.path.exists(REQUEST_HISTORY_FILE):
    pd.DataFrame(columns=['request_id', 'timestamp', 'action', 'user', 'details']).to_csv(REQUEST_HISTORY_FILE, index=False)

# --- Load Data ---
def load_requests():
    return pd.read_csv(REQUESTS_FILE)

def load_users():
    return pd.read_csv(USERS_FILE)

def load_pending_registrations():
    return pd.read_csv(PENDING_REGISTRATIONS_FILE)

def load_deleted_requests():
    return pd.read_csv(DELETED_REQUESTS_FILE)

def load_request_history():
    return pd.read_csv(REQUEST_HISTORY_FILE)

def save_requests(df):
    df.to_csv(REQUESTS_FILE, index=False)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def save_pending_registrations(df):
    df.to_csv(PENDING_REGISTRATIONS_FILE, index=False)

def save_deleted_requests(df):
    df.to_csv(DELETED_REQUESTS_FILE, index=False)

def save_request_history(df):
    df.to_csv(REQUEST_HISTORY_FILE, index=False)

# --- User Authentication and Registration ---
def register_user():
    st.subheader("User Registration")
    new_username = st.text_input("New Username")
    if st.button("Register"):
        users_df = load_users()
        pending_registrations_df = load_pending_registrations()
        if new_username in pending_registrations_df['username'].values or new_username in users_df['username'].values:
            st.error("Username already exists or is pending approval.")
        else:
            new_registration = pd.DataFrame([{'username': new_username, 'requested_role': 'user'}]) # Default to 'user'
            updated_pending_registrations = pd.concat([pending_registrations_df, new_registration], ignore_index=True)
            save_pending_registrations(updated_pending_registrations)
            st.success("Registration submitted for admin approval as a regular user.")

def initialize_admin():
    users_df = load_users()
    if users_df.empty:
        st.subheader("Initialize First Admin User")
        admin_username = st.text_input("Enter username for the first admin")
        if st.button("Initialize Admin"):
            if admin_username in users_df['username'].values:
                st.error("Admin username already exists.")
            else:
                new_admin = pd.DataFrame([{'username': admin_username, 'role': 'admin', 'approved': True}])
                updated_users = pd.concat([users_df, new_admin], ignore_index=True)
                save_users(updated_users)
                st.success(f"Admin user '{admin_username}' created. Please log in.")
                st.session_state['first_admin_initialized'] = True
                st.rerun()
        return True
    return False

def login():
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username")
    if st.sidebar.button("Login"):
        users_df = load_users()
        if username in users_df['username'].values:
            user_data = users_df[users_df['username'] == username].iloc[0]
            if user_data['approved']:
                st.session_state['logged_in_user'] = username
                st.session_state['user_role'] = user_data['role']
            else:
                st.sidebar.error("Your registration is pending admin approval.")
        else:
            st.sidebar.error("Invalid username")

def logout():
    st.session_state.pop('logged_in_user', None)
    st.session_state.pop('user_role', None)
    st.session_state.pop('editing_request_id', None) # Clear editing state
    st.session_state.pop('first_admin_initialized', None)

# --- Helper Functions ---
def generate_request_id(request_type):
    now = datetime.now()
    month_char_map = {
        1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',
        10: 'A', 11: 'B', 12: 'C'
    }
    month_char = month_char_map[now.month]

    increment_char_map = {
        i: str(i) for i in range(1, 10)
    }
    increment_char_map.update({
        10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F', 16: 'G', 17: 'H', 18: 'I',
        19: 'J', 20: 'K', 21: 'L', 22: 'M', 23: 'N', 24: 'O', 25: 'P', 26: 'Q', 27: 'R',
        28: 'S', 29: 'T', 30: 'U', 31: 'V', 32: 'W', 33: 'X', 34: 'Y', 35: 'Z'
    })

    requests_df = load_requests()
    filtered_df = requests_df[(requests_df['id'].str.startswith(f'{request_type}{month_char}'))]
    increment = len(filtered_df) + 1
    increment_str = increment_char_map.get(increment, 'Z') # Default to 'Z' if increment is very high

    return f"{request_type}{month_char}{increment_str}{0}"

def create_request(user, request_type, title, description):
    requests_df = load_requests()
    new_id = generate_request_id(request_type)
    new_request = pd.DataFrame([{'id': new_id, 'user': user, 'request_type': request_type, 'title': title, 'description': description, 'status': 'Pending', 'approver_comment': None}])
    updated_requests = pd.concat([requests_df, new_request], ignore_index=True)
    save_requests(updated_requests)
    log_request_history(new_id, 'Created', user, {'request_type': request_type, 'title': title, 'description': description})
    st.success(f"Request submitted successfully with ID: {new_id}!")

def update_request_status(request_id, new_status, user, comment=None):
    requests_df = load_requests()
    original_request = requests_df[requests_df['id'] == request_id].iloc[0].to_dict()
    requests_df.loc[requests_df['id'] == request_id, 'status'] = new_status
    requests_df.loc[requests_df['id'] == request_id, 'approver_comment'] = comment
    save_requests(requests_df)
    log_request_history(request_id, new_status, user, {'comment': comment} if comment else {})
    st.success(f"Request {request_id} updated to {new_status}")

def log_request_history(request_id, action, user, details=None):
    history_df = load_request_history()
    new_history = pd.DataFrame([{'request_id': request_id, 'timestamp': datetime.now(), 'action': action, 'user': user, 'details': details}])
    updated_history = pd.concat([history_df, new_history], ignore_index=True)
    save_request_history(updated_history)

def display_requests(df, title):
    st.subheader(title)
    if df.empty:
        st.info("No requests to display.")
        return
    for index, row in df.iterrows():
        st.markdown(f"**Request ID:** {row['id']}")
        st.markdown(f"**User:** {row['user']}")
        st.markdown(f"**Type:** {row['request_type']}")
        st.markdown(f"**Title:** {row['title']}")
        st.markdown(f"**Description:** {row['description']}")
        st.markdown(f"**Status:** {row['status']}")
        if row['approver_comment']:
            st.markdown(f"**Comment:** {row['approver_comment']}")
        st.divider()

def display_request_history(request_id):
    history_df = load_request_history()
    request_history = history_df[history_df['request_id'] == request_id].sort_values(by='timestamp', ascending=False)
    if not request_history.empty:
        st.subheader(f"Request History (ID: {request_id})")
        for index, row in request_history.iterrows():
            st.markdown(f"**Timestamp:** {row['timestamp']}")
            st.markdown(f"**Action:** {row['action']}")
            st.markdown(f"**User:** {row['user']}")
            if row['details'] is not None:
                st.markdown(f"**Details:** {row['details']}")
            st.divider()
    else:
        st.info(f"No history found for Request ID: {request_id}")

# --- Main Application Logic ---
st.title("Approval System")

if 'logged_in_user' not in st.session_state:
    if not initialize_admin():
        login()
elif st.sidebar.button("Logout"):
    logout()

if 'logged_in_user' in st.session_state:
    st.sidebar.write(f"Logged in as: {st.session_state['logged_in_user']} ({st.session_state['user_role']})")

    # --- Request Creation and Viewing for Users and Approvers ---
    if st.session_state['user_role'] in ['user', 'approver', 'admin']:
        st.subheader("Create New Request")
        request_type = st.selectbox("Request Type", ['A', 'B', 'C', 'D', 'E', 'F'])
        title = st.text_input("Request Title")
        description = st.text_area("Description")
        if st.button("Submit Request"):
            create_request(st.session_state['logged_in_user'], request_type, title, description)

        user_requests_df = load_requests()
        user_requests = user_requests_df[user_requests_df['user'] == st.session_state['logged_in_user']]
        display_requests(user_requests, "Your Requests")

        # --- Handle Returned Requests for Editing ---
        returned_requests = user_requests[user_requests['status'] == 'Returned']
        if not returned_requests.empty:
            st.subheader("Returned Requests - Edit and Resubmit")
            for index, req in returned_requests.iterrows():
                with st.expander(f"Request ID: {req['id']} - Returned"):
                    st.markdown(f"**Approver Comment:** {req['approver_comment']}")
                    st.markdown(f"**Type:** {req['request_type']}")
                    st.markdown(f"**Title:** {req['title']}")
                    edit_description = st.text_area("Edit Description", value=req['description'], key=f"edit_description_{req['id']}")
                    if st.button("Resubmit Request", key=f"resubmit_{req['id']}"):
                        requests_df = load_requests()
                        original_request = requests_df[requests_df['id'] == req['id']].iloc[0].to_dict()
                        requests_df.loc[requests_df['id'] == req['id'], 'description'] = edit_description
                        requests_df.loc[requests_df['id'] == req['id'], 'status'] = 'Pending'
                        requests_df.loc[requests_df['id'] == req['id'], 'approver_comment'] = None # Clear previous comment
                        save_requests(requests_df)
                        log_request_history(req['id'], 'Edited', st.session_state['logged_in_user'], {'old_details': {'description': original_request['description']}, 'new_details': {'description': edit_description}})
                        log_request_history(req['id'], 'Resubmitted', st.session_state['logged_in_user'], {})
                        st.success(f"Request ID {req['id']} resubmitted.")
                        st.rerun()

        st.subheader("View Request History")
        requests_df = load_requests()
        request_ids = load_requests()['id'].unique().tolist()
        request_id_to_view = st.selectbox("Select a Request ID to view history", request_ids)
        display_request_history(request_id_to_view)

    if st.session_state['user_role'] in ['approver', 'admin']:
        st.subheader("Pending Approvals")
        requests_df = load_requests()
        pending_requests = requests_df[requests_df['status'] == 'Pending'] # Add logic to filter by approver if needed
        if not pending_requests.empty:
            for index, req in pending_requests.iterrows():
                st.markdown(f"**Request ID:** {req['id']}")
                st.markdown(f"**User:** {req['user']}")
                st.markdown(f"**Type:** {req['request_type']}")
                st.markdown(f"**Title:** {req['title']}")
                st.markdown(f"**Description:** {req['description']}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Approve", key=f"approve_{req['id']}"):
                        update_request_status(req['id'], 'Approved', st.session_state['logged_in_user'])
                        st.rerun()
                with col2:
                    deny_comment = st.text_area("Deny Comment", key=f"deny_comment_{req['id']}")
                    if st.button("Deny", key=f"deny_{req['id']}"):
                        update_request_status(req['id'], 'Denied', st.session_state['logged_in_user'], deny_comment)
                        st.rerun()
                with col3:
                    return_comment = st.text_area("Return Comment", key=f"return_comment_{req['id']}")
                    if st.button("Return", key=f"return_{req['id']}"):
                        update_request_status(req['id'], 'Returned', st.session_state['logged_in_user'], return_comment)
                        st.rerun()
                st.divider()
        else:
            st.info("No pending approvals.")

        approved_requests = requests_df[requests_df['status'] == 'Approved']
        denied_requests = requests_df[requests_df['status'] == 'Denied']
        returned_requests = requests_df[requests_df['status'] == 'Returned']

        display_requests(approved_requests, "Approved Requests")
        display_requests(denied_requests, "Denied Requests")
        display_requests(returned_requests, "Returned Requests")

    if st.session_state['user_role'] == 'admin':
        st.subheader("Admin Panel")

        st.subheader("Pending Registrations")
        pending_registrations_df = load_pending_registrations()
        if not pending_registrations_df.empty:
            for index, reg in pending_registrations_df.iterrows():
                st.markdown(f"**Username:** {reg['username']}")
                st.markdown(f"**Requested Role:** user") # It will always be 'user' now
                col1, col2 = st.columns(2)
                with col1:
                    approve_role = st.selectbox("Approve As", ['user', 'approver', 'admin'], key=f"approve_role_{reg['username']}")
                    if st.button("Approve", key=f"approve_reg_{reg['username']}"):
                        users_df = load_users()
                        if reg['username'] not in users_df['username'].values:
                            new_user = pd.DataFrame([{'username': reg['username'], 'role': approve_role, 'approved': True}])
                            updated_users = pd.concat([users_df, new_user], ignore_index=True)
                            save_users(updated_users)
                            updated_pending_registrations = pending_registrations_df[pending_registrations_df['username'] != reg['username']]
                            save_pending_registrations(updated_pending_registrations)
                            st.success(f"User '{reg['username']}' approved as '{approve_role}'.")
                            st.rerun()
                        else:
                            st.error(f"User '{reg['username']}' already exists.")
                with col2:
                    if st.button("Reject", key=f"reject_reg_{reg['username']}"):
                        updated_pending_registrations = pending_registrations_df[pending_registrations_df['username'] != reg['username']]
                        save_pending_registrations(updated_pending_registrations)
                        st.info(f"Registration for '{reg['username']}' rejected.")
                        st.rerun()
                st.divider()
        else:
            st.info("No pending registrations.")

        st.subheader("User Management")
        users_df = load_users()
        st.write("Edit User Roles:")
        for index, user in users_df.iterrows():
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{user['username']}** (Current Role: {user['role']})")
            with col2:
                new_role = st.selectbox("New Role", ['user', 'approver', 'admin'], key=f"role_select_{user['username']}", index=['user', 'approver', 'admin'].index(user['role']))
                if st.button("Change Role", key=f"change_role_{user['username']}"):
                    users_df.loc[index, 'role'] = new_role
                    save_users(users_df)
                    st.success(f"Role of '{user['username']}' changed to '{new_role}'.")
                    st.rerun()
        st.dataframe(users_df)

        st.subheader("All Requests")
        all_requests_df = load_requests()
        display_requests(all_requests_df, "All Requests")

        st.subheader("Delete Requests")
        request_to_delete_id = st.number_input("Enter Request ID to Delete", min_value=1, step=1)
        if st.button("Delete Request"):
            requests_df = load_requests()
            request_to_delete = requests_df[requests_df['id'] == request_to_delete_id]
            if not request_to_delete.empty:
                deleted_request = request_to_delete.iloc[0].to_dict()
                deleted_request['deleted_by'] = st.session_state['logged_in_user']
                deleted_request['deleted_at'] = pd.Timestamp('now')
                deleted_requests_df = load_deleted_requests()
                updated_deleted_requests = pd.concat([deleted_requests_df, pd.Series(deleted_request).to_frame().T], ignore_index=True)
                save_deleted_requests(updated_deleted_requests)

                updated_requests_df = requests_df[requests_df['id'] != request_to_delete_id]
                save_requests(updated_requests_df)
                log_request_history(request_to_delete_id, 'Deleted', st.session_state['logged_in_user'], {'original_details': deleted_request})
                st.success(f"Request ID {request_to_delete_id} deleted (still available for backtracking).")
                st.rerun()
            else:
                st.error(f"Request ID {request_to_delete_id} not found.")

        if not load_deleted_requests().empty:
            st.subheader("Deleted Requests (For Backtracking)")
            st.dataframe(load_deleted_requests())

        st.subheader("Request History")
        history_df = load_request_history()
        if not history_df.empty:
            st.subheader("View Request History")
            request_ids = load_requests()['id'].unique().tolist()
            request_id_to_view = st.selectbox("Select a Request ID to view history", request_ids)
            display_request_history(request_id_to_view)
        else:
            st.info("No request history available.")

    else:
        st.info("You do not have permission to access this application.")

else:
    if 'first_admin_initialized' not in st.session_state:
        initialize_admin()
    else:
        register_user()
