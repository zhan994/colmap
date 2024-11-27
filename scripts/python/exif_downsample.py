'''
   write gps info for images and downsample.
   Zhihao Zhan
'''

import os
import sys
import csv
import piexif
import cv2
from PIL import Image

def decimal_to_dms(decimal):
    degree = int(decimal)
    temp = (decimal - degree) * 60
    minute = int(temp)
    second = int((temp - minute) * 60 * 100000)
    return ((degree, 1), (minute, 1), (second, 100000))

def add_exif_location(image_path, lat, lon, alt):
    exif_dict = piexif.load(image_path)
    gps_info = {
        piexif.GPSIFD.GPSLatitudeRef: 'N', 
        piexif.GPSIFD.GPSLatitude: decimal_to_dms(lat),
        piexif.GPSIFD.GPSLongitudeRef: 'E',
        piexif.GPSIFD.GPSLongitude:decimal_to_dms(lon),
        piexif.GPSIFD.GPSAltitudeRef: 0,
        piexif.GPSIFD.GPSAltitude: (int(alt * 1000), 1000)
    }

    # 将GPS信息添加到EXIF数据中
    exif_dict['GPS'] = gps_info
    exif_bytes = piexif.dump(exif_dict)

    img = Image.open(image_path)
    img.save(image_path, exif=exif_bytes)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python write_exif.py <dir>")
        sys.exit(1)

    input_dir = sys.argv[1]

    # 加载照片的经纬度信息
    pos_file = os.path.join(input_dir, "photo_record.csv")
    pos_map = {}
    with open(pos_file, 'r') as f:
        reader = csv.reader(f, delimiter=' ', skipinitialspace=True, )
        for row in reader:
            if len(row) >= 7:
                image_name = row[0].split("/")[-1]
                lat = float(row[1])
                lon = float(row[2])
                alt = float(row[3])
                pos_map[image_name] = (lat, lon, alt)

    # 读取所有照片
    files = os.listdir(input_dir)
    files = [f for f in files if f.endswith(".jpeg")]
    files.sort()

    output_dir = input_dir + "_GPS"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for f in files:
        img = cv2.imread(os.path.join(input_dir, f), cv2.IMREAD_UNCHANGED)
        img_2 = cv2.pyrDown(img)
        cv2.imwrite(os.path.join(output_dir, f), img_2)
        # 添加经纬度信息
        lat, lon, alt = pos_map[f]
        print(lat, lon, alt)
        add_exif_location(os.path.join(output_dir, f), lat, lon, alt)
        print(os.path.join(output_dir, f))