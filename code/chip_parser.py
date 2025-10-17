# chip_parser.py
import re
from typing import Dict, List, Any


class ChipBlock:
    """表示一个块结构"""
    def __init__(self, keyword: str, name: str, content: str):
        self.keyword = keyword
        self.name = name
        self.content = content

    def __repr__(self):
        return f"{self.keyword} {self.name}"

    def get_hierarchical(self):
        # 提取 DbgBlkId 行
        dbgblkid_lines = [line.strip() for line in self.content.splitlines() if 'DbgBlkId' in line]
        if dbgblkid_lines:
            pairs = [{"DbgBlkId": dbg, "tile_name": ""} for dbg in dbgblkid_lines]
            return {
                "module": self.keyword.strip(),
                "instance": self.name.strip(),
                "pairs": pairs
            }
        return None

def parse_chip_file(file_path: str) -> List[ChipBlock]:
    """
    全文件范围，查找所有 keyword name ( ... ) 块，括号匹配
    """
    import os
    from pathlib import Path
    
    # 转换为绝对路径
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.path.dirname(__file__), '..', 'input', file_path)
    
    file_path = os.path.abspath(file_path)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.rstrip() for line in f if line.strip() and not line.lstrip().startswith('#')]
    except UnicodeDecodeError:
        # 如果UTF-8解码失败，尝试其他编码
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                lines = [line.rstrip() for line in f if line.strip() and not line.lstrip().startswith('#')]
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                lines = [line.rstrip() for line in f if line.strip() and not line.lstrip().startswith('#')]

    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()  # 移除前导空格来处理缩进
        
        # 匹配块定义: block CHIP_MID (
        block_match = re.match(r'^(\w+)\s+([^\(]+)\s*\($', line)
        
        # 匹配模块实例化: module_name instance_name(
        # 支持很长的模块名和带特殊字符的实例名
        instance_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s+([^\(]+)\s*\($', line)
        
        if block_match:
            # 处理块定义
            keyword = block_match.group(1)
            name = block_match.group(2).strip()
            brace_count = 1
            block_lines = []
            j = i + 1
            while j < len(lines):
                l = lines[j]
                brace_count += l.count('(')
                brace_count -= l.count(')')
                block_lines.append(l)
                if brace_count == 0:
                    break
                j += 1
            block_content = '\n'.join(block_lines[:-1]) if block_lines else ''
            blocks.append(ChipBlock(keyword, name, block_content))
            i = j + 1
            
        elif instance_match:
            # 处理模块实例化
            module_name = instance_match.group(1)
            instance_name = instance_match.group(2).strip()
            
            # 只有当模块名很长或包含特定模式时才考虑（避免误匹配简单语句）
            if len(module_name) > 10 or '_wrapper_' in module_name or '_container_' in module_name:
                brace_count = 1
                block_lines = []
                j = i + 1
                while j < len(lines):
                    l = lines[j]
                    brace_count += l.count('(')
                    brace_count -= l.count(')')
                    block_lines.append(l)
                    if brace_count == 0:
                        break
                    j += 1
                block_content = '\n'.join(block_lines[:-1]) if block_lines else ''
                # 使用模块名作为keyword，实例名作为name
                blocks.append(ChipBlock(module_name, instance_name, block_content))
                i = j + 1
            else:
                i += 1
        else:
            i += 1
    return blocks