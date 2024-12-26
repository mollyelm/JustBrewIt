import sys, random, math
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QMainWindow


def onclick():
    for i in range(math.floor(random.random() * 10)):
        print("Hello World")
    print("////")

app = QApplication(sys.argv)
window = QMainWindow()

window.setWindowTitle(":}")

button = QPushButton("Click me!")
button.clicked.connect(onclick)
window.setFixedSize(QSize(800,600))
window.setCentralWidget(button)


window.show()
sys.exit(app.exec())

