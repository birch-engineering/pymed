from num2words import num2words
import decimal


def convert_num_to_word(line):
    new_line = []
    words = line.strip().split()

    for word in words:
        if word == "000000":
            new_word = "MILLION"
        elif word == "000":
            new_word = "THOUSAND"
        elif word == "00":
            new_word = "Hundred"
        elif word == ">":
            new_word = "GREATER THAN"
        elif word == "<":
            new_word = "LESS THAN"
        elif word == "%":
            new_word = "PERCENT"
        elif word == '/':
            new_word = 'OR'
        else:
            new_word = ""
            digits = ""
            idx = 0
            is_float, is_number = False, False
            
            while idx < len(word):

                if word[idx].isdigit():
                    digits += word[idx]
                    is_number = True
                elif word[idx] == ".":

                    digits += word[idx]
                    if not is_float:
                        is_float = True
                    else:
                        is_number = False

                elif word[idx] != ",":
                    new_word = convert_digits(new_word, digits, is_float, is_number)
                    digits = ""
                    if is_number :
                        if word[idx] == '/':
                            new_word += "OVER"
                            idx +=1
                            continue
                        elif word[idx] == '%':
                            new_word += "PERCENT"
                            idx +=1
                            continue
                    
                    new_word += word[idx]

                idx += 1

        new_word = convert_digits(new_word, digits, is_float, is_number)
        digits = ""
        new_line.append(new_word)
    return " ".join(new_line)


def convert_digits(new_word, digits, is_float, is_number):
    if is_number and len(digits) > 0:
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
