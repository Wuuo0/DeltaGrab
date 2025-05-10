import sys
import time
from difflib import SequenceMatcher
import re
import cv2
import keyboard
import numpy as np
import pyautogui
import pytesseract
import yaml
from datetime import datetime
import easyocr
# reader = easyocr.Reader(['en'])

jiaoyihang = [945, 75]
ht_col = [210, 1200]
money = [2026, 58]
money1 = [2210, 57]
money_pixel = [114, 38]
with open('pre_config.yaml', 'r', encoding='utf-8') as fin:
    pre_configs = yaml.load(fin, Loader=yaml.FullLoader)

with open('user_config.yaml', 'r', encoding='utf-8') as fin:
    user_configs = yaml.load(fin, Loader=yaml.FullLoader)


def match_strings(correct_strings, error_strings):
    matched_strings = []

    for error_str in error_strings:
        highest_ratio = 0
        matched_str = ""

        for correct_str in correct_strings:
            ratio = SequenceMatcher(None, correct_str, error_str).ratio()
            if ratio > highest_ratio:
                highest_ratio = ratio
                matched_str = correct_str
        if highest_ratio > 0.5:
            matched_strings.append(matched_str)

    return matched_strings


def take_screenshot(region=None):
    screenshot = pyautogui.screenshot(region=region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    cv2.imwrite(f'screenshot.png', screenshot)
    return screenshot


def click_position(position):
    pyautogui.moveTo(position[0], position[1], duration=0.1)
    pyautogui.click()


def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def get_card_name(image):
    ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    card_name = pytesseract.image_to_string(image, lang='chi_sim', config='--psm 13')
    card_name = card_name.replace('\n', '').replace(' ', '')
    return card_name



def get_card_price(image, psm=7, oem=1, whitelist='0123456789', resize_factor=2, binarize_method='otsu'):
    # 1. 放大增强细节
    if resize_factor != 1:
        h, w = image.shape
        image = cv2.resize(
            image,
            (int(w * resize_factor), int(h * resize_factor)),
            interpolation=cv2.INTER_CUBIC
        )

    # 2. 二值化
    if binarize_method == 'adaptive':
        image = cv2.adaptiveThreshold(
            image, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11, C=2
        )
    else:  # 默认 Otsu
        _, image = cv2.threshold(
            image, 0, 255,
            cv2.THRESH_BINARY | cv2.THRESH_OTSU
        )

    # 3. 可选：形态学去噪（可根据需要打开注释）
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    # 4. 配置 Tesseract
    tesseract_config = f'--psm {psm} --oem {oem} -c tessedit_char_whitelist={whitelist}'

    # 5. OCR 识别
    raw = pytesseract.image_to_string(image, lang='eng', config=tesseract_config)

    # 6. 提取数字并转整
    digits = ''.join(filter(str.isdigit, raw))
    if digits:
        return int(digits)
    else:
        # 识别失败时返回最大值
        return sys.maxsize

def get_cash():
    money_ss = take_screenshot(region=(money[0], money[1],  money_pixel[0], money_pixel[1]))
    cv2.imwrite(f'cash.png', money_ss)
    cash = get_card_price(money_ss)
    return cash

def get_cash1():
    money_ss = take_screenshot(region=(money1[0], money1[1],  money_pixel[0], money_pixel[1]))
    cv2.imwrite(f'cash.png', money_ss)
    cash = get_card_price(money_ss)
    return cash

def reset():
    for i in range(5):
        pyautogui.press('esc')
        time.sleep(0.5)
    click_position([1500, 1000])
    time.sleep(0.5)
    click_position(jiaoyihang)
    time.sleep(0.5)
    click_position(ht_col)
    time.sleep(0.5)

def buy_card():
    click_position([2180, 1225])


def main():
    # 获取卡牌名称
    card_name = []
    screenshot = take_screenshot(
        (pre_configs['coordinate_position']['card_region'][0], pre_configs['coordinate_position']['card_region'][1],
        pre_configs['coordinate_position']['card_pixel'][0] * 3, pre_configs['coordinate_position']['card_pixel'][1] * 5))
    for i in range(5):
        for j in range(3):
            card_im = screenshot[pre_configs['coordinate_position']['card_pixel'][1] * i: pre_configs['coordinate_position']['card_pixel'][1] * (i + 1),
                                pre_configs['coordinate_position']['card_pixel'][0] * j: pre_configs['coordinate_position']['card_pixel'][0] * (j + 1)
                    ]
            card_name_im = card_im[: pre_configs['coordinate_position']['name_pixel'][1],
                        : pre_configs['coordinate_position']['name_pixel'][0]]
            card_name.append(get_card_name(card_name_im))
    print(f'获取卡牌名称 :{card_name}')
    # 对各张地图中卡牌名字尝试匹配，找到匹配最符合的地图
    card_name = \
    [match_strings(pre_configs['card_name']['db'], card_name), match_strings(pre_configs['card_name']['cg'], card_name),
    match_strings(pre_configs['card_name']['ht'], card_name), match_strings(pre_configs['card_name']['bks'], card_name)][
        [len(match_strings(pre_configs['card_name']['db'], card_name)),
        len(match_strings(pre_configs['card_name']['cg'], card_name)),
        len(match_strings(pre_configs['card_name']['ht'], card_name)),
        len(match_strings(pre_configs['card_name']['bks'], card_name))].index(
            max(len(match_strings(pre_configs['card_name']['db'], card_name)),
                len(match_strings(pre_configs['card_name']['cg'], card_name)),
                len(match_strings(pre_configs['card_name']['ht'], card_name)),
                len(match_strings(pre_configs['card_name']['bks'], card_name))))]

    print(f'对各张地图中卡牌名字尝试匹配，找到匹配最符合的地图{card_name}')

    buy_card_index = [card_name.index(user_configs['buy_option']['buy_card_name']) % 3, card_name.index(
        user_configs['buy_option']['buy_card_name']) // 3]
    print(buy_card_index)

    running = True
    min_price = sys.maxsize

    log_file = open('record.txt', 'a')
    log_file.write(f'=== new record {datetime.now()} ===\n')
    page_monitor = []
    max_retries = 5
    before_cash = get_cash()
    print(f'before cash : {before_cash}')
    while running:
        click_position([pre_configs['coordinate_position']['card_region'][0] +
                        pre_configs['coordinate_position']['card_pixel'][0] // 2 +
                        pre_configs['coordinate_position']['card_pixel'][0] * buy_card_index[0],
                        pre_configs['coordinate_position']['card_region'][1] +
                        pre_configs['coordinate_position']['card_pixel'][1] // 2 +
                        pre_configs['coordinate_position']['card_pixel'][1] * buy_card_index[1]])
        time.sleep(0.5)
        # 获取价格
        screenshot = take_screenshot(
            region=(pre_configs['coordinate_position']['price_region'][0], pre_configs['coordinate_position']['price_region'][1],
                    pre_configs['coordinate_position']['price_pixel'][0], pre_configs['coordinate_position']['price_pixel'][1]))

        card_price = get_card_price(screenshot)
        log_file.write(f"{datetime.now()} - price: {card_price}\n")

        # monitor 检查是否需要reset
        page_monitor.append(card_price)
        if len(page_monitor) > max_retries:  # 保持最多5条记录
            page_monitor.pop(0)

        if len(page_monitor) == max_retries and all(price == sys.maxsize for price in page_monitor):
            log_file.write(f"{datetime.now()} - reset\n")
            print(f"reset")
            reset()
            page_monitor = [] 
            continue 

        if user_configs['buy_option']['buy_price_max'] * 10000 >= card_price >= user_configs['buy_option']['buy_price_min'] * 10000 and card_price > 0:
            print(f'{user_configs['buy_option']['buy_price_max'] * 10000} >= {card_price} >= {user_configs['buy_option']['buy_price_min'] * 10000}')
            log_file.write(f'{user_configs['buy_option']['buy_price_max'] * 10000} >= {card_price} >= {user_configs['buy_option']['buy_price_min'] * 10000}\n')
            buy_card()
            time.sleep(0.5)
            after_cash = get_cash1()
            print(f'after cash : {after_cash}')
            if(before_cash > after_cash):
                time.sleep(0.5)
                print('bought')
                log_file.write(f'bought\n')
                running = False
            else:
                print('failed')
                log_file.write('failed\n')
        
        pyautogui.press('esc')
        if keyboard.is_pressed('s'):
            running = False
            print("stop")

    log_file.close()

if __name__ == '__main__':
    main()