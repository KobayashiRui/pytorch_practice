import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.optim import lr_scheduler
from torch.autograd import Variable
import torchvision
from torchvision import transforms, datasets, models

import matplotlib.pyplot as plt
import numpy as np


def imshow(images, title=None):
    images = images.numpy().transpose((1, 2, 0))  # (h, w, c)
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    images = std * images + mean
    images = np.clip(images, 0, 1)
    #print(images)
    plt.imshow(images)
    if title is not None:
        plt.title(title)
    plt.show()

#訓練データの学習
def train(train_loader):
    #scheduler.step()
    model_ft.train()
    running_loss = 0
    for batch_idx, (images,labels) in enumerate(train_loader):
        if use_gpu:
            images = Variable(images.cuda())
            labels = Variable(labels.cuda())
        else:
            images = Variable(images)
            labels = Variable(labels)

        optimizer.zero_grad()
        outputs = model_ft(images)

        loss = criterion(outputs,labels)
        running_loss += loss.item()

        loss.backward()
        optimizer.step()

    train_loss = running_loss / len(train_loader)

    return train_loss

#テストデータに対する精度を見る
def valid(test_loader):
    model_ft.eval()
    running_loss = 0
    correct = 0
    total = 0
    for batch_idx, (images,labels) in enumerate(test_loader):
        if use_gpu:
            images = Variable(images.cuda(), volatile=True)
            labels = Variable(labels.cuda(), volatile=True)
        else:
            images = Variable(images,volatile=True)
            labels = Variable(labels,volatile=True)

        outputs = model_ft(images)

        loss = criterion(outputs, labels)
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data,1)
        correct += (predicted == labels.data).sum()
        total += labels.size()[0]

    correct = float(correct)
    total   = float(total)
    val_loss = running_loss / len(test_loader)
    val_acc  = correct / total
    #print(val_acc)

    return(val_loss,val_acc)

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.layer1 = nn.Sequential(
        nn.Conv2d(3,16,kernel_size=5,padding=2),
        nn.BatchNorm2d(16),
        nn.ReLU(),
        nn.MaxPool2d(2),
        )

        self.layer2 = nn.Sequential(
        nn.Conv2d(16,32,kernel_size=5,padding=2),
        nn.BatchNorm2d(32),
        nn.ReLU(),
        nn.MaxPool2d(2),
        )

        self.layer3 = nn.Sequential(
        nn.Conv2d(32,64,kernel_size=5,padding=2),
        nn.BatchNorm2d(64),
        nn.ReLU(),
        nn.MaxPool2d(2),
        )

        self.fc = nn.Linear(50176,5000)
        self.fc2 = nn.Linear(5000,2)

    def forward(self, out):
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = out.view(out.size(0),-1)
        out = self.fc(out)
        out = F.dropout(out, training=self.training)
        out = self.fc2(out)
        return out
    

data_transform = {
    'train': transforms.Compose([
    #transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    #transforms.RandomVerticalFlip(),
    transforms.RandomRotation((-60,60)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485,0.456,0.406],std=[0.229,0.224,0.225]),
    ]),
    'val': transforms.Compose([
    #transforms.RandomResizedCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485,0.456,0.406],std=[0.229,0.224,0.225]),
    ])
}

# train data読み込み
hymenoptera_dataset = datasets.ImageFolder(root='small_or_big_dataset/train',
                                           transform=data_transform['train'])
dataset_loader = torch.utils.data.DataLoader(hymenoptera_dataset,
                                             batch_size=4, shuffle=True,
                                             num_workers=4)

# test data読み込み
hymenoptera_testset = datasets.ImageFolder(root='small_or_big_dataset/test',transform=data_transform['val'])

dataset_testloader = torch.utils.data.DataLoader(hymenoptera_testset, batch_size=4,shuffle=False, num_workers=4)

classes = ('big','small')

images, classes_nam = next(iter(dataset_loader))
print(images.size(), classes_nam.size())  # torch.Size([4, 3, 224, 224]) torch.Size([4])
images = torchvision.utils.make_grid(images)
imshow(images, title=[classes[x] for x in classes_nam])

#modelの作成
model_ft = Net() #このままだと1000クラス分類なので512->1000
#for param in model_ft.parameters():
#    param.requires_grad = False
use_gpu = torch.cuda.is_available()
num_epochs = 100
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model_ft.parameters(), lr=0.0001)
#optimizer = optim.SGD(model_ft.parameters(), lr=0.01, momentum=0.9)
#scheduler = lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.1)

if use_gpu:
    model_ft.cuda()
    print("use cuda!!")

#学習開始
loss_list = []
val_loss_list = []
val_acc_list =[]

for epoch in range(num_epochs):
    loss = train(dataset_loader)
    val_loss, val_acc = valid(dataset_testloader)

    print('epoch : {}, loss : {:.4f}, val_loss : {:.4f}, val_acc : {:.4f}'.format(epoch,loss,val_loss, val_acc))
    #print("epoch : {}, loss : {:.4f}".format(epoch,loss))
    #logging
    loss_list.append(loss)
    val_loss_list.append(val_loss)
    val_acc_list.append(val_acc)

torch.save(model_ft.state_dict(),'mynn_weight_sb.pth')
plt.plot(range(num_epochs),loss_list,label="train_loss")
plt.plot(range(num_epochs),val_loss_list,label="val_loss")
plt.legend()
plt.show()
