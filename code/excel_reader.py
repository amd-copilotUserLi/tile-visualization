#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel文件读取工具
用于读取Mapping.xlsx文件中的数据
"""

import pandas as pd
import os
from pathlib import Path

def read_excel_column_f(excel_file_path):
    """
    读取Excel文件F列的内容（跳过表头）
    
    Args:
        excel_file_path: Excel文件路径
        
    Returns:
        list: F列中有内容的值列表
    """
    # 转换为绝对路径
    if not os.path.isabs(excel_file_path):
        excel_file_path = os.path.join(os.path.dirname(__file__), '..', 'input', excel_file_path)
    
    excel_file_path = os.path.abspath(excel_file_path)
    
    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"Excel文件不存在: {excel_file_path}")
    
    try:
        # 读取Excel文件，指定F列（索引为5）
        # 使用usecols=[5]只读取F列，skiprows=1跳过表头
        df = pd.read_excel(excel_file_path, usecols=[5], skiprows=1, header=None)
        
        # 获取F列数据（列索引为5，但由于只读取了一列，所以是索引0）
        f_column = df.iloc[:, 0]
        
        # 过滤掉空值（NaN, None, 空字符串）
        valid_values = []
        for value in f_column:
            if pd.notna(value) and str(value).strip():  # 不是NaN且不是空字符串
                valid_values.append(str(value).strip())
        
        print(f"✅ 从Excel文件读取到 {len(valid_values)} 个有效的F列值")
        return valid_values
        
    except Exception as e:
        print(f"❌ 读取Excel文件时出错: {e}")
        return []

def read_excel_client_tile_mapping(excel_file_path):
    """
    读取Excel文件，返回client到tile_name的映射关系
    
    Args:
        excel_file_path: Excel文件路径
        
    Returns:
        dict: {tile_name: [client1, client2, ...]} 映射关系
    """
    # 转换为绝对路径
    if not os.path.isabs(excel_file_path):
        excel_file_path = os.path.join(os.path.dirname(__file__), '..', 'input', excel_file_path)
    
    excel_file_path = os.path.abspath(excel_file_path)
    
    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"Excel文件不存在: {excel_file_path}")
    
    try:
        # 读取A列(BIA module)、B列(BIA instance)和F列(tile name)
        df = pd.read_excel(excel_file_path, usecols=[0, 1, 5], skiprows=1, header=None)
        
        # 重命名列
        df.columns = ['module', 'instance', 'tile_name']
        
        # 过滤掉空值
        df = df.dropna()
        
        # 读取更多列来更好地区分client
        df_full = pd.read_excel(excel_file_path, usecols=[0, 1, 2, 3, 4, 5], skiprows=1, header=None)
        df_full.columns = ['module', 'instance', 'dbg_blk_id', 'flatten_module', 'flatten_instance', 'tile_name']
        df_full = df_full.dropna(subset=['tile_name'])
        
        # 创建tile_name到client的映射
        tile_clients = {}
        for _, row in df_full.iterrows():
            module = str(row['module']).strip()
            instance = str(row['instance']).strip() 
            dbg_blk_id = str(row['dbg_blk_id']).strip()
            flatten_module = str(row['flatten_module']).strip()
            tile_name = str(row['tile_name']).strip()
            
            if tile_name and module and instance and dbg_blk_id != 'nan':
                # 使用DbgBlkId作为更精确的client标识
                client_id = f"{module}::{instance}::{dbg_blk_id}"
                
                if tile_name not in tile_clients:
                    tile_clients[tile_name] = []
                
                if client_id not in tile_clients[tile_name]:
                    tile_clients[tile_name].append(client_id)
        
        # 统计信息
        multi_client_tiles = {k: v for k, v in tile_clients.items() if len(v) > 1}
        
        print(f"✅ 读取到 {len(tile_clients)} 个tile的映射关系")
        if multi_client_tiles:
            print(f"📊 其中 {len(multi_client_tiles)} 个tile有多个client:")
            for tile, clients in list(multi_client_tiles.items())[:5]:  # 只显示前5个
                print(f"  {tile}: {len(clients)} 个client")
            if len(multi_client_tiles) > 5:
                print(f"  ... 还有 {len(multi_client_tiles) - 5} 个")
        
        return tile_clients
        
    except Exception as e:
        print(f"❌ 读取Excel映射关系时出错: {e}")
        return {}

def test_excel_reader():
    """测试Excel读取功能"""
    try:
        # 测试F列读取
        values = read_excel_column_f("Mapping.xlsx")
        print(f"F列读取测试 - 读取到 {len(values)} 个值")
        
        # 测试完整映射读取
        mapping = read_excel_client_tile_mapping("Mapping.xlsx")
        print(f"映射关系读取测试 - 读取到 {len(mapping)} 个tile映射")
        
        return values, mapping
    except Exception as e:
        print(f"测试失败: {e}")
        return [], {}

if __name__ == "__main__":
    test_excel_reader()