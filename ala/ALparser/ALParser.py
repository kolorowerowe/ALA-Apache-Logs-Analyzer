import os
import re
import pandas as pd
import datetime
from config import Configuration

class ApacheLogParser:
    __NCSAExtendedCombinedLogFormatRegex = '([(\d\.)]+) "?([\w-]+)"? "?([\w-]+)"? \[(.*?)\] "(.*?)" (\d+) ([\d-]+) "(.*?)" "(.*?)"\n?'
    __DatetimeFormat = "%d/%b/%Y:%H:%M:%S %z"
    # TODO: Refine lists
    __suspicious_agents = []
    __suspicious_referers = []
    __reserved_words = ['union','/etc','/passwd','%27',' or ','%20or%20','+or+',' and ','%20and%20','+and+','localhost',';','admin']
    #__err_statuses = []

    

    def __init__(self, sus_agents = '../../data/bad-user-agents.list', sus_referers = '../../data/bad-referer.list'):
        self.__logs = []
        self.visFormLogs = []
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in

        abs_agents_file_path = os.path.join(script_dir, sus_agents)
        with open(abs_agents_file_path, 'r') as f:
            self.__suspicious_agents = [line[:-1] for line in f]
        
        abs_referes_file_path = os.path.join(script_dir, sus_referers)
        with open(abs_referes_file_path, 'r') as f:
            self.__suspicious_referers = [line[:-1] for line in f]

    def parseLine(self, logLine):
        matched = re.fullmatch(self.__NCSAExtendedCombinedLogFormatRegex, logLine)
        if matched:
            if self.areLogsDF():
                self.addLogLineToDF(matched, logLine)
            else:
                self.addLogLineToList(matched, logLine)

    @staticmethod
    def parseExternalLine(logLine):
        matched = re.fullmatch('([(\d\.)]+) "?([\w-]+)"? "?([\w-]+)"? "(.*?)" (\d+) ([\d-]+) "(.*?)" "(.*?)"\n?', logLine)
        return matched[4]

    def preprocess(self):
        self.__logs = pd.DataFrame(self.__logs)
        self.sessions = self.normalize()
        if not self.sessions:
            raise RuntimeError('Normalization impossible, logs may be empty.')

    def areLogsDF(self):
        return isinstance(self.__logs, pd.DataFrame)

    def addLogLineToDF(self, matched, line):
        response_bytes = matched[7] if matched[7] != '-' else 0
        self.__logs = self.__logs.append({'raw': line, 'host': matched[1], 'logname': matched[2], 'user': matched[3], 'time': matched[4], 'request': matched[5], 'status': matched[6], 'bytes_of_response': response_bytes, 'referer': matched[8], 'user_agent': matched[9]},ignore_index=True)
    
    def addLogLineToList(self, matched, line):
        response_bytes = matched[7] if matched[7] != '-' else 0
        self.__logs.append({'raw': line, 'host': matched[1], 'logname': matched[2], 'user': matched[3], 'time': matched[4], 'request': matched[5], 'status': matched[6], 'bytes_of_response': response_bytes, 'referer': matched[8], 'user_agent': matched[9]})
    
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
        struct_date_1 = datetime.datetime.strptime(date1, self.__DatetimeFormat)
        struct_date_2 = datetime.datetime.strptime(date2, self.__DatetimeFormat)
        return struct_date_1 + datetime.timedelta(hours=1) < struct_date_2

    def getParsedLine(self, index):
        if self.areLogsDF():
            return self.__logs.iloc[index]
        return self.__logs[index]

    def getMLFormattedLogs(self):
        # TODO: encode string data
        ''' Return a df with columns:
        - session_id - '[host]:[session number]'
        - host*
        - logname*
        - user*
        - http_method - extracted from request
        - activity - extracted from request
        - activity_file_ext - extension of accessed file if any, else '-'
        - http_version - extracted from request
        - status*
        - bytes_of_response*
        - referer*
        - user_agent*
        - suspicious_referer - boolean, informs whether referer is on the list of known suspicious referers
        - suspicious_agent - boolean, informs whether user_agent is on the list of known suspicious agents
        - reserved_words - boolean, informs whether any words from the list of reserved words were used in request
        - err_status - boolean, informs whether response status indicates a possible attempt of unauthorized access
        - prec_sign_count - number of '%' signs in request: high number may indicate an attempt to hide reserved words by using character encodings
        - session_request_count - number of requests in current session
        - session_request_count_per_second - average number of requests in current session per second
        - session_same_count - number of identical requests in current session
        where * means that data is taken directly from parsed logs.
        '''
        MLdf = pd.DataFrame()

        for host_sessions in self.sessions:
            for session_id, logs in host_sessions['logs'].items():
                session_df = pd.DataFrame()
                min_session_time = datetime.datetime.strptime(logs.iloc[0]['time'], self.__DatetimeFormat)
                max_session_time = min_session_time
                current_session_id = f"{host_sessions['host']}:{session_id[7:]}"
                for index, log in logs.iterrows():
                    entry_time = datetime.datetime.strptime(log['time'], self.__DatetimeFormat)
                    if entry_time < min_session_time:
                        min_session_time = entry_time
                    if entry_time > max_session_time:
                        max_session_time = entry_time

                    current_entry_dict = dict()

                    current_entry_dict['session_id'] = current_session_id
                    current_entry_dict['host'] = log['host']
                    current_entry_dict['logname'] = log['logname']
                    current_entry_dict['user'] = log['user']
                    
                    request = log['request'].split(' ')
                    current_entry_dict['http_method'] = request[0]
                    current_entry_dict['activity'] = request[1]
                    if request[1].find('.html?') != -1:
                        current_entry_dict['activity_file_ext'] = 'html'
                    else:
                        last_dot = request[1].rfind('.')
                        last_slash = request[1].rfind('/')
                        extension_correct = True
                        if last_dot == -1 or last_slash > last_dot:
                            extension_correct = False
                        current_entry_dict['activity_file_ext'] = request[1][last_dot+1:] if extension_correct else '-'
                        ext_qmark = current_entry_dict['activity_file_ext'].rfind('?')
                        ext_prec = current_entry_dict['activity_file_ext'].rfind('%')
                        idc = []
                        if ext_qmark != -1:
                            idc.append(ext_qmark)
                        if ext_prec != -1:
                            idc.append(ext_prec)
                        if idc:
                            current_entry_dict['activity_file_ext'] = current_entry_dict['activity_file_ext'][:min(idc)]
                    current_entry_dict['http_version'] = request[2] if len(request) > 2 else '-'

                    current_entry_dict['status'] = int(log['status'])
                    current_entry_dict['bytes_of_response'] = int(log['bytes_of_response'])
                    current_entry_dict['referer'] = log['referer']
                    current_entry_dict['user_agent'] = log['user_agent']

                    # classify potential dangerous referers
                    current_entry_dict['suspicious_referer'] = False
                    for referer in self.__suspicious_referers:
                        if log['referer'].lower().find(referer.lower()) != -1:
                            current_entry_dict['suspicious_referer'] = True
                            break
                    # classify potential malicious bots
                    current_entry_dict['suspicious_agent'] = False
                    for agent in self.__suspicious_agents:
                        if log['user_agent'].lower().find(agent.lower()) != -1:
                            current_entry_dict['suspicious_agent'] = True
                            break
                    # classify potential injection attempts
                    current_entry_dict['reserved_words'] = False
                    for word in self.__reserved_words: 
                        if current_entry_dict['activity'].lower().find(word.lower()) != -1:
                            current_entry_dict['reserved_words'] = True
                            break
                    #current_entry_dict['err_status'] = current_entry_dict['status'] in self.__err_statuses
                    current_entry_dict['err_status'] = current_entry_dict['status'] >= 400 and current_entry_dict['status'] < 500
                    # detect potential disguising of reserved words
                    current_entry_dict['prec_sign_count'] = current_entry_dict['activity'].count('%')

                    current_entry_dict['session_request_count'] = 0
                    current_entry_dict['session_request_count_per_second'] = 0
                    current_entry_dict['session_same_count'] = 0

                    session_df = session_df.append(current_entry_dict, ignore_index=True)

                session_time = (max_session_time-min_session_time).total_seconds()
                request_count_column = [session_df.shape[0]] * session_df.shape[0]
                request_count_column_per_second = [count/session_time if session_time else 0.0 for count in request_count_column]
                session_df.update(pd.DataFrame({'session_request_count': request_count_column}))
                session_df.update(pd.DataFrame({'session_request_count_per_second': request_count_column_per_second}))

                activities_counts = session_df['activity'].value_counts()
                activities_counts_column = [activities_counts[row['activity']] for index, row in session_df.iterrows()]
                session_df.update(pd.DataFrame({'session_same_count': activities_counts_column}))

                MLdf = MLdf.append(session_df)

        return MLdf


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