import OpenEXR
import cv2
import numpy as np
import itertools
import glob
import os

# import pdb; pdb.set_trace()

def exr_get_size(exr_img):
    box = exr_img.header()["dataWindow"]
    return (box.max.x - box.min.x + 1, box.max.y - box.min.y + 1)

def exr_channel_to_np_arr(exr_img, channel):
    width, height = exr_get_size(exr_img)
    np_arr = np.fromstring(exr_img.channel(channel), dtype=np.float32)
    np_arr = np_arr.reshape(height, width)
    return np_arr

def load_exr(path):
    img = OpenEXR.InputFile(path)
    width, height = exr_get_size(img)
    depth = exr_channel_to_np_arr(img, "RenderLayer.Depth.Z")
    r = exr_channel_to_np_arr(img, "RenderLayer.Combined.R")
    g = exr_channel_to_np_arr(img, "RenderLayer.Combined.G")
    b = exr_channel_to_np_arr(img, "RenderLayer.Combined.B")
    col = np.zeros((height, width, 3), dtype=np.uint8)
    col[..., 0] = r * 256
    col[..., 1] = g * 256
    col[..., 2] = b * 256
    return (col, depth)

exr_files = glob.glob("**/*.exr")
for exr_file in exr_files:
    base_file = os.path.splitext(exr_file)[0]
    img = load_exr(exr_file)
    cv2.imwrite(base_file + ".jpg", img[0])

