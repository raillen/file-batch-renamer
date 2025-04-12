import os
import subprocess
from PyQt5.QtWidgets import QMessageBox

class FileManager:
    def __init__(self):
        self.folder_path = ""
        self.folder_files = []

    def open_folder(self, folder_path):
        """Abre uma pasta e lista seus arquivos"""
        if folder_path:
            self.folder_path = folder_path
            self.load_folder_files()
            return True
        return False

    def get_extensions_list(self, extensions_text):
        """Converte texto de extensões em lista formatada"""
        if not extensions_text:
            return []
        
        extensions = [ext.strip() for ext in extensions_text.split(',')]
        return [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]

    def load_folder_files(self, extensions_text=""):
        """Carrega arquivos da pasta com filtro de extensões"""
        if not self.folder_path:
            return []
        
        extensions = self.get_extensions_list(extensions_text)
        self.folder_files = []
        
        try:
            all_files = os.listdir(self.folder_path)
            all_files.sort()
            
            for file_name in all_files:
                file_path = os.path.join(self.folder_path, file_name)
                if os.path.isfile(file_path):
                    if not extensions or any(file_name.lower().endswith(ext.lower()) for ext in extensions):
                        self.folder_files.append(file_name)
            
            return self.folder_files
        except Exception as e:
            raise Exception(f"Erro ao listar arquivos: {str(e)}")

    def rename_file(self, old_name, new_name):
        """Renomeia um arquivo"""
        if not self.folder_path:
            raise Exception("Nenhuma pasta selecionada")
        
        old_path = os.path.join(self.folder_path, old_name)
        new_path = os.path.join(self.folder_path, new_name)
        
        if not os.path.exists(old_path):
            raise Exception(f"Arquivo não encontrado: {old_name}")
        
        if os.path.exists(new_path):
            raise Exception(f"Já existe um arquivo com o nome: {new_name}")
        
        try:
            os.rename(old_path, new_path)
            # Atualiza o nome na lista de arquivos
            index = self.folder_files.index(old_name)
            self.folder_files[index] = new_name
            return True
        except Exception as e:
            raise Exception(f"Erro ao renomear arquivo: {str(e)}")

    def delete_file(self, file_name):
        """Deleta um arquivo"""
        if not self.folder_path:
            raise Exception("Nenhuma pasta selecionada")
        
        file_path = os.path.join(self.folder_path, file_name)
        
        if not os.path.exists(file_path):
            raise Exception(f"Arquivo não encontrado: {file_name}")
        
        try:
            os.remove(file_path)
            self.folder_files.remove(file_name)
            return True
        except Exception as e:
            raise Exception(f"Erro ao deletar arquivo: {str(e)}")

    def locate_file_in_explorer(self, file_name):
        """Abre o Explorer e seleciona o arquivo"""
        if not self.folder_path or not file_name:
            raise Exception("Nenhuma pasta ou arquivo selecionado")
            
        file_path = os.path.join(self.folder_path, file_name)
        
        if not os.path.exists(file_path):
            raise Exception(f"Arquivo não encontrado: {file_name}")
            
        try:
            file_path = os.path.normpath(file_path)
            cmd = f'explorer /select,"{file_path}"'
            subprocess.Popen(cmd, shell=True)
            return True
        except Exception as e:
            raise Exception(f"Erro ao abrir o Explorer: {str(e)}")

    def open_file_with_default_app(self, file_name):
        """Abre o arquivo com o aplicativo padrão"""
        if not self.folder_path or not file_name:
            raise Exception("Nenhuma pasta ou arquivo selecionado")
            
        file_path = os.path.join(self.folder_path, file_name)
        
        if not os.path.exists(file_path):
            raise Exception(f"Arquivo não encontrado: {file_name}")
            
        try:
            file_path = os.path.normpath(file_path)
            os.startfile(file_path)
            return True
        except Exception as e:
            raise Exception(f"Erro ao abrir o arquivo: {str(e)}") 