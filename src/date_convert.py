from datetime import datetime, timedelta

class ConvertDate():
    @staticmethod
    def stringToDate(string):
        return datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
        
    @staticmethod
    def fixedTimeZoneCurrentTime():
        return datetime.now().replace(microsecond=0) + timedelta(hours=2)