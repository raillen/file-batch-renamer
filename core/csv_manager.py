import csv
import os

class CSVManager:
    def __init__(self):
        self.csv_file_path = ""
        self.csv_data = []

    def open_csv(self, file_path):
        """'Abre um arquivo CSV e carrega seus dados"""
        if file_path:
            self.csv_file_path = file_path
            self.load_csv_data()
            return True
        return False

    def load_csv_data(self):
        """Carrega dados do arquivo CSV"""
        self.csv_data = []
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if row and len(row) > 0:
                        self.csv_data.append(row[0])
            return self.csv_data
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo CSV: {str(e)}")

    def update_csv_file(self):
        """Atualiza o arquivo CSV com os dados atuais"""
        if not self.csv_file_path:
            raise Exception("Nenhum arquivo CSV selecionado")
        
        try:
            with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as file:
                csv_writer = csv.writer(file)
                for name in self.csv_data:
                    csv_writer.writerow([name])
            return True
        except Exception as e:
            raise Exception(f"Erro ao atualizar arquivo CSV: {str(e)}")

    def remove_row(self, row_index):
        """Remove uma linha do CSV"""
        if 0 <= row_index < len(self.csv_data):
            self.csv_data.pop(row_index)
            return True
        return False

    def move_row(self, current_index, new_index):
        """Move uma linha do CSV para uma nova posição"""
        if (0 <= current_index < len(self.csv_data) and 
            0 <= new_index < len(self.csv_data)):
            item = self.csv_data.pop(current_index)
            self.csv_data.insert(new_index, item)
            return True
        return False

    def filter_data(self, search_text):
        """Filtra os dados do CSV baseado no texto de busca"""
        if not search_text:
            return self.csv_data
        return [name for name in self.csv_data if search_text.lower() in name.lower()] 