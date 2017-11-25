"""
    Author : vakhet at gmail.com

This script gets all your NPC names from the original rAthena folder
and updates their lines in navi_npc_krpri.lub
wherever matches the map_name and coords
"""

import re
import os
import random
import sqlite3

NPC_match = r'^[\w\d_]+,\d+,\d+,\d+\tscript\t[\w\d_ -]+#*[\w\d_ -]*\t[\d,{]+$'
allfiles = []
log = open('result.log', 'w', errors='ignore')
conn = sqlite3.connect('db.sqlite')
db = conn.cursor()

intro = '''
Renew navi_npc_krpri.lub | Version 0.2 | (C) 2017 vakhet @ gmail.com

Changes:
  v0.2 - *.new file now creates in same folder with original *.lub
'''

outro = '''
Check results in result.log
NEW file generated: navi_npc_krpri.new
'''

db.executescript('''
DROP TABLE IF EXISTS npc;

CREATE TABLE npc (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    map TEXT,
    thing1 INTEGER,
    thing2 INTEGER,
    thing3 INTEGER,
    name TEXT,
    shadow TEXT,
    x INTEGER,
    y INTEGER
)
''')


def parse_npc(line):
    ln = line.split(',')
    map_name, x, y = ln[0], int(ln[1]), int(ln[2])
    fullname = ln[3].split('\t')
    fullname = fullname[2]
    if re.search('#', fullname):
        ln = fullname.split('#')
        name = ln[0]
        shadow = ln[1]
        # print(line,'\n',shadow,'<\n=====')
    else:
        name = fullname
        shadow = ''
    return name, map_name, x, y, shadow


def parse_navi(line):
    line = re.sub('^.*{\s*', '', line)
    line = re.sub('\s*}.*$', '', line)
    line = line.split(', ')
    for i in range(len(line)):
        line[i] = re.sub('"', '', line[i], count=2)
        try:
            line[i] = int(line[i])
        except ValueError:
            pass
    return tuple(line)


def stage_1():
    for root, dirs, files in os.walk(path_rathena):
        for file in files:
            if file.endswith('.txt'):
                line = os.path.join(root, file)
                allfiles.append(line)


def stage_2():
    fh = open(path_navi+'\\navi_npc_krpri.lub', 'r', errors='ignore')
    for line in fh.readlines():
        navi = parse_navi(line)
        if len(navi) != 8:
            continue
        db.execute('''INSERT INTO npc 
            (map, thing1, thing2, thing3, name, shadow, x, y) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', navi)
    conn.commit()
    fh.close()


def stage_3():
    total, updated = 0, 0
    print('Working... ', end='')
    for file in allfiles:
        fh = open(file, 'r', errors='ignore')
        for line in fh.readlines():
            print('\b'+chr(random.randint(65, 122)), end='')
            if re.match(NPC_match, line) is None:
                continue
            npc = parse_npc(line)
            total = total + 1
            db.execute('''SELECT COUNT(id), id, name, map, x, y, shadow FROM npc 
                WHERE map=? AND x=? AND y=?''', (npc[1], npc[2], npc[3]))
            sql = db.fetchone()
            if sql[0] == 0 or (sql[2] == npc[0] and sql[6] == npc[4]):
                continue
            log.writelines('({},{},{}) {} -> {}#{}\n'.format(
                sql[3], str(sql[4]), str(sql[5]), sql[2], npc[0], npc[4]))
            db.execute('UPDATE npc SET name=?, shadow=? WHERE id=?',
                       (npc[0], npc[4], sql[1]))
            conn.commit()
            updated += 1
        fh.close()
    log.close()
    print('\bOK!')
    print('Found {} NPC definitions (warps not included)'.format(total))
    print('Updated {} NPC names'.format(updated))


def stage_4():
    file = open(path_navi+'navi_npc_krpri.new', 'w', errors='ignore')
    file.writelines('Navi_Npc = {\n')
    sql = db.execute('SELECT * FROM npc WHERE thing1<>0 ORDER BY map, thing1')
    for row in sql:
        line = '\t{ '
        for i in range(1, 9):
            try:
                item = str(row[i])
            except (ValueError, TypeError):
                pass
            if i in (1, 5, 6):
                item = '"{}"'.format(row[i])
            line += item + ', '
        line = line[:-2] + ' },\n'
        file.writelines(line)
    file.writelines('\t{ "NULL", 0, 0, 0, "", "", 0, 0 }\n}\n\n')
    file.close()


# The Beginning
print(intro)

while True:
    path_rathena = input('Enter path to NPC: ')
    if not os.path.exists(path_rathena):
        print('Wrong path!\n\n')
        continue
    else:
        break

while True:
    path_navi = input('Enter path to navi_npc_krpri.lub: ')
    if not os.path.exists(path_navi+'\\navi_npc_krpri.lub'):
        print('Wrong path!\n\n')
        continue
    else:
        break

stage_1()   # scan for *.txt in \npc directory
stage_2()   # build DB from navi_npc_krpri.lub
stage_3()   # update NPC names in DB from *.txt
stage_4()   # building navi_npc_krpri.new

print('Complete list of changes see in log.txt')
print('NEW file generated: navi_npc_krpri.new')
input('\nPress any key')
