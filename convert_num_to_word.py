from num2words import num2words
import decimal
import string
import re
from spacy import Language


def escape_token(tok: str):

    if not tok:
        return True
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
    if not tok.isascii():
        return True

    if tok in punct:
        return True


def convert_sent_to_word(sent: str, nlp: Language):

    signs = set(["/", "%", "=", ">", "<", "+", "+-", "≤", "≥", "*"])
    filtered_sent = []
    time_re = re.compile(r"^([01]\d|2[0-4]):([0-5]\d):?([0-5]\d)?$")
    num_re = re.compile(r"[0-9]+")

    for token in nlp(sent):

        text = token.text
        if escape_token(text) or token.like_url:
            continue
        if text == ">" and filtered_sent and filtered_sent[-1] == "EQUAL TO":
            filtered_sent[-1] = "TO"
            continue

        if text[0] == "'" and filtered_sent:
            filtered_sent[-1] += text.upper()
            continue

        m = time_re.match(text)
        if m:
            time_str = (
                f"{num2words(m.group(1))} O'CLOCK {num2words(m.group(2))} MINUTES"
            )
            if m.group(3):
                time_str += f" {num2words(m.group(3))} SECONDS"
            filtered_sent.append(time_str.upper())
            continue

        if text in signs:
            filtered_sent.append(convert_signs_tok_to_word(text))
            continue
        if num_re.search(text):
            filtered_sent.append(convert_num_tok_to_word(text))
            continue
        filtered_sent.append(text.strip(string.punctuation + " +- ").upper())
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
                    "OVER" if word[idx] == "/" else convert_signs_tok_to_word(word[idx])
                )

                if sign_word:
                    new_word += f"{sign_word}"
                    idx += 1
                    continue
            if escape_token(word[idx]):
                new_word += " "
                idx += 1
                continue
            new_word += word[idx].upper()
        idx += 1
    new_word = convert_digits(new_word, digits, is_float, single_point)
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
