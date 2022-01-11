from keras.models import load_model
import os
import numpy as np

from MLs.MLmodule import MLmodule

class Checker(MLmodule):
    def __init__(self, dataframe, model_name):
        super().__init__(dataframe)
        self.dataToClassify = dataframe
        self.model = load_model(os.path.join(os.path.dirname(__file__), '../../models/' + model_name))

    def predictAndInform(self):
        encCat = self.encodeCategorical()
        numCat = encCat.shape[1]

        inputs = np.append(encCat, self.numeric, axis=1)
        ynew = self.model.predict(inputs)
        ynew_classes = self.decodeLabels([round(y) for y in ynew.flatten()])

        sus_requests = dict()

        for y in range(len(ynew_classes)):
            if ynew_classes[y] == 'attack':
                # restore original log entry
                decoded = self.decodeCategorical(inputs[y,:numCat].reshape(1,-1)).flatten().tolist()
                request = decoded[1:4]
                request.append("\"" + " ".join(decoded[4:6] + [decoded[7]]) + "\"")
                request.append(str(int(self.numeric['status'].iloc[y])))
                request.append(str(int(self.numeric['bytes_of_response'].iloc[y])))
                request.append("\"" + decoded[-2] + "\"")
                request.append("\"" + decoded[-1] + "\"")
                request = " ".join(request)

                if not decoded[0] in sus_requests:
                    sus_requests[decoded[0]] = [request]
                else:
                    sus_requests[decoded[0]].append(request)
        
        return sus_requests