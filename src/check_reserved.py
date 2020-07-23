from date_convert import ConvertDate

class CheckReserved():
    @staticmethod
    def CheckReservedBySpace(oldSchedule, newSchedule):
        return any(oldSchedule['date'] == ConvertDate.stringToDate(newSchedule.date) and oldSchedule['spaceID'] == newSchedule.serialize()['spaceID'] for oldSchedule in allSchedulesInDB)