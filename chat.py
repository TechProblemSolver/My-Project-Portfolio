import tkinter as tk
from tkinter import ttk, simpledialog, filedialog
from PIL import Image, ImageTk
import cv2
import socket
import threading
import os

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("800x600")
        self.root.title("✨ SparkChat: Chat Room")
        self.chat_area = tk.Text(self.root, state=tk.DISABLED, width=50, height=20)
        self.chat_area.pack(padx=10, pady=10)
        self.chat_area.tag_configure("tag-right", justify='right')
        self.chat_area.image = []  # Initialize the image list here
        self.entry = tk.Entry(self.root, width=40)
        self.entry.pack(side=tk.LEFT, padx=10, pady=10)

        send_button = tk.Button(self.root, text="Send", command=self.send_message)
        send_button.pack(side=tk.LEFT, padx=10, pady=10)
        send_button.config(bg="green", fg="white")

        image_button = tk.Button(self.root, text="Send Image", command=self.send_image)
        image_button.pack(side=tk.LEFT, padx=10, pady=10)
        image_button.config(bg="blue", fg="white")

        video_button = tk.Button(self.root, text="Send Video", command=self.send_video)
        video_button.pack(side=tk.LEFT, padx=10, pady=10)
        video_button.config(bg="red", fg="white")

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

    def send_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'rb') as file:
                image_data = file.read()
                image_name = os.path.basename(file_path)
                self.client_socket.send(f"{self.username}:IMAGE:{image_name}".encode('utf-8'))
                self.client_socket.sendall(image_data)
                self.update_chat_area(f"{self.username} sent an image: {image_name}")
                self.display_image(file_path)

    def send_video(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'rb') as file:
                video_data = file.read()
                video_name = os.path.basename(file_path)
                self.client_socket.send(f"{self.username}:VIDEO:{video_name}".encode('utf-8'))
                self.client_socket.sendall(video_data)
                self.update_chat_area(f"{self.username} sent a video: {video_name}")
                self.display_video(file_path)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if "IMAGE:" in message:
                    username, _, image_name = message.partition(":IMAGE:")
                    image_data = b""
                    while True:
                        chunk = self.client_socket.recv(1024)
                        if not chunk:
                            break
                        image_data += chunk
                    with open(image_name, 'wb') as file:
                        file.write(image_data)
                    self.update_chat_area(f"{username} sent an image: {image_name}")
                    self.display_image(image_name)
                elif "VIDEO:" in message:
                    username, _, video_name = message.partition(":VIDEO:")
                    video_data = b""
                    while True:
                        chunk = self.client_socket.recv(1024)
                        if not chunk:
                            break
                        video_data += chunk
                    with open(video_name, 'wb') as file:
                        file.write(video_data)
                    self.update_chat_area(f"{username} sent a video: {video_name}")
                    self.display_video(video_name)
                else:
                    self.update_chat_area(message)
            except Exception as e:
                print(f"Error: {e}")
                break

    def update_chat_area(self, message):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, message + '\n')
        self.chat_area.config(state=tk.DISABLED)

    def display_image(self, image_path):
        img = Image.open(image_path)
        img.thumbnail((100, 100))
        img = ImageTk.PhotoImage(img)
        self.chat_area.image_create(tk.END, image=img)
        self.chat_area.insert(tk.END, '\n')
        self.chat_area.image.append(img)  # Keep a reference to avoid garbage collection

    def display_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error: Could not open video.")
            return

        def play_video():
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imshow(video_path, frame)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()

        threading.Thread(target=play_video).start()

if __name__ == "__main__":
    App()
