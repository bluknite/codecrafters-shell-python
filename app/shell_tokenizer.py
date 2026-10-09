class ShellTokenizer:
    @staticmethod
    def tokenize(string: str) -> list[str]:
        i = 0
        tokens = []

        while i < len(string):
            # if space advance to next non-space character
            while i < len(string) and string[i] == ' ':
                i += 1
            if i >= len(string):
                break
            if string[i] == "'":
                (i, token) = ShellTokenizer.parse_single_quoted_string(string, i)
                if not i:
                    return None
                tokens.append(token)
            elif string[i] == '"':
                (i, token) = ShellTokenizer.parse_double_quoted_string(string, i)
                if not i:
                    return None
                tokens.append(token)
            else:
                (i, token) = ShellTokenizer.parse_unquoted_string(string, i)
                tokens.append(token)

        merged = True
        while merged:
            merged = False
            new_tokens = []
            i = 0
            while i < len(tokens):
                t = tokens[i]
                if not t[1]:
                    new_tokens.append(t)
                    i += 1
                else:
                    t2 = tokens[i+1]
                    new_tokens.append((t[0] + t2[0], t2[1]))
                    merged = True
                    i += 2
            tokens = new_tokens

        return [t[0] for t in tokens]

    @staticmethod
    def parse_unquoted_string(string: str, i:int) -> tuple[int, tuple[str, bool]]:
        if string[i] == '\\':
            i += 1
        j = i+1
        token = string[i]
        while j < len(string) and string[j] != ' ' and not ShellTokenizer.is_quote(string[j]):
            if string[j] == '\\':
                j += 1
            token += string[j]
            j += 1
        return (j, (token, j < len(string) and ShellTokenizer.is_quote(string[j])))

    @staticmethod
    def parse_single_quoted_string(string: str, i: int) -> tuple[int, tuple[str, bool]]:
        j = i + 1
        token = ''
        while j < len(string) and string[j] != "'":
            token += string[j]
            j += 1
        
        if j >= len(string):
            print(f'Expected closing quote: {string[i:]}')
            return (None, None)
        return (j+1, (token, j < len(string) - 1 and string[j+1] != ' '))

    @staticmethod
    def parse_double_quoted_string(string: str, i: int) -> tuple[int, tuple[str, bool]]:
        j = i + 1
        token = ''
        while j < len(string) and string[j] != '"':
            if string[j] == '\\':
                j += 1
            token += string[j]
            j += 1
        
        if j >= len(string):
            print(f'Expected closing quote: {string[i:]}')
            return (None, None)
        return (j+1, (token, j < len(string) - 1 and string[j+1] != ' '))

    @staticmethod
    def is_quote(c: str) -> bool:
        return c == "'" or c == '"'