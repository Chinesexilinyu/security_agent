"""
输出管理模块
将处理后的chunk保存为Dify兼容的格式
"""

import csv
import json
import os
from typing import List, Dict
from datetime import datetime


class OutputManager:
    """输出管理器"""
    
    def __init__(self, output_dir: str = "output", format: str = "csv"):
        """
        初始化输出管理器
        
        Args:
            output_dir: 输出目录
            format: 输出格式（csv或json）
        """
        self.output_dir = output_dir
        self.format = format.lower()
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
    
    def save_chunks(self, chunks: List[Dict], base_filename: str) -> str:
        """
        保存chunks到文件
        
        Args:
            chunks: chunk列表
            base_filename: 基础文件名
            
        Returns:
            保存的文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.format == "csv":
            output_path = os.path.join(
                self.output_dir, 
                f"{base_filename}_{timestamp}.csv"
            )
            self._save_csv(chunks, output_path)
        elif self.format == "json":
            output_path = os.path.join(
                self.output_dir, 
                f"{base_filename}_{timestamp}.json"
            )
            self._save_json(chunks, output_path)
        else:
            raise ValueError(f"不支持的输出格式: {self.format}")
        
        return output_path
    
    def _save_csv(self, chunks: List[Dict], output_path: str):
        """
        保存为CSV格式（Dify兼容）
        
        Args:
            chunks: chunk列表
            output_path: 输出文件路径
        """
        # CSV列定义
        fieldnames = ["content", "metadata", "source"]
        
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for chunk in chunks:
                writer.writerow({
                    "content": chunk.get("content", ""),
                    "metadata": chunk.get("metadata", "{}"),
                    "source": chunk.get("source", "")
                })
        
        print(f"✅ CSV文件已保存: {output_path}")
        print(f"   共 {len(chunks)} 个chunks")
    
    def _save_json(self, chunks: List[Dict], output_path: str):
        """
        保存为JSON格式
        
        Args:
            chunks: chunk列表
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON文件已保存: {output_path}")
        print(f"   共 {len(chunks)} 个chunks")
    
    def generate_statistics(self, chunks: List[Dict]) -> Dict:
        """
        生成统计信息
        
        Args:
            chunks: chunk列表
            
        Returns:
            统计信息字典
        """
        if not chunks:
            return {}
        
        stats = {
            "total_chunks": len(chunks),
            "total_chars": sum(len(chunk["content"]) for chunk in chunks),
            "avg_chunk_size": sum(len(chunk["content"]) for chunk in chunks) / len(chunks),
            "min_chunk_size": min(len(chunk["content"]) for chunk in chunks),
            "max_chunk_size": max(len(chunk["content"]) for chunk in chunks),
        }
        
        # 按类型统计
        category_stats = {}
        for chunk in chunks:
            metadata = json.loads(chunk.get("metadata", "{}"))
            category = metadata.get("category", "unknown")
            category_stats[category] = category_stats.get(category, 0) + 1
        stats["by_category"] = category_stats
        
        # 按年份统计
        year_stats = {}
        for chunk in chunks:
            metadata = json.loads(chunk.get("metadata", "{}"))
            year = metadata.get("year", "unknown")
            year_stats[year] = year_stats.get(year, 0) + 1
        stats["by_year"] = year_stats
        
        # 按章节统计
        section_stats = {}
        for chunk in chunks:
            metadata = json.loads(chunk.get("metadata", "{}"))
            section = metadata.get("section", "unknown")
            section_stats[section] = section_stats.get(section, 0) + 1
        stats["by_section"] = section_stats
        
        return stats
    
    def print_statistics(self, stats: Dict):
        """
        打印统计信息
        
        Args:
            stats: 统计信息字典
        """
        print("\n" + "="*50)
        print("📊 处理统计")
        print("="*50)
        print(f"总chunk数: {stats['total_chunks']}")
        print(f"总字符数: {stats['total_chars']:,}")
        print(f"平均chunk大小: {stats['avg_chunk_size']:.0f} 字符")
        print(f"最小chunk大小: {stats['min_chunk_size']} 字符")
        print(f"最大chunk大小: {stats['max_chunk_size']} 字符")
        
        print("\n按类型统计:")
        for category, count in stats.get("by_category", {}).items():
            print(f"  {category}: {count}")
        
        print("\n按年份统计:")
        for year, count in sorted(stats.get("by_year", {}).items()):
            print(f"  {year}: {count}")
        
        print("\n按章节统计:")
        for section, count in stats.get("by_section", {}).items():
            print(f"  {section}: {count}")
        
        print("="*50 + "\n")
    
    def save_statistics(self, stats: Dict, base_filename: str):
        """
        保存统计信息到文件
        
        Args:
            stats: 统计信息字典
            base_filename: 基础文件名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stats_path = os.path.join(
            self.output_dir, 
            f"{base_filename}_statistics_{timestamp}.json"
        )
        
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 统计信息已保存: {stats_path}")
