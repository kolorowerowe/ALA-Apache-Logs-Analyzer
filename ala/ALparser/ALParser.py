import re
import pandas as pd

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
        self.normalize()
        self.categorize()
        self.enrich()

    def areLogsDF(self):
        return isinstance(self.__logs, pd.DataFrame)

    def addLogLineToDF(self, matched, line):
        self.__logs = self.__logs.append({'raw': line, 'host': matched[1], 'logname': matched[2], 'user': matched[3], 'time': matched[4], 'request': matched[5], 'status': matched[6], 'bytes_of_response': matched[7], 'referer': matched[8], 'user_agent': matched[9]},ignore_index=True)
    
    def addLogLineToList(self, matched, line):
        self.__logs.append({'raw': line, 'host': matched[1], 'logname': matched[2], 'user': matched[3], 'time': matched[4], 'request': matched[5], 'status': matched[6], 'bytes_of_response': matched[7], 'referer': matched[8], 'user_agent': matched[9]})
    
    def normalize(self):
        pass

    def categorize(self):
        pass

    def enrich(self):
        pass

    def getParsedLine(self, index):
        return self.__logs[index]

    def getParsedLog(self):
        return self.__logs

    @property
    def logs(self):  
        return self.__logs