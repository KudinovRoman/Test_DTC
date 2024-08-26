import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import yagmail
from selenium.common.exceptions import NoSuchElementException

def load_config(config_path):
    with open(config_path, 'r') as file:
        return json.load(file)


def take_screenshot(driver, screen_name):
    driver.save_screenshot(f"{screen_name}.png")

def send_email(config):
    try:
        yag = yagmail.SMTP(config["login"], config["password"])
        yag.send(
            to=config["recipients"],        
            subject=config["subject"],      
            contents=config["body"],        
            attachments=config["attachment_path"],  
        )
        return "Sent"  
    except Exception as e:
        return f"Failed: {str(e)}"  

def test_login_and_send_email(driver, config):   
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10) 
    report = []

    # Доступ по URL
    driver.get(config["url"])
    take_screenshot(driver, "screen1_access_url") 
    report.append(f"Access URL - {config['url']}")

    # Вход в учетку
    try:
        login_input = wait.until(EC.presence_of_element_located((By.NAME, "login")))
        login_input.send_keys(config["login"])  
        driver.find_element(By.NAME, "password").click() 
        
        
        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_input.send_keys(config["password"])  
        driver.find_element(By.NAME, "login-to-mail").click()  

        # Ожид загрузки основной страницы после входа
        wait.until(EC.title_contains("Inbox"))  

        take_screenshot(driver, "screen2_success_login")  
        report.append(f"Login success - {config['login']}")
    except NoSuchElementException:
        take_screenshot(driver, "screen2_failed_login")  
        report.append(f"Login failed - {config['login']}")
        return report

    # Отправка письма
    result = send_email(config)
    take_screenshot(driver, "screen3_send_email")
    report.append(f"Email sent to {config['recipients']} - {result}")
    driver.quit()
    return report

# Проверерка соответствия 
    assert "Login success" in report[-2], "Login mail failed."
    assert "Sent" in result, "Email not sent successfully."
    for line in report:
        print(line)  # Отчет в консоль


