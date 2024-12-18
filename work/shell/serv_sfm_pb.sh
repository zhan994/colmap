#!/bin/sh

# 输入为封装后特征点protobuf文件，估计内外参的sfm
# /root/colmap_detailed/work/shell/serv_sfm_pb.sh protobuf_path
# Zhihao Zhan

log_time() {
    date "+%Y-%m-%d %H:%M:%S:%3N"
}

PROTOBUF_PATH=$1
PB_LIST_TXT=${PROTOBUF_PATH}/pb_list.txt
PROJECT=${PROTOBUF_PATH}/proj_param
IMAGE=${PROJECT}/images

mkdir -p ${PROJECT}
mkdir -p ${IMAGE}

protoc --proto_path=/root/colmap_detailed/work/proto/ --python_out=/root/colmap_detailed/work/python/ /root/colmap_detailed/work/proto/mapper.proto
echo "$(log_time) convert protobuf to images..."
python3 /root/colmap_detailed/work/python/extract_images_txt.py ${PB_LIST_TXT} ${IMAGE}

echo "$(log_time) feature extractor ..."
/root/colmap_detailed/build/src/colmap/exe/colmap feature_extractor \
  --ImageReader.single_camera 1 \
  --ImageReader.camera_model OPENCV \
  --SiftExtraction.use_gpu 1 \
  --SiftExtraction.max_image_size 1024 \
  --SiftExtraction.max_num_features 3000 \
  --database_path ${PROJECT}/database.db \
  --image_path ${IMAGE}
echo "$(log_time) feature_extractor done."

echo "$(log_time) feature matcher ..."
/root/colmap_detailed/build/src/colmap/exe/colmap exhaustive_matcher \
  --SiftMatching.use_gpu 1 \
  --database_path ${PROJECT}/database.db
echo "$(log_time) feature exhaustive_matcher done."

mkdir -p ${PROJECT}/sparse
echo "$(log_time) colmap mapper ..."
/root/colmap_detailed/build/src/colmap/exe/colmap mapper \
  --Mapper.ba_refine_principal_point 1 \
  --Mapper.ba_refine_focal_length 1 \
  --Mapper.ba_refine_extra_params 1 \
  --Mapper.ba_local_max_num_iterations 25 \
  --Mapper.ba_global_max_num_iterations 50 \
  --database_path ${PROJECT}/database.db \
  --image_path ${IMAGE} \
  --output_path ${PROJECT}/sparse
echo "$(log_time) colmap mapper done."

echo "$(log_time) processing sparse folder..."
LARGEST_FOLDER=$(find ${PROJECT}/sparse/* -maxdepth 0 -type d -print0 | xargs -0 du -sb | sort -n -r | head -n 1 | awk '{print $2}')
if [ -z ${LARGEST_FOLDER} ]; then
    echo "$(log_time) no valid sparse folder found!"
    exit 1
fi
echo "$(log_time) largest folder is ${LARGEST_FOLDER}, export data as txt ..."
mv ${LARGEST_FOLDER} ${PROJECT}/sparse/valid
/root/colmap_detailed/build/src/colmap/exe/colmap model_converter \
    --input_path ${PROJECT}/sparse/valid \
    --output_path ${PROJECT}/sparse/valid \
    --output_type TXT
echo "$(log_time) Parameter path: ${PROJECT}/sparse/valid/camera.txt"