import torch
from torch.utils.data import Dataset
import glob
from skimage import io
import random
import os

'''
Dataset for jpegs that contain a pair of T1 and T2 slices of equal sizes
'''
class JpegPairsDataset(Dataset):
    def __init__(self, glob_pattern='data/train/**.jpg'):
        self.file_names = glob.glob(glob_pattern, recursive=True)
        
    def __len__(self):
        return len(self.file_names)

    def __getitem__(self, index):
        file_name = self.file_names[index]
        image = io.imread(file_name) / 255.0

        t1 = torch.tensor(image[:, :image.shape[1] // 2, 0], dtype=torch.float32)
        t2 = torch.tensor(image[:, image.shape[1] // 2:, 0], dtype=torch.float32)
        
        return t2, t1

'''
Dataset for T1 and T2 slices in different jpeg files of varying sizes
To ensure the same resolution during training each image is randomly cropped to a fixed resolution.
'''
class JpegDataset(Dataset):
    def __init__(self, glob_pattern='data/train_orig/t1w_**.jpg'):
        self.file_names = glob.glob(glob_pattern, recursive=True)
        self.resolution = 128
        self.remove_bad_images = False
        
    def __len__(self):
        return len(self.file_names)

    def __getitem__(self, index):
        file_name_t1 = self.file_names[index]
        file_name_t2 = file_name_t1.replace('t1w_', 't2w_')
        image_t1 = io.imread(file_name_t1) / 255.0
        image_t2 = io.imread(file_name_t2) / 255.0

        if image_t1.shape[0] != image_t2.shape[0] or image_t1.shape[1] != image_t2.shape[1]:
            if self.remove_bad_images:
                os.remove(file_name_t1)
                os.remove(file_name_t2)
                return None
            else:
                raise Exception("T1 and T2 images have different resolutions. \n\n{:s}\n{:s}.".format(file_name_t1, file_name_t2))

        offset_x = random.randrange(image_t1.shape[0] - self.resolution) if image_t1.shape[0] > self.resolution else 0
        offset_y = random.randrange(image_t1.shape[1] - self.resolution) if image_t1.shape[1] > self.resolution else 0

        t1 = torch.tensor(image_t1[offset_x:offset_x + self.resolution, offset_y:offset_y + self.resolution], dtype=torch.float32)
        t2 = torch.tensor(image_t2[offset_x:offset_x + self.resolution, offset_y:offset_y + self.resolution], dtype=torch.float32)

        if t1.shape[0] != self.resolution or t1.shape[1] != self.resolution or t2.shape[0] != self.resolution or t2.shape[1] != self.resolution:
            padded_t1 = torch.zeros(self.resolution, self.resolution)
            padded_t2 = torch.zeros(self.resolution, self.resolution)
            padded_t1[:t1.shape[0], :t1.shape[1]] = t1
            padded_t2[:t2.shape[0], :t2.shape[1]] = t2
            t1, t2 = padded_t1, padded_t2
        
        return t2, t1

if __name__ == '__main__':
    from tqdm import tqdm
    count = 0
    dataset = JpegDataset()
    dataset.remove_bad_images = True
    for item in tqdm(dataset):
        if item is None:
            count += 1
    print("Deleted {:d} bad images.".format(count))