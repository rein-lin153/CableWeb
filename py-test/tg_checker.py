import asyncio
import pandas as pd
import os
from telethon import TelegramClient, functions, types
from telethon.errors import FloodWaitError

# --- 配置区 ---
api_id = '33378366'
api_hash = '70a851d7cd17f3ccd3ecc893f47638d4'
phone_for_login = '+8550965809551'

input_file = '柬埔寨全境电线电缆供应商调研表_2025.xlsx'
output_file = '柬埔寨电缆商_TG验证最终版.xlsx'

async def verify_telegram():
    client = TelegramClient('check_session', api_id, api_hash)
    await client.start(phone=phone_for_login)

    # 1. 加载数据：如果已有进度文件则继续，否则读原表
    if os.path.exists(output_file):
        df = pd.read_excel(output_file)
        print(f"检测到历史进度，继续执行...")
    else:
        df = pd.read_excel(input_file)
        if 'Telegram状态' not in df.columns:
            df['Telegram状态'] = "待验证"

    print(f"✅ 登录成功！总计任务：{len(df)} 行")

    for index, row in df.iterrows():
        # 如果这一行已经验证过了，直接跳过（实现断点续爬）
        if df.at[index, 'Telegram状态'] not in ["待验证", "验证失败"]:
            continue

        raw_phone = str(row['联系电话']).strip()
        formatted_phone = raw_phone.replace(" ", "").replace("-", "")
        if formatted_phone.startswith('0'):
            formatted_phone = '+855' + formatted_phone[1:]
        elif not formatted_phone.startswith('+'):
            formatted_phone = '+855' + formatted_phone

        try:
            # 核心验证
            result = await client(functions.contacts.ImportContactsRequest(
                contacts=[types.InputPhoneContact(
                    client_id=0,
                    phone=formatted_phone,
                    first_name=str(row['企业名称']),
                    last_name=''
                )]
            ))
            
            status = "已注册" if result.users else "未注册"
            df.at[index, 'Telegram状态'] = status
            
            icon = "✨" if status == "已注册" else "⚪"
            print(f"{icon} [{index+1}] {row['企业名称']} -> {status}")

            if result.users:
                await client(functions.contacts.DeleteContactsRequest(id=[result.users[0].id]))

            # --- 核心改进：每跑完一条立即存一次档 ---
            df.to_excel(output_file, index=False)
            
            # 频率控制
            await asyncio.sleep(5) 

        except FloodWaitError as e:
            print(f"⚠️ 触发 Telegram 限制，需等待 {e.seconds} 秒...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"❌ 错误: {e}")
            df.at[index, 'Telegram状态'] = "验证失败"
            df.to_excel(output_file, index=False)
            continue

    print(f"\n🎉 所有任务处理完毕！最终结果：{output_file}")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(verify_telegram())