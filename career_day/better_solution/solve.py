#!/usr/bin/env python3

# Better solution pushes kids into sessions based on their selections
# It may also downgrade them into lower pri or sessions they didn't
# pick if min students per session goals aren't met

# I resued the code from the crafting script to start this script

import random
import time

NUM_PERIODS = 4

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

	def writeSelectionLine(self, f):
		f.write(f"{self.first_name}, {self.last_name}, {self.hr}, {self.first_period}, ")
		f.write(f"{self.id}, {self.grade}")
		for i in range(4):
			f.write(f", {self.selections_attending[i].id}")
			f.write(f", {self.selections_attending[i].teacher}")
		f.write("\n")


	def isAttending(self, session):
		for s in self.selections_attending:
			if s == session:
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
	
	def tryToEnrollInNextSession(self):
		periods_to_check = []
		for p in range(NUM_PERIODS):
			if self.selections_attending[p] == None:
				periods_to_check.append(p)
		random.shuffle(periods_to_check)	

		for s in self.selections:
			if (not self.isAttending(s)):
				# Is there room?
				for p in periods_to_check:
					if (s.tryAddStudent(self, p)):
						# Success!
						print(f"Added {self.first_name} {self.last_name} to {s.subject} per {p}")
						self.selections_attending[p] = s
						return True
					
		# We are all out of choices, just assign us random session
		print(f"{self.first_name} {self.last_name} cant find a session to attend")
		return False
	
	def isFullyEnrolled(self):
		for s in self.selections_attending:
			if s == None:
				return False
		return True
					
	def tryToEnrollEmptySession(self, emptyList):
		periods_to_check = []
		for p in range(NUM_PERIODS):
			if self.selections_attending[p] == None:
				periods_to_check.append(p)
		random.shuffle(periods_to_check)

		for s in emptyList:
			if (not self.isAttending(s)):
				# Is there room?
				for p in periods_to_check:
					if (s.tryAddStudent(self, p)):
						# Success!
						print(f"Added {self.first_name} {self.last_name} to {s.subject} per {p}")
						self.selections_attending[p] = s
						return True
					
		# We are all out of choices, just assign us random session
		print(f"**** WTF {self.first_name} {self.last_name} cant find a session to attend in empty list")
		return False	





class Session:
	def __init__(self, id, subject, teacher, presenter, min_students, max_students):
		self.id = id
		self.subject = subject
		self.teacher = teacher
		self.presenter = presenter
		self.attendees = [ [] for i in range(NUM_PERIODS) ]
		self.min_students = min_students
		self.max_students = max_students

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
		f.write("PERIOD, STUDENT LAST, STUDENT FIRST\n")
		for i in range(len(self.attendees)):
			for s in self.attendees[i]:
				f.write(f"{i+1}, {s.last_name}, {s.first_name}\n")
		f.write("\n\n")

	def tryAddStudent(self, student, period):
		if (len(self.attendees[period]) >= self.max_students):
			return False
		else:
			self.attendees[period].append(student)
			return True
		
	def needMoreStudents(self):
		for per in range(NUM_PERIODS):
			if (len(self.attendees[per]) < self.min_students):
				return True
		return False
	
	def whichPeriodSmallest(self):
		min_enrolled = self.max_students
		smallest_period = None
		for per in range(NUM_PERIODS):
			if (min_enrolled > len(self.attendees[per])):
				smallest_period = per
				min_enrolled = len(self.attendees[per])
		return smallest_period


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
		cur_sess = Session(cur_id, cur_line_parts[1], cur_line_parts[2], cur_line_parts[3], min_students, max_students)

		sess_list[cur_id] = cur_sess

	return (num_sessions, min_students, max_students, sess_list)

def readStudentFile(filename, sess_dict):
	f = open(filename, "r")

	num_students = parseLineFromFile(f, "NUM_STUDENTS")

	# discard the next line
	cur_line = f.readline()

	s_list = []
	for i in range(num_students):
		cur_line = f.readline().strip()
		cur_line_parts = cur_line.split(",")
		if (len(cur_line_parts) < 7):
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
		for cur_sel_text in cur_line_parts[7:]:
			cur_sel_id = int(cur_sel_text)

			selections.append(sess_dict[cur_sel_id])

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

def sortStudentsByGrade(origList):
	sorted_list = []
	grade = 12
	while(grade > 5):
		for s in origList:
			if (s.grade == grade):
				sorted_list.append(s)
		grade -= 1

	return sorted_list



def main():
	(num_sessions, min_students, max_students, sess_dict) = readSessionFile("sessions.csv")

	sess_list = list(sess_dict.values())
	

	student_data = readStudentFile("students.csv", sess_dict)

	sorted_students = sortStudentsByGrade(student_data)

	for period in range(NUM_PERIODS):
		for s in  sorted_students:
			s.tryToEnrollInNextSession()

	students_short_enrollment = []
	for s in student_data:
		if (not s.isFullyEnrolled()):
			students_short_enrollment.append(s)

	session_needing_more_students = []
	for sid in sess_dict.keys():
		if (sess_dict[sid].needMoreStudents()):
			session_needing_more_students.append(sess_dict[sid])

	for s in students_short_enrollment:
		while(not s.isFullyEnrolled()):
			s.tryToEnrollEmptySession(session_needing_more_students)

	# At this point the students are all assigned to sessions, and none are
	# over filled, but some may not be filled to the minimum.  Lets shove
	# students from lower grades that have sessions they want into sessions
	# that no one wants...



	sessions_needing_more_students = []
	for sid in sess_dict.keys():
		if (sess_dict[sid].needMoreStudents()):
			sessions_needing_more_students.append(sess_dict[sid])

	print(f"START DOWNGRADING STUDENTS!!!")
	print(f"{len(session_needing_more_students)} sessions need more students")

	students_downgraded = set()
	infinite_loop_limit = 200
	while(len(sessions_needing_more_students) > 0):
		# Don't get stuck forever doing this
		infinite_loop_limit -= 1
		if (infinite_loop_limit < 0):
			print(f"Downgrading the nice way is exhausted attempts")
			break

		# Any students that wanted this at lower priority, shove them in

		for s in sorted_students:
			# break out of this loop if sessions fill up enough
			if (len(sessions_needing_more_students) == 0):
				break
			cur_sess = sessions_needing_more_students[0]

			if (s in students_downgraded):
				# Don't downgrade a student twice
				continue
			if (s.grade > 10):
				# Don't downgrade juniors or seniors
				continue

			# Make sure student isn't already attending
			if (s.isAttending(cur_sess)):
				continue
			
			# Did this student select thes subject as lower priority
			for selection in s.selections:
				if (selection.id == cur_sess.id):
					# Find a period that needs students and shove this kid in there
					smallest_period = cur_sess.whichPeriodSmallest()

					# Does the period we are trying to remove student from have enough?
					sess_to_rob = s.selections_attending[smallest_period]
					sess_to_rob_students_count = len(sess_to_rob.attendees[smallest_period])
					if (sess_to_rob_students_count > min_students):
						# It's safe to move this student!
						sess_to_rob.attendees[smallest_period].remove(s)
						old_subj = s.selections_attending[smallest_period]

						s.selections_attending[smallest_period] = cur_sess
						cur_sess.attendees[smallest_period].append(s)

						students_downgraded.add(s)

						print(f"Downgraded {s.first_name} {s.last_name} from {sess_to_rob.subject} to less priority {cur_sess.subject}")

						# Is the subject filled up enough now?
						if (cur_sess.needMoreStudents() == False):
							sessions_needing_more_students.pop(0)
							print(f"We filled enough empty seats in {cur_sess.subject}")
							continue

	downgrades_clear = 0
	infinite_loop_limit = 200
	while(len(sessions_needing_more_students) > 0):
		# Downgrade any student not downgraded already
		infinite_loop_limit -= 1
		if (infinite_loop_limit < 0):
			# not finding enough students to downgrade, clear the list
			students_downgraded.clear()
			print("Looped so many times, all students elgible for forcded downgrade again")
			downgrades_clear += 1
			if (downgrades_clear > 10):
				break

		for s in sorted_students:
			# break out of this loop if sessions fill up enough
			if (len(sessions_needing_more_students) == 0):
				break
			cur_sess = sessions_needing_more_students[0]

			if (s in students_downgraded):
				# Don't downgrade a student twice
				continue
			#if (s.grade > 10):
			#	# Don't downgrade juniors or seniors
			#	continue

			# Make sure student isn't already attending
			if (s.isAttending(cur_sess)):
				continue
				

			smallest_period = cur_sess.whichPeriodSmallest()
			sess_to_rob = s.selections_attending[smallest_period]
			sess_to_rob_students_count = len(sess_to_rob.attendees[smallest_period])
			if (sess_to_rob_students_count > min_students):
				# It's safe to move this student!
				sess_to_rob.attendees[smallest_period].remove(s)
				old_subj = s.selections_attending[smallest_period]

				s.selections_attending[smallest_period] = cur_sess
				cur_sess.attendees[smallest_period].append(s)

				students_downgraded.add(s)

				print(f"Downgraded {s.first_name} {s.last_name} from {sess_to_rob.subject} to {cur_sess.subject}")

				# Is the subject filled up enough now?
				if (cur_sess.needMoreStudents() == False):
					sessions_needing_more_students.pop(0)
					print(f"We filled enough empty seats in {cur_sess.subject}")
					continue



	print("DONE DOWNGRADING")

	print("Sessions not filled properly")
	for s in sessions_needing_more_students:
		print(s)

	writeStudentSelectionFile("output.csv", student_data)


if __name__ == "__main__":
	main()
