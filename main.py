import sys
import validators
from urllib.parse import urlparse

from PyQt6.QtWidgets import QGridLayout, QWidget, QApplication, QTextEdit, QPushButton, QMessageBox
from PyQt6 import QtCore
from PyQt6.QtGui import QCursor

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 400
YOUTUBE_DOMAINS = ["www.youtube.com"]
REDDIT_DOMAINS = ["www.reddit.com"]

class UVDWindow(QWidget):
    application = None
    linkTextField = None

    def __init__(self, qApp):
        super(UVDWindow, self).__init__()
        self.application = qApp
        self.initializeUI()

    def initializeUI(self):
        # Set size/center on screen
        screenGeometry = app.primaryScreen().geometry()
        self.move(int(screenGeometry.width() / 2 - WINDOW_WIDTH / 2),
                  int(screenGeometry.height() / 2 - WINDOW_HEIGHT / 2))
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Set style
        self.setWindowTitle("Universal Video Downloader")
        self.setStyleSheet("background: #161219;")

        # Grid
        grid = QGridLayout()
        self.setLayout(grid)

        # Make text field
        textField = QTextEdit()
        textField.acceptRichText = False
        textField.placeholderText = "Enter Link Here"
        textField.setStyleSheet("font-size: 16px; color: white;")
        grid.addWidget(textField)
        self.linkTextField = textField

        # Make button
        button = QPushButton("Validate Link")
        button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        button.setStyleSheet(
            "border: 4px solid '#BC006C'; font-size: 30px; color: white; padding: 15px 0;")
        button.clicked.connect(self.validateLink)
        grid.addWidget(button)

    def validateLink(self):
        # Get Link
        link = self.linkTextField.toPlainText().strip(' \n')

        # Filter nonsensical links
        if not validators.url(link):
            QMessageBox.critical(None, "Universal Video Downloader", "Link destination could not be found.")
            return

        # todo: Perform different tasks per domain type
        domain = urlparse(link).netloc
        if domain in YOUTUBE_DOMAINS:
            print("Found youtube link!")
        elif domain in REDDIT_DOMAINS:
            print("Found reddit link!")
        else:
            print("Found invalid link.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = UVDWindow(app)
    win.show()
    sys.exit(app.exec())
