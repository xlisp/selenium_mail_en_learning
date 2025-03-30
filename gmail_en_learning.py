from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import os

def load_known_words(file_path):
    """加载已知词汇列表"""
    if not os.path.exists(file_path):
        print(f"警告: 词汇文件 {file_path} 不存在")
        return set()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 假设known-words.md是一个单词列表，每行一个单词
    words = set(word.strip().lower() for word in content.split('\n') if word.strip())
    return words

def extract_words_from_text(text):
    """从文本中提取英文单词"""
    # 使用正则表达式提取英文单词（忽略数字和特殊字符）
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    return [word.lower() for word in words]

def find_unknown_words(text, known_words):
    """找出文本中所有不在已知词汇列表中的单词"""
    extracted_words = extract_words_from_text(text)
    unknown_words = [word for word in extracted_words if word not in known_words]
    return list(set(unknown_words))  # 去重

def scrape_gmail_emails(known_words_file):
    """使用Selenium抓取Gmail邮件并找出不认识的单词"""
    # 设置Chrome选项
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 取消注释以在后台运行
    chrome_options.add_argument("--window-size=1920,1080")
    
    # 初始化WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 打开Gmail
        driver.get("https://mail.google.com")
        print("请在浏览器中登录您的Gmail账户...")
        
        # 等待用户登录并加载收件箱
        WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.xpath, "//div[contains(@role, 'main')]"))
        )
        print("登录成功！开始抓取邮件...")
        
        # 加载已知词汇
        known_words = load_known_words(known_words_file)
        print(f"已加载 {len(known_words)} 个已知单词")
        
        # 获取所有邮件元素
        time.sleep(5)  # 给页面加载时间
        emails = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.xpath, "//tr[contains(@role, 'row')]"))
        )
        
        # 限制为最近的50封邮件
        emails = emails[:50] if len(emails) > 50 else emails
        print(f"找到 {len(emails)} 封邮件")
        
        all_unknown_words = []
        emails_processed = 0
        
        # 遍历邮件
        for email in emails:
            try:
                # 点击邮件打开
                email.click()
                time.sleep(2)
                
                # 等待邮件内容加载
                email_content = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.xpath, "//div[contains(@role, 'main')]"))
                )
                
                # 获取邮件内容文本
                text = email_content.text
                
                # 找出不认识的单词
                unknown_words = find_unknown_words(text, known_words)
                all_unknown_words.extend(unknown_words)
                
                # 返回到收件箱
                back_button = driver.find_element(By.xpath, "//div[contains(@aria-label, 'Back') or contains(@title, 'Back to Inbox')]")
                back_button.click()
                time.sleep(1)
                
                emails_processed += 1
                print(f"已处理 {emails_processed}/{len(emails)} 封邮件")
                
            except Exception as e:
                print(f"处理邮件时出错: {str(e)}")
                # 尝试返回收件箱
                driver.get("https://mail.google.com")
                time.sleep(3)
        
        # 去重并排序
        all_unknown_words = sorted(list(set(all_unknown_words)))
        print(f"总共找到 {len(all_unknown_words)} 个不认识的单词")
        
        # 将不认识的单词保存到文件
        with open("unknown_words.txt", "w", encoding="utf-8") as f:
            for word in all_unknown_words:
                f.write(word + "\n")
        
        print(f"不认识的单词已保存到 'unknown_words.txt'")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
    
    finally:
        # 完成后关闭浏览器
        driver.quit()

if __name__ == "__main__":
    known_words_file = "knowed-words.md"  # 已知词汇文件路径
    scrape_gmail_emails(known_words_file)
