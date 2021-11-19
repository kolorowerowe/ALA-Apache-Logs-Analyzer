import re
import pandas as pd
import datetime

class ApacheLogParser:
    NCSAExtendedCombinedLogFormatRegex = '([(\d\.)]+) "?([\w-]+)"? "?([\w-]+)"? \[(.*?)\] "(.*?)" (\d+) ([\d-]+) "(.*?)" "(.*?)"\n?'
    __logs = []

    def parseLine(self, logLine):
        matched = re.fullmatch(self.NCSAExtendedCombinedLogFormatRegex, logLine)
        if matched:
            if self.areLogsDF():
                self.addLogLineToDF(matched, logLine)
            else:
                self.addLogLineToList(matched, logLine)

    def process(self):
        self.__logs = pd.DataFrame(self.__logs)
        sessions = self.normalize()
        if not sessions:
            raise RuntimeError('Normalization impossible, logs may be empty.')
        self.categorize()
        self.enrich()

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


    def categorize(self):
        pass

    def enrich(self):
        pass

    def differMoreThanHour(self, date1, date2):
        struct_date_1 = datetime.datetime.strptime(date1, "%d/%B/%Y:%H:%M:%S +0000")
        struct_date_2 = datetime.datetime.strptime(date2, "%d/%B/%Y:%H:%M:%S +0000")
        return struct_date_1 + datetime.timedelta(hours=1) < struct_date_2

    def getParsedLine(self, index):
        if self.areLogsDF():
            return self.__logs.iloc[index]
        return self.__logs[index]

    def getMLFormattedLogs(self):
        pass

    def getVisualizationFormattedLogs(self):
        pass

    @property
    def logs(self):  
        return self.__logs