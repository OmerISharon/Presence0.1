import os
import json
import shutil
import time
import sys
import subprocess
from datetime import datetime
from send2trash import send2trash
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QListWidget, QCheckBox, QTableWidget, 
                            QTableWidgetItem, QScrollArea, QFrame, QSplitter, QHeaderView, 
                            QMessageBox, QGroupBox, QGridLayout, QTextEdit)
from PyQt5.QtGui import QFont, QIcon, QClipboard, QColor, QTextCursor
from PyQt5.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal

# Constants
CHANNELS_DIR = "D:/2025/Projects/Presence/Presence0.1/Channels"  # This can be changed as needed

# Uploader script paths
YOUTUBE_UPLOADER = r"D:\\2025\\Projects\\Presence\\Presence0.1\\Uploader\\Platforms\\Youtube\\Uploader_Youtube\\Code\\Uploader_YouTube.py"
TIKTOK_UPLOADER = r"D:\\2025\\Projects\\Presence\\Presence0.1\\Uploader\\Platforms\\Tiktok\\Uploader_Tiktok\\Code\\Uploader_TikTok.py"
INSTAGRAM_UPLOADER = r"D:\\2025\\Projects\\Presence\\Presence0.1\\Uploader\\Platforms\\Instagram\\Uploader_Instagram\\Code\\Uploader_Instagram.py"

class ModernStyle:
    """Class to define modern UI styling constants"""
    # Colors
    PRIMARY_COLOR = "#3498db"  # Blue
    SECONDARY_COLOR = "#2ecc71"  # Green
    BACKGROUND_COLOR = "#ffffff"  # Light gray
    CARD_COLOR = "#ffffff"  # White
    TEXT_COLOR = "#2c3e50"  # Dark blue/gray
    BORDER_COLOR = "#e0e0e0"  # Light gray for borders
    INACTIVE_COLOR = "#95a5a6"  # Gray
    ERROR_COLOR = "#e74c3c"  # Red
    WARNING_COLOR = "#f39c12"  # Orange
    
    # Fonts
    HEADER_FONT = QFont("Segoe UI", 12, QFont.Bold)
    SUBHEADER_FONT = QFont("Segoe UI", 10, QFont.Bold)
    BODY_FONT = QFont("Segoe UI", 9)
    SMALL_FONT = QFont("Segoe UI", 8)
    
    # Dimensions
    BORDER_RADIUS = "5px"
    BUTTON_HEIGHT = "30px"
    PADDING = "10px"
    MARGIN = "5px"
    
    # Button Styles
    BUTTON_STYLE = f"""
        QPushButton {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border: none;
            border-radius: {BORDER_RADIUS};
            padding: 5px {PADDING};
            height: {BUTTON_HEIGHT};
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #2980b9;
        }}
        QPushButton:pressed {{
            background-color: #1f6aa5;
        }}
        QPushButton:disabled {{
            background-color: {INACTIVE_COLOR};
        }}
    """
    
    SECONDARY_BUTTON_STYLE = f"""
        QPushButton {{
            background-color: {SECONDARY_COLOR};
            color: white;
            border: none;
            border-radius: {BORDER_RADIUS};
            padding: 5px {PADDING};
            height: {BUTTON_HEIGHT};
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #27ae60;
        }}
        QPushButton:pressed {{
            background-color: #1e8449;
        }}
    """
    
    DANGER_BUTTON_STYLE = f"""
        QPushButton {{
            background-color: {ERROR_COLOR};
            color: white;
            border: none;
            border-radius: {BORDER_RADIUS};
            padding: 5px {PADDING};
            height: {BUTTON_HEIGHT};
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #c0392b;
        }}
        QPushButton:pressed {{
            background-color: #a93226;
        }}
    """
    
    WARNING_BUTTON_STYLE = f"""
        QPushButton {{
            background-color: {WARNING_COLOR};
            color: white;
            border: none;
            border-radius: {BORDER_RADIUS};
            padding: 5px {PADDING};
            height: {BUTTON_HEIGHT};
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #d35400;
        }}
        QPushButton:pressed {{
            background-color: #a04000;
        }}
    """
    
    # New uploader button styles
    UPLOAD_BTN_STYLE = f"""
        QPushButton {{
            background-color: LimeGreen;
            color: white;
            border: none;
            border-radius: {BORDER_RADIUS};
            padding: 5px {PADDING};
            height: {BUTTON_HEIGHT};
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: ForestGreen;
        }}
        QPushButton:pressed {{
            background-color: DarkGreen;
        }}
        QPushButton:disabled {{
            background-color: #cccccc;
            color: #888888;
        }}
    """
    
    OPEN_BTN_STYLE = f"""
        QPushButton {{
            background-color: RoyalBlue;
            color: white;
            border: none;
            border-radius: {BORDER_RADIUS};
            padding: 5px {PADDING};
            height: {BUTTON_HEIGHT};
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: MediumBlue;
        }}
        QPushButton:pressed {{
            background-color: DarkBlue;
        }}
    """
    
    # Checkbox Style
    CHECKBOX_STYLE = f"""
        QCheckBox {{
            spacing: 10px;
            color: {TEXT_COLOR};
            font-family: "Segoe UI";
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 3px;
            border: 2px solid {BORDER_COLOR};
        }}
        QCheckBox::indicator:unchecked {{
            background-color: white;
        }}
        QCheckBox::indicator:checked {{
            background-color: {PRIMARY_COLOR};
            border: 2px solid {PRIMARY_COLOR};
            image: url(check.png);
        }}
    """
    
    # List and Table Styles
    LIST_STYLE = f"""
        QListWidget {{
            background-color: {CARD_COLOR};
            border-radius: {BORDER_RADIUS};
            border: 1px solid {BORDER_COLOR};
            padding: 5px;
        }}
        QListWidget::item {{
            padding: 5px;
            border-radius: 3px;
        }}
        QListWidget::item:selected {{
            background-color: {PRIMARY_COLOR};
            color: white;
        }}
        QListWidget::item:hover {{
            background-color: #ecf0f1;
        }}
    """
    
    TABLE_STYLE = f"""
        QTableWidget {{
            background-color: {CARD_COLOR};
            border-radius: {BORDER_RADIUS};
            border: 1px solid {BORDER_COLOR};
            gridline-color: {BORDER_COLOR};
        }}
        QTableWidget::item {{
            padding: 5px;
        }}
        QTableWidget::item:selected {{
            background-color: {PRIMARY_COLOR};
            color: white;
        }}
        QHeaderView::section {{
            background-color: #ecf0f1;
            padding: 5px;
            border: 1px solid {BORDER_COLOR};
            font-weight: bold;
        }}
    """
    
    # Group Box Style
    GROUP_BOX_STYLE = f"""
        QGroupBox {{
            font-family: "Segoe UI";
            font-weight: bold;
            border: 1px solid {BORDER_COLOR};
            border-radius: {BORDER_RADIUS};
            margin-top: 20px;
            background-color: {CARD_COLOR};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 0px;
            right: 0px;
            top: 0px;
            padding: 5px 10px;
            color: white;
            background-color: #9b59b6;
            border-top-left-radius: {BORDER_RADIUS};
            border-top-right-radius: {BORDER_RADIUS};
        }}
    """
    
    # Scroll Area Style
    SCROLL_AREA_STYLE = f"""
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        QScrollBar:vertical {{
            border: none;
            background: {BACKGROUND_COLOR};
            width: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {INACTIVE_COLOR};
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
    """
    
    # Container Box Style
    CONTAINER_BOX_STYLE = f"""
        QWidget#containerBox {{
            background-color: {CARD_COLOR};
            border-radius: 8px;
            border: 1px solid {BORDER_COLOR};
            padding: 15px;
            margin: 10px 20px;
        }}
    """


class ToastNotification(QFrame):
    """A modern toast notification widget that appears and disappears automatically"""
    def __init__(self, parent=None, message="", duration=2000):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(52, 152, 219, 0.9);
                border-radius: 20px;
                color: white;
                font-family: 'Segoe UI';
                font-weight: bold;
                padding: 0 20px;
            }}
        """)
        
        # Create layout and label
        layout = QHBoxLayout(self)
        self.label = QLabel(message)
        self.label.setStyleSheet("background-color: transparent;")
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        
        # Set up the timer for automatic dismissal
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)
        self.timer.start(duration)
        
        # Position the notification
        parent_rect = parent.rect()
        self.setFixedWidth(parent_rect.width() // 3)
        x = (parent_rect.width() - self.width()) // 2
        y = parent_rect.height() - self.height() - 20
        self.move(x, y)
        self.show()


class CredentialsWidget(QWidget):
    """Widget for displaying and managing channel credentials securely"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.credentials = {}
        self.masked = True
    
    def initUI(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Credentials grid
        self.credentials_grid = QGridLayout()
        self.credentials_grid.setColumnStretch(1, 1)  # Make the value column stretchable
        
        # Control buttons layout
        buttons_layout = QHBoxLayout()
        
        # Toggle visibility button
        self.toggle_button = QPushButton("Decrypt")
        self.toggle_button.setStyleSheet(ModernStyle.BUTTON_STYLE)
        self.toggle_button.clicked.connect(self.toggle_masking)
        
        # Copy button
        self.copy_button = QPushButton("Copy All")
        self.copy_button.setStyleSheet(ModernStyle.SECONDARY_BUTTON_STYLE)
        self.copy_button.clicked.connect(self.copy_credentials)
        
        buttons_layout.addWidget(self.toggle_button)
        buttons_layout.addWidget(self.copy_button)
        
        layout.addLayout(self.credentials_grid)
        layout.addLayout(buttons_layout)
    
    def set_credentials(self, credentials):
        """Set credentials and update display"""
        self.credentials = credentials
        self.update_display()
    
    def update_display(self):
        """Update the credentials display based on masking status"""
        # Clear existing items
        for i in reversed(range(self.credentials_grid.count())):
            self.credentials_grid.itemAt(i).widget().setParent(None)
        
        # Add header row
        header_key = QLabel("Key")
        header_key.setFont(ModernStyle.SUBHEADER_FONT)
        header_value = QLabel("Value")
        header_value.setFont(ModernStyle.SUBHEADER_FONT)
        self.credentials_grid.addWidget(header_key, 0, 0)
        self.credentials_grid.addWidget(header_value, 0, 1)
        
        # Add credential rows
        row = 1
        for key, value in self.credentials.items():
            key_label = QLabel(key)
            key_label.setStyleSheet(f"color: {ModernStyle.TEXT_COLOR};")
            
            # Mask or show the value based on the current state
            if self.masked:
                display_value = '*' * len(str(value)) if value else ''
            else:
                display_value = str(value)
            
            value_label = QLabel(display_value)
            value_label.setStyleSheet(f"color: {ModernStyle.TEXT_COLOR};")
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            
            self.credentials_grid.addWidget(key_label, row, 0)
            self.credentials_grid.addWidget(value_label, row, 1)
            row += 1
    
    def toggle_masking(self):
        """Toggle between masked and plain text display of credentials"""
        self.masked = not self.masked
        self.toggle_button.setText("Encrypt" if not self.masked else "Decrypt")
        self.update_display()
    
    def copy_credentials(self):
        """Copy all credentials to clipboard in plain text"""
        clipboard_text = '\n'.join([f"{key}: {value}" for key, value in self.credentials.items()])
        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_text)
        
        # Show toast notification
        if self.parent() and hasattr(self.parent(), 'parent'):
            main_parent = self.parent().parent()
            if main_parent:
                ToastNotification(main_parent, "Credentials copied to clipboard!")


class ChannelManagerWidget(QWidget):
    """Central widget for managing channels, their media platforms, and clip directories"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.load_channels()
        self.current_channel_name = None
        self.selected_clip_folder = None
    
    def initUI(self):
        """Initialize the UI components"""
        self.setStyleSheet(f"background-color: {ModernStyle.BACKGROUND_COLOR};")
        
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Create a splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Channel list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        channels_label = QLabel("Channels")
        channels_label.setFont(ModernStyle.HEADER_FONT)
        
        self.channel_list = QListWidget()
        self.channel_list.setStyleSheet(ModernStyle.LIST_STYLE)
        self.channel_list.setFont(ModernStyle.BODY_FONT)
        self.channel_list.currentRowChanged.connect(self.channel_selected)
        
        left_layout.addWidget(channels_label)
        left_layout.addWidget(self.channel_list)
        
        # Right panel - Channel details in a scroll area with centered container
        right_panel = QScrollArea()
        right_panel.setWidgetResizable(True)
        right_panel.setStyleSheet(ModernStyle.SCROLL_AREA_STYLE)
        
        # Create outer container widget for centering
        outer_container = QWidget()
        outer_layout = QVBoxLayout(outer_container)
        outer_layout.setAlignment(Qt.AlignHCenter)
        
        # Create boxed container with styled appearance
        self.container_box = QWidget()
        self.container_box.setObjectName("containerBox")
        self.container_box.setStyleSheet(ModernStyle.CONTAINER_BOX_STYLE)
        self.container_box.setMinimumWidth(800)
        self.container_box.setMaximumWidth(1200)
        
        # Create the details layout inside the container box
        self.details_layout = QVBoxLayout(self.container_box)
        self.details_layout.setAlignment(Qt.AlignTop)
        self.details_layout.setSpacing(15)
        self.details_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add the container box to the outer layout
        outer_layout.addWidget(self.container_box)
        
        # Set the outer container as the scroll area widget
        right_panel.setWidget(outer_container)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set a fixed width for the left panel
        left_panel.setMinimumWidth(200)
        left_panel.setMaximumWidth(250)
        
        # Make the right panel take all remaining space
        right_panel.setMinimumWidth(600)
        
        main_layout.addWidget(splitter)
    
    def load_channels(self):
        """Load channels from the CHANNELS_DIR"""
        # Clear existing items
        self.channel_list.clear()
        
        if not os.path.exists(CHANNELS_DIR):
            QMessageBox.warning(self, "Directory Not Found", 
                                f"Channels directory not found: {CHANNELS_DIR}")
            return
        
        # Get all directories in the channels folder
        channels = []
        for item in os.listdir(CHANNELS_DIR):
            item_path = os.path.join(CHANNELS_DIR, item)
            if os.path.isdir(item_path) and not item.endswith("(not in use)"):
                channels.append(item)
        
        # Add items to the list
        self.channel_list.addItems(sorted(channels))
        
        # Select the first channel if available
        if self.channel_list.count() > 0:
            self.channel_list.setCurrentRow(0)
    
    def channel_selected(self):
        """Handle channel selection from the list"""
        selected_channel = self.channel_list.currentItem()
        if selected_channel:
            self.current_channel_name = selected_channel.text()
            self.load_channel_info(self.current_channel_name)
    
    def clear_layout(self, layout):
        """Clear all widgets from a layout"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())
    
    def load_channel_info(self, channel_name):
        """Load information for the selected channel"""
        # Clear existing channel details
        self.clear_layout(self.details_layout)
        
        channel_path = os.path.join(CHANNELS_DIR, channel_name)
        
        # Create sections
        self.create_media_platforms_section(channel_path)
        
        # Add spacing between sections
        self.details_layout.addSpacing(20)
        
        self.create_credentials_section(channel_path)
        
        # Add spacing between sections
        self.details_layout.addSpacing(20)
        
        self.create_upload_section()
        
        # Add spacing between sections
        self.details_layout.addSpacing(20)
        
        self.create_clips_section(channel_path)
        
        # Add spacing between sections
        self.details_layout.addSpacing(20)
        
        self.create_archive_section(channel_path)
    
    def create_media_platforms_section(self, channel_path):
        """Create the media platforms section"""
        # Group box for media platforms
        media_group = QGroupBox("Active Media Platforms")
        media_group.setStyleSheet(ModernStyle.GROUP_BOX_STYLE)
        media_layout = QVBoxLayout(media_group)
        
        # Locate the media list file
        metadata_path = os.path.join(channel_path, "MetaData")
        if not os.path.exists(metadata_path):
            os.makedirs(metadata_path)
        
        media_list_path = os.path.join(metadata_path, "media_list.txt")
        self.media_checkboxes = []
        
        if os.path.exists(media_list_path):
            with open(media_list_path, "r") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        is_active = not line.startswith("#")
                        media_name = line[1:].strip() if line.startswith("#") else line
                        
                        checkbox = QCheckBox(media_name)
                        checkbox.setStyleSheet(ModernStyle.CHECKBOX_STYLE)
                        checkbox.setFont(ModernStyle.BODY_FONT)
                        checkbox.setChecked(is_active)
                        media_layout.addWidget(checkbox)
                        self.media_checkboxes.append((checkbox, media_name))
        
        # Add Save Changes button
        save_button = QPushButton("Save Changes")
        save_button.setStyleSheet(ModernStyle.SECONDARY_BUTTON_STYLE)
        save_button.clicked.connect(lambda: self.save_media_platforms(media_list_path))
        media_layout.addWidget(save_button)
        
        self.details_layout.addWidget(media_group)
    
    def save_media_platforms(self, media_list_path):
        """Save changes to media platforms list"""
        with open(media_list_path, "w") as file:
            for checkbox, media_name in self.media_checkboxes:
                prefix = "" if checkbox.isChecked() else "# "
                file.write(f"{prefix}{media_name}\n")
        
        # Show notification
        ToastNotification(self.parent(), "Media platforms saved successfully!")
    
    def create_credentials_section(self, channel_path):
        """Create the credentials section"""
        # Group box for credentials
        cred_group = QGroupBox("Channel Credentials")
        cred_group.setStyleSheet(ModernStyle.GROUP_BOX_STYLE)
        cred_layout = QVBoxLayout(cred_group)
        
        # Create credentials widget
        self.credentials_widget = CredentialsWidget(self)
        
        # Load credentials from file
        credentials_path = os.path.join(channel_path, "MetaData", "credentials.json")
        credentials = {}
        
        if os.path.exists(credentials_path):
            try:
                with open(credentials_path, "r") as file:
                    credentials = json.load(file)
            except json.JSONDecodeError:
                pass
        
        self.credentials_widget.set_credentials(credentials)
        cred_layout.addWidget(self.credentials_widget)
        
        self.details_layout.addWidget(cred_group)
    
    def create_upload_section(self):
        """Create the upload buttons section"""
        # Group box for upload buttons
        upload_group = QGroupBox("Upload to Platforms")
        upload_group.setStyleSheet(ModernStyle.GROUP_BOX_STYLE)
        
        # Create grid layout for buttons
        upload_layout = QGridLayout(upload_group)
        
        # YouTube button
        yt_upload_btn = QPushButton("Upload to YouTube")
        yt_upload_btn.setStyleSheet(ModernStyle.UPLOAD_BTN_STYLE)
        yt_upload_btn.setEnabled(False)
        yt_upload_btn.clicked.connect(lambda: self.upload_clip("YouTube"))
        
        # TikTok button
        tiktok_upload_btn = QPushButton("Upload to TikTok")
        tiktok_upload_btn.setStyleSheet(ModernStyle.UPLOAD_BTN_STYLE)
        tiktok_upload_btn.setEnabled(False)
        tiktok_upload_btn.clicked.connect(lambda: self.upload_clip("TikTok"))
        
        # Instagram button
        insta_upload_btn = QPushButton("Upload to Instagram")
        insta_upload_btn.setStyleSheet(ModernStyle.UPLOAD_BTN_STYLE)
        insta_upload_btn.setEnabled(False)
        insta_upload_btn.clicked.connect(lambda: self.upload_clip("Instagram"))
        
        # Add platform buttons in a single column layout
        upload_layout.addWidget(yt_upload_btn, 0, 0)
        upload_layout.addWidget(tiktok_upload_btn, 1, 0)
        upload_layout.addWidget(insta_upload_btn, 2, 0)
        
        # Store references to upload buttons to enable/disable them
        self.upload_buttons = {
            "YouTube": yt_upload_btn,
            "TikTok": tiktok_upload_btn,
            "Instagram": insta_upload_btn
        }
        
        self.details_layout.addWidget(upload_group)
    
    def create_clips_section(self, channel_path):
        """Create the clips section"""
        # Group box for clips
        clips_group = QGroupBox("Clips Directory")
        clips_group.setStyleSheet(ModernStyle.GROUP_BOX_STYLE)
        clips_layout = QVBoxLayout(clips_group)
        
        # New Clip button at the top
        new_clip_btn = QPushButton("New Clip")
        new_clip_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: {ModernStyle.BORDER_RADIUS};
                padding: 5px {ModernStyle.PADDING};
                height: {ModernStyle.BUTTON_HEIGHT};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #8e44ad;
            }}
            QPushButton:pressed {{
                background-color: #7d3c98;
            }}
        """)
        new_clip_btn.clicked.connect(self.create_new_clip)
        clips_layout.addWidget(new_clip_btn)
        
        # Ensure clips directory exists
        clips_path = os.path.join(channel_path, "Clips")
        if not os.path.exists(clips_path):
            os.makedirs(clips_path)
        
        # Create table for clips
        self.clips_table = QTableWidget(0, 2)
        self.clips_table.setHorizontalHeaderLabels(["Folder Name", "Created"])
        self.clips_table.setStyleSheet(ModernStyle.TABLE_STYLE)
        self.clips_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.clips_table.verticalHeader().setVisible(False)
        self.clips_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.clips_table.setSelectionMode(QTableWidget.SingleSelection)
        self.clips_table.itemSelectionChanged.connect(self.clip_selection_changed)
        
        # Set minimum height to show approximately 10 rows
        self.clips_table.setMinimumHeight(380)  # Allows for about 10 rows plus header
        
        # Ensure the scroll bar appears when needed
        self.clips_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        delete_button = QPushButton("DELETE")
        delete_button.setStyleSheet(ModernStyle.DANGER_BUTTON_STYLE)
        delete_button.clicked.connect(lambda: self.delete_clip(clips_path))
        
        archive_button = QPushButton("ARCHIVE")
        archive_button.setStyleSheet(ModernStyle.WARNING_BUTTON_STYLE)
        archive_button.clicked.connect(lambda: self.archive_clip(channel_path))
        
        open_selected_button = QPushButton("OPEN SELECTED")
        open_selected_button.setStyleSheet(ModernStyle.BUTTON_STYLE)
        open_selected_button.clicked.connect(lambda: self.open_selected_folder(clips_path))
        
        buttons_layout.addWidget(delete_button)
        buttons_layout.addWidget(archive_button)
        buttons_layout.addWidget(open_selected_button)
        
        clips_layout.addWidget(self.clips_table)
        clips_layout.addLayout(buttons_layout)
        
        self.details_layout.addWidget(clips_group)
        
        # Load clips data
        self.load_clips_table(clips_path)
    
    def create_archive_section(self, channel_path):
        """Create the archive section"""
        # Group box for archive
        archive_group = QGroupBox("Archive Directory")
        archive_group.setStyleSheet(ModernStyle.GROUP_BOX_STYLE)
        archive_layout = QVBoxLayout(archive_group)
        
        # Ensure archive directory exists
        archive_path = os.path.join(channel_path, "Clips_Archive")
        if not os.path.exists(archive_path):
            os.makedirs(archive_path)
        
        # Create table for archive
        self.archive_table = QTableWidget(0, 2)
        self.archive_table.setHorizontalHeaderLabels(["Folder Name", "Created"])
        self.archive_table.setStyleSheet(ModernStyle.TABLE_STYLE)
        self.archive_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.archive_table.verticalHeader().setVisible(False)
        self.archive_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.archive_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Set minimum height to show approximately 10 rows
        self.archive_table.setMinimumHeight(380)  # Allows for about 10 rows plus header
        
        # Ensure the scroll bar appears when needed
        self.archive_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        delete_button = QPushButton("DELETE")
        delete_button.setStyleSheet(ModernStyle.DANGER_BUTTON_STYLE)
        delete_button.clicked.connect(lambda: self.delete_clip(archive_path, is_archive=True))
        
        unarchive_button = QPushButton("UNARCHIVE")
        unarchive_button.setStyleSheet(ModernStyle.WARNING_BUTTON_STYLE)
        unarchive_button.clicked.connect(lambda: self.unarchive_clip(channel_path))
        
        open_selected_button = QPushButton("OPEN SELECTED")
        open_selected_button.setStyleSheet(ModernStyle.BUTTON_STYLE)
        open_selected_button.clicked.connect(lambda: self.open_selected_folder(archive_path, is_archive=True))
        
        buttons_layout.addWidget(delete_button)
        buttons_layout.addWidget(unarchive_button)
        buttons_layout.addWidget(open_selected_button)
        
        archive_layout.addWidget(self.archive_table)
        archive_layout.addLayout(buttons_layout)
        
        self.details_layout.addWidget(archive_group)
        
        # Load archive data
        self.load_archive_table(archive_path)
    
    def load_clips_table(self, clips_path):
        """Load clip folders into the table"""
        self.clips_table.setRowCount(0)
        self.selected_clip_folder = None
        
        # Disable upload buttons when loading a new clips table
        if hasattr(self, 'upload_buttons'):
            for button in self.upload_buttons.values():
                button.setEnabled(False)
        
        if os.path.exists(clips_path):
            folders = []
            for item in os.listdir(clips_path):
                item_path = os.path.join(clips_path, item)
                if os.path.isdir(item_path):
                    created_time = os.path.getctime(item_path)
                    folders.append((item, created_time))
            
            # Sort by creation time (newest first)
            folders.sort(key=lambda x: x[1], reverse=True)
            
            for row, (folder_name, created_time) in enumerate(folders):
                self.clips_table.insertRow(row)
                
                folder_item = QTableWidgetItem(folder_name)
                folder_item.setFlags(folder_item.flags() & ~Qt.ItemIsEditable)
                
                date_str = datetime.fromtimestamp(created_time).strftime("%Y-%m-%d %H:%M")
                date_item = QTableWidgetItem(date_str)
                date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
                
                self.clips_table.setItem(row, 0, folder_item)
                self.clips_table.setItem(row, 1, date_item)
    
    def load_archive_table(self, archive_path):
        """Load archived folders into the table"""
        self.archive_table.setRowCount(0)
        
        if os.path.exists(archive_path):
            folders = []
            for item in os.listdir(archive_path):
                item_path = os.path.join(archive_path, item)
                if os.path.isdir(item_path):
                    created_time = os.path.getctime(item_path)
                    folders.append((item, created_time))
            
            # Sort by creation time (newest first)
            folders.sort(key=lambda x: x[1], reverse=True)
            
            for row, (folder_name, created_time) in enumerate(folders):
                self.archive_table.insertRow(row)
                
                folder_item = QTableWidgetItem(folder_name)
                folder_item.setFlags(folder_item.flags() & ~Qt.ItemIsEditable)
                
                date_str = datetime.fromtimestamp(created_time).strftime("%Y-%m-%d %H:%M")
                date_item = QTableWidgetItem(date_str)
                date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
                
                self.archive_table.setItem(row, 0, folder_item)
                self.archive_table.setItem(row, 1, date_item)
    
    def clip_selection_changed(self):
        """Handle clip selection change to enable/disable upload buttons"""
        selected_rows = self.clips_table.selectionModel().selectedRows()
        
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_clip_folder = self.clips_table.item(row, 0).text()
            
            # Enable upload buttons
            for button in self.upload_buttons.values():
                button.setEnabled(True)
        else:
            self.selected_clip_folder = None
            
            # Disable upload buttons
            for button in self.upload_buttons.values():
                button.setEnabled(False)
    
    def upload_clip(self, platform):
        """Upload a clip to the specified platform"""
        if not self.current_channel_name or not self.selected_clip_folder:
            return
        
        # Get paths
        channel_path = os.path.join(CHANNELS_DIR, self.current_channel_name)
        clip_path = os.path.join(channel_path, "Clips", self.selected_clip_folder)
        archive_path = os.path.join(channel_path, "Clips_Archive")
        
        # Determine which uploader script to use
        uploader_script = None
        if platform == "YouTube":
            uploader_script = YOUTUBE_UPLOADER
        elif platform == "TikTok":
            uploader_script = TIKTOK_UPLOADER
        elif platform == "Instagram":
            uploader_script = INSTAGRAM_UPLOADER
        
        if not uploader_script or not os.path.exists(uploader_script):
            QMessageBox.warning(self, "Error", f"{platform} uploader script not found.")
            return
        
        try:
            # Run the uploader script with the channel name and clip path as arguments
            process = subprocess.run(
                [sys.executable, uploader_script, self.current_channel_name, clip_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Disable upload buttons
            for button in self.upload_buttons.values():
                button.setEnabled(False)
            
            self.selected_clip_folder = None
            
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(
                self,
                "Upload Failed",
                f"Failed to upload to {platform}.\n\nError: {e.stderr}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred: {str(e)}"
            )
    
    def delete_clip(self, base_path, is_archive=False):
        """Delete the selected clip folder by sending it to the trash"""
        table = self.archive_table if is_archive else self.clips_table
        selected_rows = table.selectionModel().selectedRows()
        
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        folder_name = table.item(row, 0).text()
        folder_path = os.path.join(base_path, folder_name)
        
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete '{folder_name}'?\nIt will be sent to the recycle bin.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                send2trash(folder_path)
                
                # Refresh the table
                if is_archive:
                    self.load_archive_table(base_path)
                else:
                    self.load_clips_table(base_path)
                
                ToastNotification(self.parent(), f"Folder '{folder_name}' sent to recycle bin.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not delete folder: {str(e)}")
    
    def archive_clip(self, channel_path):
        """Archive the selected clip folder"""
        clips_path = os.path.join(channel_path, "Clips")
        archive_path = os.path.join(channel_path, "Clips_Archive")
        
        selected_rows = self.clips_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        folder_name = self.clips_table.item(row, 0).text()
        src_path = os.path.join(clips_path, folder_name)
        dst_path = os.path.join(archive_path, folder_name)
        
        if not os.path.exists(archive_path):
            os.makedirs(archive_path)
        
        try:
            shutil.move(src_path, dst_path)
            
            # Refresh both tables
            self.load_clips_table(clips_path)
            self.load_archive_table(archive_path)
            
            ToastNotification(self.parent(), f"Folder '{folder_name}' archived.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not archive folder: {str(e)}")
    
    def unarchive_clip(self, channel_path):
        """Unarchive the selected folder"""
        clips_path = os.path.join(channel_path, "Clips")
        archive_path = os.path.join(channel_path, "Clips_Archive")
        
        selected_rows = self.archive_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        folder_name = self.archive_table.item(row, 0).text()
        src_path = os.path.join(archive_path, folder_name)
        dst_path = os.path.join(clips_path, folder_name)
        
        if not os.path.exists(clips_path):
            os.makedirs(clips_path)
        
        try:
            shutil.move(src_path, dst_path)
            
            # Refresh both tables
            self.load_clips_table(clips_path)
            self.load_archive_table(archive_path)
            
            ToastNotification(self.parent(), f"Folder '{folder_name}' unarchived.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not unarchive folder: {str(e)}")
    
    def open_selected_folder(self, base_path, is_archive=False):
        """Open the selected folder in Windows Explorer"""
        table = self.archive_table if is_archive else self.clips_table
        selected_rows = table.selectionModel().selectedRows()
        
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        folder_name = table.item(row, 0).text()
        folder_path = os.path.join(base_path, folder_name)
        
        try:
            os.startfile(folder_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open folder: {str(e)}")
    
    def open_directory(self, directory_path):
        """Open the directory in Windows Explorer"""
        try:
            os.startfile(directory_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open directory: {str(e)}")

    def create_new_clip(self):
        """Start the process of creating a new clip for the selected channel"""
        if not self.current_channel_name:
            QMessageBox.warning(self, "Error", "Please select a channel first.")
            return
        
        # Build the path to the channel's executor directory
        executor_dir = os.path.join("D:\\2025\\Projects\\Presence\\Presence0.1\\Creator\\Channels", 
                                self.current_channel_name, "Executer")
        
        # Build the path to the specific BAT file
        bat_file = os.path.join(executor_dir, f"{self.current_channel_name}.bat")
        
        if not os.path.exists(executor_dir):
            # Try to create the directory if it doesn't exist
            try:
                os.makedirs(executor_dir)
                QMessageBox.information(self, "Directory Created", 
                                        f"Created Executer directory for {self.current_channel_name}.")
            except Exception as e:
                QMessageBox.warning(self, "Error", 
                                f"Could not find or create Executer directory: {str(e)}")
                return
        
        # Check if the BAT file exists
        if not os.path.exists(bat_file):
            QMessageBox.warning(self, "File Not Found", 
                            f"BAT file not found: {bat_file}")
            
            # Open the executor directory so the user can see what's there
            try:
                os.startfile(executor_dir)
            except Exception as e:
                pass
            return
        
        # Create and show the output window
        self.output_window = ExecutionOutputWindow(self.current_channel_name, bat_file, self.parent())
        
        # Connect the process_finished signal to refresh the clips table
        self.output_window.process_finished.connect(self.refresh_clips_table)
        
        self.output_window.show()
        
        # Show a toast notification
        ToastNotification(self.parent(), f"Started clip creation for {self.current_channel_name}")

    def refresh_clips_table(self):
        """Refresh the clips table to show any new clips"""
        if self.current_channel_name:
            clips_path = os.path.join(CHANNELS_DIR, self.current_channel_name, "Clips")
            self.load_clips_table(clips_path)


class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Channel Manager")
        self.setMinimumSize(1080, 800)
        self.setStyleSheet(f"background-color: {ModernStyle.BACKGROUND_COLOR};")
        
        # Set central widget
        self.channel_manager = ChannelManagerWidget(self)
        self.setCentralWidget(self.channel_manager)


class ExecutionOutputWindow(QMainWindow):
    process_finished = pyqtSignal()

    """Window to display output from the clip creation process"""
    def __init__(self, channel_name, bat_file, parent=None):
        super().__init__(parent)
        self.channel_name = channel_name
        self.bat_file = bat_file
        self.process = None
        self.initUI()
        self.startProcess()
        
    def initUI(self):
        """Initialize the UI components"""
        self.setWindowTitle(f"Clip Creation - {self.channel_name}")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create output text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 10))
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #0C0C0C;
                color: #CCCCCC;
                border: none;
            }
        """)
        
        # Create status label
        self.status_label = QLabel("Starting process...")
        self.status_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                padding: 5px;
            }
        """)
        
        # Create buttons
        buttons_layout = QHBoxLayout()
        
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet(ModernStyle.DANGER_BUTTON_STYLE)
        self.close_button.clicked.connect(self.close_window)
        
        self.kill_button = QPushButton("Terminate Process")
        self.kill_button.setStyleSheet(ModernStyle.WARNING_BUTTON_STYLE)
        self.kill_button.clicked.connect(self.kill_process)
        
        buttons_layout.addWidget(self.kill_button)
        buttons_layout.addWidget(self.close_button)
        
        # Add widgets to layout
        main_layout.addWidget(self.output_text)
        main_layout.addWidget(self.status_label)
        main_layout.addLayout(buttons_layout)
        
    def startProcess(self):
        """Start the batch file process and capture its output"""
        self.output_text.append(f"Starting execution of: {self.bat_file}\n")
        self.output_text.append("-" * 80 + "\n")
        
        try:
            # Create process with pipe for stdout and stderr
            self.process = subprocess.Popen(
                self.bat_file,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True,
                bufsize=1
            )
            
            # Create threads to read output
            self.stdout_thread = StdoutReaderThread(self.process.stdout, self)
            self.stderr_thread = StdoutReaderThread(self.process.stderr, self, is_error=True)
            
            # Start threads
            self.stdout_thread.output_received.connect(self.update_output)
            self.stderr_thread.output_received.connect(self.update_output)
            self.stdout_thread.start()
            self.stderr_thread.start()
            
            # Create a timer to check process status
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.check_process_status)
            self.timer.start(500)  # Check every 500ms
            
        except Exception as e:
            self.output_text.append(f"Error starting process: {str(e)}\n")
            self.status_label.setText("Error")
            self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
    
    def update_output(self, text, is_error=False):
        """Update the output text area with new content"""
        if is_error:
            # Format error in red
            self.output_text.append(f"<span style='color:red;'>{text}</span>")
        else:
            self.output_text.append(text)
        
        # Scroll to bottom
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.output_text.setTextCursor(cursor)
    
    def check_process_status(self):
        """Check if the process is still running"""
        if self.process and self.process.poll() is not None:
            # Process has finished
            exit_code = self.process.poll()
            if exit_code == 0:
                self.status_label.setText("Process completed successfully")
                self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            else:
                self.status_label.setText(f"Process failed with exit code {exit_code}")
                self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            
            self.timer.stop()
            self.kill_button.setEnabled(False)
            
            # Emit the signal that the process has finished
            self.process_finished.emit()
    
    def kill_process(self):
        """Terminate the running process"""
        if self.process:
            try:
                self.process.terminate()
                self.output_text.append("\n<span style='color:orange;'>Process terminated by user</span>\n")
                self.status_label.setText("Process terminated by user")
                self.status_label.setStyleSheet("QLabel { color: orange; font-weight: bold; }")
                self.kill_button.setEnabled(False)
            except Exception as e:
                self.output_text.append(f"<span style='color:red;'>Error terminating process: {str(e)}</span>\n")
    
    def close_window(self):
        """Close the window and terminate the process if still running"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
        self.close()
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
        event.accept()


class StdoutReaderThread(QThread):
    """Thread to read stdout/stderr output from a process"""
    output_received = pyqtSignal(str, bool)
    
    def __init__(self, stream, parent=None, is_error=False):
        super().__init__(parent)
        self.stream = stream
        self.is_error = is_error
    
    def run(self):
        """Thread run method"""
        for line in iter(self.stream.readline, ''):
            if not line:
                break
            self.output_received.emit(line, self.is_error)


def main():
    """Application entry point"""
    app = QApplication([])
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Start event loop
    app.exec_()


if __name__ == "__main__":
    main()