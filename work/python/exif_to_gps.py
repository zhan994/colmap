"""
    获取图片的EXIF信息并保存到TXT文件
    Zhihao Zhan
"""
import piexif
import os
import sys


def convert_fraction_to_float(fraction):
    """将分数转换为浮点数"""
    if isinstance(fraction, tuple) and len(fraction) == 2:
        numerator, denominator = fraction
        return float(numerator) / float(denominator)
    return float(fraction)


def convert_to_degrees(value):
    """将 EXIF 格式的坐标转换为十进制度数"""
    degrees, minutes, seconds = value
    d = convert_fraction_to_float(degrees)
    m = convert_fraction_to_float(minutes)
    s = convert_fraction_to_float(seconds)
    return d + (m / 60.0) + (s / 3600.0)

def get_exif_info(image_path):
    """获取图片的EXIF信息"""
    if not os.path.exists(image_path):
        print(f"文件 {image_path} 不存在")
        return None, None, None

    try:
        exif_dict = piexif.load(image_path)
    except Exception as e:
        print(f"加载 EXIF 信息时发生错误: {e}")
        return None, None, None

    if 'GPS' not in exif_dict:
        print("EXIF 信息中没有 GPS 字段")
        return None, None, None

    gps_info = exif_dict['GPS']
    latitude = gps_info.get(piexif.GPSIFD.GPSLatitude)
    longitude = gps_info.get(piexif.GPSIFD.GPSLongitude)
    altitude = gps_info.get(piexif.GPSIFD.GPSAltitude)

    if not (latitude and longitude):
        print("缺少纬度或经度信息")
        return None, None, None

    lat_ref = gps_info.get(piexif.GPSIFD.GPSLatitudeRef).decode()
    lon_ref = gps_info.get(piexif.GPSIFD.GPSLongitudeRef).decode()
    latitude = convert_to_degrees(latitude)
    longitude = convert_to_degrees(longitude)
    if lat_ref == 'S':
        # print(lat_ref)
        latitude = -latitude
    if lon_ref == 'W':
        # print(lon_ref)
        longitude = -longitude

    # 处理海拔高度
    if altitude:
        altitude = convert_fraction_to_float(altitude)
    else:
        altitude = None

    return latitude, longitude, altitude


def save_to_txt(data, txt_file):
    """将数据保存到TXT文件"""
    with open(txt_file, 'w') as file:
        for filename, latitude, longitude, altitude in sorted(data, key=lambda x: x[0]):
            formatted_latitude = f"{latitude:.7f}"
            formatted_longitude = f"{longitude:.7f}"
            formatted_altitude = f"{altitude:.2f}" if altitude is not None else ""
            file.write(
                f"{filename} {formatted_latitude} {formatted_longitude} {formatted_altitude}\n")


def process_images(folder_path, txt_file):
    """处理文件夹中的所有图片"""
    data = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(folder_path, filename)
            latitude, longitude, altitude = get_exif_info(image_path)
            # print(latitude, longitude, altitude)
            if latitude is not None and longitude is not None:
                data.append((filename, latitude, longitude, altitude))
    save_to_txt(data, txt_file)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python script_name.py <path_to_your_images> <output_txt_file>")
        exit(1)

    folder_path = sys.argv[1]  # 替换为你的图片文件夹路径
    txt_file = sys.argv[2]  # 输出TXT文件的名称
    process_images(folder_path, txt_file)
