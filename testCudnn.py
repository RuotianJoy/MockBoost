import torch
from torch.backends import cudnn

print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.current_device())



print(cudnn.is_available)
a = torch.tensor(1.)
print(cudnn.is_acceptable(a))
