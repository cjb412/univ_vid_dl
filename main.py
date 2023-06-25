import sys
import validators
from urllib.parse import urlparse
from yt_dlp import YoutubeDL

from PyQt6.QtWidgets import QGridLayout, QWidget, QApplication, QLineEdit, QPushButton, QMessageBox
from PyQt6 import QtCore
from PyQt6.QtGui import QCursor

SAVE_PATH = "E:/"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 400
YOUTUBE_DOMAINS = ["www.youtube.com"]
REDDIT_DOMAINS = ["www.reddit.com"]


class UVDWindow(QWidget):
    application = None
    linkTextField = None
    downloadButton = None

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
        self.linkTextField = QLineEdit()
        grid.addWidget(self.linkTextField)
        # Text field setup
        self.linkTextField.textChanged.connect(self.OnTextFieldChanged)
        # self.linkTextField.acceptRichText = False
        # self.linkTextField.placeholderText = "Enter Link Here"
        self.linkTextField.setStyleSheet("font-size: 16px; color: white;")

        # Make button
        self.downloadButton = QPushButton("Validate Link")
        grid.addWidget(self.downloadButton)
        # Button setup
        self.downloadButton.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.downloadButton.setStyleSheet("border: 4px solid '#BC006C'; " +
                                          "font-size: 30px; color: white; padding: 15px 0;")

    def OnTextFieldChanged(self):
        # Get Link
        link = self.linkTextField.text().strip(' \n')
        domain = ResolveLinkDomain(link)
        if domain is None:
            self.DisableButton()
        elif domain in YOUTUBE_DOMAINS:
            self.EnableButton("Download Youtube Video")
            self.SetButtonFunction(self.ResolveYoutubeLink)
        elif domain in REDDIT_DOMAINS:
            self.EnableButton("Download Reddit Video")
            self.SetButtonFunction(self.ResolveRedditLink)
        else:
            self.DisableButton()

    def SetButtonFunction(self, newFunc):
        try:
            self.downloadButton.clicked.disconnect()
        except Exception:
            pass
        self.downloadButton.clicked.connect(newFunc)

    def DisableButton(self):
        self.downloadButton.setEnabled(False)
        self.downloadButton.setText("URL Unrecognized")

    def EnableButton(self, label):
        self.downloadButton.setEnabled(True)
        self.downloadButton.setText(label)

    def ResolveYoutubeLink(self):
        print("YT")

    def ResolveRedditLink(self):
        print("R")


def ResolveLinkDomain(url):
    # Filter nonsensical links
    if url == "" or not validators.url(url):
        # QMessageBox.critical(None, "Universal Video Downloader", "Link destination could not be found.")
        return None
    domain = urlparse(url).netloc
    return domain


def DownloadYoutubeLink(url):
    print(url)
    URLS = [url]
    with YoutubeDL() as ydl:
        ydl.download(URLS)
    print('Task Completed!')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = UVDWindow(app)
    win.show()
    sys.exit(app.exec())
