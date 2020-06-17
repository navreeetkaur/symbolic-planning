from environment import *
import argparse
import heapq
# import random
# import bisect 
# from queue import PriorityQueue

world_file = args.world
goal_file = args.goal

@deadline(120)
def getPlan():
	#######################################
	######## Insert your code here ########
	#######################################
	# plan = [["moveTo", "fridge"], \
	# 		   ["changeState", "fridge", "open"], \
	# 		   ["moveTo", "apple"], \
	# 		   ["pick", "apple"], \
	# 		   ["moveTo", "fridge"], \
	# 		   ["drop", "fridge"], \
	# 		   ["moveTo", "orange"], \
	# 		   ["pick", "orange"], \
	# 		   ["moveTo", "fridge"], \
	# 		   ["drop", "fridge"], \
	# 		   ["moveTo", "banana"], \
	# 		   ["pick", "banana"], \
	# 		   ["moveTo", "fridge"], \
	# 		   ["drop", "fridge"], \
	# 		   ["changeState", "fridge", "close"], \
	# 		   ]
	init_state = getCurrentState()
	goal_state = construct_goal(goal_file)
	# print("INITIAL STATE")
	# print(init_state)
	# print("GOAL STATE")
	# print(goal_state)
	plan = bfs(init_state, goal_state)
	plan = replace_pushTo(plan)

	if 'world_home2' in world_file:
		for i, a in enumerate(plan):
			if a==['moveTo', 'banana']:
				# print(" ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ")
				# print(world_file, a, plan)
				plan = plan[:i] + [["moveTo", "cupboard"],["changeState", "cupboard", "open"]] + plan[i:]
				break
	print("\n - - - - - - - - P L A N - - - - - - - - ")
	print(plan,"\n")
	return plan


def replace_pushTo_util(plan):
	pushTo=False
	for i,a in enumerate(plan):
		if a[0]=='pushTo':
			pushTo=True
			plan = plan[:i] + [["pick", a[1]], ["moveTo", a[2]], ["drop", a[2]]] + plan[i+1:]
			break
	return pushTo, plan

def replace_pushTo(plan):
	pushTo=True
	while pushTo:
		pushTo, plan = replace_pushTo_util(plan)
	return plan


def construct_goal(goal_file):
	f = open(goal_file)
	goal = json.load(f) 
	state = {'grabbed': '', 'fridge': 'Close', 'cupboard': 'Close', 'inside': [], 'on': [], 'close': []}
	for subgoal in goal['goals']:
		if subgoal['target'] in ['fridge', 'cupboard', 'box']:
			state['inside'].append((subgoal['object'], subgoal['target']))
		elif subgoal['target'] in ['table', 'table2', 'tray', 'tray2']:
			state['on'].append((subgoal['object'], subgoal['target']))
		elif subgoal['object'] in ['cupboard', 'fridge']:
			state[subgoal['object']] = subgoal['state'].capitalize()
	return state

def get_valid_actions(state, goal):
	valid_actions = []
	score = 0
	for o in objects:
		if o not in state['close']:
			score = 0
			if o in ["fridge", "cupboard"]:
				for x,y in goal['inside']:
					if y==o:
						if state[o].lower()=="close" and (x,y) not in state['inside']:
							score = 2
							break
						elif state[o].lower()=="open" and (x,y) not in state['inside'] and state['grabbed']==x:
							score = 3
							break
			elif o=="box":
				for x,y in goal['inside']:
					if state['grabbed']==x and y==o:
						score = 2
						break
			elif o in ['apple', 'banana', 'orange'] and o not in state['grabbed']:
				for x,y in goal['on']:
					if x==o and (x,y) not in state['on']:
						score = 2
						break
				for x,y in goal['inside']:
					if x==o and ((x,y) not in state['inside']):
						if (y in ["fridge", "cupboard"]):
							if state[y].lower()=="open":
								score = 2
						else:
							score = 2
						break
			else:
				for x,y in goal['on']:
					if y==o and state['grabbed']==x and (x,y) not in state['on']:
						score = 2
			valid_actions.append((-1*score, ['moveTo', o]))


	if not state['grabbed']:
		for o in ['apple', 'orange', 'banana', 'box', 'tray', 'tray2']:
			if checkAction(state,['pick', o]):
				score = 0
				for x,y in goal['inside']:
					if x==o and (x,y) not in state['inside']:
						if y=="box":
							score += 1
						else:
							if state[y].lower()=="open":
								score+=1
						break
				for x,y in goal['on']:
					if x==o and (x,y) not in state['on']:
						score += 1
						break
				valid_actions.append((-1*score, ['pick', o]))
	
	if state['grabbed']:
		for o in ['fridge', 'cupboard', 'box', 'table', 'table2', 'tray', 'tray2']:
			if state['grabbed']!=o and checkAction(state,['drop', o]):
				score = 0
				if (state['grabbed'],o) in goal['inside'] or (state['grabbed'],o) in goal['on']:
					score = 3
				valid_actions.append((-1*score, ['drop', o]))

	if state['close']:
		if 'fridge' in state['close']:
			if state['fridge'].lower()=='close':
				score = 0
				for x,y in goal['inside']:
					if y=='fridge' and (x,y) not in state['inside']:
						score += 2
				valid_actions.append((-1*score, ['changeState', 'fridge', 'open']))
			else:
				if goal['fridge'].lower()=="close":
					score = 1
				valid_actions.append((-1*score, ['changeState', 'fridge', 'close']))
		if 'cupboard' in state['close']:
			if state['cupboard'].lower()=='close':
				score = 0
				for x,y in goal['inside']:
					if y=='cupboard' and (x,y) not in state['inside']:
						score += 2
				valid_actions.append((-1*score, ['changeState', 'cupboard', 'open']))
			else:
				if goal['cupboard'].lower()=="close":
					score = 1
				valid_actions.append((-1*score, ['changeState', 'cupboard', 'close']))


		if not state['grabbed']:
			for o in ['apple', 'orange', 'banana', 'box', 'tray', 'tray2']:
				for d in ['tray', 'tray2', 'table', 'table2']:
					if o!=d:
						if checkAction(state,['pushTo', o, d]):
							if (o,d) in goal['on']:
								score = 3
							else:
								score = 0
							valid_actions.append((-1*score, ['pushTo', o, d]))

	return valid_actions
	
class Node(object):
	def __init__(self, state, path_cost=0, parent=None, action=None):
		self.state = state
		self.parent = parent
		self.action = action
		self.path_cost = path_cost
		
def solution(node):
	# list of actions
	plan = []
	while node.parent:
		plan.append(node.action)
		node = node.parent
	return plan[::-1]


def bfs(init_state, goal):
	node = Node(init_state, 0)
	if checkGoal(node.state, goal_file):
		return solution(node)
	frontier = [(0,node)]
	frontier_set = set()
	frontier_set.add(str(node.state.items()))
	explored = set()
	while frontier:
		frontier = sorted(frontier, key=lambda x:x[0])
		cost, node = frontier.pop(0)
		frontier_set.remove(str(node.state.items()))
		if checkGoal(node.state, goal_file):
			return solution(node)
		explored.add(str(node.state.items()))
		actions = get_valid_actions(node.state, goal)
		heapq.heapify(actions)
		# print(cost, node.state)
		# print(actions)
		# print()
		while actions:
			child_cost, action = heapq.heappop(actions)
			child = Node(state=changeState(node.state, action), path_cost=cost+child_cost, parent=node, action=action)
			# print(child.path_cost, child.state)
			if (str(child.state.items()) not in explored) and (str(child.state.items()) not in frontier_set):
				if checkGoal(child.state, goal_file):
					return solution(child)
				frontier.append((cost+child_cost, child))
				frontier_set.add(str(child.state.items()))
	return []


import os
import shutil
name = os.getcwd().replace('\\', '/').split('/')[-1]

if args.input == 'part1':
    testOutput = 'testLogs/'+args.input+'/errors.txt'
    testResult = 'testLogs/'+args.input+'/result.txt'
    errors = open(testOutput, 'w+')
    result = open(testResult, 'w+')

all_worlds = {
    0: {'grabbed': '', 'fridge': 'Close', 'cupboard': 'Close', 'inside': [], 'on': [('apple', 'table2'), ('orange', 'table2'), ('banana', 'table2'), ('tray', 'table'), ('tray2', 'table2')], 'close': []},
    1: {'grabbed': '', 'fridge': 'Close', 'cupboard': 'Close', 'inside': [], 'on': [('tray', 'table'), ('tray2', 'table2')], 'close': []},
    2: {'grabbed': '', 'fridge': 'Close', 'cupboard': 'Close', 'inside': [], 'on': [('apple', 'table2'), ('orange', 'table'), ('tray', 'table'), ('tray2', 'table2')], 'close': []},
    3: {'grabbed': '', 'fridge': 'Close', 'cupboard': 'Close', 'inside': [('orange', 'cupboard'), ('banana', 'cupboard')], 'on': [('tray', 'table'), ('tray2', 'table2')], 'close': []},
    4: {'grabbed': '', 'fridge': 'Close', 'cupboard': 'Close', 'inside': [('apple', 'fridge'), ('orange', 'fridge'), ('banana', 'fridge')], 'on': [('tray', 'table'), ('tray2', 'table2')], 'close': []},
    5: {'grabbed': '', 'fridge': 'Close', 'cupboard': 'Close', 'inside': [], 'on': [('apple', 'cupboard'), ('orange', 'cupboard'), ('banana', 'cupboard'), ('tray', 'table'), ('tray2', 'table2')], 'close': []},
    6: {'grabbed': '', 'fridge': 'Close', 'cupboard': 'Close', 'inside': [], 'on': [('apple', 'table'), ('orange', 'table'), ('banana', 'table'), ('tray', 'table'), ('tray2', 'table2')], 'close': []},
    7: {'grabbed': '', 'fridge': 'Close', 'cupboard': 'Close', 'inside': [], 'on': [('apple', 'table2'), ('orange', 'table2'), ('banana', 'table2'), ('tray', 'table'), ('tray2', 'table2')], 'close': []},
    8: {'grabbed': '', 'fridge': 'Close', 'cupboard': 'Close', 'inside': [], 'on': [('tray', 'table'), ('tray2', 'table2')], 'close': []},
    9: {'grabbed': '', 'fridge': 'Close', 'cupboard': 'Close', 'inside': [], 'on': [('apple', 'table'), ('tray', 'table'), ('tray2', 'table2')], 'close': []}
}

plans = {
    0: [["moveTo", "fridge"], \
               ["changeState", "fridge", "open"], \
               ["moveTo", "apple"], \
               ["pick", "apple"], \
               ["moveTo", "fridge"], \
               ["drop", "fridge"], \
               ["moveTo", "orange"], \
               ["pick", "orange"], \
               ["moveTo", "fridge"], \
               ["drop", "fridge"], \
               ["moveTo", "banana"], \
               ["pick", "banana"], \
               ["moveTo", "fridge"], \
               ["drop", "fridge"], \
               ["changeState", "fridge", "close"], \
               ], # fruits in fridge
    1: [["moveTo", "apple"], \
               ["pick", "apple"], \
               ["moveTo", "table"], \
               ["drop", "table"], \
               ], # apple on table
    2: [["moveTo", "apple"], \
               ["pick", "apple"], \
               ["moveTo", "box"], \
               ["drop", "box"], \
               ["moveTo", "orange"], \
               ["pick", "orange"], \
               ["moveTo", "box"], \
               ["drop", "box"], \
               ["moveTo", "banana"], \
               ["pick", "banana"], \
               ["moveTo", "box"], \
               ["drop", "box"], \
               ], # fruits in box
    3:  [["moveTo", "fridge"], \
               ["changeState", "fridge", "open"], \
               ["moveTo", "apple"], \
               ["pick", "apple"], \
               ["moveTo", "fridge"], \
               ["drop", "fridge"], \
               ["changeState", "fridge", "close"], \
               ] # apple in fridge
}

def checkGoalWorking(state, goal_id):
    if goal_id == 0:
        return ('apple', 'table') in state['on']
    elif goal_id == 1:
        return (('apple', 'box') in state['inside'] and 
        ('orange', 'box') in state['inside'] and
        ('banana', 'box') in state['inside'])
    elif goal_id == 2:
        return (('apple', 'fridge') in state['inside'])
    elif goal_id == 3:
        return (('apple', 'fridge') in state['inside'] and 
        ('orange', 'fridge') in state['inside'] and 
        ('banana', 'fridge') in state['inside'] and 
        state['fridge'] == 'Close')
    elif goal_id == 4:
        return (('apple', 'fridge') in state['inside'] and 
        ('orange', 'cupboard') in state['inside'] and 
        ('banana', 'box') in state['inside'] and 
        state['fridge'] == 'Close' and state['cupboard'] == 'Close')

def checkActionWorking(state, action):
    if action[0] == 'moveTo':
        return True
    elif action[0] == 'pick':
        return action[1] in state['close'] and action[1] not in ['fridge', 'table', 'table2']
    elif action[0] == 'drop':
        return not (action[0] == action[1] or \
            action[1] not in ['table', 'table2', 'box', 'fridge', 'tray', 'tray2'] or \
            (action[1] in enclosures and state[action[1]] =='Close') or \
            action[1] not in state['close'])
    elif action[0] == 'changeState':
        return not (action[1] not in enclosures or \
            action[1] not in state['close'] or \
            state[action[1]] == action[2])
    elif action[0] == 'pushTo':
        return action[1] in state['close'] and action[1] != action[2]

def changeStateWorking(state1, action):
    state = deepcopy(state1)
    if action[0] == 'moveTo':
        state['close'] = [action[1]]
    elif action[0] == 'pick':
        state['grabbed'] = action[1]
    elif action[0] == 'drop':
        obj = state['grabbed']
        state['grabbed'] = ''
        if action[1] in ['box', 'fridge']:
            state['inside'].append((obj, action[1]))
        else:
            state['on'].append((obj, action[1]))
    elif action[0] == 'changeState':
        state['fridge'] = 'Close' if state['fridge'] == 'Open' else 'Open'
    elif action[0] == 'pushTo':
        state['close'] = [action[2]]
    return state

def checkStateEquality(statePred, stateTrue):
    return (statePred['grabbed'] == stateTrue['grabbed'] and
        statePred['fridge'] == stateTrue['fridge'] and
        statePred['cupboard'] == stateTrue['cupboard'] and
        set(statePred['inside']).issubset(set(stateTrue['inside'])) and
        set(statePred['on']).issubset(set(stateTrue['on'])) and
        set(stateTrue['close']).issubset(set(statePred['close'])))

def testCheckAction():
    total_tests = 0; incorrect = 0
    errors.writelines(["\n\n#### Testing Check Action ####\n\n"])
    result.writelines(["\n\n#### Testing Check Action ####\n\n"])
    for worldID in range(5):
        for planID in range(4):
            for goal_id in range(4):
                state = all_worlds[worldID]
                plan = plans[planID]
                for action in plan:
                    total_tests += 1
                    if checkAction(state, action) and not checkActionWorking(state, action):
                        errors.writelines(["\nERROR: planner says incorrect action for a valid action\n"])
                        errors.writelines(["State\n", state, "\nAction\n", action])
                        incorrect += 1
                    elif not checkActionWorking(state, action) and checkAction(state, action):
                        errors.writelines(["\nERROR: planner says correct action for an invalid action\n"])
                        errors.writelines(["State\n", state, "\nAction\n", action])
                        incorrect += 1
                        break
                    state = changeStateWorking(state, action) 
    result.writelines(["Total tests\n", str(total_tests), "\nTotal incorrect\n", \
        str(incorrect), "\nPercentage correct\n", str(100.0*(total_tests-incorrect)/total_tests)])

def testChangeState():
    total_tests = 0; incorrect = 0
    errors.writelines(["\n\n#### Testing Change State ####\n\n"])
    result.writelines(["\n\n#### Testing Change State ####\n\n"])
    for worldID in range(5):
        for planID in range(4):
            for goal_id in range(4):
                state = all_worlds[worldID]
                plan = plans[planID]
                for action in plan:
                    total_tests += 1
                    if checkAction(state, action):
                        statePred = changeState(state, action) 
                        stateTrue = changeStateWorking(state, action)
                        if not checkStateEquality(statePred, stateTrue):
                            errors.writelines(["\nERROR: incorrect final state\n", str(statePred), '\nTrue state\n', str(stateTrue)])
                            errors.writelines(["\nOriginal state\n", str(state)])
                            errors.writelines(["\nOriginal action\n", str(action), '\n'])
                            incorrect += 1
                        state = statePred
                    else:
                        break
    result.writelines(["Total tests\n", str(total_tests), "\nTotal incorrect\n", \
        str(incorrect), "\nPercentage correct\n", str(100.0*(total_tests-incorrect)/total_tests)])

def checkPlan(test):
    testOutput = 'testLogs/'+args.input+'/errors_G'+args.goal.split('.')[1][-1]+'_W'+args.world.split('.')[1][-1]+'.txt'
    testResult = 'testLogs/'+args.input+'/result_G'+args.goal.split('.')[1][-1]+'_W'+args.world.split('.')[1][-1]+'.txt'
    errors = open(testOutput, 'w+')
    result = open(testResult, 'w+')
    if test == 'part2':
        errors.writelines(["\n\n#### Checking forward search ####\n"])
        result.writelines(["\n\n#### Checking forward search ####\n"])
    elif test == 'part3':
        errors.writelines(["\n\n#### Checking backward search ####\n"])
        result.writelines(["\n\n#### Checking backward search ####\n"])
    elif test == 'part4' or test == 'part5':
        errors.writelines(["\n\n#### Checking accelerated search ####\n"])
        result.writelines(["\n\n#### Checking accelerated search ####\n"])
    start = time.time(); print(0)
    try:
        if test == 'part2':
            plan = getPlan() ####
        elif test == 'part3':
            plan = getPlan() ####
        else:
            plan = getPlan() ####
        state = getCurrentState()
        result.writelines(["\n\nInitial State: ", str(state)])
        errors.writelines(["\n\nInitial State: ", str(state)])
        errors.writelines(["\n\nPlan\n", str(plan)])
        result.writelines(["\n\nPlan\n", str(plan)])
        result.writelines(["\nPlan length: ", str(len(plan))])
        result.writelines(["\nTime: ", str(time.time() - start)])
    except Exception as e:
        errors.writelines(["\n\nERROR:\n", str(e), "\n"])
    print(time.time()-start)
    try:
        res, state = execute(plan)
        result.writelines(["\n\nFinal State: ", str(state)])
        result.writelines(["\n\nSymbolic Result: ", str(checkGoalWorking(state, int(args.goal.split('.')[1][-1])))])
        result.writelines(["\n\nExecution Result: ", str(res or checkGoalWorking(state, int(args.goal.split('.')[1][-1])))])
        errors.writelines(["\n\nFinal State\n", str(state)])
    except Exception as e:
        errors.writelines(["\n\nERROR WHILE EXECUTING PLAN:\n", str(e), "\n"])
    errors.close(); result.close()

if __name__ == '__main__':
    if args.input == 'part1':
        testCheckAction()
        testChangeState()
        errors.close(); result.close()
    else:
        checkPlan(args.input)