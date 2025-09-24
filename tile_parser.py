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
        self.tiles_dict.clear()
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
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

        # 排序并提取 (x, y)
        for data in self.tiles_dict.values():
            data['vertices'].sort(key=lambda v: v[0])
            data['vertices'] = [(x, y) for _, x, y in data['vertices']]

        print(f"✅ 成功解析 {len(self.tiles_dict)} 个 tiles")
        return self

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

    def plot(self, title="Tile Layout Visualization", figsize=(12, 8), show_labels=False, save_path=None, dpi=300, show_legend=False, highlight_centers=None):
        """
        绘图并可选保存为高分辨率图像
        :param title: 图表标题
        :param figsize: 图像大小
        :param show_labels: 是否显示标签
        :param save_path: 图像保存路径（如 'output.png' 或 'output.pdf'), None 表示不保存
        :param dpi: 分辨率(DPI), 默认 300,适合打印/展示
        :param show_legend: 是否显示图例
        """
        if not self.tiles_dict:
            print("⚠️ 无数据可绘图，请先调用 parse_from_csv()")
            return

        fig, ax = plt.subplots(figsize=figsize)
        # 设置spine的线宽
        for spine in ax.spines.values():
            spine.set_linewidth(2.0)  # 将这里改为希望的宽度

        master_color_map = self._get_color_map()

        if highlight_centers:
            if isinstance(highlight_centers, str):
                highlight_centers = [highlight_centers]
            highlight_set = set(highlight_centers)

        for tile_name, data in self.tiles_dict.items():
            vertices = data['vertices']
            if len(vertices) < 3:
                print(f"⚠️  {tile_name} 的顶点少于3个,跳过绘图。")
                continue

            color = master_color_map[data['master']]
            polygon = Polygon(vertices, closed=True, edgecolor='black', facecolor=color, alpha=0.7, linewidth=0.2)
            ax.add_patch(polygon)

            self._draw_orient_marker(ax, vertices, data['orient'])
        
            # 可选：显示标签
            if show_labels:
                centroid_x = np.mean([v[0] for v in vertices])
                centroid_y = np.mean([v[1] for v in vertices])
                label = f"{tile_name}\n({data['orient']})"
                ax.text(centroid_x, centroid_y, label, fontsize=8, ha='center', va='center',
                        color='white', weight='bold',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="gray", alpha=0.7))

            if highlight_centers and tile_name in highlight_set:
                centroid_x = np.mean([v[0] for v in vertices])
                centroid_y = np.mean([v[1] for v in vertices])
                ax.plot(centroid_x, centroid_y, 'o', color='red', markersize=6, alpha=0.8)    

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

        # 可选：显示图例
        if show_legend:
            handles = []
            for master, color in master_color_map.items():
                handles.append(plt.Rectangle((0, 0), 1, 1, facecolor=color, edgecolor='black', alpha=0.7))
            ax.legend(handles, master_color_map.keys(), title="Master", loc='upper right', bbox_to_anchor=(1.15, 1))

        plt.tight_layout()

        # 保存图像
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
            print(f"💾 图像已保存至: {save_path} (DPI={dpi})")

        # 显示图像
        plt.show()

    def __len__(self):
        return len(self.tiles_dict)

    def __bool__(self):
        return bool(self.tiles_dict)