import sqlite3

from . import ragna

conn = sqlite3.connect('item.sqlite')
db = conn.cursor()
# db.executescript(foo.DB_INIT)

ITEMDB_SCHEMA = [('id', 'INTEGER PRIMARY KEY'),
                 ('AegisName', 'TEXT'),
                 ('Name', 'TEXT'),
                 ('Type', 'INTEGER'),
                 ('Buy', 'INTEGER'),
                 ('Sell', 'INTEGER'),
                 ('Weight', 'INTEGER'),
                 ('ATK[:MATK]', 'TEXT'),
                 ('DEF', 'INTEGER'),
                 ('Range', 'INTEGER'),
                 ('Slots', 'INTEGER'),
                 ('Job', 'TEXT'),
                 ('Class', 'INTEGER'),
                 ('Gender', 'INTEGER'),
                 ('Loc', 'INTEGER'),
                 ('wLV', 'INTEGER'),
                 ('eLV[:maxLevel]', 'TEXT'),
                 ('Refineable', 'INTEGER'),
                 ('View', 'INTEGER'),
                 ('Script', 'TEXT'),
                 ('OnEquip_Script', 'TEXT'),
                 ('OnUnequip_Script', 'TEXT')]
# Stage 1.
# Read server-side items from itemdb.txt, store in db
with open('item_db.txt', encoding='utf8', errors='ignore') as file:
    ragna.rathena_db_parse('itemdb', ITEMDB_SCHEMA, file, db)
    conn.commit()
quit()
# Stage 2.
# Read client-side items from itemInfo_re.lua, store in db
ragna.read_iteminfo_lua('itemInfo_re.lua', db)
conn.commit()

# Stage 3
# Read translating from:
#   translate.txt - scripts
#   mobdb.txt - constants
#   skilldb.txt - constants
ragna.read_translate('translate.txt', db)
conn.commit()

# Translate
'''
db.execute("""SELECT id, script FROM itemdb""")
for row in db.fetchall():
    if foo.valid(row[1]):
        # translate script
        new_script = foo.translate(row[1])
        db.execute("""UPDATE itemdb SET script=? WHERE id=?""",
                   (new_script, row[0]))
conn.commit()
'''
# Ending
