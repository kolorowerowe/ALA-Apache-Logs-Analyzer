import pandas as pd
import os
import numpy as np
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, Dropout
from MLs.MLmodule import MLmodule

from reader import file_reader
from ALparser.ALParser import ApacheLogParser

class Trainer(MLmodule):

    def __init__(self, log_file_name, labels_file_name):
        TrainerParser = ApacheLogParser()
        file_reader.read_logs_file(TrainerParser, log_file_name)
        df = TrainerParser.getMLFormattedLogs()
        super().__init__(df)
        
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        relative_file_path = '../../data/' + labels_file_name
        abs_file_path = os.path.join(script_dir, relative_file_path)
        with open(abs_file_path, "r") as f:
            for line in f:
                self.labels.append(line[:-1])
        self.labels = pd.Series(self.labels, name="labels")

    def prepareAndTrain(self):
        encLabels = self.encodeLabels()
        encCat = self.encodeCategorical()

        inputs = np.append(encCat, self.numeric, axis=1)

        X_train, X_test, y_train, y_test = train_test_split(inputs, encLabels, test_size=0.3, random_state=53)

        model = Sequential()
        model.add(Dense(128, input_dim=X_train.shape[1], activation='elu', kernel_initializer='he_normal'))
        model.add(Dense(64, input_dim=X_train.shape[1], activation='elu'))

        model.add(Dense(1, activation='sigmoid'))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['binary_accuracy'])
        model.fit(X_train, y_train, epochs=100, batch_size=16, verbose=2)
        _, accuracy = model.evaluate(X_test, y_test, verbose=0)
        print('Accuracy: %.2f' % (accuracy*100))
        # if(accuracy*100 > 78.31):
        if(accuracy*100 > 77.38):
            model.save(os.path.join(os.path.dirname(__file__), '../../models/model_01'))