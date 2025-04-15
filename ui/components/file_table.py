from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QMenu, QAction,
                            QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal
from core.language_manager import LanguageManager

class FileTable(QTableWidget):
    # Sinais
    file_selected = pyqtSignal(str)  # Emite o nome do arquivo selecionado
    file_renamed = pyqtSignal(str, str)  # Emite nome antigo e novo
    file_deleted = pyqtSignal(str)  # Emite o nome do arquivo deletado
    file_located = pyqtSignal(str)  # Emite o nome do arquivo para localizar

    def __init__(self, parent=None):
        super().__init__(parent)
        self.language_manager = LanguageManager()
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface da tabela"""
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels([self.language_manager.get_text("preview")])
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
        self.setRowCount(len(files))
        for i, file_name in enumerate(files):
            item = QTableWidgetItem(file_name)
            self.setItem(i, 0, item)

    def handle_item_changed(self, item):
        """Lida com mudanças nos itens da tabela"""
        if item.column() == 0:  # Apenas na coluna de nomes
            row = item.row()
            old_name = self.item(row, 0).text()
            new_name = item.text()
            
            if old_name != new_name:
                self.file_renamed.emit(old_name, new_name)

    def handle_selection_changed(self):
        """Lida com mudanças na seleção"""
        selected_items = self.selectedItems()
        if selected_items:
            self.file_selected.emit(selected_items[0].text())

    def show_context_menu(self, position):
        """Mostra o menu de contexto"""
        menu = QMenu()
        
        # Ações do menu
        locate_action = menu.addAction(self.language_manager.get_text("locate"))
        delete_action = menu.addAction(self.language_manager.get_text("delete"))
        rename_action = menu.addAction(self.language_manager.get_text("rename"))
        
        action = menu.exec_(self.viewport().mapToGlobal(position))
        if action == locate_action:
            self.trigger_locate()
        elif action == delete_action:
            self.trigger_delete()
        elif action == rename_action:
            self.trigger_rename()

    def trigger_locate(self):
        """Emite sinal para localizar arquivo"""
        selected_items = self.selectedItems()
        if selected_items:
            self.file_located.emit(selected_items[0].text())

    def trigger_delete(self):
        """Emite sinal para deletar arquivo"""
        selected_items = self.selectedItems()
        if selected_items:
            self.file_deleted.emit(selected_items[0].text())

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

    def move_row(self, current_index, new_index):
        """Move uma linha para uma nova posição"""
        if 0 <= current_index < self.rowCount() and 0 <= new_index < self.rowCount():
            # Salva os itens
            current_item = self.takeItem(current_index, 0)
            new_item = self.takeItem(new_index, 0)
            
            # Insere os itens nas novas posições
            self.setItem(new_index, 0, current_item)
            self.setItem(current_index, 0, new_item)
            
            # Atualiza a seleção
            self.setCurrentCell(new_index, 0)
            
            return True
        return False 