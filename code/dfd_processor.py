"""
DFD核心处理模块
包含所有主要的数据处理功能
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from tile_parser import TileParser
from chip_parser import parse_chip_file
from excel_reader import read_excel_column_f, read_excel_client_tile_mapping
from json_excel_integrator import integrate_json_excel_data


class DFDProcessor:
    """DFD数据处理核心类"""
    
    def __init__(self, expand_dict):
        """
        初始化处理器
        
        Args:
            expand_dict: 变量展开规则字典
        """
        self.expand_dict = expand_dict
        self.unmatched_analysis = None
        self.output_dir = Path(os.path.dirname(__file__)) / '..' / 'output'
        
    def expand_instance_name(self, name):
        """展开实例名称中的变量"""
        pattern = re.compile(r'\{\$(\w+)\}')
        match = pattern.search(name)
        if not match:
            return [name]
        var = f"${match.group(1)}"
        if var not in self.expand_dict:
            return [name]
        values = self.expand_dict[var]
        expanded = [pattern.sub(str(v), name) for v in values]
        return expanded

    def process_chip_blocks(self):
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
                expanded_instances = self.expand_instance_name(hier['instance'])
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
            
            success, self.unmatched_analysis = integrate_json_excel_data(
                json_file_path=str(output_file),
                excel_file_path=str(mapping_file),
                output_file_path=str(integrated_file)
            )
            
            if success:
                print(f"✅ 整合版本已保存到: {integrated_file}")
                if self.unmatched_analysis:
                    print(f"📊 未匹配Excel模块数: {self.unmatched_analysis['unmatched_excel_modules_count']}")
            else:
                print("⚠️ Excel整合失败，但原始JSON文件已成功生成")
        else:
            print(f"\n💡 提示：如果需要tile_name整合，请将Mapping.xlsx放在 {input_dir} 目录下")
        
        return len(blocks), len(result)

    def process_visualization(self, show_client_tile_names=0):
        """处理Tile可视化
        
        Args:
            show_client_tile_names: 是否在有client的tile上显示tile名称 (0=不显示, 1=显示)
        """
        print("\n🎨 开始处理Tile可视化...")
        
        # 如果开启了tile名称显示，输出提示信息
        if show_client_tile_names:
            print("🏷️ 已启用client tile名称显示功能")
        
        # 确保输出目录存在
        output_dir = Path(os.path.dirname(__file__)) / '..' / 'output'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 读取Excel文件F列作为highlight_client输入
            print("📊 读取Mapping.xlsx文件F列...")
            highlight_client_list = read_excel_column_f('Mapping.xlsx')
            print(f"✅ 成功读取到 {len(highlight_client_list)} 个client标记")
            
            # 读取完整的client-tile映射关系
            print("📊 读取client-tile映射关系...")
            tile_client_mapping = read_excel_client_tile_mapping('Mapping.xlsx')
            
            # 创建解析器
            parser = TileParser()

            # 解析数据
            parser.parse_from_csv('MID.csv')
            
            # 检查highlight_client_list中不存在的tile
            available_tiles = set(parser.tiles_dict.keys())
            highlight_client_set = set(highlight_client_list) if highlight_client_list else set()
            missing_client_tiles = highlight_client_set - available_tiles
            
            if missing_client_tiles:
                print(f"⚠️ 检测到 {len(missing_client_tiles)} 个未匹配的tile")
            else:
                print("✅ 所有highlight_client中的tile都已成功匹配")

            # 绘图并保存高分辨率图像
            save_path = output_dir / "tiles_high_res.png"
            print("🎨 开始绘制tile可视化图...")
            parser.plot(
                title="Tile Visualization by Master & Orient",
                save_path=str(save_path),
                dpi=1200,
                highlight_dbg=['soc_df_rpt4_mid_t','soc_df_rpt12_mid_t','soc_df_rpt8_mid_t'],
                highlight_client=highlight_client_list,
                tile_client_mapping=tile_client_mapping,  # 传递映射关系
                show_client_tile_names=show_client_tile_names,  # 传递开关参数
                #highlight_or_gate='pciess_xgmi4_1x8_pcs_ss0_mid_t5'
            )
            print(f"✅ 图像可视化完成")
            
            # 返回分析数据用于报告生成
            return True, missing_client_tiles, len(available_tiles), len(highlight_client_set)
            
        except FileNotFoundError as e:
            print(f"⚠️ 可视化文件错误: {e}")
            return False, set(), 0, 0
        except Exception as e:
            print(f"⚠️ 可视化处理错误: {e}")
            return False, set(), 0, 0

    def analyze_unmatched_json_entries(self):
        """分析JSON中未匹配的条目（空tile_name）"""
        print("\n🔍 分析JSON中未匹配的条目...")
        
        json_file_path = Path(self.output_dir) / "chip_blocks_integrated.json"
        if not json_file_path.exists():
            json_file_path = Path(self.output_dir) / "chip_blocks.json"
        
        unmatched_json_entries = []
        total_pairs = 0
        filled_pairs = 0
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        for json_key, json_entry in json_data.items():
            module = json_entry.get('module', '')
            instance = json_entry.get('instance', '')
            
            if 'pairs' in json_entry:
                for pair in json_entry['pairs']:
                    total_pairs += 1
                    tile_name = pair.get('tile_name', '').strip()
                    dbg_blk_id = pair.get('DbgBlkId', '').strip()
                    
                    if tile_name:
                        filled_pairs += 1
                    else:
                        # 记录未匹配的条目
                        unmatched_json_entries.append({
                            'module': module,
                            'instance': instance,
                            'dbg_blk_id': dbg_blk_id,
                            'json_key': json_key
                        })
        
        return {
            'unmatched_entries': unmatched_json_entries,
            'total_pairs': total_pairs,
            'filled_pairs': filled_pairs,
            'unmatched_count': len(unmatched_json_entries)
        }

    def generate_analysis_report(self, missing_client_tiles=None, available_tiles_count=0, highlight_client_count=0):
        """生成数据分析报告"""
        output_dir = Path(os.path.dirname(__file__)) / '..' / 'output'
        
        # 分析JSON未匹配条目
        json_unmatch_analysis = self.analyze_unmatched_json_entries()
        
        # 创建合并报告
        combined_report_file = output_dir / "data_analysis_report.txt"
        
        warning_messages = []
        
        with open(combined_report_file, 'w', encoding='utf-8') as f:
            f.write("DFD数据分析报告\n")
            f.write("=" * 60 + "\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 第一部分：JSON未填充条目分析
            f.write("第一部分：JSON中未填充tile_name的条目分析\n")
            f.write("-" * 50 + "\n")
            
            f.write(f"JSON数据统计：\n")
            f.write(f"• 总配对数 (pairs): {json_unmatch_analysis['total_pairs']}\n")
            f.write(f"• 已填充tile_name数: {json_unmatch_analysis['filled_pairs']}\n")
            f.write(f"• 未填充tile_name数: {json_unmatch_analysis['unmatched_count']}\n")
            if json_unmatch_analysis['total_pairs'] > 0:
                fill_rate = (json_unmatch_analysis['filled_pairs'] / json_unmatch_analysis['total_pairs']) * 100
                f.write(f"• 填充成功率: {fill_rate:.1f}%\n\n")
            
            # 添加警告信息
            if json_unmatch_analysis['unmatched_count'] > 0:
                warning_messages.append(f"⚠️ JSON未填充条目: {json_unmatch_analysis['unmatched_count']}个")
            
            # 详细列出未匹配的条目
            if json_unmatch_analysis['unmatched_entries']:
                f.write(f"未填充tile_name的详细条目 (前50个):\n")
                f.write("-" * 30 + "\n")
                
                # 按模块分组显示
                entries_by_module = {}
                for entry in json_unmatch_analysis['unmatched_entries']:
                    module = entry['module']
                    if module not in entries_by_module:
                        entries_by_module[module] = []
                    entries_by_module[module].append(entry)
                
                count = 0
                for module, entries in entries_by_module.items():
                    if count >= 50:
                        break
                    f.write(f"\n模块: {module}\n")
                    for entry in entries[:10]:  # 每个模块最多显示10个
                        if count >= 50:
                            break
                        f.write(f"  • 实例: {entry['instance']}, DbgBlkId: {entry['dbg_blk_id']}\n")
                        count += 1
                    if len(entries) > 10:
                        f.write(f"  ... 该模块还有 {len(entries) - 10} 个未匹配条目\n")
                
                if json_unmatch_analysis['unmatched_count'] > 50:
                    f.write(f"\n... 总计还有 {json_unmatch_analysis['unmatched_count'] - 50} 个未显示的未匹配条目\n")
            
            # 第二部分：Tile绘图匹配分析
            f.write("\n第二部分：Tile绘图数据匹配分析\n")
            f.write("-" * 40 + "\n")
            
            if missing_client_tiles is not None:
                f.write(f"总计：{len(missing_client_tiles)} 个highlight_client中的tile在绘图数据中不存在\n\n")
                
                if missing_client_tiles:
                    f.write("详细列表：\n")
                    for i, missing_tile in enumerate(sorted(missing_client_tiles), 1):
                        f.write(f"{i:3d}. {missing_tile}\n")
                        
                    # 添加警告信息
                    warning_messages.append(f"⚠️ 未匹配Tile数量: {len(missing_client_tiles)}个")
                
                f.write(f"\n可用tile总数：{available_tiles_count}\n")
                f.write(f"请求highlight数量：{highlight_client_count}\n")
                matched_count = highlight_client_count - len(missing_client_tiles)
                f.write(f"匹配成功数量：{matched_count}\n")
                if highlight_client_count > 0:
                    f.write(f"匹配成功率：{(matched_count / highlight_client_count * 100):.1f}%\n")
            else:
                f.write("未找到Tile匹配分析数据\n")
                
            # 第三部分：总结和建议
            f.write("\n第三部分：总结和建议\n")
            f.write("-" * 40 + "\n")
            f.write("建议处理步骤：\n")
            f.write("1. 检查Excel文件(Mapping.xlsx)中的模块命名是否与JSON数据一致\n")
            f.write("2. 检查Excel文件中的instance名称是否与JSON数据匹配\n")
            f.write("3. 检查Excel文件中的DbgBlkId是否与JSON数据中的DbgBlkId匹配\n")
            f.write("4. 验证Excel文件F列的Tile名称在MID.csv文件中是否存在\n")
            f.write("5. 确保数据源之间的同步性\n")
            f.write("6. 考虑更新数据映射规则以提高匹配率\n")
            f.write("7. 检查测试数据是否已正确清理\n")
        
        print(f"📄 合并分析报告已保存到: {combined_report_file}")
        return warning_messages

    def run_complete_analysis(self, show_client_tile_names=0):
        """运行完整的DFD分析流程
        
        Args:
            show_client_tile_names: 是否在有client的tile上显示tile名称 (0=不显示, 1=显示)
        """
        try:
            # 处理芯片块解析和JSON生成
            blocks_count, result_count = self.process_chip_blocks()
            
            # 处理Tile可视化
            visualization_success, missing_client_tiles, available_tiles_count, highlight_client_count = self.process_visualization(show_client_tile_names)
            
            # 生成合并报告并获取警告信息
            warning_messages = self.generate_analysis_report(
                missing_client_tiles=missing_client_tiles,
                available_tiles_count=available_tiles_count,
                highlight_client_count=highlight_client_count
            )
            
            return {
                'success': True,
                'blocks_count': blocks_count,
                'result_count': result_count,
                'visualization_success': visualization_success,
                'warning_messages': warning_messages
            }
            
        except FileNotFoundError as e:
            return {
                'success': False,
                'error': f"文件错误: {e}",
                'error_type': 'FileNotFoundError'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"运行错误: {e}",
                'error_type': 'Exception'
            }