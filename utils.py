import random


def gen_hash():
    return random.getrandbits(128)

def gen_unic_filename(filename):
    ext = filename.split('.')[-1]
    return f'{gen_hash()}.{ext}'

if __name__ == '__main__':
    print(gen_hash())