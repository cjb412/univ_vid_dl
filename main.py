import sys
import os
import math
import json
# Webp conversion
from webptools import dwebp
# URL Parsing
from urllib.parse import urlparse
import validators
# App UI
from PyQt6.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout, QLayout
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QFileDialog, QLabel
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QCursor, QPixmap
from yt_dlp import YoutubeDL

DEFAULT_SAVE_PATH = "E:/"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 400
YOUTUBE_DOMAINS = ["www.youtube.com"]
REDDIT_DOMAINS = ["www.reddit.com"]

LINK_FIELD_STYLE = "font-size: 20px;" \
                   "color: white;" \
                   "border-radius: 10px;" \
                   "border: 2px solid white;" \
                   "padding: 5px 10px;" \
                   "margin: 0px 5px;"
FILE_SELECT_STYLE = "border: none; font-size: 16px; color: #bf77be;"
BUTTON_ENABLED_STYLE = "border: 4px solid '#BC006C'; font-size: 15px; color: white; padding: 12px 12px;"
BUTTON_DISABLED_STYLE = "border: 4px solid '#BC006C'; font-size: 15px; color: gray; padding: 12px 12px;"
ERROR_STYLE = "font-size: 20px; color: red; align: center;"
SETTINGS_BACK_STYLE = "background-color: white;"
VIDEO_TITLE_STYLE = "font-weight: bold; text-align: center; margin: 0px;"
VIDEO_DURATION_STYLE = "text-align: center;"


class UVDWindow(QWidget):
    application = None
    mainVLayout = None

    searchBoxVLayout = None
    searchBoxHLayout = None
    linkTextField = None
    downloadButton = None
    folderSelectButton = None

    downloadSettingsLayout = None
    settingsBackground = None

    save_path = DEFAULT_SAVE_PATH

    def __init__(self, qApp):
        super(UVDWindow, self).__init__()
        self.application = qApp

        self.initializeWindow()
        self.initializeSearchArea()

        self.downloadSettingsLayout = QHBoxLayout()
        self.mainVLayout.addLayout(self.downloadSettingsLayout)

    def initializeWindow(self):
        # Set size/center on screen
        screenGeometry = app.primaryScreen().geometry()
        self.move(int(screenGeometry.width() / 2 - WINDOW_WIDTH / 2),
                  int(screenGeometry.height() / 2 - WINDOW_HEIGHT / 2))
        # self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Set style
        self.setWindowTitle("Universal Video Downloader")
        self.setStyleSheet("background: #161219;")

        # Grid
        self.mainVLayout = QVBoxLayout()
        self.setLayout(self.mainVLayout)

    def initializeSearchArea(self):
        # Make horizontal box for text field and button
        self.searchBoxHLayout = QHBoxLayout()

        subHBox = QHBoxLayout()
        # Make text field
        self.linkTextField = QLineEdit()
        subHBox.addWidget(self.linkTextField)
        self.linkTextField.setPlaceholderText("Enter Target URL Here")
        self.linkTextField.textChanged.connect(self.OnTextFieldChanged)
        self.linkTextField.setStyleSheet(LINK_FIELD_STYLE)
        # Make button
        self.downloadButton = QPushButton("Go")
        subHBox.addWidget(self.downloadButton)
        self.downloadButton.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.SetGoButtonEnabled(False)
        self.downloadButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)

        # Make left stretch space
        self.searchBoxHLayout.insertStretch(0, 1)
        self.searchBoxHLayout.addLayout(subHBox)
        self.searchBoxHLayout.setStretch(1, 5)
        self.searchBoxHLayout.insertStretch(2, 1)

        # Make vertical box for horizontal box and directory selector
        self.searchBoxVLayout = QVBoxLayout()

        # Make directory selector
        self.folderSelectButton = QPushButton(f"Current Directory: {self.save_path}")
        self.folderSelectButton.clicked.connect(self.OpenFileMenu)
        self.folderSelectButton.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.folderSelectButton.setStyleSheet(FILE_SELECT_STYLE)

        # Nest searchbar/button in vertical search layout.
        self.searchBoxVLayout.addLayout(self.searchBoxHLayout)
        # Nest directory selector in vertical search layout.
        self.searchBoxVLayout.addWidget(self.folderSelectButton)
        # Nest vertical search layout in main vertical layout.
        self.mainVLayout.addLayout(self.searchBoxVLayout)

    def OnTextFieldChanged(self):
        # Get Link
        link = self.linkTextField.text().strip(' \n')
        domain = ResolveLinkDomain(link)
        if domain is not None:
            self.SetGoButtonEnabled(True)
            try:
                self.downloadButton.clicked.disconnect()
            except Exception:
                pass
            self.downloadButton.clicked.connect(self.OnGoClicked)
        else:
            self.SetGoButtonEnabled(False)

    def OpenFileMenu(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file:
            self.save_path = file
            self.folderSelectButton.setText(f"Current Directory: {self.save_path}")

    def SetGoButtonEnabled(self, enabled):
        if enabled:
            self.downloadButton.setEnabled(True)
            self.downloadButton.setText("Go")
            self.downloadButton.setStyleSheet(BUTTON_ENABLED_STYLE)
        else:
            self.downloadButton.setEnabled(False)
            self.downloadButton.setText("Go")
            self.downloadButton.setStyleSheet(BUTTON_DISABLED_STYLE)

    def OnGoClicked(self):
        link = self.linkTextField.text().strip(' \n')
        domain = ResolveLinkDomain(link)
        self.RefreshDownloadSettingsPanel()
        self.application.processEvents()
        self.ShowYoutubeDownloadInfo()

    def RefreshDownloadSettingsPanel(self):
        clearLayout(self.downloadSettingsLayout)

        # add colored background
        self.settingsBackground = QWidget()
        self.settingsBackground.setStyleSheet(SETTINGS_BACK_STYLE)
        self.downloadSettingsLayout.addWidget(self.settingsBackground)

    def ShowYoutubeDownloadInfo(self):
        # On left side, thumbnail, title, uploader, duration

        ytSettingsContainer = QHBoxLayout()
        self.settingsBackground.setLayout(ytSettingsContainer)
        ytSettingsLeftSide = QVBoxLayout()
        ytSettingsRightSide = QVBoxLayout()
        ytSettingsContainer.addLayout(ytSettingsLeftSide)
        ytSettingsContainer.addLayout(ytSettingsRightSide)
        ytSettingsContainer.setStretch(0, 2)
        ytSettingsContainer.setStretch(1, 6)

        info = RetrieveYoutubeDisplayInfo(self.linkTextField.text().strip(' \n'))
        if info is None:
            errorLabel = QLabel("There was an error retrieving the requested media.")
            errorLabel.setStyleSheet(ERROR_STYLE)
            ytSettingsLeftSide.addWidget(errorLabel)
            return

        # Left side widgets
        image = QPixmap("./thumbnail.png")
        imageLabel = QLabel()
        imageLabel.setPixmap(image.scaled(225, 125, QtCore.Qt.AspectRatioMode.IgnoreAspectRatio))

        title = QLabel(info[0])
        title.setStyleSheet(VIDEO_TITLE_STYLE)
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        uploader = QLabel(f"Uploaded by: {str(info[1])}")
        uploader.setStyleSheet(VIDEO_DURATION_STYLE)
        uploader.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        duration = QLabel(f"Duration: {math.floor((info[2] / 60.0))}:{(info[2] % 60)}")
        duration.setStyleSheet(VIDEO_DURATION_STYLE)
        duration.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        ytSettingsLeftSide.addWidget(imageLabel)
        ytSettingsLeftSide.addWidget(title)
        ytSettingsLeftSide.addWidget(uploader)
        ytSettingsLeftSide.addWidget(duration)

        title2 = QLabel(info[0])
        title2.setStyleSheet(VIDEO_TITLE_STYLE)
        title2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        ytSettingsRightSide.addWidget(title2)


def ResolveLinkDomain(url):
    # Filter nonsensical links
    if url == "" or not validators.url(url):
        # QMessageBox.critical(None, "Universal Video Downloader", "Link destination could not be found.")
        return None
    domain = urlparse(url).netloc
    return domain


def clearLayout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clearLayout(item.layout())


def RetrieveYoutubeDisplayInfo(url):
    ydl_opts = \
        {
            'writethumbnail': True,
            'embedthumbnail': True,
            'skip_download': True,
            'outtmpl': 'thumbnail.%(ext)s'
        }
    try:
        info = None
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)

        # Thumbnail
        if (os.path.isfile("./thumbnail.webp")):
            print(dwebp("thumbnail.webp", "thumbnail.png", "-o"))
            os.remove("./thumbnail.webp")

        # Title
        title = info.get("title")
        uploader = info.get("channel")
        duration = info.get("duration")
        return [title, uploader, duration]
    except:
        return None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = UVDWindow(app)
    win.show()
    sys.exit(app.exec())
