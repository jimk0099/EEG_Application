import time
import threading
import numpy as np

from queue import Queue
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, NoiseTypes

def rms(data):
    """
    This function will calculate the RMS of the data.
    """
    return np.sqrt(np.mean(np.square(data)))

def ieeg(data):
    """
    This function will calculate the IEEG of the data.
    """
    return np.sum(np.abs(data))

def process_eeg(data):
    """
    This function will process the EEG data.
    """
    global SAMPLING_RATE, EEG_CHANNELS, WINDOW
    SPECIFIC_CHANNELS = ['C3', 'C4'] # either F4 or P4 because Cz is missing.
    features = {'C3': [], 'C4': []}
    for channel in SPECIFIC_CHANNELS:
        DataFilter.perform_bandpass(data[EEG_DICTIONARY[channel]], SAMPLING_RATE,
                                    0.5, 30, 4, FilterTypes.BESSEL.value, 0)
        DataFilter.perform_bandstop(data[EEG_DICTIONARY[channel]], SAMPLING_RATE,
                                    48, 52, 4, FilterTypes.BESSEL.value, 0)
        
        features[channel].append(np.log(rms(data[EEG_DICTIONARY[channel]])))
        features[channel].append(np.log(ieeg(data[EEG_DICTIONARY[channel]])))

    # TODO: implement classifier
    # for the time being, return random prediction
    return np.random.randint(0, 2)
    
def process_eeg_queue():
    """
    This function will process the EEG data from the queue.
    """
    global EEG_QUEUE, PREDICTION_QUEUE
    print("Processing thread started")
    print("Initializing queues")


    EEG_QUEUE = Queue()
    print("EEG queue initialized")
    PREDICTION_QUEUE = Queue()
    print("Prediction queue initialized")
    
    while True:
        data = EEG_QUEUE.get(block=True)
        prediction = process_eeg(data)
        PREDICTION_QUEUE.put(prediction)

def get_prediction(moment):
    """
    This function will get the prediction.
    """
    global BOARD, REACTION_DELAY, WINDOW, SAMPLING_RATE, PREDICTION_QUEUE, EEG_QUEUE
    BOARD.insert_marker(moment)        

    # wait for the user to react, suppose constant reaction time
    time.sleep(REACTION_DELAY + WINDOW)
    
    # gather eeg data
    EEG_QUEUE.put(BOARD.get_board_data(int(WINDOW*SAMPLING_RATE)))
    
    # get the prediction
    start = time.time()
    prediction = PREDICTION_QUEUE.get(block=True)
    end = time.time()

    return prediction, int(end - start + REACTION_DELAY + WINDOW)

BOARD = None
BOARD_ID = None
SAMPLING_RATE = None
EEG_CHANNELS = None
REACTION_DELAY = None
WINDOW = None
PROCESSING_THREAD = None
PREDICTION_QUEUE = None
EEG_QUEUE = None
EEG_DICTIONARY = None
def initialize():
    """
    This function will initialize the board.
    """
    global BOARD, BOARD_ID, SAMPLING_RATE, EEG_CHANNELS, REACTION_DELAY, WINDOW, PROCESSING_THREAD, EEG_DICTIONARY
    
    BoardShim.enable_dev_board_logger()
    params = BrainFlowInputParams()
    params.serial_port = "/dev/ttyUSB0"
    
    BOARD = BoardShim(BoardIds.CYTON_DAISY_BOARD, params)
    BOARD_ID = BoardIds.CYTON_DAISY_BOARD.value
    
    SAMPLING_RATE = BOARD.get_sampling_rate(BOARD_ID)
    print(f"Sampling rate is = {SAMPLING_RATE}")

    BOARD.prepare_session()
    BOARD.start_stream()
    BoardShim.log_message(LogLevels.LEVEL_INFO.value, 'start sleeping in the main thread')

    EEG_CHANNELS = BoardShim.get_eeg_channels(BOARD_ID)
    print(f"EEG channels are = {EEG_CHANNELS}")
    print(f"EEG names are = {BoardShim.get_eeg_names(BOARD_ID)}")
    EEG_DICTIONARY = dict(zip(BoardShim.get_eeg_names(BOARD_ID), EEG_CHANNELS))
    
    # 300 ms reaction delay. The reaction delay can also be
    # well tuned on the performance of the user.
    REACTION_DELAY = 0.300
    
    
    # 256 ms window for signal proposed on the paper
    # Hamedi, M., Salleh, S.-H., Noor, A. M., & Mohammad-Rezazadeh, I. (2014).
    # Neural network-based three-class motor imagery classification
    # using time-domain features for BCI applications.
    # 2014 IEEE REGION 10 SYMPOSIUM. doi:10.1109/tenconspring.2014.6863026 
    WINDOW = 0.256*2

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

