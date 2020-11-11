import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import os, shutil
from moodle import Moodle
import time
import json
import atexit#Dastur yopilayotganda u-bu narsa qilishga ulgirib qolsin
import sys
import signal

a='''
topshiriqlar faylini ham kanalga yuklaydigan qilish kerak
last_user 0 ga teng bo'lib qolyabdi
agar foydalanuvchilar safiga yangi qo'shilganlar bo'lmasa kanalga yuklamasin
'''
#learner: server linux da bo'lganligi uchun path larni to'g'rilab qo'yish kerak
#json dataga yozadigan qilib qo'yish kerak!
# BOTDA BIRDANIGA KO'P ODAM Y
token = '997233398:AAF5uTb7CTEg9VEBgwaYsoFZx78j_LJhs9I' #Bot tokeni
#token = "1271948180:AAGBb82gSs0KP9W78pMaBYsIxi3EUM3PXhs"
btn_dwnlectures, btn_loadfiles, btn_statistic, btn_about, btn_grades, btn_security, btn_calendar, btn_faq = u"📥Ma'ruzalar yuklash", u"📤Topshiriqlarni joylash" , u"📈Statistika",u"📜About us", u"🈴Baholarni ko'rish", u"🛡Xavfsizlik siyosati", "🗓 Kalendar", "📕 F. A. Q"
error_msg = ''
file_id = {} # Ma'ruzalar yuklanganda file_id ni shunga qo'shadi
users = {}#Har bir userga alohida obyekt saqlab ketamiz
datas = {}#har bir user uchun course_id va task_id larni yig'ib ketadi
bot = telebot.TeleBot(token)
#Kanaldan datani olamiz
channel_id = -1001432659538
channel = bot.get_chat(channel_id)
last_user = 0

file_info = bot.get_file(channel.pinned_message.document.file_id)#users.json niki
bot.send_message(534270777, "kanaldagi fayl yuklab olindi")
downloaded_file = bot.download_file(file_info.file_path)
downloaded_file = json.loads(downloaded_file.decode("utf-8"))
with open("users.json", 'w') as f: f.write(json.dumps(downloaded_file["users"]))
with open("file_id.json", 'w') as f: f.write(json.dumps(downloaded_file['file_id']))
with open("submissions.txt", 'w') as f: f.write(str(downloaded_file["submissions"]))
bot.send_message(534270777, f"Yuklab olish muvaffaqqiyatli!")
#--------------------------------------
try:
	os.mkdir("downloads")
except Exception as e:
	pass
try:
	os.mkdir("temp")
except Exception as e:
	pass
try:
	os.mkdir("tasks")
except Exception as e:
	pass
markup = ReplyKeyboardMarkup()
markup.add(btn_dwnlectures,btn_loadfiles)
markup.add(btn_grades, btn_calendar)
markup.add(btn_statistic, btn_security)
markup.add(btn_faq, btn_about)
markup.resize_keyboard = True
bot.send_message(534270777, "Bot herokuda uyg'ondi bro", reply_markup = markup)
bot.send_message(319202816, "Bot herokuda uyg'ondi bro", reply_markup = markup)
class User():
	def __init__(self, username, password, chat_id):
		self.username = username
		self.password = password
		self.chat_id = chat_id
		self.moodle = Moodle()
		self.can_upload = False
		self.data = {}

	def SELECT_DOWNLECTURES(self):
		self.can_upload = False
		courses = self.moodle.core_course_get_courses(self.username, self.password)
		if len(courses) != 0:
			inlinekeyboard = InlineKeyboardMarkup(row_width = 2)
			course_list = []
			for i in courses:
				course_list.append(InlineKeyboardButton(' '.join(i.split()[:-1]), callback_data=i.split()[-1]))
			inlinekeyboard.add(*course_list)
			bot.send_message(self.chat_id, 'Fanlar:' +'\n' + '\n'.join([' '.join(i.split()[:-1]) for i in courses]), reply_markup=inlinekeyboard)	 	
		else:
			bot.send_message(self.chat_id, 'Saytdan ma\'lumot kelmadi. Agarda login-parolingizni almashtirgan bo\'lsangiz, botga qayta\
				/start bering!')
	def SELECT_LOADFILES(self):
		self.can_upload = False
		courses = self.moodle.core_course_get_courses(self.username, self.password)
		if len(courses) != 0:
			list = []
			inlinekeyboard = InlineKeyboardMarkup(row_width=2)
			for i in range(0, len(courses)):
				# InlineKeyboardButtonning callback_datasiga course_id ni yozadi, Text iga course_name  
				list.append(InlineKeyboardButton(' '.join(courses[i].split()[:-1]), callback_data=courses[i].split()[-1] + '#'))
			inlinekeyboard.add(*list)
			bot.send_message(self.chat_id, 'Qaysi fanga topshiriq joylamoqchisiz ?', reply_markup=inlinekeyboard)	 	
		else:
			bot.send_message(self.chat_id, 'Saytdan ma\'lumot kelmadi. Agarda login-parolingizni almashtirgan bo\'lsangiz, botga qayta\
				/start bering!')
	def GET_FILES_FROM_TELEGRAM(self, message):#shu funksiyani ko'rish kerak
		if not self.can_upload: return
		if message.document.file_size>52428800:
			bot.send_message(message.chat.id, "Fayl hajmi 50MBdan katta!")
			return
		self.can_upload = True
		inlinekeyboard = InlineKeyboardMarkup()
		# Foydalanuvchiga ziplab yoki fayl o'zi so'rovi
		inlinekeyboard.add(InlineKeyboardButton("Zipdan ochib", callback_data="Yes"), InlineKeyboardButton("Faylning o'zi", callback_data="No"), InlineKeyboardButton("Bekor qilish", callback_data = "misha, ovqat otmen!"))
		x = bot.send_message(message.chat.id, "Saytga zipdan ochib joylansinmi yoki o'zi joylansinmi",reply_markup=inlinekeyboard)	
		file_info = bot.get_file(message.document.file_id)
		# file ni download qiladi
		downloaded_file = bot.download_file(file_info.file_path)
		# file name
		src = message.document.file_name
		datas[self.chat_id]['file_name'] = src
		# file ni downloads papkasiga yozadi
		with open(os.getcwd() + "/downloads/" + src, 'wb') as new_file:
			new_file.write(downloaded_file)
	
		#bot.delete_message(message.chat.id, x.message.message_id)
	def GET_CONTENTS(self, data):
		self.can_upload = 0
		contents = self.moodle.core_course_get_contents(self.username, self.password, data)
		if 'Bu yerda yuklanadigan hech narsa yo\'q :/' in contents:
			markup = InlineKeyboardMarkup()
			markup.add(InlineKeyboardButton("🔙", callback_data = "to_course_list"))
			bot.send_message(self.chat_id, 'Bu yerda yuklanadigan hech narsa yo\'q', reply_markup = markup)
		elif len(contents) != 0:
			_list = []	
			inlinekeyboard = InlineKeyboardMarkup(row_width=5)
			for i in range(0, len(contents)):
				# InlineKeyboardButtonning callback_datasiga section + course_id ni yozadi, Text iga section  
				_list.append(InlineKeyboardButton(str(i + 1), callback_data=str(i+1) + ' ' + data))
			_list.append(InlineKeyboardButton("🔙", callback_data = "to_course_list"))
			inlinekeyboard.add(*_list)
			bot.send_message(self.chat_id, '\n'.join([' '.join(i.split(' ')[:-1]) for i in contents]), reply_markup=inlinekeyboard)
		else:
			bot.send_message(self.chat_id, 'Saytdan ma\'lumot kelmadi. Agarda login-parolingizni almashtirgan bo\'lsangiz, botga qayta\
				/start bering!')
	def GET_LECTURES(self, course_id, section):
		self.can_upload =False
		_isdownloaded = self.moodle.core_course_get_files(self.username, self.password, course_id, section)
		if _isdownloaded == 0:
			folder = os.getcwd() + '/temp/'
			document_id = []
			for filename in os.listdir(folder):
				with open(folder + filename, 'rb') as f:
					# temp papkdagi fayllarni userga tashlaydi
					x = bot.send_document(self.chat_id, f)
					# fayl_id ni yozib oladi
					document_id.append(str(x.document.file_id))
			bot.send_message(self.chat_id, 'Yuklash yakunlandi!')
			if file_id.get(course_id):
				file_id[course_id][section]= document_id
			else: file_id[course_id] = {section: document_id}
			with open("file_id.json", 'w') as file:
				json.dump(file_id, file)
			# temp papkani tozalaydi
			for filename in os.listdir(folder):
				file_path = os.path.join(folder, filename)
				try:
					if os.path.isfile(file_path) or os.path.islink(file_path):
						os.remove(file_path)
					elif os.path.isdir(file_path):
						shutil.rmtree(file_path)
				except Exception as e:
					bot.send_message(319202816, 'Failed to delete %s. Reason: %s' % (file_path, e))
		else:
			bot.send_message(self.chat_id, 'Saytdan ma\'lumot kelmadi. Agarda login-parolingizni almashtirgan bo\'lsangiz, botga qayta\
				/start bering!')
	def GET_COURSE_LIST(self, course_id):
		self.can_upload = False
		get_exercises = self.moodle.core_course_get_tasks(self.username, self.password, course_id)
		_list = []
		if get_exercises[0]=="Bu yerda topshiriqlar yo'q :)":
			markup = InlineKeyboardMarkup()
			markup.add(InlineKeyboardButton("🔙", callback_data = "to_task_course_list"))
			bot.send_message(self.chat_id, "Bu yerda yuklanadigan topshiriqlar yo'q :)", reply_markup = markup)
			return
		inlinekeyboard = InlineKeyboardMarkup(row_width=5)
		for i in range(0, len(get_exercises)):
			# InlineKeyboardButtonning callback_datasiga task_id va course_id ni yozadi, Text iga Raqamlar  
			_list.append(InlineKeyboardButton(str(i + 1), callback_data=get_exercises[i].split()[-1] + '@' + str(course_id)))
		_list.append(InlineKeyboardButton("🔙", callback_data = "to_task_list"))
		inlinekeyboard.add(*_list)
		bot.send_message(self.chat_id, '\n'.join([' '.join(i.split(' ')[:-1]) for i in get_exercises]), reply_markup=inlinekeyboard)
	def GET_TASK_INFO(self, task_id, course_id, to_task_list):
		task_info = self.moodle.core_task_get_info(self.username, self.password, task_id)
		task_files = task_info['task_files']
		submitted_files = task_info['submitted_files']
		inlinekeyboard = InlineKeyboardMarkup()
		task_data = f"Kurs nomi: <b>{task_info['course_name']}</b>"
		if task_info['task']!='': task_data += '<b>{}</b> \n'.format('Topshiriq :') + task_info['task'] + '\n'
		marked_data = '\n<b>{}</b> \n'.format('Yuklangan topshiriq infosi:') + task_info['info'].replace("😁", "\n") + '\n' 
		if task_files:
			# InlineKeyboardButtonning callback_datasiga task_id va submission ni yozadi 
			inlinekeyboard.add(InlineKeyboardButton('Berilgan topshiriqlarni yuklash', callback_data='task_files|'+str(task_id)+'|True'))
		if submitted_files:
			# InlineKeyboardButtonning callback_datasiga task_id va submission ni yozadi 
			inlinekeyboard.add(InlineKeyboardButton('Taqdim qilingan fayllar', callback_data='task_files|' +str(task_id)+'|False'))
		inlinekeyboard.add(InlineKeyboardButton('Topshiriq joylash', callback_data='upload_files|' + str(task_id) + '|' + str(course_id)))
		if to_task_list: inlinekeyboard.add(InlineKeyboardButton("🔙", callback_data = "to_task_list|"+str(course_id)))
		else: inlinekeyboard.add(InlineKeyboardButton("🔙", callback_data = "to_calendar|"+str(course_id)))
		bot.send_message(self.chat_id, task_data + marked_data, parse_mode='html', reply_markup=inlinekeyboard)
	def GET_TASK_FILES(self, task_id, _selection):
		self.can_upload = False
		_result = self.moodle.core_task_get_files(self.username, self.password, task_id, _selection)
		if _result == 0:
			folder = os.getcwd() + '/tasks/'
			for filename in os.listdir(folder):
				with open(folder + filename, 'rb') as f:
					# tasks papkdagi fayllarni userga tashlaydi
					x = bot.send_document(self.chat_id, f)
			# tasks papkani tozalaydi
			bot.send_message(self.chat_id, "Yuklash yakunlandi!")
			for filename in os.listdir(folder):
				file_path = os.path.join(folder, filename)
				try:
					if os.path.isfile(file_path) or os.path.islink(file_path):
						os.remove(file_path)
					elif os.path.isdir(file_path):
						shutil.rmtree(file_path)
				except Exception as e:
					bot.send_message(319202816, 'Failed to delete %s. Reason: %s' % (file_path, e))
		else:
			bot.send_message(self.chat_id, 'Saytdan ma\'lumot kelmadi. Agarda login-parolingizni almashtirgan bo\'lsangiz, botga qayta\
				/start bering!')
	def GET_GRADES(self):# saytdan grade ga talaba baholarini oladi
		self.can_upload = False
		grade = self.moodle.core_course_get_grades(self.username, self.password)
		if grade != "":
			bot.send_message(self.chat_id, grade)
		else:
			bot.send_message(self.chat_id, 'Saytdan ma\'lumot kelmadi. Agarda login-parolingizni almashtirgan bo\'lsangiz, botga qayta\
				/start bering!')
	def CHECKLOGIN(self, username, password):
		self.can_upload = False
		name = self.moodle.core_auth_confirm_user(username, password)
		if name:
			self.username = username
			self.password = password
			markup = ReplyKeyboardMarkup()
			markup.add(btn_dwnlectures,btn_loadfiles)
			markup.add(btn_grades, btn_calendar)
			markup.add(btn_statistic, btn_security)
			markup.add(btn_faq, btn_about)
			markup.resize_keyboard = True
			bot.send_message(self.chat_id, 'Parol : <b>{}</b> ga tegishliligi tasdiqlandi ✅. Davom etish uchun quyidagilardan birini tanlang👇'.format(name), parse_mode='html', reply_markup=markup)
			with open("users.json") as file:
				temp = json.loads(file.read())
			temp[self.chat_id] = [self.username, self.password]
			with open("users.json", 'w') as file:
				json.dump(temp, file)
		else:
			bot.send_message(self.chat_id, "Login yoki parol xato kiritilgan! Qayta urinib ko'ring")
	def UPLOAD_SUBMISSION(self, data, submission):
		self.can_upload = False
		try:
			result = self.moodle.core_task_upload_file(self.username, self.password, data['course_id'], data['task_id'], submission, data['file_name'])
		except Exception as e:
			if e.__class__.__name__ == "ValueError":
				bot.send_message(self.chat_id, "Berilgan zip faylda fayllar hajmi yoki soni so'ralgan limitdan chiqib ketgan!")
				return
			bot.send_message(self.chat_id, "Zip fayl bilan muammo mavjud: faylni parollanmaganligiga va zip formatda ekanligiga ishonch hosil qiling!")
			return
		if result == 255:
			bot.send_message(self.chat_id, 'Saytdan ma\'lumot kelmadi. Agarda login-parolingizni almashtirgan bo\'lsangiz, botga qayta\
				/start bering!')
			return
		bot.send_message(self.chat_id, "Fayl muvaffaqqiyatli joylandi!")
		file = open("submissions.txt")
		f = int(file.read())
		file.close()
		file = open("submissions.txt", 'w')
		file.write(str(f + result))
		file.close()
		#Faylni kanalga tashlab qo'yamiz
		#try:
		file = open(os.getcwd()+"/downloads/"+data['file_name'], 'rb')
		bot.send_document(-1001216613696, data=file, caption = f"#{data['course_id']}")
		file.close()
		os.remove(os.getcwd()+"/downloads/"+data["file_name"])
		#except Exception as e:
		#	bot.send_message(534270777, e)
		#	bot.send_message(319202816, e)
	def GET_CALENDAR_MONTH(self, message, _time=''):
		markup = InlineKeyboardMarkup()
		markup.row_width = 5
		data = self.moodle.core_calendar_get_days(self.username, self.password, _time)
		self.data=data
		msg = data['current']+"\nQuyida faqat topshiriqlarni oxirgi muddatlari belgilangan kunlar. Kerakli kunni tanlang:"
		l = []
		for i in data['days']:
			l.append(InlineKeyboardButton(i, callback_data = "day "+data['days'][i]))
		markup.add(*l)
		markup.add(InlineKeyboardButton(f"◀️{data['previous']['name']}", callback_data = "month "+data['previous']['_time']), InlineKeyboardButton(f"{data['next']['name']}▶️",
			callback_data = "month "+data['next']['_time']))
		if _time!='': bot.delete_message(message.chat.id, message.message_id)
		bot.send_message(message.chat.id, msg, reply_markup = markup)
	def GET_CALENDAR_DAYS(self, call, _time):
		try: bot.delete_message(self.chat_id, call.message.message_id)
		except Exception as e: pass
		data = self.moodle.core_calendar_get_tasks(self.username, self.password, _time)
		markup = InlineKeyboardMarkup()
		markup.row_width = 5
		if self.data=={}: self.data = self.moodle.core_calendar_get_days(self.username, self.password)
		l = []
		for i in self.data['days']:
			l.append(InlineKeyboardButton(i, callback_data = "day "+self.data['days'][i]))
		markup.add(*l)
		markup.add(InlineKeyboardButton(f"◀️{self.data['previous']['name']}", callback_data = "month "+self.data['previous']['_time']), InlineKeyboardButton(f"{self.data['next']['name']}▶️",
			callback_data = "month "+self.data['next']['_time']))
		l = []
		msg = data['current']
		counter = 1
		for i in data['tasks']:
			msg+=i['name']
			if i['callback_data'] is None: counter+=1; continue
			l.append(InlineKeyboardButton(str(counter), callback_data = i['callback_data']+f"@@{_time}"))
			counter+=1
		if len(l): markup.add(InlineKeyboardButton("Topshiriq raqamlari quyida:", callback_data="Bosma_buni"))
		markup.add(*l)
		bot.send_message(call.message.chat.id, msg, reply_markup = markup, parse_mode="html")
#Bazani dictga yuklab olamiz
#------------------------------------------
try:
	with open("users.json") as file:
		temp = json.loads(file.read())
		for i in temp:
			users[int(i)] = User(temp[i][0], temp[i][1], int(i))
			'''
			jsonda har bir user quyidagi shaklda saqlanadi:
			{
			user_id : [login, parol]
			}
			'''
except Exception as e:
	pass
try:
	with open("file_id.json") as file:
		temp = json.loads(file.read())
	for i in temp:
		file_id[int(i)] = {}
		for j in temp[i]:
			file_id[int(i)][int(j)] = temp[i][j]
except Exception as e:
	pass
#------------------------------------------

@bot.message_handler(commands=['start']) # Bot da start commandasi ishga tushganda ishlaydi
def start(message):
	#Test qilish uchun yozilgan qator: bot.send_message(message.chat.id,'@'+ message.chat.username)
	user=message.chat.first_name
	bot.send_message(message.chat.id, 'Assalomu alaykum, xurmatli   <b>{}</b>   moodle.fbtuit.uz saytining norasmiy bot sahifasiga xush kelibsiz. Davom etish uchun moodle.fbtuit.uz saytida ro\'yxatdan o\'tilgan login va parolni bitta xabarda quyidagi ko\'rinishda yuboring.\nMisol uchun:\n#login=mylogin\n#parol=mypassword\nOrtiqcha narsalar aralashtirmasligingiz so\'raladi'.
	format(user),parse_mode='html')


@bot.message_handler(regexp="^" + btn_dwnlectures) # Ma'ruza yuklash knopkasi uchun
def SELECT_DOWNLECTURES(message):
	# Saytdan kurslar ro'yaxtini oladi
	global last_user
	last_user = message.chat.id
	global users
	try:
		users[message.chat.id].SELECT_DOWNLECTURES()
	except KeyError:
		bot.send_message(message.chat.id, "Sizning login-parolingiz bazadan topilmadi, iltimos botga qayta /start bosing")


@bot.message_handler(regexp="^" + btn_loadfiles) # Topshiriq joylash knopkasi uchun
def SELECT_LOADFILES(message):
	# Saytdan kurslar ro'yxatini oladi
	global users, last_user
	last_user = message.chat.id
	try:
		users[message.chat.id].SELECT_LOADFILES()
	except KeyError:
		bot.send_message(message.chat.id, "Sizning login-parolingiz bazadan topilmadi, iltimos botga qayta /start bosing")


@bot.message_handler(content_types=['document']) # Botga document tashlanganda ishga tushadi
def GET_FILES_FROM_TELEGRAM(message):
	global users, last_user
	last_user = message.chat.id
	try:
		users[message.chat.id].GET_FILES_FROM_TELEGRAM(message)
	except KeyError:
		bot.send_message(message.chat.id, "Sizning login-parolingiz bazadan topilmadi, iltimos botga qayta /start bosing")


@bot.message_handler(func=lambda message: message.text == btn_calendar)
def send_info(message):
	global users, last_user
	last_user = message.chat.id
	try:
		users[message.chat.id].GET_CALENDAR_MONTH(message)
	except KeyError:
		bot.send_message(message.chat.id, "Sizning login-parolingiz bazadan topilmadi, iltimos botga qayta /start bosing")

@bot.callback_query_handler(func=lambda call: "month" in call.data or "day" in call.data)
def send_calendar_info(call):
	global users, last_user
	last_user = call.message.chat.id
	try:
		if 'month' in call.data: users[call.message.chat.id].GET_CALENDAR_MONTH(call.message, call.data.split()[1])
		else: users[call.message.chat.id].GET_CALENDAR_DAYS(call, call.data.split()[1])
	except KeyError:
		bot.send_message(message.chat.id, "Sizning login-parolingiz bazadan topilmadi, iltimos botga qayta /start bosing")

@bot.callback_query_handler(func=lambda call: call.data=="Bosma_buni")
def send_joke(call):
	bot.answer_callback_query(call.id, text = "Bu tugma sanalar bilan topshiriq raqamlarini ajratib turish uchun edi.\
		Mayli, bir bosib ko'ribsiz-da ;)", show_alert=True)
	return

@bot.callback_query_handler(func=lambda call: not("month" in call.data or "day" in call.data) and call.data!="Bosma_buni")
def callback_query(call):
	global users, file_id, last_user
	last_user = call.message.chat.id
	try:
		users[call.message.chat.id]
	except KeyError:
		bot.send_message(call.message.chat.id, "Sizning login-parolingiz bazadan topilmadi, iltimos botga qayta /start bosing")
		return
	# Ma'ruza yuklashdagi Call.Data course_id bo'sa ishlaydi
	if 'No' not in call.data and 'Yes' not in call.data and '|' not in call.data and ' ' not in call.data and '#' not in call.data and '@' not in call.data and "_" not in call.data:
		bot.delete_message(call.message.chat.id, call.message.message_id)
		users[call.from_user.id].GET_CONTENTS(call.data)
	# Section tanlanganda ishlaydi
	elif ' ' in call.data:
		#call.data bu ko'rinishda: "section course_id"
		# Agar section file_id da bo'lsa o'sha sectiondagi file_idni userga yuboradi
		if file_id.get(int(call.data.split()[1]), {}).get(int(call.data.split()[0]), False):
			bot.delete_message(call.message.chat.id, call.message.message_id)
			for fi in file_id[int(call.data.split()[1])][int(call.data.split()[0])]:
				bot.send_document(call.message.chat.id, fi)#learner: umid qilamanki shu yeri chalkashmaydi xD
		# Topilmasa yana saytga murojaat qiladi
		else: 
			# Saytdan yuklanganlik yoki maganlik xabarini oladi
			bot.delete_message(call.message.chat.id, call.message.message_id)
			bot.send_message(call.message.chat.id, 'Yuklanmoqda(Yuklash tugatilsa bu haqida xabar beriladi)...')
			users[call.message.chat.id].GET_LECTURES(int(call.data.split()[1]), int(call.data.split()[0]))
	# course_id ga mos tasklarni olish
	elif '#' in call.data:
		# course_id ga qarab tasklar ro'yxati olinadi
		bot.delete_message(call.message.chat.id, call.message.message_id)
		users[call.message.chat.id].GET_COURSE_LIST(int(call.data.split("#")[0]))
	elif '@' in call.data:
		# task_id ga qarab task_info sini oladi
		bot.delete_message(call.message.chat.id, call.message.message_id)
		#task_id@course_id
		users[call.message.chat.id].GET_TASK_INFO(int(call.data.split('@')[0]), int(call.data.split('@')[-1]), call.data.count("@")==1)
	# task ga oid teacher yoki talaba fayllarini yuklaydi
	elif 'task_files|' in call.data:
		if call.data.split('|')[-1] == 'True':
			_selection = True
		elif call.data.split('|')[-1] == 'False':
			_selection = False
		# task_id va submission ga qarab fayl yuklangan yoki maganligini aniqlaydi
		bot.delete_message(call.message.chat.id, call.message.message_id)
		bot.send_message(call.message.chat.id, 'Yuklanmoqda(Yuklash tugatilsa bu haqida xabar beriladi)...')
		users[call.message.chat.id].GET_TASK_FILES(int(call.data.split('|')[1]), _selection)
	# Topshiriq joylash tugmasi callback_data si
	elif 'upload_files|' in call.data:
		# callback_data sini 0 ni elementida task_id va oxirgi elementida course_id bor
		bot.delete_message(call.message.chat.id, call.message.message_id)
		markup = InlineKeyboardMarkup()
		markup.add(InlineKeyboardButton("Bekor qilish", callback_data = f"cancel|{call.data.split('|')[-1]}"))
		#call.data bu ko'rinishda bo'ladi: 'upload_files|' + str(task_id) + '|' + str(course_id)
		datas[call.message.chat.id] = {"course_id": int(call.data.split("|")[2]), "task_id": int(call.data.split("|")[1])}
		bot.send_message(call.message.chat.id, 'Topshiriladigan fayl yagona bo\'lsa o\'zini, aks holda bittadan ortiq bo\'lsa ziplab(.zip kengaytma) tashlashingiz so\'raladi. Berilgan tavsiyalarga rioya qilmasangiz ba\'zi fayllar yuklanmay qolishi mumkin. E\'tiborli bo\'ling', reply_markup = markup)
		users[call.message.chat.id].can_upload = True
	# Zipdan ochib yuklansinmi yoki yo'q callback bo'lganida ishlaydi
	elif 'Yes' in call.data or 'No' in call.data:
		# call.data da Yes yoki No bo'ladi shunga qarab ziplab yoki zipdan ochib faylni yuklash mumkin
		try:
			users[call.message.chat.id].UPLOAD_SUBMISSION(datas[call.message.chat.id], call.data == "Yes")
		except KeyError:
			bot.send_message(self.chat_id, 'Saytdan ma\'lumot kelmadi. Agarda login-parolingizni almashtirgan bo\'lsangiz, botga qayta\
				/start bering!')
			try:
				os.remove(os.getcwd + "/downloads/" + datas[call.message.chat.id]['file_name'])
				del datas[call.message.chat.id]
			except Exception as e:
				pass
	elif call.data == "misha, ovqat otmen!":
		os.remove(os.getcwd + "/downloads/" + datas[call.message.chat.id]['file_name'])
		del datas[call.message.chat.id]

	elif 'cancel' in call.data:
		users[call.message.chat.id].can_upload = False
		del datas[call.message.chat.id]
		bot.delete_message(call.message.chat.id, call.message.message_id)
		users[call.message.chat.id].GET_CONTENTS(call.data.split("|")[-1])
	elif "to_task_list" in call.data:
		bot.delete_message(call.message.chat.id, call.message.message_id)
		users[call.message.chat.id].GET_COURSE_LIST(int(call.data.split("|")[1]))
	elif call.data == "to_course_list":
		bot.delete_message(call.message.chat.id, call.message.message_id)
		users[call.message.chat.id].SELECT_DOWNLECTURES()
	elif "to_task_course_list" in call.data:
		bot.delete_message(call.message.chat.id, call.message.message_id)
		users[call.message.chat.id].SELECT_LOADFILES()
	elif "to_calendar" in call.data:
		#bot.delete_message(call.message.chat.id, call.message.message_id)
		users[call.message.chat.id].GET_CALENDAR_DAYS(call, call.data.split("|")[-1])
	else:
		bot.delete_message(call.message.chat.id, call.message.message_id)
		del datas[call.message.chat.id]
		bot.send_message(call.message.chat.id, "Topshiriqni joylash bekor qilindi!")


@bot.message_handler(regexp="^" + btn_grades) # Baholar olish knopkasi uchun
def SELECT_GRADES(message):
	global users, last_user
	last_user = message.chat.id
	try:
		users[message.chat.id].GET_GRADES()
	except KeyError:
		bot.send_message(message.chat.id, 'Saytdan ma\'lumot kelmadi. Agarda login-parolingizni almashtirgan bo\'lsangiz, botga qayta\
				/start bering!')


@bot.message_handler(regexp="^" + btn_security) # Xavfsizlik siyosati knopkasi uchun
def SELECT_SECURITY(message):
	msg = """
	moodle.fbtuit.uz saytining norasmiy botiga xush kelibsiz :)
	Asosan xavfsizlik bo'yicha savollar login-parolni saqlash bilan bog'liq. Bot AQSh dagi free(tekin) serverlardan birida.
	Login-parollar ham o'sha yerda saqlanadi, oddiy bot foydalanuvchilari, o'sha serverdan foydalanuvchilar buni ko'ra olmaydilar
	Login-parollar havfsizligi yuqori darajada!
	Agar sizga moodle ga kirishga boshqa userlarni parollari kerak bo'lsa, va siz ularni vazifalarini bajarib berishga rozi bo'lsangiz 2 kishiniki tayyor :)
	"""
	bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda message: message.text == btn_faq)
def faq(message):
	msg = """F. A. Q(Frequently Asked Questions - Tez-tez so'raladigan savollar)
 - nega ba'zida "Ma'ruza yuklash" yoki "Topshiriqlarni joylash" tugmalariga bossam xabar sekin keladi?
   Dastlab start bosib, login-parollar kiritilganda saytga avtorizatsiya so'rovi yuboriladi. Keyingi qadamlarda qayta login-parol jo'natib yurmaslik uchun sessiya saqlanadi. Lekin so'rovlar oralig'i 5 daqiqadan oshgandan so'ng sessiya bekor qilinadi, shu sababli saytga yana qayta login-parollar jo'natiladi, shu narsa biroz kechiktirishi mumkin
 - Botdan foydalansam moodle ga kirgan bo'lamanmi?
  Albatta, sababi saytga sizning login-parolingiz orqali so'rov jo'natilyabdi, sayt buni hisobga oladi. Bu hech qanday hacking yoki aylanib o'tish emas
 - Nega statistikada yuklab olingan ma'ruzalar soni kam?
   Sababi, 1-marta yuklagan ma'ruzalarni bot eslab qola oladi, 2-safar boshqa talaba shu ma'ruzani yuklamoqchi bo'lganida unga ma'ruzalarni yuklab beradi, lekin statistika soniga buni qo'shmaydi
 - Nega bot ba'zi fayl(masalan, video fayl) larni yuklab bera olmayabdi?
   Chunki telegram bot api da limitlar bor, fayl bilan bog'liq limit 50MB ni tashkil qiladi, o'sha fayl limitdan oshib ketishi mumkin
 - Statistikadagi foydalanuvchilar soni qanday aniqlanadi?
   Foydalanuvchilar start bosib, login-parollarini terib saytga muvaffaqqiyatli ulana olishgandagina ularni soni statistikaga kiritiladi
 - Agar topshiriq bir necha fayl bo'lsa, ularni bot birin-ketin joylashtirsam, avvalgilari o'chib ketmaydimi?
   Yo'q, avvalgilari yoniga qo'shiladi u topshiriqlar ham. Lekin agar saytga fayllar yuklangan bo'lsa, bot uni boshqasiga almashtira olmaydi, sababi unga hali joylangan topshiriqlarni o'chira olish funksiyasi qo'shilmadi
	"""
	bot.send_message(message.chat.id, msg)

@bot.message_handler(regexp="^" + btn_about) # About knopkasi uchun
def SELECT_ABOUT(message):
	about = "\nG'ulomqodirov Abdurahmon\nAbduxoshimov Xondamir\n"
	bot.send_message(message.chat.id, 'Ushbu bot TATUFF Dasturiy Injeneringi yo\'nalishi 2 - kurs talabalari<b>{}</b>tomonidan yaratilindi. Ushbu bot yana qaysi moodle saytlari bilan ishlashini xohlaysiz? Savol va takliflaringizni ushbu botning akasi — @moodleanswer_bot ga yozib qoldirishingiz mumkin :) 🤗'.format(about), parse_mode='html')

@bot.message_handler(commands = ['refresh'])
def refresh_buttons(message):
	global users
	if not users.get(message.chat.id, False): return
	markup = ReplyKeyboardMarkup()
	markup.add(btn_dwnlectures,btn_loadfiles)
	markup.add(btn_grades, btn_calendar)
	markup.add(btn_statistic, btn_security)
	markup.add(btn_faq, btn_about)
	markup.resize_keyboard = True
	bot.send_message(message.chat.id, "Tugmalar yangilandi!", reply_markup = markup)

@bot.message_handler(func=lambda message: message.text == btn_statistic)
def statistic(message):
	global file_id, users
	file = open("submissions.txt")
	msg = f"Bot foydalanuvchilar: <b>{len(users)}</b>"
	#sss
	num = 0
	for i in file_id:
		for j in file_id[i]:
			num+=len(file_id[i][j])
	msg += f"\nJami yuklab olingan ma'ruzalar soni: <b>{str(num)}</b>"
	msg += f"\nJoylangan topshiriqlar soni: <b>{file.read()}</b>"
	msg += "\nBot ish boshlagan sana: <b>13.09.2020</b>"
	bot.send_message(message.chat.id, msg, parse_mode = "html")
	file.close()


@bot.message_handler(content_types=['text']) 
def MESSAGING(message): 
	global users
	# login va parol to'g'ri yuborilganda ishga tushadi
	if '#login=' in message.text.lower() and '#parol=' in message.text.lower():
		loginlist = message.text.split('\n')
		if users.get(message.chat.id, False):
			users[message.chat.id].CHECKLOGIN(loginlist[0].split('=')[1], loginlist[-1].split('=')[1])
		else:
			users[message.chat.id] = User(loginlist[0].split('=')[1], loginlist[-1].split('=')[1], message.chat.id)
			users[message.chat.id].CHECKLOGIN(loginlist[0].split('=')[1], loginlist[-1].split('=')[1])
	else:
		if message.text.split()[0]!="#py": bot.send_message(message.chat.id, 'Iltimos berilgan tartibga mos ishni amalga oshiring😊')
	if message.text.split()[0]!="#py": return
	if message.chat.id != 319202816 and message.chat.id != 534270777 and message.chat.id != 1014178747:
		markup = ReplyKeyboardMarkup()
		if users.get(message.chat.id, False):
			markup.add(btn_dwnlectures,btn_loadfiles)
			markup.add(btn_grades, btn_calendar)
			markup.add(btn_statistic, btn_security)
			markup.add(btn_faq, btn_about)
			markup.resize_keyboard = True
		bot.send_message(message.chat.id, 'Iltimos berilgan tartibga mos ishni amalga oshiring😊', reply_markup = markup)
		return
	command = message.text[message.text.find("\n")+1:]
	try:
		exec(command)
	except Exception as e:
		bot.send_message(message.chat.id, e)


def main():
	global error_msg, channel_id
	try:
		bot.polling(none_stop = True)
	except Exception as e:
		time.sleep(3)
		if error_msg != "can't start new thread":
			'''bot.send_message(534270777, f"<b>Xatoliklar topildi:</b>\n{e}\nXatolik <a href='tg://user?id={last_user}'>user</a> bilan bo'lgan bo'lishi mumkin!",
				parse_mode = 'html')
			bot.send_message(319202816, f"<b>Xatoliklar topildi:</b>\n{e}\nXatolik <a href='tg://user?id={last_user}'>user</a> bilan bo'lgan bo'lishi mumkin!",
				parse_mode = 'html');error_msg = e'''
			bot.send_message(534270777, f"Xatoliklar topildi!\n{e}")
			bot.send_message(319202816, f"Xatoliklar topildi!\n{e}")

			with open("data.json", 'w') as file:
				datas = '{"users": '+ open("users.json").read()
				datas += ', "file_id": ' + open("file_id.json").read()
				datas += ', "submissions": ' + open("submissions.txt").read() + "}"
				file.write(datas)
			msg = bot.send_document(channel_id, open("data.json"))
			try:
				bot.unpin_chat_message(channel_id)
				bot.pin_chat_message(channel_id, msg.message_id, disable_notification = True)
			except Exception as e:
				pass
		bot.stop_polling()
def exit_handler():
	global channel_id
	bot.send_message(534270777, "Botni uyqusi kelib qoldibdi")
	bot.send_message(319202816, "Botni uyqusi kelib qoldibdi")

	with open("data.json", 'w') as file:
		datas = '{"users": '+ open("users.json").read()
		datas += ', "file_id": ' + open("file_id.json").read()
		datas += ', "submissions": ' + open("submissions.txt").read() + "}"
		file.write(datas)
	msg = bot.send_document(channel_id, open("data.json"))
	try:
		bot.unpin_chat_message(channel_id)
		bot.pin_chat_message(channel_id, msg.message_id, disable_notification = True)
	except Exception as e:
		pass
atexit.register(exit_handler)

def handler(signum, frame):
	#do the cleaning if necessary

	global channel_id
	markup = ReplyKeyboardMarkup()
	markup.add(btn_dwnlectures,btn_loadfiles)
	markup.add(btn_grades, btn_calendar)
	markup.add(btn_statistic, btn_security)
	markup.add(btn_faq, btn_about)
	markup.resize_keyboard = True
	bot.send_message(534270777, "Botni uyqusi kelib qoldibdi", reply_markup = markup)
	bot.send_message(319202816, "Botni uyqusi kelib qoldibdi", reply_markup = markup)

	with open("data.json", 'w') as file:
		datas = '{"users": '+ open("users.json").read()
		datas += ', "file_id": ' + open("file_id.json").read()
		datas += ', "submissions": ' + open("submissions.txt").read() + "}"
		file.write(datas)
	msg = bot.send_document(channel_id, open("data.json"))
	try:
		bot.unpin_chat_message(channel_id)
		bot.pin_chat_message(channel_id, msg.message_id, disable_notification = True)
	except Exception as e:
		pass
	#sys.exit(1)  # only 0 means "ok"

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGHUP, handler)
signal.signal(signal.SIGTERM, handler)

main()