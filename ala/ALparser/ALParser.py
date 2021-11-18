import re

class ApacheLogParser:
    logLineRegex = '([(\d\.)]+) ([\w-]+) ([\w-]+) \[(.*?)\] "(.*?)" (\d+) ([\d-]+) "(.*?)" "(.*?)"\n?'
    __logs = []

    def parseLine(self, logLine):
        matched = re.fullmatch(self.logLineRegex, logLine)
        if matched:
            self.__logs.append({'raw': logLine, 'host': matched[1], 'logname': matched[2], 'user': matched[3], 'time': matched[4], 'request': matched[5], 'status': matched[6], 'bytes_of_response': matched[7], 'referer': matched[8], 'user_agent': matched[9]})

    def process(self):
        self.normalize()
        self.categorize()
        self.enrich()
    
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