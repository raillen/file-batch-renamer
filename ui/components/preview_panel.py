from PyQt5.QtWidgets import (QLabel, QScrollArea, QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap
from core.language_manager import LanguageManager

class PreviewPanel(QWidget):
    # Sinais
    file_double_clicked = pyqtSignal(str)  # Emite o caminho do arquivo

    def __init__(self, parent=None):
        super().__init__(parent)
        self.language_manager = LanguageManager()
        self.current_file_path = None
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface do painel de visualização"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Título
        self.title_label = QLabel(self.language_manager.get_text("preview"))
        self.title_label.setMaximumHeight(80)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("background-color: #888888; color: white; padding: 5px;")
        layout.addWidget(self.title_label)
        
        # Área de rolagem para o conteúdo
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(200)
        self.scroll_area.setMaximumHeight(300)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(self.scroll_area)
        
        # Label para o conteúdo
        self.content_label = QLabel()
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setWordWrap(True)
        self.content_label.setText(self.language_manager.get_text("no_file_selected"))
        self.content_label.setStyleSheet("background-color: #f0f0f0;")
        self.content_label.setMouseTracking(True)
        self.scroll_area.setWidget(self.content_label)
        
        # Conecta o evento de duplo clique
        self.content_label.mouseDoubleClickEvent = self.handle_double_click

    def resizeEvent(self, event):
        """Reajusta o preview quando a janela é redimensionada"""
        super().resizeEvent(event)
        if self.current_file_path and isinstance(self.content_label.pixmap(), QPixmap):
            self.adjust_preview_size()

    def adjust_preview_size(self):
        """Ajusta o tamanho do preview para caber na área disponível"""
        if not self.current_file_path:
            return
            
        pixmap = self.content_label.pixmap()
        if not pixmap:
            return
            
        # Obtém o tamanho disponível na scroll area
        available_size = self.scroll_area.viewport().size()
        
        # Calcula a proporção para manter o aspecto
        pixmap_size = pixmap.size()
        ratio = min(
            available_size.width() / pixmap_size.width(),
            available_size.height() / pixmap_size.height()
        )
        
        # Aplica o redimensionamento mantendo o aspecto
        new_size = QSize(
            int(pixmap_size.width() * ratio),
            int(pixmap_size.height() * ratio)
        )
        
        scaled_pixmap = pixmap.scaled(
            new_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.content_label.setPixmap(scaled_pixmap)

    def set_preview(self, content, file_path=None):
        """Define o conteúdo da visualização"""
        self.current_file_path = file_path
        if isinstance(content, QPixmap):
            self.content_label.setPixmap(content)
            self.adjust_preview_size()
        else:
            self.content_label.setText(str(content))
            self.content_label.setScaledContents(False)

    def set_file_path(self, file_path):
        """Define o caminho do arquivo atual"""
        self.current_file_path = file_path

    def handle_double_click(self, event):
        """Lida com duplo clique no painel de visualização"""
        if self.current_file_path:
            self.file_double_clicked.emit(self.current_file_path)
        
        # Chama o método original
        QLabel.mouseDoubleClickEvent(self.content_label, event)

    def clear_preview(self):
        """Limpa a visualização"""
        self.current_file_path = None
        self.content_label.setText(self.language_manager.get_text("no_file_selected"))
        self.content_label.setPixmap(None)
        self.content_label.setToolTip("") 