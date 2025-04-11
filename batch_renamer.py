import sys
import os
import csv
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
                            QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, 
                            QHeaderView, QMessageBox, QMenu, QAction, QAbstractItemView,
                            QTableWidget, QTableWidgetItem, QToolButton, QScrollArea, QDialog, QInputDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QImage, QCursor
import subprocess
import fitz  # PyMuPDF

class BatchRenamer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.csv_file_path = ""
        self.folder_path = ""
        self.csv_data = []
        self.folder_files = []
        self.rename_history = []
        self.history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rename_history.json")
        self.current_tooltip = None  # Inicializa a variável como None
        self.load_rename_history()
        self.initUI()
        
    def load_rename_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.rename_history = json.load(f)
                    print(f"Loaded rename history: {len(self.rename_history)} operations")
        except Exception as e:
            print(f"Error loading rename history: {str(e)}")
            self.rename_history = []
    
    def save_rename_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.rename_history, f, ensure_ascii=False, indent=2)
                print(f"Saved rename history: {len(self.rename_history)} operations")
        except Exception as e:
            print(f"Error saving rename history: {str(e)}")
    
    def open_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.csv_file_path = file_path
            self.csv_path_label.setText(file_path)
            self.load_csv_data()
    
    def load_csv_data(self):
        self.csv_data = []
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if row and len(row) > 0:
                        self.csv_data.append(row[0])
            
            # Reset the search field when loading CSV
            if hasattr(self, 'csv_search_field'):
                self.csv_search_field.clear()
            
            self.update_csv_table()
            print(f"CSV data loaded: {self.csv_data}")  # Debug print
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reading CSV file: {str(e)}")
    
    def update_csv_table(self, names=None):
        """Update the CSV table with the given list of names"""
        if names is None:
            names = self.csv_data
        
        self.csv_table.setRowCount(0)
        for name in names:
            row_position = self.csv_table.rowCount()
            self.csv_table.insertRow(row_position)
            self.csv_table.setItem(row_position, 0, QTableWidgetItem(name))
    
    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder_path:
            self.folder_path = folder_path
            self.folder_path_label.setText(folder_path)
            self.load_folder_files()
    
    def get_extensions_list(self):
        extensions_text = self.extensions_field.text().strip()
        if not extensions_text:
            return []
        
        extensions = [ext.strip() for ext in extensions_text.split(',')]
        # Add dot if not present
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
        return extensions
    
    def load_folder_files(self):
        if not self.folder_path:
            return
        
        extensions = self.get_extensions_list()
        self.folder_files = []
        
        try:
            all_files = os.listdir(self.folder_path)
            all_files.sort()  # Sort alphabetically
            
            for file_name in all_files:
                file_path = os.path.join(self.folder_path, file_name)
                if os.path.isfile(file_path):
                    # If extensions list is empty, include all files
                    # Otherwise, only include files with matching extensions
                    if not extensions or any(file_name.lower().endswith(ext.lower()) for ext in extensions):
                        self.folder_files.append(file_name)
            
            # Reset the search field when loading files
            if hasattr(self, 'files_search_field'):
                self.files_search_field.clear()
            
            self.update_files_table()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao listar arquivos: {str(e)}")
    
    def update_files_table(self, files=None):
        """Update the files table with the given list of files"""
        if files is None:
            files = self.folder_files
        
        self.files_table.setRowCount(0)
        for file_name in files:
            row_position = self.files_table.rowCount()
            self.files_table.insertRow(row_position)
            item = QTableWidgetItem(file_name)
            # Store the original filename as user data for rename tracking
            item.setData(Qt.UserRole, file_name)
            self.files_table.setItem(row_position, 0, item)
    
    def reload_files(self):
        self.load_folder_files()
    
    def rename_files(self):
        if not self.csv_data:
            QMessageBox.warning(self, "Aviso", "Nenhum dado CSV carregado.")
            return
        
        if not self.folder_files:
            QMessageBox.warning(self, "Aviso", "Nenhum arquivo na pasta.")
            return
        
        # Check if CSV entries are fewer than files
        if len(self.csv_data) < len(self.folder_files):
            QMessageBox.warning(
                self, 
                "Aviso", 
                f"O número de nomes no CSV ({len(self.csv_data)}) é menor que o número de arquivos ({len(self.folder_files)})."
            )
        
        # Ask for confirmation
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
            # Prepare rename operations
            rename_operations = []
            successful_renames = 0
            failed_renames = 0
            error_details = []
            files_not_renamed = []
            renamed_files_data = []  # To store old and new filenames for CSV
            
            # Sort files to ensure consistent order
            files_to_rename = self.folder_files.copy()
            
            # Create a history entry
            operation_history = {
                "timestamp": "",  # Will be filled in when saving
                "folder_path": self.folder_path,
                "operations": []
            }
            
            # Only process up to the number of CSV entries
            for i, file_name in enumerate(files_to_rename):
                if i >= len(self.csv_data):
                    # Keep track of files that won't be renamed
                    files_not_renamed.append(file_name)
                    continue
                
                old_path = os.path.join(self.folder_path, file_name)
                file_ext = os.path.splitext(file_name)[1]
                new_name = f"{self.csv_data[i]}{file_ext}"
                new_path = os.path.join(self.folder_path, new_name)
                
                rename_operations.append((old_path, new_path, file_name, new_name))
                renamed_files_data.append([file_name, new_name])  # Add to CSV data
                operation_history["operations"].append({
                    "original_name": file_name,
                    "new_name": new_name
                })
            
            # Perform the rename operations
            for old_path, new_path, old_name, new_name in rename_operations:
                try:
                    print(f"Renaming: {old_path} -> {new_path}")  # Debug print
                    os.rename(old_path, new_path)
                    successful_renames += 1
                except Exception as e:
                    failed_renames += 1
                    error_msg = f"Erro ao renomear '{old_name}' para '{new_name}': {str(e)}"
                    print(error_msg)
                    error_details.append(error_msg)
            
            # Save the rename history
            if successful_renames > 0:
                self.rename_history.append(operation_history)
                self.save_rename_history()
                
                # Generate renamed_files.csv in the folder
                self.generate_renamed_files_csv(renamed_files_data)
            
            # Reload file list after renaming
            self.load_folder_files()
            
            # Create detailed message with errors if any
            result_message = f"Renomeação concluída.\nArquivos renomeados com sucesso: {successful_renames}\nFalhas: {failed_renames}"
            
            # Add information about files not renamed due to insufficient CSV entries
            if files_not_renamed:
                result_message += f"\n\nArquivos não renomeados (CSV insuficiente): {len(files_not_renamed)}"
                result_message += "\n\nArquivos que não foram renomeados:"
                for i, file_name in enumerate(files_not_renamed, 1):
                    if i <= 10:  # Limit to 10 files to avoid huge message box
                        result_message += f"\n{i}. {file_name}"
                
                if len(files_not_renamed) > 10:
                    result_message += f"\n... e mais {len(files_not_renamed) - 10} arquivos não exibidos."
            
            if error_details:
                result_message += "\n\nDetalhes das falhas:"
                for i, error in enumerate(error_details, 1):
                    if i <= 10:  # Limit to 10 errors to avoid huge message box
                        result_message += f"\n{i}. {error}"
                
                if len(error_details) > 10:
                    result_message += f"\n... e mais {len(error_details) - 10} erros não exibidos."
            
            QMessageBox.information(
                self, 
                "Concluído", 
                result_message
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro durante a renomeação: {str(e)}")
    
    def generate_renamed_files_csv(self, renamed_files_data):
        """Generate a CSV file with old and new filenames in the target folder"""
        if not self.folder_path or not renamed_files_data:
            return
            
        csv_path = os.path.join(self.folder_path, "renamed_files.csv")
        
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as file:
                csv_writer = csv.writer(file)
                # Write header
                csv_writer.writerow(["old_name", "new_name"])
                # Write data
                csv_writer.writerows(renamed_files_data)
                
            print(f"Generated renamed_files.csv with {len(renamed_files_data)} entries")
        except Exception as e:
            print(f"Error generating renamed_files.csv: {str(e)}")
    
    def undo_rename(self):
        if not self.rename_history:
            QMessageBox.information(self, "Informação", "Não há operações de renomeação para desfazer.")
            return
        
        # Get the last rename operation
        last_operation = self.rename_history[-1]
        folder_path = last_operation["folder_path"]
        
        # Check if the folder still exists
        if not os.path.exists(folder_path):
            QMessageBox.warning(self, "Aviso", f"A pasta original não existe mais: {folder_path}")
            return
        
        # Ask for confirmation
        reply = QMessageBox.question(
            self, 
            "Confirmar Desfazer", 
            f"Deseja desfazer a última operação de renomeação em:\n{folder_path}?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Perform the undo operations
        successful_undos = 0
        failed_undos = 0
        error_details = []
        
        for op in last_operation["operations"]:
            original_name = op["original_name"]
            new_name = op["new_name"]
            
            current_path = os.path.join(folder_path, new_name)
            original_path = os.path.join(folder_path, original_name)
            
            try:
                if os.path.exists(current_path):
                    print(f"Undoing rename: {current_path} -> {original_path}")
                    os.rename(current_path, original_path)
                    successful_undos += 1
                else:
                    error_msg = f"Arquivo não encontrado: '{new_name}'"
                    print(f"File not found for undo: {current_path}")
                    failed_undos += 1
                    error_details.append(error_msg)
            except Exception as e:
                failed_undos += 1
                error_msg = f"Erro ao desfazer renomeação de '{new_name}' para '{original_name}': {str(e)}"
                print(error_msg)
                error_details.append(error_msg)
        
        # Remove the operation from history if at least one undo was successful
        if successful_undos > 0:
            self.rename_history.pop()
            self.save_rename_history()
            
            # Delete the renamed_files.csv if it exists
            self.delete_renamed_files_csv(folder_path)
            
            # If the current folder is the same as the undo folder, reload the files
            if self.folder_path == folder_path:
                self.load_folder_files()
            
            # Create detailed message with errors if any
            result_message = f"Desfazer concluído.\nArquivos restaurados com sucesso: {successful_undos}\nFalhas: {failed_undos}"
            
            if error_details:
                result_message += "\n\nDetalhes das falhas:"
                for i, error in enumerate(error_details, 1):
                    if i <= 10:  # Limit to 10 errors to avoid huge message box
                        result_message += f"\n{i}. {error}"
                
                if len(error_details) > 10:
                    result_message += f"\n... e mais {len(error_details) - 10} erros não exibidos."
            
            QMessageBox.information(
                self, 
                "Concluído", 
                result_message
            )
        else:
            error_message = "Não foi possível desfazer nenhuma operação de renomeação."
            
            if error_details:
                error_message += "\n\nDetalhes das falhas:"
                for i, error in enumerate(error_details, 1):
                    if i <= 10:
                        error_message += f"\n{i}. {error}"
                
                if len(error_details) > 10:
                    error_message += f"\n... e mais {len(error_details) - 10} erros não exibidos."
            
            QMessageBox.warning(
                self, 
                "Aviso", 
                error_message
            )
    
    def delete_renamed_files_csv(self, folder_path):
        """Delete the renamed_files.csv file from the folder"""
        csv_path = os.path.join(folder_path, "renamed_files.csv")
        
        if os.path.exists(csv_path):
            try:
                os.remove(csv_path)
                print(f"Deleted renamed_files.csv")
            except Exception as e:
                print(f"Error deleting renamed_files.csv: {str(e)}")
    
    def center_on_screen(self):
        """Center the window on the screen"""
        screen_geometry = QApplication.desktop().availableGeometry()
        window_geometry = self.geometry()
        
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        
        self.move(x, y)

    def show_csv_context_menu(self, position):
        """Show context menu for CSV table"""
        menu = QMenu()
        remove_action = QAction("Remover", self)
        remove_action.triggered.connect(self.remove_selected_csv_row)
        menu.addAction(remove_action)
        
        # Show the menu at the cursor position
        menu.exec_(self.csv_table.mapToGlobal(position))

    def remove_selected_csv_row(self):
        """Remove the selected row from the CSV table"""
        selected_rows = self.csv_table.selectionModel().selectedRows()
        
        if not selected_rows:
            return
        
        # Sort rows in descending order to avoid index shifting when removing
        rows = sorted([index.row() for index in selected_rows], reverse=True)
        
        # Ask for confirmation if multiple rows are selected
        if len(rows) > 1:
            reply = QMessageBox.question(
                self, 
                "Confirmar Remoção", 
                f"Deseja remover {len(rows)} registros selecionados?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        # Remove rows from the table and from csv_data
        for row in rows:
            self.csv_table.removeRow(row)
            self.csv_data.pop(row)
        
        # If we have a CSV file path, update the CSV file
        if self.csv_file_path:
            try:
                with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as file:
                    csv_writer = csv.writer(file)
                    for name in self.csv_data:
                        csv_writer.writerow([name])
                
                print(f"CSV file updated: {len(self.csv_data)} entries")
            except Exception as e:
                QMessageBox.warning(self, "Aviso", f"Erro ao atualizar o arquivo CSV: {str(e)}")

    def csv_table_key_press(self, event):
        """Handle key press events in the CSV table"""
        # Check if Delete key was pressed
        if event.key() == Qt.Key_Delete:
            self.remove_selected_csv_row()
        else:
            # Call the original keyPressEvent method for other keys
            QTableWidget.keyPressEvent(self.csv_table, event)
    
    def move_csv_row_up(self):
        """Move the selected CSV row up"""
        current_row = self.csv_table.currentRow()
        
        # Check if a row is selected and it's not the first row
        if current_row > 0:
            # Get the data from the current row
            item = self.csv_table.item(current_row, 0)
            if not item:
                return
            
            current_data = item.text()
            
            # Swap in the csv_data list
            self.csv_data[current_row], self.csv_data[current_row - 1] = self.csv_data[current_row - 1], self.csv_data[current_row]
            
            # Update the table
            self.csv_table.item(current_row, 0).setText(self.csv_data[current_row])
            self.csv_table.item(current_row - 1, 0).setText(self.csv_data[current_row - 1])
            
            # Select the moved row
            self.csv_table.setCurrentCell(current_row - 1, 0)
            
            # Update the CSV file
            self.update_csv_file()
    
    def move_csv_row_down(self):
        """Move the selected CSV row down"""
        current_row = self.csv_table.currentRow()
        
        # Check if a row is selected and it's not the last row
        if current_row >= 0 and current_row < self.csv_table.rowCount() - 1:
            # Get the data from the current row
            item = self.csv_table.item(current_row, 0)
            if not item:
                return
            
            current_data = item.text()
            
            # Swap in the csv_data list
            self.csv_data[current_row], self.csv_data[current_row + 1] = self.csv_data[current_row + 1], self.csv_data[current_row]
            
            # Update the table
            self.csv_table.item(current_row, 0).setText(self.csv_data[current_row])
            self.csv_table.item(current_row + 1, 0).setText(self.csv_data[current_row + 1])
            
            # Select the moved row
            self.csv_table.setCurrentCell(current_row + 1, 0)
            
            # Update the CSV file
            self.update_csv_file()
    
    def move_file_row_up(self):
        """Move the selected file row up"""
        current_row = self.files_table.currentRow()
        
        # Check if a row is selected and it's not the first row
        if current_row > 0:
            # Get the data from the current row
            item = self.files_table.item(current_row, 0)
            if not item:
                return
            
            current_data = item.text()
            
            # Swap in the folder_files list
            self.folder_files[current_row], self.folder_files[current_row - 1] = self.folder_files[current_row - 1], self.folder_files[current_row]
            
            # Update the table
            self.files_table.item(current_row, 0).setText(self.folder_files[current_row])
            self.files_table.item(current_row - 1, 0).setText(self.folder_files[current_row - 1])
            
            # Select the moved row
            self.files_table.setCurrentCell(current_row - 1, 0)
    
    def move_file_row_down(self):
        """Move the selected file row down"""
        current_row = self.files_table.currentRow()
        
        # Check if a row is selected and it's not the last row
        if current_row >= 0 and current_row < self.files_table.rowCount() - 1:
            # Get the data from the current row
            item = self.files_table.item(current_row, 0)
            if not item:
                return
            
            current_data = item.text()
            
            # Swap in the folder_files list
            self.folder_files[current_row], self.folder_files[current_row + 1] = self.folder_files[current_row + 1], self.folder_files[current_row]
            
            # Update the table
            self.files_table.item(current_row, 0).setText(self.folder_files[current_row])
            self.files_table.item(current_row + 1, 0).setText(self.folder_files[current_row + 1])
            
            # Select the moved row
            self.files_table.setCurrentCell(current_row + 1, 0)
    
    def update_csv_file(self):
        """Update the CSV file with the current data"""
        if self.csv_file_path:
            try:
                with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as file:
                    csv_writer = csv.writer(file)
                    for name in self.csv_data:
                        csv_writer.writerow([name])
                
                print(f"CSV file updated: {len(self.csv_data)} entries")
            except Exception as e:
                print(f"Error updating CSV file: {str(e)}")

    def update_file_preview(self):
        """Update the file preview when a file is selected in the files table"""
        selected_rows = self.files_table.selectionModel().selectedRows()
        
        if not selected_rows or not self.folder_path:
            self.preview_label.setText("No file selected")
            self.preview_label.setProperty("current_file_path", None)
            return
        
        # Get the selected file name
        row = selected_rows[0].row()
        file_name = self.files_table.item(row, 0).text()
        file_path = os.path.join(self.folder_path, file_name)
        
        # Store the current file path as a property of the label for double-click handling
        self.preview_label.setProperty("current_file_path", file_path)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            self.preview_label.setText("File not found")
            return
        
        # Get file extension
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Image file preview
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        if file_ext in image_extensions:
            try:
                # Load the image and display it
                pixmap = QPixmap(file_path)
                
                if pixmap.isNull():
                    self.preview_label.setText("Failed to load image")
                    return
                
                # Scale the image to fit the preview area while maintaining aspect ratio
                preview_width = self.preview_scroll.width() - 20  # Subtract some padding
                preview_height = self.preview_scroll.height() - 20
                
                scaled_pixmap = pixmap.scaled(
                    preview_width, 
                    preview_height,
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                
                self.preview_label.setPixmap(scaled_pixmap)
                self.preview_label.setAlignment(Qt.AlignCenter)
                
            except Exception as e:
                self.preview_label.setText(f"Error loading image: {str(e)}")
            
            return
        
        # PDF file preview
        if file_ext == '.pdf':
            try:
                # Open the PDF file
                pdf_document = fitz.open(file_path)
                
                if pdf_document.page_count > 0:
                    # Get the first page
                    page = pdf_document[0]
                    
                    # Render the page to an image (with a reasonable resolution)
                    # Using a zoom factor of 2 for better quality
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    
                    # Convert the pixmap to a QImage
                    img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                    
                    # Convert QImage to QPixmap
                    pixmap = QPixmap.fromImage(img)
                    
                    # Scale the image to fit the preview area while maintaining aspect ratio
                    preview_width = self.preview_scroll.width() - 20
                    preview_height = self.preview_scroll.height() - 20
                    
                    scaled_pixmap = pixmap.scaled(
                        preview_width, 
                        preview_height,
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    
                    # Display the image
                    self.preview_label.setPixmap(scaled_pixmap)
                    self.preview_label.setAlignment(Qt.AlignCenter)
                    
                    # Add page info
                    page_info = f"PDF: Page 1 of {pdf_document.page_count}"
                    self.preview_label.setToolTip(page_info)
                    
                    # Close the document
                    pdf_document.close()
                else:
                    self.preview_label.setText("Empty PDF document")
            except Exception as e:
                self.preview_label.setText(f"Error loading PDF: {str(e)}")
                print(f"PDF preview error: {str(e)}")
            
            return
        
        # Text file preview
        text_extensions = ['.txt', '.csv', '.json', '.xml', '.html', '.md', '.py', '.js', '.css', '.log', '.ini', '.cfg']
        if file_ext in text_extensions:
            try:
                # Try to read the file content
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    # Read first 2000 characters to avoid loading very large files
                    content = f.read(2000)
                    
                # If the file is larger than 2000 chars, add an indicator
                file_size = os.path.getsize(file_path)
                if file_size > 2000:
                    content += f"\n\n[...] File truncated. Showing first 2000 of {file_size} characters."
                
                # Clear any existing pixmap
                self.preview_label.clear()
                
                # Set text content with proper formatting
                self.preview_label.setText(content)
                self.preview_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                self.preview_label.setWordWrap(True)
                self.preview_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; font-family: monospace;")
                
            except Exception as e:
                self.preview_label.setText(f"Error loading text file: {str(e)}")
            
            return
        
        # For other file types
        self.preview_label.clear()
        self.preview_label.setText(f"Preview not available for {file_ext} files")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #f0f0f0;")
    
    def show_files_context_menu(self, position):
        """Show context menu for files table"""
        selected_rows = self.files_table.selectionModel().selectedRows()
        
        if not selected_rows:
            return
            
        # Get the selected file name
        row = selected_rows[0].row()
        file_name = self.files_table.item(row, 0).text()
        
        menu = QMenu()
        
        # Locate file action
        locate_action = QAction("Localizar arquivo na pasta", self)
        locate_action.triggered.connect(lambda: self.locate_file_in_explorer(file_name))
        menu.addAction(locate_action)
        
        # Delete file action
        delete_action = QAction("Deletar arquivo", self)
        delete_action.triggered.connect(lambda: self.delete_selected_file(file_name))
        menu.addAction(delete_action)
        
        # Rename file action
        rename_action = QAction("Renomear arquivo", self)
        rename_action.triggered.connect(lambda: self.rename_file_from_context_menu(row))
        menu.addAction(rename_action)
        
        # Show the menu at the cursor position
        menu.exec_(self.files_table.mapToGlobal(position))

    def rename_file_from_context_menu(self, row):
        """Rename a file using the context menu by enabling table editing"""
        # Ensure we have a folder path
        if not self.folder_path:
            QMessageBox.warning(self, "Aviso", "Nenhuma pasta selecionada.")
            return
        
        # Get the current item
        item = self.files_table.item(row, 0)
        
        # Select the row and set focus to enable editing
        self.files_table.clearSelection()
        self.files_table.selectRow(row)
        self.files_table.setFocus()
        
        # Start editing the item
        self.files_table.editItem(item)
    
    def delete_selected_file(self, file_name):
        """Delete the selected file with confirmation"""
        # Ensure we have a folder path
        if not self.folder_path:
            QMessageBox.warning(self, "Aviso", "Nenhuma pasta selecionada.")
            return
        
        # Construct full file path
        file_path = os.path.join(self.folder_path, file_name)
        
        # Confirmation popup
        reply = QMessageBox.question(
            self, 
            "Confirmar Exclusão", 
            f"Tem certeza que deseja deletar o arquivo '{file_name}' da pasta '{self.folder_path}'?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        # Proceed with deletion if confirmed
        if reply == QMessageBox.Yes:
            try:
                # Delete the file
                os.remove(file_path)
                
                # Remove from files table and folder_files list
                current_row = self.files_table.currentRow()
                self.files_table.removeRow(current_row)
                self.folder_files.remove(file_name)
                
                # Optional: Show success message
                QMessageBox.information(self, "Sucesso", f"Arquivo '{file_name}' deletado com sucesso.")
                
                # Update preview to clear it
                self.preview_label.clear()
                self.preview_label.setText("No file selected")
                self.preview_label.setProperty("current_file_path", None)
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao deletar o arquivo: {str(e)}")
    
    def locate_file_in_explorer(self, file_name):
        """Open Windows Explorer and select the file"""
        if not self.folder_path or not file_name:
            return
            
        file_path = os.path.join(self.folder_path, file_name)
        
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Aviso", f"O arquivo não foi encontrado: {file_name}")
            return
            
        try:
            # Make sure paths are properly formatted
            file_path = os.path.normpath(file_path)
            
            # Use the Windows shell command to open Explorer and select the file
            # The /select flag tells Explorer to select the specified file
            cmd = f'explorer /select,"{file_path}"'
            subprocess.Popen(cmd, shell=True)
            print(f"Opening Explorer for file: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir o Explorer: {str(e)}")

    def open_file_with_default_app(self, file_path):
        """Open a file with its default associated application"""
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Aviso", "Arquivo não encontrado.")
            return
            
        try:
            # Use the appropriate command to open the file with its default application
            # On Windows, we can use 'start' command
            file_path = os.path.normpath(file_path)
            os.startfile(file_path)
            print(f"Opening file with default application: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir o arquivo: {str(e)}")
    
    def preview_mouse_press_event(self, event):
        """Handle mouse press events on the preview label"""
        # Call the parent class's mousePressEvent to maintain default behavior
        QLabel.mousePressEvent(self.preview_label, event)
    
    def preview_double_click_event(self, event):
        """Handle double-click events on the preview label"""
        # Get the current file path from the label's property
        file_path = self.preview_label.property("current_file_path")
        
        if file_path and os.path.exists(file_path):
            self.open_file_with_default_app(file_path)
        
        # Call the parent class's mouseDoubleClickEvent
        QLabel.mouseDoubleClickEvent(self.preview_label, event)

    def filter_files(self, text):
        """Filter files based on the search text"""
        filtered_files = [file for file in self.folder_files if text.lower() in file.lower()]
        self.update_files_table(filtered_files)

    def update_files_table(self, files=None):
        """Update the files table with the given list of files"""
        if files is None:
            files = self.folder_files
        
        self.files_table.setRowCount(0)
        for file_name in files:
            row_position = self.files_table.rowCount()
            self.files_table.insertRow(row_position)
            item = QTableWidgetItem(file_name)
            # Store the original filename as user data for rename tracking
            item.setData(Qt.UserRole, file_name)
            self.files_table.setItem(row_position, 0, item)

    def filter_csv(self, text):
        """Filter CSV entries based on the search text"""
        filtered_csv = [name for name in self.csv_data if text.lower() in name.lower()]
        self.update_csv_table(filtered_csv)

    def update_csv_table(self, names=None):
        """Update the CSV table with the given list of names"""
        if names is None:
            names = self.csv_data
        
        self.csv_table.setRowCount(0)
        for name in names:
            row_position = self.csv_table.rowCount()
            self.csv_table.insertRow(row_position)
            self.csv_table.setItem(row_position, 0, QTableWidgetItem(name))

    def create_menu_bar(self):
        """Create the main menu bar for the application"""
        # Create menu bar
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("&File")
        
        # Open CSV Action
        open_csv_action = QAction("Open CSV", self)
        open_csv_action.triggered.connect(self.open_csv)
        file_menu.addAction(open_csv_action)
        
        # Open Folder Action
        open_folder_action = QAction("Open Folder", self)
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        # Exit Action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # About Menu
        about_menu = menu_bar.addMenu("&About")
        
        # Donate Action
        donate_action = QAction("Donate", self)
        donate_action.triggered.connect(self.show_donate_dialog)
        about_menu.addAction(donate_action)
    
    def show_donate_dialog(self):
        """Show a donation dialog with placeholder information"""
        # Create a dialog that is 50% the size of the main window
        dialog = QDialog(self)
        dialog.setWindowTitle("Donate")
        
        # Calculate 50% of the main window's size
        main_window_size = self.size()
        dialog_width = main_window_size.width() // 2
        dialog_height = main_window_size.height() // 2
        dialog.resize(dialog_width, dialog_height)
        
        # Create layout for the dialog
        layout = QVBoxLayout()
        
        # Donation information placeholders
        title_label = QLabel("<h2>Support Our Project</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        
        # PayPal Donation Section
        paypal_label = QLabel("PayPal Donation")
        paypal_label.setStyleSheet("font-weight: bold;")
        paypal_info = QLabel("PayPal Email: placeholder@example.com")
        
        # PIX QR Code Section
        pix_label = QLabel("PIX Donation")
        pix_label.setStyleSheet("font-weight: bold;")
        pix_info = QLabel("PIX Key: placeholder-pix-key")
        
        # Placeholder for QR Code (can be replaced with actual QR code later)
        qr_placeholder = QLabel("QR Code Placeholder")
        qr_placeholder.setStyleSheet("border: 1px solid black; min-height: 200px;")
        qr_placeholder.setAlignment(Qt.AlignCenter)
        
        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addWidget(paypal_label)
        layout.addWidget(paypal_info)
        layout.addWidget(pix_label)
        layout.addWidget(pix_info)
        layout.addWidget(qr_placeholder)
        
        # Add a close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)
        
        # Set the layout
        dialog.setLayout(layout)
        
        # Show the dialog
        dialog.exec_()

    def initUI(self):
        self.setWindowTitle("Batch File Renamer")
        self.setGeometry(100, 100, 900, 600)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Center the window on the screen
        self.center_on_screen()
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # CSV Button
        self.csv_button = QPushButton("Open CSV")
        self.csv_button.setMinimumHeight(50)
        self.csv_button.clicked.connect(self.open_csv)
        left_layout.addWidget(self.csv_button)
        
        # Folder Button
        self.folder_button = QPushButton("Open Folder")
        self.folder_button.setMinimumHeight(50)
        self.folder_button.clicked.connect(self.open_folder)
        left_layout.addWidget(self.folder_button)
        
        # Extensions Field
        self.extensions_label = QLabel("Filter files on folder by extensions")
        self.extensions_field = QLineEdit()
        self.extensions_field.setPlaceholderText("Extensions separated by comma (jpg,png,pdf)")
        
        # Reload Button
        self.reload_button = QPushButton("Reload Files")
        self.reload_button.clicked.connect(self.reload_files)
        
        left_layout.addWidget(self.extensions_label)
        left_layout.addWidget(self.extensions_field)
        left_layout.addWidget(self.reload_button)
        
        # File Preview Section
        preview_label = QLabel("File Preview")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_label.setStyleSheet("background-color: #888888; color: white; padding: 5px;")
        left_layout.addWidget(preview_label)
        
        # Create a scroll area for the image preview
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setMinimumHeight(200)
        self.preview_scroll.setMaximumHeight(300)
        
        # Create a label for the image preview
        self.preview_label = QLabel("No image selected")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #f0f0f0;")
        # Enable mouse tracking for the preview label to handle double-clicks
        self.preview_label.setMouseTracking(True)
        # Make the label accept mouse events
        self.preview_label.mousePressEvent = self.preview_mouse_press_event
        self.preview_label.mouseDoubleClickEvent = self.preview_double_click_event
        self.preview_scroll.setWidget(self.preview_label)
        
        left_layout.addWidget(self.preview_scroll)
        left_layout.addStretch()
        
        # Rename Button
        self.rename_button = QPushButton("Rename Files")
        self.rename_button.setMinimumHeight(50)
        self.rename_button.clicked.connect(self.rename_files)
        left_layout.addWidget(self.rename_button)
        
        # Undo Button
        self.undo_button = QPushButton("Undo Rename")
        self.undo_button.setMinimumHeight(50)
        self.undo_button.clicked.connect(self.undo_rename)
        left_layout.addWidget(self.undo_button)
        
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(200)
        
        # Middle panel (CSV)
        middle_panel = QWidget()
        middle_layout = QVBoxLayout()
        
        middle_title = QLabel("CSV Records")
        middle_title.setAlignment(Qt.AlignCenter)
        middle_title.setStyleSheet("background-color: #ff5555; color: white; padding: 10px;")
        middle_title.setFont(QFont("Arial", 12))
        
        # Create a layout for the CSV table and arrow buttons
        csv_table_layout = QHBoxLayout()
        
        # Up/Down arrow buttons for CSV
        csv_arrows_layout = QVBoxLayout()
        
        # Add spacer at the top to push buttons toward center
        csv_arrows_layout.addStretch(1)
        
        # Up arrow button
        self.csv_up_button = QToolButton()
        self.csv_up_button.setText("▲")
        self.csv_up_button.setToolTip("Move selected row up")
        self.csv_up_button.clicked.connect(self.move_csv_row_up)
        csv_arrows_layout.addWidget(self.csv_up_button)
        
        # Add small spacer between buttons
        csv_arrows_layout.addSpacing(10)
        
        # Down arrow button
        self.csv_down_button = QToolButton()
        self.csv_down_button.setText("▼")
        self.csv_down_button.setToolTip("Move selected row down")
        self.csv_down_button.clicked.connect(self.move_csv_row_down)
        csv_arrows_layout.addWidget(self.csv_down_button)
        
        # Add spacer at the bottom to push buttons toward center
        csv_arrows_layout.addStretch(1)
        
        # Create a table for CSV
        self.csv_table = QTableWidget(0, 1)
        self.csv_table.setHorizontalHeaderLabels(["New Names"])
        self.csv_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.csv_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.csv_table.customContextMenuRequested.connect(self.show_csv_context_menu)
        self.csv_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.csv_table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Handle delete key for CSV table
        self.csv_table.keyPressEvent = self.csv_table_key_press
        
        # Add table and arrows to layout
        csv_table_layout.addWidget(self.csv_table)
        csv_table_layout.addLayout(csv_arrows_layout)
        
        # Create a search field for CSV
        self.csv_search_field = QLineEdit()
        self.csv_search_field.setPlaceholderText("Search CSV...")
        self.csv_search_field.textChanged.connect(self.filter_csv)
        
        self.csv_path_label = QLabel("CSV directory")
        self.csv_path_label.setAlignment(Qt.AlignCenter)
        self.csv_path_label.setStyleSheet("background-color: #888888; color: white; padding: 5px;")
        
        middle_layout.addWidget(middle_title)
        middle_layout.addWidget(self.csv_search_field)
        middle_layout.addLayout(csv_table_layout)
        middle_layout.addWidget(self.csv_path_label)
        
        middle_panel.setLayout(middle_layout)
        
        # Right panel (Files)
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        right_title = QLabel("Files in Folder")
        right_title.setAlignment(Qt.AlignCenter)
        right_title.setStyleSheet("background-color: #ff9999; color: white; padding: 10px;")
        right_title.setFont(QFont("Arial", 12))
        
        # Create a search field for files
        self.files_search_field = QLineEdit()
        self.files_search_field.setPlaceholderText("Search files...")
        self.files_search_field.textChanged.connect(self.filter_files)
        
        # Create file action buttons
        self.locate_file_button = QPushButton("Localizar arquivo na pasta")
        self.locate_file_button.clicked.connect(self.locate_selected_file)
        
        self.delete_file_button = QPushButton("Deletar arquivo")
        self.delete_file_button.clicked.connect(self.delete_selected_file_button)
        
        self.rename_file_button = QPushButton("Renomear arquivo")
        self.rename_file_button.clicked.connect(self.rename_selected_file)
        
        # Create a horizontal layout for file action buttons
        file_actions_layout = QHBoxLayout()
        file_actions_layout.addWidget(self.locate_file_button)
        file_actions_layout.addWidget(self.delete_file_button)
        file_actions_layout.addWidget(self.rename_file_button)
        
        # Create a layout for the title, search field, and file actions
        files_title_search_layout = QVBoxLayout()
        files_title_search_layout.addWidget(right_title)
        files_title_search_layout.addWidget(self.files_search_field)
        files_title_search_layout.addLayout(file_actions_layout)
        
        # Create a layout for the files table and arrow buttons
        files_table_layout = QHBoxLayout()
        
        # Up/Down arrow buttons for files
        files_arrows_layout = QVBoxLayout()
        
        # Add spacer at the top to push buttons toward center
        files_arrows_layout.addStretch(1)
        
        # Up arrow button
        self.files_up_button = QToolButton()
        self.files_up_button.setText("▲")
        self.files_up_button.setToolTip("Move selected file up")
        self.files_up_button.clicked.connect(self.move_file_row_up)
        files_arrows_layout.addWidget(self.files_up_button)
        
        # Add small spacer between buttons
        files_arrows_layout.addSpacing(10)
        
        # Down arrow button
        self.files_down_button = QToolButton()
        self.files_down_button.setText("▼")
        self.files_down_button.setToolTip("Move selected file down")
        self.files_down_button.clicked.connect(self.move_file_row_down)
        files_arrows_layout.addWidget(self.files_down_button)
        
        # Add spacer at the bottom to push buttons toward center
        files_arrows_layout.addStretch(1)
        
        # Create a table for files
        self.files_table = QTableWidget(0, 1)
        self.files_table.setHorizontalHeaderLabels(["Files in Folder"])
        self.files_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.files_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.files_table.customContextMenuRequested.connect(self.show_files_context_menu)
        self.files_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.files_table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Enable editing of files table
        self.files_table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        
        # Connect itemChanged signal to handle renaming
        self.files_table.itemChanged.connect(self.handle_file_rename)
        
        # Connect selection change in files table to preview
        self.files_table.itemSelectionChanged.connect(self.update_file_preview)
        
        # Connect mouse events for image preview tooltip
        self.files_table.setMouseTracking(True)
        self.files_table.enterEvent = self.handle_enter_event
        self.files_table.leaveEvent = self.handle_leave_event
        self.files_table.mouseMoveEvent = self.handle_mouse_move
        
        # Add table and arrows to layout
        files_table_layout.addWidget(self.files_table)
        files_table_layout.addLayout(files_arrows_layout)
        
        # Add title, search, and table layout to right layout
        right_layout.addLayout(files_title_search_layout)
        right_layout.addLayout(files_table_layout)
        
        self.folder_path_label = QLabel("Folder directory")
        self.folder_path_label.setAlignment(Qt.AlignCenter)
        self.folder_path_label.setStyleSheet("background-color: #888888; color: white; padding: 5px;")
        
        right_layout.addWidget(self.folder_path_label)
        
        right_panel.setLayout(right_layout)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(middle_panel)
        main_layout.addWidget(right_panel)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def locate_selected_file(self):
        """Locate the selected file in Explorer"""
        # Ensure a row is selected
        selected_rows = self.files_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo primeiro.")
            return
        
        # Get the selected file name
        row = selected_rows[0].row()
        file_name = self.files_table.item(row, 0).text()
        
        # Call existing method to locate file
        self.locate_file_in_explorer(file_name)
    
    def delete_selected_file_button(self):
        """Delete the selected file when delete button is clicked"""
        # Ensure a row is selected
        selected_rows = self.files_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo primeiro.")
            return
        
        # Get the selected file name
        row = selected_rows[0].row()
        file_name = self.files_table.item(row, 0).text()
        
        # Call existing method to delete file
        self.delete_selected_file(file_name)
    
    def rename_selected_file(self):
        """Rename the selected file when rename button is clicked"""
        # Ensure a row is selected
        selected_rows = self.files_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo primeiro.")
            return
        
        # Get the selected row
        row = selected_rows[0].row()
        
        # Call existing method to rename file
        self.rename_file_from_context_menu(row)

    def handle_file_rename(self, item):
        """Handle renaming a file directly in the files table"""
        # Prevent unnecessary checks during initial table population
        if not hasattr(self, 'folder_path') or not self.folder_path:
            return
        
        # Get the new filename
        new_file_name = item.text().strip()
        
        # Validate the new filename
        if not new_file_name:
            QMessageBox.warning(self, "Aviso", "Nome de arquivo inválido.")
            # Revert to the original filename
            item.setText(item.data(Qt.UserRole))
            return
        
        # Get the original filename (stored as user data)
        original_file_name = item.data(Qt.UserRole)
        
        # Skip if the filename hasn't actually changed
        if new_file_name == original_file_name:
            return
        
        # Ensure we have a folder path
        if not self.folder_path:
            QMessageBox.warning(self, "Aviso", "Nenhuma pasta selecionada.")
            # Revert to the original filename
            item.setText(original_file_name)
            return
        
        # Construct full file paths
        old_file_path = os.path.join(self.folder_path, original_file_name)
        new_file_path = os.path.join(self.folder_path, new_file_name)
        
        # Check if the new filename already exists
        if os.path.exists(new_file_path):
            QMessageBox.warning(self, "Aviso", f"Já existe um arquivo com o nome '{new_file_name}'.")
            # Revert to the original filename
            item.setText(original_file_name)
            return
        
        # Confirmation popup
        reply = QMessageBox.question(
            self, 
            "Confirmar Renomeação", 
            f"Tem certeza que deseja renomear o arquivo '{original_file_name}' para '{new_file_name}'?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        # Proceed with renaming if confirmed
        if reply == QMessageBox.Yes:
            try:
                # Rename the file
                os.rename(old_file_path, new_file_path)
                
                # Update the folder_files list
                index = self.folder_files.index(original_file_name)
                self.folder_files[index] = new_file_name
                
                # Store the new filename as user data for future reference
                item.setData(Qt.UserRole, new_file_name)
                
                # Show success message
                QMessageBox.information(self, "Sucesso", f"Arquivo renomeado de '{original_file_name}' para '{new_file_name}'.")
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao renomear o arquivo: {str(e)}")
                # Revert to the original filename
                item.setText(original_file_name)
        else:
            # User cancelled, revert to the original filename
            item.setText(original_file_name)

    def handle_enter_event(self, event):
        """Handle mouse enter event to show image preview tooltip"""
        # Get the item under the mouse cursor
        item = self.files_table.itemAt(self.files_table.mapFromGlobal(QCursor.pos()))
        self.show_tooltip_for_item(item)

    def handle_mouse_move(self, event):
        """Handle mouse move event to update tooltip position"""
        # Get the item under the mouse cursor
        item = self.files_table.itemAt(event.pos())
        self.show_tooltip_for_item(item)

    def show_tooltip_for_item(self, item):
        """Show tooltip for the given item"""
        if item is None:
            self.hide_current_tooltip()
            return
            
        # Get the file name
        file_name = item.text()
        
        # Check if the file is an image
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        file_ext = os.path.splitext(file_name)[1].lower()
        
        if file_ext in image_extensions and self.folder_path:
            # Construct the full file path
            file_path = os.path.join(self.folder_path, file_name)
            
            if os.path.exists(file_path):
                try:
                    # Hide current tooltip before creating a new one
                    self.hide_current_tooltip()
                    
                    # Load the image
                    pixmap = QPixmap(file_path)
                    
                    if not pixmap.isNull():
                        # Scale the image to a reasonable size for the tooltip
                        scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        
                        # Create a tooltip with the image
                        tooltip = QLabel()
                        tooltip.setPixmap(scaled_pixmap)
                        tooltip.setWindowFlags(Qt.ToolTip)
                        
                        # Get the global position of the mouse cursor
                        global_pos = QCursor.pos()
                        
                        # Show the tooltip slightly offset from the cursor
                        tooltip.move(global_pos.x() + 20, global_pos.y() + 20)
                        tooltip.show()
                        
                        # Store the tooltip to hide it later
                        self.current_tooltip = tooltip
                except Exception as e:
                    print(f"Error showing image preview: {str(e)}")
                    self.hide_current_tooltip()
        else:
            self.hide_current_tooltip()

    def hide_current_tooltip(self):
        """Safely hide and clean up the current tooltip"""
        try:
            if self.current_tooltip is not None:
                self.current_tooltip.hide()
                self.current_tooltip.deleteLater()
                self.current_tooltip = None
        except Exception as e:
            print(f"Error hiding tooltip: {str(e)}")
            self.current_tooltip = None

    def handle_leave_event(self, event):
        """Handle mouse leave event to hide the tooltip"""
        self.hide_current_tooltip()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BatchRenamer()
    window.show()
    sys.exit(app.exec_())
