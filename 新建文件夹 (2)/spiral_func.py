import math

def spiral_func(x, width, center_y, amp, freq):
    # x: 当前x坐标
    # width: 画布宽度
    # center_y: 中心y坐标
    # amp: 振幅
    # freq: 频率
    
    # 创建一个螺旋形状
    normalized_x = x / width
    angle = freq * 2 * math.pi * normalized_x
    radius = amp * normalized_x
    y = center_y + radius * math.sin(angle)
    return y