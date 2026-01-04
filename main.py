import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def redeem():
    # 配置浏览器（GitHub Actions 专用设置）
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # 读取文件
    try:
        with open("accounts.txt", "r", encoding="utf-8") as f:
            accounts = [line.strip() for line in f if line.strip()]
        with open("codes.txt", "r", encoding="utf-8") as f:
            codes = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"读取文件失败: {e}")
        return

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
            # 如果这个账号已经兑换过这个码，跳过
            if task_key in history:
                print(f"跳过已兑换任务: {task_key}")
                continue

            print(f"正在为 [{name}] 兑换 [{code}]...")
            try:
                driver.get(url)
                time.sleep(3) # 等待加载
                
                inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                if len(inputs) >= 2:
                    inputs[0].send_keys(name)
                    inputs[1].send_keys(code)
                    driver.find_element(By.TAG_NAME, "button").click()
                    
                    time.sleep(2)
                    alert = driver.switch_to.alert
                    res_text = alert.text
                    alert.accept()
                    history[task_key] = res_text
                    print(f"结果: {res_text}")
                
                time.sleep(1) # 避免太快
            except Exception as e:
                print(f"兑换出错: {e}")
                history[task_key] = "Error or Timeout"

    # 存回历史记录
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)
    
    driver.quit()

if __name__ == "__main__":
    redeem()
