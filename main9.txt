import streamlit as st  # Import the Streamlit library for creating web applications
import pandas as pd  # Import the Pandas library for data manipulation
import os  # Import the OS library for interacting with the operating system
from datetime import datetime  # Import the datetime object for handling dates and times

class DataManager:
    def __init__(self, requests_file='requests.csv', users_file='users.csv',
                 pending_registrations_file='pending_registrations.csv',
                 deleted_requests_file='deleted_requests.csv',
                 request_history_file='request_history.csv'):
        self.requests_file = requests_file  # Initialize the file path for requests
        self.users_file = users_file  # Initialize the file path for users
        self.pending_registrations_file = pending_registrations_file  # Initialize the file path for pending registrations
        self.deleted_requests_file = deleted_requests_file  # Initialize the file path for deleted requests
        self.request_history_file = request_history_file  # Initialize the file path for request history
        self._initialize_dataframes()  # Call the method to create dataframes if files don't exist

    def _initialize_dataframes(self):
        if not os.path.exists(self.requests_file):  # Check if the requests file exists
            pd.DataFrame(columns=['id', 'user', 'request_type', 'title', 'description', 'status', 'approver_comment']).to_csv(self.requests_file, index=False)  # Create an empty DataFrame and save it as CSV if the file doesn't exist
        if not os.path.exists(self.users_file):  # Check if the users file exists
            pd.DataFrame(columns=['username', 'role', 'approved']).to_csv(self.users_file, index=False)  # Create an empty DataFrame and save it as CSV if the file doesn't exist
        if not os.path.exists(self.pending_registrations_file):  # Check if the pending registrations file exists
            pd.DataFrame(columns=['username', 'requested_role']).to_csv(self.pending_registrations_file, index=False)  # Create an empty DataFrame and save it as CSV if the file doesn't exist
        if not os.path.exists(self.deleted_requests_file):  # Check if the deleted requests file exists
            pd.DataFrame(columns=['id', 'user', 'request_type', 'title', 'description', 'status', 'approver_comment', 'deleted_by', 'deleted_at']).to_csv(self.deleted_requests_file, index=False)  # Create an empty DataFrame and save it as CSV if the file doesn't exist
        if not os.path.exists(self.request_history_file):  # Check if the request history file exists
            pd.DataFrame(columns=['request_id', 'timestamp', 'action', 'user', 'details']).to_csv(self.request_history_file, index=False)  # Create an empty DataFrame and save it as CSV if the file doesn't exist

    def load_requests(self):
        return pd.read_csv(self.requests_file)  # Load request data from the CSV file into a DataFrame

    def load_users(self):
        return pd.read_csv(self.users_file)  # Load user data from the CSV file into a DataFrame

    def load_pending_registrations(self):
        return pd.read_csv(self.pending_registrations_file)  # Load pending registration data from the CSV file into a DataFrame

    def load_deleted_requests(self):
        return pd.read_csv(self.deleted_requests_file)  # Load deleted request data from the CSV file into a DataFrame

    def load_request_history(self):
        return pd.read_csv(self.request_history_file)  # Load request history data from the CSV file into a DataFrame

    def save_requests(self, df):
        df.to_csv(self.requests_file, index=False)  # Save the request DataFrame to the CSV file

    def save_users(self, df):
        df.to_csv(self.users_file, index=False)  # Save the user DataFrame to the CSV file

    def save_pending_registrations(self, df):
        df.to_csv(self.pending_registrations_file, index=False)  # Save the pending registration DataFrame to the CSV file

    def save_deleted_requests(self, df):
        df.to_csv(self.deleted_requests_file, index=False)  # Save the deleted request DataFrame to the CSV file

    def save_request_history(self, df):
        df.to_csv(self.request_history_file, index=False)  # Save the request history DataFrame to the CSV file

class RequestManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager  # Initialize with a DataManager instance

    def generate_request_id(self, request_type):
        now = datetime.now()  # Get the current datetime
        month_char_map = {  # Map month numbers to characters
            1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',
            10: 'A', 11: 'B', 12: 'C'
        }
        month_char = month_char_map[now.month]  # Get the character for the current month

        increment_char_map = {  # Map increment numbers to characters
            i + 1: str(i + 1) if i < 9 else chr(ord('A') + (i - 9)) for i in range(36)
        }

        requests_df = self.data_manager.load_requests()  # Load existing request data
        filtered_df = requests_df[(requests_df['id'].str.startswith(f'{request_type}{month_char}'))]  # Filter requests by type and month
        increment = len(filtered_df) + 1  # Calculate the next increment
        increment_str = increment_char_map.get(increment, 'Z')  # Get the character for the increment, default to 'Z' if out of range

        return f"{request_type}{month_char}{increment_str}{0}"  # Return the generated request ID

    def create_request(self, user, request_type, title, description):
        requests_df = self.data_manager.load_requests()  # Load existing request data
        new_id = self.generate_request_id(request_type)  # Generate a new request ID
        new_request = pd.DataFrame([{'id': new_id, 'user': user, 'request_type': request_type, 'title': title, 'description': description, 'status': 'Pending', 'approver_comment': None}])  # Create a new DataFrame for the request
        updated_requests = pd.concat([requests_df, new_request], ignore_index=True)  # Add the new request to the requests DataFrame
        self.data_manager.save_requests(updated_requests)  # Save the updated requests data
        self.log_request_history(new_id, 'Created', user, {'request_type': request_type, 'title': title, 'description': description})  # Log the creation of the request
        st.success(f"Request submitted successfully with ID: {new_id}!")  # Display a success message with the new request ID

    def update_request_status(self, request_id, new_status, user, comment=None):
        requests_df = self.data_manager.load_requests()  # Load existing request data
        original_request = requests_df[requests_df['id'] == request_id].iloc[0].to_dict()  # Get the original request data for logging
        requests_df.loc[requests_df['id'] == request_id, 'status'] = new_status  # Update the status of the request
        requests_df.loc[requests_df['id'] == request_id, 'approver_comment'] = comment  # Add or update the approver's comment
        self.data_manager.save_requests(requests_df)  # Save the updated requests data
        self.log_request_history(request_id, new_status, user, {'comment': comment} if comment else {})  # Log the status update
        st.success(f"Request {request_id} updated to {new_status}")  # Display a success message

    def log_request_history(self, request_id, action, user, details=None):
        history_df = self.data_manager.load_request_history()  # Load existing request history data
        new_history = pd.DataFrame([{'request_id': request_id, 'timestamp': datetime.now(), 'action': action, 'user': user, 'details': details}])  # Create a new DataFrame for the history entry
        updated_history = pd.concat([history_df, new_history], ignore_index=True)  # Add the new history entry to the history DataFrame
        self.data_manager.save_request_history(updated_history)  # Save the updated history data

    def get_user_requests(self, user):
        requests_df = self.data_manager.load_requests()  # Load existing request data
        return requests_df[requests_df['user'] == user]  # Filter requests for the given user

    def get_pending_requests(self):
        requests_df = self.data_manager.load_requests()  # Load existing request data
        return requests_df[requests_df['status'] == 'Pending']  # Filter requests with 'Pending' status

    def get_approved_requests(self):
        requests_df = self.data_manager.load_requests()  # Load existing request data
        return requests_df[requests_df['status'] == 'Approved']  # Filter requests with 'Approved' status

    def get_denied_requests(self):
        requests_df = self.data_manager.load_requests()  # Load existing request data
        return requests_df[requests_df['status'] == 'Denied']  # Filter requests with 'Denied' status

    def get_returned_requests(self):
        requests_df = self.data_manager.load_requests()  # Load existing request data
        return requests_df[requests_df['status'] == 'Returned']  # Filter requests with 'Returned' status

    def get_request_by_id(self, request_id):
        requests_df = self.data_manager.load_requests()  # Load existing request data
        return requests_df[requests_df['id'] == request_id].iloc[0]  # Get the first row of the request with the given ID

class UserManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager  # Initialize with a DataManager instance

    def register_user(self, new_username):
        users_df = self.data_manager.load_users()  # Load existing user data
        pending_registrations_df = self.data_manager.load_pending_registrations()  # Load pending registration data
        if new_username in pending_registrations_df['username'].values or new_username in users_df['username'].values:  # Check if the username already exists
            st.error("Username already exists or is pending approval.")  # Display an error message
            return False  # Return False if registration failed
        else:
            new_registration = pd.DataFrame([{'username': new_username, 'requested_role': 'user'}])  # Create a new DataFrame for the registration
            updated_pending_registrations = pd.concat([pending_registrations_df, new_registration], ignore_index=True)  # Add the new registration
            self.data_manager.save_pending_registrations(updated_pending_registrations)  # Save the updated pending registrations
            st.success("Registration submitted for admin approval as a regular user.")  # Display a success message
            return True  # Return True if registration was successful

    def initialize_admin(self):
        users_df = self.data_manager.load_users()  # Load existing user data
        if users_df.empty:  # Check if the users DataFrame is empty (first run)
            st.subheader("Initialize First Admin User")  # Display a subheader
            admin_username = st.text_input("Enter username for the first admin")  # Get admin username input
            if st.button("Initialize Admin"):  # Button to initialize admin
                if admin_username in users_df['username'].values:  # Check if admin username already exists
                    st.error("Admin username already exists.")  # Display an error
                else:
                    new_admin = pd.DataFrame([{'username': admin_username, 'role': 'admin', 'approved': True}])  # Create admin user DataFrame
                    updated_users = pd.concat([users_df, new_admin], ignore_index=True)  # Add admin to users
                    self.data_manager.save_users(updated_users)  # Save updated users
                    st.success(f"Admin user '{admin_username}' created. Please log in.")  # Display success message
                    st.session_state['first_admin_initialized'] = True  # Set session state flag
                    st.rerun()  # Rerun to update UI
                return True  # Return True if admin initialization UI is shown
        return False  # Return False if admin is already initialized

    def login(self, username):
        users_df = self.data_manager.load_users()  # Load existing user data
        if username in users_df['username'].values:  # Check if the username exists
            user_data = users_df[users_df['username'] == username].iloc[0]  # Get user data
            if user_data['approved']:  # Check if the user is approved
                st.session_state['logged_in_user'] = username  # Set logged-in user in session state
                st.session_state['user_role'] = user_data['role']  # Set user role in session state
                return True  # Return True if login successful
            else:
                st.sidebar.error("Your registration is pending admin approval.")  # Display pending message
                return False  # Return False if login failed (pending)
        else:
            st.sidebar.error("Invalid username")  # Display invalid username message
            return False  # Return False if login failed (invalid)

    def logout(self):
        st.session_state.pop('logged_in_user', None)  # Remove logged-in user from session state
        st.session_state.pop('user_role', None)  # Remove user role from session state
        st.session_state.pop('editing_request_id', None)  # Remove editing request ID
        st.session_state.pop('first_admin_initialized', None)  # Remove admin initialized flag

    def get_pending_registrations(self):
        return self.data_manager.load_pending_registrations()  # Load and return pending registrations

    def approve_registration(self, username, role):
        users_df = self.data_manager.load_users()  # Load user data
        pending_registrations_df = self.data_manager.load_pending_registrations()  # Load pending registrations
        if username not in users_df['username'].values:  # Check if user doesn't exist
            new_user = pd.DataFrame([{'username': username, 'role': role, 'approved': True}])  # Create new user DataFrame
            updated_users = pd.concat([users_df, new_user], ignore_index=True)  # Add new user
            self.data_manager.save_users(updated_users)  # Save updated users
            updated_pending_registrations = pending_registrations_df[pending_registrations_df['username'] != username]  # Remove from pending
            self.data_manager.save_pending_registrations(updated_pending_registrations)  # Save updated pending
            st.success(f"User '{username}' approved as '{role}'.")  # Display success message
            return True  # Return True if approval successful
        else:
            st.error(f"User '{username}' already exists.")  # Display error if user exists
            return False  # Return False if approval failed

    def reject_registration(self, username):
        pending_registrations_df = self.data_manager.load_pending_registrations()  # Load pending registrations
        updated_pending_registrations = pending_registrations_df[pending_registrations_df['username'] != username]  # Remove from pending
        self.data_manager.save_pending_registrations(updated_pending_registrations)  # Save updated pending
        st.info(f"Registration for '{username}' rejected.")  # Display rejection message
        return True  # Return True if rejection successful

    def get_all_users(self):
        return self.data_manager.load_users()  # Load and return all users

    def change_user_role(self, username, new_role):
        users_df = self.data_manager.load_users()  # Load user data
        users_df.loc[users_df['username'] == username, 'role'] = new_role  # Update user role
        self.data_manager.save_users(users_df)  # Save updated users
        st.success(f"Role of '{username}' changed to '{new_role}'.")  # Display success message
        return True  # Return True if role change successful

class DisplayManager:
    def display_requests(self, df, title):
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

    def display_request_history(self, request_id, history_df):
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

    def display_pending_registrations(self, df):
        if not df.empty:  # Check if there are pending registrations
            for index, reg in df.iterrows():  # Iterate through each pending registration
                st.markdown(f"**Username:** {reg['username']}")  # Display the username
                st.markdown(f"**Requested Role:** user")  # Display the requested role
                col1, col2 = st.columns(2)  # Create two columns for actions
                with col1:
                    approve_role = st.selectbox("Approve As", ['user', 'approver', 'admin'], key=f"approve_role_{reg['username']}")  # Selectbox for approving role
                    if st.button("Approve", key=f"approve_reg_{reg['username']}"):  # Approve button
                        return 'approve', reg['username'], approve_role  # Return action, username, and role
                with col2:
                    if st.button("Reject", key=f"reject_reg_{reg['username']}"):  # Reject button
                        return 'reject', reg['username'], None  # Return action and username
                st.divider()  # Display a divider
        else:
            st.info("No pending registrations.")  # Display message if no pending registrations
        return None, None, None  # Return None if no action taken

    def display_all_users(self, df):
        st.write("Edit User Roles:")  # Display a label
        for index, user in df.iterrows():  # Iterate through each user
            col1, col2 = st.columns(2)  # Create two columns
            with col1:
                st.write(f"**{user['username']}** (Current Role: {user['role']})")  # Display username and current role
            with col2:
                new_role = st.selectbox("New Role", ['user', 'approver', 'admin'], key=f"role_select_{user['username']}", index=['user', 'approver', 'admin'].index(user['role']))  # Selectbox for new role
                if st.button("Change Role", key=f"change_role_{user['username']}"):  # Change role button
                    return 'change_role', user['username'], new_role  # Return action, username, and new role
        st.dataframe(df)  # Display the users DataFrame
        return None, None, None  # Return None if no action taken

    def display_deleted_requests(self, df):
        if not df.empty:  # Check if there are deleted requests
            st.subheader("Deleted Requests (For Backtracking)")  # Display a subheader
            st.dataframe(df)  # Display the deleted requests DataFrame

class AdminPanel:
    def __init__(self, user_manager, display_manager, request_manager):
        self.user_manager = user_manager  # Initialize with UserManager instance
        self.display_manager = display_manager  # Initialize with DisplayManager instance
        self.request_manager = request_manager  # Initialize with RequestManager instance

    def show(self):
        st.subheader("Admin Panel")  # Display a subheader

        st.subheader("Pending Registrations")  # Display a subheader
        pending_registrations = self.user_manager.get_pending_registrations()  # Get pending registrations
        action, username, role = self.display_manager.display_pending_registrations(pending_registrations)  # Display pending registrations and get action
        if action == 'approve' and username:  # If approve action
            self.user_manager.approve_registration(username, role)  # Approve the registration
            st.rerun()  # Rerun to update UI
        elif action == 'reject' and username:  # If reject action
            self.user_manager.reject_registration(username)  # Reject the registration
            st.rerun()  # Rerun to update UI

        st.subheader("User Management")  # Display a subheader
        all_users = self.user_manager.get_all_users()  # Get all users
        user_action, edit_username, new_role = self.display_manager.display_all_users(all_users)  # Display users and get action
        if user_action == 'change_role' and edit_username and new_role:  # If change role action
            self.user_manager.change_user_role(edit_username, new_role)  # Change the user's role
            st.rerun()  # Rerun to update UI

        st.subheader("All Requests")  # Display a subheader
        all_requests = self.request_manager.data_manager.load_requests()  # Load all requests
        self.display_manager.display_requests(all_requests, "All Requests")  # Display all requests

        st.subheader("Delete Requests")  # Display a subheader
        request_to_delete_id = st.number_input("Enter Request ID to Delete", min_value=1, step=1)  # Input for request ID to delete
        if st.button("Delete Request"):  # Delete request button
            request_to_delete = self.request_manager.data_manager.load_requests()  # Load all requests
            request_to_delete = request_to_delete[request_to_delete['id'] == request_to_delete_id]  # Filter the request
            if not request_to_delete.empty:  # If request found
                deleted_request = request_to_delete.iloc[0].to_dict()  # Get request data
                deleted_request['deleted_by'] = st.session_state['logged_in_user']  # Record who deleted
                deleted_request['deleted_at'] = pd.Timestamp('now')  # Record deletion time
                deleted_requests_df = self.request_manager.data_manager.load_deleted_requests()  # Load deleted requests
                updated_deleted_requests = pd.concat([deleted_requests_df, pd.Series(deleted_request).to_frame().T], ignore_index=True)  # Add to deleted
                self.request_manager.data_manager.save_deleted_requests(updated_deleted_requests)  # Save deleted
                updated_requests_df = self.request_manager.data_manager.load_requests()  # Load all requests
                updated_requests_df = updated_requests_df[updated_requests_df['id'] != request_to_delete_id]  # Remove deleted
                self.request_manager.data_manager.save_requests(updated_requests_df)  # Save updated requests
                self.request_manager.log_request_history(request_to_delete_id, 'Deleted', st.session_state['logged_in_user'], {'original_details': deleted_request})  # Log deletion
                st.success(f"Request ID {request_to_delete_id} deleted (still available for backtracking).")  # Success message
                st.rerun()  # Rerun to update UI
            else:
                st.error(f"Request ID {request_to_delete_id} not found.")  # Error message if not found

        self.display_manager.display_deleted_requests(self.request_manager.data_manager.load_deleted_requests())  # Display deleted requests

        st.subheader("Request History")  # Display a subheader
        history_df = self.request_manager.data_manager.load_request_history()  # Load request history
        if not history_df.empty:  # If history exists
            st.subheader("View Request History")  # Display a subheader
            request_ids = self.request_manager.data_manager.load_requests()['id'].unique().tolist()  # Get all request IDs
            request_id_to_view = st.selectbox("Select a Request ID to view history", request_ids)  # Selectbox for request ID
            self.display_manager.display_request_history(request_id_to_view, history_df)  # Display history
        else:
            st.info("No request history available.")  # Message if no history

class ApprovalApp:
    def __init__(self):
        self.data_manager = DataManager()  # Create DataManager instance
        self.user_manager = UserManager(self.data_manager)  # Create UserManager instance
        self.request_manager = RequestManager(self.data_manager)  # Create RequestManager instance
        self.display_manager = DisplayManager()  # Create DisplayManager instance
        self.admin_panel = AdminPanel(self.user_manager, self.display_manager, self.request_manager)  # Create AdminPanel instance

    def run(self):
        st.title("Approval System")  # Set the title of the app

        if 'logged_in_user' not in st.session_state:  # Check if user is logged in
            if not self.user_manager.initialize_admin():  # Initialize admin if not done
                self.login_ui()  # Show login UI
        elif st.sidebar.button("Logout"):  # Logout button clicked
            self.user_manager.logout()  # Perform logout

        if 'logged_in_user' in st.session_state:  # If user is logged in
            st.sidebar.write(f"Logged in as: {st.session_state['logged_in_user']} ({st.session_state['user_role']})")  # Display login info
            self.main_ui()  # Show main UI
        else:
            if 'first_admin_initialized' not in st.session_state:
                pass  # Admin initialization handled in UserManager
            else:
                self.register_ui()  # Show registration UI

    def register_ui(self):
        st.subheader("User Registration")  # Display registration subheader
        new_username = st.text_input("New Username")  # Input for new username
        if st.button("Register"):  # Register button
            self.user_manager.register_user(new_username)  # Call user registration

    def login_ui(self):
        st.sidebar.subheader("Login")  # Display login subheader in sidebar
        username = st.sidebar.text_input("Username")  # Input for username
        if st.sidebar.button("Login"):  # Login button
            self.user_manager.login(username)  # Call user login

    def main_ui(self):
        if st.session_state['user_role'] in ['user', 'approver', 'admin']:  # If user has access
            st.subheader("Create New Request")  # Display create request subheader
            request_type = st.selectbox("Request Type", ['A', 'B', 'C', 'D', 'E', 'F'])  # Selectbox for request type
            title = st.text_input("Request Title")  # Input for request title
            description = st.text_area("Description")  # Text area for description
            if st.button("Submit Request"):  # Submit request button
                self.request_manager.create_request(st.session_state['logged_in_user'], request_type, title, description)  # Create request

            user_requests = self.request_manager.get_user_requests(st.session_state['logged_in_user'])  # Get user's requests
            self.display_manager.display_requests(user_requests, "Your Requests")  # Display user's requests

            returned_requests = self.request_manager.get_returned_requests()  # Get returned requests
            returned_requests = returned_requests[returned_requests['user'] == st.session_state['logged_in_user']]  # Filter for current user
            if not returned_requests.empty:  # If there are returned requests
                st.subheader("Returned Requests - Edit and Resubmit")  # Display subheader
                for index, req in returned_requests.iterrows():  # Iterate through returned requests
                    with st.expander(f"Request ID: {req['id']} - Returned"):  # Expander for each request
                        st.markdown(f"**Approver Comment:** {req['approver_comment']}")  # Display comment
                        st.markdown(f"**Type:** {req['request_type']}")  # Display type
                        st.markdown(f"**Title:** {req['title']}")  # Display title
                        edit_description = st.text_area("Edit Description", value=req['description'], key=f"edit_description_{req['id']}")  # Edit description
                        if st.button("Resubmit Request", key=f"resubmit_{req['id']}"):  # Resubmit button
                            self.request_manager.update_request_status(req['id'], 'Pending', st.session_state['logged_in_user'], None)  # Set to pending
                            requests_df = self.data_manager.load_requests()  # Load requests
                            requests_df.loc[requests_df['id'] == req['id'], 'description'] = edit_description  # Update description
                            self.data_manager.save_requests(requests_df)  # Save requests
                            self.request_manager.log_request_history(req['id'], 'Edited', st.session_state['logged_in_user'], {'old_details': {'description': req['description']}, 'new_details': {'description': edit_description}})  # Log edit
                            self.request_manager.log_request_history(req['id'], 'Resubmitted', st.session_state['logged_in_user'], {})  # Log resubmit
                            st.success(f"Request ID {req['id']} resubmitted.")  # Success message
                            st.rerun()  # Rerun
            st.subheader("View Request History")  # Display subheader
            requests_df = self.data_manager.load_requests()  # Load requests
            request_ids = requests_df['id'].unique().tolist()  # Get all request IDs
            request_id_to_view = st.selectbox("Select a Request ID to view history", request_ids)  # Select request ID
            history_df = self.data_manager.load_request_history()  # Load history
            self.display_manager.display_request_history(request_id_to_view, history_df)  # Display history

        if st.session_state['user_role'] in ['approver', 'admin']:  # If approver or admin
            st.subheader("Pending Approvals")  # Display subheader
            pending_requests = self.request_manager.get_pending_requests()  # Get pending requests
            if not pending_requests.empty:  # If there are pending requests
                for index, req in pending_requests.iterrows():  # Iterate through pending
                    st.markdown(f"**Request ID:** {req['id']}")  # Display request ID
                    st.markdown(f"**User:** {req['user']}")  # Display user
                    st.markdown(f"**Type:** {req['request_type']}")  # Display type
                    st.markdown(f"**Title:** {req['title']}")  # Display title
                    st.markdown(f"**Description:** {req['description']}")  # Display description

                    col1, col2, col3 = st.columns(3)  # Create columns for actions
                    with col1:
                        if st.button("Approve", key=f"approve_{req['id']}"):  # Approve button
                            self.request_manager.update_request_status(req['id'], 'Approved', st.session_state['logged_in_user'])  # Approve request
                            st.rerun()  # Rerun
                    with col2:
                        deny_comment = st.text_area("Deny Comment", key=f"deny_comment_{req['id']}")  # Deny comment area
                        if st.button("Deny", key=f"deny_{req['id']}"):  # Deny button
                            self.request_manager.update_request_status(req['id'], 'Denied', st.session_state['logged_in_user'], deny_comment)  # Deny request
                            st.rerun()  # Rerun
                    with col3:
                        return_comment = st.text_area("Return Comment", key=f"return_comment_{req['id']}")  # Return comment area
                        if st.button("Return", key=f"return_{req['id']}"):  # Return button
                            self.request_manager.update_request_status(req['id'], 'Returned', st.session_state['logged_in_user'], return_comment)  # Return request
                            st.rerun()  # Rerun
                    st.divider()  # Display divider
            else:
                st.info("No pending approvals.")  # Message if no pending

            approved_requests = self.request_manager.get_approved_requests()  # Get approved
            denied_requests = self.request_manager.get_denied_requests()  # Get denied
            returned_requests = self.request_manager.get_returned_requests()  # Get returned

            self.display_manager.display_requests(approved_requests, "Approved Requests")  # Display approved
            self.display_manager.display_requests(denied_requests, "Denied Requests")  # Display denied
            self.display_manager.display_requests(returned_requests, "Returned Requests")  # Display returned

        if st.session_state['user_role'] == 'admin':  # If admin
            self.admin_panel.show()  # Show admin panel

if __name__ == "__main__":
    app = ApprovalApp()  # Create ApprovalApp instance
    app.run()  # Run the application
