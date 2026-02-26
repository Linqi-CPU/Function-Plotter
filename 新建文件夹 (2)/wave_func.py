import math

def wave_func(x, width, center_y, amp, freq):
    # x: 当前x坐标
    # width: 画布宽度
    # center_y: 中心y坐标
    # amp: 振幅
    # freq: 频率
    
    # 创建一个复合波形：正弦波 + 余弦波
    normalized_x = x / width
    y = center_y + amp * (math.sin(freq * 2 * math.pi * normalized_x) + 
                          0.5 * math.cos(freq * 4 * math.pi * normalized_x))
    return y