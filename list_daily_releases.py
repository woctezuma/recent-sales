# Objective: list game releases ; for each game, analyze the sales during the first week after release

#
# input : période de temps
# filter D pour ne garder que les jeux parus durant cette période
# construire temporairement le dico jour => [liste des appid sorties]
# déterminer J+7 et construire temporairement
# 	dico appid => [jour J+7, possesseurs à J+7, prix]
# calculer classemnt des ventes (possesseurs J+7 - possesseurs J) et revenus sur la période

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
        data = None

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

                price_in_cents = data[appid]['price']

                D[appid] = [release_day, num_owners, price_in_cents]

        # First line of the text file containing the output dictionary
        leading_comment = "# Dictionary with key=appid and value=list of release day, #owners, price in cents"

        # Save the dictionary to a text file
        with open(dict_filename, 'w', encoding="utf8") as outfile:
            print(leading_comment, file=outfile)
            print(D, file=outfile)

    return D

if __name__ == "__main__":
    import time

    # Get current day as yyyymmdd format
    date_format = "%Y%m%d"
    current_date = time.strftime(date_format)

    dict_filename = "dict_appid.txt"

    D = createAppidDictionary(dict_filename)

    print(D)
