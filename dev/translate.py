"""
Docstring
"""

import mysql.connector as mysql
from mysql.connector import errorcode
import re

CONNECTION = {'user': 'ragnarok',
              'password': '[eqcj,fxbq',
              'db': 'ragnarok',
              'host': '127.0.0.1',
              'port': '3306'}

SQL_CREATION = """
    DROP TABLE IF EXISTS translate;
    CREATE TABLE translate (
        id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        name TEXT,
        text TEXT(50) CHARACTER SET cp1251) ENGINE=MyISAM;

    DROP TABLE IF EXISTS lua;
    CREATE TABLE lua (
        id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        unidentifiedDisplayName TEXT,
        unidentifiedResourceName TEXT,
        unidentifiedDescriptionName TEXT,
        identifiedDisplayName TEXT,
        identifiedResourceName TEXT,
        identifiedDescriptionName TEXT,
        slotCount TINYINT,
        ClassNum TINYINT ) ENGINE=MyISAM;
    """

SQL_CREATE_BACKUP = """
    INSERT INTO script_backup (id, script, equip_script, unequip_script)
        SELECT id, script, equip_script, unequip_script FROM item_db_re;
    """


def create_tables():
    # Create tables `translation` and `lua`
    query = CUR.execute(SQL_CREATION, multi=True)
    for _ in query:
        pass
    CNX.commit()


def fill_translate():
    with open('translate.txt') as file:
        for line in file.readlines():
            if line.startswith('bonus'):
                name = line[:line.find(',')]
                text = re.findall(r'\t[ ]*(.+)\s*$', line)[0]
                CUR.execute('INSERT INTO translate (name, text)'
                            'VALUES (%s, %s)', (name, text.strip()))
    CNX.commit()


def read_lua():
    PATTERN = r'\[(?P<id>\d+)\] = {\s+unidentifiedDisplayName = ' \
              r'"(?P<unidentifiedDisplayName>[^"]+)",\s+unidenti' \
              r'fiedResourceName = "(?P<unidentifiedResourceName' \
              r'>[\S ]+)",\s+unidentifiedDescriptionName = {\s+"' \
              r'(?P<unidentifiedDescriptionName>[^=]+)"\s+},\s+i' \
              r'dentifiedDisplayName = "(?P<identifiedDisplayNam' \
              r'e>[\S ]+)",\s+identifiedResourceName = "(?P<iden' \
              r'tifiedResourceName>[\S ]+)",\s+identifiedDescrip' \
              r'tionName = {\s+"(?P<identifiedDescriptionName>[^' \
              r'=]+)"\s+},\s+slotCount = (?P<slotCount>\d{1}),\s' \
              r'+ClassNum = (?P<ClassNum>\d{1})\s+},'
    PATTERN = re.compile(PATTERN)
    with open('itemInfo_re.lua', encoding='cp1251', errors='ignore') as file:
        test = PATTERN.match(file.read())
    print(test.groupdict())


def make_lua():
    """
    [id] = {
        unidentifiedDisplayName = "",
        unidentifiedResourceName = "",
        unidentifiedDescriptionName = "",
        identifiedDisplayName = "",
        identifiedResourceName = "",
        identifiedDescriptionName = "",
        slotCount = 0,
        ClassNum = 0
        }
    :return:
    """
    pass


def translate(script, text):
    args = script.split(',')[1:]
    for i, arg in enumerate(args):
        try:
            args[i] = int(arg)
        except ValueError:
            continue
    try:
        result = text.format(*args)
    except ValueError:
        result = script
        #print(script + r' || ' + text)
    return result


if __name__ == '__main__':

    # Connect to DB
    try:
        CNX = mysql.connect(**CONNECTION)
        CUR = CNX.cursor()
    except mysql.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('MySql: Wrong username or password')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('MySql: Database does not exist')
        print('Check "Setup" section in this script')
        quit()

    # create_tables()
    # fill_translate()

    # Translate goes here
    CUR.execute('SELECT id, script FROM test WHERE script like "%bonus%"')
    all_scripts = CUR.fetchall()
    CUR.execute('SELECT DISTINCT name FROM translate')
    translated = [i[0] for i in CUR.fetchall()]
    for id, script in all_scripts:
        # Check for bonus_script
        bonus_script = []
        if 'bonus_script' in script:
            bonus = re.findall(r'bonus_script( ".*"[A-Z0-9,_]*);', script)[0]
            script = re.sub(bonus, '', script)
        many = re.findall(r'([\S ]+? [\S]+);', script)
        new, flag = '', False
        for one in many:
            if not re.match(r'bonus[^_]', one):
                new += one + '; '
                continue
            if 'bonus_script' == one:
                new += one + bonus + '; '
                continue
            name = re.findall(r'^([\S ]+),', one)
            if name[0] not in translated:
                new += one + '; '
                continue
            flag = True
            CUR.execute('SELECT text FROM translate WHERE name=%s', (name[0], ))
            text = CUR.fetchone()
            new += translate(one, text[0]) + '; '
        if flag:
            CUR.execute('UPDATE test SET flag = true, test = %s WHERE id = %s',
                        (new.rstrip(), id))
    CNX.commit()
    CNX.close()
