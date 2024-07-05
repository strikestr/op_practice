import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QInputDialog,
    QFileDialog,
    QMessageBox,
    QWidget,
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class ImageProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.image = None

    def initUI(self):
        self.setWindowTitle("Image Processor")

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)

        self.uploadButton = QPushButton("Загрузить изображение")
        self.uploadButton.clicked.connect(self.uploadImage)

        self.cameraButton = QPushButton("Захват камеры")
        self.cameraButton.clicked.connect(self.captureFromWebcam)

        self.gaussianBlurButton = QPushButton("Применить размытие по Гауссу")
        self.gaussianBlurButton.clicked.connect(self.applyGaussianBlur)

        self.grayScaleButton = QPushButton("Изображение в оттенках серого")
        self.grayScaleButton.clicked.connect(self.convertToGrayscale)

        self.drawLineButton = QPushButton("Нарисовать линию")
        self.drawLineButton.clicked.connect(self.drawLine)

        self.channelButton = QPushButton("Показать канал")
        self.channelButton.clicked.connect(self.showChannel)

        layout = QVBoxLayout()
        layout.addWidget(self.uploadButton)
        layout.addWidget(self.cameraButton)
        layout.addWidget(self.gaussianBlurButton)
        layout.addWidget(self.grayScaleButton)
        layout.addWidget(self.drawLineButton)
        layout.addWidget(self.channelButton)
        layout.addWidget(self.label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def uploadImage(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Открыть изображение", "", "(*.png *.jpg)", options=options
        )
        if fileName:
            self.image = cv2.imread(fileName)
            self.displayImage()

    def captureFromWebcam(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.showErrorMessage("Не удалось подключиться к камере.")
            return

        cv2.namedWindow("SPACE to Capture", cv2.WINDOW_NORMAL)

        while True:
            ret, frame = cap.read()
            if not ret:
                self.showErrorMessage("Ошибка загрузки фото с камеры.")
                break

            cv2.imshow("SPACE to Capture", frame)

            key = cv2.waitKey(1)
            if key == 32:
                self.image = frame
                self.original_image = self.image.copy()
                self.displayImage(self.image)
                break
            elif key == 27:
                break

        cap.release()
        cv2.destroyWindow("SPACE to Capture")

    def applyGaussianBlur(self):
        if self.image is not None:
            kernelSize, ok = QInputDialog.getInt(
                self, "Размытие по гауссу", "Введите нечетное число:", min=1, step=2
            )
            if int(kernelSize) % 2 != 0:
                if ok:
                    self.image = cv2.GaussianBlur(
                        self.image, (kernelSize, kernelSize), 0
                    )
                    self.displayImage()
            else:
                self.showErrorMessage("Неверные данные")
                return

    def convertToGrayscale(self):
        if self.image is not None:
            if len(self.image.shape) == 2:
                self.showErrorMessage("Изображение уже серое")
                return
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            self.displayImage()

    def drawLine(self):
        if self.image is not None:
            x1, ok1 = QInputDialog.getInt(self, "Нарисовать линию", "x1:")
            y1, ok2 = QInputDialog.getInt(self, "Нарисовать линию", "y1:")
            x2, ok3 = QInputDialog.getInt(self, "Нарисовать линию", "x2:")
            y2, ok4 = QInputDialog.getInt(self, "Нарисовать линию", "y2:")
            thickness, ok5 = QInputDialog.getInt(self, "Draw Line", "Толщина:")
            try:
                if ok1 and ok2 and ok3 and ok4 and ok5:
                    cv2.line(self.image, (x1, y1), (x2, y2), (0, 255, 0), thickness)
                    self.displayImage()
            except:
                self.showErrorMessage("Неверные данные")
                return

    def showChannel(self):
        if self.image is not None:
            if len(self.image.shape) == 2:
                self.showErrorMessage("Изображение уже серое")
                return

            channel, ok = QInputDialog.getItem(
                self,
                "Показать канал",
                "Выберите канал:",
                ["Красный", "Зеленый", "Синий"],
                0,
                False,
            )
            if ok:
                if channel == "Красный":
                    channel_image = self.image[:, :, 2]
                elif channel == "Зеленый":
                    channel_image = self.image[:, :, 1]
                else:
                    channel_image = self.image[:, :, 0]

                height, width = channel_image.shape
                bytesPerLine = width
                qImg = QImage(
                    channel_image.tobytes(),
                    width,
                    height,
                    bytesPerLine,
                    QImage.Format_Grayscale8,
                )
                pixmap = QPixmap.fromImage(qImg)
                self.label.setPixmap(pixmap)
                self.resize(pixmap.width(), pixmap.height())

    def displayImage(self, img=None):
        if img is None:
            img = self.image

        if len(img.shape) == 2:
            qImg = QImage(
                img.data,
                img.shape[1],
                img.shape[0],
                img.strides[0],
                QImage.Format_Grayscale8,
            )
        else:
            rgbImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            qImg = QImage(
                rgbImage.data,
                rgbImage.shape[1],
                rgbImage.shape[0],
                rgbImage.strides[0],
                QImage.Format_RGB888,
            )
        pixmap = QPixmap.fromImage(qImg)
        self.label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

    def showErrorMessage(self, message):
        QMessageBox.critical(self, "Error", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    processor = ImageProcessor()
    processor.show()
    sys.exit(app.exec_())
