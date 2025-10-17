'''
DFD Automation Tool - 统一主程序
功能包括：
1. 芯片块解析和JSON生成
2. Excel数据整合
3. Tile可视化
4. 数据映射和清理
'''

import json
import re
import os
from pathlib import Path
from tile_parser import TileParser
from chip_parser import parse_chip_file
from excel_reader import read_excel_column_f
from json_excel_integrator import integrate_json_excel_data

# 用户可在此配置变量展开规则
expand_dict = {
    "$SSA": [0],
    "$SSB": [0,1],
    "$SSC": [0,1],
    "$smn_ssbdci_wafl_inst":[0,1],
    "$ucis_x4_inst" : [0,1,2,3,4,5],
    "$ucis_left_inst" : [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
    "$ucis_right_inst" : [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
}

def expand_instance_name(name, expand_dict):
    """展开实例名称中的变量"""
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

def process_chip_blocks():
    """处理芯片块解析和JSON生成"""
    print("🔧 开始处理芯片块解析...")
    
    # 确保输出目录存在
    output_dir = Path(os.path.dirname(__file__)) / '..' / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 第一步：生成原始chip_blocks.json
    blocks = parse_chip_file("CHIP.txt")
    result = {}
    for block in blocks:
        hier = block.get_hierarchical()
        if hier:
            expanded_instances = expand_instance_name(hier['instance'], expand_dict)
            for inst in expanded_instances:
                new_hier = hier.copy()
                new_hier['instance'] = inst
                key = f"{hier['module']}::{inst}"
                result[key] = new_hier
    
    output_file = output_dir / "chip_blocks.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 成功处理 {len(blocks)} 个块，生成 {len(result)} 个展开结果")
    print(f"✅ 原始JSON已保存到: {output_file}")
    
    # 第二步：如果Mapping.xlsx存在，则进行整合
    input_dir = Path(os.path.dirname(__file__)) / '..' / 'input'
    mapping_file = input_dir / "Mapping.xlsx"
    
    if mapping_file.exists():
        print("\n🔄 开始整合Excel数据...")
        integrated_file = output_dir / "chip_blocks_integrated.json"
        
        success = integrate_json_excel_data(
            json_file_path=str(output_file),
            excel_file_path=str(mapping_file),
            output_file_path=str(integrated_file)
        )
        
        if success:
            print(f"✅ 整合版本已保存到: {integrated_file}")
        else:
            print("⚠️ Excel整合失败，但原始JSON文件已成功生成")
    else:
        print(f"\n💡 提示：如果需要tile_name整合，请将Mapping.xlsx放在 {input_dir} 目录下")
    
    return len(blocks), len(result)

def process_visualization():
    """处理Tile可视化"""
    print("\n🎨 开始处理Tile可视化...")
    
    # 确保输出目录存在
    output_dir = Path(os.path.dirname(__file__)) / '..' / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 读取Excel文件F列作为highlight_client输入
        print("📊 读取Mapping.xlsx文件F列...")
        highlight_client_list = read_excel_column_f('Mapping.xlsx')
        print(f"✅ 成功读取到 {len(highlight_client_list)} 个client标记")
        
        # 创建解析器
        parser = TileParser()

        # 解析数据
        parser.parse_from_csv('MID.csv')

        # 绘图并保存高分辨率图像
        save_path = output_dir / "tiles_high_res.png"
        parser.plot(
            title="Tile Visualization by Master & Orient",
            show_labels=False,
            save_path=str(save_path),
            dpi=1200,
            show_legend=False,
            highlight_dbg=['soc_df_rpt3_mid_t','soc_df_rpt1_mid_t','soc_df_rpt6_mid_t'],
            highlight_client=highlight_client_list,
            #highlight_or_gate='pciess_xgmi4_1x8_pcs_ss0_mid_t5'
        )
        print(f"✅ 图像可视化完成")
        return True
        
    except FileNotFoundError as e:
        print(f"⚠️ 可视化文件错误: {e}")
        return False
    except Exception as e:
        print(f"⚠️ 可视化处理错误: {e}")
        return False

def main():
    """主程序入口 - 整合所有功能"""
    print("🚀 DFD自动化工具启动")
    print("=" * 50)
    
    try:
        # 处理芯片块解析和JSON生成
        blocks_count, result_count = process_chip_blocks()
        
        # 处理Tile可视化
        visualization_success = process_visualization()
        
        # 输出总结
        print("\n" + "=" * 50)
        print("📋 处理总结:")
        print(f"   📦 芯片块处理: {blocks_count} 个原始块 → {result_count} 个展开结果")
        print(f"   🎨 可视化处理: {'✅ 成功' if visualization_success else '❌ 失败'}")
        print("✅ DFD自动化工具处理完成")
        
    except FileNotFoundError as e:
        print(f"❌ 文件错误: {e}")
    except Exception as e:
        print(f"❌ 运行错误: {e}")

if __name__ == "__main__":
    main()