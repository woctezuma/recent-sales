# Objective: visualize distributions of games *recently* released

import time
import datetime
import numpy as np
import matplotlib.pyplot as plt

from download_json import downloadSteamSpyData

json_filename_suffixe = "_steamspy.json"

## Download current data

# Get current day as yyyymmdd format
date_format = "%Y%m%d"
current_date = time.strftime(date_format)

# Database filename
json_filename = current_date + json_filename_suffixe

# SteamSpy's data in JSON format
data = downloadSteamSpyData(json_filename)

num_games = len(data.keys())
print("#games = %d" % num_games)

## Retrieve previous data

previous_date = "20170726"
previous_json_filename = previous_date + json_filename_suffixe
previous_data = downloadSteamSpyData(previous_json_filename)

num_games = len(previous_data.keys())
print("#games = %d" % num_games)

a = datetime.datetime.strptime(previous_date, date_format)
b = datetime.datetime.strptime(current_date, date_format)
delta = b - a
print("#days = %d" % delta.days)

## Compute the difference between the two databases

added_appids = set(data.keys()) - set(previous_data.keys())

added_data = dict()
for appid in added_appids:
    added_data[appid] = data[appid]
print(added_data)

num_games = len(added_data.keys())
print("#games = %d" % num_games)

## Visualize

## Recent releases
database = added_data
title_suffixe = " released in the past " + str(delta.days) + " days"
## Whole catalog
# database = data
# title_suffixe = ""

## Price
feature_title = "Price"
xtitle = feature_title + " (in USD)"
feature_name = feature_title.lower()
upper_bound = 70
transform = lambda x: float(x)/100
bin_list = [0.5+i for i in range(0,upper_bound)]
major_tick_value = 10
minor_tick_value = 5
## Steam score
# feature_title = "Steam Score"
# xtitle = feature_title
# feature_name = "score_rank"
# upper_bound = 100
# transform = lambda x: float(x)
# bin_list = 20
# major_tick_value = 10
# minor_tick_value = 5
## Number of players
# feature_title = "#players"
# xtitle = feature_title
# feature_name = "players_forever"
# upper_bound = 25000
# transform = lambda x: int(x)
# bin_list = range(0, upper_bound, int(upper_bound/25))
# major_tick_value = 5000
# minor_tick_value = 1000
## Revenue
feature_title = "Revenue"
xtitle = feature_title + " (in USD)"
feature_name = "owners"
upper_bound = 100000
transform = lambda x: float(x)
bin_list = range(0, upper_bound, 1000)
major_tick_value = 5000
minor_tick_value = 1000
## Average playtime
# feature_title = "Average playtime"
# xtitle = feature_title + " (in hours)"
# feature_name = "average_forever"
# upper_bound = 100
# transform = lambda x: float(x)/60
# bin_list = 100
# major_tick_value = 20
# minor_tick_value = 5
## Cumulated playtime
# feature_title = "Cumulated playtime"
# xtitle = feature_title + " (in years)"
# feature_name = "average_forever"
# upper_bound = 2000
# transform = lambda x: float(x)/60/24/365.25
# bin_list = 20000
# major_tick_value = 500
# minor_tick_value = 100

x = []
dico = dict()
for appid in database.keys():
    feature_value = database[appid][feature_name]
    try:
        formatted_feature_value = transform(feature_value)
        if feature_title == "Revenue":
            formatted_feature_value *= float(database[appid]["price"])/100
        if feature_title == "Cumulated playtime":
            formatted_feature_value *= float(database[appid]["players_forever"])
            formatted_feature_value = int(formatted_feature_value)
        x.append(formatted_feature_value)
        dico[appid] = formatted_feature_value
    except:
        continue

sorted_appids = sorted(dico, key=lambda x: dico[x], reverse=True)
counter = 1
for k in sorted_appids[:10]:
    # print(k + "\t" + database[k]["name"] + "\t" + str(dico[k]))
    print(database[k]["name"])
    counter += 1

fig, ax = plt.subplots()

# the histogram of the data
n, bins, patches = ax.hist(x, bin_list, normed=1, facecolor='g', alpha=0.75)
print(sum(n))

plt.xlabel(xtitle)
plt.ylabel('Probability')
plt.title(feature_title + " histogram of games" + title_suffixe)
# plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
plt.axis([0, upper_bound, 0, max(n)*1.01])

# Reference: https://stackoverflow.com/a/24953575
major_ticks = np.arange(0, 1+upper_bound, major_tick_value)
minor_ticks = np.arange(0, 1+upper_bound, minor_tick_value)
ax.set_xticks(major_ticks)
ax.set_xticks(minor_ticks, minor=True)
plt.grid(which='minor', alpha=0.2)
plt.grid(which='major', alpha=0.5)

plt.show()

