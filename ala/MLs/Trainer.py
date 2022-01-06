import pandas as pd
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense

class Trainer:
    VALID_COLUMNS_LIST = ['session_id', 'host', 'logname', 'user', 'http_method', 'activity', 'activity_file_ext', 'http_version', 'status', 'bytes_of_response',
                            'referer', 'user_agent', 'suspicious_referer', 'suspicious_agent', 'reserved_words', 'err_status', 'prec_sign_count', 'session_request_count',
                            'session_request_count_per_second', 'session_same_count']
    NUMERIC_COLUMNS_LIST = ['status', 'bytes_of_response', 'suspicious_agent', 'reserved_words', 'err_status', 'prec_sign_count', 'session_request_count',
                            'session_request_count_per_second', 'session_same_count']
    CATEGORICAL_COLUMNS_LIST = ['session_id', 'host', 'logname', 'user', 'http_method', 'activity', 'activity_file_ext', 'http_version', 'referer', 'user_agent']

    def __init__(self, dataframes):
        validDFs = []
        for df in dataframes:
            if self.validate(df):
                validDFs.append(df)
        sourceData = pd.concat(validDFs, ignore_index=True)
        self.numeric = sourceData[self.NUMERIC_COLUMNS_LIST]
        self.categorical = sourceData[self.CATEGORICAL_COLUMNS_LIST]
        # TODO:
        self.labels = []

        columnsToDrop = []
        for cat in self.CATEGORICAL_COLUMNS_LIST:
            u = self.categorical[cat].unique()
            # debug
            print(f'{cat}:\n{u}\n')
            if len(u) in [0,1]:
                columnsToDrop.append(cat)
        self.categorical = self.categorical.drop(columns=[columnsToDrop])


    def validate(self, dataframe):
        return list(dataframe.columns) == self.VALID_COLUMNS_LIST

    def encodeCategorical(self):
        oe = OrdinalEncoder()
        oe.fit(self.categorical)
        return oe.transform(self.categorical)

    def encodeLabels(self):
        le = LabelEncoder()
        le.fit(['normal', 'attack'])
        return le.transform(self.labels)

    def prepareAndTrain(self):
        encLabels = self.encodeLabels()
        encCat = self.encodeCategorical()

        inputs = encCat.update(self.numeric)

        X_train, X_test, y_train, y_test = train_test_split(inputs, encLabels, test_size=0.3, random_state=53)

        model = Sequential()
        model.add(Dense(64, input_dim=X_train.shape[1], activation='elu', kernel_initializer='he_normal'))
        model.add(Dense(32, input_dim=X_train.shape[1], activation='elu'))
        model.add(Dense(1, activation='sigmoid'))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        model.fit(X_train, y_train, epochs=100, batch_size=16, verbose=2)
        _, accuracy = model.evaluate(X_test, y_test, verbose=0)
        print('Accuracy: %.2f' % (accuracy*100))