#!/bin/sh

# 固定内参共享的SFM，并GPS信息对齐，输入为封装后特征点protobuf文件
# Zhihao Zhan

PROTOBUF_PATH="$1"
PROJECT="${PROTOBUF_PATH}/proj"
IMAGE="${PROJECT}/images"

mkdir -p ${PROJECT}
mkdir -p ${IMAGE}

log_time() {
    date "+%Y-%m-%d %H:%M:%S:%3N"
}

protoc --proto_path=work/proto/ --python_out=work/python/ work/proto/mapper.proto 

echo "$(log_time) convert protobuf to database ..."
python3 work/python/database.py ${PROTOBUF_PATH} ${PROJECT}/database.db

echo "$(log_time) convert protobuf to images ..."
python3 work/python/extract_images.py ${PROTOBUF_PATH} ${IMAGE}

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
  --Mapper.ba_local_max_num_iterations 25 \
  --Mapper.ba_global_max_num_iterations 50 \
  --database_path ${PROJECT}/database.db \
  --image_path ${IMAGE} \
  --output_path ${PROJECT}/sparse
echo "$(log_time) colmap mapper done."

echo "$(log_time) convert csv to gps ..."
python3 work/python/csv_to_gps.py \
  ${PROTOBUF_PATH}/photo_record.csv \
  ${PROJECT}/gps.txt
echo "$(log_time) csv conversion done."

mkdir -p ${PROJECT}/sparse/0_aligned_enu
echo "$(log_time) ENU align ..."
./build/src/colmap/exe/colmap model_aligner \
    --input_path  ${PROJECT}/sparse/0 \
    --output_path  ${PROJECT}/sparse/0_aligned_enu \
    --ref_images_path ${PROJECT}/gps.txt \
    --ref_is_gps 1 \
    --alignment_type enu \
    --alignment_max_error 3
echo "$(log_time) ENU align done."

echo "$(log_time) export ENU as txt ..."
./build/src/colmap/exe/colmap model_converter \
    --input_path ${PROJECT}/sparse/0_aligned_enu \
    --output_path ${PROJECT}/sparse/0_aligned_enu \
    --output_type TXT
echo "$(log_time) export ENU as txt done."

mkdir -p ${PROJECT}/sparse/0_aligned_ecef
echo "$(log_time) ECEF align ..."
./build/src/colmap/exe/colmap model_aligner \
    --input_path  ${PROJECT}/sparse/0 \
    --output_path  ${PROJECT}/sparse/0_aligned_ecef \
    --ref_images_path ${PROJECT}/gps.txt \
    --ref_is_gps 1 \
    --alignment_type ecef \
    --alignment_max_error 3
echo "$(log_time) ECEF align done."

echo "$(log_time) export ECEF as txt ..."
./build/src/colmap/exe/colmap model_converter \
    --input_path ${PROJECT}/sparse/0_aligned_ecef \
    --output_path ${PROJECT}/sparse/0_aligned_ecef \
    --output_type TXT
echo "$(log_time) export ECEF as txt done."

echo "$(log_time) convert camera pose from Tcw to Twc ..."
python3 work/python/colmap_pose.py \
  ${PROJECT}/sparse/0_aligned_enu/images.txt \
  ${PROJECT}/sparse/0_aligned_enu/images_Twc.txt
python3 work/python/colmap_pose.py \
  ${PROJECT}/sparse/0_aligned_ecef/images.txt \
  ${PROJECT}/sparse/0_aligned_ecef/images_Twc.txt
echo "$(log_time) camera pose conversion done."

echo "$(log_time) update images_Twc.txt ..."
python3 work/python/update_Twc.py \
  ${PROJECT}/gps.txt \
  ${PROJECT}/sparse/0_aligned_ecef/images_Twc.txt \
  ${PROJECT}/sparse/0_aligned_ecef/points3D.txt \
  ${PROJECT}/sparse/0_aligned_ecef/images_Twc_updated.txt
echo "$(log_time) update images_Twc.txt done."

echo "$(log_time) generate photo_record_quat.csv ..."
python3 work/python/colmap_quat_csv.py \
  ${PROJECT}/sparse/0_aligned_ecef/images_Twc_updated.txt \
  ${PROJECT}/sparse/0_aligned_enu/images_Twc.txt \
  ${PROJECT}/photo_record_quat.csv
echo "$(log_time) photo_record_quat.csv generation done."
