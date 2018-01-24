"""
rAthena ASPD Calculator
"""
from math import sqrt
from re import findall
from os import path, system
from sys import platform


class JobDB:

    def __init__(self):
        self.jobs = dict()
        self.template = [
            ['JobID', 0],
            ['Weight', 0],
            ['HPFactor', 0],
            ['HPMultiplicator', 0],
            ['SPFactor', 0],
            ['Unarmed', 0],
            ['Dagger', 0],
            ['1HSword', 0],
            ['2HSword', 0],
            ['1HSpear', 0],
            ['2HSpear', 0],
            ['1HAxe', 0],
            ['2HAxe', 0],
            ['1HMace', 0],
            ['2HMace(unused)', 0],
            ['Rod', 0],
            ['Bow', 0],
            ['Knuckle', 0],
            ['Instrument', 0],
            ['Whip', 0],
            ['Book', 0],
            ['Katar', 0],
            ['Revolver', 0],
            ['Rifle', 0],
            ['Gatling Gun', 0],
            ['Shotgun', 0],
            ['Grenade Launcher', 0],
            ['Fuuma Shuriken', 0],
            ['2HStaff', 0],
            ['Shield', 0],
        ]

    def new_job(self, job_name, params):
        for i in range(len(self.template)):
            assert isinstance(params[i], int)
            self.template[i][1] = params[i]
        self.jobs[job_name] = {a: b for a, b in self.template}

    def aspd_base(self, jobid, weapon):
        return self.jobs[self[jobid]][weapon]

    def __getitem__(self, jobid):
        for job in self.jobs:
            if self.jobs[job]['JobID'] == jobid:
                return job
        return False

    def __str__(self):
        l, res = [], '\r'
        for job in self.jobs:
            l.append('{:<36}: {:4d}'.format(job, self.jobs[job]['JobID']))
        for i, s in enumerate(l):
            res += s + '\n' if (i+1) % 2 == 0 else s + ' || '
        return res


def read_db():
    job_db = JobDB()
    with open('job_db.txt') as file:
        for line in file.readlines():
            if line.startswith('//'):
                name = findall(r'// (.+)$', line.strip())[0]
            else:
                args = [int(s.strip()) for s in line.strip().split(',')]
                job_db.new_job(name, args)
    return job_db


def cap_value(a, min_, max_):
    """ common/utils.h:23 """
    """Check if 'a' fits in (min, max).
    If not - returns 'min' or 'max', respectively"""
    return max_ if a >= max_ else min_ if a <= min_ else a


def check_bonus1(flag):
    """ map/status.cpp:6789 status_calc_aspd() """
    """Calculate bonus from skills and statuses"""
    bonus = 0

    if flag:
        pass
    else:
        pass

    return bonus


def check_bonus2(aspd):
    """ map/status.cpp:6914 status_calc_fix_aspd() """
    """Modify aspd depending on various status changes"""
    pass
    return cap_value(aspd, 0, 2000)


def check_item_bonus(type_=None, val=None):
    """ map/pc.cpp:2725 pc_bonus() """
    """Modify aspd and rate depending on item bonus (equip, cards, etc)
    bonus bBonusName,val
          ^ type_,   ^ val"""
    aspd_add, aspd_rate2 = 0, 0
    """
    case SP_ASPD:
        if (sd->state.lr_flag != 2)
            sd->bonus.aspd_add -= 10 * val;
            break;
    case SP_ASPD_RATE:
        if (sd->state.lr_flag != 2)
            status->aspd_rate2 += val;
            break;
    """
    return aspd_add, aspd_rate2


def check_aspd_rate():
    """map/status.cpp:4010 status_calc_pc_()"""
    """Modify aspd rate depending on riding skills and SG_DEVIL"""
    aspd_rate = 1000

    if on_peco:
        aspd_rate -= 500 - 100 * KN_CAVALIERMASTERY
    elif on_dragon:
        aspd_rate -= 250 - 50 * RK_DRAGONTRAINING
    # if ((skill = pc_checkskill(sd, SG_DEVIL)) > 0 && pc_is_maxjoblv(sd))
    #     base_status->aspd_rate += 30 * skill;

    return aspd_rate


def base_aspd():
    """map/status.cpp:2354 status_base_amotion_pc()"""
    """Calculate base aspd depending on Job and Weapon"""
    base = JOB_DB.aspd_base(job_id, weapon1)  # Single weapon
    if weapon2 != 'Unarmed':
        if weapon2 == 'Shield':
            base += JOB_DB.aspd_base(job_id, weapon2)
        else:
            base += JOB_DB.aspd_base(job_id, weapon2) / 4  # Dual - wield
    return base


def main():
    """Main calculation"""
    aspd_add, aspd_rate2 = check_item_bonus()
    aspd_rate = check_aspd_rate()

    """ map/status.cpp:2346 status_base_amotion_pc()"""
    if weapon1 in ['Bow', 'Instrument', 'Whip', 'Revolver', 'Rifle',
                   'Gatling Gun', 'Shotgun', 'Grenade Launcher']:
        aspd = DEX ** 2 / 7.0 + AGI ** 2 * 0.5
    else:
        aspd = DEX ** 2 / 5.0 + AGI ** 2 * 0.5
    aspd = sqrt(aspd) * 0.25 + 196
    val = 0
    # if ((skill_lv = pc_checkskill(sd, SA_ADVANCEDBOOK)) > 0 && sd->status.weapon == W_BOOK)
    #     val += (skill_lv - 1) / 2 + 1;
    # if ((skill_lv = pc_checkskill(sd, GS_SINGLEACTION)) > 0 &&
    #         (sd->status.weapon >= W_REVOLVER & & sd->status.weapon <= W_GRENADE))
    #     val += ((skill_lv + 1) / 2);
    aspd = int(aspd + (check_bonus1(True) + val) * AGI / 200) - min(base_aspd(), 200)

    aspd = cap_value(aspd, PC_MAX_ASPD, 2000)

    """ map/status.cpp:5126 status_calc_bl_main()"""
    aspd = aspd * aspd_rate / 1000
    # if (sd->ud.skilltimer != INVALID_TIMER && (skill_lv = pc_checkskill(sd, SA_FREECAST)) > 0)
    #     amotion = amotion * 5 * (skill_lv + 10) / 100;
    aspd += max(195 - aspd, 2) * (aspd_rate2 + check_bonus1(False)) / 100
    aspd = 10 * (200 - aspd)
    aspd += aspd_add
    aspd = check_bonus2(aspd)
    aspd = cap_value(aspd, PC_MAX_ASPD, 2000)

    """ map/clif.cpp:14809 clif_check()"""
    # Final calculation -> send to client
    aspd = (2000 - aspd) / 10

    print('ASPD: ', aspd)


if __name__ == '__main__':
    CLEAR = 'cls' if platform == 'win32' else 'clear'
    WEAPONS = ['Unarmed', 'Dagger', '1HSword', '2HSword',
               '1HSpear', '2HSpear', '1HAxe', '2HAxe',
               '1HMace', '2HMace(unused)', 'Rod', 'Bow',
               'Knuckle', 'Instrument', 'Whip', 'Book',
               'Katar', 'Revolver', 'Rifle', 'Gatling Gun',
               'Shotgun', 'Grenade Launcher', 'Fuuma Shuriken',
               '2HStaff', 'Shield']
    SUMMARY = 'JobID: {}\n' \
              'Job:   {}\n' \
              'DEX:   {}\n' \
              'AGI:   {}\n' \
              'Main weapon: {} {}\n' \
              'Second weapon: {} {}\n' \
              'Riding peco: {} ({})\n' \
              'Riding dragon: {} ({})\n'

    if not path.isfile('job_db.txt'):
        print('Please put job_db.txt in same directory with ' + __file__)
        exit()

    JOB_DB = read_db()

    system(CLEAR)
    print('Available jobs:\n', JOB_DB, '\n')
    print('Available weapons:\n', WEAPONS, '\n')
    job_id = int(input('Job ID: '))
    assert JOB_DB[job_id], 'Invalid ID: %r' % job_id

    weapon1 = input('Weapon Main: ')
    assert weapon1 in WEAPONS, 'Invalid weapon: %r' % weapon1

    weapon2 = input('Weapon Second (press Enter for Unarmed): ')
    weapon2 = weapon2 if weapon2 else 'Unarmed'
    assert weapon2 in WEAPONS, 'Invalid weapon: %r' % weapon2

    DEX = int(input('DEX: '))
    assert 0 < DEX < 200, 'DEX should be in (0, 200)'

    AGI = int(input('AGI: '))
    assert 0 < AGI < 200, 'AGI should be in (0, 200)'

    on_peco = bool(int(input('Is riding peco? (1/0) ')))
    if on_peco:
        KN_CAVALIERMASTERY = int(input('Cavalier Mastery lvl: '))
        on_dragon = False
        RK_DRAGONTRAINING = 0
    else:
        KN_CAVALIERMASTERY = 0
        on_dragon = bool(int(input('Is riding dragon? (1/0) ')))
        if on_dragon:
            RK_DRAGONTRAINING = int(input('Dragon Training lvl: '))
        else:
            RK_DRAGONTRAINING = 0

    PC_MAX_ASPD = 193 if job_id >= 4054 else 190
    PC_MAX_ASPD = 2000 - PC_MAX_ASPD * 10

    system(CLEAR)
    print(SUMMARY.format(job_id, JOB_DB[job_id], DEX, AGI,
                         weapon1, JOB_DB.aspd_base(job_id, weapon1),
                         weapon2, JOB_DB.aspd_base(job_id, weapon2),
                         on_peco, KN_CAVALIERMASTERY,on_dragon, RK_DRAGONTRAINING))

    main()
