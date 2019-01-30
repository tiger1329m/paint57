from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QAction, QFileDialog, QInputDialog, QColorDialog, QFontDialog
from PyQt5.QtGui import QIcon, QImage, QPainter, QPen, QPolygon, QColor
from PyQt5.QtCore import Qt, QPoint, QRect
import sys
from PIL import ImageDraw, Image
from sys import setrecursionlimit

setrecursionlimit(999999999)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        top = 300  # задаём размеры окна
        left = 300
        w = 800
        h = 600

        self.r = QRect(0, 5, w, h - 5)
        self.p2 = QPoint(0, 5)  # координаты верхнего угла картинки

        self.setWindowTitle('Paint Application')
        self.setGeometry(top, left, w, h)
        self.setWindowIcon(QIcon("icons/paint.png"))

        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        self.x = 0
        self.y = 0

        self.drawing = False
        self.brushSize = 2
        self.color1 = Qt.black
        self.color2 = Qt.white
        self.pen_color = self.color1

        self.is_pen = True
        self.is_eraser = False
        self.is_zalivka = False
        self.is_line = False
        self.is_rect = False
        self.is_polygon = False
        self.is_pipette = False

        self.line_pos = []
        self.rect_pos = []
        self.polygon_pos = []
        self.polygon_n = 0

        self.lastPoint = QPoint()

        mainMenu = self.menuBar()  # кнопки для выбора цвета, размера кисти, сохранения файла
        fileMenu = mainMenu.addMenu('Файл')
        sizeMenu = mainMenu.addMenu('Размер')
        colorMenu = mainMenu.addMenu('Цвет')
        typeMenu = mainMenu.addMenu('Тип')

        save_a = QAction(QIcon('icons/save.png'), 'Сохранить', self)
        save_a.setShortcut('Ctrl+S')
        open_a = QAction(QIcon('icons/open2.png'), 'Открыть', self)
        open_a.setShortcut('Ctrl+O')
        clear_a = QAction(QIcon("icons/reload.png"), 'Очистить', self)
        clear_a.setShortcut('Ctrl+X')

        fileMenu.addAction(save_a)
        save_a.triggered.connect(self.save)
        fileMenu.addAction(open_a)
        open_a.triggered.connect(self.open)
        fileMenu.addAction(clear_a)
        clear_a.triggered.connect(self.clear)

        color_a = QAction(QIcon("icons/color.png"), 'Цвет1(основной)', self)
        color2_a = QAction(QIcon("icons/color2.png"), 'Цвет2 (фон)', self)

        colorMenu.addAction(color_a)
        color_a.triggered.connect(self.set_color)
        colorMenu.addAction(color2_a)
        color2_a.triggered.connect(self.set_color2)

        one_px = QAction(QIcon("icons/1px.png"), '1px', self)
        size_a = QAction(QIcon("icons/lines.png"), 'Любой', self)

        sizeMenu.addAction(one_px)
        one_px.triggered.connect(self.onePx)
        sizeMenu.addAction(size_a)
        size_a.triggered.connect(self.set_size)

        pen_a = QAction(QIcon('icons/pen.png'), 'Перо', self)
        eraser_a = QAction(QIcon('icons/eraser.png'), 'Ластик', self)
        zalivka_a = QAction(QIcon("icons/fill.png"), 'Заливка', self)
        pipette_a = QAction(QIcon('icons/pipette.png'), 'Пипетка', self)
        line_a = QAction(QIcon('icons/line.png'), "Прямая", self)
        rect_a = QAction(QIcon("icons/rectangle.png"), 'Прямоугольник', self)
        polygon_a = QAction(QIcon('icons/polygon.png'), "Многоугольник", self)
        none_a = QAction(QIcon("icons/nothing.png"), 'Ничего', self)

        typeMenu.addAction(pen_a)
        pen_a.triggered.connect(self.pen)
        typeMenu.addAction(eraser_a)
        eraser_a.triggered.connect(self.eraser)
        typeMenu.addAction(zalivka_a)
        zalivka_a.triggered.connect(self.zalivka)
        typeMenu.addAction(pipette_a)
        pipette_a.triggered.connect(self.pipette)
        typeMenu.addAction(line_a)
        line_a.triggered.connect(self.line)
        typeMenu.addAction(rect_a)
        rect_a.triggered.connect(self.rectangle)
        typeMenu.addAction(polygon_a)
        polygon_a.triggered.connect(self.polygon)
        typeMenu.addAction(none_a)
        none_a.triggered.connect(self.none)

    def paintEvent(self, event):
        Painter = QPainter(self)
        Painter.drawImage(self.p2, self.image)
        self.resize(self.image.width(), self.image.height())

    def mousePressEvent(self, event):  # обрабатываем клик мышки
        if event.button() == Qt.LeftButton:
            if self.is_line:
                self.line_pos.append(event.pos())
                self.draw_line()
            elif self.is_rect:
                self.rect_pos.append(event.pos())
                self.draw_rect()
            elif self.is_polygon:
                self.polygon_pos.append(event.pos())
                self.draw_polygon()
            elif self.is_pen or self.is_eraser:
                self.drawing = True
            elif self.is_pipette:
                self.x = event.x()
                self.y = event.y() - 5
                self.use_pipette(1)
            elif self.is_zalivka:
                self.x = event.x()
                self.y = event.y() - 5
                self.use_zalivka()
            self.p = event.pos()
        if event.button() == Qt.RightButton:
            self.p = event.pos()
            if self.is_pipette:
                self.x = event.x()
                self.y = event.y() - 5
                self.use_pipette(2)
            else:
                self.input_text()

    def mouseMoveEvent(self, event):  # функция рисования при перемещении мышки
        if self.is_eraser:
            self.pen_color = self.color2
        else:
            self.pen_color = self.color1
        dp = QPainter(self.image)
        dp.setRenderHint(QPainter.Antialiasing)
        dp.setPen(QPen(self.pen_color, self.brushSize, Qt.SolidLine))
        if self.drawing:
            dp.drawLine(self.p, event.pos())
            self.p = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button == Qt.LeftButton:
            self.drawing = False

    def save(self):  # функция для сохранения файла в формате PNG или jpg
        file, p = QFileDialog.getSaveFileName(self, 'Save Image', '', 'PNG (*.png);;JPEG(*.jpg)')
        if file == '':
            return
        self.image.save(file)

    def open(self):  # открытие файла в формата PNG или jpg
        img, hz = QFileDialog.getOpenFileName(self, 'Open Image', '', 'PNG (*.png);;JPEG(*.jpg)')
        try:
            s = open(img)
            self.image = QImage(img)
            if self.image.height() <= 10 or self.image.width() <= 10:
                self.clear()
        except Exception:
            pass

    def clear(self):  # очищение файла
        self.c = True
        self.image = QImage('icons/white.png')
        self.update()

    def set_color(self):  # смена цвета пера
        self.color1 = QColorDialog.getColor()

    def set_color2(self):  # смена цвета ластика
        self.color2 = QColorDialog.getColor()

    def set_size(self):  # смена размера пера
        n, hz = QInputDialog.getInt(self, 'Size of pen', 'Размер:', 1, 1, 50, 1)
        if hz:
            self.brushSize = n

    def onePx(self):  # смена размера пера на 1
        self.brushSize = 1

    def input_text(self):  # рисование текста
        t, hz = QInputDialog.getText(self, 'text', 'Текст:')
        if hz:
            color_text = QColorDialog().getColor()
            f, k = QFontDialog().getFont()
            if k:
                dp = QPainter(self.image)
                dp.setRenderHint(QPainter.Antialiasing)
                dp.setPen(QPen(color_text, self.brushSize, Qt.SolidLine))
                dp.setFont(f)
                dp.drawText(self.p, t)

    def pen(self):
        self.is_pen = True
        self.is_eraser = False
        self.is_zalivka = False
        self.is_line = False
        self.is_polygon = False
        self.is_rect = False
        self.is_pipette = False
        self.pen_color = self.color1

    def none(self):
        self.is_pen = False
        self.is_eraser = False
        self.is_zalivka = False
        self.is_line = False
        self.is_polygon = False
        self.is_rect = False
        self.is_pipette = False

    def line(self):
        self.line_pos = []
        self.is_pen = False
        self.is_eraser = False
        self.is_zalivka = False
        self.is_rect = False
        self.is_polygon = False
        self.is_line = True
        self.is_pipette = False
        self.pen_color = self.color1

    def eraser(self):
        self.is_pen = False
        self.is_eraser = True
        self.is_zalivka = False
        self.is_rect = False
        self.is_line = False
        self.is_pipette = False
        self.pen_color = self.color2

    def rectangle(self):
        self.rect_pos = []
        self.is_pen = False
        self.is_eraser = False
        self.is_zalivka = False
        self.is_rect = True
        self.is_polygon = False
        self.is_line = False
        self.is_pipette = False
        self.pen_color = self.color1

    def polygon(self):
        self.polygon_pos = []
        self.is_pen = False
        self.is_eraser = False
        self.is_zalivka = False
        self.is_rect = False
        self.is_line = False
        self.is_polygon = True
        self.is_pipette = False
        self.pen_color = self.color1

    def pipette(self):
        self.is_pen = False
        self.is_eraser = False
        self.is_zalivka = False
        self.is_rect = False
        self.is_line = False
        self.is_polygon = False
        self.is_pipette = True

    def zalivka(self):
        self.is_pen = False
        self.is_eraser = False
        self.is_zalivka = True
        self.is_rect = False
        self.is_line = False
        self.is_polygon = False
        self.is_pipette = False

    def draw_line(self):  # рисование прямой
        self.pen_color = self.color1
        dp = QPainter(self.image)
        dp.setRenderHint(QPainter.Antialiasing)
        dp.setPen(QPen(self.pen_color, self.brushSize, Qt.SolidLine))
        if len(self.line_pos) == 1:
            dp.drawPoint(QPoint(self.line_pos[-1]))
        else:
            dp.drawLine(self.line_pos[-2], self.line_pos[-1])
            self.line_pos = []
        self.update()

    def draw_rect(self):  # рисование прямоугольника
        dp = QPainter(self.image)
        dp.setPen(QPen(self.pen_color, self.brushSize, Qt.SolidLine))
        self.pen_color = self.color1
        if len(self.rect_pos) == 1:
            dp.setPen(QPen(self.pen_color, self.brushSize, Qt.SolidLine))
            dp.drawPoint(QPoint(self.rect_pos[-1]))
        else:
            dp.setRenderHint(QPainter.Antialiasing)
            dp.drawRect(QRect(self.rect_pos[0], self.rect_pos[1]))
            self.rect_pos = []
        self.update()

    def draw_polygon(self):  # рисование многоугольника
        dp = QPainter(self.image)
        dp.setPen(QPen(self.pen_color, self.brushSize, Qt.SolidLine))
        if len(self.polygon_pos) == 1:
            n, hz = QInputDialog.getInt(self, 'Polygon', 'Кол-во углов:', 3, 3, 20, 1)
            if hz:
                self.polygon_n = n
            self.pen_color = self.color1
        if len(self.polygon_pos) < self.polygon_n:
            dp.drawPoint(QPoint(self.polygon_pos[-1]))
        else:
            dp.setRenderHint(QPainter.Antialiasing)
            qp = QPolygon(self.polygon_pos)
            dp.drawPolygon(qp)
            self.polygon_pos = []
        self.update()

    def use_pipette(self, but):  # пипетка
        self.is_pipette = False
        self.is_pen = True
        pix = QColor(self.image.pixel(self.x, self.y))
        if but == 1:
            self.color1 = pix
        else:
            self.color2 = pix

    def use_zalivka(self):  # заливка
        x1 = self.image.width()
        y1 = self.image.height()
        pix = self.image.pixel(self.x, self.y)
        if QColor(pix).rgb() != QColor(self.color1).rgb():
            for i in range(x1):
                for j in range(y1):
                    p2 = self.image.pixel(i, j)
                    if p2 == pix:
                        self.image.setPixel(i, j, QColor(self.color1).rgb())
        self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
