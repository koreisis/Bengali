import numpy as np
from torch import nn
import timm

from .head import Head


class EfficientNet(nn.Module):
    def __init__(self,
                 conf,
                 arch_name='efficientnet-b3',
                 input_channel=3,
                 pretrained=True):
        super(EfficientNet, self).__init__()

        self.base_model = timm.create_model(
            arch_name, in_chans=input_channel, pretrained=True)

        self.out_size = self.base_model.num_features
        self.fc_gr = Head(self.out_size, conf.gr_size)
        self.fc_vd = Head(self.out_size, conf.vd_size)
        self.fc_cd = Head(self.out_size, conf.cd_size)

    def forward(self, data):

        x = self.base_model.forward_features(data)

        gr = self.fc_gr(x)
        vd = self.fc_vd(x)
        cd = self.fc_cd(x)

        return np.array([gr, vd, cd])
