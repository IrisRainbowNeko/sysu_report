# -*- coding:UTF-8 -*-
import traceback

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
import random
import argparse
from selenium.webdriver.common.action_chains import ActionChains
from retry import retry

parser = argparse.ArgumentParser()
parser.add_argument('--repid', type=str, default='all')
parser.add_argument('--delay', type=int, default=1200)
args = parser.parse_args()

delay_time=random.randint(0, args.delay)
print('delay:', delay_time)
time.sleep(delay_time)
print('delay over')

def select_usr(usr_list, sid):
    if sid=='all':
        return usr_list
    else:
        id_str=sid.split(',')
        res=[]
        for strid in id_str:
            if ':' in strid:
                res.extend(eval(f'usr_list[{strid}]'))
            else:
                res.append(eval(f'usr_list[{strid}]'))
        return res

def FirefoxNOBrowser():
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--window-size=1920x1080")
    firefox_options.add_argument("--disable-notifications")
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--verbose')
    firefox_options.add_argument('--disable-gpu')
    firefox_options.add_argument('--disable-software-rasterizer')

    driver = webdriver.Firefox(options=firefox_options)
    return driver

'''options = webdriver.FirefoxOptions()
options.add_argument('-headless')

#browser = webdriver.Firefox(options=options)
browser = webdriver.Firefox(executable_path="/home/dongziyi/rep/geckodriver",options=options)'''

with open('usr.yaml', encoding='utf-8') as f:   # demo.yaml内容同上例yaml字符串
    usr_list=yaml.safe_load(f)
    print('raw users', usr_list)

cap_pred=Predictor()
print('model load ok')

def decode_img(img64):
    # base64解码
    img_data = base64.b64decode(img64)
    # 转换为np数组
    img_array = np.frombuffer(img_data, np.uint8)
    # 转换成opencv可用格式
    return cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)

def login(browser, usr):
    print('login')
    WebDriverWait(browser, 180).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    while True:
        input_usr_name = browser.find_element(By.ID, "username")
        input_passwd = browser.find_element(By.ID, "password")
        input_cap = browser.find_element(By.ID, "captcha")

        # 识别验证码
        img_cap = browser.find_element(By.ID, 'captchaImg')
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

        btn_submit = browser.find_element(By.NAME, 'submit')
        btn_submit.click()

        time.sleep(1)
        if len(browser.find_elements(By.ID, "username")) == 0:
            break

@retry(tries=3, delay=1)
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

    btn_login=browser.find_element(By.CLASS_NAME, 'ant-btn-lg')
    btn_login.click()

    #登录
    if T > 0:
        login(browser, usr)

    #中山大学统一门户
    WebDriverWait(browser, 180).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li div div span"))
    )
    print('report')

    health_spans=browser.find_elements(By.CSS_SELECTOR, 'li div div span')
    #print(health_span.get_attribute('outerHTML'))
    #print(btn_health.get_attribute('outerHTML'))
    #btn_health.click()
    health_span=[x for x in health_spans if x.text=='学生健康申报'][0]
    print(health_span.text)
    btn_health = health_span.find_element(By.XPATH, "../..")
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
    bnt_next=browser.find_element(By.CLASS_NAME,'command_button')
    browser.execute_script('arguments[0].click()', bnt_next)
    time.sleep(0.2)

    #提交页面
    WebDriverWait(browser, 180).until(
        EC.presence_of_element_located((By.CLASS_NAME, "kill"))
    )
    bnt_submit = browser.find_element(By.CLASS_NAME, 'command_button')
    time.sleep(1)
    bnt_submit.click()

    time.sleep(1)
    browser.close()
    browser.switch_to.window(browser.window_handles[0])
    #dialog_button default fr

    WebDriverWait(browser, 180).until(
        EC.presence_of_element_located((By.CLASS_NAME, "userName"))
    )
    text_usrname = browser.find_element(By.CLASS_NAME, 'userName')
    print(text_usrname.get_attribute('outerHTML'))
    hov = ActionChains(browser).move_to_element(text_usrname)
    hov.perform()
    time.sleep(0.5)

    logout = browser.find_element(By.CLASS_NAME, 'anticon-logout')
    btn_logout = logout.find_element(By.XPATH, "..")
    browser.execute_script('arguments[0].click()', btn_logout)
    print('logout')
    time.sleep(1)

usr_list=select_usr(usr_list, args.repid)
print('filter users', usr_list)
for i,usr in enumerate(usr_list):
    browser = FirefoxNOBrowser()
    try:
        report(browser, usr, 1)
    except:
        traceback.print_exc()
    browser.quit()
print( 'ok')