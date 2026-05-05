"""
测试脚本 - 验证PDF处理器的各个模块
"""

import os
import sys
import json
from io import StringIO

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pdf_processor.config import CHUNK_CONFIG, CLEAN_CONFIG
from pdf_processor.chunker import SemanticChunker
from pdf_processor.metadata_manager import MetadataManager
from pdf_processor.output_manager import OutputManager


def test_chunker():
    """测试文本分割器"""
    print("="*60)
    print("🧪 测试文本分割器")
    print("="*60)
    
    # 创建分割器
    chunker = SemanticChunker(CHUNK_CONFIG)
    
    # 测试文本（模拟论文）
    test_text = """
Abstract
This paper presents a novel approach for vulnerability detection using deep learning. Our method achieves state-of-the-art performance on standard benchmarks.

1. Introduction
Software vulnerabilities pose significant security risks. Traditional methods rely on manual code review which is time-consuming. In this paper we propose an automated approach using machine learning.

2. Related Work
Previous work in vulnerability detection includes static analysis, dynamic analysis, and machine learning-based approaches. However these methods have limitations in accuracy and scalability.

3. Methodology
Our approach consists of three main components: code representation, neural architecture, and training procedure. We use transformer models to learn vulnerability patterns from source code.

4. Experiments
We evaluate our method on three public benchmarks: NVD, SARD, and CVE. Results show that our approach outperforms existing methods by 15% in F1-score.

5. Conclusion
In this paper we presented a novel vulnerability detection approach. Future work includes extending to more programming languages and improving computational efficiency.
"""
    
    # 测试元数据
    metadata = {
        "category": "vulnerability_mining",
        "year": "2024",
        "filename": "test_paper.pdf"
    }
    
    # 分割文本
    chunks = chunker.chunk_text(test_text, metadata)
    
    print(f"✅ 分割成功！")
    print(f"   总chunk数: {len(chunks)}")
    print(f"\n📊 Chunk详情:")
    for i, chunk in enumerate(chunks[:3], 1):  # 只显示前3个
        print(f"\n   Chunk {i}:")
        print(f"   - 长度: {len(chunk['content'])} 字符")
        print(f"   - 章节: {chunk['metadata']['section']}")
        print(f"   - 内容预览: {chunk['content'][:100]}...")
    
    # 验证chunk大小
    chunk_sizes = [len(c['content']) for c in chunks]
    print(f"\n📏 Chunk大小统计:")
    print(f"   平均: {sum(chunk_sizes)/len(chunk_sizes):.0f} 字符")
    print(f"   最小: {min(chunk_sizes)} 字符")
    print(f"   最大: {max(chunk_sizes)} 字符")
    
    # 验证章节识别
    sections = set(c['metadata']['section'] for c in chunks)
    print(f"\n📑 识别到的章节: {', '.join(sections)}")
    
    return chunks


def test_metadata_manager():
    """测试元数据管理器"""
    print("\n" + "="*60)
    print("🧪 测试元数据管理器")
    print("="*60)
    
    manager = MetadataManager()
    
    # 测试路径提取
    test_paths = [
        "papers/漏洞挖掘/2024/paper1.pdf",
        "papers/LLM安全/2023/paper2.pdf",
        "papers/其他/2022/paper3.pdf",
        "papers/漏洞修复/2024_2025/paper4.pdf",  # 异常路径
    ]
    
    for path in test_paths:
        metadata = manager.extract_from_path(path)
        print(f"\n✅ 路径: {path}")
        print(f"   类型: {metadata['category_cn']} ({metadata['category']})")
        print(f"   年份: {metadata['year']}")
    
    return True


def test_output_manager():
    """测试输出管理器"""
    print("\n" + "="*60)
    print("🧪 测试输出管理器")
    print("="*60)
    
    # 创建测试chunks
    test_chunks = [
        {
            "content": "This is a test chunk about vulnerability detection.",
            "metadata": json.dumps({
                "category": "vulnerability_mining",
                "year": "2024",
                "section": "Abstract",
                "chunk_id": 1
            }, ensure_ascii=False),
            "source": "test_paper.pdf"
        },
        {
            "content": "Our method achieves state-of-the-art performance.",
            "metadata": json.dumps({
                "category": "vulnerability_mining",
                "year": "2024",
                "section": "Conclusion",
                "chunk_id": 2
            }, ensure_ascii=False),
            "source": "test_paper.pdf"
        }
    ]
    
    # 创建输出管理器
    output_manager = OutputManager(output_dir="test_output", format="csv")
    
    # 保存chunks
    output_path = output_manager.save_chunks(test_chunks, "test_knowledge_base")
    
    # 生成统计
    stats = output_manager.generate_statistics(test_chunks)
    output_manager.print_statistics(stats)
    
    # 保存统计
    output_manager.save_statistics(stats, "test_knowledge_base")
    
    # 检查文件是否存在
    if os.path.exists(output_path):
        print(f"\n✅ CSV文件已创建: {output_path}")
        with open(output_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            print(f"📄 文件内容预览:\n{content[:500]}...")
        return True
    else:
        print(f"\n❌ 文件创建失败")
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "🚀 开始运行测试...")
    print("="*60)
    
    results = []
    
    # 测试1: 文本分割
    try:
        chunks = test_chunker()
        results.append(("文本分割器", True, None))
    except Exception as e:
        results.append(("文本分割器", False, str(e)))
    
    # 测试2: 元数据管理
    try:
        test_metadata_manager()
        results.append(("元数据管理器", True, None))
    except Exception as e:
        results.append(("元数据管理器", False, str(e)))
    
    # 测试3: 输出管理
    try:
        test_output_manager()
        results.append(("输出管理器", True, None))
    except Exception as e:
        results.append(("输出管理器", False, str(e)))
    
    # 输出测试结果摘要
    print("\n" + "="*60)
    print("📊 测试结果摘要")
    print("="*60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, error in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {name}")
        if error:
            print(f"   错误: {error}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
