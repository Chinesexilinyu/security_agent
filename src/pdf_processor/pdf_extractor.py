"""
PDF文本提取模块
使用PyMuPDF（fitz）提取PDF文本内容
"""

import os
import re
from typing import Dict, List, Tuple
import fitz  # PyMuPDF


class PDFExtractor:
    """PDF文本提取器"""

    def __init__(self, config: Dict = None):
        """
        初始化PDF提取器

        Args:
            config: 清洗配置
        """
        self.config = config or {}
        self.remove_page_numbers = self.config.get("remove_page_numbers", True)
        self.remove_headers_footers = self.config.get("remove_headers_footers", True)
        self.normalize_whitespace = self.config.get("normalize_whitespace", True)
        self.min_paragraph_length = self.config.get("min_paragraph_length", 20)

    def extract_text(self, pdf_path: str) -> Tuple[str, Dict]:
        """
        提取PDF文本并返回元数据

        Args:
            pdf_path: PDF文件路径

        Returns:
            (cleaned_text, metadata): 清洗后的文本和元数据
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

        # 打开PDF
        doc = fitz.open(pdf_path)

        try:
            # 先提取元数据（在文档打开时）
            metadata = self._extract_metadata(doc, pdf_path)

            # 提取所有页面的文本
            all_text = []

            for page_num, page in enumerate(doc):
                try:
                    # 获取页面文本
                    text = page.get_text("text")

                    # 移除页码
                    if self.remove_page_numbers:
                        text = self._remove_page_numbers(text, page_num + 1)

                    # 移除页眉页脚
                    if self.remove_headers_footers:
                        text = self._remove_headers_footers(text)

                    all_text.append(text)
                except Exception as e:
                    # 单页处理失败，跳过该页
                    print(f"  ⚠️ 警告: 页面 {page_num + 1} 处理失败: {str(e)}")
                    all_text.append("")

        finally:
            # 确保文档被关闭
            try:
                doc.close()
            except:
                pass

        # 合并所有页面文本
        full_text = "\n\n".join(all_text)

        # 清洗文本
        cleaned_text = self._clean_text(full_text)

        return cleaned_text, metadata

    def _remove_page_numbers(self, text: str, page_num: int) -> str:
        """移除页码"""
        # 常见页码模式
        patterns = [
            rf"\b{page_num}\b",  # 纯数字
            rf"Page\s*{page_num}",  # Page X
            rf"page\s*{page_num}",  # page X
        ]

        for pattern in patterns:
            text = re.sub(pattern, "", text)

        return text

    def _remove_headers_footers(self, text: str) -> str:
        """移除页眉页脚（简化版）"""
        # 移除孤立的数字（可能是页码）
        text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)

        # 移除过短的行（可能是页眉页脚）
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            # 保留有实质内容的行
            if len(stripped) >= self.min_paragraph_length or \
                    (stripped and stripped[0].isupper()):
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def _clean_text(self, text: str) -> str:
        """清洗文本"""
        # 标准化空白字符
        if self.normalize_whitespace:
            # 替换多个空格为单个空格
            text = re.sub(r" +", " ", text)
            # 替换多个换行为单个换行（保留段落分隔）
            text = re.sub(r"\n{3,}", "\n\n", text)
            # 移除行首行尾空格
            text = "\n".join(line.strip() for line in text.split("\n"))

        # 移除引用文献（常见模式）
        text = re.sub(r"\[\d+\]", "", text)  # [1], [2] 等
        text = re.sub(r"\(\d{4}\)", "", text)  # (2024) 等

        return text.strip()

    def _extract_metadata(self, doc, pdf_path: str) -> Dict:
        """从PDF提取元数据"""
        metadata = {
            "filename": os.path.basename(pdf_path),
            "file_path": pdf_path,
            "total_pages": len(doc),
        }

        # 尝试从文档信息中提取标题
        doc_info = doc.metadata
        if doc_info.get("title"):
            metadata["title"] = doc_info["title"]

        # 尝试从第一页提取标题（通常是论文标题）
        first_page = doc[0]
        first_page_text = first_page.get_text("text")
        lines = [line.strip() for line in first_page_text.split("\n") if line.strip()]

        if lines and len(lines[0]) > 10 and len(lines[0]) < 200:
            # 第一行通常是标题
            metadata["title"] = lines[0]

        return metadata