#!/usr/bin/env python3

# This script should evaulation solutions for how students were placed in
# different sessions they selected.

# It should very all sessions have student count between the min and max
# It should verify students haven't been placed in same session twice
# It should score how well students have been placed in the sessions that
#    they wanted to attend

# This script started with the code from the sample solution and then 
# was changed / will likely end up with unused code in it

import random
import time

NUM_PERIODS = 4
DETAILED_REPORT_OUTPUT = True

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
		self.selections_attending = []
		for i in range(NUM_PERIODS):
			self.selections_attending.append(None)

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

	def attendSession(self, period, session):
		if ( (period < 0) or (period >= NUM_PERIODS) ):
			print(f"{sess_num} is invalid period number")
			return

		self.selections_attending[period] = session

	def writeSelectionLine(self, f):
		f.write(f"{self.first_name}, {self.last_name}, {self.hr}, {self.first_period}, ")
		f.write(f"{self.id}, {self.grade}")
		for i in range(4):
			f.write(f", {self.selections_attending[i].id}")
			f.write(f", {self.selections_attending[i].teacher}")
		f.write("\n")
	
	def isAttending(self, session_id):
		for s in self.selections_attending:
			if (s == None):
				continue
			if (session_id == s.id):
				return True
			
		return False

	def scoreSelections(self):
		#self.debugDump()
		perfect_period_score = len(self.selections)
		perfect_score = NUM_PERIODS * perfect_period_score

		cur_period_score = perfect_period_score

		cur_score = 0
		periods_evaluated = 0
		want_list_position = 0
		while( (want_list_position < len(self.selections)) and (periods_evaluated < NUM_PERIODS) ):
			session_wanted = self.selections[want_list_position]
			want_list_position += 1

			#print(f"Debug: {self.first_name} {self.last_name} wants to attend sess id {session_wanted})")

			if (self.isAttending(session_wanted)):
				#print(f"  Debug: Attending")
				periods_evaluated += 1
				cur_score += cur_period_score
			else:
				#print(f"  Debug: not attending")
				# Student get this choice, score goes down
				cur_period_score -= 1

			#print(f"  Debug: cur_period_score = {cur_period_score} and cur_score = {cur_score}")

		if (cur_score == 0):
			return 0
		else:
			return cur_score / perfect_score * 100.0
			
	def debugDump(self):
		print(self)
		print(f"Wanted: {self.selections}")

		attend_list_items = [ str(x) for x in self.selections_attending ]
		attend_list = " ".join(attend_list_items)
		print(f"Attending: {attend_list}")


	def write_student_schedule(self, f):
		f.write(f"{self.last_name}, {self.first_name}  ID={self.id}      Homeroom Teacher={self.hr}\n")
		f.write(f"SESS, SUBJECT, TEACHER / ROOM, PRESENTER")

		if (DETAILED_REPORT_OUTPUT):
			f.write(", PRIORITY\n")
		else:
			f.write("\n")

		for i in range(NUM_PERIODS):
			cur_sel = self.selections_attending[i]
			if (cur_sel == None):
				f.write(f"{i + 1}, N/A, N/A, N/A\n")
			else:
				f.write(f"{i + 1}, {self.selections_attending[i].subject}, {self.selections_attending[i].teacher}, {self.selections_attending[i].presenter}")

				if (DETAILED_REPORT_OUTPUT):
					f.write(f", {self.sessionPriorityLookup(cur_sel.id)}\n")
				else:
					f.write("\n")
		f.write("\n\n")

	def sessionPriorityLookup(self, sid):
		selPri = 1
		retPri = None
		for curId in self.selections:
			if (curId == sid):
				retPri = selPri
			selPri += 1
		
		if (retPri == None):
			return "N/A"
		
		if (retPri == 1):
			return "1st"
		elif (retPri == 2):
			return "2nd"
		elif (retPri == 3):
			return "3rd"
		else:
			return str(retPri) + "th"


class Session:
	def __init__(self, id, subject, teacher, presenter):
		self.id = id
		self.subject = subject
		self.teacher = teacher
		self.presenter = presenter
		self.attendees = [ ]
		for i in range(NUM_PERIODS):
			self.attendees.append([])

	def __str__(self):
		print(f"For Session {self.id}, teacher={self.teacher}")
		return f"({self.id}, {self.subject}, {self.teacher}, {self.presenter})"

	def __repr__(self):
		return str(self)

	def csvData(self):
		return f"{self.id}, {self.subject}, {self.teacher}, {self.presenter}"

	def addStudent(self, student, period):
		#print(f"Adding student {student.first_name} {student.last_name} to period {period} of {self.subject}")
		self.attendees[period].append(student)

	def smallest_session(self):
		student_counts = [ len(x) for x in self.attendees ]
		return min(student_counts)

	def largest_session(self):
		student_counts = [ len(x) for x in self.attendees ]
		return max(student_counts)

	def total_students(self):
		retval = 0
		for per in self.attendees:
			retval += len(per)
		return retval
	
	def get_student_list_period(self, period):
		return self.attendees[period]
	
	def write_student_report(self, f):
		f.write(f"SUBJECT, {self.subject}\n")
		f.write(f"{self.teacher} by {self.presenter}\n")
		f.write("PERIOD, STUDENT LAST, STUDENT FIRST")

		if (DETAILED_REPORT_OUTPUT):
			f.write(", SELECTION_LEVEL")
		
		f.write(", FOLLOWING_SESSION, FOLLOWING_SESS_TEADCHER\n")

		for i in range(len(self.attendees)):
			for s in self.attendees[i]:
				f.write(f"{i+1}, {s.last_name}, {s.first_name}")

				if (DETAILED_REPORT_OUTPUT):
					f.write(f",{s.sessionPriorityLookup(self.id)}")
	
				if (i == 3):
					# Last session
					f.write(",N/A, N/A\n")
				else:
					next_sess = s.selections_attending[i+1]
					f.write(f",{next_sess.subject}, {next_sess.teacher}\n")

		f.write("\n\n")



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
	if (len(line_parts) < 2):
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
		cur_sess = Session(cur_id, cur_line_parts[1], cur_line_parts[2], cur_line_parts[3])

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
		if (len(cur_line_parts) < 8):
			print(f"Error reading line {i+5}: {cur_line}")
			continue

		timestamp = int(cur_line_parts[0])
		first = cur_line_parts[1].strip()
		last = cur_line_parts[2].strip()
		hr_teach = cur_line_parts[3].strip()
		first_teach = cur_line_parts[4].strip()
		student_id = int(cur_line_parts[5])
		grade = int(cur_line_parts[6])

		selections = []
		for sid in cur_line_parts[7:]:
			selections.append(int(sid))

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

def readSelectionFile(filename, student_data, sess_dict):
	f = open(filename, "r")

	num_students = parseLineFromFile(f, "NUM_STUDENTS")

	# discard the next line
	cur_line = f.readline()

	for i in range(num_students):
		cur_line = f.readline().strip()
		line_parts = cur_line.split(",")

		if (len(line_parts) < 7):
			print(f"Not enough columns {len(line_parts)} in line: {cur_line}")
			return None

		first_name = line_parts[0].strip()
		last_name = line_parts[1].strip()
		hr_teacher = line_parts[2].strip()
		first_period = line_parts[3].strip()
		student_id = int(line_parts[4])
		grade = int(line_parts[5])

		sel_num = 0
		selections_id_list = []
		selection_parts = line_parts[6:]
		while(sel_num < 4):
			#print(f"sel_num = {sel_num}, {selection_parts[sel_num * 2]}")
			selections_id_list.append(int(selection_parts[sel_num * 2]))
			sel_num += 1

		# Find the student in the student list
		student_obj = None
		for s in student_data:
			if ( (student_id == s.id) and (first_name == s.first_name) and (last_name == s.last_name) ):
				student_obj = s
				break

		if (student_obj == None):
			print(f"Couldn't find a matching student in recoreds for {cur_line}")
			print(f"First={first_name}, Last={last_name}, ID={student_id}")
			return None

		# Add the session information to the student object and sesssion objects
		for i in range(len(selections_id_list)):
			cur_session_id = selections_id_list[i]
			if (cur_session_id not in sess_dict):
				print(f"Can't find a matching sesssion for period {i} for student {first_name} {last_name}")
				return None

			#print(f"Debug: Adding {first_name} {last_name} to period {i} of session {sess_dict[cur_session_id]}")

			student_obj.attendSession(i, sess_dict[cur_session_id])
			sess_dict[cur_session_id].addStudent(student_obj, i)

	f.close()
	print(f"Done reading file {filename}")

# Returns true if evaluation fails
def evaluateSessions(sess_dict, min_students, max_students):
	failed_evaluation = False
	for id in sess_dict.keys():
		s = sess_dict[id]

		# Make sure each session isn't too small or too large
		if (s.smallest_session() < min_students):
			print(f"One of the sessions on subject {s.subject} has too few students ({s.smallest_session()})")
			failed_evaluation = True
		if (s.largest_session() > max_students):
			print(f"One of the sessions on subject {s.subject} has too many students ({s.largest_session()})")
			failed_evaluation = True

		# Make sure a student is signed up for more than 1 period
		for verifying_period in range(NUM_PERIODS):
			for other_period in range(NUM_PERIODS):
				if (verifying_period == other_period):
					# Can't check the period against itself
					continue;

				vp = set(s.get_student_list_period(verifying_period))
				op = set(s.get_student_list_period(other_period))

				if (len(vp.intersection(op)) > 0):
					print(f"We have some students signed up for different periods of same session:")
					print(f"  Period {verifying_period} has dupes of students from {other_period}")
					print(f"  Students in both: {vp.intersection(op)}")
					failed_evaluation = True

	return failed_evaluation

def evaluateStudents(studentList):
	# Make sure the students have NUM_PERIOD unique sessions they are signed up for
	failed_evaluation = False	
	for s in studentList:
		unique_sess = set(s.selections_attending)
		if (len(unique_sess) != NUM_PERIODS):
			print(f"Student {s.first_name} {s.last_name} is only signed up for {len(unique_sess)} sessions!")
			failed_evaluation = True
	
	return failed_evaluation

def gen_homeroom_reports(students, sess_dict):
	# Create a list of all the first period teachers
	f = open("homeroom_reports.csv", "w")
	
	fp_teachers = set()
	for s in students:
		fp_teachers.add(s.hr)

	fp_list = list(fp_teachers)
	fp_list.sort()

	for fp in fp_list:
		for s in students:
			if (fp == s.hr):
				s.write_student_schedule(f)

	f.close()
				
def gen_session_reports(sess_dict):
	f = open("session_reports.csv", "w")

	for id in sess_dict.keys():
		sess = sess_dict[id]

		sess.write_student_report(f)

	f.close()

		

def main():
	(num_sessions, min_students, max_students, sess_dict) = readSessionFile("sessions.csv")

	#sess_list = list(sess_dict.values())

	student_data = readStudentFile("students.csv")
	selection_data = readSelectionFile("output.csv", student_data, sess_dict)


	print("Beginning evaulations")
	eval_fail = False
	sess_fail = evaluateSessions(sess_dict, min_students, max_students)
	if (sess_fail):
		print("Session evaluation FAILED")
		eval_fail = True
	else:
		print("Session evaluation passed")

	studentList_fail = evaluateStudents(student_data)
	if (studentList_fail):
		print("Student evaluation FAILED")
		eval_fail = True
	else:
		print("Student evaluation passed")

	sum_all_scores = 0
	students_per_grade_level = dict()
	sum_score_per_grade_level = dict()

	for s in student_data:
		s_score = s.scoreSelections()
		print(f"Student {s.first_name} {s.last_name} in grade {s.grade} scored selections {s_score}")
		sum_all_scores += s_score

		cur_students_in_grade = students_per_grade_level.get(s.grade, 0)
		cur_students_in_grade += 1
		students_per_grade_level[s.grade] = cur_students_in_grade

		cur_sum_for_grade = sum_score_per_grade_level.get(s.grade, 0)
		cur_sum_for_grade += s_score
		sum_score_per_grade_level[s.grade] = cur_sum_for_grade
	
	avg_score = sum_all_scores / len(student_data)
	print(f"Average score all students: {avg_score}")

	# Average scores per grade
	for g in sum_score_per_grade_level.keys():
		score = sum_score_per_grade_level[g] / students_per_grade_level[g]
		print(f"Average score {g}th grade: {score}")

	gen_homeroom_reports(student_data, sess_dict)
	gen_session_reports(sess_dict)

if __name__ == "__main__":
	main()
