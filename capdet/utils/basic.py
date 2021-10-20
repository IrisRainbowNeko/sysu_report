import time
import math
import numpy as np
import cv2

def asMinutes(s):
    m = math.floor(s / 60)
    s -= m * 60
    return '%dm %ds' % (m, s)


def timeSince(since):
    now = time.time()
    s = now - since
    return '%s' % (asMinutes(s))

def gamma_trans(img, gamma):
    #具体做法先归一化到1，然后gamma作为指数值求出新的像素值再还原
    gamma_table = [np.power(x/255.0,gamma)*255.0 for x in range(256)]
    gamma_table = np.round(np.array(gamma_table)).astype(np.uint8)
    #实现映射用的是Opencv的查表函数
    return cv2.LUT(img,gamma_table)

def adjust_histogram(img):
    dst=np.zeros(img.shape,dtype=np.uint8)
    # 创建CLAHE对象
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # 限制对比度的自适应阈值均衡化
    for i in range(3):
        dst[:,:,i] = clahe.apply(img[:,:,i])
    return dst

def most_same(clip,thr_same=0.5):
    csum=np.sum(clip,axis=2)
    cnorm=(csum-np.mean(csum))/np.std(csum)
    #print(cnorm)
    return np.where(np.abs(cnorm)<thr_same)

def rm_noise(img,thr_same=0.5,ksize=(3,3)):
    h,w,_=img.shape
    dst=np.zeros(img.shape,dtype=np.uint8)
    for y in range(1,h-1):
        for x in range(1, w - 1):
            clip=img[y-1:y+2,x-1:x+2,:]
            dst[y-1:y+2,x-1:x+2,:]=np.mean(clip[most_same(clip,thr_same)],axis=0)
    return dst

def rm_noise2(img,thr_same=0.5,ksize=(3,3),thr_color=15,rep_color=None):
    base_color=np.mean(img[most_same(img,0.5)],axis=0)

    h,w,_=img.shape
    dst=np.zeros(img.shape,dtype=np.uint8)
    for y in range(1,h-1):
        for x in range(1, w - 1):
            clip=img[y-1:y+2,x-1:x+2,:]
            cmean=np.mean(clip[most_same(clip,thr_same)],axis=0)

            if np.std(cmean-base_color)<thr_color or np.isnan(cmean).any():
                dst[y - 1:y + 2, x - 1:x + 2, :]=(base_color if rep_color is None else rep_color)
            else:
                dst[y - 1:y + 2, x - 1:x + 2, :] = cmean
    return dst



def processimg(img):
    #img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #img=cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,21,1)
    #img=rm_noise2(img,thr_same=0.5,thr_color=6)
    img = rm_noise2(img, thr_same=0.7, thr_color=5)
    #img = cv2.normalize(img, dst=None, alpha=350, beta=10, norm_type=cv2.NORM_MINMAX)
    #img=cv2.medianBlur(img, 3)
    #img = adjust_histogram(img)
    return img

def rmchr(text,index):
    return text[:index]+text[index+1:]

def count_rptch(text):
    maxch=(1,0)
    nowch=(0,0)
    lastch=None
    for index,i in enumerate(text):
        if lastch == i:
            nowch = (nowch[0]+1,nowch[1])
            if nowch[0]>maxch[0]:
                maxch=nowch
        else:
            nowch=(1,index)

        lastch=i

    return maxch

def remove_rptch(text,tar_len=4):
    while len(text)>tar_len:
        maxch = count_rptch(text)
        if maxch[0]<=1:
            break
        text=rmchr(text,maxch[1])
    return text
