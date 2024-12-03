'''
  生成 `camera_mask.png` 用于过滤图像左右下角落的飞机脚架遮挡
  Zhihao Zhan
'''

import sys
from PIL import Image, ImageDraw

def camera_mask(w, h, mw, mh, output_path):
    # 设置图片的尺寸
    width, height = w, h

    # 创建一个新的图片对象，并用灰色填充
    color = (128, 128, 128)  # 灰色，RGB值
    image = Image.new('RGB', (width, height), color)

    # 创建一个绘图对象
    draw = ImageDraw.Draw(image)

    # 设置黑色区域的坐标
    # 左下角区域
    left_bottom_x, left_bottom_y = 0, height - mh
    # 右下角区域
    right_bottom_x, right_bottom_y = width - mw, height - mh

    # 绘制左下角的黑色区域
    draw.rectangle([left_bottom_x, left_bottom_y, left_bottom_x + mw, left_bottom_y + mh], fill=(0, 0, 0))
    # 绘制右下角的黑色区域
    draw.rectangle([right_bottom_x, right_bottom_y, right_bottom_x + mw, right_bottom_y + mh], fill=(0, 0, 0))

    # 保存图片
    image.save(output_path)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python script.py w h mw mh <output_path>")
        sys.exit(1)

    w, h, mw, mh = map(int, sys.argv[1:5])
    output_path = sys.argv[5]
    camera_mask(w, h, mw, mh, output_path)