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
template_columns = template_df.columns.tolist()
print(f"模板列名: {template_columns}")
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
    # 合并时保留所有列
    merged_df = pd.concat(all_data, ignore_index=True)

    # 确定最终的列顺序：按照模板列顺序，如果有"品类"列则插入到"报告名称"之后
    final_columns = []
    if '编号' in merged_df.columns:
        final_columns.append('编号')
    if '报告名称' in merged_df.columns:
        final_columns.append('报告名称')
    if '品类' in merged_df.columns:
        final_columns.append('品类')
    if '负责人' in merged_df.columns:
        final_columns.append('负责人')
    if '日期' in merged_df.columns:
        final_columns.append('日期')

    # 重新排列列顺序
    merged_df = merged_df[final_columns]

    # 重新编号
    merged_df['编号'] = range(1, len(merged_df) + 1)

    # 对于没有"品类"的行，填充空值
    if '品类' in merged_df.columns:
        merged_df['品类'] = merged_df['品类'].fillna('')

    print(f"合并后总行数: {len(merged_df)}")
    print(f"合并后列名: {merged_df.columns.tolist()}")
    print(f"\n数据预览（前5行）:")
    print(merged_df.head())

    # 保存到新文件
    output_file = '2025年报告明细统计表-汇总.xlsx'
    print(f"\n正在保存到: {output_file}")

    # 使用 openpyxl 引擎保存，并设置列宽
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        merged_df.to_excel(writer, sheet_name='Sheet1', index=False)

        # 获取工作表并设置列宽
        worksheet = writer.sheets['Sheet1']
        worksheet.column_dimensions['A'].width = 8   # 编号
        worksheet.column_dimensions['B'].width = 50  # 报告名称
        if '品类' in merged_df.columns:
            worksheet.column_dimensions['C'].width = 15  # 品类
            worksheet.column_dimensions['D'].width = 12  # 负责人
            worksheet.column_dimensions['E'].width = 12  # 日期
        else:
            worksheet.column_dimensions['C'].width = 12  # 负责人
            worksheet.column_dimensions['D'].width = 12  # 日期

    print(f"\n✓ 汇总完成！文件已保存为: {output_file}")
    print(f"  - 总计 {len(merged_df)} 条记录")
    print(f"  - 列: {', '.join(final_columns)}")
else:
    print("错误: 没有数据可以合并")
