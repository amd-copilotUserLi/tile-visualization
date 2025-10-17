#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON和Excel数据整合工具
用于整合chip_blocks.json和Mapping.xlsx的数据
"""

import pandas as pd
import json
import os
import re
from pathlib import Path

def read_excel_mapping_data(excel_file_path):
    """
    读取Excel文件的A、B、C、F列数据（跳过表头）
    
    Args:
        excel_file_path: Excel文件路径
        
    Returns:
        list: 包含mapping数据的字典列表
    """
    # 转换为绝对路径
    if not os.path.isabs(excel_file_path):
        excel_file_path = os.path.join(os.path.dirname(__file__), '..', 'input', excel_file_path)
    
    excel_file_path = os.path.abspath(excel_file_path)
    
    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"Excel文件不存在: {excel_file_path}")
    
    try:
        # 读取Excel文件的A、B、C、F列（索引为0、1、2、5）
        df = pd.read_excel(excel_file_path, usecols=[0, 1, 2, 5], skiprows=1, header=None)
        
        # 重命名列
        df.columns = ['module', 'instance', 'dbg_blk_id', 'tile_name']
        
        # 过滤掉所有列都为空的行
        mapping_data = []
        for _, row in df.iterrows():
            # 检查是否有有效数据（至少module、instance、dbg_blk_id不为空）
            if (pd.notna(row['module']) and str(row['module']).strip() and
                pd.notna(row['instance']) and str(row['instance']).strip() and
                pd.notna(row['dbg_blk_id']) and str(row['dbg_blk_id']).strip()):
                
                mapping_entry = {
                    'module': str(row['module']).strip(),
                    'instance': str(row['instance']).strip(),
                    'dbg_blk_id': str(row['dbg_blk_id']).strip(),
                    'tile_name': str(row['tile_name']).strip() if pd.notna(row['tile_name']) and str(row['tile_name']).strip() else ""
                }
                mapping_data.append(mapping_entry)
        
        print(f"✅ 从Excel文件读取到 {len(mapping_data)} 条有效的mapping数据")
        return mapping_data
        
    except Exception as e:
        print(f"❌ 读取Excel文件时出错: {e}")
        return []

def clean_dbg_blk_id(dbg_blk_id_str):
    """
    清理DbgBlkId字符串，去掉前缀的.和后缀的()及其内容
    
    Args:
        dbg_blk_id_str: 原始的DbgBlkId字符串，如 ".PCSIP_dbg_client_DbgBlkId(0),"
        
    Returns:
        str: 清理后的DbgBlkId，如 "PCSIP_dbg_client_DbgBlkId"
    """
    # 去掉前导的.
    cleaned = dbg_blk_id_str.lstrip('.')
    
    # 去掉()及其内容和后面的逗号
    cleaned = re.sub(r'\([^)]*\)[,]*', '', cleaned)
    
    # 去掉其他可能的特殊字符
    cleaned = cleaned.strip().rstrip(',')
    
    return cleaned

def integrate_json_excel_data(json_file_path, excel_file_path, output_file_path):
    """
    整合JSON和Excel数据
    
    Args:
        json_file_path: JSON文件路径
        excel_file_path: Excel文件路径
        output_file_path: 输出文件路径
    """
    
    # 读取JSON数据
    print("📖 读取JSON文件...")
    if not os.path.isabs(json_file_path):
        json_file_path = os.path.join(os.path.dirname(__file__), '..', 'output', json_file_path)
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    print(f"✅ JSON文件包含 {len(json_data)} 个条目")
    
    # 读取Excel数据
    print("📊 读取Excel mapping数据...")
    excel_mapping = read_excel_mapping_data(excel_file_path)
    
    if not excel_mapping:
        print("❌ 没有读取到有效的Excel映射数据")
        return
    
    # 创建Excel数据的查找字典
    excel_lookup = {}
    for entry in excel_mapping:
        key = f"{entry['module']}::{entry['instance']}"
        if key not in excel_lookup:
            excel_lookup[key] = []
        excel_lookup[key].append(entry)
    
    print(f"✅ 创建了 {len(excel_lookup)} 个模块::实例映射")
    
    # 整合数据
    print("🔄 开始数据整合...")
    updated_count = 0
    cleaned_count = 0
    
    for json_key, json_entry in json_data.items():
        module = json_entry.get('module', '')
        instance = json_entry.get('instance', '')
        lookup_key = f"{module}::{instance}"
        
        # 处理pairs数组
        if 'pairs' in json_entry:
            for pair in json_entry['pairs']:
                # 清理DbgBlkId
                if 'DbgBlkId' in pair:
                    original_dbg = pair['DbgBlkId']
                    cleaned_dbg = clean_dbg_blk_id(original_dbg)
                    pair['DbgBlkId'] = cleaned_dbg
                    cleaned_count += 1
                
                # 查找匹配的Excel数据
                if lookup_key in excel_lookup:
                    for excel_entry in excel_lookup[lookup_key]:
                        # 匹配DbgBlkId
                        if cleaned_dbg == excel_entry['dbg_blk_id']:
                            # 更新tile_name
                            if excel_entry['tile_name'] and not pair.get('tile_name'):
                                pair['tile_name'] = excel_entry['tile_name']
                                updated_count += 1
                                break
    
    print(f"✅ 清理了 {cleaned_count} 个DbgBlkId")
    print(f"✅ 更新了 {updated_count} 个tile_name")
    
    # 保存整合后的数据
    print("💾 保存整合后的数据...")
    if not os.path.isabs(output_file_path):
        output_file_path = os.path.join(os.path.dirname(__file__), '..', 'output', output_file_path)
    
    # 确保输出目录存在
    Path(output_file_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 整合完成，结果已保存到: {output_file_path}")
    
    return json_data

def analyze_integration_results(original_json_path, integrated_json_path):
    """
    分析整合结果
    """
    print("\n📊 分析整合结果...")
    
    # 读取原始JSON
    with open(original_json_path, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    # 读取整合后的JSON
    with open(integrated_json_path, 'r', encoding='utf-8') as f:
        integrated_data = json.load(f)
    
    # 统计数据
    original_empty_tiles = 0
    integrated_filled_tiles = 0
    total_pairs = 0
    
    for key, entry in original_data.items():
        if 'pairs' in entry:
            for pair in entry['pairs']:
                total_pairs += 1
                if not pair.get('tile_name'):
                    original_empty_tiles += 1
    
    for key, entry in integrated_data.items():
        if 'pairs' in entry:
            for pair in entry['pairs']:
                if pair.get('tile_name'):
                    integrated_filled_tiles += 1
    
    print(f"📈 统计结果:")
    print(f"   总配对数: {total_pairs}")
    print(f"   原始空tile_name: {original_empty_tiles}")
    print(f"   整合后已填充: {integrated_filled_tiles}")
    print(f"   填充成功率: {integrated_filled_tiles/total_pairs*100:.1f}%")

def main():
    """主函数"""
    print("🚀 开始JSON和Excel数据整合...")
    print("=" * 60)
    
    try:
        # 整合数据
        integrated_data = integrate_json_excel_data(
            "chip_blocks.json",
            "Mapping.xlsx", 
            "chip_blocks_integrated.json"
        )
        
        if integrated_data:
            # 分析结果
            analyze_integration_results(
                os.path.join(os.path.dirname(__file__), '..', 'output', 'chip_blocks.json'),
                os.path.join(os.path.dirname(__file__), '..', 'output', 'chip_blocks_integrated.json')
            )
            
            print("\n🎉 数据整合完成！")
        else:
            print("❌ 数据整合失败")
            
    except Exception as e:
        print(f"❌ 整合过程中出错: {e}")

if __name__ == "__main__":
    main()