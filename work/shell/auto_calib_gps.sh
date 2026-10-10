#!/bin/sh

# 提取GPS信息自动找到合适数据进行相机内参标定，在proj/calib下进行
# ./work/shell/auto_calib_gps.sh
# Zhihao Zhan

log_time() {
    date "+%Y-%m-%d %H:%M:%S:%3N"
}

PROJECT=${PWD}/proj
CALIB_PROJECT=${PROJECT}/calib

python3 work/python/exif_to_gps.py ${PROJECT}/images ${PROJECT}/gps.txt
python3 work/python/extract_calib.py ${PROJECT}/gps.txt 30 ${PROJECT}/calib_images.txt

echo "$(log_time) copying calibration images ..."
if [ ! -f "${PROJECT}/calib_images.txt" ]; then
    echo "找不到图片清单：${PROJECT}/calib_images.txt" >&2
    exit 1
fi

mkdir -p "${CALIB_PROJECT}/images" || exit 1
count=0
while IFS= read -r image_path || [ -n "$image_path" ]; do
    [ -z "$image_path" ] && continue
    image_name=${image_path##*/}
    cp -- "${PROJECT}/images/${image_name}" "${CALIB_PROJECT}/images/${image_name}" || exit 1
    count=$((count + 1))
done < "${PROJECT}/calib_images.txt"

echo "$(log_time) copied ${count} calibration images to ${CALIB_PROJECT}/images"

echo "$(log_time) feature extractor ..."
./build/src/colmap/exe/colmap feature_extractor \
  --ImageReader.single_camera 1 \
  --ImageReader.camera_model OPENCV \
  --SiftExtraction.use_gpu 1 \
  --SiftExtraction.max_image_size 1024 \
  --SiftExtraction.max_num_features 3000 \
  --database_path ${CALIB_PROJECT}/database.db \
  --image_path ${CALIB_PROJECT}/images
echo "$(log_time) feature_extractor done."

echo "$(log_time) feature matcher ..."
./build/src/colmap/exe/colmap exhaustive_matcher \
  --SiftMatching.use_gpu 1 \
  --database_path ${CALIB_PROJECT}/database.db
echo "$(log_time) feature exhaustive_matcher done."

mkdir -p ${CALIB_PROJECT}/sparse
echo "$(log_time) colmap mapper ..."
./build/src/colmap/exe/colmap mapper \
  --Mapper.ba_refine_principal_point 1 \
  --Mapper.ba_refine_focal_length 1 \
  --Mapper.ba_refine_extra_params 1 \
  --Mapper.ba_local_max_num_iterations 25 \
  --Mapper.ba_global_max_num_iterations 50 \
  --database_path ${CALIB_PROJECT}/database.db \
  --image_path ${CALIB_PROJECT}/images \
  --output_path ${CALIB_PROJECT}/sparse
echo "$(log_time) colmap mapper done."

echo "$(log_time) processing sparse folder..."
LARGEST_FOLDER=$(find ${CALIB_PROJECT}/sparse/* -maxdepth 0 -type d -print0 | xargs -0 du -sb | sort -n -r | head -n 1 | awk '{print $2}')
if [ -z ${LARGEST_FOLDER} ]; then
    echo "$(log_time) no valid sparse folder found!"
    exit 1
fi
echo "$(log_time) largest folder is ${LARGEST_FOLDER}, export data as txt ..."
mv ${LARGEST_FOLDER} ${CALIB_PROJECT}/sparse/valid
./build/src/colmap/exe/colmap model_converter \
    --input_path ${CALIB_PROJECT}/sparse/valid \
    --output_path ${CALIB_PROJECT}/sparse/valid \
    --output_type TXT
echo "$(log_time) Parameter path: ${CALIB_PROJECT}/sparse/valid/camera.txt"

python3 work/python/check_sfm.py ${CALIB_PROJECT}/sparse/valid/images.txt ${CALIB_PROJECT}/images