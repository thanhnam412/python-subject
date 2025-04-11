import mysql.connector
from mysql.connector import Error


class Database:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                database="course_registration",
            )
            self.cursor = self.connection.cursor()
            print("Kết nối database thành công!")
        except Error as e:
            print(f"Lỗi kết nối database: {e}")
            self.connection = None
            self.cursor = None

    def __del__(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("Đã đóng kết nối database.")
