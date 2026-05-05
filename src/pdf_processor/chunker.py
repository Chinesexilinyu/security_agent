"""
智能文本分割模块
基于论文章节结构进行语义分割
"""

import re
from typing import Dict, List, Tuple
from .config import SECTION_HEADERS, CHUNK_CONFIG


class SemanticChunker:
    """语义感知的文本分割器"""
    
    def __init__(self, config: Dict = None):
        """
        初始化分割器
        
        Args:
            config: 分割配置
        """
        self.chunk_size = config.get("chunk_size", CHUNK_CONFIG["chunk_size"])
        self.chunk_overlap = config.get("chunk_overlap", CHUNK_CONFIG["chunk_overlap"])
        self.min_chunk_size = config.get("min_chunk_size", CHUNK_CONFIG["min_chunk_size"])
        self.max_chunk_size = config.get("max_chunk_size", CHUNK_CONFIG["max_chunk_size"])
        self.section_headers = SECTION_HEADERS
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        对文本进行智能分割
        
        Args:
            text: 输入文本
            metadata: 元数据（category, year, filename等）
            
        Returns:
            chunk_list: 分割后的块列表，每个块包含content和metadata
        """
        if metadata is None:
            metadata = {}
        
        # 1. 识别章节并分割
        sections = self._identify_sections(text)
        
        # 2. 对每个章节进行分割
        all_chunks = []
        chunk_id = 0
        
        for section_name, section_text in sections:
            if not section_text.strip():
                continue
            
            # 使用滑动窗口分割
            section_chunks = self._sliding_window_chunk(
                section_text, 
                section_name=section_name
            )
            
            # 为每个块添加元数据
            for chunk_text in section_chunks:
                chunk_id += 1
                chunk_metadata = {
                    **metadata,
                    "section": section_name,
                    "chunk_id": chunk_id,
                    "char_count": len(chunk_text)
                }
                
                all_chunks.append({
                    "content": chunk_text,
                    "metadata": chunk_metadata
                })
        
        return all_chunks
    
    def _identify_sections(self, text: str) -> List[Tuple[str, str]]:
        """
        识别论文的章节结构
        
        Args:
            text: 论文全文
            
        Returns:
            [(section_name, section_text), ...]: 章节列表
        """
        sections = []
        
        # 构建章节识别正则表达式
        section_patterns = []
        for section_name, patterns in self.section_headers.items():
            for pattern in patterns:
                # 转义特殊字符
                escaped_pattern = re.escape(pattern)
                section_patterns.append(f"^{escaped_pattern}\\s*$")
        
        # 合并所有模式，(?m) 标记放在最前面
        combined_pattern = "(?m)" + "|".join(section_patterns)
        
        # 查找所有章节标题
        section_matches = []
        for match in re.finditer(combined_pattern, text):
            matched_text = match.group(0).strip()
            section_name = self._get_section_name(matched_text)
            section_matches.append((match.start(), matched_text, section_name))
        
        # 如果没有找到章节，将整个文本作为一个section
        if not section_matches:
            return [("Full Text", text)]
        
        # 按位置排序
        section_matches.sort(key=lambda x: x[0])
        
        # 提取每个章节的文本
        for i, (start, header_text, section_name) in enumerate(section_matches):
            if i == 0:
                # 第一个章节从开头开始
                section_start = 0
            else:
                section_start = section_matches[i-1][0]
            
            if i == len(section_matches) - 1:
                # 最后一个章节到文本结束
                section_end = len(text)
            else:
                section_end = start
            
            section_text = text[section_start:section_end].strip()
            
            # 移除章节标题（避免在chunk中重复）
            if i > 0:
                prev_header = section_matches[i-1][1]
                if section_text.startswith(prev_header):
                    section_text = section_text[len(prev_header):].strip()
            
            sections.append((section_name, section_text))
        
        return sections
    
    def _get_section_name(self, header_text: str) -> str:
        """
        根据章节标题文本映射到标准章节名称
        
        Args:
            header_text: 章节标题文本
            
        Returns:
            标准章节名称
        """
        header_lower = header_text.lower().strip()
        
        for section_name, patterns in self.section_headers.items():
            for pattern in patterns:
                if pattern.lower() == header_lower:
                    return section_name
        
        # 默认返回原始标题
        return header_text
    
    def _sliding_window_chunk(self, text: str, section_name: str = "Unknown") -> List[str]:
        """
        使用滑动窗口分割文本，保持语义完整性
        
        Args:
            text: 文本内容
            section_name: 章节名称
            
        Returns:
            分割后的文本块列表
        """
        if len(text) <= self.max_chunk_size:
            return [text] if text.strip() else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # 确定当前块的结束位置
            end = start + self.chunk_size
            
            # 如果超出文本长度，取到末尾
            if end >= len(text):
                chunks.append(text[start:].strip())
                break
            
            # 尝试在句子边界处切分
            ideal_end = self._find_sentence_boundary(text, end)
            
            # 如果找到合适的边界，使用它
            if ideal_end > start + self.min_chunk_size:
                end = ideal_end
            else:
                # 如果没有找到边界，使用最大长度
                end = min(end, len(text))
            
            # 提取chunk
            chunk = text[start:end].strip()
            
            if chunk:
                chunks.append(chunk)
            
            # 移动起始位置（带重叠）
            start = end - self.chunk_overlap
        
        return chunks
    
    def _find_sentence_boundary(self, text: str, target_pos: int) -> int:
        """
        在目标位置附近寻找句子边界
        
        Args:
            text: 文本
            target_pos: 目标位置
            
        Returns:
            句子结束位置
        """
        # 搜索范围：目标位置前后100字符
        search_start = max(0, target_pos - 100)
        search_end = min(len(text), target_pos + 100)
        search_text = text[search_start:search_end]
        
        # 句子结束标记（按优先级）
        sentence_endings = [
            ".\n",  # 句号+换行（段落结束）
            "! ",
            "? ",
            ". ",  # 句号+空格
            ";\n",  # 分号+换行
            ":\n",  # 冒号+换行
        ]
        
        best_pos = target_pos
        
        for ending in sentence_endings:
            # 在搜索范围内查找
            found_pos = search_text.rfind(ending, 0, target_pos - search_start + 50)
            
            if found_pos != -1:
                best_pos = search_start + found_pos + len(ending)
                break
        
        # 确保不超过搜索范围
        best_pos = min(best_pos, search_end)
        
        return best_pos
    
    def _is_complete_sentence(self, text: str) -> bool:
        """
        判断文本是否是完整句子
        
        Args:
            text: 文本
            
        Returns:
            是否是完整句子
        """
        text = text.strip()
        if not text:
            return False
        
        # 检查是否以句子结束标记结尾
        return text[-1] in ['.', '!', '?']
