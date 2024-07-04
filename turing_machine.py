import re
import time
import os
from termcolor import colored

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
    for i in range(0,len(alphabet)): 
        if alphabet[i] == "blank":
            alphabet[0], alphabet[i] = alphabet[i], alphabet[0]

    turing_machine = {
        'states': states,
        'start_state': start_state,
        'final_states': final_states,
        'actions': actions,
        'alphabet': alphabet
    }

    return turing_machine

def convert_to_unary(turing_machine):
    state_mapping = {state: '1' * (i + 1) for i, state in enumerate(turing_machine['states'])}
    alphabet_mapping = {alphabet: '1' * (i + 1) for i, alphabet in enumerate(turing_machine['alphabet'])}
    
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
        'actions': actions_unary,
        'alphabet_mapping': alphabet_mapping,  # mapping for encoding
        'reverse_alphabet_mapping': {v: k for k, v in alphabet_mapping.items()}  # Reverse mapping for decoding
    }
    return unary_turing_machine

def description_tape_init(actions):
    description_tape = ""
    for action in actions:
        for element in action:
            description_tape += element + "0"
        description_tape += "0"
    
    return description_tape[:-2]

def state_tape_init(states, start_state, final_states):
    state_tape = start_state + "0"
    for state in states:
        if state == start_state or state in final_states:
            continue
        state_tape += state + "0"
    state_tape += "0"
    for state in final_states:
        state_tape += state
    
    return state_tape

def content_tape_init(content,alphabet):
    content_tape = ""
    for element in content:
        content_tape += alphabet[element] +"0"
    return "10" + content_tape + "1"

class UTM():
    def __init__(self, start_state, final_states, description_tape, content_tape, state_tape, reverse_alphabet_mapping):
        self.start_state = start_state
        self.final_states = final_states
        self.description_tape = description_tape
        self.content_tape = content_tape
        self.state_tape = state_tape
        self.state_index = 0
        self.reverse_alphabet_mapping = reverse_alphabet_mapping

    def run_turing_machine(self, index_content_tape):
        current_state = self.calculate_current_state()
        current_content = self.calculate_current_content(index_content_tape)
        i = 0
        print(f"content tape before change: \n{self.decode_content_tape()}")
        print(index_content_tape * " " + "^")
        while i < len(self.description_tape):
            print(f"description tape: \n{self.description_tape}")
            print(i * " " + "^")
            state = ""
            next_state = ""
            input = ""
            output = ""
            direction = ""
            while self.description_tape[i] == "1":
                state += "1"
                i += 1
            i += 1
            while self.description_tape[i] == "1":
                input += "1"
                i += 1
            i += 1
            while self.description_tape[i] == "1":
                output += "1"
                i += 1
            i += 1
            while self.description_tape[i] == "1":
                direction += "1"
                i += 1
            i += 1
            while i < len(self.description_tape) and self.description_tape[i] == "1":
                next_state += "1"
                i += 1
            if i < len(self.description_tape): 
                i += 2
            if state == current_state and input == current_content:
                self.change_current_state(next_state)
                self.change_current_content(output, index_content_tape)
                index_content_tape = self.apply_direction(direction, index_content_tape)
                print(f"content tape after change: \n{self.decode_content_tape()}")
                print(index_content_tape * " " + "^")
                return self.run_turing_machine(index_content_tape)
        return self.halt(current_state)

    def halt(self, current_state):
        i = len(self.state_tape) - 1
        while i >= 0:
            final_state = ""
            while i >= 0 and self.state_tape[i] != "0":
                print(f"state tape: \n{self.state_tape}")
                print(i * " " + "^")
                final_state += "1"
                i -= 1
            i -= 1
            if current_state == final_state:
                return 1
            if i >= 0 and self.state_tape[i] == "0":
                i -= 1
        return 0

    def calculate_current_state(self):
        i = 0
        state = ""
        while i + self.state_index < len(self.state_tape) and self.state_tape[i + self.state_index] != "0":
            state += "1"
            i += 1
        return state
    
    def calculate_current_content(self, index_content_tape):
        content = ""
        i = 0
        while i + index_content_tape < len(self.content_tape) and self.content_tape[i + index_content_tape] != "0":
            content += "1"
            i += 1
        return content

    def change_current_state(self, next_state):
        i = 0
        while i < len(self.state_tape):
            state = ""
            while i < len(self.state_tape) and self.state_tape[i] != "0":
                state += "1"
                i += 1
            i += 1
            if next_state == state:
                break
        else:
            raise ValueError(f"Next state {next_state} not found in state tape")
        i -= 2
        while self.state_tape[i] != "0" and i > 0:
            i -= 1
        if i > 0:
            i += 1
        self.state_index = i

    def change_current_content(self, output, index_content_tape):
        index_end_content_tape = index_content_tape
        while index_end_content_tape < len(self.content_tape) and self.content_tape[index_end_content_tape] != "0":
            index_end_content_tape += 1
        self.content_tape = self.content_tape[:index_content_tape] + output + self.content_tape[index_end_content_tape:]

    def apply_direction(self, direction, index_content_tape):
        if direction == '1':  # R
            while index_content_tape < len(self.content_tape) and self.content_tape[index_content_tape] != "0":
                index_content_tape += 1
            index_content_tape += 1
            if index_content_tape >= len(self.content_tape):
                self.content_tape += "01"  # Extend the tape with a blank
        else:  # L
            if index_content_tape == 0:
                self.content_tape = "10" + self.content_tape  # Extend the tape with a blank
            else:
                index_content_tape -= 2
                while index_content_tape >= 0 and self.content_tape[index_content_tape] != "0":
                    index_content_tape -= 1
                if index_content_tape != 0:
                    index_content_tape += 1
        return index_content_tape

    def decode_content_tape(self):
        decoded_content = ""
        i = 0
        while i < len(self.content_tape):
            symbol = ""
            while i < len(self.content_tape) and self.content_tape[i] == "1":
                symbol += "1"
                i += 1
            if symbol:
                decoded_content += self.reverse_alphabet_mapping.get(symbol, "?")
            if i < len(self.content_tape) and self.content_tape[i] == "0":
                decoded_content += " "
            i += 1
        return decoded_content.strip()

def display_step(description_tape, description_index, state_tape, state_index, content_tape, content_index, decoded_content):
    os.system('cls||clear')
    print(colored("╔════════════════════════════════════════════════════╗", 'cyan'))
    print(colored("║                   Description Tape                 ║", 'cyan'))
    print(colored("╚════════════════════════════════════════════════════╝", 'cyan'))
    print(description_tape)
    print(" " * description_index + colored("^", 'cyan'))
    print(colored("╔════════════════════════════════════════════════════╗", 'green'))
    print(colored("║                       State Tape                   ║", 'green'))
    print(colored("╚════════════════════════════════════════════════════╝", 'green'))
    print(state_tape)
    print(" " * state_index + colored("^", 'green'))
    print(colored("╔════════════════════════════════════════════════════╗", 'yellow'))
    print(colored("║                      Content Tape                  ║", 'yellow'))
    print(colored("╚════════════════════════════════════════════════════╝", 'yellow'))
    print(content_tape)
    print(" " * content_index + colored("^", 'yellow'))
    print(colored("╔════════════════════════════════════════════════════╗", 'blue'))
    print(colored("║                  Decoded Content Tape              ║", 'blue'))
    print(colored("╚════════════════════════════════════════════════════╝", 'blue'))
    print(colored(decoded_content, 'blue'))
    time.sleep(0.75) 

def run_turing_machine_with_steps(utm, index_content_tape):
    current_state = utm.calculate_current_state()
    current_content = utm.calculate_current_content(index_content_tape)
    i = 0
    decoded_content = utm.decode_content_tape()
    display_step(utm.description_tape, i, utm.state_tape, utm.state_index, utm.content_tape, index_content_tape, decoded_content)
    while i < len(utm.description_tape):
        state = ""
        next_state = ""
        input = ""
        output = ""
        direction = ""
        while i < len(utm.description_tape) and utm.description_tape[i] == "1":
            state += "1"
            i += 1
        i += 1
        while i < len(utm.description_tape) and utm.description_tape[i] == "1":
            input += "1"
            i += 1
        i += 1
        while i < len(utm.description_tape) and utm.description_tape[i] == "1":
            output += "1"
            i += 1
        i += 1
        while i < len(utm.description_tape) and utm.description_tape[i] == "1":
            direction += "1"
            i += 1
        i += 1
        while i < len(utm.description_tape) and utm.description_tape[i] == "1":
            next_state += "1"
            i += 1
        if i < len(utm.description_tape):
            i += 2
        if state == current_state and input == current_content:
            utm.change_current_state(next_state)
            utm.change_current_content(output, index_content_tape)
            index_content_tape = utm.apply_direction(direction, index_content_tape)
            decoded_content = utm.decode_content_tape()
            display_step(utm.description_tape, i, utm.state_tape, utm.state_index, utm.content_tape, index_content_tape, decoded_content)
            return run_turing_machine_with_steps(utm, index_content_tape)
    return utm.halt(current_state)

TM = convert_to_unary(parse_turing_machine("./multiplication.txt"))
description_tape = description_tape_init(TM['actions'])
state_tape = state_tape_init(TM['states'], TM['start_state'], TM['final_states'])
content_tape = content_tape_init("111011",TM['alphabet_mapping'])
print(content_tape)
uni = UTM(TM['start_state'], TM['final_states'], description_tape, content_tape, state_tape, TM['reverse_alphabet_mapping'])
print(run_turing_machine_with_steps(uni, 2))
print(parse_turing_machine("./multiplication.txt")['alphabet'])

TM2 = convert_to_unary(parse_turing_machine("./addition.txt"))
description_tape = description_tape_init(TM2['actions'])
state_tape = state_tape_init(TM2['states'], TM2['start_state'], TM2['final_states'])
content_tape = content_tape_init("111011",TM2['alphabet_mapping'])
print(content_tape)
uni = UTM(TM2['start_state'], TM2['final_states'], description_tape, content_tape, state_tape, TM2['reverse_alphabet_mapping'])
print(run_turing_machine_with_steps(uni, 2))
print(parse_turing_machine("./addition.txt")['alphabet'])
