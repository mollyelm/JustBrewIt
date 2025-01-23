import sys
from todo import SpellBook
import mysql.connector
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLineEdit, QLabel, QSizePolicy, QMessageBox, QInputDialog)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# main window creation
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Just Brew It - Login")
        self.setFixedSize(1600, 900)
        self.init_ui()
        self.conn = self.connect_to_db()
        if self.conn:
            self.cursor = self.conn.cursor(dictionary=True)
    
    # connects to db... duh
    def connect_to_db(self):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="spellbook_remote",
                password="testpass123",
                database="spellbook_db"
            )
            return conn
        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL: {err}")
            return None
        
    # creates login page (uggo mode)
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        form_layout = QVBoxLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        button_layout = QHBoxLayout()
        self.new_button = QPushButton("New")
        self.login_button = QPushButton("Login")
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.login_button)

        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addLayout(button_layout)

        main_layout.addLayout(form_layout)

        self.new_button.clicked.connect(self.create_new_user)
        self.login_button.clicked.connect(self.login_user)

    # if user logs in as new
    def create_new_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return
        try:
            self.cursor.execute('''
                INSERT INTO users (username, password)
                VALUES (%s, %s)
            ''', (username, password))
            self.conn.commit()
            
            QMessageBox.information(self, "Success", "User created successfully.")
            self.open_spellbook_page(username, is_new_user=True)
        except mysql.connector.Error as err:
            QMessageBox.warning(self, "Error", f"Could not create user: {err}")

    # if user logs in as old
    def login_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return
        try:
            self.cursor.execute('''
                SELECT * FROM users
                WHERE username = %s AND password = %s
            ''', (username, password))  
            user = self.cursor.fetchone()
            if user:
                self.open_spellbook_page(username)
            else:
                QMessageBox.warning(self, "Error", "Invalid username or password.")
        except mysql.connector.Error as err:
            QMessageBox.warning(self, "Error", f"Login failed: {err}")

    # opens up spell shelf for them to pick a book
    def open_spellbook_page(self, username, is_new_user=False):
        self.spellbook_page = SpellbookPage(username, is_new_user, self.conn)
        self.spellbook_page.show()
        self.close()

class SpellbookPage(QMainWindow):
    def __init__(self, username, is_new_user, conn):
        super().__init__()
        self.username = username
        self.is_new_user = is_new_user
        self.conn = conn
        self.potion_list = []

        self.cursor = self.conn.cursor(dictionary=True)
        self.setWindowTitle(f"Just Brew It - {username}'s Spellbooks")
        self.setFixedSize(1600, 900)
        self.init_ui()
        
        if not self.is_new_user:
            self.load_spellbooks()
        else:
            self.show_welcome_message()

    # if user has no spells
    def show_welcome_message(self):
        welcome_label = QLabel(f"Welcome, {self.username}! Click the '+' button to create your first spellbook.")
        welcome_label.setStyleSheet("color: white; font-size: 18px;")
        self.shelf_layout.addWidget(welcome_label, alignment=Qt.AlignmentFlag.AlignCenter)
    
    # builds shelf window
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # i really didnt spend long on this, i just wanted to add the most basic layout
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.avatar_label = QLabel()
        avatar_pixmap = QPixmap("avatar.png")
        avatar_pixmap = avatar_pixmap.scaledToWidth(500)
        self.avatar_label.setPixmap(avatar_pixmap)
        left_layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(left_widget)

        self.shelf_widget = QWidget()
        self.shelf_layout = QVBoxLayout(self.shelf_widget)
        self.shelf_widget.setStyleSheet("background-color: #8B4513; border: 2px solid #4A2500;")
        
        self.add_spellbook_button = QPushButton("+")
        self.add_spellbook_button.setFixedSize(50, 50)
        self.add_spellbook_button.clicked.connect(self.add_new_spellbook)
        self.shelf_layout.addWidget(self.add_spellbook_button, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addWidget(self.shelf_widget)

    # adds spellbooks to the shelf
    def load_spellbooks(self):
        try:
            self.cursor.execute('''
                SELECT * FROM spellbooks
                WHERE username = %s
                ORDER BY title
            ''', (self.username,))
            spellbooks = self.cursor.fetchall()
            
            if not spellbooks:
                self.show_welcome_message()
                return
            
            row_layout = QHBoxLayout()
            for i, spellbook in enumerate(spellbooks):
                if i > 0 and i % 3 == 0:
                    self.shelf_layout.addLayout(row_layout)
                    row_layout = QHBoxLayout()
                
                spellbook_button = QPushButton(spellbook['title'])
                spellbook_button.setFixedSize(150, 200)
                spellbook_button.setStyleSheet("background-image: url(spellbook.png); background-repeat: no-repeat; background-position: center; color: white; font-weight: bold;")
                spellbook_button.clicked.connect(lambda _, title=spellbook['title']: self.open_spellbook(title))
                row_layout.addWidget(spellbook_button)

            if row_layout.count() > 0:
                self.shelf_layout.addLayout(row_layout)

        except mysql.connector.Error as err:
            QMessageBox.warning(self, "Error", f"Could not load spellbooks: {err}")

    # creation of a new spellbook
    def add_new_spellbook(self):
        title, ok = QInputDialog.getText(self, "New Spellbook", "Enter spellbook name:")
        if ok and title:
            try:
                self.cursor.execute('''
                    INSERT INTO spellbooks (username, title)
                    VALUES (%s, %s)
                ''', (self.username, title))
                self.conn.commit()
                self.open_spellbook(title)
            except mysql.connector.Error as err:
                QMessageBox.warning(self, "Error", f"Could not create spellbook: {err}")

    # when user clicks on a spellbook, opens up the to do list page
    def open_spellbook(self, title):
        try:
            self.cursor.execute('''
                SELECT * FROM spellbooks
                WHERE username = %s AND title = %s
            ''', (self.username, title))
            spellbook = self.cursor.fetchone()
            
            if spellbook:
                spellbook_instance = SpellBook(
                    username=self.username,
                    spellbook_id=spellbook['id'],
                    title=spellbook['title'],
                    conn=self.conn
                )
                
                # clears out all the trash
                for i in reversed(range(self.layout().count())): 
                    widget = self.layout().itemAt(i).widget()
                    if widget is not None:
                        widget.setParent(None)
                
                # builds our classic container page
                container = QWidget()
                
                self.setCentralWidget(container)

                self.background_label = QLabel(container)
                self.background_label.setPixmap(QPixmap("bk.png").scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio))
                self.background_label.setGeometry(0, 0, self.width(), self.height())
                self.background_label.lower() 

                main_layout = QHBoxLayout()
                left_side_layout = QVBoxLayout()
                right_side_layout = QVBoxLayout()

                
                button_layout = QHBoxLayout()
                # right_side_layout.addSpacing(30)

                potions_button = QPushButton("Potions")
                potions_button.setStyleSheet("""
                    background-color: #f7e9e2; 
                    color: #341b10; 
                    font-size: 24px; 
                    padding: 5px; 
                    padding-top: 8px;
                    border-top-width: 4px;     
                    border-bottom-width: 4px; 
                    border-left-width: 9px;    
                    border-right-width: 9px;
                    border-radius: 6px;
                    border-color: #341b10;
                    border-style: solid;
                """)

                potions_button.clicked.connect(self.open_potions_menu)

                potions_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed) 
                potions_button.setFixedWidth(200)  
                button_layout.addWidget(potions_button)

                spellbooks_button = QPushButton("Spellbooks")
                spellbooks_button.setStyleSheet("""
                    background-color: #f7e9e2; 
                    color: #341b10; 
                    font-size: 24px; 
                    padding: 5px; 
                    padding-top: 8px;
                    border-top-width: 4px;     
                    border-bottom-width: 4px; 
                    border-left-width: 9px;    
                    border-right-width: 9px;
                    border-radius: 6px;
                    border-color: #341b10;
                    border-style: solid;
                """)
                
                spellbooks_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed) 
                spellbooks_button.setFixedWidth(200) 
                button_layout.addWidget(spellbooks_button)

                right_side_layout.setContentsMargins(0, 80, 135, 0) 
                right_side_layout.addWidget(spellbook_instance)
                
                right_side_layout.addSpacing(100)
                right_side_layout.addLayout(button_layout)

                main_layout.addLayout(left_side_layout, stretch=1)
                main_layout.addLayout(right_side_layout, stretch=3)
                container.setLayout(main_layout)

                self.setWindowTitle(f"Spellbook: {title}")

            else:
                QMessageBox.warning(self, "Error", f"Spellbook '{title}' not found.")
        except mysql.connector.Error as err:
            QMessageBox.warning(self, "Error", f"Could not open spellbook: {err}")
        
    # u wrote this so
    def open_potions_menu(self):
        self.setWindowTitle("Just Brew It")
        self.setFixedSize(1600, 900)
        container = QWidget()
        self.setCentralWidget(container)

        self.background_label = QLabel(container)
        self.background_label.setPixmap(QPixmap("backgroundwall.png").scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio))
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.lower()
        main_layout = QHBoxLayout()
        top_shelf_layout = QHBoxLayout()
        bottom_shelf_layout = QHBoxLayout()

        back_button = QPushButton("Back")

        back_button.setStyleSheet("""
            background-color: white; 
            color: #341b10; 
            font-size: 40px; 
            padding: 10px; 
            padding-top: 8px;
            border-top-width: 4px;     
            border-bottom-width: 4px; 
            border-left-width: 9px;    
            border-right-width: 9px;
            border-radius: 6px;
            border-color: #341b10;
            border-style: solid;
        """)
        back_button.clicked.connect(self.return_to_spellbook_selection)
        back_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed) 
        back_button.setFixedWidth(300)
        main_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        container.setLayout(main_layout)

    def return_to_spellbook_selection(self):
        # clear the current layout
        for i in reversed(range(self.layout().count())): 
            widget = self.layout().itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        self.init_ui()
        self.load_spellbooks()
        self.setWindowTitle(f"Just Brew It - {self.username}'s Spellbooks")
    
    # :)
    def get_potion_color(arr: list[str]):
        for todo in arr:
            vals = [0,0,0,0,0,0]
            for char in todo:
                vals[0] += ord(char)**3
                vals[1] += ord(char)**5 - ord(char)**3 + 1
                vals[2] += ord(char)**9 - ord(char)**5 + ord(char)**3 + 1
                vals[3] += ord(char)**3 + ord(char)*5
                vals[4] += ord(char)**5 + ord(char)*10
                vals[5] += ord(char)**10 + ord(char)*20
            for i in range(6):
                vals[i] %= 16
        output = ""
        for val in vals:
            output += hex(val)[2:]
        return output

# opens gui
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())