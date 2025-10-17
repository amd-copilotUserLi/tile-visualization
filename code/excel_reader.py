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

def test_excel_reader():
    """测试Excel读取功能"""
    try:
        values = read_excel_column_f("Mapping.xlsx")
        print(f"读取到的F列值:")
        for i, value in enumerate(values, 1):
            print(f"  {i}: {value}")
        return values
    except Exception as e:
        print(f"测试失败: {e}")
        return []

if __name__ == "__main__":
    test_excel_reader()