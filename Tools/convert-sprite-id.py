"""
    Author: vakhet at gmail.com

Script converts Sprite ID to Sprite Constant, i.e. 8_F_GIRL -> 700

Place script and CONSTANT_FILE in Tools directory
Each line in CONSTANT_FILE should match regex '[A-Z0-9_]+'.
Before processing each file, backup is created in same dir.
Backup is deleted if there was 0 replaces.

Script tries to autodetect encoding for each file,
using cchardet https://github.com/PyYoshi/cChardet

For any bugs/feedback please contact me: vakhet@gmail.com
"""

from shutil import copy
from os import path, walk, remove
from re import compile, search, findall
import cchardet

# Setup

PATTERN = compile(r'^[\w\d_]+[0-9,]+\tscript\t[\w\d_ -]+#*[\w\d_ :-]*\t([A-Z0-9_]+)[\d,{]*$')
CONSTANT = {}
CONSTANT_FILE = 'npc_sprite_name_id_list.txt'
SCRIPT_PATH = ['../npc', ]


def grab_constants(file):
    global CONSTANT
    with open(file) as fh:
        for line in fh:
            const = findall(r'[A-Z0-9_]+', line)
            # 1_M_HOF : 52
            CONSTANT[const[0]] = const[1]


def grab_files():
    """
    Search for all files *.txt in npc directory recursively

    :return: list
    """
    result = []
    for directory in SCRIPT_PATH:
        for root, _, files in walk(directory):
            for file in files:
                if file.endswith('.txt'):
                    line = path.join(root, file)
                    result.append(line)
    return result


def get_encoding(file):
    """
    Try to guess file encoding

    :param file: str
    :return: (str, str)
    """
    with open(file, 'r+b') as fh:
        result = cchardet.detect(fh.read())
    return result['encoding'], result['confidence']


def process_line(line):
    test = search(PATTERN, line)
    if (test is None) or (test[1] not in CONSTANT.keys()):
        return line, False
    else:
        old_const = test[1]
        pos = line.rfind(old_const)
        new_line = line[:pos] + CONSTANT[old_const] + line[pos+len(old_const):]
        return new_line, True


def process(original, backup, encoding):
    count = 0
    with open(original, 'w', encoding=encoding) as file_out:
        with open(backup, 'r', encoding=encoding) as file_in:
            for line in file_in.readlines():
                new_line, replaced = process_line(line)
                file_out.writelines(new_line)
                if replaced:
                    count += 1
    return count


def main():
    npc_files = grab_files()
    grab_constants('npc_sprite_name_id_list.txt')
    for file in npc_files:
        print('Processing file:', file)
        original, backup = file, file + '.bak'
        encoding, confidence = get_encoding(file)
        encoding = 'utf-8' if confidence < 0.5 else encoding
        copy(original, backup)
        count = process(original, backup, encoding)
        if count == 0:
            remove(backup)
        print('Replaced constants: {}\n'.format(count))


if __name__ == '__main__':
    main()
