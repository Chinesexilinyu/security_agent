"""
PDF论文处理配置文件
针对网安科研论文优化的文本分割配置
"""

# 文本分割配置
CHUNK_CONFIG = {
    # 块大小（字符数）- Dify推荐500-800字符
    "chunk_size": 700,
    
    # 块重叠大小（字符数）- 保持上下文连贯性
    "chunk_overlap": 150,
    
    # 最小块大小（字符数）- 避免过短的片段
    "min_chunk_size": 100,
    
    # 最大块大小（字符数）- 超过此值强制切分
    "max_chunk_size": 1200,
}

# 文件夹类型映射
CATEGORY_MAPPING = {
    "漏洞挖掘": "vulnerability_mining",
    "漏洞修复": "vulnerability_repair",
    "LLM安全": "llm_security",
    "其他": "other"
}

# 论文常见章节标识（用于智能分割）
SECTION_HEADERS = {
    "Abstract": ["Abstract", "ABSTRACT", "Summary", "SUMMARY"],
    "Introduction": ["Introduction", "INTRODUCTION", "1. Introduction", "1 Introduction"],
    "Related Work": ["Related Work", "RELATED WORK", "Background", "BACKGROUND"],
    "Method": ["Method", "METHOD", "Methodology", "METHODOLOGY", "Methodology", 
               "Proposed Method", "PROPOSED METHOD", "Approach", "APPROACH"],
    "Experiment": ["Experiment", "EXPERIMENT", "Experiments", "EXPERIMENTS", 
                   "Evaluation", "EVALUATION", "Results", "RESULTS"],
    "Discussion": ["Discussion", "DISCUSSION", "Analysis", "ANALYSIS"],
    "Conclusion": ["Conclusion", "CONCLUSION", "Conclusions", "CONCLUSIONS",
                   "Future Work", "FUTURE WORK", "Future Directions"],
    "References": ["References", "REFERENCES", "Bibliography", "BIBLIOGRAPHY"]
}

# 文本清洗配置
CLEAN_CONFIG = {
    # 是否移除页码
    "remove_page_numbers": True,
    
    # 是否移除页眉页脚
    "remove_headers_footers": True,
    
    # 是否标准化空白字符
    "normalize_whitespace": True,
    
    # 最小段落长度（字符数）- 过滤掉过短的段落
    "min_paragraph_length": 20,
    
    # 是否移除特殊字符
    "remove_special_chars": False,  # 保留公式符号
}

# 输出配置
OUTPUT_CONFIG = {
    # 输出格式：csv, json
    "format": "csv",
    
    # 输出文件名
    "output_file": "dify_knowledge_base",
    
    # 是否包含文件名在content中
    "include_filename_in_content": False,
    
    # CSV列名
    "csv_columns": {
        "content": "content",          # 文本内容
        "metadata": "metadata",        # 元数据JSON字符串
        "source": "source"             # 来源文件
    }
}
