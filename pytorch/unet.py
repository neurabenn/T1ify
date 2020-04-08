import torch
import torch.nn as nn
### define breadth 
### breadth is a factor which defines number of neurons
### influences the capacity of network -- too high --> overfitting, too lo --> bad
### influences how much ram and memory is udes
BREADTH = 8

class BlockDown(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(BlockDown, self).__init__()
        ### class initialized 
        self.layers = nn.Sequential(
            ### use sequential to create sequentia list of nn
            ### 2X 1: conv2d 2: Batchnorm 3: ReLU 
            nn.Conv2d(in_channels = in_channels, out_channels = out_channels, kernel_size = 3, padding=1),
            ### kernel - size of window sliding over input
            ### padding - maintains dimension size of input and output
            ### stride - amount of pixels moved each time. default = 1
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels = out_channels, out_channels = out_channels, kernel_size = 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
            
            #### thing you can play with to make better or worse
            ### number of conv->BN->RElu iterations
        )
    
    def forward(self, input):
        x, skip_values = input
        x = self.layers(x)
        skip_values = skip_values + [x]
        x = torch.nn.functional.max_pool2d(x, 2)
        return x, skip_values

class BlockUp(nn.Module):
    def __init__(self, in_channels, out_channels, use_relu=True):
        super(BlockUp, self).__init__()
        layers = [
            nn.Conv2d(in_channels = in_channels * 2, out_channels = out_channels, kernel_size = 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels = out_channels, out_channels = out_channels, kernel_size = 3, padding=1),
            nn.BatchNorm2d(out_channels)
        ]
        ##### disable activation function for final layer. 
        ##### final layer should use sigmoid as we want 0-1 output
        if use_relu:
            layers.append(nn.ReLU(inplace=True))

        self.layers = nn.Sequential(*layers)
        #### here we increase the resolution going up. #going down we lose resolution, and we vuild it back up in the up. 
        #### counter part to the max pooling
        self.up_conv = nn.ConvTranspose2d(in_channels=in_channels, out_channels=in_channels, kernel_size=4, stride=2, padding=1)
    
    def forward(self, input):
        x, skip_values = input
        x = self.up_conv(x)
        x = nn.functional.relu(x)
        x = torch.cat([x, skip_values[-1]], dim=1) 
        x = self.layers(x)
        return x, skip_values[:-1]

class Block(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(Block, self).__init__()
        self.layers = nn.Sequential(
            nn.Conv2d(in_channels = in_channels, out_channels = out_channels, kernel_size = 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels = out_channels, out_channels = out_channels, kernel_size = 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, input):
        x, skip_values = input
        x = self.layers(x)
        return x, skip_values

    ### define Unet class using torch nn.model
class UNet(nn.Module):
    def __init__(self):
        super(UNet, self).__init__()
        ### define sequential neural networks
        ### can do outside of sequential model bu this is more conventient
        ### takes list of nn and runs as sequential list of nn's all in one
        self.layers = nn.Sequential(
            ### start going down
            BlockDown(1, BREADTH * 1),
            BlockDown(BREADTH * 1, BREADTH * 2),
            BlockDown(BREADTH * 2, BREADTH * 4),
            BlockDown(BREADTH * 4, BREADTH * 8),
            BlockDown(BREADTH * 8, BREADTH * 8),
            BlockDown(BREADTH * 8, BREADTH * 8),
            ### reach bottom of U-NET
            ### each down block adds a skip value --line 24 (forward fxn)
            Block(BREADTH * 8, BREADTH * 8),
            ### start going back up
            ### each up block removes a skip connection  --line 52 (forward fxn)
            BlockUp(BREADTH * 8, BREADTH * 8),
            BlockUp(BREADTH * 8, BREADTH * 8),
            BlockUp(BREADTH * 8, BREADTH * 4),
            BlockUp(BREADTH * 4, BREADTH * 2),
            BlockUp(BREADTH * 2, BREADTH * 1),
            BlockUp(BREADTH * 1, 1, use_relu=False)
        )

        self.cuda()
    #### x should have 4 dimensions
    #### dim 1 = batch dimension - how many images are loaded every time the network is called. 
    #### dimension is left empty if for only one image
    #### dim2 = feature dimension (if in forward). (color dimension)
    #### dim3 x dimension
    #### dim4 y dimension
    #### example: [32, 1, 128, 128] 32 images, 1 color, size 128 x 128
    def forward(self, x):
        if len(x.shape) == 3:
            x = x.unsqueeze(1)
            #### example : x is an image and the  empty list will be filled with skip connections
        return torch.sigmoid(self.layers((x, []))[0])
    #### All this defines the structure of the network
