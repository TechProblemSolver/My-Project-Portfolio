import tkinter as tk
from tkinter import ttk, simpledialog
import socket
import threading

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("800x600")
        self.root.title("✨ SparkChat: Chat Room")
        self.chat_area = tk.Text(self.root, state=tk.DISABLED, width=50, height=20)
        self.chat_area.pack(padx=10, pady=10)
        self.chat_area.tag_configure("tag-right", justify='right')
        self.entry = tk.Entry(self.root, width=40)
        self.entry.pack(side=tk.LEFT, padx=10, pady=10)

        send_button = tk.Button(self.root, text="Send", command=self.send_message)
        send_button.pack(side=tk.LEFT, padx=10, pady=10)
        send_button.config(bg="green", fg="white")

        emoji_frame = tk.Frame(self.root)
        emoji_frame.pack(side=tk.LEFT, padx=10, pady=10)

        emojis = ["😀", "😂", "😍", "😎", "😭", "👍", "🙏"]
        for emoji in emojis:
            button = tk.Button(emoji_frame, text=emoji, command=lambda e=emoji: self.send_emoji(e))
            button.pack(side=tk.LEFT)

        scrollbar = ttk.Scrollbar(self.root, command=self.chat_area.yview)
        self.chat_area.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('141.219.241.72', 5555))  # Replace with your server's public IP address

        self.username = self.prompt_username()

        thread = threading.Thread(target=self.receive_messages)
        thread.start()

        self.root.mainloop()

    def prompt_username(self):
        username = simpledialog.askstring("Username", "Enter your username:")
        return username if username else "Anonymous"

    def send_message(self):
        message = self.entry.get()
        if message:
            full_message = f"{self.username}: {message}"
            self.client_socket.send(full_message.encode('utf-8'))
            self.update_chat_area(f"{self.username}: {message}")
            self.entry.delete(0, tk.END)

    def send_emoji(self, emoji):
        full_message = f"{self.username}: {emoji}"
        self.client_socket.send(full_message.encode('utf-8'))
        self.update_chat_area(f"{self.username}: {emoji}")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                self.update_chat_area(message)
            except Exception as e:
                print(f"Error: {e}")
                break

    def update_chat_area(self, message):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, message + '\n')
        self.chat_area.config(state=tk.DISABLED)

if __name__ == "__main__":
    App()
