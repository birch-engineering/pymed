from num2words import num2words
import decimal
import string
import re
from spacy import Language



def escape_punct(tok: str):
    punct = set(
        [
            "!",
            '"',
            "#",
            "$",
            "&",
            "'",
            "(",
            ")",
            ",",
            "-",
            ".",
            ":",
            ";",
            "?",
            "@",
            "[",
            "]",
            "^",
            "_",
            "`",
            "{",
            "|",
            "}",
            "~",
            "/",
            "\\",
        ]
    )
    if tok in punct:
        return True

def escape_token(tok: str):

    tok = ''.join(filter(lambda x: x.isascii(), tok))
    if not tok:
        return True

    if escape_punct(tok):
        return True

    url_re = re.compile(r"HTTPS:|HTTP:|WWW\.")
    if url_re.match(tok.upper()):
        return True

def convert_sent_to_word(sent: str, nlp: Language = None):
    signs = set(["/", "%", "=", ">", "<", "+", "+-", "≤", "≥", "*"])
    filtered_sent = []
    time_re = re.compile(r"^([01]\d|2[0-4]):([0-5]\d):?([0-5]\d)?$")
    num_re = re.compile(r"[0-9]+")

    tokenized_str = [tok.text for tok in nlp(sent)] if nlp else sent.split()
    for token in tokenized_str:
        if escape_token(token):
            continue
        if token == ">" and filtered_sent and filtered_sent[-1] == "EQUAL TO":
            filtered_sent[-1] = ""
            continue

        # Spacy will separate I'm to I 'm, but we don't use spacy anymore, so this is deprecated
        # if token[0] == "'" and filtered_sent:
        #     filtered_sent[-1] += token.upper()
        #     continue

        if token == 'A.M' or token == 'P.M':
            filtered_sent.append(token[0] + token[2])
            continue

        m = time_re.match(token)
        if m:
            time_str = (
                f"{num2words(m.group(1))} O'CLOCK {num2words(m.group(2))} MINUTES"
            )
            if m.group(3):
                time_str += f" {num2words(m.group(3))} SECONDS"
            filtered_sent.append(time_str.upper())
            continue

        if token in signs:
            filtered_sent.append(convert_signs_tok_to_word(token))
            continue

        if num_re.search(token):
            token = convert_num_tok_to_word(token)


        special_re = re.compile(r"[^A-Z ']+")
        filtered_sent.append(special_re.sub(' ', token.upper()).strip())

        
    return filtered_sent


def convert_signs_tok_to_word(word: str) -> str:
    if word == ">":
        return "GREATER THAN"
    if word == "<":
        return "LESS THAN"
    if word == "%":
        return "PERCENT"
    if word == "=":
        return "EQUAL TO"
    if word == "≤":
        return "LESS THAN OR EQUAL TO"
    if word == "≥":
        return "GREATER THAN OR EQUAL TO"
    if word == "+":
        return "PLUS"
    if word == "+-":
        return "PLUS MINUS"
    if word == "*":
        return "MULTIPLIED BY"
    
    return ""


def convert_num_tok_to_word(word: str) -> str:

    # special case:
    if word == "000000":
        return "MILLION"
    if word == "000":
        return "THOUSAND"
    if word == "00":
        return "Hundred"

    is_float, single_point = False, True
    idx = 0
    new_word = ""
    digits = ""

    while idx < len(word):
        if word[idx].isdigit():
            digits += word[idx]
        elif word[idx] == ".":

            digits += word[idx]
            if not is_float:
                is_float = True
            else:
                single_point = False

        elif word[idx] != ",":
            new_word = convert_digits(new_word, digits, is_float, single_point)
            digits = ""
            if single_point:
                sign_word = (
                    "OVER" if word[idx] == "/" and idx+1 < len(word) and word[idx+1].isdigit() else convert_signs_tok_to_word(word[idx])
                )

                if sign_word:
                    if new_word and new_word[-1] != ' ':
                        new_word = new_word + ' '
                    new_word += f"{sign_word}"
                    idx += 1
                    continue
            if escape_punct(word[idx]):
                if new_word and new_word[-1] != ' ':
                    new_word = new_word + ' '
                idx += 1
                continue
            new_word += word[idx].upper()
        idx += 1
    new_word = convert_digits(new_word, digits, is_float, single_point)
    if word[0] == '$':
        new_word += "Dollars"
    return new_word.strip()


def convert_num_to_word(line: str) -> str:
    return " ".join(convert_num_tok_to_word(word) for word in line.strip().split())


def convert_digits(new_word, digits, is_float, single_point) -> str:
    if single_point and len(digits) > 0:
        try:
            if (
                not is_float
                and str(int(digits)) == digits
                and 1900 < int(digits) < 2100
            ):
                new_word += (
                    " "
                    + num2words(digits, to="year")
                    .replace("-", " ")
                    .replace(",", "")
                    .upper()
                    + " "
                )
            else:
                if is_float and len(digits) > 1 or not is_float:
                    new_word += (
                        " "
                        + num2words(digits).replace("-", " ").replace(",", "").upper()
                        + " "
                    )
        except ValueError:
            print(f"Error in converting digits {digits}")
        except decimal.InvalidOperation:
            print(f"Error in converting digits {digits}")
        except ArithmeticError:
            print(f"Error in converting digits {digits}")
    return new_word
