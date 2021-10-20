# -*- coding: utf-8 -*-
from __future__ import print_function, division
import torch
import argparse
import torch.nn as nn
import torch.nn.functional as F
from .models.seq_module import ACE
from .models.solver import seq_solver
from .utils.basic import *
import cv2
import torchvision.models as models

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

opt=argparse.Namespace()
opt.model_path='./capdet/weights/model-raw-29.pth'
opt.class_num=26*2+10
opt.dict='_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

def vec2word(vec):
    if vec in range(0, 26):
        return chr(vec + 65)
    elif vec in range(26, 26 * 2):
        return chr(vec - 26 + 97)
    elif vec in range(26 * 2, 26 * 2 + 10):
        return chr(vec - 26 * 2 + 48)

class ResnetEncoderDecoder(nn.Module):
    def __init__(self, loss_layer, opt):
        super(ResnetEncoderDecoder, self).__init__()
        self.opt=opt
        self.bn = nn.BatchNorm2d(64)
        resnet = models.resnet18(pretrained=False)
        self.conv  = nn.Conv2d(3,   64,   kernel_size=(3, 3), padding=(1, 1), stride=(1, 1))
        self.cnn = nn.Sequential(*list(resnet.children())[4:-2])
        self.out = nn.Linear(512, self.opt.class_num+1)
        self.loss_layer = loss_layer(self.opt.dict)

    def forward(self, input, labels):
        input = F.relu(self.bn(self.conv(input)), True)
        input = F.max_pool2d(input, kernel_size=(2, 2), stride=(2, 2)) 
        input = self.cnn(input)

        input = input.permute(0,2,3,1)
        input = F.softmax(self.out(input),dim=-1)

        if labels is not None:
            labels = labels.to(device)
            return self.loss_layer(input,labels)
        else:
            self.bs, self.h, self.w, _ = input.size()
            T_ = self.h * self.w
            input = input.view(self.bs, T_, -1)
            input = input + 1e-10

            #print(torch.max(input, 2))
            pred = torch.max(input, 2)[1].data.cpu().numpy()
            pred = pred[0]  # sample #0

            return pred.reshape((self.h,self.w)).T.reshape((self.h*self.w,))


class Predictor:
    def __init__(self):
        self.model = ResnetEncoderDecoder(ACE,opt).to(device)
        if str(device)=='cpu':
            check_point = torch.load(opt.model_path, map_location=torch.device('cpu'))
        else:
            check_point = torch.load(opt.model_path)
        self.model.load_state_dict(check_point)
        self.the_solver = seq_solver(model=self.model, model_path=opt.model_path)

    def pred(self, input):
        pred = self.the_solver.demo(input)
        return remove_rptch(''.join(opt.dict[x] for x in pred if x))

    def pred_img(self, img):
        image = cv2.resize(img, (120, 40))
        image = image.astype('float32')
        # image = cv2.pyrDown(image).astype('float32')  # 100*100
        image = image.transpose((2, 0, 1))
        res = self.pred(torch.from_numpy(image).unsqueeze(0))
        return res
