from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QMenu, QAction,
                            QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal

class FileTable(QTableWidget):
    # Sinais
    file_selected = pyqtSignal(str)  # Emite o nome do arquivo selecionado
    file_renamed = pyqtSignal(str, str)  # Emite nome antigo e novo
    file_deleted = pyqtSignal(str)  # Emite o nome do arquivo deletado
    file_located = pyqtSignal(str)  # Emite o nome do arquivo para localizar

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface da tabela"""
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(["Arquivos na Pasta"])
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        
        # Conectar sinais
        self.itemChanged.connect(self.handle_item_changed)
        self.itemSelectionChanged.connect(self.handle_selection_changed)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def set_files(self, files):
        """Define os arquivos na tabela"""
        self.setRowCount(0)
        for file_name in files:
            row_position = self.rowCount()
            self.insertRow(row_position)
            item = QTableWidgetItem(file_name)
            item.setData(Qt.UserRole, file_name)  # Armazena o nome original
            self.setItem(row_position, 0, item)

    def handle_item_changed(self, item):
        """Lida com mudanças nos itens da tabela"""
        if item.column() == 0:  # Apenas na coluna de nomes
            old_name = item.data(Qt.UserRole)
            new_name = item.text().strip()
            
            if new_name and new_name != old_name:
                self.file_renamed.emit(old_name, new_name)
                item.setData(Qt.UserRole, new_name)  # Atualiza o nome armazenado

    def handle_selection_changed(self):
        """Lida com mudanças na seleção"""
        selected_items = self.selectedItems()
        if selected_items:
            file_name = selected_items[0].text()
            self.file_selected.emit(file_name)

    def show_context_menu(self, position):
        """Mostra o menu de contexto"""
        menu = QMenu()
        
        # Ações do menu
        locate_action = QAction("Localizar arquivo na pasta", self)
        locate_action.triggered.connect(self.trigger_locate)
        menu.addAction(locate_action)
        
        delete_action = QAction("Deletar arquivo", self)
        delete_action.triggered.connect(self.trigger_delete)
        menu.addAction(delete_action)
        
        rename_action = QAction("Renomear arquivo", self)
        rename_action.triggered.connect(self.trigger_rename)
        menu.addAction(rename_action)
        
        menu.exec_(self.mapToGlobal(position))

    def trigger_locate(self):
        """Emite sinal para localizar arquivo"""
        selected_items = self.selectedItems()
        if selected_items:
            file_name = selected_items[0].text()
            self.file_located.emit(file_name)

    def trigger_delete(self):
        """Emite sinal para deletar arquivo"""
        selected_items = self.selectedItems()
        if selected_items:
            file_name = selected_items[0].text()
            self.file_deleted.emit(file_name)

    def trigger_rename(self):
        """Inicia edição do item selecionado"""
        selected_items = self.selectedItems()
        if selected_items:
            self.editItem(selected_items[0])

    def move_row_up(self):
        """Move a linha selecionada para cima"""
        current_row = self.currentRow()
        if current_row > 0:
            self.move_row(current_row, current_row - 1)

    def move_row_down(self):
        """Move a linha selecionada para baixo"""
        current_row = self.currentRow()
        if current_row < self.rowCount() - 1:
            self.move_row(current_row, current_row + 1)

    def move_row(self, current_row, new_row):
        """Move uma linha para uma nova posição"""
        # Move os itens
        item = self.takeItem(current_row, 0)
        self.insertRow(new_row)
        self.setItem(new_row, 0, item)
        self.removeRow(current_row)
        
        # Seleciona a nova posição
        self.setCurrentCell(new_row, 0) 