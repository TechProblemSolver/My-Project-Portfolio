import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import socket
import threading
import time
import random as rnd
import os

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("800x600")
        self.root.title("✨ SparkChat: Chat Room")
        
        self.root.configure(bg="#2c3e50")

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Clear Chat", command=self.clear_chat)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        self.chat_frame = tk.Frame(self.root, bg="#2c3e50")
        self.chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area = tk.Text(self.chat_frame, state=tk.DISABLED, width=50, height=20, bg="#ecf0f1", fg="#2c3e50", font=("Helvetica", 12))
        self.chat_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.chat_area.tag_configure("tag-left", justify='left')
        self.chat_area.tag_configure("tag-right", justify='right')

        scrollbar = ttk.Scrollbar(self.chat_frame, command=self.chat_area.yview)
        self.chat_area.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.entry_frame = tk.Frame(self.root, bg="#2c3e50")
        self.entry_frame.pack(padx=10, pady=10, fill=tk.X)
        self.entry = tk.Entry(self.entry_frame, width=40, bg="#ecf0f1", fg="#2c3e50", font=("Helvetica", 12))
        self.entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        send_button = tk.Button(self.entry_frame, text="Send", command=self.send_message, bg="#27ae60", fg="white", font=("Helvetica", 12, "bold"))
        send_button.pack(side=tk.LEFT, padx=10, pady=10)

        emoji_frame = tk.Frame(self.root, bg="#2c3e50")
        emoji_frame.pack(padx=10, pady=10)
        emojis = ["😀", "😂", "😍", "😎", "😭", "👍", "🙏"]
        for emoji in emojis:
            button = tk.Button(emoji_frame, text=emoji, command=lambda e=emoji: self.send_emoji(e), bg="#ecf0f1", fg="#2c3e50", font=("Helvetica", 12))
            button.pack(side=tk.LEFT, padx=5)

        self.status = tk.Label(self.root, text="Connected", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#2c3e50", fg="white")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('141.219.241.72', 5555))

        self.username = self.prompt_username()

        thread = threading.Thread(target=self.receive_messages)
        thread.start()

        self.root.mainloop()

    def prompt_username(self):
        username = simpledialog.askstring("Username", "Enter your username:")
        return username if username else f"user_{rnd.randint(1, 9999)}"

    def send_message(self):
        message = self.entry.get()
        if message:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            full_message = f"{self.username} [{timestamp}]: {message}"
            self.client_socket.send(full_message.encode('utf-8'))
            self.update_chat_area(full_message, "tag-left")
            self.entry.delete(0, tk.END)

    def send_emoji(self, emoji):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        full_message = f"{self.username} [{timestamp}]: {emoji}"
        self.client_socket.send(full_message.encode('utf-8'))
        self.update_chat_area(full_message, "tag-left")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message.startswith(f"{self.username}"):
                    self.update_chat_area(message, "tag-left")
                else:
                    self.update_chat_area(message, "tag-right")
                    self.play_notification_sound()
            except Exception as e:
                print(f"Error: {e}")
                break

    def update_chat_area(self, message, tag):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, message + '\n', tag)
        self.chat_area.config(state=tk.DISABLED)

    def clear_chat(self):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def play_notification_sound(self):
        try:
            import winsound
            winsound.PlaySound('notification.wav', winsound.SND_FILENAME)
        except ImportError:
            print("")

if __name__ == "__main__":
    App()
