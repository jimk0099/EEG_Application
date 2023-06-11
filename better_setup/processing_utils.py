import time
import threading
import numpy as np

from queue import Queue
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, NoiseTypes

def process_eeg(data):
    """
    This function will process the EEG data.
    """
    for channel in EEG_CHANNELS:
        DataFilter.perform_bandstop(data[channel], SAMPLING_RATE,
                                    49, 51, 4, FilterTypes.BESSEL.value, 0)
        DataFilter.perform_bandpass(data[channel], SAMPLING_RATE,
                                    0.5, 30.0, 4, FilterTypes.BESSEL.value, 0)
        # The paper isn't clear regarding the feature extraction.
        # Specifically, it does not mention whether the features are extracted
        # by each channel alone or by all channels together.
    # TODO: extract features
    # TODO: classify
    # return prediction
    raise NotImplementedError
    
def process_eeg_queue():
    """
    This function will process the EEG data from the queue.
    """
    while True:
        data = EEG_QUEUE.get(block=True)
        prediction = process_eeg(data)
        PREDICTION_QUEUE.put(prediction)

BOARD = None
BOARD_ID = None
SAMPLING_RATE = None
EEG_CHANNELS = None
REACTION_DELAY = None
WINDOW = None
PROCESSING_THREAD = None
def initialize():
    """
    This function will initialize the board.
    """     
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
    
    # 300 ms reaction delay. The reaction delay can also be
    # well tuned on the performance of the user.
    REACTION_DELAY = 0.300
    
    
    # 256 ms window for signal proposed on the paper
    # Hamedi, M., Salleh, S.-H., Noor, A. M., & Mohammad-Rezazadeh, I. (2014).
    # Neural network-based three-class motor imagery classification
    # using time-domain features for BCI applications.
    # 2014 IEEE REGION 10 SYMPOSIUM. doi:10.1109/tenconspring.2014.6863026 
    WINDOW = 0.256
    
    # Queue to store the EEG data chunks
    EEG_QUEUE = Queue()
    # Queue to store the predictions
    PREDICTION_QUEUE = Queue()

    # Start a separate thread to run the processing function
    PROCESSING_THREAD = threading.Thread(target=process_eeg_queue)
    PROCESSING_THREAD.start()

def cleanup_threads():
    """
    This function will clean up the threads.
    """
    PROCESSING_THREAD.join()

def finish():
    """
    This function will finish the board.
    """
    BOARD.stop_stream()
    BOARD.release_session()

