import time
import threading

import numpy as np
import tkinter as tk

from processing_utils import initialize, cleanup_threads, finish, get_prediction

# game globals
DELAY = 0
HEAD = None
STICK = None
STICK_ARM_LEFT = None
STICK_ARM_RIGHT = None
STICK_LEG_LEFT = None
STICK_LEG_RIGHT = None
SCORE = 0
ROOT = None
CANVAS = None
TIMESTAMPS = None
# end game globals

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
    global CANVAS, SCORE
    # make the existing sun green
    CANVAS.after(0, lambda: CANVAS.itemconfig("sun", fill="green"))
    # raise the left arm
    CANVAS.after(0, lambda: show_stick_figure_raise_left_arm())
    # show a point gained
    SCORE += 1
    CANVAS.after(0, lambda: CANVAS.delete("score"))
    CANVAS.after(0, lambda: CANVAS.create_text(100, 300, text=str(SCORE),font=("Arial", 24),
                                            fill="black", tags="score"))

def negative_feedback():
    """
    This function will show a negative feedback
    to the user.
    """
    global CANVAS
    # make the existing sun red
    CANVAS.after(0, lambda: CANVAS.itemconfig("sun", fill="red"))


def reset_feedback():
    """
    This function will reset the feedback
    to the user.
    """
    global CANVAS
    CANVAS.after(0, lambda: CANVAS.delete("sun"))
    CANVAS.after(0, lambda: show_stick_figure())

def prompt_left():
    """
    This function will prompt the user to raise
    their left arm.
    """
    global CANVAS
    CANVAS.after(0, lambda: CANVAS.create_oval(100, 100, 200, 200, fill="yellow", tags="sun"))

def prompt_right():
    """
    This function will prompt the user to raise
    their right arm.
    """
    global CANVAS
    CANVAS.after(0, lambda: CANVAS.create_oval(600, 100, 700, 200, fill="yellow", tags="sun"))

def game_body():
    """
    This function will begin the prompting process.
    The user will be prompted to perform the motor imagery
    task and the game will process the EEG data to determine
    whether the user is performing the task or not.
    """
    # TODO: This function is not yet finished. It needs checking.

    global TIMESTAMPS, DELAY, CANVAS, SCORE
    LEFT = 0
    RIGHT = 1
    NEITHER = 2

    amount = 10
    TIMESTAMPS = np.random.randint(0, 0 + 100000, size=amount)
    TIMESTAMPS.sort()
    PROMPTS = np.random.randint(LEFT, RIGHT, size=10) # 0 for left, 1 for right

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
    CANVAS.after(local_delay + 6000,
                 lambda: CANVAS.create_text(100, 300, text=str(SCORE), font=("Arial", 24),
                                            fill="black", tags="score"))
    
    
    local_delay += 6000
    for index, timestamp in enumerate(TIMESTAMPS):
        
        # wait for the elapsed time
        # and then prompt the user
        if PROMPTS[index] == LEFT:
            CANVAS.after(local_delay + timestamp + 2000,
                         lambda: prompt_left())
        else:
            CANVAS.after(local_delay + timestamp + 2000,
                         lambda: prompt_right())
        
        local_delay += timestamp
        prediction, lag = get_prediction(timestamp)
        local_delay += lag

        if not prediction == NEITHER:
            # show the feedback
            if prediction == PROMPTS[index]:
                CANVAS.after(local_delay, lambda: positive_feedback())
            else:
                CANVAS.after(local_delay, lambda: negative_feedback())
        
        local_delay += 2000
        CANVAS.after(local_delay, lambda: reset_feedback())
    
    # end the game
    CANVAS.after(local_delay, lambda: CANVAS.delete("all"))
    CANVAS.after(local_delay, lambda: CANVAS.create_text(400, 50, text="Thanks for playing!",
                                            font=("Arial", 24), fill="black"))
    CANVAS.after(local_delay + 4000, lambda: CANVAS.delete("all"))
        
    CANVAS.after(local_delay + 6000, 
                 lambda: CANVAS.create_text(400, 50,
                                            text="Your score is: " + str(SCORE) + " out of " + str(amount),
                                            font=("Arial", 24), fill="black"))
    CANVAS.after(local_delay + 10000, lambda: CANVAS.delete("all"))
    CANVAS.after(local_delay + 12000, lambda: CANVAS.create_text(400, 50,
                                            text="Goodbye!",
                                            font=("Arial", 24), fill="black"))
    CANVAS.after(local_delay + 16000, lambda: CANVAS.delete("all"))
    DELAY += local_delay + 16000





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
    
    # TODO: this may be better
    # tutorial_thread = threading.Thread(target=tutorial)
    # tutorial_thread.start()
    # tutorial_thread.join()

    if TEST:
        tutorial() # alters the global DELAY
    else:
        print("Starting tutorial ...")
        tutorial()
        # print("Starting game body ...")
        CANVAS.after(DELAY, lambda: game_body()) # alters the global DELAY
        # print("Quiting game ...")
        ROOT.quit()

    # CANVAS.after(DELAY, lambda: game_body())
    
    
    # TODO: this may be better
    # game_body_thread = threading.Thread(target=game_body)
    # game_body_thread.start()
    # game_body_thread.join()


    # wait for the begin_prompting function
    # to finish, then destroy the window
    # TODO: not sure about the following line
    # it's probably wrong. 
    # CANVAS.after(DELAY, lambda: ROOT.destroy())


    ROOT.mainloop()


TEST = False

def main():
    # Start a separate thread to run the user prompt function
    # game()
    if TEST:
        game()
    else:
        print("Initializing...")
        initialize()
        # print("Starting game thread ...")
        # game_thread = threading.Thread(target=game)
        # game_thread.start()
        # game_thread.join()
        # print("Cleaning up threads...")
        game()



        cleanup_threads()
        print("Finishing...")
        finish()
        print("All done!")

if __name__ == "__main__":
    main()