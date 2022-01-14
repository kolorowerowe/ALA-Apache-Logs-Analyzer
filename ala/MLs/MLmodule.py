from sklearn.preprocessing import LabelEncoder, OrdinalEncoder
import numpy as np
import os

class MLmodule:
    VALID_COLUMNS_LIST = ['session_id', 'host', 'logname', 'user', 'http_method', 'activity', 'activity_file_ext', 'http_version', 'status', 'bytes_of_response',
                            'referer', 'user_agent', 'suspicious_referer', 'suspicious_agent', 'reserved_words', 'err_status', 'prec_sign_count', 'session_request_count',
                            'session_request_count_per_second', 'session_same_count']
    NUMERIC_COLUMNS_LIST = ['status', 'bytes_of_response', 'suspicious_agent', 'reserved_words', 'err_status', 'prec_sign_count', 'session_request_count',
                            'session_request_count_per_second', 'session_same_count']
    CATEGORICAL_COLUMNS_LIST = ['session_id', 'host', 'logname', 'user', 'http_method', 'activity', 'activity_file_ext', 'http_version', 'referer', 'user_agent']

    def __init__(self, df, load_oe=False, important=False) -> None:
        if not self.validate(df):
            raise RuntimeError("Invalid data passed to trainer.")
        self.numeric = df[self.NUMERIC_COLUMNS_LIST]
        self.categorical = df[self.CATEGORICAL_COLUMNS_LIST]
        self.labels = []
        self.le = LabelEncoder()
        self.le.fit(['normal', 'attack'])
        self.important = important
        self.oe = OrdinalEncoder()
        self.imp_cat = self.categorical[['http_method', 'activity_file_ext', 'http_version']]
        if important:
            self.oe.fit(self.imp_cat)
        else:
            self.oe.fit(self.categorical)
        if load_oe:
            oe_cat = np.load(os.path.join(os.path.dirname(__file__),'encoder_data.npy'), allow_pickle=True)
            for feature_num in range(len(oe_cat)):
                self.oe.categories_[feature_num] = np.unique(np.append(oe_cat[feature_num], self.oe.categories_[feature_num]))


    def validate(self, dataframe):
        return list(dataframe.columns) == self.VALID_COLUMNS_LIST

    def encodeCategorical(self):
        if self.important:
            return self.oe.transform(self.imp_cat)
        return self.oe.transform(self.categorical)

    def decodeCategorical(self, data):
        return self.oe.inverse_transform(data)

    def encodeLabels(self):
        return self.le.transform(self.labels)

    def decodeLabels(self, labels):
        return self.le.inverse_transform(labels)

    def saveOrdinalEncoder(self):
        np.save(os.path.join(os.path.dirname(__file__), 'encoder_data'), self.oe.categories_)