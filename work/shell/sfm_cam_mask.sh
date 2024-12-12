#!/bin/sh

# 固定内参共享的SFM，colmap目录下准备好proj文件夹以及图片
# ./work/shell/sfm_cam_mask.sh fx,fy,cx,cy,k1,k2,p1,p2
# Zhihao Zhan

log_time() {
    date "+%Y-%m-%d %H:%M:%S:%3N"
}

PROJECT="${PWD}/proj"
CAM_PARAM="$1"
python3 work/python/camera_mask.py 960 540 200 250 ${PROJECT}/camera_mask.png

echo "$(log_time) feature extractor ..."
./build/src/colmap/exe/colmap feature_extractor \
  --ImageReader.single_camera 1 \
  --ImageReader.camera_mask ${PROJECT}/camera_mask.png \
  --ImageReader.camera_model OPENCV \
  --ImageReader.camera_params ${CAM_PARAM} \
  --SiftExtraction.use_gpu 1 \
  --SiftExtraction.max_image_size 1024 \
  --SiftExtraction.max_num_features 3000 \
  --database_path ${PROJECT}/database.db \
  --image_path ${PROJECT}/images
echo "$(log_time) feature_extractor done."

echo "$(log_time) feature matcher ..."
./build/src/colmap/exe/colmap  exhaustive_matcher\
  --SiftMatching.use_gpu 1 \
  --database_path ${PROJECT}/database.db
echo "$(log_time) feature exhaustive_matcher done."

mkdir -p ${PROJECT}/sparse
echo "$(log_time) colmap mapper ..."
./build/src/colmap/exe/colmap mapper \
  --Mapper.ba_refine_principal_point 0 \
  --Mapper.ba_refine_focal_length 0 \
  --Mapper.ba_refine_extra_params 0 \
  --Mapper.ba_local_max_num_iterations 50 \
  --Mapper.ba_global_max_num_iterations 100 \
  --database_path ${PROJECT}/database.db \
  --image_path ${PROJECT}/images \
  --output_path ${PROJECT}/sparse
echo "$(log_time) colmap mapper done."

echo "$(log_time) processing sparse folder..."
LARGEST_FOLDER=$(find ${PROJECT}/sparse/* -maxdepth 0 -type d -print0 | xargs -0 du -sb | sort -n -r | head -n 1 | awk '{print $2}')
if [ -z ${LARGEST_FOLDER} ]; then
    echo "$(log_time) no valid sparse folder found!"
    exit 1
fi
echo "$(log_time) largest folder is ${LARGEST_FOLDER}, export valid data as txt ..."
mv ${LARGEST_FOLDER} ${PROJECT}/sparse/valid
./build/src/colmap/exe/colmap model_converter \
    --input_path ${PROJECT}/sparse/valid \
    --output_path ${PROJECT}/sparse/valid \
    --output_type TXT
echo "$(log_time) export valid data as txt done."