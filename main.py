from CYKParser import CYKParser


def main():
    parser = CYKParser()
    parser.read_grammar('Grammar.txt')
    while True:
        input_string = input()
        if input_string == 'end':
            break
        else:
            if parser.parse(input_string):
                print('The input string is accepted.')
            else:
                print('The input string is not accepted.')


if __name__ == '__main__':
    main()
