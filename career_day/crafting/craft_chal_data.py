#!/usr/bin/env python3

import random
import time

def read_file_into_list(filename):
	f = open(filename, "r")
	full_file = f.read()
	f.close()

	ret_list = []
	for each_line in full_file.split("\n"):
		if (len(each_line.strip()) >= 1):
			ret_list.append(each_line.strip())
	
	return ret_list

class Teacher:
	def __init__(self, first, last, location):
		self.first_name = first
		self.last_name = last
		self.location = location

	def shortName(self):
		#print(f"Short name for {self.first_name} {self.last_name}")
		fi = self.first_name[0]
		return f"{self.last_name} {fi}"
	
	def __str__(self):
		return f"({self.shortName()}, room={self.location})"

class Student:
	def __init__(self, first, last, teacherHr, teacherFirst, grade, timestamp):
		self.first_name = first
		self.last_name = last
		self.id = random.randint(100000, 200000)
		self.hr = teacherHr
		self.first_period = teacherFirst
		self.grade = grade
		self.timestamp = timestamp
		self.selections = set()

	def setSelections(self, selections):
		self.selections = selections

	def __str__(self):
		return f"({self.first_name} {self.last_name}, id={self.id}, hr={self.hr}, 1st={self.first_period} {self.grade}th)"

	def csvData(self):
		retval = ""
		retval += f"{self.timestamp}, "
		retval += f"{self.first_name}, "
		retval += f"{self.last_name}, "
		retval += f"{self.hr.shortName()}, "
		retval += f"{self.last_name}, "
		retval += f"{self.id}, "
		retval += f"{self.grade}, "

		for sel in self.selections:
			retval += f"{sel}, "

		retval = retval [:-2]
		return retval



class Session:
	def __init__(self, id, subject, teacher, presenter):
		self.id = id
		self.subject = subject
		self.teacher = teacher
		self.presenter = presenter

	def __str__(self):
		print(f"For Session {self.id}, teacher={self.teacher}")
		tsn = self.teacher.shortName()
		return f"({self.id}, {self.subject}, {tsn}, {self.presenter})"

	def csvData(self):
		return f"{self.id}, {self.subject}, {self.teacher.shortName()}, {self.presenter}"


def writeSessionFile(filename, sessionList, minNum, maxNum):
	f = open(filename, "w")
	f.write(f"NUM_SESSIONS,{len(sessionList)}\n")
	f.write(f"MIN_STUDENTS,{minNum}\n")
	f.write(f"MAX_STUDENTS,{maxNum}\n")
	f.write("ID, Subject, Teacher, Presenter\n")

	for s in sessionList:
		f.write(f"{s.csvData()}\n")

	f.close()

def writeStudentFile(filename, studentList):
	f = open(filename, "w")
	f.write(f"NUM_STUDENTS, {len(studentList)}\n")
	f.write("TIMESTAMP, FIRST_NAME, LAST_NAME, HOMEROOM, FIRST_PERIOD, ID, GRADE, ")
	f.write("CHOICE_1, CHOICE_2, CHOICE_3, CHOICE_4, CHOICE_5, CHOICE_6, CHOICE_7\n")
	for s in studentList:
		f.write(f"{s.csvData()}\n")
	f.close()


def main():
	student_first_names = read_file_into_list("student_first_names.txt")
	student_last_names = read_file_into_list("student_last_names.txt")
	teacher_last_names = read_file_into_list("teacher_names.txt")
	careers = read_file_into_list("subjects.txt")

	#print(student_first_names)

	teacherList = []

	for i in range(len(careers)):
		first = random.choice(student_first_names)
		last = random.choice(teacher_last_names)
		t = Teacher(first, last, i+100)
		teacherList.append(t)

	MIN_STUDENTS = 5
	MAX_STUDENTS = 20

	sessionList = []
	teachersLeft = teacherList[:]

	for i in range(len(careers)):
		id = i + 1
		t = random.choice(teachersLeft)
		teachersLeft.remove(t)
		s = Session(id, careers[i], t, f"Presenter {(i+1)}")
		sessionList.append(s)

	writeSessionFile("sessions.csv", sessionList, MIN_STUDENTS, MAX_STUDENTS)

	studentList = []
	
	time_now = int(time.time())
	time_2_weeks = time_now + 60*60 * 24 * 14

	for i in range(600):
		first = random.choice(student_first_names)
		last = random.choice(student_last_names)
		t_homeroom = random.choice(teacherList)
		t_first = random.choice(teacherList)
		ts = random.randint(time_now, time_2_weeks)
		grade = 7 + (i % 6)
		s = Student(first, last, t_homeroom, t_first, grade, ts)

		selections = set()
		while(len(selections) < 7):
			if (i < 100):
				# Overflow some sessions
				session_choice = random.choice(sessionList[:10])
			elif (i < 300):
				session_choice = random.choice(sessionList[:20])
			else:
				session_choice = random.choice(sessionList)
			selections.add(session_choice.id)

		selection_list = list(selections)
		random.shuffle(selection_list)
		s.setSelections(selection_list)

		studentList.append(s)

	writeStudentFile("students.csv", studentList)
	



if __name__ == "__main__":
	main()
