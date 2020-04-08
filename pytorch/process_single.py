#### applies trained network to an input jpeg
from itertools import count
from skimage import io

import torch
from torch.utils.data import DataLoader
from jpeg_dataset import JpegDataset
from tqdm import tqdm
from torchvision import utils
import math

from unet import UNet
import sys

input_filename = sys.argv[1]
output_filename = sys.argv[2]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NETWORK_FILENAME = 'trained_models/unet.to'
network = UNet()
network.load_state_dict(torch.load(NETWORK_FILENAME))
network.cuda()
network.eval()


image = io.imread(input_filename)[:, :, 0] / 255.0
SIZE_BASE = 64
size = tuple(math.ceil(x / SIZE_BASE) * SIZE_BASE for x in image.shape)

tensor = torch.zeros(size, dtype=torch.float32, device=device)
tensor[:image.shape[0], :image.shape[1]] = torch.tensor(image, dtype=torch.float32, device=device)


with torch.no_grad():
    output = network(tensor.unsqueeze(0)).squeeze().squeeze()

output = output[:image.shape[0], :image.shape[1]]
utils.save_image(output, output_filename)
