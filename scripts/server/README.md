运行脚本
---------------

进入接收data文件夹中
```shell
cd /path/to/you/data
```

修改sfm.sh中protobuf文件的路径，database生成在当前PROJECT文件下
```shell
python3 /root/colmaptzt/colmap_detailed/scripts/server/database.py /path/to/you/protobuf/bin ${PROJECT}/
```

运行sfm.sh脚本
```shell
./root/colmaptzt/colmap_detailed/scripts/server/sfm.sh
```