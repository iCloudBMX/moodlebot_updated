# moodlebot_uodated
﻿moodle.py v0.2

klass Moodle, metodaar:
core_auth_confirm_user(string username, string password): login-parolni tekshiradi, agar to'g'ri bo'lsa True, aks holda False qiymat qaytaradi

core_user_get_username(string username, string password): userning nikini qaytaradi, agar login-parol xato bo'lsa string tipida "xato" qaytadi

core_course_get_courses(string username, string password): barcha kurslarni listda qaytaradi, shakli: ["dasturlash 136", "fizika 176", ..., "kursnomi idsi"], agar login-parol xato bo'lsa bo'sh list qaytadi

core_course_get_contents(string username, string password, int course_id): barcha darslar ro'yxatini list tipida qaytaradi(masalan ["1. ma'ruza", "2. Laboratoriya"...]), agar login-parol xato bo'lsa bo'sh list qaytadi. course_id kurslar ro'yxatidan olinadi(masalan, dasturlashniki 136). Agar tanlangan kursda yuklash uchun ma'lumot bo'lmasa, ["Bu yerda yuklanadigan hech narsa yo'q :/"] qiymati qaytadi

core_course_get_grades(string username, string password): baholarni string tipida qaytaradi, masalan:
Kurs nomi|baho
Dasturlash C++|70
...
agar login-parol xato bo'lsa bo'sh string qaytadi

core_course_get_files(string username, string password, int course_id, int section):
course_id - kurslar ro'yxatidan olinadi, masalan dasturlashniki-136
section-tanlangan dars raqami, masalan:
1. Kirish
2. Laboratoriya 1.
Agar shularni ichidan Laboratoriya 2 tanlansa unda section=2 bo'lishi kerak
Fayl yuklansa 0 qiymatni, aks holda 255 ni qaytaradi

-----------------------------------------------
Tasklar bilan ishlash uchun bo'lim qo'shildi(hali sinab ko'rmadim ;D)

core_course_get_tasks(string username, string password, int course_id) - berilgan kurs id si bo'yicha vazifalar ro'yxatini list shaklida qaytaradi. Agar login-parol xato bo'lsa bo'sh list qaytadi, agar berilgan kursda topshiriq mavjud bo'lmasa ["Bu yerda topshiriqlar yo'q :)"] listi qaytadi. Tasklar ro'yxatining har bir elementini oxirroq qismida task_id si bo'ladi. Qaytariladigan listga namuna:
['Nazorat turlari\n├1. 1-Dedline 6280 ', '├2. 2-Dedline 6304 ', '├3. 3-dedline 8466 ', '├4. 4-Dedline 10742 ', '├5. 5-Dedline 10743 ', '└6. MUSTAQIL ISH 8786 ']
tasklar ro'yxatini jo'natayotganda ularni orasiga enter qo'shilib str holatiga keltirib olish kerak:
task_list = core_course_get_courses(...)
tasks = '\n'.join(' '.join(i.split()[:-1]) for i in task_list)


core_task_get_info(string username, string password, int task_id) - berilgan task_id bo'yicha informatsiyani dict tipida qaytaradi, agar login parol xato bo'lsa bo'sh dict qaytadi. task_id ni core_course_get_tasks dan olish kerak. Namuna uchun kod:
task_info = core_task_get_info(...)
task_info['task'] #task shartini olish, string qiymatda bo'ladi
task_info['info'] #task informatsiyasi. Baholar, muddat, o'zgartirish sanalari, vhkz lar string qiymatda
task_info['task_files'] #topshiriqlar fayl shaklida berilgan bo'lsa True, aks holda False bo'ladi. Shunga qarab xabarga "Topshiriq faylini yuklash" tugmasini qo'shish/qo'shmaslik mumkin
task_info['submitted_files'] #Talaba tomonidan fayllar joylangan bo'lsa True, aks holda False qiymatda bo'ladi. Shunga qarab xabarga "Topshiriqni joylash" va "Joylangan topshiriqni yuklab olish" tugmalarini qo'shish/qo'shmaslik mumkin

core_task_upload_file(string username, string password, int course_id, int task_id, bool unzip, string file_name): - topshiriqni yuklash vazifasini bajaradi. unzip qiymatiga qarab zipni sochib joylashi yoki shundayligicha joylab berishi mumkin. Agar topshiriq hajmi/soni maxbytes/maxfiles dan ortib ketsa yoki berilgan zip fayl ochilmasa, downloads papkasidagi zip faylni o'chirib yuboradi va error beradi. Agar login parol xato bo'lsa 255 qiymatini, fayllar muvaffaqqiyatli yuklansa 0 qiymatini qaytaradi

core_task_get_files(string username, string password, int task_id, bool submission) - topshiriqqa oid fayllarni yuklab olib beradi. agar submission=True bo'lsa, o'qituvchi tomonidan berilgan topshiriq fayllarni, aks holda talaba tomonidan joylangan fayllarni olib beradi. login parol xato bo'lsa 255, fayllar muvaffaqqiyatli yuklab olinsa 0 qiymatini beradi


#Keyinroq kalendar eventlarni ham qo'shamiz, hozircha shular. Omad!
