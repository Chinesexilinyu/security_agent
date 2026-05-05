"""
主处理流程模块
整合PDF提取、文本分割、元数据管理和输出
"""

import os
from typing import List, Dict
from tqdm import tqdm

from .pdf_extractor import PDFExtractor
from .chunker import SemanticChunker
from .metadata_manager import MetadataManager
from .output_manager import OutputManager
from .config import CHUNK_CONFIG, CLEAN_CONFIG, OUTPUT_CONFIG


class PDFProcessor:
    """PDF论文处理器"""
    
    def __init__(self, config: Dict = None):
        """
        初始化处理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 初始化各模块
        self.extractor = PDFExtractor(CLEAN_CONFIG)
        self.chunker = SemanticChunker(CHUNK_CONFIG)
        self.metadata_manager = MetadataManager()
        self.output_manager = OutputManager(
            output_dir=self.config.get("output_dir", "output"),
            format=OUTPUT_CONFIG.get("format", "csv")
        )
    
    def process_file(self, pdf_path: str) -> List[Dict]:
        """
        处理单个PDF文件
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            chunk列表
        """
        # 1. 从路径提取基础元数据
        base_metadata = self.metadata_manager.extract_from_path(pdf_path)
        
        # 2. 提取PDF文本和元数据
        text, pdf_metadata = self.extractor.extract_text(pdf_path)
        
        # 合并元数据
        base_metadata.update(pdf_metadata)
        
        # 3. 语义分割
        chunks = self.chunker.chunk_text(text, base_metadata)
        
        # 4. 丰富元数据并格式化为Dify格式
        dify_chunks = []
        for chunk in chunks:
            chunk = self.metadata_manager.enrich_metadata(chunk, pdf_metadata)
            dify_chunk = self.metadata_manager.format_for_dify(chunk)
            dify_chunks.append(dify_chunk)
        
        return dify_chunks
    
    def process_directory(self, root_dir: str, recursive: bool = True) -> List[Dict]:
        """
        处理目录下的所有PDF文件
        
        Args:
            root_dir: 根目录
            recursive: 是否递归处理子目录
            
        Returns:
            所有chunk列表
        """
        if not os.path.exists(root_dir):
            raise FileNotFoundError(f"目录不存在: {root_dir}")
        
        # 查找所有PDF文件
        pdf_files = self._find_pdf_files(root_dir, recursive)
        
        print(f"📂 找到 {len(pdf_files)} 个PDF文件")
        print("="*50)
        
        all_chunks = []
        failed_files = []
        
        # 处理每个PDF文件
        for pdf_path in tqdm(pdf_files, desc="处理PDF文件"):
            try:
                chunks = self.process_file(pdf_path)
                all_chunks.extend(chunks)
                tqdm.write(f"✅ {os.path.basename(pdf_path)}: {len(chunks)} chunks")
            except Exception as e:
                failed_files.append((pdf_path, str(e)))
                tqdm.write(f"❌ {os.path.basename(pdf_path)}: {str(e)}")
        
        # 输出结果
        print("\n" + "="*50)
        print(f"📊 处理完成:")
        print(f"  成功: {len(pdf_files) - len(failed_files)}/{len(pdf_files)}")
        print(f"  失败: {len(failed_files)}/{len(pdf_files)}")
        print(f"  总chunks: {len(all_chunks)}")
        
        if failed_files:
            print("\n⚠️ 失败文件列表:")
            for file_path, error in failed_files:
                print(f"  - {os.path.basename(file_path)}: {error}")
        
        return all_chunks
    
    def _find_pdf_files(self, directory: str, recursive: bool = True) -> List[str]:
        """
        查找目录下的所有PDF文件
        
        Args:
            directory: 目录路径
            recursive: 是否递归
            
        Returns:
            PDF文件路径列表
        """
        pdf_files = []
        
        if recursive:
            # 递归查找
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))
        else:
            # 仅查找当前目录
            for file in os.listdir(directory):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(directory, file))
        
        return sorted(pdf_files)
    
    def save_results(self, chunks: List[Dict], output_filename: str = None):
        """
        保存处理结果
        
        Args:
            chunks: chunk列表
            output_filename: 输出文件名（可选）
        """
        if not chunks:
            print("⚠️ 没有数据需要保存")
            return
        
        # 保存chunks
        output_path = self.output_manager.save_chunks(
            chunks, 
            output_filename or OUTPUT_CONFIG.get("output_file", "dify_knowledge_base")
        )
        
        # 生成统计信息
        stats = self.output_manager.generate_statistics(chunks)
        self.output_manager.print_statistics(stats)
        
        # 保存统计信息
        self.output_manager.save_statistics(
            stats, 
            output_filename or OUTPUT_CONFIG.get("output_file", "dify_knowledge_base")
        )
        
        return output_path


def main():
    """示例用法"""
    # 配置参数
    config = {
        "output_dir": "output",
    }
    
    # 创建处理器
    processor = PDFProcessor(config)
    
    # 处理目录（替换为你的实际路径）
    root_dir = "./papers"  # 你的PDF论文根目录
    
    print("🚀 开始处理PDF论文...")
    print(f"📂 输入目录: {root_dir}")
    print("="*50 + "\n")
    
    # 处理所有PDF
    chunks = processor.process_directory(root_dir, recursive=True)
    
    # 保存结果
    if chunks:
        output_path = processor.save_results(chunks, "cyber_security_papers")
        print(f"\n🎉 处理完成！")
        print(f"📄 输出文件: {output_path}")
        print("\n💡 下一步:")
        print("   1. 打开Dify知识库")
        print("   2. 选择'文本文件'上传方式")
        print("   3. 上传生成的CSV文件")
        print("   4. 配置索引方式（推荐：高质量embedding）")
        print("   5. 开始向量化并创建知识库")
    else:
        print("❌ 没有生成任何chunks，请检查输入目录")


if __name__ == "__main__":
    main()
