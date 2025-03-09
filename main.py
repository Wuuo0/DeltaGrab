import cv2
import numpy as np
import pyautogui
import time
import pytesseract
from difflib import SequenceMatcher
import keyboard
import yaml
import sys

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
    return screenshot


def click_position(position):
    pyautogui.moveTo(position[0], position[1], duration=0.1)
    pyautogui.click()


def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def get_card_name(image):
    ret, image = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    card_name = pytesseract.image_to_string(
        image, lang='tessdata\chi_sim', config='--psm 13')
    card_name = card_name.replace('\n', '').replace(' ', '')
    return card_name


def get_card_price(image):
    ret, image = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    card_price = pytesseract.image_to_string(
        image, lang='tessdata\eng', config='--psm 13 -c tessedit_char_whitelist=\'0123456789\'')
    card_price = card_price.replace('\n', '').replace(' ', '')
    try:
        return int(card_price)
    except ValueError:
        return sys.maxsize


# 获取卡牌名称
card_name = []
screenshot = take_screenshot((pre_configs['coordinate_position']['card_region'][0], pre_configs['coordinate_position']['card_region']
                             [1], pre_configs['coordinate_position']['card_pixel'][0] * 3, pre_configs['coordinate_position']['card_pixel'][1] * 5))
for i in range(5):
    for j in range(3):
        card_im = screenshot[pre_configs['coordinate_position']['card_pixel'][1] * i: pre_configs['coordinate_position']['card_pixel'][1] * (i+1),
                             pre_configs['coordinate_position']['card_pixel'][0] * j: pre_configs['coordinate_position']['card_pixel'][0] * (j + 1)]
        card_name_im = card_im[: pre_configs['coordinate_position']['name_pixel']
                               [1], : pre_configs['coordinate_position']['name_pixel'][0]]
        card_name.append(get_card_name(card_name_im))
print(card_name)
# 对各张地图中卡牌名字尝试匹配，找到匹配最符合的地图
card_name = [match_strings(pre_configs['card_name']['db'], card_name), match_strings(pre_configs['card_name']['cg'], card_name),
             match_strings(pre_configs['card_name']['ht'], card_name), match_strings(pre_configs['card_name']['bks'], card_name)][[len(match_strings(pre_configs['card_name']['db'], card_name)), len(match_strings(pre_configs['card_name']['cg'], card_name)),
                                                                                                                                   len(match_strings(pre_configs['card_name']['ht'], card_name)), len(match_strings(pre_configs['card_name']['bks'], card_name))].index(
                 max(len(match_strings(pre_configs['card_name']['db'], card_name)), len(match_strings(pre_configs['card_name']['cg'], card_name)),
                     len(match_strings(pre_configs['card_name']['ht'], card_name)), len(match_strings(pre_configs['card_name']['bks'], card_name))))]

print(card_name)

buy_card_index = [card_name.index(user_configs['buy_option']['buy_card_name']) % 3, card_name.index(
    user_configs['buy_option']['buy_card_name'])//3]
print(buy_card_index)

running = True
min_price = sys.maxsize

while running:
    click_position([pre_configs['coordinate_position']['card_region'][0]+pre_configs['coordinate_position']['card_pixel'][0]//2+pre_configs['coordinate_position']['card_pixel'][0]*buy_card_index[0],
                    pre_configs['coordinate_position']['card_region'][1]+pre_configs['coordinate_position']['card_pixel'][1]//2+pre_configs['coordinate_position']['card_pixel'][1]*buy_card_index[1]])
    # 获取价格
    screenshot = take_screenshot(region=(pre_configs['coordinate_position']['price_region'][0], pre_configs['coordinate_position']
                                 ['price_region'][1], pre_configs['coordinate_position']['price_pixel'][0], pre_configs['coordinate_position']['price_pixel'][1]))
    card_price = get_card_price(screenshot)
    if card_price <= user_configs['buy_option']['buy_price_max'] * 10000 and card_price >= user_configs['buy_option']['buy_price_min'] * 10000 and card_price > 0:
        click_position([pre_configs['coordinate_position']['price_region']
                       [0], pre_configs['coordinate_position']['price_region'][1]+60])
        time.sleep(1)
        if min_price > card_price:
            min_price = card_price
            print('min_price', min_price)
        screenshot = take_screenshot((pre_configs['coordinate_position']['wallet_region'][0], pre_configs['coordinate_position']['wallet_region']
                                     [1], pre_configs['coordinate_position']['wallet_pixel'][0], pre_configs['coordinate_position']['wallet_pixel'][1]))
        wallet_price = get_card_price(screenshot)
        print('wallet_price', wallet_price)
        if wallet_price < user_configs['wallet_option']['now_money'] and wallet_price >= (user_configs['wallet_option']['now_money'] - card_price):
            print('bought')
            running = False
        else:
            continue
    pyautogui.press('esc')
    if keyboard.is_pressed('s'):
        running = False
        print("stop")
