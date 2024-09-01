import re
from nfa import BuildAutomata

class NFAfromRegex:
    def __init__(self, regex, alphabet=None):
        self.star = '*'
        self.plus = '+'
        self.dot = '.'
        self.openingBracket = '('
        self.closingBracket = ')'
        self.epsilon = '€'  # Epsilon symbol
        self.operators = [self.plus, self.dot]
        self.regex = regex
        self.alphabet = alphabet if alphabet else [chr(i) for i in range(65, 91)] + \
                                                [chr(i) for i in range(97, 123)] + \
                                                [chr(i) for i in range(48, 58)]
        self.buildNFA()

    def getNFA(self):
        return self.nfa

    def displayNFA(self):
        self.nfa.display()

    def buildNFA(self):
        language = set()
        self.stack = []
        self.automata = []
        previous = "::e::"
        i = 0

        try:
            while i < len(self.regex):
                char = self.regex[i]
                if char in self.alphabet:
                    language.add(char)
                    if previous != self.dot and (
                            previous in self.alphabet or previous in [self.closingBracket, self.star, "}"]):
                        self.addOperatorToStack(self.dot)
                    self.automata.append(BuildAutomata.basicstruct(char))
                    i += 1
                elif char == self.epsilon:  # Handle epsilon transitions
                    self.automata.append(BuildAutomata.epsilonStruct())
                    i += 1
                elif char == self.openingBracket:
                    if previous != self.dot and (
                            previous in self.alphabet or previous in [self.closingBracket, self.star, "}"]):
                        self.addOperatorToStack(self.dot)
                    self.stack.append(char)
                    i += 1
                elif char == self.closingBracket:
                    while len(self.stack) != 0 and self.stack[-1] != self.openingBracket:
                        op = self.stack.pop()
                        self.processOperator(op)
                    self.stack.pop()
                    i += 1
                elif char == self.plus:
                    while len(self.stack) != 0 and self.stack[-1] == self.dot:
                        op = self.stack.pop()
                        self.processOperator(op)
                    self.stack.append(char)
                    i += 1
                elif char == self.star:
                    self.processOperator(self.star)
                    i += 1
                elif char == "{":
                    end_brace = self.regex.find("}", i)
                    if end_brace == -1:
                        raise BaseException("Unmatched '{' in regex")
                    repeat_pattern = self.regex[i + 1:end_brace]
                    if "," in repeat_pattern:
                        parts = repeat_pattern.split(",")
                        n = int(parts[0]) if parts[0] else 0
                        m = int(parts[1]) if parts[1] else float('inf')
                    else:
                        n = int(repeat_pattern)
                        m = n
                    self.processRepetition(n, m)
                    i = end_brace + 1
                else:
                    raise BaseException(f"Unsupported character '{char}' in regex")

                previous = char

            while len(self.stack) != 0:
                op = self.stack.pop()
                self.processOperator(op)

            if len(self.automata) > 1:
                while len(self.automata) > 1:
                    a = self.automata.pop()
                    b = self.automata.pop()
                    self.automata.append(BuildAutomata.dotstruct(b, a))

            self.nfa = self.automata.pop()
            self.nfa.language = language

        except Exception as e:
            raise BaseException(f"Error parsing regex '{self.regex}' at position {i}: {str(e)}")

    def addOperatorToStack(self, char):
        while True:
            if len(self.stack) == 0:
                break
            top = self.stack[-1]
            if top == self.openingBracket:
                break
            if top == char or top == self.dot:
                op = self.stack.pop()
                self.processOperator(op)
            else:
                break
        self.stack.append(char)

    def processOperator(self, operator):
        if len(self.automata) == 0:
            raise BaseException(f"Error processing operator '{operator}'. Stack is empty")
        if operator == self.star:
            a = self.automata.pop()
            self.automata.append(BuildAutomata.starstruct(a))
        elif operator in self.operators:
            if len(self.automata) < 2:
                raise BaseException(f"Error processing operator '{operator}'. Inadequate operands")
            a = self.automata.pop()
            b = self.automata.pop()
            if operator == self.plus:
                self.automata.append(BuildAutomata.plusstruct(b, a))
            elif operator == self.dot:
                self.automata.append(BuildAutomata.dotstruct(b, a))

    def processRepetition(self, n, m):
        if len(self.automata) == 0:
            raise BaseException("Error processing repetition. Stack is empty")
        a = self.automata.pop()
        if n == m:
            self.automata.append(BuildAutomata.exactRepetitionStruct(a, n))
        elif m == float('inf'):
            self.automata.append(BuildAutomata.atLeastRepetitionStruct(a, n))
        else:
            self.automata.append(BuildAutomata.rangeRepetitionStruct(a, n, m))
