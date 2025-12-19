import pandas as pd

# --- 配置区 ---
input_file = '柬埔寨电缆商_TG验证最终版.xlsx'
output_vcf = '柬埔寨电缆商_带标签导入包.vcf'
# 统一的前缀，方便你以后在搜索框输入“电缆”两个字，所有人就全出来了
name_prefix = "[电缆] " 

def generate_vcf_with_tag():
    try:
        df = pd.read_excel(input_file)
    except FileNotFoundError:
        print("❌ 找不到文件，请确认文件名。")
        return

    # 只导出“已注册”且有电话的
    mask = (df['Telegram状态'] == '已注册')
    registered_df = df[mask]
    
    if registered_df.empty:
        print("⚠️ 没有找到已注册的客户。")
        return

    vcf_content = ""
    for index, row in registered_df.iterrows():
        original_name = str(row['企业名称']).strip()
        # 【核心优化】：给名字加上前缀
        display_name = name_prefix + original_name
        
        phone = str(row['联系电话']).strip()
        formatted_phone = phone.replace(" ", "").replace("-", "")
        if formatted_phone.startswith('0'):
            formatted_phone = '+855' + formatted_phone[1:]
        elif not formatted_phone.startswith('+'):
            formatted_phone = '+855' + formatted_phone

        vcf_content += "BEGIN:VCARD\n"
        vcf_content += "VERSION:3.0\n"
        vcf_content += f"FN:{display_name}\n"      # 通讯录显示的完整姓名
        vcf_content += f"ORG:{original_name}\n"    # 公司名字段保持原始
        vcf_content += f"TEL;TYPE=CELL:{formatted_phone}\n"
        vcf_content += "END:VCARD\n"

    with open(output_vcf, 'w', encoding='utf-8') as f:
        f.write(vcf_content)

    print(f"✨ 带有备注的导入包已生成：{output_vcf}")
    print(f"💡 现在导入后，你只需在 Telegram 搜索 '{name_prefix.strip()}' 就能找到所有人。")

if __name__ == "__main__":
    generate_vcf_with_tag()