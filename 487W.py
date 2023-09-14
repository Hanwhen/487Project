import sys
import firebase_admin
from firebase_admin import db, credentials
from PyQt6.QtWidgets import QApplication, QDialog, QInputDialog
from PyQt6 import uic, QtWidgets
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred, {'databaseURL': 'https://w-b00e6-default-rtdb.firebaseio.com/'})
ref = db.reference('py/')
access_ref = ref.child('access')


# # Create a dictionary of users for testing
# access_ref.set({
#     '1': {
#         'name': 'Han',
#         'ID': '1',
#         'role': 'admin',
#         'status': '1',
#         'date': '2021-10-10',
#         'time_in': '10:10:10',
#         'exit_time': '10:10:10'
#     },
#     '2': {
#         'name': 'a',
#         'ID': '2',
#         'role': 'student',
#         'status': '1',
#         'date': '2021-10-10',
#         'time_in': '10:10:10',
#         'exit_time': '10:10:10'
#     },
#     '3': {
#         'name': 'b',
#         'ID': '3',
#         'role': 'student',
#         'status': '1',
#         'date': '2021-10-10',
#         'time_in': '10:10:10',
#         'exit_time': '10:10:10'
#     },
#     '4': {
#         'name': 'c',
#         'ID': '4',
#         'role': 'student',
#         'status': '1',
#         'date': '2021-10-10',
#         'time_in': '10:10:10',
#         'exit_time': '10:10:10'
#     },
#     '5': {
#         'name': 'd',
#         'ID': '5',
#         'role': 'student',
#         'status': '1',
#         'date': '2021-10-10',
#         'time_in': '10:10:10',
#         'exit_time': '10:10:410'
#     }
#     ,
#    'record': {}
# })


class SwipeInGui(QDialog):
    def __init__(self):
        super(SwipeInGui, self).__init__()
        uic.loadUi("swipe_in_view.ui", self)
        self.show()
        # Connect the button click event to open AdminView
        self.swipe_in_btn.clicked.connect(self.open_new_view)

    def open_new_view(self):
        # Retrieve the user input from a QLineEdit widget
        user_input = self.id_entry.text()

        # Query the Firestore database to check if the user input exists
        user_ref = access_ref.child(user_input).get()

        if user_ref is not None:
            # Update the 'time_in' record to the current time
            current_time = datetime.now().strftime("%H:%M:%S")
            current_date = datetime.now().strftime('%Y-%m-%d')
            access_ref.child(user_input).update({'time_in': current_time})
            access_ref.child(user_input).update({'date': current_date})

            role = user_ref.get('role')

            self.close()

            if role == 'admin':
                admin_view = AdminView(user_input)  # Pass the parent
                admin_view.exec()
            else:
                other_view = OtherView(user_input)
                other_view.exec()


class AdminView(QDialog):
    def __init__(self, user_input):
        super(AdminView, self).__init__()  # Set the parent
        uic.loadUi("admin_view.ui", self)
        self.table_view.setColumnWidth(0, 100)
        self.table_view.setColumnWidth(1, 100)
        self.table_view.setColumnWidth(2, 100)
        self.table_view.setColumnWidth(3, 100)
        self.table_view.setColumnWidth(4, 100)
        self.table_view.setColumnWidth(5, 100)
        self.table_view.setColumnWidth(6, 100)
        self.show()

        # Connect the exit button to the exit method
        self.swipe_out_btn.clicked.connect(self.return_to_main_view)
        self.browse_student_btn.clicked.connect(self.browse_student)
        self.browse_student_by_id_btn.clicked.connect(self.browse_student_by_id)
        self.user_input = user_input
        self.browse_student_by_date_btn.clicked.connect(self.browse_student_by_date)
        self.browse_student_by_time_btn.clicked.connect(self.browse_student_by_time)
        
        ######################## For future implementation ##################################
        # self.activate_account_btn.clicked.connect(self.activate_account)
        # self.suspend_account_btn.clicked.connect(self.suspend_account)
        # self.reactivate_account_btn.clicked.connect(self.reactivate_account)
        
    def return_to_main_view(self):
            current_time = datetime.now().strftime("%H:%M:%S")
            access_ref.child(self.user_input).update({'exit_time': current_time})

            # Retrieve user data
            user_data = access_ref.child(self.user_input).get()

            if user_data is not None:
                # Update the 'record' field with user information
                record_ref = access_ref.child('record').push()  # Generate a new unique key
                record_ref.set(user_data)  # Set the user data into the 'record' field

            self.close()
            main_view = SwipeInGui()
            main_view.exec()


    def browse_student(self):
        # Query the 'record' field in Firebase for all records
        record_data = access_ref.child('record').get()

        if record_data:
            # Filter records by role (e.g., 'student')
            student_records = [record for record in record_data.values()]

            if student_records:
                # Display the filtered student records in a table
                self.table_view.setRowCount(len(student_records))
                rowPosition = 0
                for user_data in student_records:
                    name = user_data.get('name', '')
                    id = user_data.get('ID', '')
                    role = user_data.get('role', '')
                    status = user_data.get('status', '')
                    date = user_data.get('date', '')
                    time_in = user_data.get('time_in', '')
                    exit_time = user_data.get('exit_time', '')
                    self.table_view.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(name))
                    self.table_view.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(id))
                    self.table_view.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(role))
                    self.table_view.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(status))
                    self.table_view.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(date))
                    self.table_view.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(time_in))
                    self.table_view.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(exit_time))
                    rowPosition += 1
            else:
                # No student records found in 'record' field
                QtWidgets.QMessageBox.information(self, "No Student Records Found", "No student records found in the 'record' field.")
        else:
            # 'record' field is empty
            QtWidgets.QMessageBox.information(self, "No Records Found", "No records found in the 'record' field.")



    def browse_student_by_id(self):
        # Prompt the user for the ID using a dialog
        user_id, ok_pressed = QInputDialog.getText(self, "Search by ID", "Enter User ID:")

        if ok_pressed and user_id:
            # Convert user_id to a string (it might be a QString)
            user_id = str(user_id)

            # Query the 'record' field in Firebase for the provided user_id
            record_data = access_ref.child('record').get()

            if record_data:
                # Filter records by user ID
                filtered_records = [record for record in record_data.values() if record.get('ID') == user_id]

                if filtered_records:
                    # Display the filtered records in a table
                    self.table_view.setRowCount(len(filtered_records))
                    rowPosition = 0
                    for user_data in filtered_records:
                        name = user_data.get('name', '')
                        role = user_data.get('role', '')
                        status = user_data.get('status', '')
                        date = user_data.get('date', '')
                        time_in = user_data.get('time_in', '')
                        exit_time = user_data.get('exit_time', '')
                        self.table_view.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(name))
                        self.table_view.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(user_id))
                        self.table_view.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(role))
                        self.table_view.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(status))
                        self.table_view.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(date))
                        self.table_view.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(time_in))
                        self.table_view.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(exit_time))
                        rowPosition += 1
                else:
                    # No records found for the provided ID
                    QtWidgets.QMessageBox.information(self, "No Records Found", "No records found for the provided ID.")
            else:
                # 'record' field is empty
                QtWidgets.QMessageBox.information(self, "No Records Found", "No records found in the 'record' field.")

    def browse_student_by_date(self):
        # Prompt the user for a date in 'YYYY-MM-DD' format
        date_input, ok_pressed = QInputDialog.getText(self, "Search by Date", "Enter Date (YYYY-MM-DD):")

        if ok_pressed and date_input:
            # Query the 'record' field in Firebase for records with the specified date
            record_data = access_ref.child('record').get()

            if record_data:
                # Filter records by date
                filtered_records = [record for record in record_data.values() if record.get('date') == date_input]

                if filtered_records:
                    # Display the filtered records in a table
                    self.table_view.setRowCount(len(filtered_records))
                    rowPosition = 0
                    for user_data in filtered_records:
                        name = user_data.get('name', '')
                        user_id = user_data.get('ID', '')
                        role = user_data.get('role', '')
                        status = user_data.get('status', '')
                        time_in = user_data.get('time_in', '')
                        exit_time = user_data.get('exit_time', '')
                        self.table_view.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(name))
                        self.table_view.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(user_id))
                        self.table_view.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(role))
                        self.table_view.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(status))
                        self.table_view.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(date_input))
                        self.table_view.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(time_in))
                        self.table_view.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(exit_time))
                        rowPosition += 1
                else:
                    # No records found for the specified date
                    QtWidgets.QMessageBox.information(self, "No Records Found", f"No records found for the date: {date_input}.")
            else:
                # 'record' field is empty
                QtWidgets.QMessageBox.information(self, "No Records Found", "No records found in the 'record' field.")
    def browse_student_by_time(self):
        # Prompt the user for a time range in 'hh:mm:ss' format
        time_range, ok_pressed = QInputDialog.getText(self, "Search by Time Range", "Enter Time Range (hh:mm:ss - hh:mm:ss):")

        if ok_pressed and time_range:
            # Split the time range into start time and end time
            time_range_parts = time_range.split('-')

            if len(time_range_parts) != 2:
                QtWidgets.QMessageBox.critical(self, "Invalid Input", "Invalid time range format. Please use 'hh:mm:ss - hh:mm:ss' format.")
                return

            start_time, end_time = map(str.strip, time_range_parts)

            try:
                # Validate the time format
                datetime.strptime(start_time, "%H:%M:%S")
                datetime.strptime(end_time, "%H:%M:%S")
            except ValueError:
                QtWidgets.QMessageBox.critical(self, "Invalid Time Format", "Invalid time format. Please use 'hh:mm:ss' format.")
                return

            # Query the 'record' field in Firebase for records with time-in within the specified range
            record_data = access_ref.child('record').get()

            if record_data:
                # Filter records by time-in
                filtered_records = [record for record in record_data.values() if self.is_within_time_range(record, start_time, end_time)]

                if filtered_records:
                    # Display the filtered records in a table
                    self.table_view.setRowCount(len(filtered_records))
                    rowPosition = 0
                    for user_data in filtered_records:
                        name = user_data.get('name', '')
                        user_id = user_data.get('ID', '')
                        role = user_data.get('role', '')
                        status = user_data.get('status', '')
                        date = user_data.get('date', '')
                        time_in = user_data.get('time_in', '')
                        exit_time = user_data.get('exit_time', '')
                        self.table_view.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(name))
                        self.table_view.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(user_id))
                        self.table_view.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(role))
                        self.table_view.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(status))
                        self.table_view.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(date))
                        self.table_view.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(time_in))
                        self.table_view.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(exit_time))
                        rowPosition += 1
                else:
                    # No records found for the specified time range
                    QtWidgets.QMessageBox.information(self, "No Records Found", f"No records found for the time range: {time_range}.")
            else:
                # 'record' field is empty
                QtWidgets.QMessageBox.information(self, "No Records Found", "No records found in the 'record' field.")

    def is_within_time_range(self, record, start_time, end_time):
        try:
            record_time = datetime.strptime(record.get('time_in'), "%H:%M:%S").time()
            start_time_obj = datetime.strptime(start_time, "%H:%M:%S").time()
            end_time_obj = datetime.strptime(end_time, "%H:%M:%S").time()
            return start_time_obj <= record_time <= end_time_obj
        except ValueError:
            return False



        
class OtherView(QDialog):
    def __init__(self, user_input):
        super(OtherView, self).__init__()  # Set the parent
        uic.loadUi("other_view.ui", self)
        self.show()
    
        # Connect the exit button to the exit method
        self.swipe_out_btn.clicked.connect(self.return_to_main_view)

        self.user_input = user_input

    def return_to_main_view(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        access_ref.child(self.user_input).update({'exit_time': current_time})

        # Retrieve user data
        user_data = access_ref.child(self.user_input).get()

        if user_data is not None:
            # Update the 'record' field with user information
            record_ref = access_ref.child('record').push()  # Generate a new unique key
            record_ref.set(user_data)  # Set the user data into the 'record' field

        self.close()
        main_view = SwipeInGui()
        main_view.exec()
   


def main():
    app = QApplication([])
    window = SwipeInGui()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
