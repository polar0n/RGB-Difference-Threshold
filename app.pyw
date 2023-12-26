import csv
from tkinter import *
from tkinter import ttk, messagebox
from ctypes import windll
from time import sleep
from random import choice
from math import fsum
from collections import deque
from functools import partial
from turtle import color
from numpy import array
import constants as c
from utils.rgb2hex import rgb2hex as hex_color
from utils.csv_writer import Data2CSV


windll.shcore.SetProcessDpiAwareness(1)

csv_writer = Data2CSV(c.CSV_FILE, c.CSV_HEADINGS)

color_wheel = deque([1, 0, 0])
rotations = 0

current_color = c.BASE_COLOR - c.STARTING_DIFFERENCE[rotations]
current_difference = c.STARTING_DIFFERENCE[rotations]
mistakes = []
mean_values = []

loaded = False
sex = None
age = None
vision = None
vision_problem = None


def save_data():
    csv_writer.append_row([
        int(sex.get()),
        int(age.get()),
        int(vision.get()), 
        vision_problem.get(),
        *mean_values
    ])


def rotate_color_wheel():
    global current_color, mistakes, current_difference, mean_values, rotations
    mean_values.append(fsum(mistakes)/len(mistakes))
    mistakes = []
    color_wheel.rotate(1)
    rotations += 1
    current_color = c.BASE_COLOR - c.STARTING_DIFFERENCE[rotations]
    current_difference = c.STARTING_DIFFERENCE[rotations]


def participant_response(response):
    global current_color, mistakes, current_difference, mean_values, rotations
    correct = c.SAME if c.BASE_COLOR == current_color else c.DIFFERENT 
    if correct == response:
        current_difference -= 1
        if current_difference == -1:
            mistakes.append(current_color)
            rotate_color_wheel()
        else:
            current_color = c.BASE_COLOR - current_difference
    else:
        mistakes.append(current_color)
        if len(mistakes) == c.CHANCES:
            rotate_color_wheel()
        else:
            current_difference += 1
            current_color = c.BASE_COLOR - current_difference
    print(current_difference)
    if rotations == 6:
        save_data()
        finish()
    else:
        measurement()


root = Tk()
root.title('Color Just Noticeable Difference')
root.geometry(f'{c.WIDTH}x{c.HEIGHT}+{int(root.winfo_screenwidth()/2-c.WIDTH/2)}+{int(root.winfo_screenheight()/2-c.HEIGHT/2)}')
root.resizable(False, False)

base_frame = Frame(root)
base_frame.place(relwidth=1, relheight=0.8)

color_pane1 = Frame(base_frame, bg=c.BLACK)
color_pane1.place(x=1, y=1, relheight=1, width=250)
# color_pane1.place(relheight=1, relwidth=0.5)

color_pane2 = Frame(base_frame, bg=c.BLACK)
color_pane2.place(x=252, y=1, relheight=1, width=250)
# color_pane2.place(relx=0.5, relheight=1, relwidth=0.5)

color_panes = (color_pane1, color_pane2)

button_frame = Frame(root)
button_frame.place(rely=0.8, relwidth=1, relheight=0.2)

same_button = ttk.Button(
    button_frame,
    text='Same',
    state=DISABLED,
    command=partial(participant_response, c.SAME)
)
same_button.place(anchor='center', relx=0.25, rely=0.5, relheight=0.75, relwidth=0.4)

different_button = ttk.Button(
    button_frame,
    text='Different',
    state=DISABLED,
    command=partial(participant_response, c.DIFFERENT)
)
different_button.place(anchor='center', relx=0.75, rely=0.5, relheight=0.75, relwidth=0.4)


def lock(lock):
    state = DISABLED if lock else NORMAL
    global same_button, different_button
    same_button.configure(state=state)
    different_button.configure(state=state)
    if lock:
        global color_pane1, color_pane2
        color_pane1['bg'] = c.BLACK
        color_pane2['bg'] = c.BLACK
    else:
        base_color_pane = choice(color_panes)
        test_color_pane = color_panes[color_panes.index(base_color_pane)-1]

        base_color_pane['bg'] = hex_color(*(array(color_wheel) * c.BASE_COLOR))
        test_color_pane['bg'] = hex_color(*(array(color_wheel) * current_color))


def measurement():
    lock(True)
    root.after(700, partial(lock, False))


def finish():
    messagebox.showinfo(
        title='Done',
        message='The data collection is done and the app will close.'
    )
    root.quit()


def create_q_window():
    q_window = Toplevel(root)
    q_window.title('Questionnaire')
    q_window.geometry(f'{350}x{400}+{int(root.winfo_screenwidth()/2-350/2)}+{int(root.winfo_screenheight()/2-400/2)}')
    q_window.wait_visibility()
    q_window.grab_set()

    global sex
    sex = IntVar(q_window)

    H = 1/13

    label_sex = Label(q_window, text='What is your sex?', anchor=W)
    label_sex.place(relx=0.03, relheight=H, relwidth=1)

    i = 0
    for (text, value) in c.SEX_VALUES.items():
        button = ttk.Radiobutton(q_window, text=text, variable=sex, value=value)
        button.place(rely=H+H*i, relx=0.05)
        i += 1

    label_age = ttk.Label(q_window, text='What is your age:', anchor=W)
    label_age.place(rely=3*H, relx=0.03, relheight=H, relwidth=1)

    global age
    age = IntVar(q_window, 18)
    spinbox_age = ttk.Spinbox(q_window, from_=14, to=65, textvariable=age, wrap=True)
    spinbox_age.place(rely=4*H, relx=0.05)

    label_color_blindness = ttk.Label(q_window, text='Do you have color blindness?', anchor=W)
    label_color_blindness.place(rely=5*H, relx=0.03, relheight=H, relwidth=1)

    chosen_color_problems = IntVar(q_window)

    i = 0
    for (text, value) in c.COLOR_BLINDNESS.items():
        button = ttk.Radiobutton(q_window, text=text, variable=chosen_color_problems, value=value)
        button.place(rely=6*H+H*i, relx=0.05)
        i += 1


    label_vision = ttk.Label(q_window, text='Do you have any vision problems?', anchor=W)
    label_vision.place(rely=8*H, relx=0.03, relheight=H, relwidth=1)

    global vision
    vision = IntVar(q_window)


    def specify_vision_problem():
        entry['state'] = ACTIVE if bool(int(vision.get())) else DISABLED


    i = 0
    for (text, value) in c.VISION_PROBLEMS.items():
        button = ttk.Radiobutton(q_window, text=text, variable=vision, value=value, command=specify_vision_problem)
        button.place(rely=9*H+H*i, relx=0.05)
        i += 1

    global vision_problem
    vision_problem = StringVar(q_window, '')
    entry = ttk.Entry(q_window, textvariable=vision_problem, state=DISABLED)
    entry.place(rely=11*H, relx=0.1, relwidth=0.8)


    def proceed():
        q_window.destroy()
        if chosen_color_problems.get() == 1:
            messagebox.showinfo(
                title='Colorblindness',
                message='Because of colorblindness you are not eligible to take this test.'
            )
            root.quit()
        else:
            create_info_window()


    continue_button = ttk.Button(q_window, text='Continue', command=proceed)
    continue_button.place(rely=13*H-0.008, relx=0.5, anchor=S)


    def on_closing():
        user_exit = messagebox.askyesno(
            title='Exit',
            message='Are you sure you want to exit?'
        )
        if user_exit:
            root.quit()


    q_window.protocol("WM_DELETE_WINDOW", on_closing)


def create_info_window():
    info_window = Toplevel(root)
    info_window.title('Info')
    info_window.geometry(f'{c.WIDTH}x{c.HEIGHT}+{int(root.winfo_screenwidth()/2-c.WIDTH/2)}+{int(root.winfo_screenheight()/2-c.HEIGHT/2)}')
    info_window.wait_visibility()
    info_window.grab_set()
    label_info = Text(info_window, font=('Consolas', 12), height=10, wrap=WORD)
    label_info.insert(1.0, c.INFO_TEXT)
    label_info['state'] = DISABLED
    label_info.place(relheight=0.9, relwidth=1)


    def proceed():
        info_window.destroy()
        measurement()

    continue_button = ttk.Button(info_window, text='Proceed to testing', command=proceed)
    continue_button.place(relx=0.5, rely=0.95, anchor=CENTER)


def after_load_cb(_):
    global loaded
    if loaded:
        return
    loaded = True
    # After load commands go here
    create_q_window()    


root.bind('<Visibility>', after_load_cb)

root.mainloop()