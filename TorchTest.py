import torch
print(torch.__version__)
print(torch.cuda.is_available())  # 应返回True
print(torch.cuda.device_count())  # 应返回大于0的数字
print(torch.cuda.get_device_name(0))  # 应显示GPU的名称
print(torch.cuda.device_count())  # 输出系统中可用的GPU数量