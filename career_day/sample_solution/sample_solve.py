#!/usr/bin/env python3

# This sample solution justs randomly places students in random sessions.  So
# it shouldn't score well, but likely will create a valid solution since the
# randomness should distribute the students pretty evenly

# I resued the code from the crafting script to start this script

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

class Student:
	def __init__(self, student_id, first, last, teacherHr, teacherFirst, grade, timestamp):
		self.first_name = first
		self.last_name = last
		self.id = student_id
		self.hr = teacherHr
		self.first_period = teacherFirst
		self.grade = grade
		self.timestamp = timestamp
		self.selections = []
		self.selections_attending = [None, None, None, None]

	def setSelectionsWanted(self, selections):
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
			retval += f"{sel}, "

		retval = retval [:-2]
		return retval

	def attendSession(self, sess_num, session):
		if ( (sess_num < 0) or (sess_num >= 4) ):
			print(f"{sess_num} is a session number")
			return

		self.selections_attending[sess_num] = session

	def writeSelectionLine(self, f):
		f.write(f"{self.first_name}, {self.last_name}, {self.hr}, {self.first_period}, ")
		f.write(f"{self.id}, {self.grade}")
		for i in range(4):
			f.write(f", {self.selections_attending[i].id}")
			f.write(f", {self.selections_attending[i].teacher}")
		f.write("\n")


class Session:
	def __init__(self, id, subject, teacher, presenter):
		self.id = id
		self.subject = subject
		self.teacher = teacher
		self.presenter = presenter
		self.attendees = []

	def __str__(self):
		print(f"For Session {self.id}, teacher={self.teacher}")
		return f"({self.id}, {self.subject}, {self.teacher}, {self.presenter})"

	def __repr__(self):
		return str(self)

	def csvData(self):
		return f"{self.id}, {self.subject}, {self.teacher}, {self.presenter}"

	def addStudent(self, student):
		self.attendees.append(student)

def writeSessionFile(filename, sessionList, minNum, maxNum):
	f = open(filename, "w")
	f.write(f"NUM_SESSIONS,{len(sessionList)}\n")
	f.write(f"MIN_STUDENTS,{minNum}\n")
	f.write(f"MAX_STUDENTS,{maxNum}\n")
	f.write("ID, Subject, Teacher, Presenter\n")

	for s in sessionList:
		f.write(f"{s.csvData()}\n")

	f.close()

def parseLineFromFile(f, line_name):
	single_line = f.readline().strip()
	line_parts = single_line.split(",")
	if (len(line_parts) != 2):
		print(f"Line for {line_name} invalid: {single_line}")
		return None

	if (line_parts[0] != line_name):
		print(f"Line for {line_name} invalid: {single_line}")
		return None

	value = int(line_parts[1])
	return value

def readSessionFile(filename):
	f = open(filename, "r")

	num_sessions = parseLineFromFile(f, "NUM_SESSIONS")
	min_students = parseLineFromFile(f, "MIN_STUDENTS")
	max_students = parseLineFromFile(f, "MAX_STUDENTS")

	if ( (num_sessions == None) or (min_students == None) or (max_students == None) ):
		return None

	# discard the next line
	cur_line = f.readline()

	sess_list = dict()
	for i in range(num_sessions):
		cur_line = f.readline().strip()
		cur_line_parts = cur_line.split(",")
		if (len(cur_line_parts) < 4):
			print(f"Error reading line {i+5}: {cur_line}")
			continue

		cur_id = int(cur_line_parts[0])
		cur_sess = Session(cur_id, cur_line_parts[0], cur_line_parts[2], cur_line_parts[2])

		sess_list[cur_id] = cur_sess

	return (num_sessions, min_students, max_students, sess_list)

def readStudentFile(filename):
	f = open(filename, "r")

	num_students = parseLineFromFile(f, "NUM_STUDENTS")

	# discard the next line
	cur_line = f.readline()

	s_list = []
	for i in range(num_students):
		cur_line = f.readline().strip()
		cur_line_parts = cur_line.split(",")
		if (len(cur_line_parts) < 14):
			print(f"Error reading line {i+5}: {cur_line}")
			continue

		timestamp = int(cur_line_parts[0])
		first = cur_line_parts[1]
		last = cur_line_parts[2]
		hr_teach = cur_line_parts[3]
		first_teach = cur_line_parts[4]
		student_id = int(cur_line_parts[5])
		grade = int(cur_line_parts[6])

		selections = []
		for choice_num in range(7):
			selections.append(cur_line_parts[7 + choice_num])

		cur_student = Student(student_id, first, last, hr_teach, first_teach, grade, timestamp)
		cur_student.setSelectionsWanted(selections)

		s_list.append(cur_student)

	return s_list

def writeStudentFile(filename, studentList):
	f = open(filename, "w")
	f.write(f"NUM_STUDENTS, {len(studentList)}\n")
	f.write("TIMESTAMP, FIRST_NAME, LAST_NAME, HOMEROOM, FIRST_PERIOD, ID, GRADE, ")
	f.write("CHOICE_1, CHOICE_2, CHOICE_3, CHOICE_4, CHOICE_5, CHOICE_6, CHOICE_7\n")
	for s in studentList:
		f.write(f"{s.csvData()}\n")
	f.close()

def writeStudentSelectionFile(filename, studentList):
	f = open(filename, "w")
	f.write(f"NUM_STUDENTS, {len(studentList)}\n")
	f.write("FIRST_NAME, LAST_NAME, HR_TEACH, FIRST_PERIOD, STUDENT_ID, GRADE, ")
	f.write("SEL1_ID, SEL1_TEACH, SEL2_ID, SEL2_TEACH, SEL3_ID, SEL3_TEACH, ")
	f.write("SEL4_ID, SEL4_TEACH\n")

	for s in studentList:
		s.writeSelectionLine(f)

	f.close()

def main():
	(num_sessions, min_students, max_students, sess_dict) = readSessionFile("sessions.csv")

	sess_list = list(sess_dict.values())

	student_data = readStudentFile("students.csv")

	for cur_s in student_data:
		sess_list_copy = sess_list[:]
		for i in range(4):
			sess = random.choice(sess_list_copy)
			sess_list_copy.remove(sess)
			sess.addStudent(cur_s)
			cur_s.attendSession(i, sess)

	


	#print(student_data)

	writeStudentSelectionFile("output.csv", student_data)


if __name__ == "__main__":
	main()
