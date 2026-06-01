from sys import exit
def error(line, i, type, text):
    print(f"{type}Error on line {line + 1}, index {i + 1}: {text}")
    exit()