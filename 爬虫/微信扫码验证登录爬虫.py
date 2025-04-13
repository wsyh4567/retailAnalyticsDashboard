import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pickle
import time
from bs4 import BeautifulSoup
import os

def save_cookies():
    # 配置 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
    chrome_options.add_argument('--no-sandbox')  # 禁用沙箱模式
    chrome_options.add_argument('--disable-dev-shm-usage')  # 禁用/dev/shm使用
    chrome_options.add_argument('--disable-web-security')  # 禁用网页安全性检查
    chrome_options.add_experimental_option('detach', True)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 禁用自动化提示
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 指定 Chrome 浏览器路径
    chrome_options.binary_location = r"D:\Chrome\App\chrome.exe"
    
    # 使用 ChromeDriverManager 自动安装和管理 ChromeDriver
    service = Service(ChromeDriverManager().install())
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("正在打开登录页面...")
        
        # 访问登录页面
        driver.get("https://stu.tulingpyton.cn/wechat/mp/login/")
        
        print("请扫码登录，登录成功后会自动保存cookies...")
        
        # 等待URL发生变化，最多等待120秒
        original_url = driver.current_url
        
        def url_changed(driver):
            current_url = driver.current_url
            print(f"当前URL: {current_url}")  # 打印当前URL以便调试
            return current_url != original_url and "login" not in current_url
        
        # 等待URL变化，表示登录成功
        WebDriverWait(driver, 120).until(url_changed)
        
        print("检测到登录成功，正在保存cookies...")
        cookies = driver.get_cookies()
        with open('cookies.pkl', 'wb') as f:
            pickle.dump(cookies, f)
        print("Cookies保存成功！")
        
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        time.sleep(2)  # 给一点时间看到最后的提示
        driver.quit()

def load_cookies():
    if not os.path.exists('cookies.pkl'):
        print("没有找到保存的Cookies，请先登录！")
        save_cookies()
        return load_cookies()
    
    session = requests.Session()
    # 添加一个模拟真实浏览器的 User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    session.headers.update(headers)
    
    with open('cookies.pkl', 'rb') as f:
        cookies = pickle.load(f)
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    return session

def delete_cookies():
    if os.path.exists('cookies.pkl'):
        try:
            os.remove('cookies.pkl')
            print("Cookies文件已成功删除！")
        except Exception as e:
            print(f"删除Cookies文件时发生错误: {e}")
    else:
        print("没有找到Cookies文件！")

def main():
    session = load_cookies()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://stu.tulingpyton.cn/problem-detail/2/',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # 用于存储所有数字
    all_numbers = []
    page = 1
    
    while True:
        url = f'https://stu.tulingpyton.cn/api/problem-detail/2/data/?page={page}'
        response = session.get(url, headers=headers)
        
        try:
            data = response.json()
            current_array = data.get('current_array', [])
            print(f"第{page}页数据：", current_array)
            
            # 如果返回的数组为空，就退出循环
            if not current_array:
                break
                
            all_numbers.extend(current_array)
            
            # 检查是否还有下一页
            pagination = data.get('pagination', {})
            if not pagination.get('has_next'):
                break
                
            page += 1
            time.sleep(0.5)  # 添加短暂延时
            
        except Exception as e:
            print(f"处理第{page}页时出错：", e)
            break
    
    # 计算总和
    total = sum(all_numbers)
    print(f"\n获取到所有数字：{all_numbers}")
    print(f"数字总和：{total}")

        # 提交答案
    submit_url = "https://stu.tulingpyton.cn/problem/2/submit/"
    submit_data = {
        'user_answer': str(total),
        'csrfmiddlewaretoken': session.cookies.get('csrftoken')  # 获取CSRF token
    }
    
    submit_response = session.post(submit_url, data=submit_data, headers={
        **headers,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://stu.tulingpyton.cn/problem-detail/2/'
    })
    
    print("\n提交结果：")
    print(submit_response.text)
if __name__ == "__main__":
    main()