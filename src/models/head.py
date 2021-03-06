import math
import numpy as np
import torch
import torch.nn.functional as F
from torch import nn


class Head(nn.Module):
    def __init__(self, input_size, output_size, dropout=0.2):
        super(Head, self).__init__()
        self.head = nn.Sequential(
            nn.Linear(input_size, output_size),
            nn.BatchNorm1d(output_size),
            nn.ReLU(),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.head(x)


class BranchedHead(nn.Module):
    def __init__(self, conf, input_size, dropout=0.2):
        super(BranchedHead, self).__init__()
        middle_size = 512
        self.gr1 = Head(input_size, middle_size)
        self.vd1 = Head(input_size, middle_size)
        self.cd1= Head(input_size, middle_size)
        self.center = nn.Sequential(
            Head(input_size, 1280),
            Head(1280, middle_size)
        )
        self.fc_gr = nn.Linear(middle_size, conf.gr_size)        
        self.fc_vd = nn.Linear(middle_size, conf.vd_size)
        self.fc_cd = nn.Linear(middle_size, conf.cd_size)

    def forward(self, x):
        gr = self.gr1(x)
        vd = self.vd1(x)
        cd = self.cd1(x)
        center = self.center(x)

        gr = self.fc_gr(gr+center)
        vd = self.fc_vd(vd+center)
        cd = self.fc_cd(cd+center)

        return np.array([gr, vd, cd])


class AttentionHead(nn.Module):
    def __init__(self, conf, input_size, output_size):
        super(AttentionHead, self).__init__()
        middle_size = output_size
        self.l1 = nn.Sequential(
            nn.Linear(input_size, middle_size),
            nn.BatchNorm1d(middle_size),
            nn.ReLU()
        )
        self.l2 = nn.Sequential(
            nn.Linear(input_size, middle_size),
            nn.BatchNorm1d(middle_size),
            nn.ReLU()
        )
        self.l3 = nn.Sequential(
            nn.Linear(input_size, middle_size),
            nn.BatchNorm1d(middle_size),
            nn.ReLU()
        )
        self.cv = nn.Sequential(
            nn.Conv1d(256, 256, kernel_size=3),
            nn.BatchNorm1d(256),
            nn.ReLU()
        )
        self.gr_out = nn.Linear(middle_size, conf.gr_size)
        self.vd_out = nn.Linear(middle_size, conf.vd_size)
        self.cd_out = nn.Linear(middle_size, conf.cd_size)

    def forward(self, x):
        l1 = self.l1(x)[:, :, None]
        l2 = self.l2(x)[:, :, None]
        l3 = self.l3(x)[:, :, None]
        v = torch.cat([l1, l2, l3], dim=2)
        v = self.cv(v).squeeze(2)

        gr = self.gr_out(v+l1.squeeze(2))
        vd = self.vd_out(v+l2.squeeze(2))
        cd = self.cd_out(v+l3.squeeze(2))
        
        return np.array([gr, vd, cd])


class ArcMarginProduct(nn.Module):
    r"""Implement of large margin arc distance: :
        Args:
            in_features: size of each input sample
            out_features: size of each output sample
            s: norm of input feature
            m: margin
            cos(theta + m)
        """
    def __init__(self, in_features, out_features):
        super(ArcMarginProduct, self).__init__()
        self.weight = nn.Parameter(torch.FloatTensor(out_features, in_features))
        # nn.init.xavier_uniform_(self.weight)
        self.reset_parameters()

    def reset_parameters(self):
        stdv = 1. / math.sqrt(self.weight.size(1))
        self.weight.data.uniform_(-stdv, stdv)

    def forward(self, features):
        cosine = F.linear(F.normalize(features), F.normalize(self.weight.cuda()))
        return cosine

