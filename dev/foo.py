from re import search, findall, split, match


def valid(line):
    if any(i in line for i in INVALID) or line == '':
        return False
    return True


def rathena_db_parse(table, schema, file, db):
    # Parse any *db.txt from rAthena
    #   table  - table's name
    #   schema - [('id', 'INTEGER PRIMARY KEY'), ('name', 'TEXT'), etc...]
    #   file   - file handler
    #   db     - sqlite3 db handler

    table_init = 'DROP TABLE IF EXIST {0}; CREATE TABLE {0} ('.format(table)
    for column in schema:
        table_init += '{0} {1}, '.format(*column)
    table_init = table_init.rstrip(', ') + ')'
    db.executescript(table_init)
    for line in file.readlines():
        if len(line.split(',')) != len(schema.keys()):
            continue
        row = [i.strip() for i in line.split(',')]
        row_script = 'INSERT OR IGNORE INTO {} VALUES ('.format(table)
        for column in row:
            row_script += '{}, '.format(column)
        row_script = row_script.rstrip(', ') + ')'
        db.execute(row_script)
        """
        if not line[0].isdigit():
            continue
        # get scripts - last 3 parameters
        line, tail = line.split(',{', 1)
        tail = tail.split('},{')
        tail[2] = tail[2][:-2]
        for i in (0, 1, 2):
            tail[i] = tail[i].strip()
        line = line.split(',')
        # handling values with ':'
        if ':' in line[16]:
            tmp = line[16].split(':')
            line[16] = tmp[1]
            line.insert(16, tmp[0])
        else:
            line.insert(17, '')
        if ':' in line[7]:
            tmp = line[7].split(':')
            line[7] = tmp[1]
            line.insert(7, tmp[0])
        else:
            line.insert(8, '')
        # converting num strings to integers
        for i in range(len(line)):
            try:
                line[i] = int(line[i])
            except Exception:
                pass
        line += tail
        db.execute('''INSERT INTO itemdb VALUES (?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', tuple(line))
        """


def read_iteminfo_lua(file, db):
    with open(file, 'r', encoding='cp1251', errors='ignore') as fh:
        for line in fh.readlines()[1:-1]:
            if line[0] == '}':
                break
            if line[1] == '[':
                item = {}
                item['id'] = int(search('\d+', line)[0])
                continue
            elif line[1] == '}':
                item['slotCount'] = int(item['slotCount'])
                item['ClassNum'] = int(item['ClassNum'])
                item['unidentifiedDescriptionName'] = ''.join(i+'___'
                    for i in item['unidentifiedDescriptionName']).rstrip('___')
                item['identifiedDescriptionName'] = ''.join(i+'___'
                    for i in item['identifiedDescriptionName']).rstrip('___')
                try:
                    db.execute('''INSERT INTO item_desc VALUES
                               (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               tuple(item.values()))
                except Exception:
                    print('count:', len(item), '\n', item, '\n========')
                    quit()
                continue
            tab = len(findall('\t', line))
            if tab == 2 and search('},$', line) is None:
                s = search('\t+(.+) = (.+)', line)
                if s[2][0] == '"':
                    item[s[1]] = s[2][:-1].strip('"')
                elif s[2][0] == '{':
                    item[s[1]] = []
                else:
                    item[s[1]] = s[2].rstrip(',')
                continue
            elif tab == 3:
                item[s[1]].append(search('"(.*)"', line)[1])
                continue


def read_translate(file, db):
    with open(file, 'r', encoding='utf8', errors='ignore') as fh:
        line = ''
        while not line.startswith('[variable]'):
            line = fh.readline()
        while not line.startswith('[script]'):
            line = fh.readline()
            if match('[A-Z]', line):
                variable = line.strip().split(maxsplit=1)
                db.execute("INSERT OR IGNORE INTO variables VALUES (?, ?)",
                           tuple(variable))
        while not line.startswith('[other]'):
            line = fh.readline()
            if match('[a-z]', line):
                script, translate = split(';[\s]*', line, maxsplit=1)
                name, variables = split(',', script, maxsplit=1)
                db.execute("INSERT OR IGNORE INTO scripts VALUES (?, ?, ?)",
                           (name, variables, translate.strip()))


def translate(script):
    global db
    name, var = script.split(',', maxsplit=1)
    db.execute("""SELECT var, translate FROM scripts WHERE name=?""",
               name)
    row = db.fetchone()
    try:
        translate = row[1].format(*var)
    except Exception:
        translate = script
    return translate


INVALID = ('@', 'getrefine', 'readparam', 'readParam', 'autobonus', 'getskill',
           'getgroupitem', 'getrandgroupitem', 'callfunc', 'getitem',
           'rentitem', 'monster ', 'pet ', 'Roulette', 'specialeffect',
           'mercenary_create', 'getcharid', 'rand(', 'itemheal', 'produce',
           'if(', 'if (', '/*', 'min('
           )

DB_INIT = ("""
DROP TABLE IF EXISTS itemdb;
DROP TABLE IF EXISTS item_desc;
DROP TABLE IF EXISTS variables;
DROP TABLE IF EXISTS scripts;

CREATE TABLE itemdb (
    ID INTEGER PRIMARY KEY,
    AegisName TEXT,
    Name TEXT,
    Type INTEGER,
    Buy INTEGER,
    Sell INTEGER,
    Weight INTEGER,
    ATK INTEGER,
    MATK INTEGER,
    DEF INTEGER,
    Range INTEGER,
    Slots INTEGER,
    Job INTEGER,
    Class INTEGER,
    Gender INTEGER,
    Loc INTEGER,
    wLV INTEGER,
    eLV INTEGER,
    maxLevel INTEGER,
    Refineable INTEGER,
    View INTEGER,
    Script TEXT,
    OnEquip_Script TEXT,
    OnUnequip_Script TEXT
);

CREATE TABLE item_desc (
    ID INTEGER PRIMARY KEY,
    unidentifiedDisplayName TEXT,
    unidentifiedResourceName TEXT,
    unidentifiedDescriptionName TEXT,
    identifiedDisplayName TEXT,
    identifiedResourceName TEXT,
    identifiedDescriptionName TEXT,
    slotCount INTEGER,
    ClassNum INTEGER
);

CREATE TABLE variables (
    original TEXT UNIQUE,
    translate TEXT
);

CREATE TABLE scripts (
    name TEXT UNIQUE,
    var TEXT,
    translate TEXT
)
""")
