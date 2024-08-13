import os
import tarfile
import glob
import random
import pandas as pd
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import transforms
from sklearn.model_selection import train_test_split
import sys

# Custom Dataset class
class ImageDataset(Dataset):
    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path)
        if self.transform:
            image = self.transform(image)
        label = self.labels[idx]
        return image, label

# Extract and load images
def extract_images(base_path):
    image_paths = []
    labels = []
    classes = ['plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
    for category in classes:
        tar_files = glob.glob(f"{base_path}/cifar10_images_{category}_*.tgz")
        for tar_file in tar_files:
            # Create a folder with the same name as the .tgz file minus the extension
            folder_name = os.path.splitext(os.path.basename(tar_file))[0]
            extracted_folder = os.path.join(base_path, folder_name)
            os.makedirs(extracted_folder, exist_ok=True)
            
            # Extract the contents of the .tgz file into this folder
            with tarfile.open(tar_file, 'r:gz') as tar:
                tar.extractall(path=extracted_folder)
                print(f"Extracted {tar_file} to {extracted_folder}")
                
                # The images are located in the 'cifar10_images' subfolder within the extracted folder
                images_folder = os.path.join(extracted_folder, 'cifar10_images')
                extracted_images = glob.glob(f"{images_folder}/*.png")
                image_paths.extend(extracted_images)
                labels.extend([classes.index(category)] * len(extracted_images))

            # Optionally, you can delete the extracted folder after processing to save space
            # shutil.rmtree(extracted_folder)
    print("ex", image_paths, labels)
    return image_paths, labels

print ("Start transform")
# Define transformations
transform = transforms.Compose([
    transforms.Resize((32, 32)),  # Resizing images to 32x32, adjust as necessary
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])

if __name__ == '__main__':
    # Load data and split into train/validation/test
    base_path = '../data/generated_images'
    image_paths, labels = extract_images(base_path)

    print ("Split")
    train_paths, temp_paths, train_labels, temp_labels = train_test_split(image_paths, labels, test_size=0.4, stratify=labels)
    val_paths, test_paths, val_labels, test_labels = train_test_split(temp_paths, temp_labels, test_size=0.5, stratify=temp_labels)

    train_dataset = ImageDataset(train_paths, train_labels, transform=transform)
    val_dataset = ImageDataset(val_paths, val_labels, transform=transform)
    test_dataset = ImageDataset(test_paths, test_labels, transform=transform)

    trainloader = DataLoader(train_dataset, batch_size=4, shuffle=True, num_workers=2)
    valloader = DataLoader(val_dataset, batch_size=4, shuffle=False, num_workers=2)
    testloader = DataLoader(test_dataset, batch_size=4, shuffle=False, num_workers=2)

    # Define the neural network
    class Net(nn.Module):
        def __init__(self):
            super(Net, self).__init__()
            self.conv1 = nn.Conv2d(3, 6, 5)
            self.pool = nn.MaxPool2d(2, 2)
            self.conv2 = nn.Conv2d(6, 16, 5)
            self.fc1 = nn.Linear(16 * 5 * 5, 120)
            self.fc2 = nn.Linear(120, 84)
            self.fc3 = nn.Linear(84, 10)

        def forward(self, x):
            x = self.pool(F.relu(self.conv1(x)))
            x = self.pool(F.relu(self.conv2(x)))
            x = x.view(-1, 16 * 5 * 5)
            x = F.relu(self.fc1(x))
            x = F.relu(self.fc2(x))
            x = self.fc3(x)
            return x

    # Initialize the network, criterion, and optimizer
    net = Net()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    # Training the model
    num_epochs = int(sys.argv[1])
    train_results = []
    val_results = []

    print ("Start train")
    for epoch in range(num_epochs):
        net.train()
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            inputs, labels = data
            optimizer.zero_grad()
            outputs = net(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        # Record training loss
        avg_train_loss = running_loss / len(trainloader)
        train_results.append({'epoch': epoch + 1, 'loss': avg_train_loss})
        
        # Validation
        net.eval()
        val_loss = 0.0
        with torch.no_grad():
            for data in valloader:
                inputs, labels = data
                outputs = net(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item()

        avg_val_loss = val_loss / len(valloader)
        val_results.append({'epoch': epoch + 1, 'loss': avg_val_loss})
        print(f'[Epoch {epoch + 1}] Train loss: {avg_train_loss:.3f}, Validation loss: {avg_val_loss:.3f}')

    # Save the model
    torch.save(net.state_dict(), '../data/cifar10_model.pth')

    # Save training and validation results to CSV files
    train_df = pd.DataFrame(train_results)
    val_df = pd.DataFrame(val_results)
    train_df.to_csv('../data/train_results.csv', index=False)
    val_df.to_csv('../data/val_results.csv', index=False)

    # Testing the model
    correct = 0
    total = 0
    with torch.no_grad():
        for data in testloader:
            images, labels = data
            outputs = net(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    print(f'Accuracy of the network on the test images: {100 * correct / total:.2f} %')
