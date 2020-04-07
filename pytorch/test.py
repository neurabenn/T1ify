from itertools import count

import torch
from torch.utils.data import DataLoader
from jpeg_dataset import JpegDataset
from tqdm import tqdm
from torchvision import utils

from unet import UNet

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NETWORK_FILENAME = 'trained_models/unet.to'

network = UNet()
network.load_state_dict(torch.load(NETWORK_FILENAME))
network.cuda()

dataset = JpegDataset(glob_pattern='data/test/**.jpg')
data_loader = DataLoader(dataset, batch_size=8, shuffle=True, num_workers=8)

index = 0

with torch.no_grad():
    for t2, t1 in tqdm(data_loader):
        size = t1.shape[1]

        predicted = network(t2.to(device))

        test_output = torch.zeros(size * t2.shape[0], size * 3)

        for i in range(t1.shape[0]):
            test_output[i * size:(i+1) * size, :size] = t2[i, :, :]
            test_output[i * size:(i+1) * size, size:-size] = t1[i, :, :]
            test_output[i * size:(i+1) * size, -size:] = predicted[i, :, :]
        
        utils.save_image(test_output, 'data/output/{:05d}.jpg'.format(index))
        index += 1