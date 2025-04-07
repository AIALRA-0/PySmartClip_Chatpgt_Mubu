import tkinter as tk
from tkinter import scrolledtext

def process_text(text):
    text = text.replace("。", "；")  # 将所有。替换为；
    text = text.replace("\\)", "$")  # 将所有\)替换为$
    text = text.replace("\\(", "$")  # 将所有\(替换为$
    return text

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

check_clipboard.last_text = ""

# 创建主窗口
root = tk.Tk()
root.title("文本处理工具")
root.geometry("500x500")

# 设置窗口始终置顶
root.attributes("-topmost", True)

# 输出框
output_label = tk.Label(root, text="处理后文本:")
output_label.pack()
output_area = scrolledtext.ScrolledText(root, height=20, width=60, state=tk.DISABLED)  # 增大高度与宽度
output_area.pack(expand=True, fill='both')  # 允许窗口大小自动扩展填满整个区域
# 复制按钮
tk.Button(root, text="复制处理后文本", command=copy_to_clipboard).pack()

# 启动剪贴板监听
check_clipboard()

# 运行应用
root.mainloop()
