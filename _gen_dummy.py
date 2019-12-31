# For sample only, not for production use

import datetime
import hashlib
import os
import shutil

MAX_ARTICLE_PER_DAY = 3

YEAR_LIST = [2000,2002,2003]
MONTH_CHANCE = 0.5
DAY_CHANCE = 0.2
ARTICLE_CHANCE = 0.5

SHA_INT_END = int('f'*64,16)+1
# print(SHA_INT_END)

def main():
    shutil.rmtree('blogs', ignore_errors=True)
    for YEAR in YEAR_LIST:
        start_date = datetime.date(YEAR,1,1)
        end_date = datetime.date(YEAR+1,1,1)
        for date in date_range(start_date, end_date):
            if not good_hash_chance(date.strftime('%Y%m'), MONTH_CHANCE): continue
            if not good_hash_chance(date.strftime('%Y%m%d'), DAY_CHANCE): continue
            # print(date.strftime('%Y%m%d'))
            for article_idx in range(3):
                if not good_hash_chance(date.strftime('%Y%m%d')+str(article_idx), ARTICLE_CHANCE): continue
                yyyy = date.strftime('%Y')
                yyyymm = date.strftime('%Y-%m')
                yyyymmdd = date.strftime('%Y-%m-%d')
                yyyymmddaa = date.strftime('%Y-%m-%d') + '-' + str(article_idx).zfill(2)
                title = 'T' + hash(f'title-{yyyymmddaa}')[:12]
                content = 'content ' + hash(f'content-{yyyymmddaa}')
                tag_list = list(bin(int(hash(f'tag-{yyyymmddaa}')[-1:],16))[2:].zfill(4))
                tag_list = zip(range(len(tag_list)),tag_list)
                tag_list = filter(lambda i:i[1]!='0',tag_list)
                tag_list = map(lambda i:f'tag-{i[0]}',tag_list)
                tag_list = list(tag_list)
                file_path = os.path.join('blogs',yyyy,yyyymm,f'{yyyymmddaa}-{title}.html.jinja')
                if not os.path.isdir(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                with open(file_path, mode='wt') as fout:
                    fout.write('{% extends "article.html.jinja" %}\n')
                    fout.write('\n')
                    fout.write(f'{{% set date = "{yyyymmdd}" %}}\n')
                    fout.write(f'{{% set order = {article_idx} %}}\n')
                    fout.write(f'{{% set title = "{title}" %}}\n')
                    fout.write(f'{{% set tag_list = {tag_list} %}}\n')
                    fout.write('\n')
                    fout.write('{% block article %}\n')
                    fout.write(f'<p>{content}</p>\n')
                    fout.write('{% endblock %}\n')

def date_range(start_date, end_date):
    date = start_date
    while date < end_date:
        yield date
        date += datetime.timedelta(days=1)

def hash(s):
    m = hashlib.sha256()
    m.update(s.encode('utf8'))
    return m.hexdigest()

def good_hash_chance(s,c):
    s = hash(s)
    s = int(s,16)
    s = s / SHA_INT_END
    return s < c

main()
