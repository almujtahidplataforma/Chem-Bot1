"""Durable lecture notifications independent of group delivery."""
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

ZONE=ZoneInfo('Asia/Baghdad')


def lecture_markup(ns,row,group=False):
    rows=[]
    if not group:
        for lecture in map(int,row['lectures'].split(',')):
            entry=ns['PLAYLISTS'][row['chapter']][lecture-1]
            rows.append([ns['InlineKeyboardButton'](f'📖 {entry[1]}'[:60],callback_data=entry[2])])
            for title,url in ns.get('LECTURE_SUPPLEMENTS',{}).get((row['chapter'],lecture),[]):
                rows.append([ns['InlineKeyboardButton'](f'▶️ {title}'[:60],url=url)])
    rows.append([ns['InlineKeyboardButton']('📚 تحاضير اليوم',callback_data='today_prep')])
    return ns['InlineKeyboardMarkup'](rows)


def install(ns,db):
    lock=asyncio.Lock()
    async def sql(statement,args=(),one=False,write=False):
        def op():
            with db.connect() as conn,conn.cursor() as cur:
                cur.execute(statement,args)
                result=(cur.fetchone() if one else cur.fetchall()) if cur.description else None
                if write:conn.commit()
                return result
        return await db.run(op)
    old_init=db.init_db
    def init_db():
        old_init()
        with db.connect() as conn,conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS arabic_lecture_delivery(
                prep_no INTEGER NOT NULL REFERENCES arabic_preparations(prep_no) ON DELETE CASCADE,
                chat_id BIGINT NOT NULL,recipient_type TEXT NOT NULL,
                sent_at TIMESTAMPTZ,attempts INTEGER NOT NULL DEFAULT 0,last_error TEXT,
                retry_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(prep_no,chat_id,recipient_type));''')
            conn.commit()
    db.init_db=ns['init_db']=init_db

    async def enqueue(row):
        students=await ns['students_for_scope']('course')
        students=[s for s in students if await db.section_enabled(s['user_id'],'lectures')]
        def op():
            with db.connect() as conn,conn.cursor() as cur:
                recipients=[(s['user_id'],'student') for s in students if not s.get('admin_blocked') and not s.get('reset_pending')]
                if ns['ARABIC_GROUP_ID']:recipients.append((ns['ARABIC_GROUP_ID'],'group'))
                for uid,kind in recipients:
                    cur.execute('''INSERT INTO arabic_lecture_delivery(prep_no,chat_id,recipient_type)
                        VALUES(%s,%s,%s) ON CONFLICT DO NOTHING;''',(row['prep_no'],uid,kind))
                # Save recipient work before opening the lecture. An API error cannot lose it.
                cur.execute('''UPDATE arabic_preparations SET published=TRUE,
                    published_at=COALESCE(published_at,CURRENT_TIMESTAMP),needs_announcement=FALSE WHERE prep_no=%s;''',(row['prep_no'],))
                conn.commit()
        await db.run(op)

    async def publish(context):
        if lock.locked():return
        async with lock:
            for row in await ns['due_preparations'](datetime.now(ZONE)):
                await enqueue(row)
            # Recover the latest already-published lecture after installing the fix.
            # ON CONFLICT retains delivery receipts on every subsequent execution.
            latest=await sql('''SELECT * FROM arabic_preparations WHERE published=TRUE
                AND ((target_date-1)+TIME '23:00')<=%s ORDER BY target_date DESC,prep_no DESC LIMIT 1;''',
                (datetime.now(ZONE).replace(tzinfo=None),),one=True)
            if latest:await enqueue(latest)
            rows=await sql('''SELECT q.chat_id,q.recipient_type,p.* FROM arabic_lecture_delivery q
                JOIN arabic_preparations p ON p.prep_no=q.prep_no
                LEFT JOIN arabic_students s ON q.recipient_type='student' AND s.user_id=q.chat_id
                WHERE q.sent_at IS NULL AND q.retry_at<=CURRENT_TIMESTAMP AND p.published
                AND ((p.target_date-1)+TIME '23:00')<=%s
                AND (q.recipient_type='group' OR (s.approved AND NOT s.reset_pending
                     AND NOT s.admin_blocked AND s.study_track='course'))
                ORDER BY q.retry_at,p.target_date,q.chat_id LIMIT 100;''',(datetime.now(ZONE).replace(tzinfo=None),))
            for row in rows:
                group=row['recipient_type']=='group'
                if not group and not await db.section_enabled(row['chat_id'],'lectures'):continue
                if not group and await ns['student_exam_lock'](row['chat_id']):
                    await sql("UPDATE arabic_lecture_delivery SET retry_at=CURRENT_TIMESTAMP+INTERVAL '1 minute' WHERE prep_no=%s AND chat_id=%s AND recipient_type=%s;",
                              (row['prep_no'],row['chat_id'],row['recipient_type']),write=True)
                    continue
                try:
                    await context.bot.send_message(row['chat_id'],ns['preparation_text'](row),
                        parse_mode=ns['ParseMode'].HTML,
                        message_thread_id=(ns['PREPARATION_TOPIC_ID'] or None) if group else None,
                        reply_markup=lecture_markup(ns,row,group))
                    await sql('''UPDATE arabic_lecture_delivery SET sent_at=CURRENT_TIMESTAMP,last_error=NULL
                        WHERE prep_no=%s AND chat_id=%s AND recipient_type=%s;''',
                        (row['prep_no'],row['chat_id'],row['recipient_type']),write=True)
                except ns['TelegramError'] as exc:
                    ns['logger'].warning('Lecture delivery failed prep=%s recipient=%s',row['prep_no'],row['chat_id'])
                    await sql("""UPDATE arabic_lecture_delivery SET attempts=attempts+1,last_error=%s,
                        retry_at=CURRENT_TIMESTAMP+INTERVAL '5 minutes'
                        WHERE prep_no=%s AND chat_id=%s AND recipient_type=%s;""",
                        (str(exc)[:800],row['prep_no'],row['chat_id'],row['recipient_type']),write=True)
                    continue
                if not group:
                    for parent in await ns['student_parents'](row['chat_id'],True):
                        try:await context.bot.send_message(parent['parent_chat_id'],f"📚 وصل تحضير جديد للطالب {row['chat_id']} — الوحدة {row['chapter']}، المحاضرة {row['lectures']}.")
                        except ns['TelegramError']:ns['logger'].warning('Parent lecture notice failed')
    ns['publish_preparations_job']=publish
    old_personal=ns['personal_preparations_job']
    async def personal(context):
        # Preserve personal scheduling and existing retry/permission checks;
        # attach all lecture video parts to the successful delivery.
        class BotProxy:
            def __getattr__(self,name):return getattr(context.bot,name)
            async def send_message(self,chat_id,text,*args,**kwargs):
                row=active.get(chat_id)
                if row and 'تحضيرك الشخصي الجديد' in text:
                    kwargs['reply_markup']=lecture_markup(ns,row)
                return await context.bot.send_message(chat_id,text,*args,**kwargs)
        active={r['user_id']:r for r in await ns['due_personal_preparation_notifications'](datetime.now(ZONE))}
        class ContextProxy:
            bot=BotProxy()
            def __getattr__(self,name):return getattr(context,name)
        await old_personal(ContextProxy())
    ns['personal_preparations_job']=personal
    old_post=ns['post_init']
    async def post(app):
        await old_post(app)
        from course_schedule_v10 import migrate_future
        days=await migrate_future(db)
        if days:ns['_ADMIN_COURSE_DAYS']=days
    ns['post_init']=post
