import tkinter as tk
from tkinter import scrolledtext
import re

class TextProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文本处理工具")
        self.root.geometry("500x500")
        self.root.attributes("-topmost", True)

        self.is_locked = False  # 添加一个状态变量来检测是否锁定
        self.last_text = ""

        self.output_label = tk.Label(root, text="处理后文本:")
        self.output_label.pack()

        self.output_area = scrolledtext.ScrolledText(root, height=20, width=60, state=tk.DISABLED)
        self.output_area.pack(expand=True, fill='both')

        self.copy_button = tk.Button(root, text="复制处理后文本", command=self.copy_to_clipboard)
        self.copy_button.pack()

        self.lock_button = tk.Button(root, text="🟢 解锁", bg="green", fg="white", command=self.toggle_lock)
        self.lock_button.pack()

        self.check_clipboard()  # 开始监听剪贴板

    def toggle_lock(self):
        """切换锁定状态"""
        self.is_locked = not self.is_locked
        if self.is_locked:
            self.lock_button.config(text="🔴 锁定", bg="red", fg="white")
        else:
            self.lock_button.config(text="🟢 解锁", bg="green", fg="white")
            self.check_clipboard()  # 解锁时立即重新开始监听

    def clean_text(self, text):
        """去掉行首和行尾的空格、逗号、句号。"""
        text = text.strip()
        text = re.sub(r'^[,，.。]+', '', text)
        text = re.sub(r'[,，.。]+$', '', text)
        return text.strip()

    def process_text(self, text):
        text = text.strip()
        text = text.replace("。", "；")
        text = text.replace("\\)", "$")
        text = text.replace("\\(", "$")
        text = text.replace("**", "")
        text = text.replace("---", "")
        text = re.sub(r'#{2,}', '', text)
        
        text = re.sub(r"\\\[(.*?)\\\]", lambda m: f"${' '.join(m.group(1).strip().splitlines())}$", text, flags=re.DOTALL)
        
        lines = text.split('\n')
        merged_lines = []
        buffer = []

        for line in lines:
            stripped_line = line.strip()
            
            if stripped_line.startswith('- '):
                if buffer:
                    buffer.append(self.clean_text(stripped_line[2:].strip()))
                else:
                    buffer = [self.clean_text(stripped_line[2:].strip())]
            else:
                if buffer:
                    merged_line = ""
                    for i, item in enumerate(buffer):
                        item = self.clean_text(item)
                        if i == 0:
                            merged_line += item
                        else:
                            if merged_line.endswith('；'):
                                merged_line += f" {item}"
                            else:
                                merged_line += f"；{item}"
                    
                    merged_lines.append(merged_line)
                    buffer = []
                merged_lines.append(line)
        
        if buffer:
            merged_line = ""
            for i, item in enumerate(buffer):
                item = self.clean_text(item)
                if i == 0:
                    merged_line += item
                else:
                    if merged_line.endswith('；'):
                        merged_line += f" {item}"
                    else:
                        merged_line += f"；{item}"
                        
            merged_lines.append(merged_line)
        
        return '\n'.join(merged_lines)

    def check_clipboard(self):
        if not self.is_locked:  # 只有在未锁定状态下才监听剪贴板
            try:
                current_clipboard = self.root.clipboard_get()
                if isinstance(current_clipboard, str) and current_clipboard != self.last_text:
                    self.last_text = current_clipboard
                    processed_text = self.process_text(current_clipboard)
                    self.output_area.config(state=tk.NORMAL)
                    self.output_area.delete("1.0", tk.END)
                    self.output_area.insert(tk.END, processed_text)
                    self.output_area.config(state=tk.DISABLED)
            except tk.TclError:
                pass
        
        if not self.is_locked:
            self.root.after(1000, self.check_clipboard)

    def copy_to_clipboard(self):
        processed_text = self.output_area.get("1.0", tk.END).strip()
        if processed_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(processed_text)
            self.root.update()

# 创建主窗口
root = tk.Tk()
app = TextProcessorApp(root)
root.mainloop()
