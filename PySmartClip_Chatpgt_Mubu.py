import re
from collections import Counter  # 用于统计字符频次
import tkinter as tk
from tkinter import scrolledtext

def process_text(text):
    text = convert_to_raw_text(text)  
    text = remove_chn_symbols(text)
    text = remove_newline_char(text)
    text = remove_unicode_control_char(text)
    text = remove_double_backslashes(text)
    text = remove_duplicate_non_chinese(text)
    text = remove_star_wrapped_chinese(text)
    text = replace_eng_with_chn_char(text)
    text = final_cleanup(text)

    return text

def remove_chn_symbols(text):
    text = text.replace("。",".")
    return text

def remove_newline_char(text):
    
    # 允许保留的 LaTeX 符号列表
    allowed_latex_symbols = ["nabla", "neq", "nmid", "nparallel"]

    # 先找到所有 `\n` 的位置
    matches = list(re.finditer(r'\\n[a-zA-Z]*', text))
    
    # 处理后的文本构建
    new_text = []
    last_pos = 0
    
    for match in matches:
        start, end = match.span()  # 获取匹配的起止位置
        match_text = text[start:end]  # 取出匹配的文本

        # 判断是否是 LaTeX 符号
        if any(match_text.startswith(f"\\{symbol}") for symbol in allowed_latex_symbols):
            new_text.append(text[last_pos:end])  # **保留完整的 LaTeX 符号**
        else:
            new_text.append(text[last_pos:start])  # **删除 `\n`，但保留后续内容**
            new_text.append(text[start+2:end])  # **添加 `\n` 后的内容，避免丢失字符**
        
        last_pos = end  # 更新起点位置

    new_text.append(text[last_pos:])  # 加上剩余部分

    result_text = "".join(new_text)  # 组合文本
    return result_text

    
def remove_double_backslashes(text):
    # 使用 replace() 去除双斜线
    return text.replace("\\\\", "\\")

def replace_eng_with_chn_char(text):
    result = []  # 存放处理后的文本
    inside_math = False  # 标记是否在数学公式内
    buffer = ""  # 缓存当前正在处理的内容
    
    for char in text:
        if char == "$":  
            if inside_math:
                # 结束一个数学块
                buffer += "$"
                result.append(buffer)  # 直接存入结果，不做替换
                buffer = ""
            else:
                # 开始一个数学块
                result.append(buffer.replace(',', '，').replace('.', '；').replace(':', '：'))  # 处理非数学块
                buffer = "$"
            inside_math = not inside_math  # 翻转标志
        else:
            buffer += char  # 继续累积字符
    
    # 处理最后的剩余部分（如果最后不是数学块）
    if buffer:
        result.append(buffer.replace(',', '，').replace('.', '；').replace(':', '：'))
    
    return "".join(result)

def convert_to_raw_text(text):
    text = repr(text).strip("'")
    text = text.replace("\\x0c", "\\f")
    return text

def remove_unicode_control_char(text):
    """去除开头的控制字符及后两个字符"""
    # 使用原始字符串（Raw String），避免反斜杠被误解释为转义字符
    # 检测文本中是否包含 \u20 开头的字符，并删除其后两个字符
    while '\\u20' in text:  # 如果文本中存在 \u20
        match = re.search(r'\\u20.{2}', text)  # 查找匹配的 \u20 后面跟着的两个字符
        if match:
            # 删除匹配到的部分
            text = text[:match.start()] + text[match.end():]
    return text

def remove_duplicate_non_chinese(text):
    # 提取所有非中文部分，并去除前后空格
    non_chinese_parts = [part.strip() for part in re.findall(r'[^\u4e00-\u9fa5]+', text)]

    # 处理每个非中文部分，去掉开头的符号（按需添加）
    non_chinese_parts = [re.sub(r'^[\s:：,，.。;；（）()*]+|[\s:：,，.。;；（）()*]+$', '', part) for part in non_chinese_parts]

    # 处理符号后的空格
    non_chinese_parts = [part.strip() for part in non_chinese_parts]


    for part in non_chinese_parts:
        length = len(part)
        if length < 2:
            continue  # 如果长度小于2，跳过匹配

        i = 0
        matched = False  # 记录是否找到匹配
        while not matched:  # 直到找到匹配
            # 找到首个字符在后面所有匹配的字符，并提取从匹配点到结尾的部分
            matches = [(j, part[j:]) for j in range(length - 1, i, -1) if part[j] == part[i]]
            for j, match_segment in matches:
                # 1. **检查前后是否完全匹配**
                if part.startswith(match_segment):
                    # 删除两端匹配部分
                    new_part = part[len(match_segment):-len(match_segment)]
                    new_part = "$" + new_part + "$"
                    text = text.replace(part, new_part, 1)
                    matched = True  # 记录成功匹配
                    break  # 处理完后退出匹配循环
            
            if matched:
                break  # 成功匹配后退出外层循环
            
            # 2. **如果完全匹配失败，则检查前后部分是否包含相同字符**
            for j, match_segment in matches:
                match_length = len(match_segment)

                # 获取前后等长部分
                left_part = part[:match_length]
                right_part = part[-match_length:]

                if Counter(left_part) == Counter(right_part):  # 判断字符和数量是否相同
                    new_part = part[match_length:-match_length]  # 删除前后等长部分
                    new_part = "$" + new_part + "$"
                    text = text.replace(part, new_part, 1)
                    matched = True
                    break  # 退出匹配循环
            break  # 退出匹配循环
    return text

def remove_star_wrapped_chinese(text):
    """
    去掉文本中间是中文，两端是**的部分，例如 **目标**，以及两端的空格
    """
    text = re.sub(r'\*\*([\u4e00-\u9fa5]+)\*\*', r'\1', text)
    text = re.sub(r'\*\*([\u4e00-\u9fa5]+)', r'\1', text)
    text = re.sub(r'([\u4e00-\u9fa5]+)\*\*', r'\1', text)
    text = re.sub(r' ([\u4e00-\u9fa5]+) ', r'\1', text)
    text = re.sub(r'([\u4e00-\u9fa5]+) ', r'\1', text)
    text = re.sub(r' ([\u4e00-\u9fa5]+)', r'\1', text)
    return text

def final_cleanup(text):
    result = []
    inside_math = False
    buffer = ""

    i = 0
    while i < len(text):
        if text[i] == "$":
            if inside_math:
                buffer += "$"
                result.append(buffer)  # 数学块内容原样保留
                buffer = ""
            else:
                # 非数学块：清理 buffer
                cleaned = buffer.replace("**", "")
                cleaned = cleaned.replace(" ", "").replace("\u3000", "")
                result.append(cleaned + "$")
                buffer = ""
            inside_math = not inside_math
            i += 1
        else:
            buffer += text[i]
            i += 1

    # 处理最后一段（如果不在数学块中）
    if buffer:
        if inside_math:
            result.append(buffer)  # 理论上不应该落单，但安全起见保留
        else:
            cleaned = buffer.replace("**", "")
            cleaned = cleaned.replace(" ", "").replace("\u3000", "")
            result.append(cleaned)

    return "".join(result)

def check_clipboard():
    try:
        current_clipboard = root.clipboard_get()
        if isinstance(current_clipboard, str) and current_clipboard != check_clipboard.last_text:
            check_clipboard.last_text = current_clipboard
            processed_text = process_text(current_clipboard)
            output_area.config(state=tk.NORMAL)
            output_area.delete("1.0", tk.END)
            output_area.insert(tk.END, processed_text)
            output_area.config(state=tk.DISABLED)
    except tk.TclError:
        pass  # 忽略非文本剪贴板内容
    root.after(1000, check_clipboard)  # 每秒检查一次剪贴板

def copy_to_clipboard():
    processed_text = output_area.get("1.0", tk.END).strip()
    if processed_text:
        root.clipboard_clear()
        root.clipboard_append(processed_text)
        root.update()

# 测试
print("text 1:", process_text("目标是找到 c∗c^*c∗ 使得 xxx 和 g(c)g(c)g(c) 之间的距离最小"))
print("text 2:", process_text("g(c)g(c)g(c)是由编码 ccc 生成的近似重构向量"))
print("text 3:", process_text("这是**目标**需要实现的功能"))
print("text 4:", process_text("计算公式：P[r][c]=max⁡1≤i≤d,1≤j≤dA[(r−1)s+i][(c−1)s+j] P[r][c] = \max_{1 \leq i \leq d, 1 \leq j \leq d} A[(r-1)s + i][(c-1)s + j] P[r][c]=1≤i≤d,1≤j≤dmaxA[(r−1)s+i][(c−1)s+j]其中："))
print("text 5:", process_text("将梯度传递到上一层∇Hl−1(m)=Wl∇Zl(m)\nabla H^{l-1}(m) = W^l \nabla Z^l(m)∇Hl−1(m)=Wl∇Zl(m)"))
print("text 6:", process_text("偏置梯度的计算如下：∇W0L+1(m)=∂z(m)∂W0L+1∂σM(z(m))∂z(m)∇y^(m)\nabla W_0^{L+1}(m) = \frac{\partial z(m)}{\partial W_0^{L+1}} \frac{\partial \sigma_M (z(m))}{\partial z(m)} \nabla \hat{y}(m)∇W0L+1(m)=∂W0L+1∂z(m)∂z(m)∂σM(z(m))∇y^(m)，由于：∂z(m)∂W0L+1=1\frac{\partial z(m)}{\partial W_0^{L+1}} = 1∂W0L+1∂z(m)=1，所以：∇W0L+1(m)=∂σM(z(m))∂z(m)∇y^(m)\nabla W_0^{L+1}(m) = \frac{\partial \sigma_M (z(m))}{\partial z(m)} \nabla \hat{y}(m)∇W0L+1(m)=∂z(m)∂σM(z(m))∇y^(m)"))
print("text 7:", process_text("测试： 案例； g(c.1)g(c.1)g(c.1) 我不知道： f(x) = x, y:2.5f(y)=y，xf(x) = x, y:2.5； 结束"))

check_clipboard.last_text = ""

# 创建主窗口
root = tk.Tk()
root.title("文本处理工具")
root.geometry("500x200")

# 设置窗口始终置顶
root.attributes("-topmost", True)

# 输出框
output_label = tk.Label(root, text="处理后文本:")
output_label.pack()
output_area = scrolledtext.ScrolledText(root, height=5, state=tk.DISABLED)
output_area.pack()

# 复制按钮
tk.Button(root, text="复制处理后文本", command=copy_to_clipboard).pack()

# 启动剪贴板监听
check_clipboard()

# 运行应用
root.mainloop()

