import streamlit as st
import pandas as pd
import os

# --- File Paths ---
REQUESTS_FILE = 'requests.csv'
USERS_FILE = 'users.csv'
PENDING_REGISTRATIONS_FILE = 'pending_registrations.csv'
DELETED_REQUESTS_FILE = 'deleted_requests.csv'

# --- Initialize DataFrames if files don't exist ---
if not os.path.exists(REQUESTS_FILE):
    pd.DataFrame(columns=['id', 'user', 'title', 'description', 'status', 'approver_comment']).to_csv(REQUESTS_FILE, index=False)
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=['username', 'role', 'approved']).to_csv(USERS_FILE, index=False)
if not os.path.exists(PENDING_REGISTRATIONS_FILE):
    pd.DataFrame(columns=['username', 'requested_role']).to_csv(PENDING_REGISTRATIONS_FILE, index=False)
if not os.path.exists(DELETED_REQUESTS_FILE):
    pd.DataFrame(columns=['id', 'user', 'title', 'description', 'status', 'approver_comment', 'deleted_by', 'deleted_at']).to_csv(DELETED_REQUESTS_FILE, index=False)

# --- Load Data ---
def load_requests():
    return pd.read_csv(REQUESTS_FILE)

def load_users():
    return pd.read_csv(USERS_FILE)

def load_pending_registrations():
    return pd.read_csv(PENDING_REGISTRATIONS_FILE)

def load_deleted_requests():
    return pd.read_csv(DELETED_REQUESTS_FILE)

def save_requests(df):
    df.to_csv(REQUESTS_FILE, index=False)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def save_pending_registrations(df):
    df.to_csv(PENDING_REGISTRATIONS_FILE, index=False)

def save_deleted_requests(df):
    df.to_csv(DELETED_REQUESTS_FILE, index=False)

# --- User Authentication and Registration ---
def register_user():
    st.subheader("User Registration")
    new_username = st.text_input("New Username")
    requested_role = st.selectbox("Requesting Role", ['user', 'approver'])
    if st.button("Register"):
        pending_registrations_df = load_pending_registrations()
        if new_username in pending_registrations_df['username'].values or new_username in load_users()['username'].values:
            st.error("Username already exists or is pending approval.")
        else:
            new_registration = pd.DataFrame([{'username': new_username, 'requested_role': requested_role}])
            updated_pending_registrations = pd.concat([pending_registrations_df, new_registration], ignore_index=True)
            save_pending_registrations(updated_pending_registrations)
            st.success("Registration submitted for admin approval.")

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

# --- Helper Functions ---
def create_request(user, title, description):
    requests_df = load_requests()
    new_id = requests_df['id'].max() + 1 if not requests_df.empty else 1
    new_request = pd.DataFrame([{'id': new_id, 'user': user, 'title': title, 'description': description, 'status': 'Pending', 'approver_comment': None}])
    updated_requests = pd.concat([requests_df, new_request], ignore_index=True)
    save_requests(updated_requests)
    st.success("Request submitted successfully!")

def update_request_status(request_id, new_status, comment=None):
    requests_df = load_requests()
    requests_df.loc[requests_df['id'] == request_id, 'status'] = new_status
    requests_df.loc[requests_df['id'] == request_id, 'approver_comment'] = comment
    save_requests(requests_df)
    st.success(f"Request {request_id} updated to {new_status}")

def display_requests(df, title):
    st.subheader(title)
    if df.empty:
        st.info("No requests to display.")
        return
    for index, row in df.iterrows():
        st.markdown(f"**Request ID:** {row['id']}")
        st.markdown(f"**User:** {row['user']}")
        st.markdown(f"**Title:** {row['title']}")
        st.markdown(f"**Description:** {row['description']}")
        st.markdown(f"**Status:** {row['status']}")
        if row['approver_comment']:
            st.markdown(f"**Comment:** {row['approver_comment']}")
        st.divider()

# --- Main Application Logic ---
st.title("Approval System")

if 'logged_in_user' not in st.session_state:
    login()
elif st.sidebar.button("Logout"):
    logout()

if 'logged_in_user' in st.session_state:
    st.sidebar.write(f"Logged in as: {st.session_state['logged_in_user']} ({st.session_state['user_role']})")

    # --- Request Creation for Users and Approvers ---
    if st.session_state['user_role'] in ['user', 'approver']:
        st.subheader("Create New Request")
        title = st.text_input("Request Title")
        description = st.text_area("Description")
        if st.button("Submit Request"):
            create_request(st.session_state['logged_in_user'], title, description)

        user_requests_df = load_requests()
        user_requests = user_requests_df[user_requests_df['user'] == st.session_state['logged_in_user']]
        display_requests(user_requests, "Your Requests")

    elif st.session_state['user_role'] == 'approver':
        st.subheader("Pending Approvals")
        requests_df = load_requests()
        pending_requests = requests_df[requests_df['status'] == 'Pending'] # Add logic to filter by approver if needed
        if not pending_requests.empty:
            for index, req in pending_requests.iterrows():
                st.markdown(f"**Request ID:** {req['id']}")
                st.markdown(f"**User:** {req['user']}")
                st.markdown(f"**Title:** {req['title']}")
                st.markdown(f"**Description:** {req['description']}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Approve", key=f"approve_{req['id']}"):
                        update_request_status(req['id'], 'Approved')
                        st.rerun()
                with col2:
                    deny_comment = st.text_area("Deny Comment", key=f"deny_comment_{req['id']}")
                    if st.button("Deny", key=f"deny_{req['id']}"):
                        update_request_status(req['id'], 'Denied', deny_comment)
                        st.rerun()
                with col3:
                    return_comment = st.text_area("Return Comment", key=f"return_comment_{req['id']}")
                    if st.button("Return", key=f"return_{req['id']}"):
                        update_request_status(req['id'], 'Returned', return_comment)
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

    elif st.session_state['user_role'] == 'admin':
        st.subheader("Admin Panel")

        st.subheader("Pending Registrations")
        pending_registrations_df = load_pending_registrations()
        if not pending_registrations_df.empty:
            for index, reg in pending_registrations_df.iterrows():
                st.markdown(f"**Username:** {reg['username']}")
                st.markdown(f"**Requested Role:** {reg['requested_role']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Approve", key=f"approve_reg_{reg['username']}"):
                        users_df = load_users()
                        if reg['username'] not in users_df['username'].values:
                            new_user = pd.DataFrame([{'username': reg['username'], 'role': reg['requested_role'], 'approved': True}])
                            updated_users = pd.concat([users_df, new_user], ignore_index=True)
                            save_users(updated_users)
                            updated_pending_registrations = pending_registrations_df[pending_registrations_df['username'] != reg['username']]
                            save_pending_registrations(updated_pending_registrations)
                            st.success(f"User '{reg['username']}' approved as '{reg['requested_role']}'.")
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
                new_role = st.selectbox("New Role", ['user', 'approver'], key=f"role_select_{user['username']}", index=['user', 'approver'].index(user['role']))
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
                st.success(f"Request ID {request_to_delete_id} deleted (still available for backtracking).")
                st.rerun()
            else:
                st.error(f"Request ID {request_to_delete_id} not found.")

        if not load_deleted_requests().empty:
            st.subheader("Deleted Requests (For Backtracking)")
            st.dataframe(load_deleted_requests())

    else:
        st.info("You do not have permission to access this application.")

else:
    register_user()
