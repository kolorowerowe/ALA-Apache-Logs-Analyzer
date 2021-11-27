import re
import pandas as pd
import datetime
from config import Configuration

class ApacheLogParser:
    NCSAExtendedCombinedLogFormatRegex = '([(\d\.)]+) "?([\w-]+)"? "?([\w-]+)"? \[(.*?)\] "(.*?)" (\d+) ([\d-]+) "(.*?)" "(.*?)"\n?'
    __logs = []
    visFormLogs = []
    def parseLine(self, logLine):
        matched = re.fullmatch(self.NCSAExtendedCombinedLogFormatRegex, logLine)
        if matched:
            if self.areLogsDF():
                self.addLogLineToDF(matched, logLine)
            else:
                self.addLogLineToList(matched, logLine)

    def preprocess(self):
        self.__logs = pd.DataFrame(self.__logs)
        self.sessions = self.normalize()
        if not self.sessions:
            raise RuntimeError('Normalization impossible, logs may be empty.')

    def areLogsDF(self):
        return isinstance(self.__logs, pd.DataFrame)

    def addLogLineToDF(self, matched, line):
        self.__logs = self.__logs.append({'raw': line, 'host': matched[1], 'logname': matched[2], 'user': matched[3], 'time': matched[4], 'request': matched[5], 'status': matched[6], 'bytes_of_response': matched[7], 'referer': matched[8], 'user_agent': matched[9]},ignore_index=True)
    
    def addLogLineToList(self, matched, line):
        self.__logs.append({'raw': line, 'host': matched[1], 'logname': matched[2], 'user': matched[3], 'time': matched[4], 'request': matched[5], 'status': matched[6], 'bytes_of_response': matched[7], 'referer': matched[8], 'user_agent': matched[9]})
    
    def normalize(self):
        if not self.areLogsDF:
            return None

        hosts = pd.unique(self.__logs['host'])
        logs_by_hosts = [{'host': address, 'logs': self.__logs[self.__logs['host'] == address]} for address in hosts]
        # divide into sessions
        for log_idx, entry in enumerate(logs_by_hosts):
            sessions_dict = dict()
            i = 1

            for index, row in entry['logs'].iterrows():
                session_name = f'session{i}'
                if session_name not in sessions_dict.keys():
                    sessions_dict[session_name] = pd.DataFrame()
                elif self.differMoreThanHour(sessions_dict[session_name].iloc[-1]['time'], row['time']):
                    i += 1
                    session_name = f'session{i}'
                    sessions_dict[session_name] = pd.DataFrame()
                sessions_dict[session_name] = sessions_dict[session_name].append(row)

            logs_by_hosts[log_idx]['logs'] = sessions_dict
        return logs_by_hosts

    def differMoreThanHour(self, date1, date2):
        struct_date_1 = datetime.datetime.strptime(date1, "%d/%B/%Y:%H:%M:%S +0000")
        struct_date_2 = datetime.datetime.strptime(date2, "%d/%B/%Y:%H:%M:%S +0000")
        return struct_date_1 + datetime.timedelta(hours=1) < struct_date_2

    def getParsedLine(self, index):
        if self.areLogsDF():
            return self.__logs.iloc[index]
        return self.__logs[index]

    def getMLFormattedLogs(self):
        # TODO:
        ''' Return a df with columns:
        - session_id - '[host]:[session number]'
        - host*
        - logname*
        - user*
        - http_method - extracted from request
        - activity - extracted from request
        - http_version - extracted from request
        - status*
        - bytes_of_response*
        - referer*
        - user_agent*
        - suspicious_agent - boolean, informs whether user_agent is on the list of known suspicious agents
        - reserved_words - boolean, informs whether any words from the list of reserved words were used in request
        - err_status - boolean, informs whether response status indicates a possible attempt of unauthorized access
        - prec_sign_count - number of '%' signs in request: high number may indicate an attempt to hide reserved words by using character encodings
        - session_request_count - number of requests in current session
        - session_request_count_per_second - average number of requests in current session per second
        where * means that data is taken directly from parsed logs.
        '''
        pass

    def getVisualizationFormattedLogs(self):
        for log_idx, session in enumerate(self.sessions):
            for log in session['logs'].keys():
                if "session" in log:
                    req = []
                    i = 0 
                    for r in session['logs'][log]['request']:
                        normRequest = r.lower().split(" ")[1]
                        normRequest = normRequest.split("?")[0]
                        url = normRequest.split(".")
                        if normRequest[len(normRequest) - 1] == '/':
                            normRequest = normRequest[:len(normRequest)-1]
                        if len(normRequest) > 0 and (len(url) == 1 or url[len(url)-1].lower() not in Configuration.extensionsToRemove):
                            req.append(normRequest)
                            self.visFormLogs.append({'caseId': f'{log_idx}_{log}', 'Activity': normRequest, 'index': i})
                            i= i + 1
                    self.visFormLogs.append({'caseId': f'{log_idx}_{log}', 'Activity': 'End', 'index': i})

        return self.visFormLogs

    @property
    def logs(self):  
        return self.__logs