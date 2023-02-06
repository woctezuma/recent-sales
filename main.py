# Objective: visualize distributions of games *recently* released

import datetime
import pathlib
import time

import numpy as np
import steamspypi

from list_daily_releases import get_mid_of_interval


def get_data_path():
    # Data folder
    data_path = "data/"
    # Reference of the following line: https://stackoverflow.com/a/14364249
    pathlib.Path(data_path).mkdir(parents=True, exist_ok=True)

    return data_path


def get_json_filename_suffixe():
    json_filename_suffixe = "_steamspy.json"
    return json_filename_suffixe


def get_current_data(date_format='%Y%m%d'):
    # Download current data

    # Get current day as yyyymmdd format
    current_date = time.strftime(date_format)

    # Database filename
    json_filename = current_date + get_json_filename_suffixe()

    # SteamSpy's data in JSON format
    data = steamspypi.load(get_data_path() + json_filename)

    num_games = len(data.keys())
    print("[today] #games = %d" % num_games)

    return data


def get_previous_data(date_format='%Y%m%d', previous_date='20170726'):
    # Retrieve previous data

    previous_json_filename = previous_date + get_json_filename_suffixe()
    previous_data = steamspypi.load(get_data_path() + previous_json_filename)

    num_games = len(previous_data.keys())
    print("[previously] #games = %d" % num_games)

    # Get current day as yyyymmdd format
    current_date = time.strftime(date_format)

    a = datetime.datetime.strptime(previous_date, date_format)
    b = datetime.datetime.strptime(current_date, date_format)
    delta = b - a
    print("[previously] #days = %d" % delta.days)

    return previous_data, delta


def get_new_releases(data, previous_data, verbose=False):
    # Compute the difference between the two databases

    added_appids = set(data.keys()) - set(previous_data.keys())

    added_data = dict()
    for appid in added_appids:
        added_data[appid] = data[appid]
    if verbose:
        print(added_data)

    num_games = len(added_data.keys())
    print("[new releases] #games = %d" % num_games)

    return added_data


def prepare_display(database, dict_parameters):
    # Read parameters from dictionary
    feature_title = dict_parameters['feature_title']

    _ = dict_parameters['xtitle']
    feature_name = dict_parameters['feature_name']

    _ = dict_parameters['upper_bound']
    transform = dict_parameters['transform']

    _ = dict_parameters['bin_list']

    _ = dict_parameters['major_tick_value']

    _ = dict_parameters['minor_tick_value']

    x = []
    dico = dict()
    for appid in database.keys():
        feature_value = database[appid][feature_name]
        try:
            feature_value = float(feature_value)
        except ValueError:
            feature_value = get_mid_of_interval(feature_value)
        formatted_feature_value = transform(feature_value)
        if feature_title == "Revenue":
            try:
                formatted_feature_value *= float(database[appid]["price"]) / 100
            except TypeError:
                formatted_feature_value = -1
        if feature_title == "Cumulated playtime":
            formatted_feature_value *= float(database[appid]["players_forever"])
            formatted_feature_value = int(formatted_feature_value)
        x.append(formatted_feature_value)
        dico[appid] = formatted_feature_value

    print('\nRanking')
    sorted_appids = sorted(dico, key=lambda val: dico[val], reverse=True)
    counter = 1
    for k in sorted_appids[:10]:
        sentence = '{:3}. appID = {:7}\t' + feature_name + ' ={:12.0f}\tname = {}'
        print(sentence.format(counter, k, dico[k], database[k]["name"]))
        counter += 1

    return x


def get_display_parameters(feature_title):
    if feature_title == "Price":
        # Price
        xtitle = feature_title + " (in USD)"
        feature_name = feature_title.lower()
        upper_bound = 70

        def transform(x):
            return float(x) / 100

        bin_list = [0.5 + i for i in range(0, upper_bound)]
        major_tick_value = 10
        minor_tick_value = 5
    elif feature_title == "Steam Score":
        # Steam score
        xtitle = feature_title
        feature_name = "score_rank"
        upper_bound = 100

        def transform(x):
            return float(x)

        bin_list = 20
        major_tick_value = 10
        minor_tick_value = 5
    elif feature_title == "#players":
        # Number of players
        xtitle = feature_title
        feature_name = "players_forever"
        upper_bound = 25000

        def transform(x):
            return int(x)

        bin_list = range(0, upper_bound, int(upper_bound / 25))
        major_tick_value = 5000
        minor_tick_value = 1000
    elif feature_title == "Revenue":
        # Revenue
        xtitle = feature_title + " (in USD)"
        feature_name = "owners"
        upper_bound = 100000

        def transform(x):
            return float(x)

        bin_list = range(0, upper_bound, 1000)
        major_tick_value = 5000
        minor_tick_value = 1000
    elif feature_title == "Average playtime":
        # Average playtime
        xtitle = feature_title + " (in hours)"
        feature_name = "average_forever"
        upper_bound = 100

        def transform(x):
            return float(x) / 60

        bin_list = 100
        major_tick_value = 20
        minor_tick_value = 5
    elif feature_title == "Cumulated playtime":
        # Cumulated playtime
        xtitle = feature_title + " (in years)"
        feature_name = "average_forever"
        upper_bound = 2000

        def transform(x):
            return float(x) / 60 / 24 / 365.25

        bin_list = 20000
        major_tick_value = 500
        minor_tick_value = 100
    else:
        raise NotImplementedError

    dict_parameters = dict()
    dict_parameters['feature_title'] = feature_title
    dict_parameters['xtitle'] = xtitle
    dict_parameters['feature_name'] = feature_name
    dict_parameters['upper_bound'] = upper_bound
    dict_parameters['transform'] = transform
    dict_parameters['bin_list'] = bin_list
    dict_parameters['major_tick_value'] = major_tick_value
    dict_parameters['minor_tick_value'] = minor_tick_value

    return dict_parameters


def display_sales(x, dict_parameters, title_suffixe, no_display_available):
    # Read parameters from dictionary
    feature_title = dict_parameters['feature_title']
    xtitle = dict_parameters['xtitle']
    _ = dict_parameters['feature_name']
    upper_bound = dict_parameters['upper_bound']
    _ = dict_parameters['transform']
    bin_list = dict_parameters['bin_list']
    major_tick_value = dict_parameters['major_tick_value']
    minor_tick_value = dict_parameters['minor_tick_value']

    # Visualize

    if no_display_available:
        import matplotlib

        matplotlib.use('Agg')

    import matplotlib.pyplot as plt

    _, ax = plt.subplots()

    # the histogram of the data
    n, _, _ = ax.hist(x, bin_list, density=True, facecolor='g', alpha=0.75)
    print('\nIntegral = {}'.format(sum(n)))

    plt.xlabel(xtitle)
    plt.ylabel('Probability')
    plt.title(feature_title + " histogram of games" + title_suffixe)
    # plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    try:
        plt.axis([0, upper_bound, 0, max(n) * 1.01])
    except ValueError:
        print('Upper bound = {} ; n = {}'.format(upper_bound, n))

    # Reference: https://stackoverflow.com/a/24953575
    major_ticks = np.arange(0, 1 + upper_bound, major_tick_value)
    minor_ticks = np.arange(0, 1 + upper_bound, minor_tick_value)
    ax.set_xticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)
    plt.grid(which='minor', alpha=0.2)
    plt.grid(which='major', alpha=0.5)

    plt.show()

    return


def main(no_display_available=False):
    only_use_recent_releases = True

    date_format = '%Y%m%d'

    data = get_current_data(date_format)

    if only_use_recent_releases:
        previous_date = '20170726'
        previous_data, delta = get_previous_data(date_format, previous_date)

        added_data = get_new_releases(data, previous_data)

        # Recent releases
        database = added_data
        title_suffixe = " released in the past " + str(delta.days) + " days"
    else:
        # Whole catalog
        database = data
        title_suffixe = ""

    dict_parameters = get_display_parameters(feature_title='Revenue')

    x = prepare_display(database, dict_parameters)

    display_sales(x, dict_parameters, title_suffixe, no_display_available)

    return True


if __name__ == '__main__':
    main()
