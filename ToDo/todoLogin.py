import sys
from todo import SpellBook
import mysql.connector
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLineEdit, QLabel, QSizePolicy, QMessageBox, QInputDialog, QStackedLayout, QStackedWidget)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QPoint

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
            # self.load_spellbooks()
            pass
        else:
            self.show_welcome_message()

    # if user has no spells
    def show_welcome_message(self):
        welcome_label = QLabel(f"Welcome, {self.username}! Click the '+' button to create your first spellbook.")
        welcome_label.setStyleSheet("color: white; font-size: 18px;")
        self.shelf_layout.addWidget(welcome_label, alignment=Qt.AlignmentFlag.AlignCenter)
    
    # builds shelf window
    def init_ui(self):
        container = QWidget()
        self.setCentralWidget(container)

        # Background setup
        self.background_label = QLabel(container)
        self.background_label.setPixmap(QPixmap("bookshelf.png").scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio))
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.lower()

        # book buttons setup
        # bro
        # the amount of time this took me 
        # is so embarrassing
        # i had to go back and just remake the images bc i couldnt figure it out
        self.book_buttons = []
        # pot_button = ImageButton("potshelf.png", 1, lambda idx=1: self.pot_clicked(), container)
        # pot_button.setGeometry(0, 0, pot_button.width(), pot_button.height())
        # pot_button.show()
        
        book_button = ImageButton("book1.png", 1, lambda idx=1: self.book_clicked(1), container)
        book_button.setGeometry(573, 697, book_button.width(), book_button.height())
        self.book_buttons.append(book_button)

        book_button2 = ImageButton("book2.png", 2, lambda idx=2: self.book_clicked(2), container)
        book_button2.setGeometry(667, 900-304, book_button2.width(), book_button2.height())
        self.book_buttons.append(book_button2)
        
        book_button2 = ImageButton("book3.png", 2, lambda idx=2: self.book_clicked(3), container)
        book_button2.setGeometry(600, 900-447, book_button2.width(), book_button2.height())
        self.book_buttons.append(book_button2)
        
        book_button2 = ImageButton("book4.png", 2, lambda idx=2: self.book_clicked(4), container)
        book_button2.setGeometry(645, 900-573, book_button2.width(), book_button2.height())
        self.book_buttons.append(book_button2)
        
        book_button2 = ImageButton("book5.png", 2, lambda idx=2: self.book_clicked(5), container)
        book_button2.setGeometry(736, 900-662, book_button2.width(), book_button2.height())
        self.book_buttons.append(book_button2)
        
        book_button2 = ImageButton("book6.png", 2, lambda idx=2: self.book_clicked(6), container)
        book_button2.setGeometry(701, 900-857, book_button2.width(), book_button2.height())
        self.book_buttons.append(book_button2)
        
        self.load_existing_spellbooks()
        
            
    
    def pot_clicked(self):
        self.open_potions_menu()
        
    def book_clicked(self, index):
        try:
            self.cursor.execute('SELECT title FROM spellbooks WHERE username = %s AND id = %s', 
                            (self.username, index))
            result = self.cursor.fetchone()
            
            if result:
                self.open_spellbook(result['title'])
            else:
                self.add_new_spellbook(index)
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
                
                
    def load_existing_spellbooks(self):
        try:
            self.cursor.execute('''
                SELECT title, book_index 
                FROM spellbooks 
                WHERE username = %s
            ''', (self.username,))
            spellbooks = self.cursor.fetchall()
            
            for spellbook in spellbooks:
                book_index = spellbook['book_index']
                if 0 <= book_index-1 < len(self.book_buttons):
                    button = self.book_buttons[book_index-1]
                    button.setText(spellbook['title'])

                    button.clicked.disconnect()
                    button.clicked.connect(lambda _, t=spellbook['title']: self.open_spellbook(t))
            
        except mysql.connector.Error as err:
            print(f"Error loading spellbooks: {err}")
    def add_new_spellbook(self, book_index):
        title, ok = QInputDialog.getText(self, "New Spellbook", "Enter spellbook name:")
        if ok and title:
            try:
                self.cursor.execute('''
                    SELECT * FROM spellbooks 
                    WHERE username = %s AND title = %s
                ''', (self.username, title))
                existing_book = self.cursor.fetchone()
                
                if existing_book:
                    QMessageBox.warning(self, "Error", "A spellbook with this name already exists.")
                    return
                
                self.cursor.execute('''
                    INSERT INTO spellbooks (username, title, book_index)
                    VALUES (%s, %s, %s)
                ''', (self.username, title, book_index))
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
                spellbooks_button.clicked.connect(self.init_ui)

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
        
    # u wrote this so i feel like it would be weird if i commented it
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
        for i in reversed(range(self.layout().count())): 
            widget = self.layout().itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        self.init_ui()
        self.load_existing_spellbooks()
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


class ImageButton(QPushButton):
    def __init__(self, image_path, index, handler, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap(image_path)
        self.setIcon(QIcon(self.pixmap))
        self.setIconSize(self.pixmap.size())
        self.setFixedSize(self.pixmap.size())
        self.index = index
        self.handler = handler
        self.clicked.connect(self.handler)
        self.text_label = QLabel(self)
        self.text_label.setStyleSheet("color: white; text-align: center;  font-size: 65px;")
        # self.text_label.move((self.pixmap.width() // 2) - self.text_label.width(), (self.pixmap.height() // 3) - ( self.text_label.height() - 10))

    def setText(self, text):
        self.text_label.setText(text)
        
    def hitButton(self, point):
        color = self.pixmap.toImage().pixelColor(point)
        return color.alpha() > 0


# opens gui
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())