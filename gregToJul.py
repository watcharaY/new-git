import re

def gregtojul(request):
    index_leapYear = {
        "01": 0,
        "02": 31,
        "03": 60,
        "04": 91,
        "05": 121,
        "06": 152,
        "07": 182,
        "08": 213,
        "09": 244,
        "10": 274,
        "11": 305,
        "12": 335
    }
    index_nonLeapYear = {
        "01": 0,
        "02": 31,
        "03": 59,
        "04": 90,
        "05": 120,
        "06": 151,
        "07": 181,
        "08": 212,
        "09": 243,
        "10": 273,
        "11": 304,
        "12": 334
    }
    request_json = request.get_json()
    if request.args and 'date' in request.args:
        dte_greg = request.args.get("date")
        if len(dte_greg) == 8 and re.search("[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]", dte_greg) is not None:
            day   = dte_greg[:2]
            month = dte_greg[2:4]
            year  = dte_greg[4:]
            year_jul = year
            if int(year) % 4 == 0: # leapYear
                for index_key, index_value in index_leapYear.items():
                    if month == index_key:
                        day_jul = index_value + int(day)
            else:                  # nonLeapYear
                for index_key, index_value in index_nonLeapYear.items():
                    if month == index_key:
                        day_jul = index_value + int(day)
            dte_jul = year_jul + str(day_jul)
            return dte_jul
        else:
            return "Please send ddmmyyyy to get julian date !"
    elif request_json and 'date' in request_json:
        return request_json['date']
    else:
        return f'Send ddmmyyyy to get julian date !'
