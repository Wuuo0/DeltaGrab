import cv2
import numpy as np
import pyautogui
import time
import pytesseract
from difflib import SequenceMatcher
import keyboard

screen_pixel = [2560, 1440]
card_region = [583, 208]
card_pixel = [625, 212]
name_pixel = [178, 27]
price_region = [2184, 1172]
price_pixel = [116, 23]

cg_name = ['酒店国王房', '雷达站无人机平台', '酒店王子房', '雷达站数据中心', '实验楼资料室', '酒店黑桃房', '雷达站控制室', '实验楼办公室', '酒店将军房', '酒店方片房', '小镇餐厅', '运输机会议室']
db_name = ['东楼经理室', '变电站技术室', '西楼调控房', '西楼监视室', '售票办公室', '军营保管室', '设备领用室', '水泥厂宿舍201', '中心贵宾室', '水泥厂办公室', '地下通道钥匙', '西楼医务室', '变电站宿舍']

test_buy_name = '酒店国王房'
test_buy_price_max = 320 * 10000
test_buy_price_min = 260 * 10000

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

# 获取屏幕截图
def take_screenshot(region = None):
    screenshot = pyautogui.screenshot(region = region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    return screenshot

# 点击指定位置
def click_position(position):
    pyautogui.click(position[0], position[1])

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def get_card_name(image):
    ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    card_name = pytesseract.image_to_string(image, lang='tessdata\chi_sim', config='--psm 13')
    card_name = card_name.replace('\n', '').replace(' ', '')
    return card_name

def get_card_price(image):
    ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    card_price = pytesseract.image_to_string(image, lang='tessdata\eng', config='--psm 13 -c tessedit_char_whitelist=\'0123456789\'')
    card_price = card_price.replace('\n', '').replace(' ', '')
    try:
        return int(card_price)
    except ValueError:
        return 999999999

# 获取卡牌名称
card_name = []
screenshot = take_screenshot()
for i in range(5):
    for j in range(3):
        card_im = screenshot[card_region[1] + card_pixel[1] * i : card_region[1] + card_pixel[1] * (i+1), \
                     card_region[0] + card_pixel[0] * j : card_region[0] + card_pixel[0] * (j + 1)]
        card_name_im = card_im[ : name_pixel[1], : name_pixel[0]]
        card_name.append(get_card_name(card_name_im))
print(match_strings(cg_name, card_name))

buy_card_index = [card_name.index(test_buy_name)%3, card_name.index(test_buy_name)//3]
print(buy_card_index)

running = False 
while True:
    if keyboard.is_pressed('s'):  # 检测是否按下 's' 键
        running = True
        print("start")
    
    while running:
        click_position([card_region[0]+card_pixel[0]//2+card_pixel[0]*buy_card_index[0], \
                        card_region[1]+card_pixel[1]//2+card_pixel[1]*buy_card_index[1]])
        # 获取价格
        screenshot = take_screenshot()
        card_price = get_card_price(screenshot[price_region[1] : price_region[1] + price_pixel[1], \
        price_region[0] : price_region[0] + price_pixel[0]])
        print(card_price)
        if card_price <= test_buy_price_max and card_price >= test_buy_price_min:
            print('buy')
            click_position([price_region[0], price_region[1]+60])
            running = False
        pyautogui.press('esc')
        # time.sleep(1)
        if keyboard.is_pressed('w'):  # 按下 'w' 键可以暂停循环
            running = False
            print("pause")
