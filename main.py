import os
import sys
import tkinter as tk
from tkinter import messagebox

# Import các module tự tạo
from gui.app import EnvSetupApp

if __name__ == "__main__":
    # Kiểm tra phiên bản Python
    if sys.version_info < (3, 6):
        messagebox.showerror("Lỗi", "Ứng dụng yêu cầu Python 3.6 trở lên")
        sys.exit(1)

    # Khởi tạo ứng dụng
    root = tk.Tk()
    app = EnvSetupApp(root)
    root.mainloop()
