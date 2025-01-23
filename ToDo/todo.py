import sys
import mysql.connector
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QWidget, QLineEdit, QCheckBox
from PyQt6.QtCore import Qt, QTimer


class SpellBook(QFrame):
    def __init__(self, username=None, spellbook_id=None, title=None, conn=None):
        super().__init__()
        
        # gives spellbook variables for later use
        self.username = username
        self.spellbook_id = spellbook_id
        self.title = title
        self.conn = conn
        self.cursor = self.conn.cursor(dictionary=True)

        # sets up style for building the page 
        # i honestly dont know if this is needed anymore but i dont want to break things
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
        
        # size of spellbook
        self.setFixedSize(1000, 700)
        self.spell_entries = []
        self.pages = [[], []]
        
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_database)
        self.current_entry = None

        # sets up spellbook itself
        self.init_spellbook()
        self.load_saved_entries()

    def init_spellbook(self):
        main_layout = QHBoxLayout(self)
        # margins are slightly off
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.current_page = 0

        # there are 2 pages per spellbook (for now)
        # each with 18 entry slots
        for page_index in range(2):
            page_widget = QWidget()
            page_layout = QVBoxLayout(page_widget)
            page_layout.setSpacing(6)
            
            if page_index == 0:
                title_field = QLineEdit()
                title_field.setText(self.title)
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
                title_field.setTextMargins(10, 10, 30, 10)
            
            # makes the 18 entry slots
            for i in range(18):
                entry_widget = QWidget()
                entry_layout = QHBoxLayout(entry_widget)
                entry_layout.setContentsMargins(5, 1, 5, 5)
                
                # click for next spell button
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
                
                # sets up check box
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
    
                # sets up removal button
                remove_button = QPushButton("×")
                remove_button.setFixedWidth(25)
                remove_button.setProperty("class", "remove-button")
                remove_button.hide()
                remove_button.clicked.connect(lambda _, entry=spell_entry: self.remove_spell(entry))
                
                # sets up the next box that can be typed in
                spell_entry.plus_label = plus_label
                spell_entry.checkbox = checkbox
                spell_entry.remove_button = remove_button
                spell_entry.entry_index = len(self.spell_entries)
                
                # connects changing the text with editing the db spell_entries entry
                # as well as multiline comment handling
                spell_entry.textChanged.connect(self.handle_text_changed)
                
                # adds all to frame
                entry_layout.addWidget(plus_label)
                entry_layout.addWidget(checkbox)
                entry_layout.addWidget(spell_entry, stretch=1)
                entry_layout.addWidget(remove_button)
                
                page_layout.addWidget(entry_widget)
                self.pages[page_index].append((spell_entry, checkbox))
                self.spell_entries.append(spell_entry)
            
            # i added this a long time ago and idk if its still needed
            if page_index == 1:
                add_spell_button = QPushButton("Click to insert a spell")
                add_spell_button.hide()
                page_layout.addWidget(add_spell_button)
            
            page_layout.addStretch()
            
            main_layout.addWidget(page_widget)
            if page_index == 0:
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.VLine)
                separator.setStyleSheet("background-color: #341b10;")
                main_layout.addWidget(separator)

        self.update_entry_states()
    
    # for mysql, loads user's past entries for the spellbook if there are any
    def load_saved_entries(self):
        try:
            self.cursor.execute('''
                SELECT * FROM spell_entries 
                WHERE spellbook_id = %s 
                ORDER BY entry_index
            ''', (self.spellbook_id,))
            
            saved_entries = self.cursor.fetchall()
         
            # places entries in spellbook   
            max_entry_index = max([entry['entry_index'] for entry in saved_entries], default=-1)
            while len(self.spell_entries) <= max_entry_index:
                page_layout = self.layout().itemAt(0).widget().layout()
                
                entry_widget = QWidget()
                entry_layout = QHBoxLayout(entry_widget)
                entry_layout.setContentsMargins(4, 0, 0, 4)
                
                page_layout.insertWidget(page_layout.count() - 1, entry_widget)
                self.spell_entries.append(spell_entry)
            
            current_parent = None
            for entry_data in saved_entries:
                entry_index = entry_data['entry_index']
                text = entry_data['text']
                is_checked = entry_data['is_checked']
                parent_index = entry_data['parent_index']
                
                if entry_index < len(self.spell_entries):
                    spell_entry = self.spell_entries[entry_index]
                    spell_entry.setText(text)
                    spell_entry.checkbox.setChecked(is_checked)
                    
                    if parent_index == entry_index:
                        current_parent = spell_entry
                        spell_entry.remove_button.show()
                        spell_entry.checkbox.show()
                        spell_entry.plus_label.hide()
                        if hasattr(spell_entry, 'parent_entry'):
                            delattr(spell_entry, 'parent_entry')
                    else:
                        spell_entry.parent_entry = current_parent
                        spell_entry.remove_button.hide()
                        spell_entry.checkbox.hide()
                        spell_entry.plus_label.hide()
            
            # ensures the last entry of each multiline entry shows the remove button
            for i, entry in enumerate(self.spell_entries):
                if entry.text() and hasattr(entry, 'parent_entry'):
                    next_entry = self.spell_entries[i+1] if i+1 < len(self.spell_entries) else None
                    if next_entry is None or not hasattr(next_entry, 'parent_entry') or next_entry.text() == "":
                        entry.remove_button.show()
                        entry.parent_entry.remove_button.hide()
            
            self.update_entry_states()
                                
        except mysql.connector.Error as err:
            print(f"Error loading saved entries: {err}")
        
    # for mysql, ensures checkbox's state is maintained
    def handle_checkbox_changed(self):
        checkbox = self.sender()
        spell_entry = None
        
        # find corresponding spell
        for entry in self.spell_entries:
            if entry.checkbox == checkbox:
                spell_entry = entry
                break
        
        # if spell entry exists, update in the db
        if spell_entry:
            try:
                self.cursor.execute('''
                    UPDATE spell_entries 
                    SET is_checked = %s 
                    WHERE spellbook_id = %s AND page_number = %s AND entry_index = %s
                ''', (
                    checkbox.isChecked(),
                    self.spellbook_id,
                    # determine page number
                    0 if spell_entry.entry_index < 36 else 1,  
                    spell_entry.entry_index
                ))
                self.conn.commit()
                
            except mysql.connector.Error as err:
                print(f"Error updating checkbox state: {err}")
                self.conn.rollback()

    # handles multiline entries and adding entries to db
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
            
        # set remove button on last line of entry
        # set check box on first line of entry 
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
        
        # set the current entry and start/restart the timer
        self.current_entry = spell_entry
        self.update_timer.start(1000)  

        self.update_entry_states()

    # bro this thing made me want to quit
    # it has a timer set to add entries to the db
    # dels old versions of the entry
    def update_database(self):
        if not self.current_entry:
            return

        spell_entry = self.current_entry
        text = spell_entry.text()
        page_number = 0 if spell_entry.entry_index < 36 else 1

        try:
            if hasattr(spell_entry, 'parent_entry'):
                parent_index = spell_entry.parent_entry.entry_index
            else:
                parent_index = spell_entry.entry_index 

            # first, deletes any existing entry
            self.cursor.execute('''
                DELETE FROM spell_entries 
                WHERE spellbook_id = %s AND entry_index = %s
            ''', (self.spellbook_id, spell_entry.entry_index))

            # inserts the new/updated entry
            self.cursor.execute('''
                INSERT INTO spell_entries 
                (spellbook_id, page_number, entry_index, parent_index, is_checked, text) 
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                self.spellbook_id, 
                page_number, 
                spell_entry.entry_index,
                parent_index, 
                spell_entry.checkbox.isChecked(),
                text
            ))
            self.conn.commit()
        
        except mysql.connector.Error as err:
            print(f"Error updating database: {err}")
            self.conn.rollback()

        self.current_entry = None
    
    # removes spell from gui and db
    def remove_spell(self, entry_to_remove):
        # groups multilines together
        try:
            entry_index = entry_to_remove.entry_index

            if hasattr(entry_to_remove, 'parent_entry'):
                entry_index = entry_to_remove.parent_entry.entry_index

            # deletes from db
            try:
                self.cursor.execute('''
                    DELETE FROM spell_entries 
                    WHERE spellbook_id = %s AND (entry_index = %s OR parent_index = %s)
                ''', (self.spellbook_id, entry_index, entry_index))

                num_removed = self.cursor.rowcount

                self.cursor.execute('''
                    UPDATE spell_entries
                    SET entry_index = entry_index - %s,
                        parent_index = CASE 
                            WHEN parent_index > %s THEN parent_index - %s 
                            ELSE parent_index 
                        END
                    WHERE spellbook_id = %s AND entry_index > %s
                ''', (num_removed, entry_index, num_removed, self.spellbook_id, entry_index))

                self.conn.commit()
            except mysql.connector.Error as err:
                print(f"Error removing entries from database: {err}")
                self.conn.rollback()
                return

            entries_to_remove = [entry for entry in self.spell_entries if 
                                entry.entry_index == entry_index or 
                                (hasattr(entry, 'parent_entry') and entry.parent_entry.entry_index == entry_index)]

            num_to_remove = len(entries_to_remove)

            # adjusting gui
            for i in range(entry_index, len(self.spell_entries) - num_to_remove):
                current_entry = self.spell_entries[i]
                next_entry = self.spell_entries[i + num_to_remove]
                
                current_entry.setText(next_entry.text())
                current_entry.checkbox.setChecked(next_entry.checkbox.isChecked())
                
                if hasattr(next_entry, 'parent_entry'):
                    if next_entry.parent_entry.entry_index > entry_index:
                        current_entry.parent_entry = self.spell_entries[next_entry.parent_entry.entry_index - num_to_remove]
                    else:
                        current_entry.parent_entry = next_entry.parent_entry
                elif hasattr(current_entry, 'parent_entry'):
                    delattr(current_entry, 'parent_entry')

            for i in range(len(self.spell_entries) - num_to_remove, len(self.spell_entries)):
                entry = self.spell_entries[i]
                entry.setText("")
                entry.checkbox.setChecked(False)
                if hasattr(entry, 'parent_entry'):
                    delattr(entry, 'parent_entry')

            current_parent = None
            for i, entry in enumerate(self.spell_entries):
                entry.entry_index = i
                if not entry.text():
                    current_parent = None
                    entry.remove_button.hide()
                    entry.checkbox.hide()
                    entry.plus_label.show()
                elif not hasattr(entry, 'parent_entry') or (current_parent is None):
                    current_parent = entry
                    entry.remove_button.show()
                    entry.checkbox.show()
                    entry.plus_label.hide()
                    if hasattr(entry, 'parent_entry'):
                        delattr(entry, 'parent_entry')
                else:
                    entry.parent_entry = current_parent
                    entry.remove_button.hide()
                    entry.checkbox.hide()
                    entry.plus_label.hide()

                # adjusting indices in db
                try:
                    if entry.text():
                        parent_index = current_parent.entry_index if current_parent and current_parent != entry else entry.entry_index
                        self.cursor.execute('''
                            UPDATE spell_entries
                            SET parent_index = %s
                            WHERE spellbook_id = %s AND entry_index = %s
                        ''', (parent_index, self.spellbook_id, entry.entry_index))
                        self.conn.commit()
                except mysql.connector.Error as err:
                    print(f"Error updating parent index in database: {err}")
                    self.conn.rollback()

                # dictates remove button showing
                if current_parent:
                    next_entry = self.spell_entries[i+1] if i+1 < len(self.spell_entries) else None
                    if next_entry is None or not hasattr(next_entry, 'parent_entry') or next_entry.text() == "":
                        entry.remove_button.show()
                        if current_parent != entry:
                            current_parent.remove_button.hide()
                    else:
                        entry.remove_button.hide()

            self.update_entry_states()

        except Exception as e:
            print(f"An error occurred in remove_spell: {e}")
            
    def is_next_available_entry(self, entry):
        index = entry.entry_index
        if index == 0:
            return True
        prev_entry = self.spell_entries[index - 1]
        return bool(prev_entry.text())

    # updates click to add spell line 
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