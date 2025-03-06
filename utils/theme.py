LIGHT_THEME = """
    /* Biến màu sắc */
    * {
        font-family: Arial, sans-serif;
        line-height: 1.2;
    }
    
    /* QWidget - Toàn bộ cửa sổ và widget */
    QWidget {
        background-color: #dddddd;
        color: #333333;
    }
    
    QTabBar::tab {
        margin-right: 5px;  /* Khoảng cách giữa các tab */
    }
    
    /* QMainWindow - Cửa sổ chính */
    QMainWindow {
        background-color: #f5f5f5;
    }
    
    /* Các panel và container */
    QFrame, QDialog, QGroupBox {
        background-color: #dddddd;
    }

    QTextEdit, QPlainTextEdit {
        border-right: 1.5px solid #ffffff;
        border-bottom: 1.5px solid #ffffff;
        border-top: 1.5px solid #292929;
        border-left: 1.5px solid #292929;
        border-radius: 2px;
        padding: 8px;
        background-color: white;
        selection-background-color: #0078D7;
        min-height: 20px;
    }
    QTextEdit:disabled, QPlainTextEdit:disabled {
        background-color: #f5f5f5;
        color: #000;
    }
    
    /* QLineEdit - Ô nhập liệu */
    QLineEdit {
        border-right: 1.5px solid #ffffff;
        border-bottom: 1.5px solid #ffffff;
        border-top: 1.5px solid #292929;
        border-left: 1.5px solid #292929;
        border-radius: 2px;
        padding: 3.5px 8px;
        background-color: white;
        selection-background-color: #0078D7;
        min-height: 20px;
    }
    QLineEdit:disabled {
        background-color: #f5f5f5;
        color: #000;
    }
    /* QPushButton - Nút bấm */
    QPushButton {
        font-family: inherit;
        border: 2px solid #dddddd;
        background-color: #dddddd;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 5px 30px;
        min-height: 20px;
        font-weight: bold;
        
        border-top: 2px solid #ffffff;
        border-left: 2px solid #ffffff;
        border-right: 2px solid #292929;
        border-bottom: 2px solid #292929;
    }
    QPushButton:disabled {
        color: #ffffff;
        border: 2px solid #dddddd;
        background-color: #dddddd;
        border-top: 2px solid #ffffff;
        border-left: 2px solid #ffffff;
        border-right: 2px solid #292929;
        border-bottom: 2px solid #292929;
    }
    QPushButton:pressed {
        border-top: 2px solid #292929;
        border-left: 2px solid #292929;
        border-right: 2px solid #ffffff;
        border-bottom: 2px solid #ffffff;
    }
    /* QProgressBar - Thanh tiến trình */
    QProgressBar {
        border-top: 2px solid #ffffff;
        border-left: 2px solid #ffffff;
        border-right: 2px solid #292929;
        border-bottom: 2px solid #292929;
        border-radius: 2px;
        text-align: center;
        background-color: white;
        height: 12px;
        color: #333333;
    }
    QProgressBar::chunk {
        background-color: #0078D7;
        border-radius: 2px;
    }
    
    /* QTreeWidget - Cây thư mục */
    QTreeWidget {
        border-radius: 2px;
        background-color: white;
        alternate-background-color: #f9f9f9;
        show-decoration-selected: 0;
        border-top: 2px solid #292929;
        border-left: 2px solid #292929;
        border-right: 2px solid #ffffff;
        border-bottom: 2px solid #ffffff;
    }
    QTreeWidget::item:focus {
        border: none;
        outline: none;
    }
    QTreeWidget::item {
        height: 25px;
        border-radius: 2px;
    }
    QTreeWidget::item:hover {
        background-color: #dddddd;
    }
    QTreeWidget::item:selected {
        background-color: #dddddd;
        font-weight: bold;
        color: #000000;
        border: none;
        outline: none;
        show-decoration-selected: 0;
    }
    /* QSplitter - Chia tách cửa sổ */
    QSplitter::handle {
        background-color: #dddddd;
    }
    QSplitter::handle:horizontal {
        width: 4px;
    }
    QSplitter::handle:vertical {
        height: 4px;
    }
    
    /* QTabWidget - Tab */
    QTabWidget::pane {
        border-top: 2px solid #ffffff;
        border-left: 2px solid #ffffff;
        border-right: 2px solid #292929;
        border-bottom: 2px solid #292929;
        border-radius: 2px;
        background-color: white;
        border-top-left-radius: 0px;
    }
    QTabBar::tab {
        background-color: #dddddd;
        border-top: 2px solid #ffffff;
        border-left: 2px solid #ffffff;
        border-right: 2px solid #292929;
        border-bottom: 2px solid #292929;
        padding: 8px 12px;
        min-width: 80px;
        margin-bottom: 4px;
    }
    QTabBar::tab:selected {
        border-right: 2px solid #ffffff;
        border-bottom: 2px solid #ffffff;
        border-top: 2px solid #292929;
        border-left: 2px solid #292929;
        background-color: transparent;
    }
    QTabBar::tab:hover:!selected {
        background-color: #e6e6e6;
    }
    /* QLabel - Nhãn */
    QLabel {
        color: #333333;
    }
    
    /* QScrollBar - Thanh cuộn */
    QScrollBar:vertical {
        background: #f8f8f8;
        width: 12px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #cccccc;
        min-height: 20px;
        border-radius: 2px;
    }
    QScrollBar::handle:vertical:hover {
        background: #aaaaaa;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar:horizontal {
        background: #f8f8f8;
        height: 12px;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background: #cccccc;
        min-width: 20px;
        border-radius: 2px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #aaaaaa;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    QComboBox {
        border-right: 1.5px solid #ffffff;
        border-bottom: 1.5px solid #ffffff;
        border-top: 1.5px solid #292929;
        border-left: 1.5px solid #292929;
        border-radius: 2px;
        padding: 3.5px 8px;
        background-color: white;
        selection-background-color: #0078D7;
        min-height: 20px;
    }
    QComboBox:disabled {
        background-color: #dddddd;
    }
    QComboBox QAbstractItemView {
        border: 1px solid #292929;
        border-radius: 2px;
        padding: 8px;
        background-color: white;
        selection-background-color: #0078D7;
        min-height: 20px;
    }
"""