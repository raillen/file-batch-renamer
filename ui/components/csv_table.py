from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QMenu, QAction,
                            QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal
from core.language_manager import LanguageManager

class CSVTable(QTableWidget):
    # Sinais
    row_removed = pyqtSignal(int)  # Emite o índice da linha removida
    row_moved = pyqtSignal(int, int)  # Emite índice atual e novo
    data_changed = pyqtSignal()  # Emite quando os dados são alterados

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
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def set_data(self, data):
        """Define os dados na tabela"""
        self.setRowCount(len(data))
        for i, name in enumerate(data):
            item = QTableWidgetItem(name)
            self.setItem(i, 0, item)

    def handle_item_changed(self, item):
        """Lida com mudanças nos itens da tabela"""
        if item.column() == 0:  # Apenas na coluna de nomes
            self.data_changed.emit()

    def show_context_menu(self, position):
        """Mostra o menu de contexto"""
        menu = QMenu()
        
        # Ações do menu
        remove_action = QAction(self.language_manager.get_text("remove"), self)
        menu.addAction(remove_action)
        
        action = menu.exec_(self.viewport().mapToGlobal(position))
        if action == remove_action:
            self.trigger_remove()

    def trigger_remove(self):
        """Remove a linha selecionada"""
        current_row = self.currentRow()
        if current_row >= 0:
            self.removeRow(current_row)
            self.row_removed.emit(current_row)

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
            
            # Emite o sinal
            self.row_moved.emit(current_index, new_index)
            
            return True
        return False

    def get_data(self):
        """Retorna os dados da tabela"""
        data = []
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item:
                data.append(item.text())
        return data 