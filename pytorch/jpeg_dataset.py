import torch
from torch.utils.data import Dataset
import glob
from skimage import io
import random

class JpegDataset(Dataset):
    def __init__(self, glob_pattern='data/train/**.jpg'):
        self.file_names = glob.glob(glob_pattern, recursive=True)
        
    def __len__(self):
        return len(self.file_names)

    def __getitem__(self, index):
        file_name = self.file_names[index]
        image = io.imread(file_name) / 255.0

        t2 = torch.tensor(image[:, :image.shape[1] // 2, 0], dtype=torch.float32)
        t1 = torch.tensor(image[:, image.shape[1] // 2:, 0], dtype=torch.float32)
        
        return t2, t1