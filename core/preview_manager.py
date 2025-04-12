import os
import fitz  # PyMuPDF
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class PreviewManager:
    def __init__(self):
        self.current_file_path = None

    def set_current_file(self, file_path):
        """Define o arquivo atual para visualização"""
        self.current_file_path = file_path

    def get_preview(self, max_width=800, max_height=600):
        """Retorna uma visualização do arquivo atual"""
        if not self.current_file_path or not os.path.exists(self.current_file_path):
            return None, "Arquivo não encontrado"

        file_ext = os.path.splitext(self.current_file_path)[1].lower()
        
        # Visualização de imagens
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        if file_ext in image_extensions:
            try:
                pixmap = QPixmap(self.current_file_path)
                if pixmap.isNull():
                    return None, "Falha ao carregar imagem"
                
                scaled_pixmap = pixmap.scaled(
                    max_width, 
                    max_height,
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                return scaled_pixmap, None
            except Exception as e:
                return None, f"Erro ao carregar imagem: {str(e)}"

        # Visualização de PDF
        if file_ext == '.pdf':
            try:
                pdf_document = fitz.open(self.current_file_path)
                if pdf_document.page_count > 0:
                    page = pdf_document[0]
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(img)
                    
                    scaled_pixmap = pixmap.scaled(
                        max_width, 
                        max_height,
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    
                    pdf_document.close()
                    return scaled_pixmap, f"PDF: Página 1 de {pdf_document.page_count}"
                else:
                    return None, "PDF vazio"
            except Exception as e:
                return None, f"Erro ao carregar PDF: {str(e)}"

        # Visualização de texto
        text_extensions = ['.txt', '.csv', '.json', '.xml', '.html', '.md', '.py', '.js', '.css', '.log', '.ini', '.cfg']
        if file_ext in text_extensions:
            try:
                with open(self.current_file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read(2000)
                    file_size = os.path.getsize(self.current_file_path)
                    if file_size > 2000:
                        content += f"\n\n[...] Arquivo truncado. Mostrando os primeiros 2000 de {file_size} caracteres."
                return content, None
            except Exception as e:
                return None, f"Erro ao carregar arquivo de texto: {str(e)}"

        return None, f"Visualização não disponível para arquivos {file_ext}" 