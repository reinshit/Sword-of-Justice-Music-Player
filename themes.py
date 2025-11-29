"""
Theme stylesheets for dark and light modes
"""

DARK_THEME = """
    QMainWindow, QWidget {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    QLabel {
        color: #ffffff;
    }
    QPushButton {
        background-color: #2d2d30;
        color: #ffffff;
        border: 1px solid #3f3f46;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #3e3e42;
        border: 1px solid #007acc;
    }
    QPushButton:pressed {
        background-color: #007acc;
    }
    QPushButton:disabled {
        background-color: #252526;
        color: #656565;
    }
    QComboBox, QSpinBox {
        background-color: #2d2d30;
        color: #ffffff;
        border: 1px solid #3f3f46;
        border-radius: 4px;
        padding: 5px;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #ffffff;
    }
    QProgressBar {
        border: 1px solid #3f3f46;
        border-radius: 4px;
        background-color: #2d2d30;
        text-align: center;
        color: #ffffff;
    }
    QProgressBar::chunk {
        background-color: #007acc;
        border-radius: 3px;
    }
    QTextEdit {
        background-color: #1e1e1e;
        color: #d4d4d4;
        border: 1px solid #3f3f46;
        border-radius: 4px;
        font-family: Consolas, monospace;
    }
    QListWidget {
        background-color: #2d2d30;
        color: #ffffff;
        border: 1px solid #3f3f46;
        border-radius: 4px;
    }
    QListWidget::item:selected {
        background-color: #007acc;
    }
    QListWidget::item:hover {
        background-color: #3e3e42;
    }
    QCheckBox {
        color: #ffffff;
    }
    QFrame[frameShape="4"] {
        color: #3f3f46;
    }
"""

LIGHT_THEME = """
    QMainWindow, QWidget {
        background-color: #f5f5f5;
        color: #000000;
    }
    QPushButton {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #d0d0d0;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #e8e8e8;
        border: 1px solid #0078d4;
    }
    QPushButton:pressed {
        background-color: #0078d4;
        color: #ffffff;
    }
    QPushButton:disabled {
        background-color: #f0f0f0;
        color: #a0a0a0;
    }
    QComboBox, QSpinBox {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        padding: 5px;
    }
    QProgressBar {
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        background-color: #ffffff;
        text-align: center;
    }
    QProgressBar::chunk {
        background-color: #0078d4;
        border-radius: 3px;
    }
    QTextEdit {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        font-family: Consolas, monospace;
    }
    QListWidget {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
    }
    QListWidget::item:selected {
        background-color: #0078d4;
        color: #ffffff;
    }
    QListWidget::item:hover {
        background-color: #e8e8e8;
    }
"""


def get_theme(dark_mode=True):
    """Get theme stylesheet based on mode"""
    return DARK_THEME if dark_mode else LIGHT_THEME