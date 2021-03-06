import cv2
from albumentations import Compose, OneOf, Normalize, ShiftScaleRotate
from albumentations import GaussNoise, OpticalDistortion, GridDistortion
from albumentations import Cutout, Rotate, ElasticTransform, IAAAffine, IAAPerspective

augmix_transform = [
    ShiftScaleRotate(rotate_limit=15, p=1),
    OpticalDistortion(p=1),
    Cutout(max_h_size=8, max_w_size=8, p=1),
    # GridDistortion(p=1),
    Rotate(limit=15, p=1)
]


faa_transform = Compose([
    # GaussNoise(p=0.2),
    GridDistortion(num_steps=6, distort_limit=0.046, p=0.02),
    # OneOf([
    #     OpticalDistortion(p=1),
    #     ElasticTransform(p=1),
    # ], p=0.2),
    Cutout(num_holes=7, max_h_size=18, max_w_size=2, p=0.05),
])

train_transform = Compose([
    ShiftScaleRotate(rotate_limit=15, p=0.5),
    # GaussNoise(p=0.2),
    # GridDistortion(p=0.5),
    # OneOf([
    #     OpticalDistortion(p=1),
    #     ElasticTransform(p=1),
    # ], p=0.2),
    # Cutout(max_h_size=8, max_w_size=8, p=0.2),
])

valid_transform = Compose([
])
