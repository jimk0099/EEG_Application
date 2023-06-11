import numpy as np
import tkinter as tk
import time


# game globals
DELAY = 0
HEAD = None
STICK = None
STICK_ARM_LEFT = None
STICK_ARM_RIGHT = None
STICK_LEG_LEFT = None
STICK_LEG_RIGHT = None
ROOT = None
CANVAS = None

TIMESTAMPS = None

def show_stick_figure():
    global HEAD, STICK, STICK_ARM_LEFT, STICK_ARM_RIGHT, STICK_LEG_LEFT, STICK_LEG_RIGHT
    global CANVAS
    # if stick figure is already shown, delete it
    if HEAD is not None:
        CANVAS.delete(HEAD)
        CANVAS.delete(STICK)
        CANVAS.delete(STICK_ARM_LEFT)
        CANVAS.delete(STICK_ARM_RIGHT)
        CANVAS.delete(STICK_LEG_LEFT)
        CANVAS.delete(STICK_LEG_RIGHT)
    HEAD            = CANVAS.create_oval(425, 200, 375, 150, width=5)
    STICK           = CANVAS.create_line(400, 300, 400, 200, width=5)
    STICK_ARM_LEFT  = CANVAS.create_line(400, 200, 350, 250, width=5)
    STICK_ARM_RIGHT = CANVAS.create_line(400, 200, 450, 250, width=5)
    STICK_LEG_LEFT  = CANVAS.create_line(400, 300, 350, 375, width=5)
    STICK_LEG_RIGHT = CANVAS.create_line(400, 300, 450, 375, width=5)
    
def show_stick_figure_raise_left_arm():
    global STICK_ARM_LEFT, DELAY, CANVAS
    CANVAS.delete(STICK_ARM_LEFT)
    STICK_ARM_LEFT = CANVAS.create_line(400, 200, 350, 150, width=5)

def show_new_text(texts_list, index=0):
    global CANVAS
    if index < len(texts_list):
        new_text = texts_list[index]
        width = len(new_text) * 10
        text_item = CANVAS.create_text(400, 50, text=new_text,
                                        font=("Arial", 24), fill="black",
                                        width=width, justify="center")
        CANVAS.after(3000, 
                     lambda: CANVAS.delete(text_item))
        CANVAS.after(4000, 
                     lambda: show_new_text(texts_list, index + 1))

def tutorial():
    """
    This function will show the tutorial of the game.
    """
    global CANVAS, DELAY
    print("FIRST")
    # Initial text
    texts = [
        "Welcome to the Motor Imagery Game!",
        "In this game, you will be asked to perform a motor imagery task.",
        "The task is to imagine that you are moving your left or right hand.",
        "You will be given a visual cue to perform the task.",
        "Depending on your performance, you will be given a feedback.",
        "Here is a little preview of the game.",
        "You don't have to do anything, just watch the screen.",
    ]
    
    # Start displaying the texts
    show_new_text(texts)
    # wait for the show_new_text function
    # to finish with the texts
    CANVAS.after(len(texts) * 4000, 
                 lambda: show_stick_figure())
    # show a prompt, like a yellow sun on the left of the user
    CANVAS.after(len(texts) * 4000 + 2000,
                 lambda: CANVAS.create_oval(100, 100, 200, 200, fill="yellow", tags="sun"))
    DELAY = len(texts) * 4000 + 2000
    # show some text that explains the prompt
    texts = [
        "The sun on your left means that you have to raise your left arm.", 
        "If you manage to imagine it correctly, the sun will turn green,", 
        "the stick figure will raise its left arm and you will get a point."
    ]
    CANVAS.after(DELAY, lambda: show_new_text(texts))
    # wait for the show_new_text function
    # to finish with the texts, then show the stick figure
    # with the left arm raised and the sun green

    CANVAS.after(DELAY + len(texts) * 4000,
                 lambda: show_stick_figure_raise_left_arm())
    CANVAS.after(DELAY + len(texts) * 4000,
                 lambda: CANVAS.delete("sun"))
    CANVAS.after(DELAY + len(texts) * 4000, 
                 lambda: CANVAS.create_oval(100, 100, 200, 200, fill="green", tags="sun"))
    # also show a point gained
    CANVAS.after(DELAY + len(texts) * 4000,
                 lambda: CANVAS.create_text(100, 300, text="1",font=("Arial", 24), 
                                            fill="black", tags="score"))

    # works perfect up to this point
    DELAY += len(texts) * 4000
    # show what happens if the user fails to perform the task
    # reset the stick figure
    CANVAS.after(DELAY + 1000, 
                 lambda: show_stick_figure())
    # also delete previous counter
    # and set to 0
    CANVAS.after(DELAY + 1000,
                 lambda: CANVAS.delete("sun"))
    CANVAS.after(DELAY + 1000,
                 lambda: CANVAS.create_oval(100, 100, 200, 200, fill="yellow", tags="sun"))
    CANVAS.after(DELAY + 1000, 
                 lambda: CANVAS.delete("score"))
    CANVAS.after(DELAY + 1000, 
                 lambda: CANVAS.create_text(100, 300, text="0", font=("Arial", 24),
                                            fill="black", tags="score"))

    texts2 = [
        "If you fail to imagine the task correctly, the sun will turn red,",
        "the stick figure will not raise its left arm and you will not get a point."
    ]
    DELAY += 1000
    CANVAS.after(DELAY + 1000,
                 lambda: show_new_text(texts2))
    DELAY += 1000
    CANVAS.after(DELAY + len(texts2) * 4000,
                 lambda: CANVAS.delete("sun"))
    CANVAS.after(DELAY + len(texts2) * 4000, 
                 lambda: CANVAS.create_oval(100, 100, 200, 200, fill="red", tags="sun"))
    DELAY += len(texts2) * 4000
    texts3 = [
        "Accordingly, the sun on your right means that you have to raise your right arm."
    ]
    # show the prompt for the right arm accordingly
    CANVAS.after(DELAY + 1000,
                    lambda: CANVAS.delete("sun"))
    CANVAS.after(DELAY + 1000,
                    lambda: CANVAS.create_oval(600, 100, 700, 200, fill="yellow", tags="sun"))
    CANVAS.after(DELAY + 1000, lambda: show_new_text(texts3))
    DELAY += 1000
    # declare that the tutorial is over
    texts4 = [
        "That's it for the tutorial.",
        "You can now start the game."
    ]
    CANVAS.after(DELAY + len(texts3) * 4000, lambda: show_new_text(texts4))
    # clear everything
    DELAY += len(texts3) * 4000
    CANVAS.after(DELAY + len(texts4) * 4000, lambda: CANVAS.delete("all"))
    DELAY += 1000 + len(texts4) * 4000

def positive_feedback():
    """
    This function will show a positive feedback
    to the user.
    """
    global CANVAS
    CANVAS.after(0, lambda: CANVAS.create_oval(100, 100, 200, 200, fill="green"))
    CANVAS.after(0, lambda: show_stick_figure_raise_left_arm())

def negative_feedback():
    """
    This function will show a negative feedback
    to the user.
    """
    global CANVAS
    CANVAS.after(0, lambda: CANVAS.create_oval(100, 100, 200, 200, fill="red"))

def reset_feedback():
    """
    This function will reset the feedback
    to the user.
    """
    global CANVAS
    CANVAS.after(0, lambda: CANVAS.create_oval(100, 100, 200, 200, fill="yellow"))

def begin_prompting():
    """
    This function will begin the prompting process.
    The user will be prompted to perform the motor imagery
    task and the game will process the EEG data to determine
    whether the user is performing the task or not.
    """
    # TODO: This function is not yet finished. It needs work.
    global TIMESTAMPS, DELAY, CANVAS
    print("begin prompting", DELAY)
    TIMESTAMPS = np.random.randint(DELAY, DELAY + 100000, size=10)
    TIMESTAMPS.sort()
    RESPONSES = np.random.randint(0, 1, size=10)
    local_delay = 0
    CANVAS.after(local_delay,
                 lambda: CANVAS.create_text(400, 50, text="Let's play!",
                                            font=("Arial", 24), fill="black"))
    CANVAS.after(local_delay + 4000,
                 lambda: CANVAS.delete("all"))
    CANVAS.after(local_delay + 6000, 
                 lambda: CANVAS.create_oval(100, 100, 200, 200, fill="yellow"))
    CANVAS.after(local_delay + 6000,
                 lambda: show_stick_figure())
    local_delay += 6000
    for index, timestamp in enumerate(TIMESTAMPS):
        # wait for the elapsed time
        CANVAS.after(local_delay + timestamp,
                     lambda: CANVAS.create_oval(100, 100, 200, 200, fill="yellow"))
        local_delay += timestamp

        if RESPONSES[index] == 0:
            # execute the actual prompting function
            CANVAS.after(local_delay,
                         lambda: negative_feedback())
            local_delay += 2000
        else:
            CANVAS.after(local_delay,
                         lambda: positive_feedback())
            local_delay += 2000
        CANVAS.after(local_delay,
                        lambda: reset_feedback())
        

def game():
    """
    This function will start the game.
    """

    global ROOT, CANVAS, DELAY
    ROOT = tk.Tk()
    ROOT.title("Motor Imagery Game")
    ROOT.geometry("1200x600")
    CANVAS = tk.Canvas(ROOT, width=800, height=600)
    CANVAS.pack()
    print(f"entering tutorial {DELAY}")
    tutorial()
    print(f"entering prompting {DELAY}")
    CANVAS.after(DELAY, lambda: begin_prompting())

    ROOT.mainloop()
