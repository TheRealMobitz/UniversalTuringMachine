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
    
    return state_tape


print("state tape:", state_tape_init(TM['states'], TM['start_state'], TM['final_states']))


class UTM():
    def __init__(self, start_state, final_states, description_tape, content_tape, state_tape):
        self.start_state = start_state
        self.final_states = final_states
        self.description_tape = description_tape
        self.content_tape = content_tape
        self.state_tape = state_tape
        self.state_index = 0


    def run_turing_machine(self, index_content_tape):
        current_state = self.calculate_current_state()
        current_content = self.calculate_current_content(index_content_tape)
        i=0
        print(f"content tape before change: \n{self.content_tape}")
        print(index_content_tape*" " +"^")
        while i < len(description_tape):
            print(f"description tape: \n{self.description_tape}")
            print(i*" " +"^")
            state = ""
            next_state = ""
            input = ""
            output = ""
            direction = ""
            while self.description_tape[i] == "1":
                state += "1"
                i+=1
            i+=1
            while self.description_tape[i] == "1":
                input += "1"
                i+=1
            i+=1
            while self.description_tape[i] == "1":
                output += "1"
                i+=1
            i+=1
            while self.description_tape[i] == "1":
                direction += "1"
                i+=1
            i+=1
            while i < len(self.description_tape) and self.description_tape[i] == "1":
                next_state += "1"
                i+=1
            if i < len(self.description_tape): 
                i+=2
            # print(f"state: {state} next: {next_state}")
            # print(f"input: {input} output: {output}")
            # print(f"current state: {current_state} current input: {current_content}")
            
            if state == current_state and input == current_content:
                self.change_current_state(next_state)
                self.change_current_content(output, index_content_tape)
                index_content_tape = self.apply_direction(direction, index_content_tape)
                # print(f"state index: {self.state_index}")
                # print(f"content index: {index_content_tape}")
                # print(f"description index: {i}")
                print(f"content tape after change: \n{self.content_tape}")
                print(index_content_tape*" " +"^")
                return self.run_turing_machine(index_content_tape)
        # print(self.content_tape)
        return self.halt(current_state)

    def halt(self,current_state):
        i = len(self.state_tape)-1
        while True:
            final_state = ""
            while self.state_tape[i] != "0":
                print(f"state tape: \n{self.state_tape}")
                print(i*" " +"^")
                final_state += "1"
                i -= 1
            i-=1
            print("final state: "+final_state)
            if current_state == final_state:
                return 1
            if self.state_tape[i] == "0":
                return 0
        
    def calculate_current_state(self):
        i = 0
        state = ""
        while self.state_tape[i + self.state_index] != "0":
            state += "1"
            i += 1
        print("calculate current state: "+state)
        return state
    
    def calculate_current_content(self, index_content_tape):
        content = ""
        i = 0
        while self.content_tape[i + index_content_tape] != "0":
            content += "1"
            i +=1
        print("calculate current content: "+content)
        return content

    def change_current_state(self, next_state):
        i = 0
        while True:
            state = ""
            while self.state_tape[i] != "0":
                state += "1"
                i += 1
            i += 1
            # print(f"state is {state} and next is : {next_state}")
            if(next_state == state):
                break
        i -= 2
        while self.state_tape[i] != "0" and i>0:
                i -= 1
        if i >0:
            i += 1
        self.state_index = i
    
    def change_current_content(self, output, index_content_tape):
        index_end_content_tape = index_content_tape
        while self.content_tape[index_end_content_tape] != "0":
            index_end_content_tape += 1
        self.content_tape = self.content_tape[:index_content_tape] + output + self.content_tape[index_end_content_tape:]

    def apply_direction(self,direction,index_content_tape):
        if direction=='1' : #R
            while self.content_tape[index_content_tape] != "0" and index_content_tape < len(self.content_tape):
                index_content_tape += 1
            # TODO: need some condition here for overloading
            index_content_tape += 1
        else: #L
            index_content_tape -= 2
            while self.content_tape[index_content_tape] != "0" and index_content_tape > 0:
                index_content_tape -= 1
            if index_content_tape != 0:
                index_content_tape += 1
            # TODO: need some condition here for overloading
        return index_content_tape

description_tape = description_tape_init(TM['actions'])
state_tape = state_tape_init(TM['states'], TM['start_state'], TM['final_states'])

uni = UTM(TM['start_state'],TM['final_states'],description_tape,"110101011011011011",state_tape)
print(uni.run_turing_machine(3))

# TODO: translate contenet tape