#!/bin/sh

# Normalize images, calibrate intrinsics, then run GPS-aligned SfM.
# ./work/shell/sfm_cam_gps_auto_calib.sh

log_time() {
    date "+%Y-%m-%d %H:%M:%S:%3N"
}

PROJECT=${PWD}/proj

if [ ! -d "${PROJECT}/images_raw" ]; then
    echo "Missing raw image directory: ${PROJECT}/images_raw" >&2
    exit 1
fi

echo "$(log_time) normalize image EXIF orientation ..."
python3 work/python/rm_exif_rot.py "${PROJECT}/images_raw" "${PROJECT}/images"

echo "$(log_time) auto calibration ..."
# Run with -e because the existing scripts do not enable failure propagation.
./work/shell/auto_calib_gps.sh

CAM_PARAM=$(python3 work/python/get_intrinsics.py "${PROJECT}/calib/sparse/valid")

echo "$(log_time) GPS-aligned SfM with calibrated intrinsics ${CAM_PARAM}..."
./work/shell/sfm_cam_gps.sh ${CAM_PARAM}
echo "$(log_time) auto-calibrated GPS SfM done."