'''
DFD Automation Tool - 统一主程序
功能包括：
1. 芯片块解析和JSON生成
2. Excel数据整合
3. Tile可视化
4. 数据映射和清理
'''

from dfd_processor import DFDProcessor

# 用户可在此配置变量展开规则
expand_dict = {
    "$SSA": [0],
    "$SSB": [0,1],
    "$SSC": [0,1],
    "$smn_ssbdci_wafl_inst":[0,1],
    "$ucis_x4_inst" : [0,1,2,3,4,5],
    "$ucis_left_inst" : [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
    "$ucis_right_inst" : [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
}

def main():
    """主程序入口 - 整合所有功能"""
    print("🚀 DFD自动化工具启动")
    print("=" * 50)
    
    # 🔧 用户配置参数
    # 设置为1开启有client的tile上显示tile名称功能，设置为0关闭此功能（默认）
    show_client_tile_names = 1  # 用户可在此修改：0=不显示, 1=显示tile名称
    
    # 创建处理器实例
    processor = DFDProcessor(expand_dict)
    
    # 运行完整分析流程（传入开关参数）
    result = processor.run_complete_analysis(show_client_tile_names=show_client_tile_names)
    
    # 输出结果
    print("\n" + "=" * 50)
    
    if result['success']:
        print("📋 处理总结:")
        print(f"   📦 芯片块处理: {result['blocks_count']} 个原始块 → {result['result_count']} 个展开结果")
        print(f"   🎨 可视化处理: {'✅ 成功' if result['visualization_success'] else '❌ 失败'}")
        
        # 输出警示信息
        if result['warning_messages']:
            print("\n🚨 数据分析警告:")
            for warning in result['warning_messages']:
                print(f"   {warning}")
            print("   📄 详细信息请查看: output/data_analysis_report.txt")
        else:
            print("\n✅ 所有数据匹配检查通过，无警告信息")
            
        print("✅ DFD自动化工具处理完成")
    else:
        print(f"❌ {result['error']}")

if __name__ == "__main__":
    main()