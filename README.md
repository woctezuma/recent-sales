# Data visualization for recently released Steam games

[![Build status][build-image]][build]
[![Code coverage][codecov-image]][codecov]
[![Code Quality][codacy-image]][codacy]

This repository contains the following code:
-   [`main.py`](main.py) to compute & visualize histograms for recently released Steam games,
-   [`list_daily_releases.py`](list_daily_releases.py) to evaluate [sales and revenue](output.txt) generated by games during release week.

## Requirements

-   Install the latest version of [Python 3.X](https://www.python.org/downloads/).

-   Install the required packages:

```bash
pip install -r requirements.txt
```

-   Download SteamSpy's data **everyday** for while. To do so, set up an automated task to run the following daily:

```python
import steamspypi

steamspypi.load()
```

## Usage

Examples of input data, downloaded from beginning of October to end of December 2017, is available [in this repository](https://github.com/woctezuma/recent-sales-data).

Output includes distribution of:
-   revenue (product of price and number of players),
-   price,
-   number of players,
-   user score,
-   average playtime,
-   cumulated playtime (for all players).

![revenue](https://i.imgur.com/h14Zr9W.png)

![price](https://i.imgur.com/iNZBAio.png)

![number of players](https://i.imgur.com/L7Wme1D.png)

![user score](https://i.imgur.com/ikhiOSt.png)

![average playtime](https://i.imgur.com/NYTMqGH.png)

## The most profitable games of all-time

1.    Grand Theft Auto V
2.    Counter-Strike: Global Offensive
3.    Left 4 Dead 2
4.    PLAYERUNKNOWN'S BATTLEGROUNDS
5.    ARK: Survival Evolved
6.    Counter-Strike: Source
7.    Sid Meier's Civilization V
8.    The Elder Scrolls V: Skyrim
9.    Portal 2
10.   Call of Duty: Black Ops II

NB: This does not take into account F2P games, as the revenue is based on the game price listed on the Steam store.

## The most profitable games, among these released in the past 48 days

1.    F1 2017
2.    Car Mechanic Simulator 2018
3.    Foxhole
4.    Sine Mora EX
5.    Citadel: Forged with Fire
6.    Interplanetary: Enhanced Edition
7.    Fate/EXTELLA
8.    Halcyon 6: Lightspeed Edition
9.    Quake Champions
10.   West of Loathing
11.   The Legend of Heroes: Trails of Cold Steel
12.   \>observer_
13.   Super ComboMan: Smash Edition
14.   Battlestar Galactica Deadlock
15.   Startup Company
 
NB: Games with "Enhanced Edition" or "Lightspeed Edition" are likely remastered versions of older games, so they might not be the most profitable in practice. Indeed, their userbase likely consists of owners of the older game, which have been freely upgraded to the new game and artificially inflates the revenue computed on this page.

## References

-   Steam Blog post: ["Top Steam Releases of April 2019"](https://steamcommunity.com/games/593110/announcements/detail/2565275416677184326)
-   Steam Blog post: ["Data Deep Dive: How are new releases on Steam performing?"](https://steamcommunity.com/groups/steamworks/announcements/detail/2117195691992645419)
-   Steam Research appendix: ["Research notes: What we studied and why"](https://partner.steamgames.com/doc/blog/2020/new_releases)

<!-- Definitions -->

[build]: <https://travis-ci.org/woctezuma/recent-sales>
[build-image]: <https://travis-ci.org/woctezuma/recent-sales.svg?branch=master>

[pyup]: <https://pyup.io/repos/github/woctezuma/recent-sales/>
[dependency-image]: <https://pyup.io/repos/github/woctezuma/recent-sales/shield.svg>
[python3-image]: <https://pyup.io/repos/github/woctezuma/recent-sales/python-3-shield.svg>

[codecov]: <https://codecov.io/gh/woctezuma/recent-sales>
[codecov-image]: <https://codecov.io/gh/woctezuma/recent-sales/branch/master/graph/badge.svg>

[codacy]: <https://www.codacy.com/app/woctezuma/recent-sales>
[codacy-image]: <https://api.codacy.com/project/badge/Grade/9f6e0b8724f74ce890b2216bc53aa5a9>
