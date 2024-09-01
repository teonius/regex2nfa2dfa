class Automata:
    """Class to represent an Automaton (NFA or DFA)."""

    def __init__(self, language={'0', '1'}):
        self.states = set()
        self.startstate = None
        self.finalstates = []
        self.transitions = dict()
        self.language = language

    @staticmethod
    def epsilon():
        return ":e:"  # Epsilon transition symbol

    def addstate(self, state):
        """Add a state to the automaton and initialize its transition dictionary."""
        self.states.add(state)
        if state not in self.transitions:
            self.transitions[state] = {}

    def setstartstate(self, state):
        self.startstate = state
        self.addstate(state)

    def addfinalstates(self, state):
        if isinstance(state, int):
            state = [state]
        for s in state:
            self.addstate(s)
            if s not in self.finalstates:
                self.finalstates.append(s)

    def addtransition(self, fromstate, tostate, regex):
        self.addstate(fromstate)
        self.addstate(tostate)
        if isinstance(regex, str):
            regex = {regex}
        if fromstate in self.transitions:
            if tostate in self.transitions[fromstate]:
                self.transitions[fromstate][tostate] = self.transitions[fromstate][tostate].union(regex)
            else:
                self.transitions[fromstate][tostate] = regex
        else:
            self.transitions[fromstate] = {tostate: regex}

    def addtransition_dict(self, transitions):
        for fromstate, tostates in transitions.items():
            for state in tostates:
                self.addtransition(fromstate, state, tostates[state])

    def gettransitions(self, state, key):
        if isinstance(state, int):
            state = [state]
        trstates = set()
        for st in state:
            if st in self.transitions:
                for tns in self.transitions[st]:
                    if key in self.transitions[st][tns]:
                        trstates.add(tns)
        return trstates

    def getEClose(self, findstate):
        allstates = set()
        states = {findstate}
        while states:
            state = states.pop()
            allstates.add(state)
            if state in self.transitions:
                for tns in list(self.transitions[state]):  # Use list to avoid modifying the set during iteration
                    if Automata.epsilon() in self.transitions[state][tns] and tns not in allstates:
                        states.add(tns)
        return allstates

    def display(self):
        print("States:", sorted(self.states))
        print("Start State:", self.startstate)
        print("Final States:", sorted(self.finalstates))
        print("Transitions:")
        for fromstate in sorted(self.transitions.keys()):
            tostates = self.transitions[fromstate]
            for state in sorted(tostates.keys()):
                for char in sorted(tostates[state]):
                    print(f"  {fromstate} --{char}--> {state}")

    def getPrintText(self):
        text = "Language: {" + ", ".join(self.language) + "}\n"
        text += "States: {" + ", ".join(map(str, sorted(self.states))) + "}\n"
        text += "Start State: " + str(self.startstate) + "\n"
        text += "Final States: {" + ", ".join(map(str, sorted(self.finalstates))) + "}\n"
        text += "Transitions:\n"
        linecount = 5
        for fromstate in sorted(self.transitions.keys()):
            tostates = self.transitions[fromstate]
            for state in sorted(tostates.keys()):
                for char in sorted(tostates[state]):
                    text += "    " + str(fromstate) + " -> " + str(state) + " on '" + char + "'\n"
                    linecount += 1
        return [text, linecount]

    def newBuildFromNumber(self, startnum):
        translations = {}
        for i in sorted(self.states):
            translations[i] = startnum
            startnum += 1
        rebuild = Automata(self.language)
        rebuild.setstartstate(translations[self.startstate])
        rebuild.addfinalstates(translations[self.finalstates[0]])
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                rebuild.addtransition(translations[fromstate], translations[state], tostates[state])
        return [rebuild, startnum]

    def newBuildFromEquivalentStates(self, equivalent, pos):
        rebuild = Automata(self.language)
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                rebuild.addtransition(pos[fromstate], pos[state], tostates[state])
        rebuild.setstartstate(pos[self.startstate])
        for s in self.finalstates:
            rebuild.addfinalstates(pos[s])
        return rebuild


class BuildAutomata:
    """Class for building basic NFA structures."""

    @staticmethod
    def basicstruct(inp):
        """
        Create a basic NFA for a single character input.
        The NFA will have two states: a start state and a final state.
        """
        state1 = 1
        state2 = 2
        basic = Automata()
        basic.setstartstate(state1)
        basic.addfinalstates(state2)
        basic.addtransition(state1, state2, inp)
        return basic

    @staticmethod
    def plusstruct(a, b):
        [a, m1] = a.newBuildFromNumber(2)
        [b, m2] = b.newBuildFromNumber(m1)
        state1 = 1
        state2 = m2
        plus = Automata()
        plus.setstartstate(state1)
        plus.addfinalstates(state2)

        # Add transitions from the start state to the start states of both a and b
        plus.addtransition(plus.startstate, a.startstate, Automata.epsilon())
        plus.addtransition(plus.startstate, b.startstate, Automata.epsilon())

        # Add transitions from the final states of a and b to the final state of plus
        plus.addtransition(a.finalstates[0], plus.finalstates[0], Automata.epsilon())
        plus.addtransition(b.finalstates[0], plus.finalstates[0], Automata.epsilon())

        # Add all transitions of a and b to the plus automaton
        plus.addtransition_dict(a.transitions)
        plus.addtransition_dict(b.transitions)

        return plus

    @staticmethod
    def dotstruct(a, b):
        [a, m1] = a.newBuildFromNumber(1)
        [b, m2] = b.newBuildFromNumber(m1)
        state1 = 1
        state2 = m2 - 1
        dot = Automata()
        dot.setstartstate(state1)
        dot.addfinalstates(state2)
        dot.addtransition(a.finalstates[0], b.startstate, Automata.epsilon())
        dot.addtransition_dict(a.transitions)
        dot.addtransition_dict(b.transitions)
        return dot

    @staticmethod
    def starstruct(a):
        [a, m1] = a.newBuildFromNumber(2)
        state1 = 1
        state2 = m1
        star = Automata()
        star.setstartstate(state1)
        star.addfinalstates(state2)
        star.addtransition(star.startstate, a.startstate, Automata.epsilon())
        star.addtransition(star.startstate, star.finalstates[0], Automata.epsilon())
        star.addtransition(a.finalstates[0], star.finalstates[0], Automata.epsilon())
        star.addtransition(a.finalstates[0], a.startstate, Automata.epsilon())  # Loop back for Kleene star
        star.addtransition_dict(a.transitions)
        return star

    @staticmethod
    def exactRepetitionStruct(a, n):
        if n <= 0:
            raise ValueError("Repetition count 'n' must be greater than 0")

        repeated = Automata(a.language)
        repeated.setstartstate(1)
        previous_final_state = 1

        for i in range(n):
            [a_copy, new_state] = a.newBuildFromNumber(previous_final_state)
            repeated.addtransition(previous_final_state, a_copy.startstate, Automata.epsilon())
            repeated.addtransition_dict(a_copy.transitions)
            previous_final_state = a_copy.finalstates[0]

        repeated.addfinalstates(previous_final_state)
        return repeated

    @staticmethod
    def rangeRepetitionStruct(a, n, m):
        if n > m or n < 0:
            raise ValueError("Repetition counts must satisfy 0 <= n <= m")

        repeated = BuildAutomata.exactRepetitionStruct(a, n)

        # Add the remaining optional repetitions
        current_final_state = repeated.finalstates[0]
        last_final_state = current_final_state

        for i in range(n, m):
            [a_copy, new_state] = a.newBuildFromNumber(current_final_state + 1)
            repeated.addtransition(current_final_state, a_copy.startstate, Automata.epsilon())
            repeated.addtransition_dict(a_copy.transitions)
            current_final_state = a_copy.finalstates[0]

            # Ensure that every intermediate state can also reach the final state
            repeated.addtransition(current_final_state, repeated.finalstates[0], Automata.epsilon())

        # Ensure that the last final state is marked as final
        repeated.addfinalstates(current_final_state)
        return repeated

    @staticmethod
    def atLeastRepetitionStruct(a, n):
        repeated = BuildAutomata.exactRepetitionStruct(a, n)
        loop = BuildAutomata.starstruct(a)
        repeated = BuildAutomata.dotstruct(repeated, loop)

        return repeated
