# -*- coding:UTF-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import yaml
from capdet.cap import Predictor
import base64
import numpy as np
import cv2
import time
from selenium.webdriver.common.action_chains import ActionChains

def ChromeDriverNOBrowser():
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--verbose')
    #chrome_options.add_argument(r'--profile-directory=C:\Users\Administrator\AppData\Local\Google\Chrome\User')
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": "./",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
    })
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')

    driverChrome = webdriver.Chrome(chrome_options=chrome_options)
    return driverChrome

def FirefoxNOBrowser():
    chrome_options = webdriver.FirefoxOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--verbose')
    #chrome_options.add_argument(r'--profile-directory=C:\Users\Administrator\AppData\Local\Google\Chrome\User')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')

    driverChrome = webdriver.Firefox(options=chrome_options)
    return driverChrome

'''options = webdriver.FirefoxOptions()
options.add_argument('-headless')

#browser = webdriver.Firefox(options=options)
browser = webdriver.Firefox(executable_path="/home/dongziyi/rep/geckodriver",options=options)'''

with open('usr.yaml', encoding='utf-8') as f:   # demo.yaml内容同上例yaml字符串
    usr_list=yaml.safe_load(f)
    print(usr_list)

cap_pred=Predictor()
print('model load ok')

browser=FirefoxNOBrowser()

def decode_img(img64):
    # base64解码
    img_data = base64.b64decode(img64)
    # 转换为np数组
    img_array = np.fromstring(img_data, np.uint8)
    # 转换成opencv可用格式
    return cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)

def login(browser, usr):
    print('login')
    WebDriverWait(browser, 180).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    while True:
        input_usr_name = browser.find_element_by_id("username")
        input_passwd = browser.find_element_by_id("password")
        input_cap = browser.find_element_by_id("captcha")

        # 识别验证码
        img_cap = browser.find_element_by_id('captchaImg')
        cv_cap = decode_img(img_cap.screenshot_as_base64)
        pst = time.time()
        cap_text = cap_pred.pred_img(cv_cap)
        pend = time.time()
        print('pred time:', pend - pst)
        print(cap_text)

        input_usr_name.click()
        input_usr_name.send_keys(usr['uid'])
        input_passwd.click()
        input_passwd.send_keys(usr['pwd'])
        input_cap.click()
        input_cap.send_keys(cap_text)

        btn_submit = browser.find_element_by_name('submit')
        btn_submit.click()

        time.sleep(1)
        if len(browser.find_elements_by_id("username")) == 0:
            break

def report(browser, usr, T):
    print(usr)
    browser.get("https://portal.sysu.edu.cn/#/index")
    '''WebDriverWait(browser, 180).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ant-btn-lg"))
            )'''
    time.sleep(0.5)
    print(browser.window_handles)
    print(browser.current_window_handle)

    if T==0:
        login(browser, usr)

    WebDriverWait(browser, 180).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ant-btn-lg"))
    )

    btn_login=browser.find_element_by_class_name('ant-btn-lg')
    btn_login.click()

    #登录
    if T > 0:
        login(browser, usr)

    #中山大学统一门户
    WebDriverWait(browser, 180).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li div div span"))
    )
    print('report')

    health_span=browser.find_element_by_css_selector('li div div span')
    btn_health=health_span.find_element(By.XPATH, "../..")
    #print(health_span.get_attribute('outerHTML'))
    #print(btn_health.get_attribute('outerHTML'))
    #btn_health.click()
    time.sleep(1)
    browser.execute_script('arguments[0].click()', btn_health)
    time.sleep(1)
    browser.switch_to.window(browser.window_handles[1])
    time.sleep(1)

    #下一步页面
    WebDriverWait(browser, 180).until(
        EC.presence_of_element_located((By.CLASS_NAME, "command_button"))
    )
    time.sleep(1)
    bnt_next=browser.find_element_by_class_name('command_button')
    browser.execute_script('arguments[0].click()', bnt_next)
    time.sleep(0.2)

    #提交页面
    WebDriverWait(browser, 180).until(
        EC.presence_of_element_located((By.CLASS_NAME, "kill"))
    )
    bnt_submit = browser.find_element_by_class_name('command_button')
    time.sleep(1)
    bnt_submit.click()

    time.sleep(1)
    browser.close()
    browser.switch_to.window(browser.window_handles[0])
    #dialog_button default fr

    WebDriverWait(browser, 180).until(
        EC.presence_of_element_located((By.CLASS_NAME, "userName"))
    )
    text_usrname = browser.find_element_by_class_name('userName')
    hov = ActionChains(browser).move_to_element(text_usrname)
    hov.perform()
    time.sleep(0.5)

    logout = browser.find_element_by_class_name('anticon-logout')
    btn_logout = logout.find_element(By.XPATH, "..")
    browser.execute_script('arguments[0].click()', btn_logout)
    print('logout')
    time.sleep(1)

for i,usr in enumerate(usr_list):
    report(browser, usr, i)
browser.quit()
print('ok')