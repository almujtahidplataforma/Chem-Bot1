from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
CHAPTER_COUNT=5
CHAPTER_NAMES={1:'الاستفهام',2:'النفي',3:'التقديم والتأخير',4:'التوكيد',5:'النداء'}
BOOKLET_NAME='ملزمة عقيل الزبيدي — القواعد'
TOPIC_PAGES={1:118,2:154,3:62,4:82,5:28}
PAGES_PER_LECTURE={1:8,2:10,3:6,4:6,5:6}
PAGE_RANGES={}
for chapter,total in TOPIC_PAGES.items():
    size=PAGES_PER_LECTURE[chapter]
    for i,start in enumerate(range(1,total+1,size),1):
        PAGE_RANGES[(chapter,i)]=(start,min(total,start+size-1))
# The requested third vocative preparation explicitly includes page 12.
PAGE_RANGES[(5,3)]=(12,18)
PLAYLISTS={ch:[(lec,f'{CHAPTER_NAMES[ch]} — ص {a}–{b}',f'pages|{ch}|{lec}')
    for (c,lec),(a,b) in PAGE_RANGES.items() if c==ch] for ch in CHAPTER_NAMES}
LECTURE_SUPPLEMENTS={}
CHAPTER_PREPARATION_DISTRIBUTION={ch:[[n] for n,_,_ in items] for ch,items in PLAYLISTS.items()}
PREPARATIONS={}
NEXT_PREPARATIONS=[]
COURSE_DAYS=[0,2,3]
COURSE_START=(3,1)

def page_description(chapter,lecture):
    a,b=PAGE_RANGES[(int(chapter),int(lecture))]
    return f'{BOOKLET_NAME}\n{CHAPTER_NAMES[int(chapter)]} — المحاضرة {lecture}\n📖 من ص {a} إلى ص {b}'

def page_button_target(item):
    return {'callback_data':item[2]}

def initial_course_rows(first_date=None):
    day=first_date or datetime.now(ZoneInfo('Asia/Baghdad')).date()
    rows=[];number=0
    for ch in sorted(CHAPTER_NAMES):
        for lec,_,_ in PLAYLISTS[ch]:
            number+=1
            if (ch,lec)<COURSE_START:continue
            while day.weekday() not in COURSE_DAYS:day+=timedelta(days=1)
            rows.append((number,day,str(lec),ch,lec))
            day+=timedelta(days=1)
    return rows
