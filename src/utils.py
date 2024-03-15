import logging
import multiprocessing
import threading
import sys
import ttkbootstrap.validation as ttkval
from os.path import dirname as ospathdirname
from os.path import abspath as ospathabspath
from os.path import join as ospathjoin


@ttkval.validator
def validate_coord(event=None):
    """
    Validation function for the coordinates of an entry

    :param event: The event that called this function
    :type event: ttkboostrap.Event

    :returns: True if the validation succeded, False otherwise
    :rtype: Bool
    """
    if not event.validationreason == "Final":
        return True
    entry = event.widget.get()
    if not "," in entry:
        return False
    entry = entry.split(",")
    try:
        float(entry[0])
        float(entry[1].replace(" ", ""))
        return True
    except ValueError:
        return False


def resource_path(relative_path, debug_mode=True, file_name=None):
    """
    Gets the path to the resource input. This is needed for the pyinstaller system to make an executable

    :param relative_path: The input path to find the first part of
    :type relative_path: str
    :param debug_mode: Switches between bebug and production (Needed for pyinstaller to work correctly)
    :type debug: Bool
    :param file_name: The name of the file that it should look at when debug mode is on (Helps keep the main directory from becoming cluttered)
    :type file_name: str

    :returns: The absolute path to the input
    :rtype: str
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        if debug_mode:
            base_path = ospathdirname(ospathabspath(file_name))
        else:
            base_path = ospathdirname(sys._MEIPASS)
    except Exception:
        base_path = ospathabspath(".")

    if relative_path == "":
        return base_path
    else:
        return ospathjoin(base_path, relative_path)


def setup_logger(name, filename, level=logging.INFO):
    """
    Handles setting up the logger system and returns a handle to it

    :param name: The name to give the logger
    :type name: str
    :param filename: The name of the file to be created
    :type filename: str
    :level: The level the logger will operate at (Default to INFO)
    :type level: logging.Level

    :returns: The handle to the logger
    :rtype: logging.Logger
    """
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler = logging.FileHandler(resource_path("Logs/" + filename, file_name=__file__))
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


class RepeatTimer(threading.Timer):
    """
    Runs the input function when the class is instantiated, Waits the interval time, and calls it again until cancelled
    """

    def run(self):
        while not self.finished.wait(self.interval):
            self.function()


class ModelTrainer:
    """
    Handles training of models in non-blocking manner

    :param logger: The logger handle to use while model training
    :type logger: logging.Logger
    :param req_mod_cb: Callback that runs to load in any required models to train the current one
    :type req_mod_cb: Callable
    :param load_data_cb: Callback that runs to load in training data for the model
    :type load_data_cb: Callable
    :param training_kwarg_cb: Callback that runs to load any information that needs to be passed to the training function
    :type training_kwarg_cb: Callable
    :param training_cb: Callback that runs to train the model
    :type training_cb: Callable
    :param post_train_cb: Callback that runs after the model has finished training. Usually to save the model to a directory
    :type post_train_cb: Callable
    
    ..note::
    
        This module requires that all modules that use this to train themselves have a parameter called isLoading to ensure they are fully trained before using them
    """

    def __init__(
        self,
        logger,
        name,
        req_mod_cb=None,
        load_data_cb=None,
        training_kwarg_cb=None,
        training_cb=None,
        post_train_cb=None,
    ):
        self.logger = logger
        self.name = name
        self.requiredModulesCallback = req_mod_cb
        self.loadDataCallback = load_data_cb
        self.trainingKwargCallback = training_kwarg_cb
        self.trainingCallback = training_cb
        self.postTrainingCallback = post_train_cb
        self.doneTimer = RepeatTimer(1, self.check_training_done, ["Repeating"])
        self.loadedTimer = RepeatTimer(1, self.check_all_modules_loaded, ["Repeating"])
        self.load_required_modules()

    def load_required_modules(self):
        """
        Calls the callback to load any required modules

        .. warning::

           Do not make a required modules callback unless it really needs it. The default value of function call with no return is None, which corresponds to an error in this module and will quit training
        """

        if self.requiredModulesCallback is not None:
            self.logger.info("Loading needed modules for training")
            self.moduleList = self.requiredModulesCallback()
            if (
                self.moduleList is None
            ):  # If the callback returns none, then there was an error trying to load required modules
                self.post_training(True)
            self.loadedTimer.start()
        else:  # If no modules are needed, then we can just skip to gathering data
            if self.gather_training_data() is not None:
                self.postTrainingCallback(failed=True)

    def gather_training_data(self):
        """
        Calls the function to gather any training data needed. Function needs to return the training data
        """
        self.logger.info("Gathering data for training")
        if self.loadDataCallback is not None:
            result = self.loadDataCallback()
            if result is not None:
                self.logger.error(result)
                return result
        self.logger.info("training data collected")
        self.start_training()

    def start_training(self):
        """
        Calls the training callback
        """
        if self.trainingKwargCallback is not None:
            self.logger.info("Gathering training function keywords dictionary")
            self.trainKwargs = self.trainingKwargCallback()
            self.logger.info("Got keyword dictionary")
        else:
            self.trainKwargs = {}
        self._start_training_thread()

    def _start_training_thread(self):
        """
        Starts a thread to train the model to not block any other operations
        """
        self.trainThread = multiprocessing.Process(
            target=self.trainingCallback, kwargs=self.trainKwargs
        )
        self.trainThread.name = self.name
        self.logger.info("Starting training thread")
        self.trainThread.start()
        self.doneTimer.start()

    def check_training_done(self):
        """
        Checks to see if the training thread has finished its job
        """
        if not self.trainThread.is_alive():  # Training thread has completed
            self.logger.info("Model training ended")
            self.doneTimer.cancel()
            self.post_training()

    def check_all_modules_loaded(self):
        """
        Checks to see if all the required models are loaded properly. I.E, any other modules that require training are done
        """
        if (
            self.moduleList is None
        ):  # If no submodules are required, then there are no modules to wait on
            return

        for module in self.moduleList:
            if module.isLoading:
                return
        self.logger.info("All required modules loaded")
        self.loadedTimer.cancel()
        self.gather_training_data()

    def post_training(self, failed: bool = False):
        """
        Calls the post train callback
        
        :param failed: Determines if we should run the post training function or not (Defaults to false, which will run the post training function)
        :type failed: bool
        """
        if not failed:
            self.logger.info("Calling post train function")
            result = self.postTrainingCallback()
            self.trainThread.close()
            if result is not None:
                self.logger.error(result)
                return
            self.logger.info("Done training")
        else:
            self.logger.error("Failed to train the system")
