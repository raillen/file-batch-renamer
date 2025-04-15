from PyQt5.QtCore import QObject, pyqtSignal

class LanguageManager(QObject):
    language_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_language = "en"
        self.translations = {
            "en": {
                "file_menu": "File",
                "open_csv": "Open CSV",
                "open_folder": "Open Folder",
                "exit": "Exit",
                "language_menu": "Language",
                "english": "English",
                "portuguese": "Portuguese",
                "spanish": "Spanish",
                "about_menu": "About",
                "about": "About",
                "reload_files": "Reload Files",
                "rename_files": "Rename Files",
                "undo_rename": "Undo Rename",
                "extensions": "Extensions (comma separated)",
                "search": "Search...",
                "preview": "Preview",
                "no_file_selected": "No file selected",
                "preview_not_available": "Preview not available for this file type",
                "file_not_found": "File not found",
                "error": "Error",
                "success": "Success",
                "confirm": "Confirm",
                "cancel": "Cancel",
                "are_you_sure": "Are you sure you want to rename these files?",
                "rename_complete": "Files renamed successfully",
                "undo_complete": "Last rename operation undone",
                "no_history": "No history to undo",
                "csv_loaded": "CSV file loaded successfully",
                "folder_loaded": "Folder loaded successfully",
                "invalid_csv": "Invalid CSV file",
                "invalid_folder": "Invalid folder",
                "about_text": "Batch File Renamer\n\nVersion 1.0\n\nA simple application to rename files in batch using a CSV file."
            },
            "pt": {
                "file_menu": "Arquivo",
                "open_csv": "Abrir CSV",
                "open_folder": "Abrir Pasta",
                "exit": "Sair",
                "language_menu": "Idioma",
                "english": "Inglês",
                "portuguese": "Português",
                "spanish": "Espanhol",
                "about_menu": "Sobre",
                "about": "Sobre",
                "reload_files": "Recarregar Arquivos",
                "rename_files": "Renomear Arquivos",
                "undo_rename": "Desfazer Renomeação",
                "extensions": "Extensões (separadas por vírgula)",
                "search": "Buscar...",
                "preview": "Visualização",
                "no_file_selected": "Nenhum arquivo selecionado",
                "preview_not_available": "Visualização não disponível para este tipo de arquivo",
                "file_not_found": "Arquivo não encontrado",
                "error": "Erro",
                "success": "Sucesso",
                "confirm": "Confirmar",
                "cancel": "Cancelar",
                "are_you_sure": "Tem certeza que deseja renomear estes arquivos?",
                "rename_complete": "Arquivos renomeados com sucesso",
                "undo_complete": "Última operação de renomeação desfeita",
                "no_history": "Nenhum histórico para desfazer",
                "csv_loaded": "Arquivo CSV carregado com sucesso",
                "folder_loaded": "Pasta carregada com sucesso",
                "invalid_csv": "Arquivo CSV inválido",
                "invalid_folder": "Pasta inválida",
                "about_text": "Renomeador em Lote\n\nVersão 1.0\n\nUm aplicativo simples para renomear arquivos em lote usando um arquivo CSV."
            },
            "es": {
                "file_menu": "Archivo",
                "open_csv": "Abrir CSV",
                "open_folder": "Abrir Carpeta",
                "exit": "Salir",
                "language_menu": "Idioma",
                "english": "Inglés",
                "portuguese": "Portugués",
                "spanish": "Español",
                "about_menu": "Acerca de",
                "about": "Acerca de",
                "reload_files": "Recargar Archivos",
                "rename_files": "Renombrar Archivos",
                "undo_rename": "Deshacer Renombrado",
                "extensions": "Extensiones (separadas por coma)",
                "search": "Buscar...",
                "preview": "Vista Previa",
                "no_file_selected": "Ningún archivo seleccionado",
                "preview_not_available": "Vista previa no disponible para este tipo de archivo",
                "file_not_found": "Archivo no encontrado",
                "error": "Error",
                "success": "Éxito",
                "confirm": "Confirmar",
                "cancel": "Cancelar",
                "are_you_sure": "¿Está seguro de que desea renombrar estos archivos?",
                "rename_complete": "Archivos renombrados exitosamente",
                "undo_complete": "Última operación de renombrado deshecha",
                "no_history": "No hay historial para deshacer",
                "csv_loaded": "Archivo CSV cargado exitosamente",
                "folder_loaded": "Carpeta cargada exitosamente",
                "invalid_csv": "Archivo CSV inválido",
                "invalid_folder": "Carpeta inválida",
                "about_text": "Renombrador por Lotes\n\nVersión 1.0\n\nUna aplicación simple para renombrar archivos por lotes usando un archivo CSV."
            }
        }
    
    def set_language(self, language_code):
        if language_code in self.translations:
            self.current_language = language_code
            self.language_changed.emit(language_code)
    
    def get_text(self, key):
        return self.translations[self.current_language].get(key, key)
    
    def get_available_languages(self):
        return list(self.translations.keys()) 