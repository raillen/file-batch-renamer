from PyQt5.QtWidgets import (QLabel, QScrollArea, QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap

class PreviewPanel(QWidget):
    # Sinais
    file_double_clicked = pyqtSignal(str)  # Emite o caminho do arquivo

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface do painel de visualização"""
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Visualização do Arquivo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #888888; color: white; padding: 5px;")
        layout.addWidget(title)
        
        # Área de rolagem para a visualização
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(200)
        self.scroll_area.setMaximumHeight(300)
        
        # Label para a visualização
        self.preview_label = QLabel("Nenhum arquivo selecionado")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #f0f0f0;")
        self.preview_label.setMouseTracking(True)
        
        # Conectar eventos do mouse
        self.preview_label.mouseDoubleClickEvent = self.handle_double_click
        
        self.scroll_area.setWidget(self.preview_label)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)

    def set_preview(self, preview_data, tooltip=None):
        """Define o conteúdo da visualização"""
        if isinstance(preview_data, QPixmap):
            # Se for uma imagem
            self.preview_label.setPixmap(preview_data)
            self.preview_label.setAlignment(Qt.AlignCenter)
        else:
            # Se for texto
            self.preview_label.clear()
            self.preview_label.setText(preview_data)
            self.preview_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.preview_label.setWordWrap(True)
            self.preview_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; font-family: monospace;")
        
        if tooltip:
            self.preview_label.setToolTip(tooltip)
        else:
            self.preview_label.setToolTip("")

    def set_file_path(self, file_path):
        """Define o caminho do arquivo atual"""
        self.preview_label.setProperty("current_file_path", file_path)

    def handle_double_click(self, event):
        """Lida com duplo clique no painel de visualização"""
        file_path = self.preview_label.property("current_file_path")
        if file_path:
            self.file_double_clicked.emit(file_path)
        
        # Chama o método original
        QLabel.mouseDoubleClickEvent(self.preview_label, event)

    def clear_preview(self):
        """Limpa a visualização"""
        self.preview_label.clear()
        self.preview_label.setText("Nenhum arquivo selecionado")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #f0f0f0;")
        self.preview_label.setProperty("current_file_path", None)
        self.preview_label.setToolTip("") 