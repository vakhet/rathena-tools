import re


def read_lua():
    PATTERN = r'\s*\[(?P<id>\d+)\] = {\s*unidentifiedDisplayName = ' \
              r'"(?P<unidentifiedDisplayName>[^"]+)",\s*unidentifie' \
              r'dResourceName = "(?P<unidentifiedResourceName>[^"]+' \
              r')",\s*unidentifiedDescriptionName = {\s*"(?P<uniden' \
              r'tifiedDescriptionName>[^=]+)"\s*},\s*identifiedDisp' \
              r'layName = "(?P<identifiedDisplayName>[\S ]+)",\s*id' \
              r'entifiedResourceName = "(?P<identifiedResourceName>' \
              r'[\S ]+)",\s*identifiedDescriptionName = {\s*"(?P<id' \
              r'entifiedDescriptionName>[^=]+)"\s*},\s*slotCount = ' \
              r'(?P<slotCount>\d{1}),\s*ClassNum = (?P<ClassNum>\d{' \
              r'1})\s*}'
    
    PATTERN = re.compile(PATTERN)
    with open('testcase.txt', encoding='utf8', errors='ignore') as file:
        test = PATTERN.findall(file.read())
    for item in test:
        if item[0] == '502':
            print(item)
    print(len(test))
    return 0

"""
for group in test.groupdict():
    for k, v in group.items():
        print(k + ' : ' + v)
    print()
"""

read_lua()