import cv2


def read_text(filename):
    with open(filename, 'r') as f:
        return f.read().split('\n')


def read_img(filename):
    return cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
