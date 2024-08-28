class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"({self.type}, {self.value})"


class RegexTokenizer:
    def __init__(self, regex, alphabet):
        self.regex = regex
        self.alphabet = alphabet
        self.tokens_combinations = self.tokenize()

    def tokenize(self):
        tokens = []
        i = 0
        while i < len(self.regex):
            if self.regex[i] in self.alphabet:
                tokens.append(Token("CHAR", self.regex[i]))
            elif self.regex[i] == "*":
                tokens.append(Token("KLEENE", "*"))
            elif self.regex[i] == "|":
                tokens.append(Token("UNION", "|"))
            elif self.regex[i] == "(":
                tokens.append(Token("LPAREN", "("))
            elif self.regex[i] == ")":
                tokens.append(Token("RPAREN", ")"))
            elif self.regex[i] == "+":
                tokens.append(Token("PLUS", "+"))
            elif self.regex[i] == "?":
                tokens.append(Token("QUESTION", "?"))
            elif self.regex[i] == ".":
                tokens.append(Token("DOT", "."))
            else:
                raise ValueError(f"Unexpected character in regex: {self.regex[i]}")
            i += 1
        return [tokens]

    def get_tokens_combinations(self):
        return self.tokens_combinations