import sys
# import mysql.connector
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QWidget, QSizePolicy, QLineEdit, QCheckBox
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QRect


class SpellBook(QFrame):
    def __init__(self, host="localhost", user="spellbook_remote", password="your_secure_password"):        
        super().__init__()
        
        self.user_id = 1

        # try:
        #     self.conn = mysql.connector.connect(
        #         host = host,
        #         user = user,
        #         password = password,
        #         database ="spellbook_db"
        #     )
        #     self.cursor = self.conn.cursor(dictionary=True)
        
        # except mysql.connector.Error as err:
        #     print(f"Error connecting to MySQL: {err}")
        #     sys.exit(1)
            

        self.setStyleSheet("""
            QFrame {
                background-color: #f7e9e2;
                border: 2px solid #341b10;
                border-radius: 10px;
            }
            QLineEdit {
                background-color: transparent;
                border: none;
                border-bottom: 1px solid #341b10;
                padding: 10px 5px 23px 5px; 
                margin: 4px 2px;
                color: #341b10;
                font-size: 14px;
                line-height: 20px;
            }
            QLineEdit:disabled {
                color: #9e8b84;
                border-bottom: 1px solid #9e8b84;
            }
            QPushButton {
                color: white;
                background-color: #341b10;
                padding: 8px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton.remove-button {
                color: #341b10;
                background-color: transparent;
                border: none;
                font-size: 16px;
                padding: 0px;
                margin: 0px;
                font-weight: bold;
            }
            QPushButton.remove-button:hover {
                color: #d4533c;
            }
        """)
        
        self.setFixedSize(1000, 700)
        self.spell_entries = []
        self.pages = [[], []]
        
        self.init_spellbook()
        # self.load_saved_entries()


    def init_spellbook(self):
        main_layout = QHBoxLayout(self)
        # margins are slightly off
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.current_page = 0

        for page_index in range(2):
            page_widget = QWidget()
            page_layout = QVBoxLayout(page_widget)
            page_layout.setSpacing(6)
            
            if page_index == 0:
                title_field = QLineEdit()
                title_field.setPlaceholderText("Enter Spellbook Title")
                title_field.setStyleSheet("""
                    QLineEdit {
                        font-size: 24px;
                        font-weight: bold;
                        padding: 15px 20px;
                        margin-bottom: 20px;
                        border: none;
                        color: #341b10;
                        line-height: 20px;
                    }
                """)
                page_layout.addWidget(title_field)
                # margins are slightly off
                title_field.setTextMargins(0, 10, 0, 0)

            for i in range(18):
                entry_widget = QWidget()
                entry_layout = QHBoxLayout(entry_widget)
                # margins are slightly off 
                entry_layout.setContentsMargins(4, 0, 0, 4)
                
                plus_label = QLabel("+")
                plus_label.setFixedWidth(25)
                plus_label.setStyleSheet("""
                    QLabel {
                        color: #341b10;
                        font-size: 30px;
                        font-weight: bolder;
                        border: none;
                        padding: 0px;
                    }
                """)
                plus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                checkbox = QCheckBox()
                checkbox.stateChanged.connect(self.handle_checkbox_changed)
                checkbox.setFixedWidth(25)
                checkbox.setStyleSheet("""
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                        border: 2px solid #341b10;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #341b10;
                    }
                """)
                checkbox.hide()  
                
                spell_entry = QLineEdit()
                spell_entry.setPlaceholderText("")
                spell_entry.raise_()

                remove_button = QPushButton("×")
                remove_button.setFixedWidth(25)
                remove_button.setProperty("class", "remove-button")
                remove_button.hide()
                remove_button.clicked.connect(lambda _, entry=spell_entry: self.remove_spell(entry))

                spell_entry.plus_label = plus_label
                spell_entry.checkbox = checkbox
                spell_entry.remove_button = remove_button
                spell_entry.entry_index = len(self.spell_entries)

                spell_entry.textChanged.connect(self.handle_text_changed)
                
                entry_layout.addWidget(plus_label)
                entry_layout.addWidget(checkbox)
                entry_layout.addWidget(spell_entry, stretch=1)
                entry_layout.addWidget(remove_button)
                
                page_layout.addWidget(entry_widget)
                self.pages[page_index].append((spell_entry, checkbox))
                self.spell_entries.append(spell_entry)
            
            if page_index == 1:
                add_spell_button = QPushButton("Click to insert a spell")
                page_layout.addWidget(add_spell_button)
                add_spell_button.hide()
                            
            page_layout.addStretch()
            
            main_layout.addWidget(page_widget)
            if page_index == 0:
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.VLine)
                separator.setStyleSheet("background-color: #341b10;")
                main_layout.addWidget(separator)
        
            # these are supposed to be arrows but the unicode doesnt show on mac
            self.next_page_button = QPushButton("🠆", self)
            self.prev_page_button = QPushButton("🠄", self)

            arrow_style = """
                QPushButton {
                    position: absolute;
                    color: #341b10;
                    background-color: transparent;
                    border: none;
                    font-size: 45px;
                    font-weight: 900;
                }
                QPushButton:hover {
                    color: #d4533c;
                }
            """
            
            self.next_page_button.setStyleSheet(arrow_style)
            self.prev_page_button.setStyleSheet(arrow_style)
            self.next_page_button.setGeometry(self.width() - 60, self.height() - 60, 60, 60)
            self.prev_page_button.setGeometry(0, self.height() - 60, 60, 60)
            
            self.next_page_button.raise_()
            self.prev_page_button.raise_()
            self.next_page_button.hide()
            self.prev_page_button.hide()
            
            self.next_page_button.clicked.connect(self.next_page)
            self.prev_page_button.clicked.connect(self.prev_page)

            self.update_entry_states()

    def next_page(self):
        self.current_page = 1
        # hide og page
        for i in range(36):
            self.spell_entries[i].parent().hide()

        # show next 
        for i in range(36, 72):
            entry = self.spell_entries[i]
            if not entry.text() and i == 36:
                entry.plus_label.show()
                entry.setPlaceholderText("Click to add a new spell...")
            entry.parent().show()
        self.check_arrow_visibility()

    def prev_page(self):
        self.current_page = 0
        # show og page 
        for i in range(36):
            self.spell_entries[i].parent().show()
        # hide prev page
        for i in range(36, 72):
            self.spell_entries[i].parent().hide()
        self.check_arrow_visibility()
        
    def check_arrow_visibility(self):
        self.prev_page_button.setVisible(self.current_page == 1)
        last_entry = self.spell_entries[35]
        self.next_page_button.setVisible(
            (self.current_page == 0 and bool(last_entry.text()))
        )

    # for mysql
    def load_saved_entries(self):
        # try:
        #     self.cursor.execute('''
        #         SELECT * FROM spell_entries 
        #         WHERE user_id = %s 
        #         ORDER BY page_number, entry_index
        #     ''', (self.user_id,))
            
        #     saved_entries = self.cursor.fetchall()
            
        #     for entry_data in saved_entries:
        #         page_number = entry_data['page_number']
        #         entry_index = entry_data['entry_index']
        #         text = entry_data['text']
        #         is_checked = entry_data['is_checked']
                
        #         spell_entry = self.spell_entries[entry_index]
        #         spell_entry.setText(text)
        #         spell_entry.checkbox.setChecked(is_checked)
                
        #     self.update_entry_states()
        #     self.check_arrow_visibility()
                
        # except mysql.connector.Error as err:
        #     print(f"Error loading saved entries: {err}")
        pass

    # for mysql
    def handle_checkbox_changed(self):
        # checkbox = self.sender()
        # spell_entry = None
        
        # # find corresponding spell
        # for entry in self.spell_entries:
        #     if entry.checkbox == checkbox:
        #         spell_entry = entry
        #         break
        # 
        # if spell_entry:
        #     try:
        #         self.cursor.execute('''
        #             UPDATE spell_entries 
        #             SET is_checked = %s 
        #             WHERE user_id = %s AND page_number = %s AND entry_index = %s
        #         ''', (
        #             checkbox.isChecked(),
        #             self.user_id,
        #             # determine page number
        #             0 if spell_entry.entry_index < 36 else 1,  
        #             spell_entry.entry_index
        #         ))
        #         self.conn.commit()
                
        #     except mysql.connector.Error as err:
        #         print(f"Error updating checkbox state: {err}")
        #         self.conn.rollback()
        pass

    def handle_text_changed(self, text):
        spell_entry = self.sender()
        plus_label = spell_entry.plus_label
        checkbox = spell_entry.checkbox
        remove_button = spell_entry.remove_button
        
        text_width = spell_entry.fontMetrics().boundingRect(text).width()
        # subtracting to account for padding, can alter if looks uggo
        available_width = spell_entry.width() - 20 

        # go next line  
        if text_width > available_width:
                next_index = spell_entry.entry_index + 1
                if next_index < len(self.spell_entries):
                    next_entry = self.spell_entries[next_index]
                    
                    words = text.split()
                    if len(words) > 1:
                        first_line = ' '.join(words[:-1])
                        to_move = words[-1]
                    else:
                        first_line = text[:-1]
                        to_move = text[-1]
                    
                    spell_entry.setText(first_line)
                    next_entry.setText(to_move)
                    
                    if hasattr(spell_entry, 'parent_entry'):
                        next_entry.parent_entry = spell_entry.parent_entry
                    else:
                        next_entry.parent_entry = spell_entry
                        
                    if not hasattr(spell_entry, 'parent_entry'):
                        checkbox.show()
                        remove_button.hide()
                    else:
                        checkbox.hide()
                        remove_button.hide()
                    
                    next_entry.checkbox.hide()
                    next_entry.remove_button.show()
                    
                    next_entry.setFocus()
                    next_entry.setCursorPosition(len(to_move))
                    return
            
        if text:
            plus_label.hide()
            if hasattr(spell_entry, 'parent_entry'):
                checkbox.hide()
                remove_button.show()
            else:
                checkbox.show()

            next_index = spell_entry.entry_index + 1
            
            if next_index >= len(self.spell_entries) or not hasattr(self.spell_entries[next_index], 'parent_entry'):
                remove_button.show()
            else:
                remove_button.hide()

        else:
            if self.is_next_available_entry(spell_entry):
                plus_label.show()

            checkbox.hide()
            checkbox.setChecked(False)
            remove_button.hide()
        
        # try:
            # page_number = 0
            # for page_side in range(len(self.pages)):
            #     for entry_index, (entry, checkbox) in enumerate(self.pages[page_side]):
            #         if entry == spell_entry:
            #             page_number = page_side
            #             break
            
            # if text:
            #     self.cursor.execute('''
            #         INSERT INTO spell_entries 
            #         (user_id, page_number, entry_index, text, is_checked) 
            #         VALUES (%s, %s, %s, %s, %s)
            #         ON DUPLICATE KEY UPDATE 
            #         text = %s, is_checked = %s
            #     ''', (
            #         self.user_id, 
            #         page_number, 
            #         spell_entry.entry_index, 
            #         text, 
            #         spell_entry.checkbox.isChecked(),
            #         text,
            #         spell_entry.checkbox.isChecked()
            #     ))
            #     self.conn.commit()
        
        # except mysql.connector.Error as err:
        #     print(f"error storing entry: {err}")
        #     self.conn.rollback()
        
        self.check_arrow_visibility()
        self.update_entry_states()

    def remove_spell(self, entry_to_remove):
        if hasattr(entry_to_remove, 'parent_entry'):
            first_entry = entry_to_remove.parent_entry

            while hasattr(first_entry, 'parent_entry'):
                first_entry = first_entry.parent_entry

        else:
            first_entry = entry_to_remove
        
        linked_entries = [first_entry]
        current_entry = first_entry
        current_index = first_entry.entry_index
        
        while current_index + 1 < len(self.spell_entries):
            next_entry = self.spell_entries[current_index + 1]
            if hasattr(next_entry, 'parent_entry') and next_entry.parent_entry == first_entry:
                linked_entries.append(next_entry)
                current_index += 1
            else:
                break
        
        num_to_remove = len(linked_entries)
        remove_start = first_entry.entry_index
        
        for i in range(remove_start, len(self.spell_entries) - num_to_remove):
            current_entry = self.spell_entries[i]
            next_entry = self.spell_entries[i + num_to_remove]
            
            current_entry.setText(next_entry.text())
            current_entry.checkbox.setChecked(next_entry.checkbox.isChecked())
            current_entry.checkbox.hide()
            current_entry.remove_button.hide()
            
            if hasattr(next_entry, 'parent_entry'):
                original_parent = next_entry.parent_entry

                while hasattr(original_parent, 'parent_entry'):
                    original_parent = original_parent.parent_entry
                    
                new_parent_index = original_parent.entry_index - num_to_remove
                if new_parent_index >= 0:
                    current_entry.parent_entry = self.spell_entries[new_parent_index]
                    next_next_index = i + num_to_remove + 1
                    is_last_in_group = (next_next_index >= len(self.spell_entries) or 
                                      not hasattr(self.spell_entries[next_next_index], 'parent_entry') or
                                      self.spell_entries[next_next_index].parent_entry != next_entry.parent_entry)
                    
                    if is_last_in_group:
                        current_entry.remove_button.show()
            else:
                if hasattr(current_entry, 'parent_entry'):
                    delattr(current_entry, 'parent_entry')
                current_entry.checkbox.show()
        
        for i in range(num_to_remove):
            entry = self.spell_entries[-(i+1)]
            entry.setText("")
            entry.checkbox.setChecked(False)
            entry.checkbox.hide()
            entry.remove_button.hide()
            if hasattr(entry, 'parent_entry'):
                delattr(entry, 'parent_entry')
        
            entry_index = remove_start
            while entry_index < len(self.spell_entries):
                entry = self.spell_entries[entry_index]
                
                entry.checkbox.hide()
                entry.remove_button.hide()
                
                if entry.text():
                    if not hasattr(entry, 'parent_entry'):
                        entry.checkbox.show()
                        next_index = entry_index + 1

                        if (next_index >= len(self.spell_entries) or 
                            not hasattr(self.spell_entries[next_index], 'parent_entry') or
                            self.spell_entries[next_index].parent_entry != entry):
                            entry.remove_button.show()
                    else:
                        next_index = entry_index + 1
                        is_last_in_group = (next_index >= len(self.spell_entries) or 
                                        not hasattr(self.spell_entries[next_index], 'parent_entry') or
                                        self.spell_entries[next_index].parent_entry != entry.parent_entry)
                        if is_last_in_group:
                            entry.remove_button.show()
                
                entry_index += 1

            self.check_arrow_visibility()
            self.update_entry_states()

    def is_next_available_entry(self, entry):
        index = entry.entry_index
        if index == 0:
            return True
        prev_entry = self.spell_entries[index - 1]
        return bool(prev_entry.text())

    def update_entry_states(self):
        found_empty = False
        for i, entry in enumerate(self.spell_entries):
            if i == 0:
                entry.setEnabled(True)
                is_empty = not bool(entry.text())
                entry.plus_label.setVisible(is_empty)
                entry.setPlaceholderText("Click to add a new spell..." if is_empty else "")
                continue
                
            prev_entry = self.spell_entries[i - 1]
            should_enable = bool(prev_entry.text())
            
            entry.setEnabled(should_enable)
            
            if not found_empty and should_enable:
                is_empty = not bool(entry.text())
                entry.plus_label.setVisible(is_empty)
                entry.setPlaceholderText("Click to add a new spell..." if is_empty else "")
                if is_empty:
                    found_empty = True
            else:
                entry.plus_label.hide()
                entry.setPlaceholderText("")

    # def insert_spell(self):
    #     for spell_entry in self.spell_entries:
    #         if not spell_entry.text():
    #             spell_entry.setFocus()
    #             return

    def paintEvent(self, event):
        super().paintEvent(event)

class MainWindow(QMainWindow):
    potion_list = []

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Just Brew It")
        self.setFixedSize(1600, 900)
        
        self.show_connection_dialog()

        # dont think its needed anymore 
        # self.open_main_screen()
        
    def show_connection_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Connect to Database")
        layout = QVBoxLayout()
        
        host_label = QLabel("Host IP:")
        self.host_input = QLineEdit("localhost")
        user_label = QLabel("Username:")
        self.user_input = QLineEdit("spellbook_remote")
        pass_label = QLabel("Password:")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addWidget(host_label)
        layout.addWidget(self.host_input)
        layout.addWidget(user_label)
        layout.addWidget(self.user_input)
        layout.addWidget(pass_label)
        layout.addWidget(self.pass_input)
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(lambda: self.connect_to_db(dialog))
        layout.addWidget(connect_btn)
        
        dialog.setLayout(layout)
        dialog.exec()

    def connect_to_db(self, dialog):
        host = self.host_input.text()
        user = self.user_input.text()
        password = self.pass_input.text()
        
        container = QWidget()
        self.setCentralWidget(container)

        self.background_label = QLabel(container)
        self.background_label.setPixmap(QPixmap("background.png").scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio))
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.lower() 

        main_layout = QHBoxLayout()
        left_side_layout = QVBoxLayout()
        right_side_layout = QVBoxLayout()

        self.avatar_label = QLabel()
        self.avatar_pixmap = QPixmap("avatar.png")
        self.avatar_pixmap = self.avatar_pixmap.scaledToWidth(500)
        self.avatar_label.setPixmap(self.avatar_pixmap)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_side_layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout()
        right_side_layout.addSpacing(30)

        potions_button = QPushButton("Potions")
        potions_button.setStyleSheet("""
            background-color: #f7e9e2; 
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

        potions_button.clicked.connect(self.open_potions_menu)

        potions_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed) 
        potions_button.setFixedWidth(300)  
        button_layout.addWidget(potions_button)

        spellbooks_button = QPushButton("Spellbooks")
        spellbooks_button.setStyleSheet("""
            background-color: #f7e9e2; 
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
        spellbooks_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed) 
        spellbooks_button.setFixedWidth(300) 
        button_layout.addWidget(spellbooks_button)

        right_side_layout.addLayout(button_layout)
        right_side_layout.addSpacing(30)

        spellbook = SpellBook(host=host, user=user, password=password)
        right_side_layout.addWidget(spellbook)

        main_layout.addLayout(left_side_layout, stretch=1)
        main_layout.addLayout(right_side_layout, stretch=3)
        container.setLayout(main_layout)

        dialog.accept()
        
    # mysql close db
    # def __del__(self):
    #     if hasattr(self, 'conn'):
    #         self.conn.close()

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
        back_button.clicked.connect(self.open_main_screen)
        back_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed) 
        back_button.setFixedWidth(300)
        main_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        container.setLayout(main_layout)
    
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

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()