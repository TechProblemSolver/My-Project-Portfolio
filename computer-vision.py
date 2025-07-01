import torch
import cv2
import os
import time

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

cap = cv2.VideoCapture(0)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 14, (640, 480))

frame_count = 0
frame_files = []

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    results.render()

    out.write(frame)

    frame_filename = f'videoframes/frame_{frame_count}.jpg'
    cv2.imwrite(frame_filename, frame)
    frame_files.append(frame_filename)
    frame_count += 1

    # os.startfile(frame_filename)

    time.sleep(0.05)

    if os.path.exists('quit.txt'):
        break

cap.release()
out.release()

for frame_file in frame_files:
    if os.path.exists(frame_file):
        os.remove(frame_file)