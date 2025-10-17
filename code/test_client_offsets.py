#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Client偏移布局测试工具
用于验证5个client的偏移坐标分布
"""

import matplotlib.pyplot as plt
import numpy as np

def test_client_offsets():
    """测试并可视化5个client的偏移布局"""
    
    # 定义最多5个client的偏移坐标 (x_offset, y_offset)
    offset_positions = [
        (0, 0),        # 第一个client在中心，无偏移
        (100, 100),    # 第二个client右上
        (-100, -100),  # 第三个client左下  
        (100, -100),   # 第四个client右下
        (-100, 100)    # 第五个client左上
    ]
    
    client_names = ['Client_1', 'Client_2', 'Client_3', 'Client_4', 'Client_5']
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    
    # 模拟tile的几何中心
    tile_center_x, tile_center_y = 500, 300
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 绘制tile边界（示例矩形）
    tile_width, tile_height = 400, 200
    from matplotlib.patches import Rectangle
    tile_rect = Rectangle((tile_center_x - tile_width/2, tile_center_y - tile_height/2), 
                         tile_width, tile_height, 
                         linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
    ax.add_patch(tile_rect)
    
    # 绘制client标记
    for i, (client, (offset_x, offset_y), color) in enumerate(zip(client_names, offset_positions, colors)):
        marker_x = tile_center_x + offset_x
        marker_y = tile_center_y + offset_y
        
        ax.plot(marker_x, marker_y, 'o', color=color, markersize=12, alpha=0.8, 
               markeredgecolor='black', markeredgewidth=1)
        
        # 添加标签
        ax.annotate(client, (marker_x, marker_y), xytext=(10, 10), 
                   textcoords='offset points', fontsize=10, 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.7))
        
        # 绘制从中心到标记的连线
        if offset_x != 0 or offset_y != 0:
            ax.plot([tile_center_x, marker_x], [tile_center_y, marker_y], 
                   '--', color=color, alpha=0.5, linewidth=1)
    
    # 标记tile中心
    ax.plot(tile_center_x, tile_center_y, '+', color='black', markersize=15, markeredgewidth=3)
    ax.annotate('Tile Center', (tile_center_x, tile_center_y), xytext=(15, -20), 
               textcoords='offset points', fontsize=12, weight='bold')
    
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 600)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_title('5-Client Offset Layout for Overlapping Tiles', fontsize=16, weight='bold')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    
    # 添加说明文本
    info_text = """Offset Layout:
Client 1: Center (0, 0)
Client 2: Top-Right (+100, +100)
Client 3: Bottom-Left (-100, -100)
Client 4: Bottom-Right (+100, -100)
Client 5: Top-Left (-100, +100)"""
    
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
           verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # 保存图像
    save_path = "../output/client_offset_test.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"💾 偏移布局测试图已保存至: {save_path}")
    
    plt.show()
    
    return offset_positions

def show_real_data_distribution():
    """显示实际数据中的client分布情况"""
    from excel_reader import read_excel_client_tile_mapping
    
    try:
        # 使用更新后的映射函数
        tile_clients = read_excel_client_tile_mapping('Mapping.xlsx')
        
        # 按client数量分组
        client_count_groups = {}
        for tile, clients in tile_clients.items():
            count = len(clients)
            if count not in client_count_groups:
                client_count_groups[count] = []
            client_count_groups[count].append((tile, clients))
        
        print("📊 实际数据中的Client分布:")
        print("=" * 50)
        
        for count in sorted(client_count_groups.keys()):
            tiles = client_count_groups[count]
            print(f"\n{count} 个Client的Tile: {len(tiles)} 个")
            
            if count >= 3:  # 显示有3个或更多client的详细信息
                print("详细信息:")
                for tile, clients in tiles:
                    print(f"  📍 {tile}:")
                    for i, client in enumerate(clients, 1):
                        offset_positions = [
                            (0, 0), (100, 100), (-100, -100), (100, -100), (-100, 100)
                        ]
                        if i <= len(offset_positions):
                            offset = offset_positions[i-1]
                            print(f"    Client {i}: {client} → 偏移{offset}")
        
        print(f"\n✅ 当前支持最多5个client，实际最大需求: {max(client_count_groups.keys())} 个")
        
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    print("🧪 开始Client偏移布局测试")
    print("=" * 50)
    
    # 显示实际数据分布
    show_real_data_distribution()
    
    print("\n🎨 生成偏移布局可视化...")
    test_client_offsets()
    
    print("\n✅ 测试完成！")