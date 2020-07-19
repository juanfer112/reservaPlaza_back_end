from datetime import datetime, timedelta

class ConvertDate():
    def stringToDate(self):
        return datetime.strptime(self, '%Y-%m-%d %H:%M:%S')
    
    def fixedTimeZoneCurrentTime():
        return datetime.now().replace(microsecond=0) + timedelta(hours=2)