import tkinter

import pytesseract
import pyautogui
import cv2
import threading
import re
import winsound
import os

import tkinter as tk
import pygetwindow as gw
import numpy as np

from time import sleep
from tkinter import filedialog, ttk


# URL for Tesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'


def create_button(text, command, style="elder.TButton"):
    return ttk.Button(root, text=text, style=style, command=command)


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
    def __init__(self, root):
        self.root = root
        self.flag = False
        self.thread = None
        self.status = 'idle'

        self.header = tk.Label(root, text="Base finder", font=("Arial", 20))
        self.header.grid(row=0, column=0, columnspan=2, pady=10)

        self.select_tesseract_button = create_button(text='Select Tesseract', command=select_tesseract)
        self.select_tesseract_button.grid(row=1, column=0, columnspan=2, pady=10)
        self.tesseract_label = tk.Label(
            root,
            text=f'Tesseract path: {open('tesseract_path.txt', 'r').read().strip() if os.path.exists('tesseract_path.txt') else 'not selected'}')
        self.tesseract_label.grid(row=2, column=0)

        self.gold_label = tk.Label(root, text="Target gold:")
        self.gold_label.grid(row=3, column=0)
        self.gold_entry = tk.Entry(root)
        self.gold_entry.grid(row=3, column=1)
        self.gold_entry.insert(0, "700000")

        self.elixir_label = tk.Label(root, text="Target elixir:")
        self.elixir_label.grid(row=4, column=0)
        self.elixir_entry = tk.Entry(root)
        self.elixir_entry.grid(row=4, column=1)
        self.elixir_entry.insert(0, "700000")

        self.dark_elixir_label = tk.Label(root, text="Target dark elixir:")
        self.dark_elixir_label.grid(row=5, column=0)
        self.dark_elixir_entry = tk.Entry(root)
        self.dark_elixir_entry.grid(row=5, column=1)
        self.dark_elixir_entry.insert(0, "6000")

        self.start_button = create_button(text='Start', command=self.start, style="start.TButton")
        self.start_button.grid(row=6, column=0, pady=10, padx=10)

        self.stop_button = create_button(text='Stop', command=self.stop, style="stop.TButton")
        self.stop_button.grid(row=6, column=1, pady=10, padx=10)

        self.quit_button = create_button(text='Quit', command=self.quit)
        self.quit_button.grid(row=7, column=1, pady=10, padx=10)

        if os.path.exists('tesseract_path.txt'):
            with open('tesseract_path.txt', 'r') as f:
                pytesseract.pytesseract.tesseract_cmd = f.read().strip()

    def start(self):
        if self.thread is not None and self.thread.is_alive():
            return

        self.status = 'idle'

        self.flag = True
        self.gold = int(self.gold_entry.get())
        self.elixir = int(self.elixir_entry.get())
        self.dark_elixir = int(self.dark_elixir_entry.get())

        self.thread = threading.Thread(target=self.loop)
        self.thread.start()

    def stop(self):
        self.flag = False

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
            self.status = 'base found'
            winsound.MessageBeep()
            self.stop()

    def loop(self):
        while self.flag:
            try:
                app = gw.getWindowsWithTitle('Clash of Clans')[0]

                if not app.isActive:
                    print('app not active')
                    sleep(1)
                    continue

                self.status = 'searching for base'

                (r, g, b) = pyautogui.pixel(874, 23)

                if r > 252 and 215 > g > 212 and 214 > b > 210:
                    print('base found')
                    self.check_resources()
                else:
                    print('looking for base')

                sleep(1)
            except Exception as e:
                print(f'Did you remember to start CoC? error: {e}')
                sleep(1)


root = tk.Tk()
root.minsize(250, 280)

# widget styles
style = ttk.Style()
style.theme_use('default')
style.configure(
    'start.TButton',
    font=('Arial', 12),
    padding=5,
    background="#228B22",
    foreground="#fff",
    relief='flat',
    borderwidth=0
)
style.map('start.TButton', background=[('active', '#28A428')])
style.configure(
    'stop.TButton',
    font=('Arial', 12),
    padding=5,
    background="#922D50",
    foreground="#fff",
    relief='flat',
    borderwidth=0)
style.map('stop.TButton', background=[('active', '#BB3A67')])
style.configure(
    'elder.TButton',
    font=('Arial', 12),
    padding=5,
    background='#947BD3',
    foreground="#000",
    relief='flat',
    borderwidth=0
)
style.map(
    'elder.TButton',
    background=[
        ('active', '#C1B3E6')
    ]
)

app = App(root)
root.mainloop()
