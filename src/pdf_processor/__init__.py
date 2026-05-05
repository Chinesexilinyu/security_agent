"""
PDF论文处理器 - 对接Dify知识库
用于将网安科研PDF论文分割为高质量chunks并导出为Dify兼容格式
"""

from .pdf_extractor import PDFExtractor
from .chunker import SemanticChunker
from .metadata_manager import MetadataManager
from .output_manager import OutputManager
from .processor import PDFProcessor

__version__ = "1.0.0"
__all__ = [
    "PDFExtractor",
    "SemanticChunker", 
    "MetadataManager",
    "OutputManager",
    "PDFProcessor"
]
