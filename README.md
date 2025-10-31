# DFD Automation Tool

一个用于处理芯片设计数据的自动化工具，支持芯片块解析、Excel数据整合、Tile可视化和数据分析。

## 📋 功能概览

1. **芯片块解析和JSON生成**
2. **Excel数据整合** 
3. **Tile可视化**
4. **数据映射和清理**
5. **未匹配数据分析**

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 必需的Python包：
  ```bash
  pip install pandas openpyxl matplotlib numpy pathlib
  ```

### 基本使用

1. 将输入文件放入 `input/` 目录：
   - `CHIP.txt` - 芯片设计文件
   - `MID.csv` - Tile数据文件  
   - `Mapping.xlsx` - Excel映射文件

2. 运行主程序：
   ```bash
   python main.py
   ```

3. 查看输出结果（`output/` 目录）：
   - `chip_blocks.json` - 原始JSON数据
   - `chip_blocks_integrated.json` - 整合后的JSON数据
   - `tiles_high_res.png` - 高分辨率可视化图像
   - `data_analysis_report.txt` - 数据分析报告

## 🔧 配置选项

在 `main.py` 中修改 `expand_dict` 来配置变量展开规则：

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

## � 项目结构

```
automation/
├── code/
│   ├── main.py                    # 主程序入口 (用户配置)
│   ├── dfd_processor.py           # 核心处理逻辑
│   ├── chip_parser.py             # 芯片数据解析
│   ├── tile_parser.py             # Tile可视化处理
│   ├── excel_reader.py            # Excel文件读取
│   ├── json_excel_integrator.py   # JSON-Excel数据整合
│   └── ...
├── input/
│   ├── CHIP.txt
│   ├── MID.csv  
│   └── Mapping.xlsx
└── output/
    ├── chip_blocks.json
    ├── chip_blocks_integrated.json
    ├── tiles_high_res.png
    └── data_analysis_report.txt
```

## ✨ Enhancement 历史

### v3.0 - 代码重构与模块化 (2025-10-31)
- **重构main.py**: 从280+行精简到52行
- **创建DFDProcessor类**: 封装所有核心处理逻辑
- **模块化设计**: 提高代码可维护性和可扩展性
- **简化用户接口**: 只需配置expand_dict即可

### v2.3 - 报告系统优化 (2025-10-31)
- **统一报告文件**: 只生成`data_analysis_report.txt`一个报告文件
- **删除冗余报告**: 移除`unmatched_analysis_report.txt`、`missing_tiles_report.txt`等
- **内存数据处理**: 直接从内存传递分析结果，减少文件I/O
- **最终警示输出**: 在程序结束时显示警告摘要

### v2.2 - 未匹配数据检查增强 (2025-10-31)
- **Tile匹配验证**: 检查highlight_client中不存在的tile
- **实时警告显示**: 在绘图过程中显示未匹配tile警告
- **详细报告生成**: 生成包含统计信息的未匹配分析报告
- **匹配率统计**: 提供匹配成功率和详细数量统计

### v2.1 - 数据分析报告合并 (2025-10-31)
- **合并分析报告**: 将Excel-JSON和Tile分析合并到统一报告
- **警示信息集中**: 在程序最后显示所有警告信息
- **维护友好输出**: 便于调试和问题排查

### v2.0 - 未匹配数据分析系统 (2025-10-31)
- **Excel-JSON匹配分析**: 分析JSON与Excel数据之间的匹配情况
- **模块级去重统计**: 提供按模块去重的未匹配数据统计
- **详细分析报告**: 生成JSON和文本格式的分析报告
- **匹配问题诊断**: 识别数据不一致的具体原因

### v1.3 - 客户端标记可视化增强 (2025-10-31)
- **5客户端支持**: 支持每个tile最多5个客户端标记
- **精确偏移定位**: 使用±50单位的顺时针偏移模式
- **高精度标记**: markersize=1, markeredgewidth=0.01的精确显示
- **映射关系处理**: 完整的client-tile映射关系支持

### v1.2 - Excel F列集成 (2025-10-31)
- **F列数据提取**: 自动读取Excel文件F列作为highlight_client
- **数据清理优化**: 改进DbgBlkId清理逻辑
- **tile_name填充**: 自动填充Excel数据中的tile_name字段
- **集成流程优化**: 简化JSON-Excel数据整合流程

### v1.1 - JSON-Excel数据整合 (2025-10-31)
- **数据映射系统**: 建立JSON和Excel数据之间的映射关系
- **DbgBlkId清理**: 自动清理和标准化DbgBlkId格式
- **tile_name更新**: 根据映射关系更新tile名称
- **整合验证**: 添加数据整合结果验证机制

### v1.0 - 基础功能实现 (2025-10-31)
- **芯片块解析**: 解析CHIP.txt文件并生成JSON结构
- **变量展开**: 支持可配置的实例名称变量展开
- **Tile可视化**: 高分辨率Tile布局可视化
- **Excel数据读取**: 支持Excel文件数据提取

## � 数据分析功能

### 匹配分析
- **Excel-JSON匹配**: 分析模块和实例的匹配情况
- **Tile绘图匹配**: 检查highlight_client中的tile是否存在
- **匹配率统计**: 提供详细的匹配成功率

### 报告生成
- **统一分析报告**: `data_analysis_report.txt`包含所有分析结果
- **分类问题识别**: 按问题类型分类显示未匹配项
- **处理建议**: 提供数据修复和同步建议

### 实时反馈
- **进度显示**: 详细的处理进度和状态信息
- **警告提示**: 实时显示数据匹配问题
- **最终摘要**: 程序结束时的警告信息汇总

## 🎨 可视化功能

### Tile可视化
- **高分辨率输出**: 1200 DPI的PNG图像
- **Master分组着色**: 按Master字段自动分组着色
- **Orient方向标记**: 显示Tile的方向信息

### 客户端标记
- **多客户端支持**: 每个tile支持最多5个客户端标记  
- **精确偏移**: ±50单位的clockwise偏移模式
- **可视化层次**: 不同类型的标记使用不同样式

### 调试支持
- **highlight_dbg**: 蓝色方形标记用于调试
- **highlight_client**: 红色圆形标记用于客户端
- **highlight_or_gate**: 绿色三角标记用于OR门

## �🔍 故障排除

### 常见问题

1. **文件未找到错误**
   - 确保输入文件在正确的目录中
   - 检查文件名是否正确

2. **匹配率较低**
   - 检查Excel文件中的模块命名
   - 验证JSON数据的完整性
   - 查看data_analysis_report.txt了解详细原因

3. **可视化问题**
   - 确保MID.csv文件格式正确
   - 检查highlight_client中的tile名称是否存在

### 调试方法

1. 查看控制台输出的详细日志
2. 检查`data_analysis_report.txt`分析报告
3. 验证输入文件的数据格式
4. 检查`expand_dict`配置是否正确

## 🚀 未来规划

- [ ] 支持更多的输入文件格式
- [ ] 添加交互式可视化界面
- [ ] 实现批量处理功能
- [ ] 增强数据验证机制
- [ ] 支持自定义可视化样式

## � 许可证

本项目使用 MIT 许可证。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

---

*最后更新: 2025-10-31*