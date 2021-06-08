import csv
import sys
import random
import math
#import numpy

innings = 9
statsBase = { #2020 stats https://www.baseball-reference.com/leagues/MLB/bat.shtml
	'pa': 37.03,
	'bb': 3.39,
	'hbp': .46, #treated as a BB by the simulation
	'ba': .245,
	'obp': .322,
	'slg': .418,
	'2b': 1.57,
	'3b': 0.13,
	"4b": 1.28
}
sample = 30000
runsAllowed=4.59 # grabbed median from here https://www.teamrankings.com/mlb/stat/runs-per-game?date=2020-10-28
doublePlayRatioOnOutsWhenRunnerOnFirst=.17 #No source for this. Wild guess.




statsBase['ab'] =statsBase['pa'] - statsBase['hbp'] - statsBase['bb']
statsBase['hits']=statsBase['ab']*statsBase['ba']
onbasect = statsBase['pa'] * statsBase['obp']
statsBase['walkPerc'] = (statsBase['bb']+statsBase['hbp']) / onbasect

class Player:
	def __init__(self,name,ba,obp,slg):
		self.name = name
		self.obp = obp
		self.ba = ba
		self.slg = slg
		self.sb = 0.0
		self.cs = 0.0
	def __init__(self,name,ba,obp,slg,sb,cs):
		self.name = name
		self.obp = obp
		self.ba = ba
		self.slg = slg
		self.sb = sb
		self.cs = cs

def loadSequential():
	with open('lineup.csv', 'r') as csv_file:
		lineup = []
		reader = csv.reader(csv_file)
		firstRow = True
		for row in reader:
			if(firstRow):
				firstRow = False
			else:
				if(len(row) == 4):
					lineup.append(Player(row[0],float(row[1]),float(row[2]),float(row[3])))
				if(len(row) == 6):
					lineup.append(Player(row[0],float(row[1]),float(row[2]),float(row[3]),float(row[4]), float(row[5]) ))
	return lineup

def determineHitType(player):
	#Assumes doubles,triples,HR contribute to slg in same proportions same as in statbase
	averageExtraBases = player.slg - player.ba
	extraBasesScalar = averageExtraBases / (statsBase['slg'] - statsBase['ba'])
	leaguewideDoublesPercent = statsBase['2b'] / statsBase['hits']
	doublesContribution = leaguewideDoublesPercent * extraBasesScalar
	leaguewideTriplesPercent = statsBase['3b'] / statsBase['hits']
	triplesContribution = leaguewideTriplesPercent * extraBasesScalar
	leaguewideHrPercent = statsBase['4b'] / statsBase['hits']
	hrContribution = leaguewideHrPercent * extraBasesScalar

	rng = random.uniform(0,1)
	if(rng > hrContribution + triplesContribution + doublesContribution):
		return "1"
	if(rng > hrContribution + triplesContribution):
		return "2"
	if(rng > hrContribution):
		return "3"
	return "4"

def outcomeFromStats(player):
	rng = random.uniform(0,1)
	if(rng > player.obp):
		return "out"
	rng = random.uniform(0,1)
	if(rng < statsBase['walkPerc']):
		return "walk"
	
	return determineHitType(player)

def stealBase(stealer,baseState):
	if(baseState[0] == 1 and baseState[1] == 0):
		rng = random.uniform(0,1)
		if(rng < stealer.sb):
			baseState[0] = 0
			baseState[1] = 1
			#print(stealer.name + " Stole second")
			res["sb"] +=1
			return False
		if(rng < stealer.sb + stealer.cs):
			baseState[0] = 0
			#print(stealer.name + " Caught stealing")
			res["cs"] +=1
			return True

res = {"1": 0, "2": 0, "3": 0, "4": 0, "out": 0, "walk":0, "sb": 0, "cs": 0, "double play": 0} #for season stats output
def simInning(lineup, orderSlot):
	baseState = [0,0,0]
	runs = 0
	outs = 0
	stealer=None
	while outs < 3:
		caught = stealBase(stealer,baseState)
		if(caught):
			outs+=1
			continue
		player = lineup[orderSlot - 1]
		outcome = outcomeFromStats(player)
		#print(player.name + " at-bat: " + outcome)
		res[outcome] = res[outcome]+1
		if(outcome == "out"):
			outs+=1
			if(baseState[0] == 1 and outs < 3):
				rng = random.uniform(0,1)
				if(rng < doublePlayRatioOnOutsWhenRunnerOnFirst): 
					#print("double play (6-4-3/4-6-3)")
					res["double play"] +=1
					outs+=1
					baseState[0] = 0
		if(outcome == "4"):
			runs+= 1 + baseState[0] + baseState[1] + baseState[2]
			baseState = [0,0,0]
		if(outcome == "3"):
			runs+= baseState[0] + baseState[1] + baseState[2]
			baseState = [0,0,1]
		if(outcome == "2"):
			runs+= baseState[0] + baseState[1] + baseState[2]
			baseState = [0,1,0]
		if(outcome == "1"):
			runs+= baseState[1] + baseState[2]
			baseState[1] = baseState[0] #first to second
			baseState[2] = 0
			baseState[0] = 1
			stealer=player
		if(outcome == "walk"):
			stealer=player
			if(baseState[0] + baseState[1] + baseState[2] == 3): #ld
				runs+=1
			elif(baseState[0] == 1 and baseState[2] == 1): #13
				baseState[1] = 1
			elif(baseState[0] == 1 and baseState[1] == 1): #12
				baseState[2] = 1
			elif(baseState[1] == 1 and baseState[2] == 1): #23
				baseState[0] = 1
			elif(baseState[1] == 1): #1
				baseState[1] = 1
			else: #first empty
				baseState[0] = 1
		orderSlot += 1
		if(orderSlot > 9):
			orderSlot -= 9
	#print("Scored " + str(runs))
	return {"orderSlot": orderSlot, "runs": runs}

def simOffensiveGame(lineup):
	runs=0
	orderSlot=1 # need scoped to game method
	for inn in range(0,innings):
		result=simInning(lineup,orderSlot)
		orderSlot=result["orderSlot"]
		runs+=result["runs"]
	#print("Game over, run count: " + str(runs))
	return runs

def stddev(runDist, avg):
	sumOfSquares = 0
	for runs,occurrences in enumerate(runDist):
		if(occurrences > 0):
			for cnt in range(0,occurrences):
				sumOfSquares += math.pow(runs - avg, 2)
	return math.sqrt(sumOfSquares / (sample - 1))

runDist = []
for create in range(0,100): #100 max runs in a game
	runDist.append(0)

lineup = loadSequential()
total = 0
print("Running " + str(sample) + " simulated games of " + str(innings) + " innings")
for num in range(0,sample):
	runs = simOffensiveGame(lineup)
	runDist[runs] += 1
	total += runs
avg = total/sample
stddev = stddev(runDist,avg)
print("Average runs: " + str(avg) + " stddev " + str(stddev)) 
#numpy.trim_zeros(runDist, trim='fb')
print("Run distribution: ")
for runs,occurrences in enumerate(runDist):
	if(occurrences != 0):
		print(str(runs) + " runs: " + str(occurrences) + " times")
res["hits"]=res["1"]+res["2"]+res["3"]+res["4"]
res["pa"]=res["hits"]+res["out"]+res["walk"]
res["average"]=res["hits"]/(res["hits"] + res["out"])
res["obp"]=(res["hits"]+res["walk"]) / res["pa"]
res["slg"]=(res["1"] + (res["2"]*2) + (res["3"]*3) + (res["4"]*4)) / (res["hits"] + res["out"])
res["ops"]=res["obp"]+res["slg"]
print("Lineup statistics: " + str(res))
winrate = math.pow(avg,2) / (math.pow(avg,2) + math.pow(runsAllowed,2))
print("Expected winrate when defense allows " + str(runsAllowed) + " avg per game " + str(winrate))