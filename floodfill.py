import cv2
import numpy as np

"""
TODO list in future versions:
1. implement floodfill algorithm without opencv
2. adjust algorithm to all colors 
"""


def erode(src, radius):
    result = src.copy()
    w = src.shape[1]
    h = src.shape[0]
    rr = radius*radius
    for x in range(1, h-1):
        for y in range(1, w-1):
            # 边界条件：四邻域内至少有一个与自己的值不相等
            is_edge = (src[x][y] != 255) and (src[x-1][y] == 255
                                              or src[x+1][y] == 255
                                              or src[x][y-1] == 255 or src[x][y+1] == 255)

            if is_edge:
                for dx in range(-radius, radius+1):
                    for dy in range(-radius, radius+1):
                        if dx*dx + dy*dy < rr:
                            x1 = x + dx
                            y1 = y + dy
                            if 0 <= x1 < h and 0 <= y1 < w:
                                result[x1][y1] = 0
    return result


def dilate(src, radius):
    result = src.copy()
    w = src.shape[1]
    h = src.shape[0]
    rr = radius*radius
    for x in range(1, h-1):
        for y in range(1, w-1):
            # 边界条件：四邻域内至少有一个与自己的值不相等
            is_edge = (src[x][y] == 255) and (src[x-1][y] == 0
                                              or src[x+1][y] == 0
                                              or src[x][y-1] == 0 or src[x][y+1] == 0)

            if is_edge:
                for dx in range(-radius, radius+1):
                    for dy in range(-radius, radius+1):
                        if dx*dx + dy*dy < rr:
                            x1 = x + dx
                            y1 = y + dy
                            if 0 <= x1 < h and 0 <= y1 < w:
                                result[x1][y1] = 255
    return result


def floodfill_with_gap(img, seedX, seedY, gap):
    normalFilled = np.zeros((img.shape[0]+2, img.shape[1]+2), dtype=np.uint8)

    flood_fill_flags = (
        4 | cv2.FLOODFILL_FIXED_RANGE | cv2.FLOODFILL_MASK_ONLY | 255 << 8)

    cv2.floodFill(img, normalFilled, (seedY, seedX),
                  0, (0,)*3, (0,)*3, flood_fill_flags)

    radius = int(round(gap/2))

    eroded = normalFilled.copy()
    eroded = eroded[1:-1, 1:-1]

    eroded = erode(eroded, radius)

    insideEroded = np.zeros((img.shape[0]+2, img.shape[1]+2), dtype=np.uint8)
    for dx in range(-radius, radius+1):  # 行
        for dy in range(-radius, radius+1):  # 列
            x = seedX + dx
            y = seedY + dy
            if 0 <= x < img.shape[0] and 0 <= y < img.shape[1]:
                if eroded[x][y] == 0:
                    continue

                cv2.floodFill(eroded, insideEroded, (y, x),
                              1, (0,)*3, (0,)*3, flood_fill_flags)

    eroded = eroded - insideEroded[1:-1, 1:-1]
    outside = dilate(eroded, radius)

    normalFilled = normalFilled[1:-1, 1:-1]-outside

    finalResult = np.zeros((img.shape[0]+2, img.shape[1]+2), dtype=np.uint8)
    cv2.floodFill(normalFilled, finalResult, (seedY, seedX),
                  0, (0,)*3, (0,)*3, flood_fill_flags)
    return finalResult[1:-1, 1:-1]
