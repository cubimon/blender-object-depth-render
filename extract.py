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
    col_mat = np.zeros((height, width, 3), dtype=np.uint8)
    col_mat[..., 0] = r * 256
    col_mat[..., 1] = g * 256
    col_mat[..., 2] = b * 256
    depth_mat = np.zeros((height, width, 1), dtype=np.uint8)
    depth_mat[..., 0] = depth / np.amax(depth) * 256
    return (col_mat, depth)

def extract_here():
    exr_files = glob.glob("**/*.exr")
    for exr_file in exr_files:
        base_file = os.path.splitext(exr_file)[0]
        col, depth = load_exr(exr_file)
        cv2.imwrite(base_file + "_rgb.png", col)
        cv2.imwrite(base_file + "_depth.png", depth)

def get_bb_from_depth(depth_img):
    img = np.copy(depth_img)
    cv2.bitwise_not(img, img)
    nz_x_idx, nz_y_idx = np.nonzero(img)
    min_pos = (min(nz_y_idx), min(nz_x_idx))
    max_pos = (max(nz_y_idx), max(nz_x_idx))
    return (min_pos, max_pos)

'''
img = cv2.imread("0/1_depth.png", 0)
min_pos, max_pos = get_bb_from_depth(img)
cv2.rectangle(img, min_pos, max_pos, 128, 3)
cv2.namedWindow("test", cv2.WINDOW_NORMAL)
cv2.imshow("test", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("asdf.png", img)
'''

