from ultralytics import YOLO
from os.path import join as ospathjoin
from os import listdir as oslistdir
from tkinter import messagebox
from dialogs.infobox import InfoBox
from dialogs.trainanimaldetector import AnimalDetectorTrainingDialog
from shutil import copy as shutilcopy
import utils

"""Class to handle the operations involved with detecting animals in a picture"""
class HuntingAnimalDetector():
    """
    Initialize the module
    
    :param root_window: The main window of the program
    :type root_window: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Tk, tkinter.Frame
    :param retrain: Whether to force training or not when loading the module (Defaults to False)
    :type retrain: bool
    """
    def __init__(self, root_window, retrain = False):
        self.root = root_window
        self.logger = utils.setup_logger("AnimalDetector", "Animal Detector.log")
        self.logger.info("Detector Started")
        self.baseDirectory = utils.resource_path("",file_name=__file__)
        self.isLoading = False
        self.numTrainingEpochs = 0
        self.trainingBatchSize = 0
        if len([item for item in oslistdir(ospathjoin(self.baseDirectory, "Models")) if item.endswith(".pt")]) == 0 or retrain:
            self.modelPath = ospathjoin(self.baseDirectory,"yolov8n.pt")
            self.model = YOLO(self.modelPath) #Create the model using the modelPath
            if not retrain:
                msgboxAnswer = messagebox.askyesno("Train New Model", "There is no trained model, do you wish to train a model now?")
                if not msgboxAnswer:
                    messagebox.showinfo("No Model", "Cannot continue without a model, exiting now")
                    raise Exception("No Model Loaded and Training Not Initiated")
            self.isLoading = True
            try:
                self.trainer = utils.ModelTrainer(self.logger, "Animal Detector", None, self.get_train_info, self.trainingKwargs, self.model.train, self.transfer_weights)
            except Exception as e:
                self.logger.log(e.args[0])
        else:
            self.modelPath = ospathjoin(self.baseDirectory, "Models", [item for item in oslistdir(ospathjoin(self.baseDirectory, "Models")) if item.endswith(".pt")][0]) #Grab the first file in the models folder (Could add that it looks for the latest file put in)
            self.model = YOLO(self.modelPath) #Create the model using the modelPath
            
    """
    Loads any images to train the model on
    """
    def get_train_info(self):
        trainDialog = AnimalDetectorTrainingDialog(self.root)
        if trainDialog.result is None:
            self.logger.info("User cancelled the training of the animal detector")
            return "User cancelled the training of the animal detector"
        self.infoBox = InfoBox(self.root, "Training", "Please wait while the model trains, you may continue to use the app except for the Go Hunt button in the sidebar")
        
        self.device = trainDialog.result["Device"]
        self.numTrainingEpochs = trainDialog.result["Epochs"]
        self.trainingBatchSize = trainDialog.result["Batch Size"]
        self.trainingName = str(len(oslistdir(ospathjoin(self.baseDirectory, "Models/Detector Data/dataset/training/images")))) + \
                            "x" + str(self.numTrainingEpochs) + \
                            "x" + str(self.trainingBatchSize)
    """
    Sets up any information that should be passed to the training function
    
    :returns: A dictionary with keyword arguments to pass to the training function
    :rtype: dict
    """
    def trainingKwargs(self):
        detectorTrainKwargs = {"data":str(ospathjoin(self.baseDirectory, "Models/Detector Data/dataset/dataset.yaml")),
            "imgsz":640,
            "task":"detect", 
            "project":ospathjoin(self.baseDirectory, "Models/Detector Data/runs"),
            "epochs":self.numTrainingEpochs,
            "batch":self.trainingBatchSize,
            "name":self.trainingName,
            "exist_ok":True,
            "device":self.device,
            "save":False}
        return detectorTrainKwargs
    
    """
    Saves the trained model in a location for later use
    """
    def transfer_weights(self):
        src =  ospathjoin(self.baseDirectory, "Models/Detector Data/runs", self.trainingName, "weights/best.pt")
        dest = ospathjoin(self.baseDirectory, "Models", self.trainingName+".pt")
        shutilcopy(src,dest)
        self.modelPath = ospathjoin(self.baseDirectory,"Models", oslistdir(ospathjoin(self.baseDirectory, "Models"))[0]) #Grab the first file in the models folder (Could add that it looks for the latest file put in)
        self.infoBox.close_info_box()
        messagebox.showinfo("Detector Training Completed", "Animal detector model has finished training, you may use it to acess the hunt section")
        self.logger.info("Transfered best training to be default model")
        self.isLoading = False
        
    """
    Predicts if there are any animals in the picture and what kind they are
    
    :returns: A list of the classes seen in the picture
    :rtype: list[int] or None
    """
    def detect_animals(self, image_path, confidence_threshold):
        if not self.isLoading:
            results = list(self.model.predict(image_path, conf=confidence_threshold, verbose=False))[0].boxes.cls.tolist()
            return [int(x) for x in results]
        else:
            return None




