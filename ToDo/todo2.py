import sys, random, math
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QMainWindow


def onclick():
    arr = ["hello!", "hows it hanging!", "wahoo", "yippee", "i am suffering actively"]
    result = get_potion_color(arr)
    print(result)

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
window = QMainWindow()

window.setWindowTitle(":}")

button = QPushButton("Click me!")
button.clicked.connect(onclick)
window.setFixedSize(QSize(800,600))
window.setCentralWidget(button)


window.show()
sys.exit(app.exec())

