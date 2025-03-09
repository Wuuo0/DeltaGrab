# 免责申明
该软件仅供学习交流使用，请勿用于商业用途。
由于完全模拟人类操作，作者个人低频率使用时无封号历史。他人使用被封号请不要找我！！！

# 使用说明
## 环境搭建
### tesseract-ocr
文字识别基于此软件
1. 安装[tesseract-ocr](https://github.com/tesseract-ocr/tesseract)
2. 安装[中文识别包](https://github.com/tesseract-ocr/tessdata)
3. 将tesseract加入环境变量

### python
能找到这的人应该有点python基础，不介绍了

## 配置文件
### user_config.yaml
- buy_option: 填写要买的卡/最高购买与最低购买价格
- wallet_option: 填写当前的钱包钱数（仅适配k结尾的数字，作者哈夫币还没过亿）

## 开始使用
1. 游戏内点到交易行 -> 钥匙 -> 包含你要买的钥匙的那张图
2. 以管理员方式运行main.py，注意cmd窗口不要挡住钥匙区域（可以放在左边）
3. 等待，想停的话按住's'

## TODO
1. 自动识别钱包余额
2. 适配2k屏以外分辨率