import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def redeem():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # 从 GitHub Secrets 读取隐藏名单
    accounts_str = os.getenv("MY_ACCOUNTS_SECRET", "")
    accounts = [a.strip() for a in accounts_str.split(",") if a.strip()]
    
    # 读取兑换码清单
    try:
        with open("codes.txt", "r", encoding="utf-8") as f:
            codes = [line.strip() for line in f if line.strip()]
    except:
        codes = []

    # 加载历史记录
    history_file = "history.json"
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = {}

    url = "https://redeem.bd2.pmang.cloud/bd2/index.html?lang=zh-TW"
    
    for code in codes:
        for name in accounts:
            task_key = f"{name}---{code}"
            if task_key in history:
                continue

            # 脱敏显示名 (例如: 玩家123 -> 玩家1***)
            display_name = name[0:2] + "***" if len(name) > 2 else name + "***"
            
            print(f"正在兌換: {display_name} | 代碼: {code}")
            try:
                driver.get(url)
                time.sleep(3)
                inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                if len(inputs) >= 2:
                    inputs[0].send_keys(name)
                    inputs[1].send_keys(code)
                    driver.find_element(By.TAG_NAME, "button").click()
                    time.sleep(2)
                    alert = driver.switch_to.alert
                    res_text = alert.text
                    alert.accept()
                    # 存入 JSON 数据
                    history[task_key] = {"display": display_name, "status": res_text, "code": code, "time": time.strftime("%Y-%m-%d %H:%M")}
            except Exception as e:
                print(f"出错: {e}")
                
    # 写入结果
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)
    
    driver.quit()

if __name__ == "__main__":
    redeem()
