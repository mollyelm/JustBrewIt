import sys, random, math
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QMainWindow, QVBoxLayout, QColorDialog
from PyQt6.QtGui import QPixmap, QPainter, QColor, QImage

class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(":]")
        self.resize(400, 400)
        self.button = QPushButton("Click me!!!")
        self.button.clicked.connect(self.onclick)
        self.setCentralWidget(self.button)

    def onclick(self):
        arr = ["apple", "banana", "strawberry", "tomato"]  # change this to get different colors!
        hex = self.get_potion_color(arr)
        if random.random() < 0.5:
            potion_path = "potion.png"
        else:
            potion_path = "potion2.png"
        potion = self.recolor_image(potion_path, "#" + hex)
        pixmap = QPixmap.fromImage(potion)
        self.label = QLabel()
        self.label.setPixmap(pixmap)
        self.label.setWindowTitle("wow a cool looking potion! isnt that neat!")
        self.label.resize(pixmap.width(), pixmap.height())
        self.label.show()

    def get_potion_color(self, arr: list[str]):
        vals = [0,0,0,0,0,0]
        for todo in arr:
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
    
    def recolor_image(self, image_path, target_color_hex):
        image = QImage(image_path)
        target_color = QColor(target_color_hex)
        gray_color = QColor(128, 128, 128) # color to be replaced
        tolerance = 20  # i havent tested it but this should help create a bubbly effect

        for x in range(image.width()):
            for y in range(image.height()):
                pixel_color = QColor(image.pixel(x, y))
                # checks if the pixel matches the gray color within the tolerance
                if (abs(pixel_color.red() - gray_color.red()) <= tolerance and
                    abs(pixel_color.green() - gray_color.green()) <= tolerance and
                    abs(pixel_color.blue() - gray_color.blue()) <= tolerance):
                    image.setPixelColor(x, y, target_color)

        return image


        
app = QApplication(sys.argv)
window = TestApp()
window.show()
sys.exit(app.exec())
