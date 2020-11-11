# coding: utf-8
import sys
import requests
import os
import json
import zipfile
import shutil
from urllib.parse import unquote
#Quyida unicode bilan bog'liq muammoni bartaraf etish
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')
#https://cknotes.com/python-error-unicodeencodeerror-charmap-codec-cant-encode-character/ ga rahmat :)
#DIQQAT! siz tushunadigan darajada koment yozilmagan, bu abrakadabralarga qaramang
"Saytdan chiqib ketib qolish holatini ko'rish kerak"
"mod/assign da yuklanishi kerak bo'lgan topshiriqlarga link berilarkan :) joningdan"
"Matnda krillcha belgilar ham bormi? Yaxshi, ularni almashtirib beramiz!"
# v 0.1 buglar to'la versiya ;)
from selectolax.parser import HTMLParser
class Moodle:
	def __init__(self):
		self.session = requests.Session()
		MAX_RETRIES = 20
		adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
		self.session.mount('https://', adapter)
		self.session.mount('http://', adapter)
		#self.session.post("http://moodle.fbtuit.uz/login/index.php", data = {'username':username, 'password': password, 'rememberusername':'1'})
		#self.username = username
		#self.password = password
		#self.main_page = HTMLParser(self.session.get("http://moodle.fbtuit.uz/my/").text)
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
	def core_auth_confirm_user(self, username, password):
		"Bu funksiyani biroz o'zgartirish kerak"
		page = HTMLParser(self.session.post("http://moodle.fbtuit.uz/login/index.php", data = {'username':username, 'password': password, 'rememberusername':'1'}).text)
		#return page.css_first('title').text() != "TATUFF Masofaviy ta'lim: Вход на сайт"
		for node in page.css("span"):
			if 'class' in node.attributes:
				if node.attributes['class'] == 'menu-action-text':
					return node.text().strip()
		return ''
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
	def core_course_get_courses(self, username, password):
		page = HTMLParser(self.session.get("http://moodle.fbtuit.uz/my/").text)#todo bundan ham optimal qilish mumkin :/
		if page.css_first('title').text() == "TATUFF Masofaviy ta'lim: Вход на сайт":
			if not self.core_auth_confirm_user(username, password): return []#Parol xato bo'lsa bo'sh list qaytaradi
			page = HTMLParser(self.session.get("http://moodle.fbtuit.uz/my/").text)
		"dasturlash 136 shaklida bo'ladi har bir list elementi"
		"kursnomi idsi"
		course_list = []
		'''
		Parse ni quyidagi qism bo'yicha amalga oshiradi:
		<div class="media-body">
        <h4 class="h5"><a href="http://moodle.fbtuit.uz/course/view.php?id=173" class="">Kurs nomi</a></h4>
        </div>
		'''
		for node in page.css("div"):
			if 'class' in node.attributes:
				if node.attributes['class']=='media-body' and node.text()!='':
					if node.text().strip()+" "+node.css_first('a').attributes['href'][node.css_first('a').attributes['href'].find("=")+1:] in course_list: break
					course_list.append(node.text().strip()+" "+node.css_first('a').attributes['href'][node.css_first('a').attributes['href'].find("=")+1:])
		return course_list
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
	def core_user_get_username(self, username, password):
		page = HTMLParser(self.session.get("http://moodle.fbtuit.uz/my/").text)
		if page.css_first('title').text() == "TATUFF Masofaviy ta'lim: Вход на сайт":
			if not self.core_auth_confirm_user(username, password):
				return ""
			page = HTMLParser(self.session.get("http://moodle.fbtuit.uz/my/").text)
		'''
 		<span class="menu-action-text" id="actionmenuaction-1">
                                                	Abduraxmon G`ulomqodirov
        shu qismidan qirqib olamiz :)
		'''
		for node in page.css("span"):
			if 'class' in node.attributes:
				if node.attributes['class'] == 'menu-action-text':
					return node.text().strip()
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
	def core_course_get_contents(self, username, password, course_id):
		"Kursdagi mavzularni ko'rsatish uchun govno kod"
		page = HTMLParser(self.session.get("http://moodle.fbtuit.uz/course/view.php?id="+str(course_id)).text)
		if page.css_first('title').text() == "TATUFF Masofaviy ta'lim: Вход на сайт":
			if not self.core_auth_confirm_user(username, password):
				return []
			page = HTMLParser(self.session.get("http://moodle.fbtuit.uz/course/view.php?id="+str(course_id)).text)
		counter = 1
		contents = []
		"Kursdagi barcha mavzularni olamiz"
		'''
		>>> s=''
		>>> for node in page.css("li"):
		...  if 'id' in node.attributes:
		...   if node.attributes['id'][:7]=='section' and node.attributes['id']!='sectio
		n-0': print(node.child.css_first("span").text()); s+= node.child.css_first('span').text()
		'''
		for tag in page.tags("li"):
			if 'id' in tag.attributes:
				if tag.attributes['id'][:7]=="section" and tag.attributes['id']!="section-0":
					if not('resource' in tag.html): continue
					section=HTMLParser(tag.html)
					contents.append(str(counter)+". "+section.css_first("span").text())
					counter+=1
		if contents==[]: contents=["Bu yerda yuklanadigan hech narsa yo'q :/"]
		return contents
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
	def core_course_get_grades(self, username, password):#, course_id): keyinchalik kurslarni o'zidagi baholarni batafsil ko'rsatadigan qilish
		"Kurs id si bo'yicha baholarni aytadi"
		"Buni sal chiroyliroq qilib qo'ygin-ey :)"
		page = HTMLParser(self.session.get("http://moodle.fbtuit.uz/grade/report/overview/index.php").text)
		if page.css_first('title').text() == "TATUFF Masofaviy ta'lim: Вход на сайт":
			if not self.core_auth_confirm_user(username, password):
				return ""
			page = HTMLParser(self.session.get("http://moodle.fbtuit.uz/grade/report/overview/index.php").text)
		grades = "Kurs nomi|Baho\n"
		#td - table tegi, table dan baholarni olamiz
		counter = 0
		for node in page.css('td'):
			if node.text()=="": return grades
			grades += node.text()
			counter += 1
			if counter%2: grades += "|"
			else: grades += "\n"
		#qaytuvchi shakli: kurs_nomi|baho
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
	def core_course_get_files(self, username, password, course_id, section):
		page=HTMLParser(self.session.get("http://moodle.fbtuit.uz/course/view.php?id="+str(course_id)).text)
		if page.css_first('title').text() == "TATUFF Masofaviy ta'lim: Вход на сайт":
			if not self.core_auth_confirm_user(username,password):
				return 0xff
			page=HTMLParser(self.session.get("http://moodle.fbtuit.uz/course/view.php?id="+str(course_id)).text)
		#li teglari oralig'ini tekshiradi, mavzular va fayllar o'sha yerda
		for tag in page.tags('li'):
			if 'id' in tag.attributes:
				if tag.attributes['id']=='section-'+str(section):
					page=HTMLParser(tag.html)#aaaaaaa
					break
		links=[]
		for tag in page.tags('a'):
			if not(tag.attributes['href'] in links): links.append(tag.attributes['href'])
		try:
			os.mkdir(os.getcwd()+"/temp")
		except Exception as e:
			pass
		for link in links:
			if not('resource' in link): continue
			resp=self.session.get(link, allow_redirects=True)
			file_name = resp.url[resp.url.rfind("/")+1:]
			file_name = unquote(file_name)
			if 'view.php' in file_name: continue
			with open(os.getcwd()+"/temp/"+file_name, 'wb') as file:
				file.write(resp.content)
		return 0
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
	#Topshiriqlar bilan ishlash bo'limi qo'shildi!
	def core_course_get_tasks(self, username, password, course_id):#Topshiriq mavzularini ko'rsatadi
		"Topshiriqlar list shaklida qaytadi, masalan: [1-dedline 6280, ..., vazifa uning_idsi]"
		page = HTMLParser(self.session.get("http://moodle.fbtuit.uz/course/view.php?id="+str(course_id)).text)
		if page.css_first('title').text() == "TATUFF Masofaviy ta'lim: Вход на сайт":
			if not self.core_auth_confirm_user(username, password):
				return []
			page = HTMLParser(self.session.get("http://moodle.fbtuit.uz/course/view.php?id="+str(course_id)).text)
		tasks = []
		counter = 1
		ids = []
		#Yana li tegiga murojaat qilamiz, chunki topshiriqlar sectionlarni ichida berilgan bo'ladi
		#if lar ko'payib ketarkan, optimal yo'lini qidirish kerak
		for tag in page.tags('li'):
			if 'id' in tag.attributes:
				if tag.attributes['id'][:7]=='section':
					if not('http://moodle.fbtuit.uz/mod/assign/view.php?' in tag.html): continue
					section = HTMLParser(tag.html)
					theme = section.css_first('span').text() + '\n'
					for tag1 in section.tags('a'):
						if not('http://moodle.fbtuit.uz/mod/assign/view.php?' in tag1.attributes['href']): continue
						#if 'section' in tag1.attributes['id']: continue
						#tasks.append("├"+str(counter)+". "+tag1.text().replace("\n"," ")+" "+tag1.css_first('input').attributes['value'])
						#tasks.append("├"+str(counter)+". "+tag1.css_first('span').text()+" "+tag1.css_first('input').attributes['value'])
						if tag1.attributes['href'][tag1.attributes['href'].rfind("=")+1:] in ids: continue
						tasks.append(theme+"├"+str(counter)+". "+tag1.text() + " "+ tag1.attributes['href'][tag1.attributes['href'].rfind("=")+1:])
						ids.append(tag1.attributes['href'][tag1.attributes['href'].rfind("=")+1:])
						counter += 1
						theme = ''
						'''s = ''
						for input_tag in tag1.css('input'):
							if input_tag.attributes['name']!='modulename' and input_tag.attributes['name']!='id': continue
							s = input_tag.attributes['value']+" "+s
						tasks[-1]+=s'''

					tasks[-1]=tasks[-1].replace("├", "└")


		if tasks==[]: return ["Bu yerda topshiriqlar yo'q :)"]
		return tasks
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
	def core_task_get_info(self, username, password, task_id):
		page = HTMLParser(self.session.get('http://moodle.fbtuit.uz/mod/assign/view.php?id='+str(task_id)+"&lang=uz").text)
		if page.css_first('title').text() == "TATUFF Masofaviy ta'lim: Вход на сайт":
			if not self.core_auth_confirm_user(username, password):
				return {}
			page = HTMLParser(self.session.get('http://moodle.fbtuit.uz/mod/assign/view.php?id='+str(task_id)+"&lang=uz").text)
		infos = {'task': ''}
		for div in page.css("div"):
			if div.attributes.get("id", '')=="page":
				infos['course_name'] = div.css_first("h1").text()
		links = []
		submitted_files = []
		page.unwrap_tags(['p'])
		for tag in page.tags("div"):
			if 'id' in tag.attributes:
				if tag.attributes['id']=='intro':
					infos ['task'] = ' '.join(tag.text().split())
					for css in tag.css('a'):
						links.append(css.attributes['href'])#Taskka ilova qilingan fayllar
		counter = 0
		info = ''
		for tag in page.tags('td'):
			if 11<counter<14: counter+=1; continue
			info += tag.text()
			if counter%2: info += "😁"
			else: info += ": "
			counter += 1
			if tag.css_first('a'):
				for css in tag.css('a'):
					if "submission_files" in css.attributes['href']: submitted_files.append(css.attributes['href'])
			if counter==3:
				if "Urinish bo'lmagan" in info: break
		infos['info'] = ' '.join(info.split())
		infos['task_files'] = len(links)>0
		infos['submitted_files'] = len(submitted_files)>0
		return infos
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
	def core_task_upload_file(self, username, password, course_id, task_id, unzip, file_name):
		page = HTMLParser(self.session.get(f"http://moodle.fbtuit.uz/mod/assign/view.php?id={task_id}&action=editsubmission").text)
		if page.css_first('title').text() == "TATUFF Masofaviy ta'lim: Вход на сайт":
			if not self.core_auth_confirm_user(username, password):
				return 0xff
			page = HTMLParser(self.session.get(f"http://moodle.fbtuit.uz/mod/assign/view.php?id={task_id}&action=editsubmission").text)
		#post qilish uchun asosiy o'zgaruvchilar:
		link = page.css_first("object").attributes['data']
		link = link.split('&')[2:]
		itemid = link[0].split('=')[1]
		subdirs = link[1].split('=')[1]
		maxbytes = link[2].split('=')[1]
		areamaxbytes = link[3].split('=')[1]
		maxfiles = link[4].split('=')[1]
		ctx_id = link[5].split('=')[1]
		course = link[6].split('=')[1]
		sesskey = link[7].split('=')[1]
		client_id = page.html[page.html.find('client_id')+12:page.html.find('client_id')+25]
		file_list = []
		#----------------------------------------------------------------------------
		if unzip:
			with zipfile.ZipFile(open(os.getcwd()+"/downloads/"+file_name, 'rb')) as zippy:
				if len(zippy.filelist)>maxfiles:
					zippy.close()
					os.remove(os.getcwd()+"/downloads/"+file_name)
					raise ValueError
				sizes = 0
				for i in zippy.infolist():
					sizes += i.file_size
					file_list.append(i.file_name)
				if sizes>maxbytes:
					zippy.close()
					os.remove(os.getcwd()+"/downloads/"+file_name)
					raise ValueError
				os.mkdir(file_name[:file_name.rfind('.')])
				zippy.extractall(path = file_name[:file_name.rfind('.')])
				zippy.close()
				#os.remove(os.getcwd()+"/downloads/"+file_name)
		#----------------------------------------------------------------------------
		token = json.loads(self.session.get(f"http://moodle.fbtuit.uz/login/token.php?username={username}&password={password}&service=moodle_mobile_app").text)['token']
		datas = json.loads(self.session.get(f"http://moodle.fbtuit.uz/webservice/rest/server.php?wsfunction=mod_assign_get_assignments&moodlewsrestformat=json&wstoken={token}&courseids[0]={course_id}").text)['courses'][0]['assignments']
		assignmentid = 0
		for data in datas:
			if data['cmid']==task_id:
				assignmentid = data['id']
				break

		data = {
			"token": token,
			'itemid': itemid,
			'json': 'True',
			'repo_id': (None, '4'),
			'p': (None, ''),
			'page': (None, ''),
			'env': (None, 'filemanager'),
			'sesskey': (None, sesskey),
			'client_id': (None, client_id),
			'itemid': (None, itemid),
			'maxbytes': (None, maxbytes),
			'areamaxbytes': (None, areamaxbytes),
			'ctx_id': (None, ctx_id),
			'subdirs': (None, subdirs),
			'maxfiles': (None, maxfiles),
			'course': (None, course),
			'savepath': (None, '/')
			}
		path = file_name[:file_name.rfind('.')]
		files = {}
		if file_list==[]:
			files['file1'] = open(f"{os.getcwd()}/downloads/{file_name}", 'rb')
		else:
			for i in range(1,len(file_list)+1):
				files['file'+str(i)] = open(path+f"/{file_list[i-1]}", 'rb')
		self.session.post(f"http://moodle.fbtuit.uz/webservice/upload.php", data=data,files=files, timeout=100)
		self.session.get(f"http://moodle.fbtuit.uz/webservice/rest/server.php?wstoken={token}&wsfunction=mod_assign_save_submission&assignmentid={assignmentid}&plugindata[onlinetext_editor][text]=sometext&plugindata[onlinetext_editor][format]=1&plugindata[onlinetext_editor][itemid]={itemid}&plugindata[files_filemanager]={itemid}")
		for i in range(1, len(files)+1):
			files['file'+str(i)].close()
		if unzip:
			shutil.rmtree(path)
		#os.remove(f"downloads/{file_name}")

		return len(file_list)+(file_list == [])	
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
	def core_task_get_files(self, username, password, task_id, submission):
		page = HTMLParser(self.session.get(f"http://moodle.fbtuit.uz/mod/assign/view.php?id={task_id}").text)
		if page.css_first('title').text() == "TATUFF Masofaviy ta'lim: Вход на сайт":
			if not self.core_auth_confirm_user(username, password):
				return 0xff
			page = HTMLParser(self.session.get(f"http://moodle.fbtuit.uz/mod/assign/view.php?id={task_id}").text)
		#submission True bo'lsa unda talaba tomonidan yuklangan fayllarni olamiz, bo'lmasa o'qituvchi yuklaganni
		#Diqqat! O'qilmaydigan qatorlar! x(
		links = []
		if submission:
			'''for tag in page.tags("div"):
				if 'id' in tag.attributes:
					if tag.attributes['id']=='intro':
						for css in tag.css('a'):
							links.append(css.attributes['href'])#Taskka ilova qilingan fayllar'''
			for tag in page.tags("a"):
				if 'mod_assign' in tag.attributes['href']:
					links.append(tag.attributes['href'])
		else:
			'''for tag in page.tags('tr'):
				if tag.css_first('a'):
					for css in tag.css('a'):
						if "submission_files" in css.attributes['href']: links.append(css.attributes['href'])'''
			for tag in page.tags('a'):
				if "submission_files" in tag.attributes['href']:
					links.append(tag.attributes['href'])
		#O'qilmaydigan qatorlar tugadi
		try:
			os.mkdir("tasks")
		except Exception as e:
			pass
		for url in links:
			file_name = url[url.rfind("/")+1:url.rfind("?")]
			file_name = unquote(file_name)
			file = open(os.getcwd()+ "/tasks/"+file_name, 'wb')
			file.write(self.session.get(url).content)
			file.close()
		return 0
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
	#3-versiya -- Kalendardagi topshiriqlarni ko'rsatish qismi qo'shiladi nasib qilsa :)
	def core_calendar_get_days(self, username, password, _time = ''):
		page = HTMLParser(self.session.get(f"http://moodle.fbtuit.uz/calendar/view.php?view=month&lang=uz{f'&time={_time}' if len(_time) else ''}").text)
		if page.css_first('title').text() == "TATUFF Masofaviy ta'lim: Saytga kirish":
			if not self.core_auth_confirm_user(username, password):
				return 0xff
			page = HTMLParser(self.session.get(f"http://moodle.fbtuit.uz/calendar/view.php?view=month&lang=uz{f'&time={_time}' if _time!='' else ''}").text)
		data = {}
		for tag in page.css("h2"):#Kalendar ko'rsatayotgan oyni olamiz
			if tag.attributes.get("class", {}) == "current": data['current'] = tag.text(); break

		for tag in page.css("a"):
			if "arrow_link" in tag.attributes.get("class", {}):#if 'class' tag.attributes da va tag.attributes['class'] == ...ni qisqartirilgani
				for i in tag.css("span"):
					if i.attributes['class'] == 'arrow_text': name = i.text()
				data[tag.attributes['class'].split()[-1]] = {'name': name, '_time':
				tag.attributes['href'][tag.attributes['href'].rfind("=")+1:]}
		data['days'] = {}
		#├
		#└
		for table in page.css("table"):
			if not('calendar' in table.attributes.get('class',{})): continue
			for td in table.css("td"):
				if td.css_first("a"):
					if td.css_first("a").attributes.get("class", {})=='day':
						data['days'][td.css_first('a').text()] = td.css_first('a').attributes['href'][td.css_first('a').attributes['href'].rfind("=")+1:]
		return data
		#data['current'] - hozirgi oy va yilni ko'rsatadi
		#data['days'] da topshiriq qo'yilgan kunlar ro'yxati, {'5': callback_data} shaklida saqlanadi
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
	def core_calendar_get_tasks(self, username, password, _time):
		page = HTMLParser(self.session.get(f"http://moodle.fbtuit.uz/calendar/view.php?view=day&lang=uz&time={_time}").text)
		if page.css_first('title').text() == "TATUFF Masofaviy ta'lim: Saytga kirish":
			if not self.core_auth_confirm_user(username, password):
				return 0xff
			page = HTMLParser(self.session.get(f"http://moodle.fbtuit.uz/calendar/view.php?view=month&lang=uz&time={_time}").text)
		data = {'tasks': []}
		for h2 in page.css("h2"):
			if h2.attributes.get("class", {})=="current": data['current'] = h2.text()
		counter = 1
		for div in page.css("div"):
			if div.attributes.get("data-type", '')=='event':
				data['tasks'].append({'name': "\n├"+str(counter)+". "+div.css_first("h3").text()+"\n| Oxirgi muddat: "+div.css_first("span").text()})
				for i in div.css("a"):
					if i.text() == "Go to activity": link = i.attributes['href']; break
				if "quiz" in link:
					data['tasks'][-1]['name'] = "\n├ "+f"<a href='{div.css_first('a').attributes['href']}'>{div.css_first('h3').text()}</a>\
					\n| Oxirgi muddat: {div.css_first('span').text()}"
					data['tasks'][-1]['callback_data'] = None
				else:
					data['tasks'][-1]['callback_data'] = link[link.rfind("=")+1:]
					counter += 1
		return data
#print('\n'.join(tasks))