import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_cambodia_cable_industry():
    chrome_options = Options()
    # 自动识别你的 Chromium 路径
    chrome_options.binary_location = "/usr/bin/chromium-browser" 
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--lang=en-US")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 10)
    
    # 1. 定义要覆盖的省份/城市 (实现全柬埔寨爬取)
    locations = ["Phnom Penh", "Sihanoukville", "Siem Reap", "Battambang", "Poipet", "Kampong Cham", "Bavet"]
    base_keyword = "Cable and Wire supplier"
    
    all_leads_urls = set() # 使用集合去重

    try:
        for city in locations:
            search_query = f"{base_keyword} in {city}, Cambodia"
            print(f"🔍 正在搜索区域: {city}...")
            driver.get(f"https://www.google.com/maps/search/{search_query}")
            time.sleep(5)

            # 滚动加载当前区域的所有列表项
            try:
                scrollable_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]')))
                for _ in range(5): # 增加滚动次数以获取更多商家
                    driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
                    time.sleep(2)
            except:
                print(f"⚠️ 该区域结果较少或未找到列表: {city}")

            # 提取所有商家的链接
            links = driver.find_elements(By.CLASS_NAME, "hfpxzc")
            for link in links:
                url = link.get_attribute("href")
                if url:
                    all_leads_urls.add(url)
        
        print(f"📊 扫描完毕！共识别到 {len(all_leads_urls)} 个唯一商家链接。开始深度抓取详情...")

        # 2. 深度抓取逻辑：通过直接跳转 URL 规避点击报错
        final_results = []
        for index, url in enumerate(list(all_leads_urls)):
            try:
                print(f"[{index+1}/{len(all_leads_urls)}] 正在跳转详情页...")
                driver.get(url)
                # 等待标题加载，确保页面渲染完成
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "DUwDvf")))
                time.sleep(2)

                # 提取数据
                name = driver.find_element(By.CLASS_NAME, "DUwDvf").text
                phone, address, website = "N/A", "N/A", "N/A"
                
                details = driver.find_elements(By.CLASS_NAME, "Io6YTe")
                for d in details:
                    val = d.text.strip()
                    if not val: continue
                    # 柬埔寨电话特征
                    if val.startswith('+') or val.startswith('01') or val.startswith('06') or val.startswith('08') or val.startswith('09'):
                        phone = val
                    elif '.' in val and ('com' in val or 'kh' in val or 'net' in val):
                        website = val
                    elif len(val) > 15 and name not in val:
                        address = val

                final_results.append({
                    "省份/城市": "自动识别",
                    "企业名称": name,
                    "联系电话": phone,
                    "官方网站": website,
                    "详细地址": address,
                    "Google地图链接": url
                })
                print(f"✅ 成功提取: {name}")

            except Exception as e:
                print(f"❌ 抓取失败 (已跳过): {url[:50]}...")
                continue

    finally:
        save_to_excel(final_results)
        driver.quit()

def save_to_excel(data):
    if not data:
        print("没有抓取到任何数据。")
        return
    df = pd.DataFrame(data)
    filename = '柬埔寨全境电线电缆供应商调研表_2025.xlsx'
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='供应商汇总')
        # 美化表格列宽
        worksheet = writer.sheets['供应商汇总']
        for i, col in enumerate(df.columns):
            worksheet.column_dimensions[chr(65+i)].width = 25
            
    print(f"\n✨ 全柬埔寨行业报表已生成：{filename}")

if __name__ == "__main__":
    scrape_cambodia_cable_industry()