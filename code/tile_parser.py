import csv
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
from pathlib import Path
import pickle

"""
Tile数据解析与可视化工具
功能：
    - 从CSV中提取 struct='tile' 的记录
    - 聚合每个tile的顶点
    - 按 master 分组上色
    - 高分辨率图像导出
"""

class TileParser:


    def __init__(self):
        self.tiles_dict = {}  # {tile_name: {master, orient, vertices}}

    def save_data(self, filepath):
        """保存解析后的数据到文件"""
        with open(filepath, 'wb') as f:
            pickle.dump(self.tiles_dict, f)
        print(f"💾 数据已保存至: {filepath}")        
    ## parser.save_data("tiles_data.pkl")

    def parse_from_csv(self, csv_file_path):
        """解析CSV文件"""
        import os
        from pathlib import Path
        
        # 转换为绝对路径
        if not os.path.isabs(csv_file_path):
            csv_file_path = os.path.join(os.path.dirname(__file__), '..', 'input', csv_file_path)
        
        csv_file_path = os.path.abspath(csv_file_path)
        
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"CSV文件不存在: {csv_file_path}")
        
        self.tiles_dict.clear()
        try:
            with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self._process_csv_rows(reader)
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            try:
                with open(csv_file_path, mode='r', newline='', encoding='gbk') as file:
                    reader = csv.DictReader(file)
                    self._process_csv_rows(reader)
            except UnicodeDecodeError:
                with open(csv_file_path, mode='r', newline='', encoding='latin-1') as file:
                    reader = csv.DictReader(file)
                    self._process_csv_rows(reader)        # 排序并提取 (x, y)
        for data in self.tiles_dict.values():
            data['vertices'].sort(key=lambda v: v[0])
            data['vertices'] = [(x, y) for _, x, y in data['vertices']]

        print(f"✅ 成功解析 {len(self.tiles_dict)} 个 tiles")
        return self

    def _process_csv_rows(self, reader):
        """处理CSV行数据"""
        for row in reader:
            if row.get('struct') != 'tile':
                continue

            tile_name = row['tile']
            master = row['master']
            orient = row['orient']
            vertex_idx = int(row['vertex_index'])
            x = float(row['vertex_x'])
            y = float(row['vertex_y'])

            if tile_name not in self.tiles_dict:
                self.tiles_dict[tile_name] = {
                    'master': master,
                    'orient': orient,
                    'vertices': []
                }

            self.tiles_dict[tile_name]['vertices'].append((vertex_idx, x, y))

    def get_data(self):
        """返回数据副本"""
        return self.tiles_dict.copy()

    def _get_color_map(self):

        base_colors = plt.cm.Set3(np.linspace(0, 1, 12))
        pastel1 = plt.cm.Pastel1(np.linspace(0, 1, 9))
        pastel2 = plt.cm.Pastel2(np.linspace(0, 1, 8))
        accent = plt.cm.Accent(np.linspace(0, 1, 8))
        dark2 = plt.cm.Dark2(np.linspace(0, 1, 8))
        all_colors = np.vstack([base_colors, pastel1, pastel2, accent, dark2])
        unique_colors = []
        seen = set()
        for color in all_colors:
            color_tuple = tuple(color)
            if color_tuple not in seen:
                seen.add(color_tuple)
                unique_colors.append(color)
            if len(unique_colors) >= 30:
                break
        unique_masters = sorted(set(data['master'] for data in self.tiles_dict.values()))
        colors = [unique_colors[i % len(unique_colors)] for i in range(len(unique_masters))]
        return {master: colors[i] for i, master in enumerate(unique_masters)}
    
    def _draw_orient_marker(self, ax, vertices, orient):
        """
        根据 orient 类型在多边形对应角上绘制方向角标。
        支持: R0 (左下), MX (左上), MY (右下), R180 (右上)
        在角的两条邻边上各取最小边长的 10% 长度，连成一条短线作为方向标识。
        """
        if orient not in ['R0', 'MX', 'MY', 'R180']:
            return

        # 获取所有顶点的 x 和 y 坐标
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]

        # 根据 orient 确定目标角的坐标
        if orient == 'R0':      # 左下角
            target_x, target_y = min(xs), min(ys)
        elif orient == 'MX':    # 左上角
            target_x, target_y = min(xs), max(ys)
        elif orient == 'MY':    # 右下角
            target_x, target_y = max(xs), min(ys)
        elif orient == 'R180':  # 右上角
            target_x, target_y = max(xs), max(ys)

        # 找到最接近目标角的顶点（可能有多个点接近，取欧氏距离最近的）
        corner = min(vertices, key=lambda v: (v[0] - target_x)**2 + (v[1] - target_y)**2)
        corner_idx = vertices.index(corner)

        n = len(vertices)
        prev_point = vertices[(corner_idx - 1) % n]  # 前一个点
        next_point = vertices[(corner_idx + 1) % n]  # 后一个点

        # 计算边长
        edge_length_1 = ((prev_point[0] - corner[0])**2 + (prev_point[1] - corner[1])**2)**0.5
        edge_length_2 = ((next_point[0] - corner[0])**2 + (next_point[1] - corner[1])**2)**0.5

        # 取最小边长的 10%
        length = 0.1 * min(edge_length_1, edge_length_2)

        # 计算新的点的位置
        p1 = (
            corner[0] + (prev_point[0] - corner[0]) / edge_length_1 * length,
            corner[1] + (prev_point[1] - corner[1]) / edge_length_1 * length
        )
        p2 = (
            corner[0] + (next_point[0] - corner[0]) / edge_length_2 * length,
            corner[1] + (next_point[1] - corner[1]) / edge_length_2 * length
        )

        # 绘制红色短线（角标）
        #ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='red', linewidth=2, solid_capstyle='round')
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='black', linewidth=0.2, alpha=0.5, solid_capstyle='round')
        #ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='black', linewidth=0.2)      

    def _calculate_client_offsets(self, tile_client_mapping):
        """
        计算同一tile中多个client的坐标偏移
        支持最多5个client的智能偏移布局
        
        Args:
            tile_client_mapping: {tile_name: [client1, client2, ...]} 映射关系
            
        Returns:
            {tile_name: [(client_name, offset_x, offset_y), ...]}
            
        偏移布局:
            Client 1: 中心 (0, 0)
            Client 2: 右上 (+50, +50) 
            Client 3: 左上 (-50, +50)
            Client 4: 左下 (-50, -50)
            Client 5: 右下 (+50, -50)
        """
        # 定义最多5个client的偏移坐标 (x_offset, y_offset)
        offset_positions = [
            (0, 0),         # 第一个client在中心，无偏移
            (50, 50),       # 第二个client右上
            (-50, 50),      # 第三个client左下  
            (-50, -50),     # 第四个client右下
            (50, -50)       # 第五个client左上
        ]
        
        tile_offsets = {}
        
        for tile_name, clients in tile_client_mapping.items():
            if tile_name not in self.tiles_dict:
                continue  # 跳过不存在的tile
                
            if len(clients) == 1:
                # 单个client，不需要偏移
                tile_offsets[tile_name] = [(clients[0], 0, 0)]
            else:
                # 多个client，分配偏移坐标
                client_list = []
                for i, client in enumerate(clients[:5]):  # 最多处理5个
                    offset_x, offset_y = offset_positions[i % len(offset_positions)]
                    client_list.append((client, offset_x, offset_y))
                tile_offsets[tile_name] = client_list
                
        return tile_offsets

    def plot(self, title="Tile Layout Visualization", figsize=(12, 8), save_path=None, dpi=300, 
              highlight_dbg=None, highlight_client=None, highlight_or_gate=None, tile_client_mapping=None, show_client_tile_names=0):
        """
        绘图并可选保存为高分辨率图像
        :param title: 图表标题
        :param figsize: 图像大小
        :param save_path: 图像保存路径（如 'output.png' 或 'output.pdf'), None 表示不保存
        :param dpi: 分辨率(DPI), 默认 300,适合打印/展示
        :param highlight_dbg: 调试标记列表
        :param highlight_client: 客户端标记列表  
        :param highlight_or_gate: OR门标记列表
        :param tile_client_mapping: tile到client的映射关系 {tile_name: [client1, client2, ...]}
        :param show_client_tile_names: 是否在有client的tile上显示tile名称 (0=不显示, 1=显示)
        """
        if not self.tiles_dict:
            print("⚠️ 无数据可绘图，请先调用 parse_from_csv()")
            return

        fig, ax = plt.subplots(figsize=figsize)
        # 设置spine的线宽
        for spine in ax.spines.values():
            spine.set_linewidth(2.0)  # 将这里改为希望的宽度

        master_color_map = self._get_color_map()

        def to_set(x):
            return set() if x is None else {x} if isinstance(x, str) else set(x)

        highlight_dbg_set = to_set(highlight_dbg)
        highlight_client_set = to_set(highlight_client)
        highlight_or_gate_set = to_set(highlight_or_gate)
        
        # 检查highlight_client中不存在的tile
        available_tiles = set(self.tiles_dict.keys())
        missing_client_tiles = highlight_client_set - available_tiles
        if missing_client_tiles:
            print("⚠️ 警告：以下highlight_client中的tile在绘图数据中不存在：")
            for missing_tile in sorted(missing_client_tiles):
                print(f"   • {missing_tile}")
            print(f"   总计：{len(missing_client_tiles)} 个未匹配的tile")
        
        # 计算client标记的偏移坐标
        tile_offsets = {}
        if tile_client_mapping:
            tile_offsets = self._calculate_client_offsets(tile_client_mapping)

        def calculate_adaptive_font_size(vertices, tile_name):
            """根据tile尺寸和名称长度计算合适的字体大小"""
            # 计算tile的边界框尺寸
            xs = [v[0] for v in vertices]
            ys = [v[1] for v in vertices]
            width = max(xs) - min(xs)
            height = max(ys) - min(ys)
            
            # 计算最小边长
            min_dimension = min(width, height)
            
            # 基于最小边长计算基础字体大小，降低比例因子
            base_font_size = max(2, min_dimension / 400)  # 更小的基础字体
            
            # 根据字符长度调整
            name_length = len(tile_name)
            if name_length > 15:
                font_size = base_font_size * 0.5
            elif name_length > 12:
                font_size = base_font_size * 0.6
            elif name_length > 8:
                font_size = base_font_size * 0.75
            else:
                font_size = base_font_size
            
            # 限制字体大小范围，更小的范围
            return max(1.5, min(6, font_size))  # 最小1.5pt，最大6pt

        for tile_name, data in self.tiles_dict.items():
            vertices = data['vertices']
            if len(vertices) < 3:
                print(f"⚠️  {tile_name} 的顶点少于3个,跳过绘图。")
                continue

            color = master_color_map[data['master']]
            polygon = Polygon(vertices, closed=True, edgecolor='black', facecolor=color, alpha=0.7, linewidth=0.2)
            ax.add_patch(polygon)

            self._draw_orient_marker(ax, vertices, data['orient'])
        
            # 🔹 分类型绘制中心点标记
            centroid_x = np.mean([v[0] for v in vertices])
            centroid_y = np.mean([v[1] for v in vertices])
    
            # 🔹 先绘制tile名称（如果开关开启），再绘制标记点
            if show_client_tile_names and tile_name in highlight_client_set:
                font_size = calculate_adaptive_font_size(vertices, tile_name)
                
                # 直接显示黑色文字，无背景
                ax.text(centroid_x, centroid_y, tile_name, 
                       fontsize=font_size, 
                       ha='center', va='center',
                       color='black', 
                       weight='normal')  # 无背景，简洁显示
    
            # 🔹 然后绘制标记点，确保在文字之上
            if tile_name in highlight_dbg_set:
                ax.plot(centroid_x, centroid_y, 's', color='blue', markersize=3, alpha=0.8, markeredgecolor='darkblue', markeredgewidth=0.5)
            elif tile_name in highlight_client_set:
                # 检查是否有多个client需要偏移
                if tile_name in tile_offsets:
                    # 有映射关系，绘制所有client标记
                    for client_name, offset_x, offset_y in tile_offsets[tile_name]:
                        marker_x = centroid_x + offset_x
                        marker_y = centroid_y + offset_y
                        ax.plot(marker_x, marker_y, 'o', color='red', markersize=1, alpha=0.8, markeredgecolor='darkred', markeredgewidth=0.01, zorder=10)
                else:
                    # 没有映射关系，使用默认位置
                    ax.plot(centroid_x, centroid_y, 'o', color='red', markersize=1, alpha=0.8, markeredgecolor='darkred', markeredgewidth=0.01, zorder=10)
            elif tile_name in highlight_or_gate_set:
                ax.plot(centroid_x, centroid_y, '^', color='green', markersize=3, alpha=0.8, markeredgecolor='darkgreen', markeredgewidth=0.5)  
    
        # 设置坐标范围
        all_x = [v[0] for data in self.tiles_dict.values() for v in data['vertices']]
        all_y = [v[1] for data in self.tiles_dict.values() for v in data['vertices']]
        ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
        ax.set_ylim(min(all_y) - 1, max(all_y) + 1)

        ax.set_title(title, fontsize=16)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.grid(True, linestyle='--', alpha=0.2)
        ax.set_aspect('equal')

        plt.tight_layout()

        # 保存图像
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
            print(f"💾 图像已保存至: {save_path} (DPI={dpi})")

        # 显示图像（2秒后自动关闭）
        plt.show(block=False)
        plt.pause(2)  # 显示2秒
        plt.close()   # 自动关闭

    def __len__(self):
        return len(self.tiles_dict)

    def __bool__(self):
        return bool(self.tiles_dict)