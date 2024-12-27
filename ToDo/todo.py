import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QWidget, QSizePolicy, QLineEdit, QCheckBox
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QRect

class SpellBook(QFrame):
    def __init__(self):
        super().__init__()
        
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
                padding: 5px;
                margin: 2px;
                color: #341b10; 

            }
            QPushButton {
                color: white;
                background-color: #341b10;
                padding: 8px;
                font-size: 14px;
                border-radius: 5px;
            }
        """)
        
        self.setFixedSize(1000, 700)
        self.spell_entries = []
        self.pages = [[], []]
        
        self.init_spellbook()

    def init_spellbook(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        for page_index in range(2):
            page_widget = QWidget()
            page_layout = QVBoxLayout(page_widget)
            page_layout.setSpacing(10)
            
            if page_index == 0:
                title_field = QLineEdit()
                title_field.setPlaceholderText("Enter Spellbook Title")
                title_field.setStyleSheet("""
                    QLineEdit {
                        font-size: 24px;
                        font-weight: bold;
                        padding: 10px;
                        margin-bottom: 20px;
                        border: none;
                        color: #341b10; 
                    }
                """)
                page_layout.addWidget(title_field)
            
            for i in range(18):
                entry_widget = QWidget()
                entry_layout = QHBoxLayout(entry_widget)
                entry_layout.setContentsMargins(5, 2, 5, 2)
                
                plus_label = QLabel("+")
                plus_label.setFixedWidth(25)
                plus_label.setStyleSheet("""
                    QLabel {
                        color: #341b10;
                        font-size: 20px;
                        font-weight: bold;
                        padding: 0px;
                    }
                """)
                plus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                checkbox = QCheckBox()
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
                spell_entry.setPlaceholderText(f"Enter Spell Name")
                
                spell_entry.plus_label = plus_label
                spell_entry.checkbox = checkbox
                
                spell_entry.textChanged.connect(self.handle_text_changed)
                
                entry_layout.addWidget(plus_label)
                entry_layout.addWidget(checkbox)
                entry_layout.addWidget(spell_entry, stretch=1)
                
                page_layout.addWidget(entry_widget)
                self.pages[page_index].append((spell_entry, checkbox))
                self.spell_entries.append(spell_entry)
            
            if page_index == 1:
                add_spell_button = QPushButton("Click to insert a spell")
                page_layout.addWidget(add_spell_button)
                add_spell_button.clicked.connect(self.insert_spell)
            
            page_layout.addStretch()
            
            main_layout.addWidget(page_widget)
            if page_index == 0:
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.VLine)
                separator.setStyleSheet("background-color: #341b10;")
                main_layout.addWidget(separator)

    def handle_text_changed(self, text):
        spell_entry = self.sender()
        plus_label = spell_entry.plus_label
        checkbox = spell_entry.checkbox
        
        if text:
            plus_label.hide()
            checkbox.show()
        else:
            plus_label.show()
            checkbox.hide()
            checkbox.setChecked(False)

    def insert_spell(self):
        for spell_entry in self.spell_entries:
            if not spell_entry.text():
                spell_entry.setFocus()
                return

    def paintEvent(self, event):
        super().paintEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Just Brew It")
        self.setFixedSize(1600, 900)

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
        potions_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed) 
        potions_button.setFixedWidth(300)  
        button_layout.addWidget(potions_button)

        spellbooks_button = QPushButton("Spellbooks")
        spellbooks_button.setStyleSheet("""
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
        spellbooks_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed) 
        spellbooks_button.setFixedWidth(300) 
        button_layout.addWidget(spellbooks_button)

        right_side_layout.addLayout(button_layout)
        right_side_layout.addSpacing(30)

        spellbook = SpellBook()
        right_side_layout.addWidget(spellbook)

        main_layout.addLayout(left_side_layout, stretch=1)
        main_layout.addLayout(right_side_layout, stretch=3)
        container.setLayout(main_layout)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()