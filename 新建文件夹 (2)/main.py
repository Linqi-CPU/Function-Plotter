import tkinter as tk
from tkinter import ttk
import math


class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("智能绘图板")
        self.root.geometry("900x700")

        # 绘图状态
        self.is_drawing = False
        self.is_auto_drawing = False
        self.auto_function = None
        self.last_x = None
        self.last_y = None

        # 滑动值计算
        self.slide_distance = 0.0

        # y值上限设定
        self.y_limit = 300

        # 画布尺寸
        self.canvas_width = 700
        self.canvas_height = 500

        self.setup_ui()
        self.populate_file_combobox()

    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ========== 最左侧自定义函数面板 ==========
        custom_panel = ttk.LabelFrame(main_frame, text="自定义函数", width=240)
        custom_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        custom_panel.pack_propagate(False)

        ttk.Label(custom_panel, text="函数名称:").pack(pady=2, padx=5, anchor=tk.NW)
        name_frame = ttk.Frame(custom_panel)
        name_frame.pack(pady=2, padx=5, fill=tk.X, anchor=tk.NW)
        self.custom_func_name_var = tk.StringVar(value="custom_func")
        ttk.Entry(name_frame, textvariable=self.custom_func_name_var, width=15).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        self.file_combobox = ttk.Combobox(name_frame, width=10, state="readonly")
        self.file_combobox.pack(side=tk.RIGHT, padx=2)
        self.file_combobox.bind("<<ComboboxSelected>>", self.on_file_select)

        ttk.Label(custom_panel, text="函数代码:").pack(pady=2, padx=5, anchor=tk.NW)
        self.custom_code_text = tk.Text(custom_panel, height=15, width=28, font=("Consolas", 9))
        self.custom_code_text.pack(pady=2, padx=5, fill=tk.BOTH, expand=True, anchor=tk.NW)
        # 使用函数名称框中的内容作为函数名
        func_name = self.custom_func_name_var.get()
        self.custom_code_text.insert("1.0", 
            f"def {func_name}(x, width, center_y, amp, freq):\n"
            "    # x: 当前x坐标\n"
            "    # width: 画布宽度\n"
            "    # center_y: 中心y坐标\n"
            "    # amp: 振幅\n"
            "    # freq: 频率\n"
            "    return center_y + amp * math.sin(freq * math.pi * x / width * 2)\n"
        )

        button_frame = ttk.Frame(custom_panel)
        button_frame.pack(fill=tk.X, pady=5, padx=5, side=tk.BOTTOM)
        ttk.Button(button_frame, text="保存函数", command=self.save_custom_function).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(button_frame, text="清除内容", command=self.clear_custom_function).pack(side=tk.RIGHT, padx=2, fill=tk.X, expand=True)

        # ========== 左侧控制面板 ==========
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", width=180)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        control_frame.pack_propagate(False)

        # --- 滑动值显示 ---
        slide_frame = ttk.LabelFrame(control_frame, text="滑动值计算")
        slide_frame.pack(fill=tk.X, padx=5, pady=5)

        self.slide_label = ttk.Label(slide_frame, text="滑动距离: 0.00", font=("Arial", 10))
        self.slide_label.pack(pady=5)

        ttk.Button(slide_frame, text="重置滑动值", command=self.reset_slide).pack(pady=2)

        # --- Y值限制设置 ---
        y_frame = ttk.LabelFrame(control_frame, text="Y值上限设定")
        y_frame.pack(fill=tk.X, padx=5, pady=5)

        self.y_limit_var = tk.IntVar(value=300)
        y_spinbox = ttk.Spinbox(y_frame, from_=50, to=500, textvariable=self.y_limit_var,
                                width=10, command=self.update_y_limit)
        y_spinbox.pack(pady=5)
        y_spinbox.bind("<Return>", lambda e: self.update_y_limit())

        self.y_limit_label = ttk.Label(y_frame, text=f"当前上限: {self.y_limit}")
        self.y_limit_label.pack(pady=2)

        # --- 自动画线函数设置 ---
        func_frame = ttk.LabelFrame(control_frame, text="自动画线函数")
        func_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(func_frame, text="函数类型:").pack(pady=2)
        self.func_type = tk.StringVar(value="sine")
        functions = [("正弦波", "sine"), ("余弦波", "cosine"),
                     ("抛物线", "parabola"), ("直线", "linear"), ("自定义", "custom")]
        for text, value in functions:
            rb = ttk.Radiobutton(func_frame, text=text, value=value, variable=self.func_type)
            rb.pack(anchor=tk.W, padx=10)

        ttk.Label(func_frame, text="振幅:").pack(pady=2)
        self.amplitude_var = tk.DoubleVar(value=100)
        ttk.Scale(func_frame, from_=10, to=200, variable=self.amplitude_var,
                  orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5)

        ttk.Label(func_frame, text="频率:").pack(pady=2)
        self.frequency_var = tk.DoubleVar(value=2)
        ttk.Scale(func_frame, from_=0.5, to=10, variable=self.frequency_var,
                  orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5)

        # --- 操作按钮 ---
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=10)

        # 清除按钮
        self.clear_btn = ttk.Button(btn_frame, text="清除按钮", command=self.clear_canvas)
        self.clear_btn.pack(fill=tk.X, pady=3)

        # 自动按钮
        self.auto_btn = ttk.Button(btn_frame, text="自动按钮", command=self.auto_draw)
        self.auto_btn.pack(fill=tk.X, pady=3)

        # 停止按钮
        self.stop_btn = ttk.Button(btn_frame, text="停止绘画", command=self.stop_drawing)
        self.stop_btn.pack(fill=tk.X, pady=3)

        # 帮助按钮
        ttk.Button(btn_frame, text="帮助", command=self.show_help).pack(fill=tk.X, pady=3)

        # ========== 右侧画布区域 ==========
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 画布
        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_width,
                                height=self.canvas_height, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 绘制Y值限制线（红色虚线）
        self.draw_y_limit_line()

        # 绑定事件
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # ========== 底部状态栏 ==========
        self.status_bar = ttk.Label(self.root, text="就绪 | 点击并拖动鼠标开始绘制",
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def draw_y_limit_line(self):
        """绘制Y值限制线"""
        self.canvas.delete("y_limit_line")
        self.canvas.create_line(0, self.y_limit, self.canvas_width, self.y_limit,
                                fill="red", dash=(5, 5), tags="y_limit_line")
        self.canvas.create_text(10, self.y_limit - 10, text=f"Y上限: {self.y_limit}",
                                anchor=tk.W, fill="red", tags="y_limit_line")

    def on_canvas_resize(self, event):
        """画布大小改变时更新"""
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.draw_y_limit_line()

    def update_y_limit(self):
        """更新Y值上限"""
        self.y_limit = self.y_limit_var.get()
        self.y_limit_label.config(text=f"当前上限: {self.y_limit}")
        self.draw_y_limit_line()

    def start_draw(self, event):
        """开始手动绘制"""
        if self.is_auto_drawing:
            self.stop_drawing()

        self.is_drawing = True
        self.last_x = event.x
        self.last_y = event.y

    def draw(self, event):
        """手动绘制过程，计算滑动值"""
        if not self.is_drawing:
            return

        # 计算滑动距离
        if self.last_x is not None and self.last_y is not None:
            distance = math.sqrt((event.x - self.last_x) ** 2 + (event.y - self.last_y) ** 2)
            self.slide_distance += distance
            self.slide_label.config(text=f"滑动距离: {self.slide_distance:.2f}")

        # 绘制线条
        self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                fill="blue", width=2, tags="manual_draw")

        self.last_x = event.x
        self.last_y = event.y

        # 更新状态栏
        self.status_bar.config(text=f"绘制中 | 坐标: ({event.x}, {event.y}) | 滑动值: {self.slide_distance:.2f}")

    def stop_draw(self, event=None):
        """停止手动绘制"""
        self.is_drawing = False
        self.last_x = None
        self.last_y = None
        self.status_bar.config(text=f"绘制结束 | 总滑动值: {self.slide_distance:.2f}")

    def reset_slide(self):
        """重置滑动值"""
        self.slide_distance = 0.0
        self.slide_label.config(text="滑动距离: 0.00")

    def clear_canvas(self):
        """清除按钮：中断绘画并清除画板"""
        # 中断所有绘画
        self.is_drawing = False
        self.is_auto_drawing = False
        self.last_x = None
        self.last_y = None

        # 清除画板上的所有绘制内容（保留Y限制线）
        self.canvas.delete("manual_draw")
        self.canvas.delete("auto_draw")

        # 重置滑动值
        self.slide_distance = 0.0
        self.slide_label.config(text="滑动距离: 0.00")

        self.status_bar.config(text="画板已清除")

    def auto_draw(self):
        """自动按钮：中断并清除绘画，然后调用内置函数自动绘画"""
        # 先执行清除操作
        self.clear_canvas()

        # 开始自动绘画
        self.is_auto_drawing = True
        self.status_bar.config(text="自动绘画中...")

        # 根据选择的函数类型绘制
        func_type = self.func_type.get()
        amplitude = self.amplitude_var.get()
        frequency = self.frequency_var.get()

        # X从画布左端到右端
        x_start = 0
        x_end = self.canvas_width
        canvas_height = self.canvas_height

        # 加载自定义函数
        custom_func = None
        if func_type == "custom":
            func_name = self.custom_func_name_var.get().strip()
            if not func_name:
                self.status_bar.config(text="错误: 请先设置自定义函数名称")
                self.is_auto_drawing = False
                return
            
            try:
                import importlib.util
                import os
                
                # 检查文件是否存在
                file_path = f"{func_name}.py"
                if not os.path.exists(file_path):
                    self.status_bar.config(text=f"错误: 文件 '{file_path}' 不存在")
                    self.is_auto_drawing = False
                    return
                
                # 加载模块
                spec = importlib.util.spec_from_file_location(func_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 检查模块中是否有对应的函数
                    if hasattr(module, func_name):
                        custom_func = getattr(module, func_name)
                        self.status_bar.config(text=f"成功加载函数 '{func_name}'")
                    else:
                        # 列出模块中所有可用的函数
                        available_funcs = [name for name in dir(module) if not name.startswith('_')]
                        func_list = ', '.join(available_funcs)
                        self.status_bar.config(text=f"错误: 文件中未找到函数 '{func_name}'，可用函数: {func_list}")
                        self.is_auto_drawing = False
                        return
                else:
                    self.status_bar.config(text=f"错误: 无法加载文件 '{file_path}'")
                    self.is_auto_drawing = False
                    return
                    
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                self.status_bar.config(text=f"加载失败: {str(e)}")
                print(f"详细错误信息:\n{error_detail}")
                self.is_auto_drawing = False
                return

        # 初始中心Y坐标
        center_y = canvas_height / 2

        # 计算函数的Y值范围，用于自动缩放
        def calculate_y_value(x_val):
            if func_type == "sine":
                return center_y + amplitude * math.sin(frequency * math.pi * x_val / self.canvas_width * 2)
            elif func_type == "cosine":
                return center_y + amplitude * math.cos(frequency * math.pi * x_val / self.canvas_width * 2)
            elif func_type == "parabola":
                normalized_x = (x_val - self.canvas_width / 2) / (self.canvas_width / 2)
                return center_y + amplitude * normalized_x ** 2
            elif func_type == "custom" and custom_func:
                try:
                    # 保持原始x值，不进行归一化
                    # 直接使用0到canvas_width的x值
                    result = custom_func(x_val, self.canvas_width, center_y, amplitude, frequency)
                    # 确保返回值是实数
                    if isinstance(result, complex):
                        # 如果是复数，取其实部
                        result = result.real
                    return result
                except Exception as e:
                    self.status_bar.config(text=f"函数计算错误: {str(e)}")
                    return center_y
            else:  # linear
                return center_y

        # 预计算所有点的Y值，确定范围
        y_values = []
        step = 2
        test_x = x_start
        while test_x <= x_end:
            y = calculate_y_value(test_x)
            y_values.append(y)
            test_x += step

        # 计算Y值范围
        if y_values:
            min_y = min(y_values)
            max_y = max(y_values)
            y_range = max(1, max_y - min_y)  # 避免除零
        else:
            min_y = center_y - 50
            max_y = center_y + 50
            y_range = 100

        # 计算缩放比例，确保图像在画布内
        # 留10%的边距
        available_height = canvas_height * 0.9
        scale_factor = available_height / y_range
        if scale_factor > 1:
            scale_factor = 1  # 不放大，只缩小

        # 计算新的中心Y坐标
        new_center_y = (min_y + max_y) / 2
        offset_y = canvas_height / 2 - new_center_y * scale_factor

        # 开始绘制
        x = x_start
        # 绘制起始点
        start_y = calculate_y_value(x)
        scaled_start_y = start_y * scale_factor + offset_y
        self.canvas.create_oval(x - 3, scaled_start_y - 3, x + 3, scaled_start_y + 3, fill="green", tags="auto_draw")

        def draw_step():
            nonlocal x
            if not self.is_auto_drawing or x > x_end:
                self.is_auto_drawing = False
                self.status_bar.config(text=f"自动绘画完成 | 滑动值: {self.slide_distance:.2f}")
                return

            # 计算下一点
            next_x = x + step

            # 计算当前点和下一点的Y值
            current_y = calculate_y_value(x)
            next_y = calculate_y_value(next_x)

            # 应用缩放
            scaled_current_y = current_y * scale_factor + offset_y
            scaled_next_y = next_y * scale_factor + offset_y

            # 绘制线条
            self.canvas.create_line(x, scaled_current_y, next_x, scaled_next_y,
                                    fill="green", width=2, tags="auto_draw")
            
            # 计算滑动值
            distance = math.sqrt((next_x - x) ** 2 + (scaled_next_y - scaled_current_y) ** 2)
            self.slide_distance += distance
            self.slide_label.config(text=f"滑动距离: {self.slide_distance:.2f}")

            x = next_x
            self.root.after(10, draw_step)  # 动画效果

        draw_step()

    def stop_drawing(self):
        """停止所有绘画"""
        self.is_drawing = False
        self.is_auto_drawing = False
        self.status_bar.config(text=f"绘画已停止 | 滑动值: {self.slide_distance:.2f}")

    def save_custom_function(self):
        """保存自定义函数到文件"""
        func_name = self.custom_func_name_var.get().strip()
        if not func_name:
            self.status_bar.config(text="错误: 函数名称不能为空")
            return

        code = self.custom_code_text.get("1.0", tk.END).strip()
        if not code:
            self.status_bar.config(text="错误: 函数代码不能为空")
            return

        try:
            with open(f"{func_name}.py", "w", encoding="utf-8") as f:
                f.write(code)
            self.status_bar.config(text=f"自定义函数 '{func_name}' 已保存到 {func_name}.py")
        except Exception as e:
            self.status_bar.config(text=f"保存失败: {str(e)}")

    def clear_custom_function(self):
        """清除自定义函数内容，替换为x*math.pi函数"""
        self.custom_code_text.delete("1.0", tk.END)
        # 使用函数名称框中的内容作为函数名
        func_name = self.custom_func_name_var.get()
        self.custom_code_text.insert("1.0", 
            f"def {func_name}(x, width, center_y, amp, freq):\n"
            "    # x: 当前x坐标\n"
            "    # width: 画布宽度\n"
            "    # center_y: 中心y坐标\n"
            "    # amp: 振幅\n"
            "    # freq: 频率\n"
            "    # 返回x*math.pi\n"
            "    return x * math.pi\n"
        )
        self.status_bar.config(text="自定义函数内容已重置为x*math.pi函数")

    def populate_file_combobox(self):
        """填充文件下拉框，列出所有.py文件（除了main.py）"""
        import os
        
        # 获取当前目录下的所有.py文件
        py_files = []
        for file in os.listdir('.'):
            if file.endswith('.py') and file != 'main.py':
                # 去掉.py后缀
                py_files.append(file[:-3])
        
        # 填充下拉框
        self.file_combobox['values'] = py_files
        
        # 如果有文件，默认选择第一个
        if py_files:
            self.file_combobox.current(0)

    def on_file_select(self, event):
        """处理文件选择事件，读取文件内容并显示在代码框中"""
        selected_file = self.file_combobox.get()
        if not selected_file:
            return
        
        try:
            # 构建文件路径
            file_path = f"{selected_file}.py"
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新函数名称输入框
            self.custom_func_name_var.set(selected_file)
            
            # 更新代码编辑框
            self.custom_code_text.delete("1.0", tk.END)
            self.custom_code_text.insert("1.0", content)
            
            # 更新状态栏
            self.status_bar.config(text=f"已加载文件 '{file_path}'")
            
        except Exception as e:
            self.status_bar.config(text=f"读取文件失败: {str(e)}")

    def show_help(self):
        """显示math库帮助窗口"""
        # 创建帮助窗口
        help_window = tk.Toplevel(self.root)
        help_window.title("Math库帮助")
        help_window.geometry("500x400")
        help_window.resizable(True, True)

        # 创建文本框显示帮助内容
        help_text = tk.Text(help_window, font=("Consolas", 10), wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(help_text, command=help_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        help_text.config(yscrollcommand=scrollbar.set)

        # 帮助内容
        help_content = """
Math库常用函数和常量
====================

1. 常量
-------
math.pi      - π (圆周率)，约等于 3.14159
math.e       - 自然对数的底，约等于 2.71828

2. 三角函数
-----------
math.sin(x)  - 正弦函数，x为弧度
math.cos(x)  - 余弦函数，x为弧度
math.tan(x)  - 正切函数，x为弧度
math.asin(x) - 反正弦函数，返回弧度
math.acos(x) - 反余弦函数，返回弧度
math.atan(x) - 反正切函数，返回弧度

3. 指数和对数
-------------
math.exp(x)  - e的x次方
math.log(x)  - 自然对数（以e为底）
math.log10(x) - 以10为底的对数
math.pow(x, y) - x的y次方
math.sqrt(x) - x的平方根

4. 其他常用函数
---------------
math.abs(x)  - 绝对值
math.ceil(x) - 向上取整
math.floor(x) - 向下取整
math.round(x) - 四舍五入
math.max(x, y, ...) - 最大值
math.min(x, y, ...) - 最小值

5. 使用示例
-----------
# 计算圆的面积
radius = 5
area = math.pi * math.pow(radius, 2)

# 计算正弦值（角度转弧度）
angle = 45
radians = math.radians(angle)
sin_value = math.sin(radians)

# 计算两点之间的距离
x1, y1 = 0, 0
x2, y2 = 3, 4
distance = math.sqrt(math.pow(x2-x1, 2) + math.pow(y2-y1, 2))

6. 在自定义函数中使用
-------------------
# 示例：创建一个螺旋函数
def spiral(x, width, center_y, amp, freq):
    angle = freq * 2 * math.pi * x / width
    radius = amp * x / width
    return center_y + radius * math.sin(angle)

# 示例：创建一个复合波形
def complex_wave(x, width, center_y, amp, freq):
    return center_y + amp * (math.sin(freq * math.pi * x / width * 2) + 
                            0.5 * math.cos(freq * 4 * math.pi * x / width * 2))
"""

        # 插入帮助内容
        help_text.insert("1.0", help_content)

        # 禁止编辑
        help_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
