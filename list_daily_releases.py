# Objective: list game releases ; for each game, analyze the sales during the first week after release

def loadJsonData(json_filename):
    # Load the content of a JSON data file

    import json

    # Data folder
    data_path = "data/"

    if not(json_filename.endswith(".json")):
        # Assume the filename is wrong and the user provided only the date instead
        date = json_filename

        json_filename_suffixe = "_steamspy.json"
        json_filename = date + json_filename_suffixe

    data_filename = data_path + json_filename

    try:
        with open(data_filename, 'r', encoding="utf8") as in_json_file:
            data = json.load(in_json_file)
    except FileNotFoundError:
        print("File not found:\t" + data_filename)
        data = dict()

    return data

def listFiles(folder_path):
    # List all the files found in a directory

    # Reference: https://stackoverflow.com/a/3207973
    from os import listdir
    from os.path import isfile, join
    only_files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]

    return only_files

def createAppidDictionary(dict_filename, data_path ="data/"):
    # Create a dictionary: appid -> [ release day, number of owners on release day, price ]

    try:
        # Load the appID dictionary
        with open(dict_filename, 'r', encoding="utf8") as infile:
            lines = infile.readlines()
            # The dictionary is on the second line
            D = eval(lines[1])
    except FileNotFoundError:
        # Write the appID dictionary if it does not exist yet

        only_files = listFiles(data_path)

        # Sort by chronological order (due to file nomenclature)
        sorted_files = sorted(only_files)

        D = dict()

        # Loop over days (one file corresponds to one day)
        for data_filename in sorted_files:
            print(data_filename)

            # Assume data_filename looks like:  "20171130_steamspy.json"
            release_day = data_filename.split('_')[0]

            # SteamSpy's data in JSON format
            data = loadJsonData(data_filename)

            # Compute the difference between the two databases
            added_appids = set(data.keys()) - set(D.keys())

            num_games = len(added_appids)
            print("#games = %d" % num_games)

            for appid in added_appids:
                num_owners = int(data[appid]['owners'])

                price_in_cents = int(data[appid]['price'])

                D[appid] = [release_day, num_owners, price_in_cents]

        # First line of the text file containing the output dictionary
        leading_comment = "# Dictionary with key=appid and value=list of release day, #owners, price in cents"

        # Save the dictionary to a text file
        with open(dict_filename, 'w', encoding="utf8") as outfile:
            print(leading_comment, file=outfile)
            print(D, file=outfile)

    return D

def filterDictionary(D, start_date_str, end_date_str, date_format = "%Y%m%d"):
    # Keep every appID which was released in the time window [start_date, end_date] ; remove all the other appIDs

    import datetime

    start_date = datetime.datetime.strptime(start_date_str, date_format)
    end_date = datetime.datetime.strptime(end_date_str, date_format)

    filtered_D = dict()

    for appID in D.keys():
        date_str = D[appID][0]
        date = datetime.datetime.strptime(date_str, date_format)

        delta_start = date - start_date
        delta_end = end_date - date
        if (delta_start.days>=0) and (delta_end.days>=0):
            filtered_D[appID] = D[appID]

    return filtered_D

def reverseDictionary(D):
    # Input dictionary: appid -> [ release day, number of owners on release day, price ]
    # Output dictionary: release day -> [ list of appID released on that day ]

    reversed_D = dict()

    for appID in D.keys():
        date_str = D[appID][0]
        try:
            reversed_D[date_str].append(appID)
        except KeyError:
            reversed_D[date_str] = [ appID ]

    return reversed_D

def findLaterDay(current_day_str, delta_in_days, date_format = "%Y%m%d"):
    # Compute the day coresponding to the current day plus a number delta of days

    import datetime

    current_day = datetime.datetime.strptime(current_day_str, date_format)

    later_day = current_day + datetime.timedelta(delta_in_days)

    later_day_str = later_day.strftime(date_format)

    return later_day_str

def createAppidLateDictionary(D, delta_in_days = 7, data_path ="data/"):
    # Input dictionary: appid -> [ release day, number of owners on release day, price ]
    # Input number of days elapsed before checking the new number of owners
    #
    # Output dictionary: appid -> [ the date which is delta days after release,
    #                               number of owners after delta days have elapsed,
    #                               price after delta days have elapsed ]

    reversed_D = reverseDictionary(D)

    late_D = dict()

    for day in reversed_D.keys():
        late_day = findLaterDay(day, delta_in_days)

        data = loadJsonData(late_day)

        for appID in reversed_D[day]:
            try:
                num_owners = int( data[appID]['owners'] )
                price_in_cents = int( data[appID]['price'] )
            except KeyError:
                continue

            late_D[appID] = [late_day, num_owners, price_in_cents]

    return late_D


def computeRevenueDictionary(D, late_D):
    # Given two dictionaries obtained on different days, return a dictionary: appid -> a list of
    # - the number of people who purchased the game between the two snapshots,
    # - and then the revenue (price times the #units sold).

    original_appID = set(D.keys())
    late_appID = set(late_D.keys())
    consistent_appID = original_appID.intersection( late_appID )

    revenue_D = dict()

    for appID in consistent_appID:
        previous_num_owners = int(D[appID][1])
        new_num_owners = int(late_D[appID][1])
        num_units_sold = new_num_owners - previous_num_owners

        previous_price = int(D[appID][2])
        new_price = int(late_D[appID][2])
        average_price = (previous_price+new_price)/2.0
        revenue = average_price * num_units_sold

        revenue_D[appID] = [num_units_sold, revenue]

    return revenue_D

if __name__ == "__main__":
    import time
    import datetime

    dict_filename = "dict_appid.txt"

    D = createAppidDictionary(dict_filename)

    # Get current day as yyyymmdd format
    date_format = "%Y%m%d"
    current_date = time.strftime(date_format)

    # We consider all the games released on a time window of 30 days
    time_window_duration = 30

    # We will compute revenue earned during the first 10 days of release
    delta_in_days = 10

    date_days_ago = datetime.datetime.strptime(current_date, date_format) - datetime.timedelta(time_window_duration+delta_in_days)
    date_days_ago_str = date_days_ago.strftime(date_format)

    D = filterDictionary(D, date_days_ago_str, current_date)

    late_D = createAppidLateDictionary(D)

    revenue_D = computeRevenueDictionary(D, late_D)

    print(revenue_D)
