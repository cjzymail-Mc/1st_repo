# -*- coding: utf-8 -*-
import pandas as pd
import openpyxl
from pathlib import Path
import sys

# 设置输出编码
sys.stdout.reconfigure(encoding='utf-8')

# 文件路径
excel_dir = Path('excel')
template_file = excel_dir / '模板.xlsx'

# 需要汇总的文件列表
files_to_merge = [
    '2025 【运动表现研究部报告统计】隋晗.xlsx',
    '2025 庄旭宏报告统计.xlsx',
    '徐亮—2025年报告明细统计表.xlsx',
    '延领—2025年报告明细统计表.xlsx',
    '杨祖锐—2025年报告明细统计表.xlsx',
    '张宇昂—2025年报告明细统计表.xlsx'
]

print("=== 开始处理Excel文件汇总 ===\n")

# 读取模板文件以了解结构
print(f"正在读取模板文件: {template_file.name}")
template_df = pd.read_excel(template_file, sheet_name='Sheet1')
print(f"模板列名: {template_df.columns.tolist()}")
print(f"模板数据行数: {len(template_df)}\n")

# 存储所有数据
all_data = []

# 读取每个文件
for filename in files_to_merge:
    file_path = excel_dir / filename
    print(f"正在读取: {filename}")

    try:
        # 读取第一个工作表
        df = pd.read_excel(file_path, sheet_name=0)
        print(f"  - 列名: {df.columns.tolist()}")
        print(f"  - 数据行数: {len(df)}")

        # 添加到汇总列表
        all_data.append(df)
    except Exception as e:
        print(f"  - 错误: {e}")

    print()

# 合并所有数据
print("=== 开始合并数据 ===")
if all_data:
    merged_df = pd.concat(all_data, ignore_index=True)
    print(f"合并后总行数: {len(merged_df)}")
    print(f"合并后列名: {merged_df.columns.tolist()}\n")

    # 重新编号（如果有序号列）
    if '序号' in merged_df.columns:
        merged_df['序号'] = range(1, len(merged_df) + 1)

    # 保存到新文件
    output_file = '2025年报告明细统计表-汇总.xlsx'
    print(f"正在保存到: {output_file}")

    # 使用模板的格式保存
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        merged_df.to_excel(writer, sheet_name='Sheet1', index=False)

    print(f"\n✓ 汇总完成！文件已保存为: {output_file}")
    print(f"  - 总计 {len(merged_df)} 条记录")
else:
    print("错误: 没有数据可以合并")
