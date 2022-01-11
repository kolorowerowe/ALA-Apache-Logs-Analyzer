from keras.models import load_model
import os
import numpy as np

from MLs.MLmodule import MLmodule

class Checker(MLmodule):
    def __init__(self, dataframe, model_name):
        super().__init__(dataframe)
        self.dataToClassify = dataframe
        self.model = load_model(os.path.join(os.path.dirname(__file__), '../../models/' + model_name))

    def predict(self):
        encCat = self.encodeCategorical()

        inputs = np.append(encCat, self.numeric, axis=1)
        ynew = self.model.predict(inputs)
        ynew_classes = self.decodeLabels([round(y) for y in ynew.flatten()])
        for y in ynew_classes:
            if y == 'attack':
                # send feedback to report and visualizer modules
                print()