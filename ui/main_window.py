import os
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QFileDialog, QLabel, 
                            QLineEdit, QVBoxLayout, QHBoxLayout, QWidget,
                            QMessageBox, QMenuBar, QAction, QToolButton, QMenu)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.components.file_table import FileTable
from ui.components.csv_table import CSVTable
from ui.components.preview_panel import PreviewPanel
from core.file_manager import FileManager
from core.csv_manager import CSVManager
from core.history_manager import HistoryManager
from core.preview_manager import PreviewManager
from core.language_manager import LanguageManager

class BatchRenamer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Inicializa os gerenciadores
        self.file_manager = FileManager()
        self.csv_manager = CSVManager()
        self.history_manager = HistoryManager(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rename_history.json")
        )
        self.preview_manager = PreviewManager()
        self.language_manager = LanguageManager()
        
        # Conecta o sinal de mudança de idioma
        self.language_manager.language_changed.connect(self.update_ui_text)
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("Renomeador em Lote")
        self.setGeometry(100, 100, 1200, 800)
        
        # Cria a barra de menus
        self.create_menu_bar()
        
        # Widget principal e layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Painel esquerdo
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)
        
        # Painel do meio (CSV)
        middle_panel = self.create_middle_panel()
        main_layout.addWidget(middle_panel)
        
        # Painel direito (Arquivos)
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Atualiza os textos da interface
        self.update_ui_text()
        
    def create_menu_bar(self):
        """Cria a barra de menus"""
        menu_bar = self.menuBar()
        
        # Menu Arquivo
        self.file_menu = menu_bar.addMenu(self.language_manager.get_text("file_menu"))
        
        # Ações do menu Arquivo
        self.open_csv_action = QAction(self.language_manager.get_text("open_csv"), self)
        self.open_csv_action.triggered.connect(self.open_csv)
        self.file_menu.addAction(self.open_csv_action)
        
        self.open_folder_action = QAction(self.language_manager.get_text("open_folder"), self)
        self.open_folder_action.triggered.connect(self.open_folder)
        self.file_menu.addAction(self.open_folder_action)
        
        self.file_menu.addSeparator()
        
        # Menu de idiomas
        self.language_menu = QMenu(self.language_manager.get_text("language_menu"), self)
        self.file_menu.addMenu(self.language_menu)
        
        # Ações do menu de idiomas
        self.english_action = QAction(self.language_manager.get_text("english"), self)
        self.english_action.triggered.connect(lambda: self.language_manager.set_language("en"))
        self.language_menu.addAction(self.english_action)
        
        self.portuguese_action = QAction(self.language_manager.get_text("portuguese"), self)
        self.portuguese_action.triggered.connect(lambda: self.language_manager.set_language("pt"))
        self.language_menu.addAction(self.portuguese_action)
        
        self.spanish_action = QAction(self.language_manager.get_text("spanish"), self)
        self.spanish_action.triggered.connect(lambda: self.language_manager.set_language("es"))
        self.language_menu.addAction(self.spanish_action)
        
        self.file_menu.addSeparator()
        
        self.exit_action = QAction(self.language_manager.get_text("exit"), self)
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)
        
        # Menu Sobre
        self.about_menu = menu_bar.addMenu(self.language_manager.get_text("about_menu"))
        self.about_action = QAction(self.language_manager.get_text("about"), self)
        self.about_action.triggered.connect(self.show_about)
        self.about_menu.addAction(self.about_action)
        
    def create_left_panel(self):
        """Cria o painel esquerdo"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Botões principais
        self.csv_button = QPushButton("Abrir CSV")
        self.csv_button.setMinimumHeight(50)
        layout.addWidget(self.csv_button)
        
        self.folder_button = QPushButton("Abrir Pasta")
        self.folder_button.setMinimumHeight(50)
        layout.addWidget(self.folder_button)
        
        # Campo de extensões
        self.extensions_label = QLabel("Filtrar arquivos por extensão")
        self.extensions_field = QLineEdit()
        self.extensions_field.setPlaceholderText("Extensões separadas por vírgula (jpg,png,pdf)")
        layout.addWidget(self.extensions_label)
        layout.addWidget(self.extensions_field)
        
        # Botão de recarregar
        self.reload_button = QPushButton("Recarregar Arquivos")
        layout.addWidget(self.reload_button)
        
        # Painel de visualização
        self.preview_panel = PreviewPanel()
        layout.addWidget(self.preview_panel)
        
        # Botões de ação
        self.rename_button = QPushButton("Renomear Arquivos")
        self.rename_button.setMinimumHeight(50)
        layout.addWidget(self.rename_button)
        
        self.undo_button = QPushButton("Desfazer Renomeação")
        self.undo_button.setMinimumHeight(50)
        layout.addWidget(self.undo_button)
        
        panel.setLayout(layout)
        panel.setMaximumWidth(300)
        return panel
        
    def create_middle_panel(self):
        """Cria o painel do meio (CSV)"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Registros CSV")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #ff5555; color: white; padding: 10px;")
        title.setFont(QFont("Arial", 12))
        layout.addWidget(title)
        
        # Campo de busca
        self.csv_search_field = QLineEdit()
        self.csv_search_field.setPlaceholderText("Buscar CSV...")
        layout.addWidget(self.csv_search_field)
        
        # Layout para tabela e botões
        table_layout = QHBoxLayout()
        
        # Tabela CSV
        self.csv_table = CSVTable()
        table_layout.addWidget(self.csv_table)
        
        # Botões de seta
        arrows_layout = QVBoxLayout()
        arrows_layout.addStretch(1)
        
        self.csv_up_button = QToolButton()
        self.csv_up_button.setText("▲")
        self.csv_up_button.setToolTip("Mover linha para cima")
        arrows_layout.addWidget(self.csv_up_button)
        
        arrows_layout.addSpacing(10)
        
        self.csv_down_button = QToolButton()
        self.csv_down_button.setText("▼")
        self.csv_down_button.setToolTip("Mover linha para baixo")
        arrows_layout.addWidget(self.csv_down_button)
        
        arrows_layout.addStretch(1)
        table_layout.addLayout(arrows_layout)
        
        layout.addLayout(table_layout)
        
        # Label do caminho do CSV
        self.csv_path_label = QLabel("Diretório do CSV")
        self.csv_path_label.setAlignment(Qt.AlignCenter)
        self.csv_path_label.setStyleSheet("background-color: #888888; color: white; padding: 5px;")
        layout.addWidget(self.csv_path_label)
        
        panel.setLayout(layout)
        return panel
        
    def create_right_panel(self):
        """Cria o painel direito (Arquivos)"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Arquivos na Pasta")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #ff9999; color: white; padding: 10px;")
        title.setFont(QFont("Arial", 12))
        layout.addWidget(title)
        
        # Campo de busca
        self.files_search_field = QLineEdit()
        self.files_search_field.setPlaceholderText("Buscar arquivos...")
        layout.addWidget(self.files_search_field)
        
        # Layout para tabela e botões
        table_layout = QHBoxLayout()
        
        # Tabela de arquivos
        self.files_table = FileTable()
        table_layout.addWidget(self.files_table)
        
        # Botões de seta
        arrows_layout = QVBoxLayout()
        arrows_layout.addStretch(1)
        
        self.files_up_button = QToolButton()
        self.files_up_button.setText("▲")
        self.files_up_button.setToolTip("Mover arquivo para cima")
        arrows_layout.addWidget(self.files_up_button)
        
        arrows_layout.addSpacing(10)
        
        self.files_down_button = QToolButton()
        self.files_down_button.setText("▼")
        self.files_down_button.setToolTip("Mover arquivo para baixo")
        arrows_layout.addWidget(self.files_down_button)
        
        arrows_layout.addStretch(1)
        table_layout.addLayout(arrows_layout)
        
        layout.addLayout(table_layout)
        
        # Label do caminho da pasta
        self.folder_path_label = QLabel("Diretório da Pasta")
        self.folder_path_label.setAlignment(Qt.AlignCenter)
        self.folder_path_label.setStyleSheet("background-color: #888888; color: white; padding: 5px;")
        layout.addWidget(self.folder_path_label)
        
        panel.setLayout(layout)
        return panel
        
    def setup_connections(self):
        """Configura as conexões entre componentes"""
        # Botões principais
        self.csv_button.clicked.connect(self.open_csv)
        self.folder_button.clicked.connect(self.open_folder)
        self.reload_button.clicked.connect(self.reload_files)
        self.rename_button.clicked.connect(self.rename_files)
        self.undo_button.clicked.connect(self.undo_rename)
        
        # Campos de busca
        self.csv_search_field.textChanged.connect(self.filter_csv)
        self.files_search_field.textChanged.connect(self.filter_files)
        
        # Botões de seta
        self.csv_up_button.clicked.connect(self.csv_table.move_row_up)
        self.csv_down_button.clicked.connect(self.csv_table.move_row_down)
        self.files_up_button.clicked.connect(self.files_table.move_row_up)
        self.files_down_button.clicked.connect(self.files_table.move_row_down)
        
        # Sinais da tabela CSV
        self.csv_table.row_removed.connect(self.handle_csv_row_removed)
        self.csv_table.row_moved.connect(self.handle_csv_row_moved)
        self.csv_table.data_changed.connect(self.handle_csv_data_changed)
        
        # Sinais da tabela de arquivos
        self.files_table.file_selected.connect(self.handle_file_selected)
        self.files_table.file_renamed.connect(self.handle_file_renamed)
        self.files_table.file_deleted.connect(self.handle_file_deleted)
        self.files_table.file_located.connect(self.handle_file_located)
        
        # Sinais do painel de visualização
        self.preview_panel.file_double_clicked.connect(self.handle_file_double_clicked)
        
    def open_csv(self):
        """Abre um arquivo CSV"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Arquivo CSV", "", "CSV Files (*.csv)")
        if file_path:
            try:
                if self.csv_manager.open_csv(file_path):
                    self.csv_table.set_data(self.csv_manager.csv_data)
                    self.csv_path_label.setText(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao abrir arquivo CSV: {str(e)}")
                
    def open_folder(self):
        """Abre uma pasta"""
        folder_path = QFileDialog.getExistingDirectory(self, "Abrir Pasta")
        if folder_path:
            try:
                if self.file_manager.open_folder(folder_path):
                    self.files_table.set_files(self.file_manager.folder_files)
                    self.folder_path_label.setText(folder_path)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao abrir pasta: {str(e)}")
                
    def reload_files(self):
        """Recarrega os arquivos da pasta"""
        try:
            files = self.file_manager.load_folder_files(self.extensions_field.text())
            self.files_table.set_files(files)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao recarregar arquivos: {str(e)}")
            
    def rename_files(self):
        """Renomeia os arquivos"""
        if not self.csv_manager.csv_data:
            QMessageBox.warning(self, "Aviso", "Nenhum dado CSV carregado.")
            return
            
        if not self.file_manager.folder_files:
            QMessageBox.warning(self, "Aviso", "Nenhum arquivo na pasta.")
            return
            
        # Verifica se há entradas CSV suficientes
        if len(self.csv_manager.csv_data) < len(self.file_manager.folder_files):
            QMessageBox.warning(
                self, 
                "Aviso", 
                f"O número de nomes no CSV ({len(self.csv_manager.csv_data)}) é menor que o número de arquivos ({len(self.file_manager.folder_files)})."
            )
            
        # Pede confirmação
        reply = QMessageBox.question(
            self, 
            "Confirmar Renomeação", 
            "Deseja renomear os arquivos?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        try:
            # Prepara operações de renomeação
            operations = []
            successful_renames = 0
            failed_renames = 0
            error_details = []
            
            # Processa até o número de entradas CSV
            for i, file_name in enumerate(self.file_manager.folder_files):
                if i >= len(self.csv_manager.csv_data):
                    break
                    
                old_name = file_name
                new_name = f"{self.csv_manager.csv_data[i]}{os.path.splitext(file_name)[1]}"
                
                try:
                    if self.file_manager.rename_file(old_name, new_name):
                        operations.append({
                            "original_name": old_name,
                            "new_name": new_name
                        })
                        successful_renames += 1
                except Exception as e:
                    failed_renames += 1
                    error_details.append(f"Erro ao renomear '{old_name}' para '{new_name}': {str(e)}")
                    
            # Salva o histórico se houver renomeações bem-sucedidas
            if successful_renames > 0:
                self.history_manager.add_operation(self.file_manager.folder_path, operations)
                
            # Atualiza a lista de arquivos
            self.files_table.set_files(self.file_manager.folder_files)
            
            # Mostra resultado
            result_message = f"Renomeação concluída.\nArquivos renomeados com sucesso: {successful_renames}\nFalhas: {failed_renames}"
            
            if error_details:
                result_message += "\n\nDetalhes das falhas:"
                for i, error in enumerate(error_details, 1):
                    if i <= 10:  # Limita a 10 erros
                        result_message += f"\n{i}. {error}"
                    if len(error_details) > 10:
                        result_message += f"\n... e mais {len(error_details) - 10} erros não exibidos."
                        
            QMessageBox.information(self, "Concluído", result_message)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro durante a renomeação: {str(e)}")
            
    def undo_rename(self):
        """Desfaz a última operação de renomeação"""
        last_operation = self.history_manager.get_last_operation()
        if not last_operation:
            QMessageBox.information(self, "Informação", "Não há operações de renomeação para desfazer.")
            return
            
        folder_path = last_operation["folder_path"]
        
        if not os.path.exists(folder_path):
            QMessageBox.warning(self, "Aviso", f"A pasta original não existe mais: {folder_path}")
            return
            
        # Pede confirmação
        reply = QMessageBox.question(
            self, 
            "Confirmar Desfazer", 
            f"Deseja desfazer a última operação de renomeação em:\n{folder_path}?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        try:
            successful_undos = 0
            failed_undos = 0
            error_details = []
            
            for op in last_operation["operations"]:
                original_name = op["original_name"]
                new_name = op["new_name"]
                
                try:
                    if self.file_manager.rename_file(new_name, original_name):
                        successful_undos += 1
                except Exception as e:
                    failed_undos += 1
                    error_details.append(f"Erro ao desfazer renomeação de '{new_name}' para '{original_name}': {str(e)}")
                    
            # Remove a operação do histórico se pelo menos um desfazer foi bem-sucedido
            if successful_undos > 0:
                self.history_manager.remove_last_operation()
                
                # Atualiza a lista de arquivos se estiver na mesma pasta
                if self.file_manager.folder_path == folder_path:
                    self.files_table.set_files(self.file_manager.folder_files)
                    
            # Mostra resultado
            result_message = f"Desfazer concluído.\nArquivos restaurados com sucesso: {successful_undos}\nFalhas: {failed_undos}"
            
            if error_details:
                result_message += "\n\nDetalhes das falhas:"
                for i, error in enumerate(error_details, 1):
                    if i <= 10:
                        result_message += f"\n{i}. {error}"
                    if len(error_details) > 10:
                        result_message += f"\n... e mais {len(error_details) - 10} erros não exibidos."
                        
            QMessageBox.information(self, "Concluído", result_message)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao desfazer renomeação: {str(e)}")
            
    def filter_csv(self, text):
        """Filtra os dados do CSV"""
        filtered_data = self.csv_manager.filter_data(text)
        self.csv_table.set_data(filtered_data)
        
    def filter_files(self, text):
        """Filtra os arquivos"""
        filtered_files = [f for f in self.file_manager.folder_files if text.lower() in f.lower()]
        self.files_table.set_files(filtered_files)
        
    def handle_csv_row_removed(self, row_index):
        """Lida com remoção de linha do CSV"""
        if self.csv_manager.remove_row(row_index):
            self.csv_manager.update_csv_file()
            
    def handle_csv_row_moved(self, current_index, new_index):
        """Lida com movimento de linha do CSV"""
        if self.csv_manager.move_row(current_index, new_index):
            self.csv_manager.update_csv_file()
            
    def handle_csv_data_changed(self):
        """Lida com mudança nos dados do CSV"""
        self.csv_manager.csv_data = self.csv_table.get_data()
        self.csv_manager.update_csv_file()
        
    def handle_file_selected(self, file_name):
        """Lida com seleção de arquivo"""
        file_path = os.path.join(self.file_manager.folder_path, file_name)
        self.preview_manager.set_current_file(file_path)
        preview_data, message = self.preview_manager.get_preview()
        if preview_data:
            self.preview_panel.set_preview(preview_data, file_path)
            if message:
                self.preview_panel.content_label.setToolTip(message)
        else:
            self.preview_panel.clear_preview()
            if message:
                self.preview_panel.content_label.setText(message)
            
    def handle_file_renamed(self, old_name, new_name):
        """Lida com renomeação de arquivo"""
        try:
            if self.file_manager.rename_file(old_name, new_name):
                self.files_table.set_files(self.file_manager.folder_files)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao renomear arquivo: {str(e)}")
            
    def handle_file_deleted(self, file_name):
        """Lida com deleção de arquivo"""
        try:
            if self.file_manager.delete_file(file_name):
                self.files_table.set_files(self.file_manager.folder_files)
                self.preview_panel.clear_preview()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao deletar arquivo: {str(e)}")
            
    def handle_file_located(self, file_name):
        """Lida com localização de arquivo no Explorer"""
        try:
            self.file_manager.locate_file_in_explorer(file_name)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao localizar arquivo: {str(e)}")
            
    def handle_file_double_clicked(self, file_path):
        """Lida com duplo clique no arquivo"""
        try:
            self.file_manager.open_file_with_default_app(os.path.basename(file_path))
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir arquivo: {str(e)}")
            
    def show_about(self):
        """Mostra diálogo de informações sobre o programa"""
        QMessageBox.information(
            self,
            "Sobre",
            "Renomeador em Lote\n\n"
            "Versão: 1.0\n"
            "Desenvolvido por: Seu Nome\n"
            "Contato: seu.email@example.com"
        )
        
    def update_ui_text(self):
        # Atualiza os textos da barra de menus
        self.file_menu.setTitle(self.language_manager.get_text("file_menu"))
        self.about_menu.setTitle(self.language_manager.get_text("about_menu"))
        
        # Atualiza os textos das ações do menu Arquivo
        self.open_csv_action.setText(self.language_manager.get_text("open_csv"))
        self.open_folder_action.setText(self.language_manager.get_text("open_folder"))
        self.language_menu.setTitle(self.language_manager.get_text("language_menu"))
        self.english_action.setText(self.language_manager.get_text("english"))
        self.portuguese_action.setText(self.language_manager.get_text("portuguese"))
        self.spanish_action.setText(self.language_manager.get_text("spanish"))
        self.exit_action.setText(self.language_manager.get_text("exit"))
        
        # Atualiza os textos do menu Sobre
        self.about_action.setText(self.language_manager.get_text("about"))
        
        # Atualiza os textos dos botões
        self.csv_button.setText(self.language_manager.get_text("open_csv"))
        self.folder_button.setText(self.language_manager.get_text("open_folder"))
        self.reload_button.setText(self.language_manager.get_text("reload_files"))
        self.rename_button.setText(self.language_manager.get_text("rename_files"))
        self.undo_button.setText(self.language_manager.get_text("undo_rename"))
        
        # Atualiza os placeholders
        self.extensions_field.setPlaceholderText(self.language_manager.get_text("extensions"))
        self.csv_search_field.setPlaceholderText(self.language_manager.get_text("search"))
        self.files_search_field.setPlaceholderText(self.language_manager.get_text("search"))
        
        # Atualiza o título da janela
        self.setWindowTitle(self.language_manager.get_text("file_menu")) 