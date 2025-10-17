# DFD自动化工具 (DFD Automation Tool)

一个用于芯片设计数据处理和可视化的自动化工具套件。

## 🎯 功能概述

### 核心功能
- **芯片块解析**: 解析CHIP.txt文件，提取模块和实例信息
- **变量展开**: 支持配置化的实例名称变量展开规则
- **Excel数据整合**: 自动整合Mapping.xlsx中的tile映射数据
- **数据清理**: 清理DbgBlkId格式，填充空白的tile_name字段
- **高分辨率可视化**: 生成Tile布局的高质量可视化图像

### 输出文件
- `chip_blocks.json`: 原始解析结果
- `chip_blocks_integrated.json`: 整合Excel数据后的完整结果
- `tiles_high_res.png`: 1200 DPI高分辨率可视化图像

## 📁 项目结构

```
automation/
├── code/
│   ├── main.py                    # 🎯 统一主程序入口
│   ├── chip_parser.py             # 芯片解析器
│   ├── tile_parser.py             # Tile解析器  
│   ├── excel_reader.py            # Excel读取工具
│   ├── json_excel_integrator.py   # JSON-Excel整合工具
│   └── expand_chip_blocks.py      # 块展开工具
├── input/
│   ├── CHIP.txt                   # 芯片定义文件
│   ├── MID.csv                    # Tile数据文件
│   └── Mapping.xlsx               # 映射数据文件 (可选)
├── output/                        # 自动生成目录
│   ├── chip_blocks.json           # 原始JSON数据
│   ├── chip_blocks_integrated.json # 整合后的完整数据
│   └── tiles_high_res.png         # 高分辨率可视化图像
└── README.md                      # 项目说明文档
```

## 🚀 快速开始

### 环境要求
- Python 3.x
- 依赖包: `pandas`, `openpyxl`, `matplotlib`, `numpy`

### 安装依赖
```bash
pip install pandas openpyxl matplotlib numpy
```

### 使用方法
1. 确保输入文件位于 `input/` 目录：
   - `CHIP.txt` (必需): 芯片定义文件
   - `MID.csv` (必需): Tile数据文件
   - `Mapping.xlsx` (可选): 映射数据文件

2. 运行主程序：
```bash
cd code
python main.py
```

3. 查看 `output/` 目录中的生成文件

## 🔧 配置选项

### 变量展开规则
在 `main.py` 中可以配置变量展开规则：

```python
expand_dict = {
    "$SSA": [0],
    "$SSB": [0,1],
    "$SSC": [0,1],
    "$smn_ssbdci_wafl_inst":[0,1],
    "$ucis_x4_inst" : [0,1,2,3,4,5],
    "$ucis_left_inst" : [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
    "$ucis_right_inst" : [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
}
```

### 可视化参数
可在 `process_visualization()` 函数中调整：
- `dpi`: 图像分辨率 (默认1200)
- `highlight_dbg`: 需要高亮显示的调试块
- `highlight_client`: 从Excel F列读取的客户端标记

## 📊 处理流程

### 第一步：芯片块处理
1. 解析CHIP.txt文件中的模块定义
2. 应用变量展开规则
3. 生成原始JSON数据 (`chip_blocks.json`)

### 第二步：Excel数据整合 (可选)
1. 检测是否存在 `Mapping.xlsx` 文件
2. 读取A列(module)、B列(instance)、C列(DbgBlkId)、F列(tile_name)
3. 清理DbgBlkId格式 (移除点号和括号)
4. 根据module::instance匹配，填充空白的tile_name
5. 生成整合后的JSON数据 (`chip_blocks_integrated.json`)

### 第三步：Tile可视化
1. 从Mapping.xlsx的F列读取highlight_client数据
2. 解析MID.csv文件中的Tile布局信息
3. 生成高分辨率可视化图像 (`tiles_high_res.png`)

## 📈 处理统计

典型处理结果示例：
- **芯片块处理**: 393个原始块 → 71个展开结果
- **Excel整合**: 151条映射记录 → 103个tile_name填充 (30.1%成功率)
- **可视化**: 518个tiles，146个highlight标记

## 🛠️ 技术特性

### 数据处理
- **正则表达式解析**: 支持多种芯片定义语法格式
- **变量展开**: 灵活的实例名称模板处理
- **数据清理**: 自动清理和标准化数据格式
- **容错处理**: 完善的错误处理和异常捕获

### 文件操作
- **编码支持**: UTF-8编码处理，支持中文字符
- **路径处理**: 跨平台路径处理
- **自动创建**: 输出目录自动创建

### 可视化
- **高分辨率**: 支持1200 DPI输出
- **自定义高亮**: 支持多种高亮标记类型
- **图例控制**: 可配置图例显示

## 📝 输出文件说明

### chip_blocks.json
原始芯片块解析结果，包含：
- 模块名称和实例名称
- DbgBlkId对数组 (原始格式)
- 空的tile_name字段

### chip_blocks_integrated.json
整合Excel数据后的完整结果，包含：
- 清理后的DbgBlkId (移除格式符号)
- 填充的tile_name字段
- 完整的模块映射关系

### tiles_high_res.png
高分辨率Tile可视化图像，特点：
- 1200 DPI分辨率
- 按Master和Orient分组的颜色编码
- highlight_client和highlight_dbg标记
- 清晰的布局和标签

## 🔍 故障排除

### 常见问题
1. **文件未找到**: 确保输入文件位于正确的目录
2. **编码错误**: 确保文件使用UTF-8编码保存
3. **Excel读取失败**: 检查Mapping.xlsx文件格式和列结构
4. **内存不足**: 大文件处理时可能需要增加系统内存

### 调试信息
程序运行时会输出详细的处理信息：
- ✅ 成功操作
- ⚠️ 警告信息  
- ❌ 错误信息
- 🔄 处理进度

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个工具。

## 📄 许可证

本项目采用开源许可证，详见LICENSE文件。

---

*最后更新: 2025年10月17日*