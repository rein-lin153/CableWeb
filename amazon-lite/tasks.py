import requests
import models
from datetime import datetime
from sqlalchemy.orm import Session
from database import AsyncSessionLocal
from config import settings # <--- 导入

# ==========================================
# 核心修改：使用新浪财经接口 (Sina Finance)
# ==========================================
def get_realtime_copper_prices():
    """
    获取实时铜价 (Source: 新浪财经)
    接口地址: http://hq.sinajs.cn/list=nf_CU0
    说明: nf_CU0 代表 "沪铜连续" (Shanghai Copper Continuous)
    """
    print("🕷️ 正在从新浪财经获取数据...", end=" ")

    # 1. 获取沪铜 (CNY)
    # 新浪接口返回的是一段 JS 赋值代码，例如: var hq_str_nf_CU0="沪铜连,145623,69000,69500...";
    sina_url = settings.SINA_API_URL
    headers = {"Referer": "https://finance.sina.com.cn/"}

    cny_price = 0.0

    try:
        resp = requests.get(sina_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            # 解析字符串
            # 格式: var hq_str_nf_CU0="Name,Time,Open,High,Low,LastClose,Bid,Ask,Current,..."
            content = resp.text
            # 提取引号中的内容
            data_str = content.split('"')[1]
            data_list = data_str.split(',')

            # 字段索引 8 通常是“最新价” (Current Price)
            # 有时候如果没有最新价(如休市)，可能需要取索引 6 (Bid) 或 7 (Ask)
            # 这里我们取索引 8
            if len(data_list) > 8:
                cny_price = float(data_list[8])
                
    except Exception as e:
        print(f"\n❌ 新浪接口报错: {e}")
        return None

    # 2. 获取汇率 (保持你原来的逻辑，或使用备用)
    usd_to_cny_rate = 7.07
    usd_price = 0.0
    try:
        # 使用公开汇率 API
        rate_resp = requests.get(settings.EXCHANGE_RATE_API, timeout=5)
        if rate_resp.status_code == 200:
            usd_to_cny_rate = rate_resp.json().get("rates", {}).get("CNY", 7.07)
    except Exception:
        pass # 失败则使用默认值

    # 计算美元价格
    if cny_price > 0:
        usd_price = cny_price / usd_to_cny_rate

    print(f"✅ 获取成功: ¥{cny_price}")

    # 3. 返回符合数据库要求的结构
    return {
        "CNY": {
            "source": "沪铜连续 (Sina)",
            "symbol": "¥",
            "price": round(cny_price, 2),
            "change": 0.0
        },
        "USD": {
            "source": "折算 (Rate: 1:{:.2f})".format(usd_to_cny_rate),
            "symbol": "$",
            "price": round(usd_price, 2),
            "change": 0.0
        },
        "exchange_rate": round(usd_to_cny_rate, 4),
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ==========================================
# 定时任务 (保持不变，只是调用了新的爬虫函数)
# ==========================================
async def update_copper_price_task():
    print(f"[{datetime.now()}] ⏰ 定时任务启动...")
    
    data = get_realtime_copper_prices() # 这个函数是同步爬虫，保持不变
    
    if not data or data['CNY']['price'] <= 0:
        print("⚠️ 价格无效，跳过数据库写入")
        return

    # 修改此处：使用 async with 和 await
    async with AsyncSessionLocal() as db:
        try:
            record = models.CopperPrice(
                cny_price = data['CNY']['price'],
                usd_price = data['USD']['price'],
                exchange_rate = data['exchange_rate'],
                updated_at = datetime.now()
            )
            
            db.add(record)
            await db.commit() # 必须加 await
            print(f"💾 数据库已更新: ¥{record.cny_price}")
            
        except Exception as e:
            print(f"❌ 数据库写入失败: {e}")
            await db.rollback() # 必须加 await