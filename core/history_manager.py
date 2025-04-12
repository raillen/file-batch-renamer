import json
import os
from datetime import datetime

class HistoryManager:
    def __init__(self, history_file):
        self.history_file = history_file
        self.rename_history = []
        self.load_rename_history()

    def load_rename_history(self):
        """Carrega o histórico de renomeações do arquivo"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.rename_history = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar histórico: {str(e)}")
            self.rename_history = []

    def save_rename_history(self):
        """Salva o histórico de renomeações no arquivo"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.rename_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar histórico: {str(e)}")

    def add_operation(self, folder_path, operations):
        """Adiciona uma nova operação ao histórico"""
        operation = {
            "timestamp": datetime.now().isoformat(),
            "folder_path": folder_path,
            "operations": operations
        }
        self.rename_history.append(operation)
        self.save_rename_history()

    def get_last_operation(self):
        """Retorna a última operação do histórico"""
        if self.rename_history:
            return self.rename_history[-1]
        return None

    def remove_last_operation(self):
        """Remove a última operação do histórico"""
        if self.rename_history:
            self.rename_history.pop()
            self.save_rename_history()
            return True
        return False

    def clear_history(self):
        """Limpa todo o histórico"""
        self.rename_history = []
        self.save_rename_history() 