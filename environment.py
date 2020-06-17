from husky_ur5 import *
from copy import deepcopy

state = getCurrentState()
print(state)

# state: {'grabbed': '', 'fridge': 'Close', 'cupboard': 'Close', 'inside': [], 'on': [], 'close': []}

objects = ['apple', 'orange', 'banana', 'table', 'table2', 'box', 'fridge', 'tray', 'tray2', 'cupboard']
enclosures = ['fridge', 'cupboard']
actions = ['moveTo', 'pick', 'drop', 'changeState', 'pushTo']

# A checker for action feasibility
def checkAction(state, action):
	# Check if action is possible for state
	#######################################
	######## Insert your code here ########
	#######################################
	if action[0] == 'moveTo':
		if action[1] in state['close'] or action[1]==state['grabbed']:
			return False

	elif action[0] == 'pick':
		if state['grabbed']:
			return False
		else:
			if action[1] in ['table', 'table2', 'fridge', 'cupboard']:
				return False
			else:
				if action[1] not in state['close']:
					return False
				for a,b in state['inside']:
					if a==action[1] and b in ['fridge', 'cupboard']:
						if state[b].lower()=='close':
							return False 
						break

	elif action[0] == 'drop':
		if state['grabbed'] == action[1]:
			return False
		if state['grabbed']:
			if action[1] in state['close']:
				if action[1] == 'fridge':
					if state['fridge'].lower() == 'close':
						return False
				elif action[1] == 'cupboard':
					if state['cupboard'].lower() == 'close':
						return False
				elif action[1] in ['table', 'table2', 'tray', 'tray2', 'box']:
					return True
				else:
					return False
			else:
				return False
		else:
			return False

	elif action[0] == 'changeState':
		obj = action[1]
		if obj == 'fridge' or obj == 'cupboard':
			if obj in state['close']:
				if action[2] == 'open':
					if state[obj].lower() == 'open':
						return False
				elif action[2] == 'close':
					if state[obj].lower() == 'close':
						return False
				else:
					return False
			else:
				return False
		else:
			return False

	elif action[0] == 'pushTo':
		if state['grabbed']:
			return False
		elif action[1] == action[2]:
			return False
		else:
			if action[1] in ['fridge', 'cupboard', 'table', 'table2', 'box']:
				return False
			if action[1] not in state['close']:
				return False
			for a,b in state['inside']:
					if a==action[1] and b in ['fridge', 'cupboard']:
						if state[b].lower()=='close':
							return False 
						break

	else:
		return False

	return True

# An approximate environment model
def changeState(state1, action):
	state = deepcopy(state1)
	# Change state based on action
	#######################################
	######## Insert your code here ########
	#######################################
	if not checkAction(state1, action):
		return state

	def moveTo(obj, state):
		state = deepcopy(state)
		state['close'] = []
		state['close'].append(obj)
		# if object is an enclosure, it is also close to the objects inside it
		# if object is a surface, it is also close to the objects on it 
		### dont include table - table is big
		if obj in ['fridge', 'cupboard', 'box']:
			for a,b in state['inside']:
				if b==obj:
					state['close'].append(a)
		elif obj in ['table', 'table2', 'tray', 'tray2']:
			for a,b in state['on']:
				if b==obj:
					state['close'].append(a)
		return state

	if action[0]=='moveTo':
		state = moveTo(action[1], state)

	elif action[0]=='pick':
		state['grabbed'] = action[1]
		state['close'].append(action[1])
		state['inside'] = list(filter(lambda x: x[0]!=action[1], state['inside']))
		state['on'] = list(filter(lambda x: x[0]!=action[1], state['on']))

	elif action[0]=='drop':
		if action[1] in ['fridge', 'cupboard', 'box']:
			state['inside'].append((state['grabbed'], action[1]))
		elif action[1] in ['table', 'table2', 'tray', 'tray2']:
			state['on'].append((state['grabbed'], action[1]))
		# not necessarily close	- empty 
		state['close'] = []
		state['grabbed'] = ''

	elif action[0]=='changeState':
		# when state of enclosure changes, the robot is no longer close to that object
		state[action[1]] = action[2].capitalize()
		state['close'] = []

	elif action[0]=='pushTo':
		# remove from inside and on
		# if destination is surface, add on it
		# not necessarily close to anything!!
		state['inside'] = list(filter(lambda x: x[0]!=action[1], state['inside']))
		state['on'] = list(filter(lambda x: x[0]!=action[1], state['on']))
		# print(state['on'])
		if action[2] in ['table', 'table2', 'tray', 'tray2']:
			state['on'].append((action[1], action[2]))
		state['close'] = [action[1], action[2]] 
		state['grabbed'] = ''
		
	return state

# An approximate goal checker
def checkGoal(state, goal_file):
	f = open(goal_file)
	goal = json.load(f)
	for subgoal in goal['goals']:
		if subgoal['target'] in ['fridge', 'cupboard', 'box']:
			if (subgoal['object'], subgoal['target']) not in state['inside']:
				# print(subgoal['object']+" is not inside "+subgoal['target'])
				return False
		elif subgoal['target'] in ['table', 'table2', 'tray', 'tray2']:
			if (subgoal['object'], subgoal['target']) not in state['on']:
				# print(subgoal['object']+" is not on "+subgoal['target'])
				return False
		elif subgoal['object'] in ['cupboard', 'fridge']:
			if state[subgoal['object']].lower() != subgoal['state'].lower():
				# print(subgoal['object']+" is not in "+subgoal['state']+" state")
				return False
	return True

