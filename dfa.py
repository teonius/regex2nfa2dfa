from nfa import Automata

class DFAfromNFA:
    def __init__(self, nfa, alphabet):
        self.alphabet = {char for char in alphabet if char in nfa.language}
        self.dfa = None
        self.minDFA = None
        self.buildDFA(nfa)
        self.minimise()

    def getDFA(self):
        return self.dfa

    def getMinimisedDFA(self):
        return self.minDFA

    def displayDFA(self):
        self.dfa.display()

    def displayMinimisedDFA(self):
        self.minDFA.display()

    def buildDFA(self, nfa):
        allstates = {}
        eclose = {}
        count = 1

        # Calculate the epsilon closure for the start state
        state1 = frozenset(sorted(nfa.getEClose(nfa.startstate)))
        eclose[nfa.startstate] = state1
        dfa = Automata(nfa.language)
        dfa.setstartstate(count)
        states = [[state1, count]]
        allstates[count] = state1
        count += 1

        while states:
            state, fromindex = states.pop()
            for char in sorted(self.alphabet):
                if char == Automata.epsilon():
                    continue

                trstates = set()
                for s in state:
                    trstates.update(nfa.gettransitions(s, char))

                expanded_trstates = set()
                for s in trstates:
                    if s not in eclose:
                        eclose[s] = nfa.getEClose(s)
                    expanded_trstates.update(eclose[s])

                trstates = frozenset(sorted(expanded_trstates))

                if trstates:
                    if trstates not in allstates.values():
                        states.append([trstates, count])
                        allstates[count] = trstates
                        toindex = count
                        count += 1
                    else:
                        toindex = [k for k, v in allstates.items() if v == trstates][0]
                    dfa.addtransition(fromindex, toindex, char)

        # Handle final states carefully, ensuring only correct final states are marked
        for value, state in allstates.items():
            if any(final in state for final in nfa.finalstates):
                dfa.addfinalstates(value)

        self.dfa = dfa
        print("DFA Construction Complete")

    def minimise(self):
        final_states = set(self.dfa.finalstates)
        non_final_states = self.dfa.states - final_states

        partitions = [final_states, non_final_states] if non_final_states else [final_states]

        while True:
            new_partitions = []
            for part in partitions:
                splits = {}
                for state in part:
                    key = tuple(
                        self.find_partition(self.get_trans_state(state, char), partitions) for char in sorted(self.alphabet)
                    )
                    if key not in splits:
                        splits[key] = set()
                    splits[key].add(state)

                new_partitions.extend(splits.values())

            if len(new_partitions) == len(partitions):
                break
            partitions = new_partitions

        state_map = {}
        new_state_id = 1
        for part in sorted(new_partitions, key=lambda x: min(x) if x else float('inf')):
            for state in part:
                state_map[state] = new_state_id
            new_state_id += 1

        self.minDFA = Automata(self.dfa.language)
        self.minDFA.setstartstate(state_map[self.dfa.startstate])
        self.minDFA.addfinalstates([state_map[s] for s in self.dfa.finalstates])

        for fromstate, tostates in self.dfa.transitions.items():
            for tostate, chars in tostates.items():
                for char in chars:
                    mapped_from = state_map[fromstate]
                    mapped_to = state_map[tostate]
                    self.minDFA.addtransition(mapped_from, mapped_to, char)

        print("DFA Minimization Complete")

    def get_trans_state(self, state, char):
        transitions = self.dfa.gettransitions(state, char)
        return next(iter(transitions), None)

    def find_partition(self, state, partitions):
        for i, part in enumerate(partitions):
            if state in part:
                return i
        return -1
