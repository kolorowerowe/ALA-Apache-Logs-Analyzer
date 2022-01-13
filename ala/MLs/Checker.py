from keras.models import load_model
import os
import numpy as np
import joblib

from MLs.MLmodule import MLmodule

class Checker(MLmodule):
    def __init__(self, dataframe, model_name):
        super().__init__(dataframe, True)
        self.dataToClassify = dataframe
        self.model = joblib.load(os.path.join(os.path.dirname(__file__), '../../models/RFC'))
        # self.model = load_model(os.path.join(os.path.dirname(__file__), '../../models/' + model_name))

    def predictAndInform(self):
        encCat = self.encodeCategorical(important=True)
        numCat = encCat.shape[1]

        inputs = np.append(encCat, self.numeric, axis=1)
        ynew = self.model.predict(inputs)
        ynew_classes = self.decodeLabels([round(y) for y in ynew.flatten()])

        sus_requests = dict()

        for y in range(len(ynew_classes)):
            if ynew_classes[y] == 'attack':
                # restore original log entry
                decoded = self.decodeCategorical(inputs[y,:numCat].reshape(1,-1)).flatten().tolist()
                request = self.categorical[['host', 'logname', 'user']].iloc[y].tolist()
                request.append(f"\"{decoded[0]} {self.categorical['activity'].iloc[y]} {decoded[2]}\"")
                request.append(str(int(self.numeric['status'].iloc[y])))
                request.append(str(int(self.numeric['bytes_of_response'].iloc[y])))
                request.append("\"" + self.categorical['referer'].iloc[y] + "\"")
                request.append("\"" + self.categorical['user_agent'].iloc[y] + "\"")
                request = " ".join(request)

                id = self.categorical['session_id'].iloc[y]
                if not id in sus_requests:
                    sus_requests[id] = [request]
                else:
                    sus_requests[id].append(request)
        
        return sus_requests