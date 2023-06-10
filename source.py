import time
import threading
import numpy as np
import pandas as pd
import tkinter as tk
from queue import Queue

from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, NoiseTypes

def process_eeg(data):
    for channel in EEG_CHANNELS:
        DataFilter.perform_bandstop(data[channel], SAMPLING_RATE,
                                    49, 51, 4, FilterTypes.BESSEL.value, 0)
        DataFilter.perform_bandpass(data[channel], SAMPLING_RATE,
                                    0.5, 30.0, 4, FilterTypes.BESSEL.value, 0)
        # The paper isn't clear regarding the feature extraction.
        # Specifically, it does mention whether the features are extracted
        # by each channel alone or by all channels together.
    

def process_eeg_queue():
    while True:
        data = EEG_QUEUE.get(block=True)
        threading.Thread(Target=process_eeg, args=(data,)).start()

def prompt_user():
    for timestamp in TIMESTAMPS:
        # wait for the elapsed time
        time.sleep(timestamp)
        
        # execute the actual prompting function
        # ========= MISSING FUNCTION =========

        # mark the prompt
        BOARD.insert_marker(timestamp)
        
        # wait for the user to react, suppose constant reaction time
        time.sleep(REACTION_DELAY + WINDOW)
        
        # gather eeg data
        EEG_QUEUE.put(BOARD.get_board_data(WINDOW*SAMPLING_RATE))
        
        TIMESTAMPS = np.minus(TIMESTAMPS, timestamp)
        
delay = 0
head = None
stick = None
stick_arm_left = None
stick_arm_right = None
stick_leg_left = None
stick_leg_right = None
def game():
    # this function will run the game. The game will be
    # a simple game that will prompt the user to perform
    # a motor imagery task. The game will then process the
    # EEG data and will give a feedback to the user.
    root = tk.Tk()
    root.title("Motor Imagery Game")
    root.geometry("1200x600")
    # showcase preview
    # firstly, print some text that will explain the game
    # to the user
    canvas = tk.Canvas(root, width=800, height=600)
    canvas.pack()
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

    def show_stick_figure():
        global head, stick, stick_arm_left, stick_arm_right, stick_leg_left, stick_leg_right
        head = canvas.create_oval(425, 200, 375, 150, width=5)
        stick = canvas.create_line(400, 300, 400, 200, width=5)
        stick_arm_left = canvas.create_line(400, 200, 350, 250, width=5)
        stick_arm_right = canvas.create_line(400, 200, 450, 250, width=5)
        stick_leg_left = canvas.create_line(400, 300, 350, 375, width=5)
        stick_leg_right = canvas.create_line(400, 300, 450, 375, width=5)
    
    def show_stick_figure_raise_left_arm():
        global stick_arm_left, delay
        canvas.delete(stick_arm_left)
        stick_arm_left = canvas.create_line(400, 200, 350, 150, width=5)

    def show_new_text(texts_list, index=0):
        global delay
        if index < len(texts_list):
            new_text = texts_list[index]
            width = len(new_text) * 10
            text_item = canvas.create_text(400, 50, text=new_text,
                                           font=("Arial", 24), fill="black",
                                           width=width, justify="center")
            canvas.after(delay + 3000, lambda: canvas.delete(text_item))
            canvas.after(delay + 4000, lambda: show_new_text(texts_list, index + 1))
    # Start displaying the texts

    show_new_text(texts)
    # wait for the show_new_text function
    # to finish with the texts
    canvas.after(len(texts) * 4000, show_stick_figure)
    # show a prompt, like a yellow sun on the left of the user
    canvas.after(len(texts) * 4000 + 2000, lambda: canvas.create_oval(100, 100, 200, 200, fill="yellow"))
    delay = len(texts) * 4000 + 2000
    # show some text that explains the prompt
    texts = [
        "The sun on your left means that you have to raise your left arm.", 
        "If you manage to imagine it correctly, the sun will turn green,", 
        "the stick figure will raise its left arm and you will get a point."
    ]
    canvas.after(delay + 1000, lambda: show_new_text(texts))
    # wait for the show_new_text function
    # to finish with the texts, then show the stick figure
    # with the left arm raised and the sun green

    canvas.after(delay + len(texts) * 4000, 
                 lambda: show_stick_figure_raise_left_arm())
    canvas.after(delay + len(texts) * 4000, 
                 lambda: canvas.create_oval(100, 100, 200, 200, fill="green"))
    # also show a point gained
    canvas.after(delay + len(texts) * 4000,
                 lambda: canvas.create_text(100, 300, text="1", font=("Arial", 24), fill="black"))

    
    root.mainloop()
        
        
def main():
    game_tread = threading.Thread(target=game)
    game_thread.start()
    
    BoardShim.enable_dev_board_logger()
    
    params = BrainFlowInputParams()
    params.serial_port = "/dev/ttyUSB0"
    BOARD = BoardShim(BoardIds.CYTON_DAISY_BOARD, params)
    BOARD_ID = BoardIds.CYTON_DAISY_BOARD.value
    SAMPLING_RATE = BOARD.get_sampling_rate(BOARD_ID)

    BOARD.prepare_session()
    BOARD.start_stream()
    BoardShim.log_message(LogLevels.LEVEL_INFO.value, 'start sleeping in the main thread')

    EEG_CHANNELS = BoardShim.get_eeg_channels(BOARD_ID)
    
    # 300 ms reaction delay
    # the reaction delay can also be
    # well tuned on the performance
    # of the user.
    REACTION_DELAY = 0.300
    # 256 ms window for signal proposed on the paper
    # Hamedi, M., Salleh, S.-H., Noor, A. M., & Mohammad-Rezazadeh, I. (2014).
    # Neural network-based three-class motor imagery classification
    # using time-domain features for BCI applications.
    # 2014 IEEE REGION 10 SYMPOSIUM. doi:10.1109/tenconspring.2014.6863026 
    WINDOW = 0.256
    # generate uniformly distributed random time stamps
    TIMESTAMPS = np.random.uniform(low=5.0, high=110.0, size=(10, ))
    EEG_QUEUE = Queue()

    # Start a separate thread to run the user prompt function
    game_thread = threading.Thread(target=game)
    game_thread.start()
    # Start a separate thread to run the user prompt function
    prompting_thread = threading.Thread(target=prompt_user)
    prompting_thread.start()
    # Start a separate thread to run the processing function
    processing_thread = threading.Thread(target=process_eeg_queue)
    processing_thread.start()


    BOARD.stop_stream()
    BOARD.release_session()


if __name__ == "__main__":
    main()
