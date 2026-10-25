"""Booklet-page view preserving the existing study and exam completion flows."""
from data import PAGE_RANGES,CHAPTER_NAMES,page_description

def install(ns,db):
    B,K=ns['InlineKeyboardButton'],ns['InlineKeyboardMarkup']
    old_text=ns['preparation_text']
    def text(row):
        details='\n\n'.join(page_description(row['chapter'],int(n)) for n in row['lectures'].split(','))
        return old_text(row)+'\n\n'+ns['bold'](details)
    ns['preparation_text']=text
    old=ns['button_handler']
    async def button(update,context):
        q=update.callback_query
        if not (q.data or '').startswith('pages|'):return await old(update,context)
        try:
            _,ch,lec=q.data.split('|');ch,lec=int(ch),int(lec)
            description=page_description(ch,lec)
        except (ValueError,KeyError):
            await q.answer('هذا التحضير غير موجود.',show_alert=True);return
        student=await db.get_student(q.from_user.id)
        if not ns['is_admin'](q.from_user.id) and (not student or not student.get('approved') or student.get('admin_blocked') or student.get('reset_pending')):
            await q.answer('فعّل حسابك أولاً من /start.',show_alert=True);return
        # Viewing a page range never marks a lecture complete or bypasses an exam.
        await q.answer()
        await q.edit_message_text(ns['bold'](description+'\n\nادرس هذه الصفحات من نسختك من الملزمة، ثم ارجع إلى التحضير لتسجيل الإكمال.\nترقيم الصفحات خاص بهذا الموضوع. '),parse_mode=ns['ParseMode'].HTML,
            reply_markup=K([[B('📚 فتح التحضير وتسجيل الدراسة',callback_data=f'prepopen|{ch}|{lec}')],
                [B('📝 دراسة المحاضرة ضمن متطلبات الامتحان',callback_data=f'v55_exam_study|{ch}|{lec}')],
                [B('📑 محاضرات '+CHAPTER_NAMES[ch],callback_data=f'chapter|{ch}')],
                [ns['back_menu']()]]))
    ns['button_handler']=button
