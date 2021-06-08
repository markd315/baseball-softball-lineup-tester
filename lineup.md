This is a python application.

To modify the test lineup, edit lineup.csv in Excel or a text software like notepad/sublime.

the order to specify each stat is shown in the top row
`name,ba,obp,slg,sbPerc,csPerc`

Please include exactly 9 players in the lineup (for now)

ba/obp/slg are the primary hitting stats. If a player has a lot of walks, they will have a OBP much higher than their BA.

If he has a lot of doubles and home runs, their slg will be much higher than their ba.

To change settings like the number of innings, or the base stats for the simulation, tweak lines 7-21 of the `lineup.py` file.

To run it, run
```
python lineup.py
```

Lineup construction tips:

1) Better hitters can hit more often by being near the top of the order. This will score you more 
runs in general.

2) Hitters that draw a lot of walks and/or steals are better off being near the top of the order as well.

3) Hitters that get a lot of multi-base hits are better off being near the 3 and 4 spots of your order.

4) A point of OBP for a hitter is always better than a point of SLG. However, this is slot dependent. OBP is most valuable for the leadoff hitter, and SLG is most important for the cleanu slots 3-4.

Example:

For the players in the example `lineup.csv` they are in optimal spots, scoring about 5.0 RPG.

The position of the feast-or-famine slugger does not seem to be particularly important, since their contributions in slugging are cancelled out by a lower average.

Moving the cleanup to third in the order does not seem to change the outcome much either.

You could, of course, make some awful mistakes with this lineup.
Switching the weak hitter with the ideal leadoff sacrifices almost 0.15 runs per game.
Switching the weak hitter with the cleanup sacrifices about 0.13 runs per game.

That's not what you want. Making those egregious lineup errors would singlehandedly cost you about 1.5% of all your games if you had league-average defense.