from random import randrange, randint
from datetime import date, timedelta


def random_date(start, end):
    delta = end - start
    return start + timedelta(seconds=randrange(delta.total_seconds()))


def generate_identification_id(start_date, end_date):
    birthday = random_date(start_date, end_date)
    year = str(birthday.year)[2:]
    month = str(birthday.month).zfill(2)
    day = str(birthday.day).zfill(2)
    gender = str(randint(1, 998)).zfill(3)
    millenium_baby = birthday.year > 2000

    main_number = year + month + day + gender
    control_number = '2' + main_number if millenium_baby else main_number
    control_number = 97 - int(control_number) % 97
    control_number = str(control_number).zfill(2)

    return main_number + control_number


def identification_id_to_gender(identification_id):
    if identification_id and len(identification_id) == 11:
        gender = identification_id[6:9]
        return int(gender) % 2


INDENTITY_ID = generate_identification_id(date(1920, 1, 1), date(1995, 12, 31))
GENDER = identification_id_to_gender(INDENTITY_ID)
print('Rijksregisternummer: ' + INDENTITY_ID)
print('Geslacht: ' + ('Man' if GENDER else 'Vrouw'))
