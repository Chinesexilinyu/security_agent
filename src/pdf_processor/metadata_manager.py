"""
元数据管理模块
从文件路径提取元数据并构建Dify兼容的metadata
"""

import os
import json
from typing import Dict
from .config import CATEGORY_MAPPING


class MetadataManager:
    """元数据管理器"""
    
    def __init__(self, category_mapping: Dict = None):
        """
        初始化元数据管理器
        
        Args:
            category_mapping: 文件夹类型映射
        """
        self.category_mapping = category_mapping or CATEGORY_MAPPING
    
    def extract_from_path(self, file_path: str) -> Dict:
        """
        从文件路径提取元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            元数据字典
        """
        # 分割路径
        parts = file_path.replace('\\', '/').split('/')
        
        metadata = {
            "filename": parts[-1],
            "category": "unknown",
            "year": "unknown",
            "category_cn": "unknown"
        }
        
        # 查找category和year
        for i, part in enumerate(parts):
            # 检查是否是category
            if part in self.category_mapping:
                metadata["category_cn"] = part
                metadata["category"] = self.category_mapping[part]
                
                # 下一个文件夹可能是年份
                if i + 1 < len(parts) - 1:
                    year_part = parts[i + 1]
                    if self._is_valid_year(year_part):
                        metadata["year"] = year_part
                break
        
        # 尝试从文件名提取年份
        if metadata["year"] == "unknown":
            year_from_filename = self._extract_year_from_filename(parts[-1])
            if year_from_filename:
                metadata["year"] = year_from_filename
        
        return metadata
    
    def _is_valid_year(self, year_str: str) -> bool:
        """
        判断字符串是否是有效年份
        
        Args:
            year_str: 年份字符串
            
        Returns:
            是否是有效年份（2000-2030）
        """
        try:
            year = int(year_str)
            return 2000 <= year <= 2030
        except ValueError:
            return False
    
    def _extract_year_from_filename(self, filename: str) -> str:
        """
        从文件名提取年份
        
        Args:
            filename: 文件名
            
        Returns:
            年份字符串，如果未找到返回None
        """
        # 常见年份格式：2024, '24, 2024_
        patterns = [
            r"(20\d{2})",  # 2024
            r"'(\d{2})",  # '24
        ]
        
        import re
        for pattern in patterns:
            matches = re.findall(pattern, filename)
            for match in matches:
                if len(match) == 2:
                    year = "20" + match
                else:
                    year = match
                
                if self._is_valid_year(year):
                    return year
        
        return None
    
    def enrich_metadata(self, chunk: Dict, pdf_metadata: Dict = None) -> Dict:
        """
        为chunk添加元数据
        
        Args:
            chunk: 包含content和基础metadata的chunk
            pdf_metadata: PDF提取的元数据
            
        Returns:
            丰富后的chunk
        """
        if "metadata" not in chunk:
            chunk["metadata"] = {}
        
        # 合并PDF元数据
        if pdf_metadata:
            for key, value in pdf_metadata.items():
                if key not in chunk["metadata"]:
                    chunk["metadata"][key] = value
        
        # 添加Dify推荐的元数据格式
        dify_metadata = {
            "category": chunk["metadata"].get("category", "unknown"),
            "category_cn": chunk["metadata"].get("category_cn", "unknown"),
            "year": chunk["metadata"].get("year", "unknown"),
            "section": chunk["metadata"].get("section", "unknown"),
            "chunk_id": chunk["metadata"].get("chunk_id", 0),
            "source_file": chunk["metadata"].get("filename", "unknown"),
            "char_count": chunk["metadata"].get("char_count", len(chunk["content"]))
        }
        
        # 添加论文标题（如果存在）
        if "title" in chunk["metadata"]:
            dify_metadata["title"] = chunk["metadata"]["title"]
        
        chunk["metadata"] = dify_metadata
        
        return chunk
    
    def format_for_dify(self, chunk: Dict) -> Dict:
        """
        格式化为Dify兼容的格式
        
        Args:
            chunk: 原始chunk
            
        Returns:
            Dify格式chunk
        """
        # Dify CSV格式需要：content列和metadata列（JSON字符串）
        dify_chunk = {
            "content": chunk["content"],
            "metadata": json.dumps(chunk["metadata"], ensure_ascii=False),
            "source": chunk["metadata"].get("source_file", "")
        }
        
        return dify_chunk
