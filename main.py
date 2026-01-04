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

    # --- 修改点：从 GitHub Secrets 读取账号 ---
    accounts_str = os.getenv("MY_ACCOUNTS_SECRET", "")
    accounts = [a.strip() for a in accounts_str.split(",") if a.strip()]
    
    if not accounts:
        print("未检测到账号列表，请检查 Secrets 设置！")
        return

    # 读取公开的兑换码文件
    try:
        with open("codes.txt", "r", encoding="utf-8") as f:
            codes = [line.strip() for line in f if line.strip()]
    except:
        print("未找到 codes.txt")
        return

    history_file = "history.json"
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = {}

    url = "https://redeem.bd2.pmang.cloud/bd2/index.html?lang=zh-TW"
    
    for code in codes:
        for name in accounts:
            # 为了在公开的 history.json 中隐藏全名，我们可以只显示名字的前两个字
            display_name = name[0:2] + "***" 
            task_key = f"{name}---{code}"
            display_key = f"{display_name}---{code}"

            if task_key in history:
                continue

            print(f"正在兑换: {display_name}...")
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
                    # 记录时使用脱敏后的名字，保护隐私
                    history[task_key] = {"display": display_name, "status": res_text, "code": code}
            except:
                history[task_key] = {"display": display_name, "status": "Error", "code": code}

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)
    driver.quit()

if __name__ == "__main__":
    redeem()
