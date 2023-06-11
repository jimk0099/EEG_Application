import time
import threading
import numpy as np
import pandas as pd
import tkinter as tk
from queue import Queue

from game_utils import show_new_text, show_stick_figure, show_stick_figure_raise_left_arm, game

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
