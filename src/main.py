import customtkinter as ctk
import pytesseract
import pyautogui
import cv2
import threading
import re
import winsound
import os

import pygetwindow as gw
import numpy as np

from time import sleep
from tkinter import filedialog
from customtkinter import StringVar


def select_tesseract():
    filename = filedialog.askopenfilename()
    print('selected file:', filename)
    with open('tesseract_path.txt', 'w') as f:
        f.write(filename)


def extract_number(text):
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(''.join(numbers))
    else:
        return None


class App:
    def __init__(self, root, frame):
        self.root = root
        self.frame = frame
        self.flag = False
        self.thread = None
        self.status = StringVar()
        self.status.set('idle')

        self.header = ctk.CTkLabel(master=frame, text="Base finder", font=("Roboto", 24))
        self.header.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        self.select_tesseract_button = ctk.CTkButton(master=frame, text='Select Tesseract', command=select_tesseract, font=("Roboto", 16))
        self.select_tesseract_button.grid(row=1, column=0, columnspan=1, pady=10, padx=10, sticky="nsew")
        self.tesseract_label = ctk.CTkLabel(
            master=frame,
            text=f'Tesseract path: {open("tesseract_path.txt", "r").read().strip() if os.path.exists("tesseract_path.txt") else "not selected"}',
            font=("Roboto", 16)
        )
        self.tesseract_label.grid(row=1, column=1, columnspan=1, pady=10, padx=10, sticky="nsew")

        self.gold_label = ctk.CTkLabel(master=frame, text="Target gold:", font=("Roboto", 16))
        self.gold_label.grid(row=2, column=0, columnspan=1, pady=10, padx=10, sticky="nsew")
        self.gold_entry = ctk.CTkEntry(master=frame, font=("Roboto", 16))
        self.gold_entry.grid(row=2, column=1, columnspan=1, pady=10, padx=10, sticky="nsew")
        self.gold_entry.insert(0, "700000")

        self.elixir_label = ctk.CTkLabel(master=frame, text="Target elixir:", font=("Roboto", 16))
        self.elixir_label.grid(row=3, column=0, columnspan=1, pady=10, padx=10, sticky="nsew")
        self.elixir_entry = ctk.CTkEntry(master=frame, font=("Roboto", 16))
        self.elixir_entry.grid(row=3, column=1, columnspan=1, pady=10, padx=10, sticky="nsew")
        self.elixir_entry.insert(0, "700000")

        self.dark_elixir_label = ctk.CTkLabel(master=frame, text="Target dark elixir:", font=("Roboto", 16))
        self.dark_elixir_label.grid(row=4, column=0, columnspan=1, pady=10, padx=10, sticky="nsew")
        self.dark_elixir_entry = ctk.CTkEntry(master=frame, font=("Roboto", 16))
        self.dark_elixir_entry.grid(row=4, column=1, columnspan=1, pady=10, padx=10, sticky="nsew")
        self.dark_elixir_entry.insert(0, "6000")

        self.wrapper1 = ctk.CTkFrame(master=frame)
        self.wrapper1.grid(row=5, column=0, columnspan=2, sticky="ew")

        self.start_button = ctk.CTkButton(
            master=self.wrapper1,
            text='Start',
            command=self.start,
            font=("Roboto", 16),
            fg_color="green",
            hover_color="lightgreen"
        )
        self.start_button.pack(side="left", pady=10, padx=10, fill="x", expand=True)

        self.stop_button = ctk.CTkButton(
            master=self.wrapper1,
            text='Stop',
            command=self.stop,
            font=("Roboto", 16),
            fg_color="red",
            hover_color="lightcoral"
        )
        self.stop_button.pack(side="right", pady=10, padx=10, fill="x", expand=True)

        self.status_label = ctk.CTkLabel(master=frame, textvariable=self.status, font=("Roboto", 16))
        self.status_label.grid(row=6, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        self.quit_button = ctk.CTkButton(master=frame, text='Quit', command=self.quit, font=("Roboto", 16))
        self.quit_button.grid(row=7, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        if os.path.exists('tesseract_path.txt'):
            with open('tesseract_path.txt', 'r') as f:
                pytesseract.pytesseract.tesseract_cmd = f.read().strip()

    def start(self):
        if self.thread is not None and self.thread.is_alive():
            return

        self.status.set('idle')

        self.flag = True
        self.gold = int(self.gold_entry.get())
        self.elixir = int(self.elixir_entry.get())
        self.dark_elixir = int(self.dark_elixir_entry.get())

        self.thread = threading.Thread(target=self.loop)
        self.thread.start()

    def stop(self, status='idle'):
        self.flag = False
        self.status.set(status)

    def quit(self):
        self.flag = False
        if self.thread is not None:
            self.thread.join()
        self.root.destroy()

    def go_next(self):
        pyautogui.click(1750, 800)

    def check_resources(self):
        gold_screenshot = pyautogui.screenshot(region=(80, 125, 140, 35))
        elixir_screenshot = pyautogui.screenshot(region=(80, 170, 140, 35))
        dark_elixir_screenshot = pyautogui.screenshot(region=(80, 215, 140, 35))

        gold_grayscale = cv2.cvtColor(np.array(gold_screenshot), cv2.COLOR_BGR2GRAY)
        elixir_grayscale = cv2.cvtColor(np.array(elixir_screenshot), cv2.COLOR_BGR2GRAY)
        dark_elixir_grayscale = cv2.cvtColor(np.array(dark_elixir_screenshot), cv2.COLOR_BGR2GRAY)

        gold_text = pytesseract.image_to_string(
            gold_grayscale,
            config='--psm 6 -c tessedit_char_whitelist=0123456789'
        )
        elixir_text = pytesseract.image_to_string(
            elixir_grayscale,
            config='--psm 6 -c tessedit_char_whitelist=0123456789'
        )
        dark_elixir_text = pytesseract.image_to_string(
            dark_elixir_grayscale,
            config='--psm 6 -c tessedit_char_whitelist=0123456789'
        )

        if (int(extract_number(gold_text) if gold_text != '' else 0) < self.gold
                or int(extract_number(elixir_text) if elixir_text != '' else 0) < self.elixir
                or int(extract_number(dark_elixir_text) if dark_elixir_text != '' else 0) < self.dark_elixir):
            print('not enough resources')
            self.go_next()
        else:
            print('enough resources')
            self.stop('base found')
            winsound.MessageBeep()

    def loop(self):
        while self.flag:
            try:
                app = gw.getWindowsWithTitle('Clash of Clans')[0]

                if not app.isActive:
                    print('app not active')
                    sleep(1)
                    continue

                self.status.set('searching for base')

                (r, g, b) = pyautogui.pixel(874, 23)

                if r > 252 and 215 > g > 212 and 214 > b > 210:
                    print('base found')
                    self.check_resources()
                else:
                    print('looking for base')

                sleep(0.5)
            except Exception as e:
                print(f'Did you remember to start CoC? error: {e}')
                sleep(1)


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("Base finder")

frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

app = App(root, frame)
root.mainloop()
