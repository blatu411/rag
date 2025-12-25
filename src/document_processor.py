"""
文档处理模块
支持 PDF、Word、TXT 等多种格式
"""
import os
from typing import List, Tuple
from pathlib import Path
from loguru import logger

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from docx import Document
except ImportError:
    Document = None

from langchain.text_splitter import RecursiveCharacterTextSplitter


class DocumentProcessor:
    """文档处理器"""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        """
        初始化文档处理器

        Args:
            chunk_size: 分块大小（字符数）
            chunk_overlap: 分块重叠（字符数）
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 创建文本分割器（中文友好）
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "，", " ", ""],  # 中文友好的分隔符
        )

        logger.info(f"DocumentProcessor initialized with chunk_size={chunk_size}, overlap={chunk_overlap}")

    def load_file(self, file_path: str) -> Tuple[str, dict]:
        """
        加载文件并提取文本

        Args:
            file_path: 文件路径

        Returns:
            (文本内容, 元数据字典)

        Raises:
            ValueError: 不支持的文件格式
            Exception: 文件读取失败
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = file_path.suffix.lower()
        logger.info(f"Loading file: {file_path}")

        try:
            if suffix == ".pdf":
                text, metadata = self._load_pdf(file_path)
            elif suffix in [".docx", ".doc"]:
                text, metadata = self._load_docx(file_path)
            elif suffix in [".txt", ".md"]:
                text, metadata = self._load_txt(file_path)
            else:
                raise ValueError(f"Unsupported file format: {suffix}")

            logger.info(f"File loaded successfully. Text length: {len(text)} characters")
            return text, metadata

        except Exception as e:
            logger.error(f"Error loading file {file_path}: {str(e)}")
            raise

    def _load_pdf(self, file_path: Path) -> Tuple[str, dict]:
        """加载 PDF 文件"""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 is not installed. Install it with: pip install PyPDF2")

        try:
            text_content = []
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)

                for page_num, page in enumerate(pdf_reader.pages):
                    text_content.append(page.extract_text())

            text = "\n".join(text_content)
            metadata = {
                "source": str(file_path),
                "format": "pdf",
                "pages": num_pages,
            }
            return text, metadata

        except Exception as e:
            logger.error(f"Error reading PDF: {str(e)}")
            raise

    def _load_docx(self, file_path: Path) -> Tuple[str, dict]:
        """加载 Word 文件"""
        if Document is None:
            raise ImportError("python-docx is not installed. Install it with: pip install python-docx")

        try:
            doc = Document(file_path)
            text_content = [paragraph.text for paragraph in doc.paragraphs]
            text = "\n".join(text_content)

            metadata = {
                "source": str(file_path),
                "format": "docx",
                "paragraphs": len(text_content),
            }
            return text, metadata

        except Exception as e:
            logger.error(f"Error reading DOCX: {str(e)}")
            raise

    def _load_txt(self, file_path: Path) -> Tuple[str, dict]:
        """加载文本文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            metadata = {
                "source": str(file_path),
                "format": "txt",
                "size": len(text),
            }
            return text, metadata

        except UnicodeDecodeError:
            # 尝试其他编码
            with open(file_path, "r", encoding="gbk") as f:
                text = f.read()

            metadata = {
                "source": str(file_path),
                "format": "txt",
                "size": len(text),
            }
            return text, metadata

        except Exception as e:
            logger.error(f"Error reading TXT: {str(e)}")
            raise

    def split_text(self, text: str) -> List[str]:
        """
        分割文本成小块

        Args:
            text: 输入文本

        Returns:
            分割后的文本块列表
        """
        if not text or not text.strip():
            logger.warning("Empty text provided")
            return []

        try:
            chunks = self.splitter.split_text(text)
            logger.info(f"Text split into {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Error splitting text: {str(e)}")
            raise

    def process_file(self, file_path: str) -> Tuple[List[str], dict]:
        """
        处理文件：加载 -> 分割

        Args:
            file_path: 文件路径

        Returns:
            (文本块列表, 元数据字典)
        """
        text, metadata = self.load_file(file_path)
        chunks = self.split_text(text)
        return chunks, metadata

    @staticmethod
    def get_supported_formats() -> List[str]:
        """获取支持的文件格式"""
        formats = [".txt", ".md"]

        if PyPDF2 is not None:
            formats.append(".pdf")

        if Document is not None:
            formats.extend([".docx", ".doc"])

        return formats
