#!/usr/bin/env python3

import random
import time
import datetime
from typing import List

NUM_PERIODS = 4

def read_file_into_list(filename: str) -> List[str]:
	f = open(filename, "r")
	full_file = f.read()
	f.close()

	ret_list = []
	for each_line in full_file.split("\n"):
		if (len(each_line.strip()) >= 1):
			ret_list.append(each_line.strip())
	
	return ret_list

# Splits a line of text on commas, but doesn't split quotes
def smart_split(data: str) -> List[int]:
	inQuote = False
	token = ""
	retVal = []
	for c in data:
		if ( (c == ',') and (inQuote == False) ):
			retVal.append(token)
			token = ""
			continue
		elif ( c == '"' ):
			inQuote = not inQuote
			continue

		token += c
	
	# add the last token?
	if (token != ""):
		retVal.append(token)
	return retVal


class Teacher:
	def __init__(self, first: str, last: str, location: str):
		self.first_name = first
		self.last_name = last
		self.location = location

	def shortName(self) -> str:
		#print(f"Short name for {self.first_name} {self.last_name}")
		fi = self.first_name[0]
		return f"{self.last_name} {fi}"
	
	def __str__(self) -> str:
		return f"({self.shortName()}, room={self.location})"

unique_student_ids = set()
def generate_new_student_id():
	while(True):
		random_id = random.randint(100000, 200000)
		if (random_id not in unique_student_ids):
			unique_student_ids.add(random_id)
			return random_id

class Student:
	def __init__(self, student_id:int, first:str, last:str, teacherHr: str, teacherFirst: str, grade: int, timestamp: int):
		self.first_name = first
		self.last_name = last
		self.id = student_id
		self.hr = teacherHr
		self.first_period = teacherFirst
		self.grade = grade
		self.timestamp = timestamp
		self.selections = []
		self.selections_attending = []
		for i in range(NUM_PERIODS):
			self.selections_attending.append(None)

	def setSelectionsWanted(self, selections: List[int]):
		self.selections = selections

	def __str__(self):
		return f"({self.first_name} {self.last_name}, id={self.id}, hr={self.hr}, 1st={self.first_period} {self.grade}th)"

	def __repr__(self):
		return str(self)

	def csvData(self):
		retval = ""
		retval += f"{self.timestamp}, "
		retval += f"{self.first_name}, "
		retval += f"{self.last_name}, "
		retval += f"{self.hr}, "
		retval += f"{self.first_period}, "
		retval += f"{self.id}, "
		retval += f"{self.grade}, "

		for sel in self.selections:
			if sel != None:
				retval += f"{sel}, "

		retval = retval [:-2]
		return retval

	def add_random_selection(self, maxSessId: int):
		while(True):
			randSess = random.randint(1,maxSessId)
			if (randSess not in self.selections):
				self.selections.append(randSess)
				return

	def randomize_missing_selections(self, maxSessId: int):
		# hack for algroithms that didn't like no selections
		
		if (len(self.selections) < 7):
			self.add_randome_selection()

		for i in range(len(self.selections)):
			sessId = self.selections[i]
			if (sessId == None):
				self.selections.pop(i)
				self.add_random_selection(maxSessId)


class Session:
	def __init__(self, id: int, subject: str, teacher: str, presenter: str):
		self.id = id
		self.subject = subject
		self.teacher = teacher
		self.presenter = presenter

	def __str__(self):
		print(f"For Session {self.id}, teacher={self.teacher}")
		return f"({self.id}, {self.subject}, {self.teacher}, {self.presenter})"

	def __repr__(self):
		return str(self)

	def csvData(self) -> str:
		return f"{self.id}, {self.subject}, {self.teacher}, {self.presenter}"

	def addStudent(self, student: Student, period: int):
		#print(f"Adding student {student.first_name} {student.last_name} to period {period} of {self.subject}")
		self.attendees[period].append(student)

	def smallest_session(self) -> int:
		student_counts = [ len(x) for x in self.attendees ]
		return min(student_counts)

	def largest_session(self) -> int:
		student_counts = [ len(x) for x in self.attendees ]
		return max(student_counts)

	def total_students(self) -> int:
		retval = 0
		for per in self.attendees:
			retval += len(per)
		return retval
	
	def get_student_list_period(self, period: int):
		return self.attendees[period]
	
	def write_student_report(self, f):
		f.write(f"SUBJECT, {self.subject}\n")
		f.write(f"{self.teacher} by {self.presenter}\n")
		f.write("PERIOD, STUDENT LAST, STUDENT FIRST\n")
		for i in range(len(self.attendees)):
			for s in self.attendees[i]:
				f.write(f"{i+1}, {s.last_name}, {s.first_name}\n")
		f.write("\n\n")



def writeSessionFile(filename: str, sessionList: List[Session], minNum: int, maxNum: int):
	f = open(filename, "w")
	f.write(f"NUM_SESSIONS,{len(sessionList)}\n")
	f.write(f"MIN_STUDENTS,{minNum}\n")
	f.write(f"MAX_STUDENTS,{maxNum}\n")
	f.write("ID, Subject, Teacher, Presenter\n")

	for s in sessionList:
		f.write(f"{s.csvData()}\n")

	f.close()

def writeStudentFile(filename: str, studentList: List[Student]):
	f = open(filename, "w")
	f.write(f"NUM_STUDENTS, {len(studentList)}\n")
	f.write("TIMESTAMP, FIRST_NAME, LAST_NAME, HOMEROOM, FIRST_PERIOD, ID, GRADE, ")
	f.write("CHOICE_1, CHOICE_2, CHOICE_3, CHOICE_4, CHOICE_5, CHOICE_6, CHOICE_7\n")
	for s in studentList:
		f.write(f"{s.csvData()}\n")
	f.close()

# Change problematic entries from hand auditting the list
def hs_filter(text: str) -> str:
	retVal = text.replace(" USE THIS ONE","")
	retVal = retVal.replace("places, and the teams", "places and the teams")
	retVal = retVal.replace("fun, profit, and",
		                  "fun profit and")
	retVal = retVal.replace("Attorney, Corporate", "Attorney: Corporate")
	retVal = retVal.replace("Development, Recruiting", "Development: Recruiting")
	retVal = retVal.replace("Biology, the", "Biology: the")
	retVal = retVal.upper()
	return retVal

def obfuscate_last_names(name: str) -> str:
	first_char = True
	retVal = ""
	for c in name:
		if (first_char):
			first_char = False
			retVal += c
		else:
			if (c == ' '):
				retVal += c
			else:
				retVal += "x"

	return retVal

def teacher_filter(name: str) -> str:
	name = name.upper()

	if "GLEZ" in name:
		# We have 2 Glezens
		# Mr A Glezen
		# Mrs B Glezen
		if ("MR" in name):
			if ("MRS" in name):
				return "B GLEZEN"
			else:
				return "A GLEZEN"
			
		if ("A" in name):
			return "A GLEZEN"
		else:
			return "B GLEZEN"
		
		# if we made it here, out of ideas...
		return "GLEZEN"
	
	if "BRAML" in name:
		# We have 2 Bramletts
		# Mr G Bramlett
		# Mrs L N Bramlett
		if "MR" in name:
			if "MRS" in name:
				return "N BRAMLETT"
			else:
				return "G BRAMLETT"
		
		if "G" in name:
			return "G BRAMLETT"
		else:
			return "N BRAMLETT"

	# Get rid of all the extra mr mrs ms that we don't need anymore...
	name = name.replace("MR.", "")
	name = name.replace("MR ", "")
	name = name.replace("MRS.", "")
	name = name.replace("MRS ", "")	
	name = name.replace("MS.","")
	name = name.replace("MS ", "")
	name = name.replace(" ", "")	
	
	if "BARRET" in name:
		return "BARRETT"

	if "BARROT" in name:
		return "BARRETT"

	if "DOWNIE" in name:
		return "DOWNIE"

		
	if ("SNIV" in name):
		return "SNIVELY"
	
	if ("SCOTT" in name or "RODGER" in name or "ROGER" in name):
		return "SCOTT-RODGERS"
	
	if ("PIET" in name):
		return "PIETRZAK"
	
	if ("ROBIN" in name or "ROBBIN" in name):
		return "ROBBINS"
	
	if ("ORT" in name):
		return "ORTON"
	
	if ("PAZ" in name or "PASTER" in name):
		return "PAZDERAK"

	if ("CAPRON" in name):
		return "CAPRON"

	if ("BICH" in name):
		return "KHLYABICH"
	
	if ("PITT" in name):
		return "PITTENGER"
	
	if ("GEOFF" in name):
		return "GEOFFREY"
	
	if ("WALLING" in name):
		return "WALLING"
	if ("WAIL" in name):
		return "WALLING"
	
	if ("HACKER" in name):
		return "HACKER"
	
	if ("AKANSON" == name):
		return "ATKINSON"

	if ("AUNE" in name):
		return "AUNE"
	
	if ("BARTLET" == name):
		return "BARTLETT"

	if ("ESTEBEZ" == name):
		return "ESTEVEZ"
	
	if ("GRAH" in name):
		return "GRAHAM"
	
	if ("GRIFF" in name):
		return "GRIFFIN"
	
	if ("ARCHI" in name or "ACHI" in name):
		return "ARCHIBALD"
	
	if ("JOHNSON" in name):
		return "JOHNSON"
	
	if ("OLS" in name):
		return "OLSON"
	
	if ("NAV" in name):
		return "NAVARRETE"
	
	if ("RHEM" in name):
		return "REHM"

	if ("MCCOR" in name):
		return "MCCORMICK"

	if ("REHAB" == name) or ("RAHAB" == name):
		return "RAHEB"

	if ("MARTIN" in name):
		return "MARTIN"
	
	if ("KIMBERLY" in name):
		return "KIMBERLY"
	
	if (name.startswith("VAU")):
		return "VAUTIER"

	return name

oldTimestampValue = None
def parseStudentSelectionLine(studentList: List[Student], selectionLine: str) -> Student:
	global oldTimestampValue
	lineParts = smart_split(selectionLine)

	if (len(lineParts) < 6):
		print(f"Ignoring line (not enough cells): {selectionLine}")
		return None

	if (lineParts[0] == ""):
		timestamp = oldTimestampValue
	else:
		timeObj = datetime.datetime.strptime(lineParts[0], "%m/%d/%Y %H:%M:%S")
		timestamp = int(timeObj.timestamp())
		oldTimestampValue = timestamp

	firstName = lineParts[1].strip().upper()
	#lastName = lineParts[2].strip()
	lastName = obfuscate_last_names(lineParts[2].strip())
	hrTeacher = lineParts[3].strip()

	teacher = teacher_filter(hrTeacher)
	#print(f"Converted {firstPeriod} to {teacher}")

	if (lineParts[4] == ""):
		# Not sure why so many kids now don't have a grade, but it's likely the first digits of their first name
		if (firstName[0] == '1'):
			grade = int(firstName[0:1])
		else:
			grade = int(firstName[0])
	else:
		grade = int(lineParts[4])

	# Some programs broke when names were just numbers
	#firstName = "ID#" + firstName
	
	#print(f"Name: {firstPeriod}")


	# Look at selection data
	numMaxSelections = 7
	selections = []
	for i in range(numMaxSelections):
		selections.append(None)

	for i in range(5,len(lineParts)):
		sid = i - 4

		# Did the student want this session?
		if (lineParts[i] != ""):
			# Many of the kids picked session more than once - FAIL
			if ("," in lineParts[i]):
				print(f"{firstName} {lastName} expertly picked {lineParts[i]} for sid {sid}")
				priVal = int(lineParts[i].split(",")[0])
			else:
				priVal = int(lineParts[i])

			# Somehow one of the students had a really high number in this field
			if (priVal > 7):
				priVal = 7

			selections[priVal - 1] = sid

	# So now we have a student, look and see if they are already in the list...
	for s in studentList:
		if (s.first_name == firstName) and (s.last_name == lastName) and (s.first_period == teacher):
			print(f"Removing old entry for {s.first_name} {s.last_name}")
			studentList.remove(s)

	# Add the student to the student list
	stud = Student(generate_new_student_id(), firstName, lastName,teacher, "N/A", grade, timestamp)
	stud.setSelectionsWanted(selections)
	studentList.append(stud)
	return stud

def main():

	f = open("HS.csv","r")
	wholeHs = f.read().strip()
	f.close()

	wholeHs = hs_filter(wholeHs)

	f = open("MS.csv", "r")
	wholeMs = f.read().strip()
	f.close()

	hsLines = wholeHs.split("\n")
	msLines = wholeMs.split("\n")

	# Get session information from high school since it has all the sessions
	# (ms is missing 3 sessions)
	firstLineParts = smart_split(hsLines[0])

	sessList = []
	for i in range(5, len(firstLineParts)):
		subj = firstLineParts[i].strip()
		id = i - 4
		teacher = f"TeacherSession{id}"
		presenter = f"Presenter{id}"
		sess = Session(id, subj, teacher, presenter)
		sessList.append(sess)

	# Don't overwrite sessions.csv file anymore
	#writeSessionFile("sessions.csv", sessList, 15, 25)

	teacherCounts = dict()

	studentList = []

	print("Reading High School Student Data")

	for hsStudLine in hsLines[1:]:
		s = parseStudentSelectionLine(studentList, hsStudLine)

		if (s == None):
			continue

		tc = teacherCounts.get(s.hr, 0) 
		tc += 1
		teacherCounts[s.hr] = tc

	# Hack: Make worst priority class the high school only classes at random
	for s in studentList:
		hsOnlySessionList = []
		
		if 44 not in s.selections:
			hsOnlySessionList.append(44)
		
		if 45 not in s.selections:
			hsOnlySessionList.append(45)
		
		if 46 not in s.selections:
			hsOnlySessionList.append(46)

		# Any gaps, add one of these session to HS students so HS students fill them all up
		for i in range(len(s.selections)):
			sel = s.selections[i]
			if (sel == None) and (len(hsOnlySessionList) > 0):
				sid = random.choice(hsOnlySessionList)	
				hsOnlySessionList.remove(sid)
				s.selections[i] = sid


	print("Reading Middle School Student Data")
	
	for msStudLine in msLines[1:]:
		s = parseStudentSelectionLine(studentList, msStudLine)

		if (s == None):
			continue

		tc = teacherCounts.get(s.first_period, 0) 
		tc += 1
		teacherCounts[s.first_period] = tc



	namelist = list(teacherCounts.keys())
	namelist.sort()
	for name in namelist:
		print(f"{name} {teacherCounts[name]}")


	print(f"Read in data for {len(studentList)} students")

	#for s in studentList:
	#	s.randomize_missing_selections(44)

	writeStudentFile("students.csv", studentList)





if __name__ == "__main__":
	main()
