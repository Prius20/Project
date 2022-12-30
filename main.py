import sys
import sqlite3
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QPushButton, QTableWidget, \
    QWidget,QFormLayout, QLineEdit, QDialogButtonBox, QDialog, QHeaderView, QMainWindow,\
    QGridLayout, QMessageBox, QLabel, QComboBox, QListWidget
from PIL import Image


fname = "data/books"
con = sqlite3.connect(fname)
size = width, height = 800, 700


def img_resize(fname):
    img = Image.open("data/cover/" + fname)
    img = img.resize((200, 300))
    new = "data/cover/" + 'current.jpg'
    img.save(new)
    return new

def load_text(fname):
    try:
        f = open("data/anons/" + fname, encoding="utf-8")
        text = f.read()
    except:
        text = "Описание"
    return text

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tags = ['', 'Название','Автор',
            'Год','Жанр','Тэги']
        self.total = 0
        self.setGeometry(50, 50, width, height)
        self.setWindowTitle('Моя библиотека')
        self.main = QWidget(self)
        self.setCentralWidget(self.main)
        self.grid = QGridLayout(self)
        self.main.setLayout(self.grid)
        self.comboBox = QComboBox(self)
        self.comboBox.addItems([x for x in self.tags])
        self.grid.addWidget(self.comboBox, 0, 0)
        self.edit = QLineEdit(self)
        self.grid.addWidget(self.edit, 0, 1)
        self.btn = QPushButton(self)
        self.btn.setText('Поиск')
        self.filter = self.comboBox.currentText()
        self.btn.clicked.connect(self.search)
        self.grid.addWidget(self.btn, 0, 2)
        self.setLayout(self.grid)
        #
        img = img_resize("1.jpg")
        self.pixmap = QPixmap(img)
        self.image = QLabel(self)
        self.image.setPixmap(self.pixmap)
        self.grid.addWidget(self.image, 1, 0, 3, 1)
        #
        self.font = QFont()  # создаём объект шрифта
        self.font.setPointSize(10)  # размер шрифта
        self.anons = QLabel(self)
        self.anons.setWordWrap(True)
        text = load_text("1.txt")
        self.anons.setText(text)
        self.grid.addWidget(self.anons, 3, 1, 1, 2)
        #
        self.title = QLabel(self)
        self.grid.addWidget(self.title, 1, 1, 1, 2)
        self.title.setFont(self.font)  # задаём шрифт метке
        self.author = QLabel(self)
        self.grid.addWidget(self.author, 2, 1, 1, 2)
        self.author.setFont(self.font)  # задаём шрифт метке
        self.search()
        #
        self.status = QLabel(self)
        self.grid.addWidget(self.status, 4, 0, 1, 3)
        self.status.setFont(self.font)  # задаём шрифт метке
        #
        self.table = QTableWidget(self)
        self.grid.addWidget(self.table, 5, 0, 1, 3)
        self.load_form()
        self.status.setText("Найдено записей: " + str(self.total))

    def search(self):
        text_search = self.edit.text()
        cur = con.cursor()
        if self.comboBox.currentText() == "":
            query = """SELECT   books.title, 
                                authors.name FROM books
                        INNER JOIN authors ON
                        books.author = authors.id     
                        ORDER BY books.id
                        LIMIT 1"""
            result = cur.execute(query).fetchall()[0]
            self.title.setText(str(result[0]))
            self.author.setText(str(result[1]))
        # поиск по названию
        elif self.comboBox.currentText() == "Название":
            cur = con.cursor()
            query = f"""SELECT books.id, books.title, 
                                authors.name FROM books
                        INNER JOIN authors ON
                        books.author = authors.id
                        WHERE  books.title LIKE '%{text_search}%'    
                        ORDER BY books.id
                        LIMIT 5"""
            result = cur.execute(query).fetchall()
            self.total = len(result)
            self.status.setText("Найдено записей: " + str(self.total))
            if len(result) != 0:
                result = result[0]
                self.title.setText(str(result[1]))
                self.author.setText(str(result[2]))
                img = img_resize(str(result[0]) + ".jpg")
                self.pixmap = QPixmap(img)
                self.image.setPixmap(self.pixmap)
                text = load_text(str(result[0]) + ".txt")
                self.anons.setText(text)
        elif self.comboBox.currentText() == "Автор":
            cur = con.cursor()
            query = f"""SELECT books.id, books.title, 
                                authors.name FROM books
                        INNER JOIN authors ON
                        books.author = authors.id
                        WHERE  authors.name LIKE '%{text_search}%'    
                        ORDER BY books.id
                        LIMIT 5"""
            result = cur.execute(query).fetchall()
            self.total = len(result)
            self.status.setText("Найдено записей: " + str(self.total))
            if len(result) != 0:
                result = result[0]
                self.title.setText(str(result[1]))
                self.author.setText(str(result[2]))
                img = img_resize(str(result[0]) + ".jpg")
                self.pixmap = QPixmap(img)
                self.image.setPixmap(self.pixmap)
                text = load_text(str(result[0]) + ".txt")
                self.anons.setText(text)

    def load_form(self):
        cur = con.cursor()
        query = """SELECT books.title AS Название,
                authors.name AS Автор,
                generes.name AS Жанр
                FROM books INNER JOIN generes ON
                books.genre = generes.id
                INNER JOIN authors ON
                books.author = authors.id
                """
        result = cur.execute(query).fetchall()
        col_width = (width - 40) // 3
        cols_names =['Название', 'Автор', 'Жанр']
        self.table.verticalHeader().setDefaultSectionSize(20)
        self.table.horizontalHeader().setDefaultSectionSize(col_width)
        self.table.setHorizontalHeaderLabels(cols_names)
        #
        style = '''
                QTableWidget::item {
                border-style: outset;
                border-width: 1px;
                text-align: center;}
                QTableWidget::item:selected {color:white; background-color: rgb(255, 90, 90)}
                '''
        style_head = '''
                ::section {background-color: rgb(192, 192, 192); font-weight: bold;
                border-style: outset;
                border-width: 1px;
                border-color: rgb(34, 34, 34);
                text-aligin: center;}
                '''
        # self.setStyleSheet(style)
        self.table.horizontalHeader().setStyleSheet(style_head)
        self.total = len(result)
        print(self.total)
        for i in result:
            print(i)
            self.table.setColumnCount(len(result[0]))
        self.table.setRowCount(len(result))
        self.table.setHorizontalHeaderLabels([description[0] for description in cur.description])
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())