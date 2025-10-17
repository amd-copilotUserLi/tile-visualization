import json
import re

def expand_instance_name(name, expand_dict):
    # 匹配 {...} 结构
    pattern = re.compile(r'\{\$(\w+)\}')
    match = pattern.search(name)
    if not match:
        return [name]
    var = f"${match.group(1)}"
    if var not in expand_dict:
        return [name]
    values = expand_dict[var]
    expanded = [pattern.sub(str(v), name) for v in values]
    return expanded

def expand_chip_blocks(input_json, output_json, expand_dict):
    import os
    from pathlib import Path
    
    # 处理输入文件路径
    if not os.path.isabs(input_json):
        input_json = os.path.join(os.path.dirname(__file__), '..', 'output', input_json)
    input_json = os.path.abspath(input_json)
    
    # 处理输出文件路径
    if not os.path.isabs(output_json):
        output_json = os.path.join(os.path.dirname(__file__), '..', 'output', output_json)
    output_json = os.path.abspath(output_json)
    
    # 确保输出目录存在
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    
    if not os.path.exists(input_json):
        raise FileNotFoundError(f"输入文件不存在: {input_json}")
    
    try:
        with open(input_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except UnicodeDecodeError:
        with open(input_json, 'r', encoding='gbk') as f:
            data = json.load(f)
    
    expanded_data = {}
    for key, block in data.items():
        orig_instance = block['instance']
        expanded_instances = expand_instance_name(orig_instance, expand_dict)
        for inst in expanded_instances:
            new_key = f"{block['module']}::{inst}"
            new_block = block.copy()
            new_block['instance'] = inst
            expanded_data[new_key] = new_block
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(expanded_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 展开完成: {len(data)} -> {len(expanded_data)} 个块")
    print(f"✅ 结果已保存到: {output_json}")
