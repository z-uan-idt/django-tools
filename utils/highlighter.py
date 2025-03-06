from PyQt6.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat, QPainter
from PyQt6.QtCore import QRegularExpression, Qt, QRect
from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QWidget

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.width = 40  # Fixed width for line numbers

    def paintEvent(self, event):
        """Paint line numbers in the margin area"""
        painter = QPainter(self)
        painter.setPen(Qt.GlobalColor.darkGray)
        painter.setFont(QFont("Consolas", 10))
        
        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(
                    0, top, 
                    self.width - 4, 
                    self.editor.fontMetrics().height(), 
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, 
                    number
                )
            
            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            block_number += 1

class PythonCodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Line number area setup
        self.line_number_area = LineNumberArea(self)
        
        # Syntax highlighter
        self.highlighter = PythonSyntaxHighlighter(self.document())
        
        # Connect paintEvent for line numbers
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        
        # Initial setup
        self.update_line_number_area_width(0)
        
        # Set stylesheet for line number margin
        self.setStyleSheet("""
            QPlainTextEdit {
                padding-left: 0px;
            }
        """)
    
    def update_line_number_area_width(self, block_count):
        """Update width of line number area"""
        self.setViewportMargins(self.line_number_area.width, 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        """Update line number area when text is scrolled or changed"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                         self.line_number_area.width, 
                                         rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """Override resize event to update line number area"""
        super().resizeEvent(event)
        
        contents_rect = self.contentsRect()
        self.line_number_area.setGeometry(
            contents_rect.left(), 
            contents_rect.top(), 
            self.line_number_area.width, 
            contents_rect.height()
        )
    
    def paintEvent(self, event):
        """Paint line numbers before main paint event"""
        # Call parent paintEvent to render text
        super().paintEvent(event)
        
        # Additional painting for line numbers can be done here if needed

class PythonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        
        self.highlighting_rules = []
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))  # Blue
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "and", "as", "assert", "break", "class", "continue", "def",
            "del", "elif", "else", "except", "False", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda", "None",
            "nonlocal", "not", "or", "pass", "raise", "return", "True",
            "try", "while", "with", "yield"
        ]
        for word in keywords:
            pattern = QRegularExpression(r'\b' + word + r'\b')
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))  # Orange
        self.highlighting_rules.append((QRegularExpression(r'".*?"'), string_format))
        self.highlighting_rules.append((QRegularExpression(r"'.*?'"), string_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))  # Light green
        self.highlighting_rules.append((QRegularExpression(r'\b[0-9]+\b'), number_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))  # Green
        self.highlighting_rules.append((QRegularExpression(r'#[^\n]*'), comment_format))
    
    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            matches = pattern.globalMatch(text)
            while matches.hasNext():
                match = matches.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)