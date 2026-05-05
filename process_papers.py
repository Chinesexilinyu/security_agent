"""
PDF论文处理主脚本
用于处理网安科研论文并生成Dify兼容的知识库数据
"""

import os
import sys
import argparse
from src.pdf_processor import PDFProcessor
from src.pdf_processor.config import CHUNK_CONFIG, CLEAN_CONFIG, OUTPUT_CONFIG


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="处理PDF论文并生成Dify知识库数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 基本用法
  python process_papers.py --input ./papers
  
  # 指定输出目录
  python process_papers.py --input ./papers --output ./dify_data
  
  # 调整chunk大小
  python process_papers.py --input ./papers --chunk-size 800 --overlap 200
  
  # 仅处理单个文件
  python process_papers.py --input ./papers/vulnerability_mining/2024/paper.pdf --single-file
  
目录结构要求:
  papers/
  ├── 漏洞挖掘/
  │   ├── 2024/
  │   └── 2023/
  ├── 漏洞修复/
  │   ├── 2024/
  │   └── 2023/
  ├── LLM安全/
  │   └── 2024/
  └── 其他/
      └── 2024/
        """
    )
    
    # 参数定义
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="输入目录（包含PDF论文）或单个PDF文件路径"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output",
        help="输出目录（默认: output）"
    )
    
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=CHUNK_CONFIG["chunk_size"],
        help=f"Chunk大小（字符数，默认: {CHUNK_CONFIG['chunk_size']}）"
    )
    
    parser.add_argument(
        "--overlap",
        type=int,
        default=CHUNK_CONFIG["chunk_overlap"],
        help=f"Chunk重叠大小（字符数，默认: {CHUNK_CONFIG['chunk_overlap']}）"
    )
    
    parser.add_argument(
        "--format",
        type=str,
        choices=["csv", "json"],
        default=OUTPUT_CONFIG.get("format", "csv"),
        help="输出格式（csv或json，默认: csv）"
    )
    
    parser.add_argument(
        "--single-file",
        action="store_true",
        help="处理单个文件而不是整个目录"
    )
    
    parser.add_argument(
        "--output-name",
        type=str,
        default="dify_knowledge_base",
        help="输出文件名（默认: dify_knowledge_base）"
    )
    
    args = parser.parse_args()
    
    # 验证输入路径
    if not os.path.exists(args.input):
        print(f"❌ 错误: 输入路径不存在: {args.input}")
        sys.exit(1)
    
    # 更新配置
    CHUNK_CONFIG["chunk_size"] = args.chunk_size
    CHUNK_CONFIG["chunk_overlap"] = args.overlap
    OUTPUT_CONFIG["format"] = args.format
    
    # 创建处理器
    config = {
        "output_dir": args.output,
    }
    
    processor = PDFProcessor(config)
    
    # 打印配置信息
    print("="*60)
    print("🚀 PDF论文处理器 - Dify知识库数据生成工具")
    print("="*60)
    print(f"📂 输入路径: {args.input}")
    print(f"📁 输出目录: {args.output}")
    print(f"📏 Chunk大小: {args.chunk_size} 字符")
    print(f"🔄 重叠大小: {args.overlap} 字符")
    print(f"📄 输出格式: {args.format.upper()}")
    print("="*60 + "\n")
    
    try:
        # 处理文件
        if args.single_file or os.path.isfile(args.input):
            # 处理单个文件
            print("📝 处理单个PDF文件...")
            print("-"*60)
            
            chunks = processor.process_file(args.input)
            print(f"✅ 文件处理完成: {len(chunks)} chunks")
            
        else:
            # 处理整个目录
            print("📂 处理PDF目录...")
            print("-"*60)
            
            chunks = processor.process_directory(args.input, recursive=True)
            
            if chunks:
                print(f"\n✅ 目录处理完成: {len(chunks)} chunks")
            else:
                print("\n⚠️ 没有生成任何chunks")
                sys.exit(0)
        
        # 保存结果
        if chunks:
            print("\n💾 保存结果...")
            print("-"*60)
            
            output_path = processor.save_results(chunks, args.output_name)
            
            print("\n" + "="*60)
            print("🎉 处理完成！")
            print("="*60)
            print(f"📄 输出文件: {output_path}")
            print(f"📊 总chunks: {len(chunks)}")
            print("\n💡 下一步操作:")
            print("   1. 登录Dify平台（https://cloud.dify.ai/）")
            print("   2. 创建或进入你的知识库")
            print("   3. 选择'文档' → '导入'")
            print("   4. 选择'上传文件' → 选择生成的CSV文件")
            print("   5. 配置索引选项:")
            print("      - 索引模式: 高质量")
            print("      - Embedding模型: 推荐使用支持中英文的模型")
            print("   6. 点击'开始处理'")
            print("   7. 等待向量化完成")
            print("   8. 在知识库中测试检索效果")
            print("\n📚 使用建议:")
            print("   - Chunk大小 500-800: 适合精确检索")
            print("   - Chunk大小 800-1200: 适合长文理解")
            print("   - 重叠率 20-30%: 保持上下文连贯性")
            print("   - 对于论文摘要、结论等关键部分，可以手动调小chunk")
            print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断处理")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 处理出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
