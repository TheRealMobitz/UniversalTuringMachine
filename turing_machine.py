import re

def parse_turing_machine(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    states = re.findall(r'states:\{(.*?)\}', content)[0].split(',')
    start_state = re.findall(r'start_state:\{(.*?)\}', content)[0]
    final_states = re.findall(r'final_states:\{(.*?)\}', content)[0].split(',')
    actions = re.findall(r'actions:\{(.*?)\}', content)[0].split('),(')

    actions = [action.replace('(', '').replace(')', '').split(',') for action in actions]

    alphabet = set()
    for action in actions:
        alphabet.add(action[1])
        alphabet.add(action[2])

    alphabet = sorted(list(alphabet))
    print('alph=',alphabet)

    turing_machine = {
        'states': states,
        'start_state': start_state,
        'final_states': final_states,
        'actions': actions,
        'alphabet': alphabet
    }

    return turing_machine

print (parse_turing_machine("./test.txt"))

def convert_to_unary(turing_machine):
    state_mapping = {state: '1' * (i + 1) for i, state in enumerate(turing_machine['states'])}
    alphabet_mapping = {alphabet: '1' * (i+1) for i, alphabet in enumerate(turing_machine['alphabet'])}
    
    start_state_unary = state_mapping[turing_machine['start_state']]
    final_states_unary = [state_mapping[state] for state in turing_machine['final_states']]
    
    actions_unary = []
    for action in turing_machine['actions']:
        current_state = state_mapping[action[0]]
        read_symbol = alphabet_mapping[action[1]]
        write_symbol = alphabet_mapping[action[2]]
        direction = '1' if action[3] == 'R' else '11'
        next_state = state_mapping[action[4]]
        
        actions_unary.append((current_state, read_symbol, write_symbol, direction, next_state))
    
    unary_turing_machine = {
        'states': list(state_mapping.values()),
        'start_state': start_state_unary,
        'final_states': final_states_unary,
        'actions': actions_unary
    }
    return unary_turing_machine

print(convert_to_unary(parse_turing_machine("./test.txt")))

def description_tape_init(actions):
    description_tape = ""
    for action in actions:
        for element in action:
            description_tape += element + "0"
        description_tape += "0"
    
    return description_tape[:-2]


TM = convert_to_unary(parse_turing_machine("./test.txt"))
print("description tape: ",description_tape_init(TM['actions']))

def state_tape_init(states,start_state, final_states):
    state_tape = start_state + "0"
    for state in states:
        if state == start_state or state == final_states:
            continue
        state_tape += state + "0"
    state_tape += "0"
    for state in final_states:
        state_tape += state
    
    return state_tape[:-1]


print("state tape:", state_tape_init(TM['states'], TM['start_state'], TM['final_states']))


class UTM():
    def __init__(self, start_state, final_states, description_tape, content_tape, state_tape):
        self.start_state = start_state
        self.final_states = final_states
        self.description_tape = description_tape
        self.content_tape = content_tape
        self.state_tape = state_tape