import sys
import os
import shutil
import time
import subprocess
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QScrollArea,
    QHeaderView,
    QMessageBox,
)
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt

# Constants
CHANNELS_DIR = Path(r"D:\2025\Projects\Presence\Presence0.1\Channels")

# Uploader paths and commands
YOUTUBE_UPLOADER = r"D:\2025\Projects\Presence\Presence0.1\Uploader\Platforms\Youtube\Uploader_Youtube\Code\Uploader_YouTube.py"
TIKTOK_UPLOADER = r"D:\2025\Projects\Presence\Presence0.1\Uploader\Platforms\Tiktok\Uploader_Tiktok\Code\Uploader_TikTok.py"
INSTAGRAM_UPLOADER = r"D:\2025\Projects\Presence\Presence0.1\Uploader\Platforms\Instagram\Uploader_Instagram\Code\Uploader_Instagram.py"

YOUTUBE_OPEN_DIR = r"D:\2025\Projects\Presence\Presence0.1\Uploader\Platforms\Youtube\Uploader_Youtube\Code"
TIKTOK_OPEN_DIR = r"D:\2025\Projects\Presence\Presence0.1\Uploader\Platforms\Tiktok\Uploader_Tiktok\Code"
INSTAGRAM_OPEN_DIR = r"D:\2025\Projects\Presence\Presence0.1\Uploader\Platforms\Instagram\Uploader_Instagram\Code"

ALL_EXECUTER_BAT = r"D:\2025\Projects\Presence\Presence0.1\Uploader\Executers\All_Uploader_Executer\All_Uploader_Executer.bat"
ALL_EXECUTER_DIR = r"D:\2025\Projects\Presence\Presence0.1\Uploader\Executers\All_Uploader_Executer"

# Style for the "Open" buttons (blue with hover).
OPEN_BTN_STYLE = """
QPushButton {
    background-color: #87CEFA;
}
QPushButton:hover {
    background-color: #00BFFF;
}
"""

# Style for the green upload buttons with hover.
# Disabled state is lighter gray to resemble a system default button.
UPLOAD_BTN_STYLE = """
QPushButton {
    background-color: #32CD32;  /* LimeGreen when enabled */
}
QPushButton:hover:enabled {
    background-color: #228B22; /* ForestGreen on hover */
}
QPushButton:disabled {
    background-color: #d4d4d4; /* Lighter gray to mimic default system button */
    color: #808080;
}
"""

class UploaderManagerWidget(QWidget):
    """
    Uploader Manager:
      - Left pane: List of channels (plus an "EXECUTERS" option, styled bold blue).
      - Right pane:
         • When a channel is selected, shows the channel title with its logo (if available)
           and a clips table (populated from <channel>/Clips) with three upload buttons (YouTube, TikTok, Instagram)
           plus their corresponding "Open" buttons (blue with hover).
         • When no channel is selected or "EXECUTERS" is selected, a homepage is shown with "EXECUTERS"
           and a button "All Uploader Executer" (green with hover), plus its "Open" button.
      - Clicking outside the clips table or buttons clears the table selection.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_channel = None  # Path object or None
        self.selected_clip = None    # Full path to selected clip folder

        # We'll keep references to the table and buttons so we know when NOT to clear selection.
        self.clips_table = None
        self.btn_upload_yt = None
        self.btn_upload_tt = None
        self.btn_upload_ig = None
        self.btn_open_yt = None
        self.btn_open_tt = None
        self.btn_open_ig = None

        self.setup_ui()
        self.load_channel_list()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        # We enable mouse tracking so we can catch clicks in mousePressEvent.
        self.setMouseTracking(True)

        # Left pane: Channel menu (plus EXECUTERS option)
        self.channel_list = QListWidget()
        self.channel_list.setMaximumWidth(200)
        self.channel_list.itemClicked.connect(self.on_channel_selected)
        main_layout.addWidget(self.channel_list, 1)

        # Right pane: Details in scroll area with margins
        self.detail_widget = QWidget()
        detail_layout = QVBoxLayout(self.detail_widget)
        detail_layout.setContentsMargins(50, 20, 50, 20)
        detail_layout.setAlignment(Qt.AlignTop)

        # Top area: Title and optional logo (for channel view)
        top_layout = QHBoxLayout()
        self.title_label = QLabel("EXECUTERS")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(self.title_label, 1, Qt.AlignLeft)
        # Logo label: fixed to 128x128 px.
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(128, 128)
        self.logo_label.setScaledContents(True)
        top_layout.addWidget(self.logo_label, 0, Qt.AlignRight)
        detail_layout.addLayout(top_layout)

        # Content area for the rest of the details.
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        detail_layout.addWidget(self.content_widget)

        # Embed detail_widget in a scroll area.
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.detail_widget)
        main_layout.addWidget(scroll_area, 2)

        # Initially, show homepage (EXECUTERS)
        self.show_homepage()

    def mousePressEvent(self, event):
        """
        Override to clear table selection if the user clicks outside the table and the buttons.
        """
        if self.clips_table:
            # childAt uses local coordinates of the widget
            child = self.childAt(event.pos())

            # If the child is none of the relevant table/buttons, clear selection
            safe_widgets = {
                self.clips_table,
                self.btn_upload_yt,
                self.btn_upload_tt,
                self.btn_upload_ig,
                self.btn_open_yt,
                self.btn_open_tt,
                self.btn_open_ig
            }

            if child not in safe_widgets:
                self.clips_table.clearSelection()

        super().mousePressEvent(event)

    def clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Reset references so we don't incorrectly skip clearing selection
        self.clips_table = None
        self.btn_upload_yt = None
        self.btn_upload_tt = None
        self.btn_upload_ig = None
        self.btn_open_yt = None
        self.btn_open_tt = None
        self.btn_open_ig = None

    def load_channel_list(self):
        """Load channels from CHANNELS_DIR and add an 'EXECUTERS' option at the top."""
        self.channel_list.clear()
        # Add a "EXECUTERS" option first.
        exec_item = QListWidgetItem("EXECUTERS")
        # Style it bold and blue.
        font = exec_item.font()
        font.setBold(True)
        exec_item.setFont(font)
        exec_item.setForeground(QColor("blue"))
        self.channel_list.addItem(exec_item)

        if not CHANNELS_DIR.exists():
            QMessageBox.critical(self, "Error", f"Channels directory not found:\n{CHANNELS_DIR}")
            return

        for entry in CHANNELS_DIR.iterdir():
            if entry.is_dir() and not entry.name.endswith("(not in use)"):
                item = QListWidgetItem(entry.name)
                self.channel_list.addItem(item)

    def on_channel_selected(self, item: QListWidgetItem):
        text = item.text()
        if text == "EXECUTERS":
            self.current_channel = None
            self.logo_label.clear()
            self.show_homepage()
        else:
            self.current_channel = CHANNELS_DIR / text
            self.show_channel_details(text)

    def show_homepage(self):
        """Homepage view when no channel is selected."""
        self.clear_content()
        self.title_label.setText("EXECUTERS")

        # "All Uploader Executer" button (green style)
        executer_btn = QPushButton("All Uploader Executer")
        executer_btn.setStyleSheet(UPLOAD_BTN_STYLE)
        executer_btn.clicked.connect(lambda: self.run_process(ALL_EXECUTER_BAT))
        self.content_layout.addWidget(executer_btn)

        # Open folder button (blue with hover)
        open_btn = QPushButton("Open 'All Uploader Executer' Directory")
        open_btn.setStyleSheet(OPEN_BTN_STYLE)
        open_btn.clicked.connect(lambda: self.open_directory(ALL_EXECUTER_DIR))
        self.content_layout.addWidget(open_btn)

    def show_channel_details(self, channel_name: str):
        """Show details for the given channel."""
        self.clear_content()
        self.title_label.setText(f"Channel: {channel_name}")

        # Load logo image from Resources\Logo (max 128x128).
        logo_dir = self.current_channel / "Resources" / "Logo"
        logo_loaded = False
        if logo_dir.exists() and logo_dir.is_dir():
            for ext in ["*.png", "*.jpg", "*.jpeg"]:
                files = list(logo_dir.glob(ext))
                if files:
                    pixmap = QPixmap(str(files[0]))
                    if not pixmap.isNull():
                        self.logo_label.setPixmap(pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                        logo_loaded = True
                        break
        if not logo_loaded:
            self.logo_label.clear()

        self.content_layout.addSpacing(-150)  # 5px below the "Clips" label

        # Setup Clips table view
        clips_dir = self.current_channel / "Clips"
        clips_dir.mkdir(parents=True, exist_ok=True)
        archive_dir = self.current_channel / "Clips_Archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        self.channel_clips_dir = clips_dir
        self.channel_archive_dir = archive_dir

        # "Clips" title, then table 5px below
        clips_title = QLabel("Clips")
        clips_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.content_layout.addWidget(clips_title)

        self.content_layout.addSpacing(-200)

        self.clips_table = QTableWidget()
        self.clips_table.setColumnCount(2)
        self.clips_table.setHorizontalHeaderLabels(["Folder Name", "Creation Date"])
        self.clips_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.clips_table.setSelectionMode(QTableWidget.SingleSelection)
        self.clips_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.load_clips_table()
        self.content_layout.addWidget(self.clips_table)

        # Update selected clip when table selection changes
        self.clips_table.itemSelectionChanged.connect(self.on_clip_selection_changed)

        # Uploader buttons for YouTube, TikTok, Instagram
        # Keep them close to the table, so minimal spacing
        self.content_layout.addSpacing(2)

        # --- YouTube ---
        yt_layout = QHBoxLayout()
        self.btn_upload_yt = QPushButton("Upload to YouTube")
        self.btn_upload_yt.setStyleSheet(UPLOAD_BTN_STYLE)
        self.btn_upload_yt.clicked.connect(lambda: self.upload_clip("Youtube"))
        self.btn_upload_yt.setEnabled(False)
        yt_layout.addWidget(self.btn_upload_yt)

        self.btn_open_yt = QPushButton("Open 'Upload to YouTube' Directory")
        self.btn_open_yt.setStyleSheet(OPEN_BTN_STYLE)
        self.btn_open_yt.clicked.connect(lambda: self.open_directory(YOUTUBE_OPEN_DIR))
        yt_layout.addWidget(self.btn_open_yt)
        self.content_layout.addLayout(yt_layout)

        # --- TikTok ---
        tt_layout = QHBoxLayout()
        self.btn_upload_tt = QPushButton("Upload to TikTok")
        self.btn_upload_tt.setStyleSheet(UPLOAD_BTN_STYLE)
        self.btn_upload_tt.clicked.connect(lambda: self.upload_clip("Tiktok"))
        self.btn_upload_tt.setEnabled(False)
        tt_layout.addWidget(self.btn_upload_tt)

        self.btn_open_tt = QPushButton("Open 'Upload to TikTok' Directory")
        self.btn_open_tt.setStyleSheet(OPEN_BTN_STYLE)
        self.btn_open_tt.clicked.connect(lambda: self.open_directory(TIKTOK_OPEN_DIR))
        tt_layout.addWidget(self.btn_open_tt)
        self.content_layout.addLayout(tt_layout)

        # --- Instagram ---
        ig_layout = QHBoxLayout()
        self.btn_upload_ig = QPushButton("Upload to Instagram")
        self.btn_upload_ig.setStyleSheet(UPLOAD_BTN_STYLE)
        self.btn_upload_ig.clicked.connect(lambda: self.upload_clip("Instagram"))
        self.btn_upload_ig.setEnabled(False)
        ig_layout.addWidget(self.btn_upload_ig)

        self.btn_open_ig = QPushButton("Open 'Upload to Instagram' Directory")
        self.btn_open_ig.setStyleSheet(OPEN_BTN_STYLE)
        self.btn_open_ig.clicked.connect(lambda: self.open_directory(INSTAGRAM_OPEN_DIR))
        ig_layout.addWidget(self.btn_open_ig)
        self.content_layout.addLayout(ig_layout)

    def load_clips_table(self):
        """Populate the clips table with folders from the current channel's Clips directory."""
        folders = []
        for item in self.channel_clips_dir.iterdir():
            if item.is_dir():
                try:
                    ctime = item.stat().st_ctime
                except Exception:
                    ctime = 0
                folders.append((item.name, ctime, item))
        folders.sort(key=lambda x: x[1], reverse=True)
        self.clips_table.setRowCount(len(folders))
        for row, (folder_name, ctime, folder_obj) in enumerate(folders):
            name_item = QTableWidgetItem(folder_name)
            date_item = QTableWidgetItem(time.ctime(ctime))
            name_item.setFlags(name_item.flags() ^ Qt.ItemIsEditable)
            date_item.setFlags(date_item.flags() ^ Qt.ItemIsEditable)
            self.clips_table.setItem(row, 0, name_item)
            self.clips_table.setItem(row, 1, date_item)
            self.clips_table.setRowHeight(row, 25)

        header_height = self.clips_table.horizontalHeader().height()
        row_height = self.clips_table.verticalHeader().defaultSectionSize()
        self.clips_table.setFixedHeight(header_height + row_height * 5)

    def on_clip_selection_changed(self):
        selected = self.clips_table.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            folder_name = self.clips_table.item(row, 0).text()
            self.selected_clip = self.channel_clips_dir / folder_name
            self.btn_upload_yt.setEnabled(True)
            self.btn_upload_tt.setEnabled(True)
            self.btn_upload_ig.setEnabled(True)
        else:
            self.selected_clip = None
            if self.btn_upload_yt:
                self.btn_upload_yt.setEnabled(False)
            if self.btn_upload_tt:
                self.btn_upload_tt.setEnabled(False)
            if self.btn_upload_ig:
                self.btn_upload_ig.setEnabled(False)

    def upload_clip(self, platform: str):
        """Upload the selected clip using the uploader script for the given platform."""
        if self.selected_clip is None or self.current_channel is None:
            return

        channel_name = self.current_channel.name
        clip_path = str(self.selected_clip)
        if platform == "Youtube":
            uploader_script = YOUTUBE_UPLOADER
        elif platform == "Tiktok":
            uploader_script = TIKTOK_UPLOADER
        elif platform == "Instagram":
            uploader_script = INSTAGRAM_UPLOADER
        else:
            return

        try:
            subprocess.run([sys.executable, uploader_script, channel_name, clip_path], check=True)
            QMessageBox.information(self, "Upload", f"{platform} upload completed.")
            dest = self.channel_archive_dir / self.selected_clip.name
            shutil.move(clip_path, str(dest))
            self.load_clips_table()
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Upload Error", f"Error uploading to {platform}:\n{e}")

    def run_process(self, process_path: str):
        """Run an external process (bat file, etc.)."""
        try:
            subprocess.run(process_path, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Error running process:\n{e}")

    def open_directory(self, directory: str):
        """Open a directory in Windows Explorer."""
        try:
            os.startfile(directory)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open directory:\n{e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Presence Manager - Uploader")
        self.resize(900, 700)
        self.uploader_manager = UploaderManagerWidget()
        self.setCentralWidget(self.uploader_manager)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
