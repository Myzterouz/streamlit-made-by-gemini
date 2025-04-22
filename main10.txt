import streamlit as st
import pandas as pd
import os
from datetime import datetime

class DataManager:
    def __init__(self, requests_file='requests.csv', users_file='users.csv',
                 pending_registrations_file='pending_registrations.csv',
                 deleted_requests_file='deleted_requests.csv',
                 request_history_file='request_history.csv'):
        self.requests_file = requests_file
        self.users_file = users_file
        self.pending_registrations_file = pending_registrations_file
        self.deleted_requests_file = deleted_requests_file
        self.request_history_file = request_history_file
        self._initialize_dataframes()

    def _initialize_dataframes(self):
        if not os.path.exists(self.requests_file):
            pd.DataFrame(columns=['id', 'user', 'request_type', 'title', 'description', 'status', 'approver_comment']).to_csv(self.requests_file, index=False)
        if not os.path.exists(self.users_file):
            pd.DataFrame(columns=['username', 'role', 'approved']).to_csv(self.users_file, index=False)
        if not os.path.exists(self.pending_registrations_file):
            pd.DataFrame(columns=['username', 'requested_role']).to_csv(self.pending_registrations_file, index=False)
        if not os.path.exists(self.deleted_requests_file):
            pd.DataFrame(columns=['id', 'user', 'request_type', 'title', 'description', 'status', 'approver_comment', 'deleted_by', 'deleted_at']).to_csv(self.deleted_requests_file, index=False)
        if not os.path.exists(self.request_history_file):
            pd.DataFrame(columns=['request_id', 'timestamp', 'action', 'user', 'details']).to_csv(self.request_history_file, index=False)

    def load_requests(self):
        return pd.read_csv(self.requests_file)

    def load_users(self):
        return pd.read_csv(self.users_file)

    def load_pending_registrations(self):
        return pd.read_csv(self.pending_registrations_file)

    def load_deleted_requests(self):
        return pd.read_csv(self.deleted_requests_file)

    def load_request_history(self):
        return pd.read_csv(self.request_history_file)

    def save_requests(self, df):
        df.to_csv(self.requests_file, index=False)

    def save_users(self, df):
        df.to_csv(self.users_file, index=False)

    def save_pending_registrations(self, df):
        df.to_csv(self.pending_registrations_file, index=False)

    def save_deleted_requests(self, df):
        df.to_csv(self.deleted_requests_file, index=False)

    def save_request_history(self, df):
        df.to_csv(self.request_history_file, index=False)

class RequestManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def generate_request_id(self, request_type):
        now = datetime.now()
        month_char_map = {
            1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',
            10: 'A', 11: 'B', 12: 'C'
        }
        month_char = month_char_map[now.month]

        increment_char_map = {
            i + 1: str(i + 1) if i < 9 else chr(ord('A') + (i - 9)) for i in range(36)
        }

        requests_df = self.data_manager.load_requests()
        filtered_df = requests_df[(requests_df['id'].str.startswith(f'{request_type}{month_char}'))]
        increment = len(filtered_df) + 1
        increment_str = increment_char_map.get(increment, 'Z')

        return f"{request_type}{month_char}{increment_str}{0}"

    def create_request(self, user, request_type, title, description):
        requests_df = self.data_manager.load_requests()
        new_id = self.generate_request_id(request_type)
        new_request = pd.DataFrame([{'id': new_id, 'user': user, 'request_type': request_type, 'title': title, 'description': description, 'status': 'Pending', 'approver_comment': None}])
        updated_requests = pd.concat([requests_df, new_request], ignore_index=True)
        self.data_manager.save_requests(updated_requests)
        self.log_request_history(new_id, 'Created', user, {'request_type': request_type, 'title': title, 'description': description})
        st.success(f"Request submitted successfully with ID: {new_id}!")

    def update_request_status(self, request_id, new_status, user, comment=None):
        requests_df = self.data_manager.load_requests()
        original_request = requests_df[requests_df['id'] == request_id].iloc[0].to_dict()
        requests_df.loc[requests_df['id'] == request_id, 'status'] = new_status
        requests_df.loc[requests_df['id'] == request_id, 'approver_comment'] = comment
        self.data_manager.save_requests(requests_df)
        self.log_request_history(request_id, new_status, user, {'comment': comment} if comment else {})
        st.success(f"Request {request_id} updated to {new_status}")

    def log_request_history(self, request_id, action, user, details=None):
        history_df = self.data_manager.load_request_history()
        new_history = pd.DataFrame([{'request_id': request_id, 'timestamp': datetime.now(), 'action': action, 'user': user, 'details': details}])
        updated_history = pd.concat([history_df, new_history], ignore_index=True)
        self.data_manager.save_request_history(updated_history)

    def get_user_requests(self, user):
        requests_df = self.data_manager.load_requests()
        return requests_df[requests_df['user'] == user]

    def get_pending_requests(self):
        requests_df = self.data_manager.load_requests()
        return requests_df[requests_df['status'] == 'Pending']

    def get_approved_requests(self):
        requests_df = self.data_manager.load_requests()
        return requests_df[requests_df['status'] == 'Approved']

    def get_denied_requests(self):
        requests_df = self.data_manager.load_requests()
        return requests_df[requests_df['status'] == 'Denied']

    def get_returned_requests(self):
        requests_df = self.data_manager.load_requests()
        return requests_df[requests_df['status'] == 'Returned']

    def get_request_by_id(self, request_id):
        requests_df = self.data_manager.load_requests()
        return requests_df[requests_df['id'] == request_id].iloc[0]

class UserManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def register_user(self, new_username):
        users_df = self.data_manager.load_users()
        pending_registrations_df = self.data_manager.load_pending_registrations()
        if new_username in pending_registrations_df['username'].values or new_username in users_df['username'].values:
            st.error("Username already exists or is pending approval.")
            return False
        else:
            new_registration = pd.DataFrame([{'username': new_username, 'requested_role': 'user'}])
            updated_pending_registrations = pd.concat([pending_registrations_df, new_registration], ignore_index=True)
            self.data_manager.save_pending_registrations(updated_pending_registrations)
            st.success("Registration submitted for admin approval as a regular user.")
            return True

    def initialize_admin(self):
        users_df = self.data_manager.load_users()
        if users_df.empty:
            st.subheader("Initialize First Admin User")
            admin_username = st.text_input("Enter username for the first admin")
            if st.button("Initialize Admin"):
                if admin_username in users_df['username'].values:
                    st.error("Admin username already exists.")
                else:
                    new_admin = pd.DataFrame([{'username': admin_username, 'role': 'admin', 'approved': True}])
                    updated_users = pd.concat([users_df, new_admin], ignore_index=True)
                    self.data_manager.save_users(updated_users)
                    st.success(f"Admin user '{admin_username}' created. Please log in.")
                    st.session_state['first_admin_initialized'] = True
                    st.rerun()
                return True
        return False

    def login(self, username):
        users_df = self.data_manager.load_users()
        if username in users_df['username'].values:
            user_data = users_df[users_df['username'] == username].iloc[0]
            if user_data['approved']:
                st.session_state['logged_in_user'] = username
                st.session_state['user_role'] = user_data['role']
                return True
            else:
                st.sidebar.error("Your registration is pending admin approval.")
                return False
        else:
            st.sidebar.error("Invalid username")
            return False

    def logout(self):
        st.session_state.pop('logged_in_user', None)
        st.session_state.pop('user_role', None)
        st.session_state.pop('editing_request_id', None)
        st.session_state.pop('first_admin_initialized', None)

    def get_pending_registrations(self):
        return self.data_manager.load_pending_registrations()

    def approve_registration(self, username, role):
        users_df = self.data_manager.load_users()
        pending_registrations_df = self.data_manager.load_pending_registrations()
        if username not in users_df['username'].values:
            new_user = pd.DataFrame([{'username': username, 'role': role, 'approved': True}])
            updated_users = pd.concat([users_df, new_user], ignore_index=True)
            self.data_manager.save_users(updated_users)
            updated_pending_registrations = pending_registrations_df[pending_registrations_df['username'] != username]
            self.data_manager.save_pending_registrations(updated_pending_registrations)
            st.success(f"User '{username}' approved as '{role}'.")
            return True
        else:
            st.error(f"User '{username}' already exists.")
            return False

    def reject_registration(self, username):
        pending_registrations_df = self.data_manager.load_pending_registrations()
        updated_pending_registrations = pending_registrations_df[pending_registrations_df['username'] != username]
        self.data_manager.save_pending_registrations(updated_pending_registrations)
        st.info(f"Registration for '{username}' rejected.")
        return True

    def get_all_users(self):
        return self.data_manager.load_users()

    def change_user_role(self, username, new_role):
        users_df = self.data_manager.load_users()
        users_df.loc[users_df['username'] == username, 'role'] = new_role
        self.data_manager.save_users(users_df)
        st.success(f"Role of '{username}' changed to '{new_role}'.")
        return True

class DisplayManager:
    def display_requests(self, df, title):
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

    def display_request_history(self, request_id, history_df):
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

    def display_pending_registrations(self, df):
        if not df.empty:
            for index, reg in df.iterrows():
                st.markdown(f"**Username:** {reg['username']}")
                st.markdown(f"**Requested Role:** user")
                col1, col2 = st.columns(2)
                with col1:
                    approve_role = st.selectbox("Approve As", ['user', 'approver', 'admin'], key=f"approve_role_{reg['username']}")
                    if st.button("Approve", key=f"approve_reg_{reg['username']}"):
                        return 'approve', reg['username'], approve_role
                with col2:
                    if st.button("Reject", key=f"reject_reg_{reg['username']}"):
                        return 'reject', reg['username'], None
                st.divider()
        else:
            st.info("No pending registrations.")
        return None, None, None

    def display_all_users(self, df):
        st.write("Edit User Roles:")
        for index, user in df.iterrows():
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{user['username']}** (Current Role: {user['role']})")
            with col2:
                new_role = st.selectbox("New Role", ['user', 'approver', 'admin'], key=f"role_select_{user['username']}", index=['user', 'approver', 'admin'].index(user['role']))
                if st.button("Change Role", key=f"change_role_{user['username']}"):
                    return 'change_role', user['username'], new_role
        st.dataframe(df)
        return None, None, None

    def display_deleted_requests(self, df):
        if not df.empty:
            st.subheader("Deleted Requests (For Backtracking)")
            st.dataframe(df)

class AdminPanel:
    def __init__(self, user_manager, display_manager, request_manager):
        self.user_manager = user_manager
        self.display_manager = display_manager
        self.request_manager = request_manager

    def show(self):
        st.subheader("Admin Panel")

        st.subheader("Pending Registrations")
        pending_registrations = self.user_manager.get_pending_registrations()
        action, username, role = self.display_manager.display_pending_registrations(pending_registrations)
        if action == 'approve' and username:
            self.user_manager.approve_registration(username, role)
            st.rerun()
        elif action == 'reject' and username:
            self.user_manager.reject_registration(username)
            st.rerun()

        st.subheader("User Management")
        all_users = self.user_manager.get_all_users()
        user_action, edit_username, new_role = self.display_manager.display_all_users(all_users)
        if user_action == 'change_role' and edit_username and new_role:
            self.user_manager.change_user_role(edit_username, new_role)
            st.rerun()

        st.subheader("All Requests")
        all_requests = self.request_manager.data_manager.load_requests()
        self.display_manager.display_requests(all_requests, "All Requests")

        st.subheader("Delete Requests")
        request_to_delete_id = st.number_input("Enter Request ID to Delete", min_value=1, step=1)
        if st.button("Delete Request"):
            request_to_delete = self.request_manager.data_manager.load_requests()
            request_to_delete = request_to_delete[request_to_delete['id'] == request_to_delete_id]
            if not request_to_delete.empty:
                deleted_request = request_to_delete.iloc[0].to_dict()
                deleted_request['deleted_by'] = st.session_state['logged_in_user']
                deleted_request['deleted_at'] = pd.Timestamp('now')
                deleted_requests_df = self.request_manager.data_manager.load_deleted_requests()
                updated_deleted_requests = pd.concat([deleted_requests_df, pd.Series(deleted_request).to_frame().T], ignore_index=True)
                self.request_manager.data_manager.save_deleted_requests(updated_deleted_requests)

                updated_requests_df = self.request_manager.data_manager.load_requests()
                updated_requests_df = updated_requests_df[updated_requests_df['id'] != request_to_delete_id]
                self.request_manager.data_manager.save_requests(updated_requests_df)
                self.request_manager.log_request_history(request_to_delete_id, 'Deleted', st.session_state['logged_in_user'], {'original_details': deleted_request})
                st.success(f"Request ID {request_to_delete_id} deleted (still available for backtracking).")
                st.rerun()
            else:
                st.error(f"Request ID {request_to_delete_id} not found.")

        self.display_manager.display_deleted_requests(self.request_manager.data_manager.load_deleted_requests())

        st.subheader("Request History")
        history_df = self.request_manager.data_manager.load_request_history()
        if not history_df.empty:
            st.subheader("View Request History")
            request_ids = self.request_manager.data_manager.load_requests()['id'].unique().tolist()
            request_id_to_view = st.selectbox("Select a Request ID to view history", request_ids)
            self.display_manager.display_request_history(request_id_to_view, history_df)
        else:
            st.info("No request history available.")

class ApprovalApp:
    def __init__(self):
        self.data_manager = DataManager()
        self.user_manager = UserManager(self.data_manager)
        self.request_manager = RequestManager(self.data_manager)
        self.display_manager = DisplayManager()
        self.admin_panel = AdminPanel(self.user_manager, self.display_manager, self.request_manager)

    def run(self):
        st.title("Approval System")

        if 'logged_in_user' not in st.session_state:
            if not self.user_manager.initialize_admin():
                self.login_ui()
        elif st.sidebar.button("Logout"):
            self.user_manager.logout()

        if 'logged_in_user' in st.session_state:
            st.sidebar.write(f"Logged in as: {st.session_state['logged_in_user']} ({st.session_state['user_role']})")
            self.main_ui()
        else:
            if 'first_admin_initialized' not in st.session_state:
                pass # Admin initialization is handled in UserManager
            else:
                self.register_ui()

    def register_ui(self):
        st.subheader("User Registration")
        new_username = st.text_input("New Username")
        if st.button("Register"):
            self.user_manager.register_user(new_username)

    def login_ui(self):
        st.sidebar.subheader("Login")
        username = st.sidebar.text_input("Username")
        if st.sidebar.button("Login"):
            self.user_manager.login(username)

    def main_ui(self):
        if st.session_state['user_role'] in ['user', 'approver', 'admin']:
            st.subheader("Create New Request")
            request_type = st.selectbox("Request Type", ['A', 'B', 'C', 'D', 'E', 'F'])
            title = st.text_input("Request Title")
            description = st.text_area("Description")
            if st.button("Submit Request"):
                self.request_manager.create_request(st.session_state['logged_in_user'], request_type, title, description)

            user_requests = self.request_manager.get_user_requests(st.session_state['logged_in_user'])
            self.display_manager.display_requests(user_requests, "Your Requests")

            returned_requests = self.request_manager.get_returned_requests()
            returned_requests = returned_requests[returned_requests['user'] == st.session_state['logged_in_user']]
            if not returned_requests.empty:
                st.subheader("Returned Requests - Edit and Resubmit")
                for index, req in returned_requests.iterrows():
                    with st.expander(f"Request ID: {req['id']} - Returned"):
                        st.markdown(f"**Approver Comment:** {req['approver_comment']}")
                        st.markdown(f"**Type:** {req['request_type']}")
                        st.markdown(f"**Title:** {req['title']}")
                        edit_description = st.text_area("Edit Description", value=req['description'], key=f"edit_description_{req['id']}")
                        if st.button("Resubmit Request", key=f"resubmit_{req['id']}"):
                            self.request_manager.update_request_status(req['id'], 'Pending', st.session_state['logged_in_user'], None)
                            requests_df = self.data_manager.load_requests()
                            requests_df.loc[requests_df['id'] == req['id'], 'description'] = edit_description
                            self.data_manager.save_requests(requests_df)
                            self.request_manager.log_request_history(req['id'], 'Edited', st.session_state['logged_in_user'], {'old_details': {'description': req['description']}, 'new_details': {'description': edit_description}})
                            self.request_manager.log_request_history(req['id'], 'Resubmitted', st.session_state['logged_in_user'], {})
                            st.success(f"Request ID {req['id']} resubmitted.")
                            st.rerun()

            st.subheader("View Request History")
            requests_df = self.data_manager.load_requests()
            request_ids = requests_df['id'].unique().tolist()
            request_id_to_view = st.selectbox("Select a Request ID to view history", request_ids)
            history_df = self.data_manager.load_request_history()
            self.display_manager.display_request_history(request_id_to_view, history_df)

        if st.session_state['user_role'] in ['approver', 'admin']:
            st.subheader("Pending Approvals")
            pending_requests = self.request_manager.get_pending_requests()
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
                            self.request_manager.update_request_status(req['id'], 'Approved', st.session_state['logged_in_user'])
                            st.rerun()
                    with col2:
                        deny_comment = st.text_area("Deny Comment", key=f"deny_comment_{req['id']}")
                        if st.button("Deny", key=f"deny_{req['id']}"):
                            self.request_manager.update_request_status(req['id'], 'Denied', st.session_state['logged_in_user'], deny_comment)
                            st.rerun()
                    with col3:
                        return_comment = st.text_area("Return Comment", key=f"return_comment_{req['id']}")
                        if st.button("Return", key=f"return_{req['id']}"):
                            self.request_manager.update_request_status(req['id'], 'Returned', st.session_state['logged_in_user'], return_comment)
                            st.rerun()
                    st.divider()
            else:
                st.info("No pending approvals.")

            approved_requests = self.request_manager.get_approved_requests()
            denied_requests = self.request_manager.get_denied_requests()
            returned_requests = self.request_manager.get_returned_requests()

            self.display_manager.display_requests(approved_requests, "Approved Requests")
            self.display_manager.display_requests(denied_requests, "Denied Requests")
            self.display_manager.display_requests(returned_requests, "Returned Requests")

        if st.session_state['user_role'] == 'admin':
            self.admin_panel.show()

if __name__ == "__main__":
    app = ApprovalApp()
    app.run()
