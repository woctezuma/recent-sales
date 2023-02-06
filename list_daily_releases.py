# Objective: list game releases ; for each game, analyze the sales during the first week after release

import ast
import pathlib


def load_json_data(json_filename):
    # Load the content of a JSON data file

    import json

    # Data folder
    data_path = "data/"

    if not (json_filename.endswith(".json")):
        # Assume the filename is wrong and the user provided only the date instead
        date = json_filename

        json_filename_suffixe = "_steamspy.json"
        json_filename = date + json_filename_suffixe

    data_filename = data_path + json_filename

    try:
        with open(data_filename, encoding="utf8") as in_json_file:
            data = json.load(in_json_file)
    except FileNotFoundError:
        print("File not found:\t" + data_filename)
        data = {}

    return data


def list_files(folder_path):
    # List all the files found in a directory

    # Reference: https://stackoverflow.com/a/41447012
    only_files = [f.parts[-1] for f in pathlib.Path(folder_path).glob('*.json')]

    return only_files


def get_mid_of_interval(interval_as_str):
    # Code copied from get_mid_of_interval() in create_dict_using_json.py in hidden-gems repository.
    interval_as_str_formatted = [
        s.replace(',', '') for s in interval_as_str.split('..')
    ]
    lower_bound = float(interval_as_str_formatted[0])
    upper_bound = float(interval_as_str_formatted[1])
    mid_value = (lower_bound + upper_bound) / 2

    return mid_value


def create_appid_dictionary(dict_filename, data_path="data/"):
    # Create a dictionary: appid -> [ release day, number of owners on release day, price, name of the game ]

    try:
        # Load the appID dictionary
        with open(dict_filename, encoding="utf8") as infile:
            lines = infile.readlines()
            # The dictionary is on the second line
            # noinspection PyPep8Naming
            D = ast.literal_eval(lines[1])
    except FileNotFoundError:
        # Write the appID dictionary if it does not exist yet

        only_files = list_files(data_path)

        # Sort by chronological order (due to file nomenclature)
        sorted_files = sorted(only_files)

        # noinspection PyPep8Naming
        D = {}
        encountered_app_id_so_far = []

        # Loop over days (one file corresponds to one day)
        for data_filename in sorted_files:
            print(data_filename)

            # Assume data_filename looks like:  "20171130_steamspy.json"
            release_day = data_filename.split('_')[0]

            # SteamSpy's data in JSON format
            data = load_json_data(data_filename)

            # Compute the difference between the two databases
            added_appids = set(data.keys()) - set(encountered_app_id_so_far)

            num_games = len(added_appids)
            print("#games = %d" % num_games)

            for appid in added_appids:
                encountered_app_id_so_far.append(appid)

                num_owners_value = data[appid]['owners']
                try:
                    num_owners = float(num_owners_value)
                except ValueError:
                    num_owners = get_mid_of_interval(num_owners_value)

                try:
                    price_in_cents = int(data[appid]['price'])
                except TypeError:
                    print(data[appid]['name'] + " has no set price.")
                    continue

                game_name = data[appid]['name']

                D[appid] = [release_day, num_owners, price_in_cents, game_name]

        # First line of the text file containing the output dictionary
        leading_comment = (
            "# Dictionary with key=appid and "
            "value=list of release day, #owners, price in cents, game name"
        )

        # Save the dictionary to a text file
        with open(dict_filename, 'w', encoding="utf8") as outfile:
            print(leading_comment, file=outfile)
            print(D, file=outfile)

    return D


# noinspection PyPep8Naming
def filter_dictionary(D, start_date_str, end_date_str, date_format="%Y%m%d"):
    # Keep every appID which was released in the time window [start_date, end_date] ; remove all the other appIDs

    import datetime

    start_date = datetime.datetime.strptime(start_date_str, date_format)
    end_date = datetime.datetime.strptime(end_date_str, date_format)

    # noinspection PyPep8Naming
    filtered_D = {}

    for appID in D:
        date_str = D[appID][0]
        date = datetime.datetime.strptime(date_str, date_format)

        delta_start = date - start_date
        delta_end = end_date - date
        if (delta_start.days >= 0) and (delta_end.days >= 0):
            filtered_D[appID] = D[appID]

    return filtered_D


# noinspection PyPep8Naming
def reverse_dictionary(D):
    # Input dictionary: appid -> [ release day, number of owners on release day, price, name of the game ]
    # Output dictionary: release day -> [ list of appID released on that day ]

    # noinspection PyPep8Naming
    reversed_D = {}

    encountered_game_names_so_far = []

    for appID in D:
        date_str = D[appID][0]

        # Remove duplicate entries (two different appID but actually the same game:
        # "Call of Duty: WWII" is both "476600" and "476620"
        game_name = D[appID][-1]

        if game_name not in encountered_game_names_so_far:
            encountered_game_names_so_far.append(game_name)
            try:
                reversed_D[date_str].append(appID)
            except KeyError:
                reversed_D[date_str] = [appID]
        else:
            print("Duplicate " + game_name + " removed.")

    return reversed_D


def find_later_day(current_day_str, delta_in_days, date_format="%Y%m%d"):
    # Compute the day coresponding to the current day plus a number delta of days

    import datetime

    current_day = datetime.datetime.strptime(current_day_str, date_format)

    later_day = current_day + datetime.timedelta(delta_in_days)

    later_day_str = later_day.strftime(date_format)

    return later_day_str


# noinspection PyPep8Naming
def create_appid_late_dictionary(D, delta_in_days=7):
    # Input dictionary: appid -> [ release day, number of owners on release day, price, name of the game ]
    # Input number of days elapsed before checking the new number of owners
    #
    # Output dictionary: appid -> [ the date which is delta days after release,
    #                               number of owners after delta days have elapsed,
    #                               price after delta days have elapsed ]

    reversed_D = reverse_dictionary(D)

    late_D = {}

    for day in reversed_D:
        late_day = find_later_day(day, delta_in_days)

        data = load_json_data(late_day)

        for appID in reversed_D[day]:
            try:
                num_owners = int(data[appID]['owners'])
                price_in_cents = int(data[appID]['price'])
            except KeyError:
                continue

            late_D[appID] = [late_day, num_owners, price_in_cents]

    return late_D


# noinspection PyPep8Naming
def compute_revenue_dictionary(D, late_D, remove_F2P=False):
    # Given two dictionaries obtained on different days, return a dictionary: appid -> a list of
    # - the number of people who purchased the game between the two snapshots,
    # - the revenue (price times the #units sold),
    # - and then the name of the game.

    original_app_id = set(D.keys())
    late_app_id = set(late_D.keys())
    consistent_app_id = original_app_id.intersection(late_app_id)

    # noinspection PyPep8Naming
    revenue_D = {}

    for appID in consistent_app_id:
        previous_num_owners = int(D[appID][1])
        new_num_owners = int(late_D[appID][1])
        num_units_sold = new_num_owners - previous_num_owners

        previous_price = int(D[appID][2])
        new_price = int(late_D[appID][2])
        average_price = (previous_price + new_price) / 2.0
        revenue = average_price * num_units_sold

        game_name = D[appID][-1]

        revenue_D[appID] = [num_units_sold, revenue, game_name]

    # Remove F2P games
    if remove_F2P:
        for appID in list(filter(lambda x: revenue_D[x][1] <= 0, revenue_D.keys())):
            revenue_D.pop(appID)

    return revenue_D


# noinspection PyPep8Naming
def display_ranking(revenue_D, delta_in_days, num_ranks_to_show=15):
    # Show rankings of most sold and most profitable games

    ranking_by_sold_units = sorted(
        revenue_D.keys(),
        key=lambda x: revenue_D[x][0],
        reverse=True,
    )
    ranking_by_revenue = sorted(
        revenue_D.keys(),
        key=lambda x: revenue_D[x][1],
        reverse=True,
    )

    print(
        "\nMost sold units over the first "
        + str(delta_in_days)
        + " days following their release:",
    )
    for i in range(min(num_ranks_to_show, len(ranking_by_sold_units))):
        app_id = ranking_by_sold_units[i]
        try:
            print(
                f'{i + 1:02}'
                + ".\tappID: "
                + app_id
                + "\tsold units: "
                + f'{revenue_D[app_id][0]:7}'
                + "\trevenue: "
                + f'{int(revenue_D[app_id][1] / 100 / 1000):5}'
                + "k€\t"
                + revenue_D[app_id][-1],
            )
        except KeyError:
            print("Missing data for " + app_id)

    print(
        "\nMost profitable games over the first "
        + str(delta_in_days)
        + " days following their release:",
    )
    for i in range(min(num_ranks_to_show, len(ranking_by_revenue))):
        app_id = ranking_by_revenue[i]
        try:
            print(
                f'{i + 1:02}'
                + ".\tappID: "
                + app_id
                + "\tsold units: "
                + f'{revenue_D[app_id][0]:7}'
                + "\trevenue: "
                + f'{int(revenue_D[app_id][1] / 100 / 1000):5}'
                + "k€\t"
                + revenue_D[app_id][-1],
            )
        except KeyError:
            print("Missing data for " + app_id)


def main(chosen_date='20180101'):
    import datetime

    dict_filename = "dict_appid.txt"

    # noinspection PyPep8Naming
    D = create_appid_dictionary(dict_filename)

    date_format = "%Y%m%d"

    # We consider all the games released on a time window of 30 days
    time_window_duration = 90

    # We will compute revenue earned during the first 10 days of release
    delta_in_days = 7

    date_days_ago = datetime.datetime.strptime(
        chosen_date,
        date_format,
    ) - datetime.timedelta(time_window_duration + delta_in_days)
    # Any date prior to the following date is not reliable: games released in August will appear to be released
    # on 20170912 because I started to regularly sample from SteamSpy only then.
    hard_date_threshold_str = '20170914'
    hard_date_threshold = datetime.datetime.strptime(
        hard_date_threshold_str,
        date_format,
    )
    check_delta = hard_date_threshold - date_days_ago
    if check_delta.days > 0:
        date_days_ago = hard_date_threshold
    # Conversion to string
    date_days_ago_str = date_days_ago.strftime(date_format)

    # noinspection PyPep8Naming
    D = filter_dictionary(D, date_days_ago_str, chosen_date)

    # noinspection PyPep8Naming
    late_D = create_appid_late_dictionary(D, delta_in_days)

    # noinspection PyPep8Naming
    remove_F2P = True
    # noinspection PyPep8Naming
    revenue_D = compute_revenue_dictionary(D, late_D, remove_F2P)

    num_ranks_to_show = 50
    display_ranking(revenue_D, delta_in_days, num_ranks_to_show)

    return True


if __name__ == "__main__":
    main()
