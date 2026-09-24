"""المحتوى الثابت لبوت الكيمياء: التحاضير وقوائم التشغيل."""

PREPARATIONS = {
    3: [4, 5], 4: [6], 5: [7], 6: [8, 9], 7: [10],
    8: [11, 12], 9: [13], 10: [14, 15], 11: [16, 17],
    12: [18], 13: [19], 14: [20], 15: [21], 16: [22], 17: [23, 24],
}

# (الفصل، رقم التحضير داخل الفصل، المحاضرات). الفصل السابع بلا تحاضير آلية.
NEXT_PREPARATIONS = [
    *[(4,i,v) for i,v in enumerate([[1],[2,3],[4],[5],[6],[7],[8],[9],[10],[11,12],[13]],1)],
    *[(5,i,v) for i,v in enumerate([[1],[2,3],[4],[5],[6],[7]],1)],
    *[(6,i,[i]) for i in range(1,10)],
]


# التوزيع المعتمد للتحاضير — يُستخدم لبناء المسارات الجديدة وربط الامتحانات بالتحضير.
# الفصل 1 و2: التوزيع الجديد الذي حدده الأستاذ.
# الفصل 3: التوزيع القديم الموجود في البوت، دون تغييره.
CHAPTER_PREPARATION_DISTRIBUTION = {
    1: [
        [1], [2], [3, 4], [5], [6], [7], [8, 9], [10], [11], [12],
        [13], [14], [15], [16, 17], [18], [19, 20],
    ],
    2: [
        [1], [2], [3], [4], [5], [6, 7], [8], [9, 10], [11], [12],
        [13, 14], [15], [16, 17],
    ],
    # شمول المحاضرات 1-3 التي كانت ساقطة من الجدول القديم.
    3: [[1], [2], [3], *[list(v) for v in PREPARATIONS.values()]],
}

# الفصلان 4–6 يبقيان على التوزيع السابق.
for _chapter in (4, 5, 6):
    _groups = [v for ch, _, v in NEXT_PREPARATIONS if ch == _chapter]
    CHAPTER_PREPARATION_DISTRIBUTION[_chapter] = [list(v) for v in _groups]

# الفصل السابع كان موجوداً في قائمة التشغيل لكنه غير قابل للدراسة تلقائياً.
CHAPTER_PREPARATION_DISTRIBUTION[7] = [[i] for i in range(1,12)]

CHAPTER_1 = [
    (1, "الديناميكا الحرارية (الثرموداينمك).", "https://youtu.be/00sbo5VzlKM?si=zzVZBUCGrpLOp3ce"),
    (2, "الحرارة ودرجة الحرارة.", "https://youtu.be/yesMWC_CbZg?si=Ny6pA7vc73GchjKM"),
    (3, "استكمال حل مسائل الحرارة ودرجة الحرارة.", "https://youtu.be/4e5mLSRWH3A?si=IJ96FPK3xe8z7Fzv"),
    (4, "دالة الحالة ودالة المسار.", "https://youtu.be/frMxzGzxFl8?si=omlLvhIPUeW4A_OA"),
    (5, "حل أسئلة المسعر.", "https://youtu.be/cqqC5YWKttg?si=8U3OXjalUa7GKKVv"),
    (6, "استكمال مسائل المسعر.", "https://youtu.be/_bVmy8WiDTQ?si=dELkUni2B8LT5xMy"),
    (7, "إنثالبي التكوين القياسي.", "https://youtu.be/QhL-4Fsku6Y?si=LDV63uor2sOHPURn"),
    (8, "إنثالبي الاحتراق القياسي.", "https://youtu.be/QXi_PusNd4A?si=O7mugdMhOvAui0Bb"),
    (9, "إنثالبي التغيرات الفيزيائية.", "https://youtu.be/GSr-_8v11KU?si=rRztZikCnCY0wKaG"),
    (10, "حل معادلات قانون هيس.", "https://youtu.be/gxYQbjyxNpY?si=F1-E1EMkt0BEdp_5"),
    (11, "استكمال حل معادلات قانون هيس – الجزء الأول.", "https://youtu.be/e206CU4MIgg?si=tVs1rGqsKhGBNCdE"),
    (12, "استكمال حل معادلات قانون هيس – الجزء الثاني.", "https://youtu.be/UPv8LuKYHTI?si=TyFYEEWNp7rXofqB"),
    (13, "طريقة حساب ΔHᵣ°.", "https://youtu.be/GyVA21RKlak?si=VIZf5cpZp82kV6HD"),
    (14, "العمليات التلقائية والإنتروبي.", "https://youtu.be/OAxqnir5aFc?si=lHVasHSicZK9qfNH"),
    (15, "طريقة حساب ΔSᵣ°.", "https://youtu.be/fiN-jN-qWK4?si=x-JAXNIVLpxkkN7t"),
    (16, "الأسئلة الثلاثية: ΔHᵣ°، ΔSᵣ°، ΔGᵣ°.", "https://youtu.be/E0QeNnD8ePA?si=N3SOywACG9A7sHSE"),
    (17, "حل الأسئلة الخارجية والوزارية لموضوع الأسئلة الثلاثية.", "https://youtu.be/J7hAN-2yKt4?si=v_fZNbOkPcZX73sL"),
    (18, "استكمال حل الأسئلة الثلاثية.", "https://youtu.be/Q0TNVN1SHes?si=fDv2yMyZ9C570IXt"),
    (19, "تطبيقات على علاقة جبس (ΔGᵣ°).", "https://youtu.be/mQdGl22WYAM?si=o8Zhu4I87mAAqRPJ"),
    (20, "حساب إنتروبي التغيرات الفيزيائية.", "https://youtu.be/maK-XRWct0o?si=yyf2d87XETqiY6Sh"),
]

CHAPTER_2_URLS = [
    "feZP9bMIdoA", "JwDpIPdp9f0", "AQfuSKIVnQ4", "rw_wP59v2f4", "XydWrHm2BhQ",
    "DiBDN_oW3GY", "i2qdroMZk14", "lJzEPCzdxVo", "ua5iG4fVAHQ", "d6Ypf6yeYI8",
    "sFWCXrilXwo", "SGXof_5Oh5E", "z6ePFsIQdoE", "W4U1qsS7DuE", "HKDB6HHL_ao",
    "oYp0yLcmYDI", "KZ1qulTo5T8",
]
CHAPTER_2 = [(i, f"الدرس رقم {i}{' والأخير' if i == 17 else ''}.", f"https://www.youtube.com/watch?v={v}") for i, v in enumerate(CHAPTER_2_URLS, 1)]

CHAPTER_3_URLS = [
    "or45GOFOq_Q", "mlF5TkOxIHk", "fBOvQRh3zZY", "yxC-Y-eUVYg", "nRVGYfCGK6A",
    "gyHfy0a54Js", "JbwEXwFakmE", "HbwvtccadxY", "6JdszL8unjw", "bC6YWlZzlkM",
    "numypBA-RL4", "0Nw2eEe4yVI", "S57_D7UcLIU", "ouzZ9ujv0N8", "FWIUVixA13c",
    "5I7jAIFQ8Y0", "9gfJe4mmynA", "BDD14sAMBdk", "_buFYKw0RN8", "fJtwNqHXHSQ",
    "d9c6phwEGE8", "50LJ5F7QSvY", "rPnN8AgJCno", "PP6sCV5InEI",
]
CHAPTER_3 = [(i, f"الدرس رقم {i}{' والأخير' if i == 24 else ''}.", f"https://www.youtube.com/watch?v={v}") for i, v in enumerate(CHAPTER_3_URLS, 1)]

CHAPTER_4_URLS = ["1XjGbqXLtUg","h6nTQ_dbcsk","zFN4MFL8PjI","bL7ED3zkfn8","xTQVbFOMvZk","7L5hsdB-FDk","d_EAMMIeDYo","r-6m8Pdn9Fs","VBhIFHSpKrs","_1-uUBx-ds0","VfSazl_-WLc","e_c0_pelyi8","ErZQ2Uef29M"]
CHAPTER_5_URLS = ["WXL-yvTDLkM","laNdOJt-XPU","_sbTzftSHM4","bFPAZMIS0-4","leWmRuzfI9g","q0flDaPF0Bw","Y1XGkHgjdng"]
CHAPTER_6_URLS = ["2rGAJYX8yvM","4gy1rusWca4","L13KsScMCJQ","MyKp_bTB5a4","dYhhfm7CHuI","vqX2U5yoPh0","Xg1-l7XoHH8","9D5muC10Kp0","dwU5O7U7v6Y"]
CHAPTER_7_URLS = ["GCMW_Q-9nqI","RD3ZRx_pGU4","t8MltYAdQM0","aeVsbVAmG8Y","5jkFFzx7GsI","2xXuULM_U9s","YGA_izOvidg","ZVKHByRTmaw","JjkjFPN9JwU","ZdSGjghpXiw","8dPKrCdRZb4"]

def simple_chapter(urls):
    return [(i,f"الدرس رقم {i}{' والأخير' if i==len(urls) else ''}.",f"https://www.youtube.com/watch?v={v}") for i,v in enumerate(urls,1)]

PLAYLISTS = {1:CHAPTER_1,2:CHAPTER_2,3:CHAPTER_3,4:simple_chapter(CHAPTER_4_URLS),5:simple_chapter(CHAPTER_5_URLS),6:simple_chapter(CHAPTER_6_URLS),7:simple_chapter(CHAPTER_7_URLS)}
