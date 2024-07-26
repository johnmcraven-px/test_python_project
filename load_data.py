import os
import torch
import torchvision
import torchvision.transforms as transforms
from PIL import Image
import json

# Define the transformation
transform = transforms.Compose([
    transforms.ToTensor()
])

# Load the CIFAR-10 dataset
trainset = torchvision.datasets.CIFAR10(root='../data/input', train=True, download=True, transform=transform)
# testset = torchvision.datasets.CIFAR10(root='../data/input', train=False, download=True, transform=transform)


with open('../data/run_params.json') as f:
    runParams = json.load(f)
className = runParams["class"]
startIdxInclusive = runParams["startIdxInclusive"]
endIdxExclusive = runParams["endIdxExclusive"]

# Directory to save images
train_dir = '../data/cifar10_images'

# Create directories if they don't exist
os.makedirs(train_dir, exist_ok=True)
#os.makedirs(test_dir, exist_ok=True)

classes = ('plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck')

# Function to save images
def save_images(dataset, directory):
    foundIdx = -1
    for i in range(len(dataset)):
        img, label = dataset[i]
        if classes[label] == className:
            foundIdx += 1
            if foundIdx < startIdxInclusive:
                continue
            if foundIdx >= endIdxExclusive:
                break
            img = transforms.ToPILImage()(img)
            img.save(os.path.join(directory, f'{foundIdx}_{className}.png'))

# Save training images
save_images(trainset, train_dir)

# Save test images
#save_images(testset, test_dir)

print('Images saved successfully!')