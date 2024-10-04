#!/usr/bin/env python3

import random

def read_file_into_list(filename):
	f = open(filename, "r")
	full_file = f.read()
	f.close()

	ret_list = []
	for each_line in full_file.split("\n"):
		ret_list.append(each_line.strip())
	
	return ret_list

class Teacher:
	def __init__(self, first, last, location):
		self.first_name = first
		self.last_name = last
		self.location = location
	
	def __str__(self):
		fi = self.first_name[0]
		return f"({fi} {self.last_name}, room={self.location})"

class Student:
	def __init__(self, first, last, teacherHr, teacherFirst):
		self.first_name = first
		self.last_name = last
		self.id = random.randint(100000, 200000)
		self.hr = teacherHr
		self.first_period = teacherFirst

	def __str__(self):
		return f"({self.first_name} {self.last_name}, id={self.id}, hr={self.hr}, 1st={self.first_period})"

def main():
	student_first_names = read_file_into_list("student_first_names.txt")
	student_last_names = read_file_into_list("student_last_names.txt")
	teacher_last_names = read_file_into_list("teacher_names.txt")
	careers = read_file_into_list("subjects.txt")

	print(student_first_names)

	teacherList = []

	for i in range(len(careers)):
		first = random.choice(student_first_names)
		last = random.choice(teacher_last_names)
		t = Teacher(first, last, i+100)
		teacherList.append(t)

	studentList = []

	for i in range(600):
		first = random.choice(student_first_names)
		last = random.choice(student_last_names)
		t_homeroom = random.choice(teacherList)
		t_first = random.choice(teacherList)
		s = Student(first, last, t_homeroom, t_first)

		studentList.append(s)

	for s in studentList:
		print(s)





if __name__ == "__main__":
	main()
