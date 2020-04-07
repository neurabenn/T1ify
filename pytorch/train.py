from itertools import count

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.utils.data import DataLoader
from tqdm import tqdm
from jpeg_dataset import *

from unet import UNet

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NETWORK_FILENAME = 'trained_models/unet.to'

network = UNet()
try:
    network.load_state_dict(torch.load(NETWORK_FILENAME))
except:
    print("Found no model, training a new one.")
network.cuda()

dataset = JpegPairsDataset()
data_loader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=8)

optimizer = optim.Adam(network.parameters(), lr=0.0002)
criterion = nn.MSELoss()

def train():
    for epoch in count():
        loss_history = []
        for batch in tqdm(data_loader):
            network_input, ground_truth = batch
            network_input = network_input.to(device)
            ground_truth = ground_truth.to(device)

            network.zero_grad()
            output = network(network_input).squeeze(1)
            loss = criterion(output, ground_truth)
            loss.backward()
            optimizer.step()
            error = loss.item()
            loss_history.append(error)

        print(epoch, np.mean(loss_history))
        torch.save(network.state_dict(), NETWORK_FILENAME)

train()