from jsondecoder import JSONDecoder


if __name__ == '__main__':
    decoder = JSONDecoder('assets/input_3.json')


    decoder.print_structure(indentstep=3)