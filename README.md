# dicom_preprocess

1. 将CT扫描重采样为所有方向上的公共体素间距为1毫米。
2. 将像素值转换为Hounsfield单位，并对图像进行中心裁剪，使其形状为320320320。
3. 将上述处理后的图像调整大小为128128128。
4. 对图像进行最小-最大归一化，使其范围在-1和1之间。
5. 将它们保存到一个新目录中，其中包含与存储原始.dcm文件的目录相同的子目录。