import sys
import os
import json
import shutil
import time
from pathlib import Path

from send2trash import send2trash

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
    QCheckBox,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QScrollArea,
    QHeaderView,
)
from PyQt5.QtCore import Qt

# Define the channels directory as a constant (adjust as needed)
CHANNELS_DIR = Path(r"D:\2025\Projects\Presence\Presence0.1\Channels")


class CredentialsWidget(QWidget):
    """
    A widget to display credentials.
    Credentials are masked by default (each character replaced with '*').
    A global toggle button allows you to decrypt/encrypt all credentials.
    A global copy button copies all credentials in plain text.
    """
    def __init__(self, credentials: dict, parent=None):
        super().__init__(parent)
        self.credentials = {k: str(v) for k, v in credentials.items()}  # store plain text credentials
        self.encrypted = True  # default state: encrypted (masked)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.row_labels = {}
        # Create a row for each credential: key and value.
        for key, value in self.credentials.items():
            row_layout = QHBoxLayout()
            key_label = QLabel(f"{key}:")
            key_label.setFixedWidth(120)
            row_layout.addWidget(key_label)
            value_label = QLabel(self.mask_value(value))
            row_layout.addWidget(value_label, 1)
            self.row_labels[key] = value_label
            layout.addLayout(row_layout)
        # Global buttons layout.
        buttons_layout = QHBoxLayout()
        self.toggle_button = QPushButton("Decrypt")
        self.toggle_button.clicked.connect(self.toggle_encryption)
        buttons_layout.addWidget(self.toggle_button)
        self.copy_button = QPushButton("COPY")
        self.copy_button.clicked.connect(self.copy_credentials)
        buttons_layout.addWidget(self.copy_button)
        layout.addLayout(buttons_layout)

    def mask_value(self, value: str) -> str:
        return '*' * len(value)

    def toggle_encryption(self):
        self.encrypted = not self.encrypted
        if self.encrypted:
            # Switch to masked view.
            for key, label in self.row_labels.items():
                label.setText(self.mask_value(self.credentials[key]))
            self.toggle_button.setText("Decrypt")
        else:
            # Show plain text.
            for key, label in self.row_labels.items():
                label.setText(self.credentials[key])
            self.toggle_button.setText("Encrypt")

    def copy_credentials(self):
        # Always copy plain text credentials.
        text = "\n".join(f"{k}: {v}" for k, v in self.credentials.items())
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copied", "Credentials copied.")


class ChannelManagerWidget(QWidget):
    """
    Widget to manage channels.
    Scans the CHANNELS_DIR for subfolders (excluding ones ending with '(not in use)'),
    reads each channel's media_list.txt file and displays media platforms as checkboxes.
    Also loads and displays channel credentials (with global Encrypt/Decrypt and COPY buttons),
    plus shows the Clips and Archive directories with options to delete, archive/unarchive, open folders,
    and open the directory itself.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_channel = None
        self.media_checkboxes = {}  # Mapping: platform name -> QCheckBox instance
        self.clips_dir = None
        self.archive_dir = None
        self.setup_ui()
        self.load_channels()

    def setup_ui(self):
        """Setup the main layout and widgets."""
        main_layout = QHBoxLayout(self)

        # Left side: List of channel folders.
        self.channel_list = QListWidget()
        # Make the channels menu less wide.
        self.channel_list.setMaximumWidth(200)
        self.channel_list.itemClicked.connect(self.on_channel_selected)
        main_layout.addWidget(self.channel_list, 1)

        # Right side: Wrap the details in a scroll area.
        self.detail_widget = QWidget()
        detail_layout = QVBoxLayout(self.detail_widget)
        # Add margins (left, top, right, bottom) so content is centered with space on sides.
        detail_layout.setContentsMargins(50, 20, 50, 20)
        detail_layout.setAlignment(Qt.AlignTop)

        # "Select a channel" label at top with larger font.
        self.channel_label = QLabel("Select a channel")
        self.channel_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.channel_label.setAlignment(Qt.AlignLeft)
        detail_layout.addWidget(self.channel_label)

        # Widget to hold all channel-specific information.
        self.info_widget = QWidget()
        self.info_layout = QVBoxLayout(self.info_widget)
        self.info_layout.setContentsMargins(20, 20, 20, 20)
        self.info_layout.setAlignment(Qt.AlignTop)
        detail_layout.addWidget(self.info_widget)

        # "Save Changes" button below info; initially hidden.
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        self.save_button.hide()
        detail_layout.addWidget(self.save_button)

        # Embed detail_widget in a scroll area.
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.detail_widget)
        main_layout.addWidget(scroll_area, 2)

    def clear_layout(self, layout):
        """Helper function to clear all items from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def load_channels(self):
        """Populate the channel list by scanning CHANNELS_DIR, excluding folders ending with '(not in use)'."""
        self.channel_list.clear()
        if not CHANNELS_DIR.exists():
            QMessageBox.critical(self, "Error", f"Channels directory not found:\n{CHANNELS_DIR}")
            return

        for entry in CHANNELS_DIR.iterdir():
            if entry.is_dir() and not entry.name.endswith("(not in use)"):
                item = QListWidgetItem(entry.name)
                self.channel_list.addItem(item)

    def on_channel_selected(self, item: QListWidgetItem):
        """Load the media list, credentials, clips and archive sections for the selected channel."""
        channel_name = item.text()
        self.current_channel = CHANNELS_DIR / channel_name
        self.channel_label.setText(f"Channel: {channel_name}")
        self.save_button.show()
        self.load_channel_info()

    def load_channel_info(self):
        """
        Load the media_list.txt (platforms), credentials.json, and directories (Clips and Archive)
        for the selected channel.
        """
        # Clear previous info widgets.
        self.clear_layout(self.info_layout)
        self.media_checkboxes.clear()

        # -------------------------------
        # ACTIVE PLATFORMS Section
        # -------------------------------
        title_label = QLabel("ACTIVE PLATFORMS")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.info_layout.addWidget(title_label)

        media_list_path = self.current_channel / "MetaData" / "media_list.txt"
        if not media_list_path.exists():
            QMessageBox.warning(self, "Warning", f"Media list file not found for channel '{self.current_channel.name}'.")
        else:
            try:
                with open(media_list_path, "r") as f:
                    lines = f.read().splitlines()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error reading media list:\n{str(e)}")
                lines = []

            # Create a checkbox for each media platform.
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                active = not line.startswith("#")
                platform_name = line.lstrip("#").strip()
                checkbox = QCheckBox(platform_name)
                checkbox.setChecked(active)
                self.info_layout.addWidget(checkbox)
                self.media_checkboxes[platform_name] = checkbox

        # -------------------------------
        # CHANNEL CREDENTIALS Section
        # -------------------------------
        self.info_layout.addSpacing(20)
        credentials_title = QLabel("CHANNEL CREDENTIALS")
        credentials_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.info_layout.addWidget(credentials_title)

        credentials_path = self.current_channel / "MetaData" / "credentials.json"
        if not credentials_path.exists():
            cred_label = QLabel("No credentials file found.")
            self.info_layout.addWidget(cred_label)
        else:
            try:
                with open(credentials_path, "r") as f:
                    credentials = json.load(f)
                # Create a global CredentialsWidget.
                cred_widget = CredentialsWidget(credentials)
                self.info_layout.addWidget(cred_widget)
            except Exception as e:
                error_label = QLabel(f"Error loading credentials: {str(e)}")
                self.info_layout.addWidget(error_label)

        # -------------------------------
        # CLIPS DIRECTORY Section
        # -------------------------------
        self.info_layout.addSpacing(20)
        self.clips_dir = self.current_channel / "Clips"
        self.archive_dir = self.current_channel / "Clips_Archive"
        # Ensure directories exist.
        self.clips_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        clips_title = QLabel("CLIPS DIRECTORY")
        clips_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.info_layout.addWidget(clips_title)
        clips_info = QLabel(str(self.clips_dir))
        self.info_layout.addWidget(clips_info)

        self.clips_table = QTableWidget()
        self.clips_table.setColumnCount(2)
        self.clips_table.setHorizontalHeaderLabels(["Folder Name", "Creation Date"])
        self.clips_table.setSelectionBehavior(QTableWidget.SelectRows)
        # Disable multiple selection.
        self.clips_table.setSelectionMode(QTableWidget.SingleSelection)
        # Stretch table columns.
        self.clips_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.load_clips_table()
        self.info_layout.addWidget(self.clips_table)

        clips_buttons_widget = QWidget()
        clips_buttons_layout = QHBoxLayout(clips_buttons_widget)
        self.clips_delete_btn = QPushButton("DELETE")
        self.clips_delete_btn.clicked.connect(self.delete_selected_clips)
        clips_buttons_layout.addWidget(self.clips_delete_btn)
        self.clips_archive_btn = QPushButton("ARCHIVE")
        self.clips_archive_btn.clicked.connect(self.archive_selected_clips)
        clips_buttons_layout.addWidget(self.clips_archive_btn)
        self.clips_open_btn = QPushButton("OPEN SELECTED")
        self.clips_open_btn.clicked.connect(self.open_selected_clips)
        clips_buttons_layout.addWidget(self.clips_open_btn)
        # Button to open the Clips directory itself.
        self.clips_open_dir_btn = QPushButton("OPEN DIRECTORY")
        self.clips_open_dir_btn.clicked.connect(self.open_clips_directory)
        clips_buttons_layout.addWidget(self.clips_open_dir_btn)
        self.info_layout.addWidget(clips_buttons_widget)

        # -------------------------------
        # ARCHIVE DIRECTORY Section
        # -------------------------------
        self.info_layout.addSpacing(20)
        archive_title = QLabel("ARCHIVE DIRECTORY")
        archive_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.info_layout.addWidget(archive_title)
        archive_info = QLabel(str(self.archive_dir))
        self.info_layout.addWidget(archive_info)

        self.archive_table = QTableWidget()
        self.archive_table.setColumnCount(2)
        self.archive_table.setHorizontalHeaderLabels(["Folder Name", "Creation Date"])
        self.archive_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.archive_table.setSelectionMode(QTableWidget.SingleSelection)
        # Stretch table columns.
        self.archive_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.load_archive_table()
        self.info_layout.addWidget(self.archive_table)

        archive_buttons_widget = QWidget()
        archive_buttons_layout = QHBoxLayout(archive_buttons_widget)
        self.archive_delete_btn = QPushButton("DELETE")
        self.archive_delete_btn.clicked.connect(self.delete_selected_archives)
        archive_buttons_layout.addWidget(self.archive_delete_btn)
        self.archive_unarchive_btn = QPushButton("UNARCHIVE")
        self.archive_unarchive_btn.clicked.connect(self.unarchive_selected_archives)
        archive_buttons_layout.addWidget(self.archive_unarchive_btn)
        self.archive_open_btn = QPushButton("OPEN SELECTED")
        self.archive_open_btn.clicked.connect(self.open_selected_archives)
        archive_buttons_layout.addWidget(self.archive_open_btn)
        # Button to open the Archive directory itself.
        self.archive_open_dir_btn = QPushButton("OPEN DIRECTORY")
        self.archive_open_dir_btn.clicked.connect(self.open_archive_directory)
        archive_buttons_layout.addWidget(self.archive_open_dir_btn)
        self.info_layout.addWidget(archive_buttons_widget)

        self.info_layout.addStretch(1)

    def load_clips_table(self):
        """Load the Clips directory table with folder name and creation date (sorted desc by creation date)
        and fix its height to show 5 rows."""
        folders = []
        for item in self.clips_dir.iterdir():
            if item.is_dir():
                try:
                    ctime = item.stat().st_ctime
                except Exception:
                    ctime = 0
                folders.append((item.name, ctime))
        folders.sort(key=lambda x: x[1], reverse=True)

        self.clips_table.setRowCount(len(folders))
        for row, (folder_name, ctime) in enumerate(folders):
            name_item = QTableWidgetItem(folder_name)
            date_item = QTableWidgetItem(time.ctime(ctime))
            name_item.setFlags(name_item.flags() ^ Qt.ItemIsEditable)
            date_item.setFlags(date_item.flags() ^ Qt.ItemIsEditable)
            self.clips_table.setItem(row, 0, name_item)
            self.clips_table.setItem(row, 1, date_item)

        header_height = self.clips_table.horizontalHeader().height()
        row_height = self.clips_table.verticalHeader().defaultSectionSize()
        self.clips_table.setFixedHeight(header_height + row_height * 5)

    def load_archive_table(self):
        """Load the Archive directory table with folder name and creation date (sorted desc by creation date)
        and fix its height to show 5 rows."""
        folders = []
        for item in self.archive_dir.iterdir():
            if item.is_dir():
                try:
                    ctime = item.stat().st_ctime
                except Exception:
                    ctime = 0
                folders.append((item.name, ctime))
        folders.sort(key=lambda x: x[1], reverse=True)

        self.archive_table.setRowCount(len(folders))
        for row, (folder_name, ctime) in enumerate(folders):
            name_item = QTableWidgetItem(folder_name)
            date_item = QTableWidgetItem(time.ctime(ctime))
            name_item.setFlags(name_item.flags() ^ Qt.ItemIsEditable)
            date_item.setFlags(date_item.flags() ^ Qt.ItemIsEditable)
            self.archive_table.setItem(row, 0, name_item)
            self.archive_table.setItem(row, 1, date_item)

        header_height = self.archive_table.horizontalHeader().height()
        row_height = self.archive_table.verticalHeader().defaultSectionSize()
        self.archive_table.setFixedHeight(header_height + row_height * 5)

    def delete_selected_clips(self):
        """Delete selected folder in the Clips directory (send to recycle bin)."""
        selected_rows = self.clips_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        folder_name = self.clips_table.item(selected_rows[0].row(), 0).text()
        folder_path = self.clips_dir / folder_name
        try:
            send2trash(str(folder_path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete {folder_name}:\n{str(e)}")
        self.load_clips_table()

    def archive_selected_clips(self):
        """Move selected folder from Clips to Clips_Archive."""
        selected_rows = self.clips_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        folder_name = self.clips_table.item(selected_rows[0].row(), 0).text()
        src = self.clips_dir / folder_name
        dst = self.archive_dir / folder_name
        try:
            shutil.move(str(src), str(dst))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to archive {folder_name}:\n{str(e)}")
        self.load_clips_table()
        self.load_archive_table()

    def open_selected_clips(self):
        """Open selected folder from the Clips directory in Windows Explorer."""
        selected_rows = self.clips_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        folder_name = self.clips_table.item(selected_rows[0].row(), 0).text()
        folder_path = self.clips_dir / folder_name
        try:
            os.startfile(str(folder_path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open {folder_name}:\n{str(e)}")

    def open_clips_directory(self):
        """Open the Clips directory itself in Windows Explorer."""
        try:
            os.startfile(str(self.clips_dir))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Clips directory:\n{str(e)}")

    def delete_selected_archives(self):
        """Delete selected folder in the Archive directory (send to recycle bin)."""
        selected_rows = self.archive_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        folder_name = self.archive_table.item(selected_rows[0].row(), 0).text()
        folder_path = self.archive_dir / folder_name
        try:
            send2trash(str(folder_path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete {folder_name}:\n{str(e)}")
        self.load_archive_table()

    def unarchive_selected_archives(self):
        """Move selected folder from Clips_Archive back to Clips."""
        selected_rows = self.archive_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        folder_name = self.archive_table.item(selected_rows[0].row(), 0).text()
        src = self.archive_dir / folder_name
        dst = self.clips_dir / folder_name
        try:
            shutil.move(str(src), str(dst))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to unarchive {folder_name}:\n{str(e)}")
        self.load_archive_table()
        self.load_clips_table()

    def open_selected_archives(self):
        """Open selected folder from the Archive directory in Windows Explorer."""
        selected_rows = self.archive_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        folder_name = self.archive_table.item(selected_rows[0].row(), 0).text()
        folder_path = self.archive_dir / folder_name
        try:
            os.startfile(str(folder_path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open {folder_name}:\n{str(e)}")

    def open_archive_directory(self):
        """Open the Archive directory itself in Windows Explorer."""
        try:
            os.startfile(str(self.archive_dir))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Archive directory:\n{str(e)}")

    def save_changes(self):
        """Save the current checkbox states back to the media_list.txt file."""
        if self.current_channel is None:
            QMessageBox.warning(self, "Warning", "No channel selected!")
            return

        lines = []
        for platform, checkbox in self.media_checkboxes.items():
            if checkbox.isChecked():
                lines.append(platform)
            else:
                lines.append(f"#{platform}")

        media_list_path = self.current_channel / "MetaData" / "media_list.txt"
        try:
            with open(media_list_path, "w") as f:
                f.write("\n".join(lines))
            QMessageBox.information(self, "Success", "Media list updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update media list:\n{str(e)}")


class MainWindow(QMainWindow):
    """
    Main application window containing only the Channels Manager.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Presence Manager - Channels")
        self.resize(900, 700)
        self.channel_manager = ChannelManagerWidget()
        self.setCentralWidget(self.channel_manager)


def main():
    """Entry point for the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
