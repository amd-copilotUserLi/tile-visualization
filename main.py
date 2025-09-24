'''
tile_visualization/
│
├── tile_parser.py          # 核心类:TileParser
├── main.py                 # 主程序入口（调用类）
├── config.py               # 配置参数（可选）
└── output/                 # 自动保存图像的目录（运行时生成）
'''

# main.py
from tile_parser import TileParser

def main():
    # 创建解析器
    parser = TileParser()

    # 解析数据
    parser.parse_from_csv('your_file.csv')  # 替换为你的文件路径

    # 绘图并保存高分辨率图像
    parser.plot(
        title="Tile Visualization by Master & Orient",
        show_labels=False,
        save_path="output/tiles_high_res.png",  # 推荐 PDF 矢量图
        dpi=1200,
        show_legend=False,
        highlight_centers=['pciess_serdes_cphy444444_ss1_mid_t', 'pciess_serdes_cphy4444_ss2_mid_t0']
    )

if __name__ == "__main__":
    main()