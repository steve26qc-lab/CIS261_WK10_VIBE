"""Student record manager for CIS261.

Features:
- Add and remove students
- Store student name and student id
- Record three test scores (Test 1, Test 2, Test 3)
- Calculate average score and letter grade
- Print student reports
- Save/load records from students.json
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

DATA_FILE = "students.json"


@dataclass
class StudentRecord:
    name: str
    student_id: str
    scores: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    average: float = field(init=False)
    grade: str = field(init=False)

    def __post_init__(self) -> None:
        self.update_metrics()

    def set_scores(self, scores: List[float]) -> bool:
        if len(scores) != 3:
            return False
        self.scores = [float(score) for score in scores]
        self.update_metrics()
        return True

    def update_metrics(self) -> None:
        self.average = sum(self.scores) / len(self.scores)
        self.grade = self.calculate_letter_grade()

    def calculate_letter_grade(self) -> str:
        if self.average >= 90:
            return "A"
        if self.average >= 80:
            return "B"
        if self.average >= 70:
            return "C"
        if self.average >= 60:
            return "D"
        return "F"


class StudentManager:
    def __init__(self) -> None:
        self.records: Dict[str, StudentRecord] = {}
        self.load()

    def add_student(self, name: str, student_id: str) -> bool:
        key = student_id.strip()
        if not key or key in self.records or not name.strip():
            return False
        self.records[key] = StudentRecord(name=name.strip().title(), student_id=key)
        return True

    def remove_student(self, student_id: str) -> bool:
        key = student_id.strip()
        if key in self.records:
            del self.records[key]
            return True
        return False

    def update_scores(self, student_id: str, scores: List[float]) -> bool:
        key = student_id.strip()
        student = self.records.get(key)
        if student is None:
            return False
        return student.set_scores(scores)

    def get_student(self, student_id: str) -> Optional[StudentRecord]:
        return self.records.get(student_id.strip())

    def list_students(self) -> List[StudentRecord]:
        return sorted(self.records.values(), key=lambda student: student.name)

    def save(self) -> bool:
        data = {
            student_id: {"name": record.name, "scores": record.scores}
            for student_id, record in self.records.items()
        }
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except OSError as error:
            print(f"Error: Could not save student records to {DATA_FILE}. {error}")
            return False

    def load(self) -> None:
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for student_id, details in data.items():
                scores = [float(score) for score in details.get("scores", [0.0, 0.0, 0.0])]
                record = StudentRecord(
                    name=details.get("name", "").strip().title(),
                    student_id=student_id.strip(),
                    scores=scores,
                )
                self.records[student_id] = record
        except FileNotFoundError:
            print(f"Note: No existing record file found at {DATA_FILE}. Starting fresh.")
        except json.JSONDecodeError:
            print(f"Warning: {DATA_FILE} is not valid JSON. Starting with an empty record list.")
        except (OSError, ValueError) as error:
            print(f"Error: Could not load student records from {DATA_FILE}. {error}")


def prompt_nonempty_string(prompt: str) -> Optional[str]:
    value = input(prompt).strip()
    if not value:
        print("Input cannot be blank. Please try again.")
        return None
    return value


def print_main_menu() -> None:
    print("\nStudent Record Manager")
    print("1. Add student")
    print("2. Add multiple students")
    print("3. Remove student")
    print("4. Update three test scores")
    print("5. View student report")
    print("6. List all students")
    print("7. Save and exit")


def prompt_float(prompt: str) -> Optional[float]:
    value = input(prompt).strip()
    try:
        return float(value)
    except ValueError:
        print("Invalid input. Please enter a numeric value.")
        return None


def prompt_three_scores() -> Optional[List[float]]:
    scores: List[float] = []
    for test_number in range(1, 4):
        score = prompt_float(f"Test {test_number} score (0-100): ")
        if score is None or score < 0 or score > 100:
            print("Invalid score. Please enter a number between 0 and 100.")
            return None
        scores.append(score)
    return scores


def add_student_flow(manager: StudentManager) -> None:
    name = prompt_nonempty_string("Student name: ")
    if name is None:
        return
    student_id = prompt_nonempty_string("Student ID: ")
    if student_id is None:
        return
    if manager.add_student(name, student_id):
        print(f"Student '{name.title()}' with ID '{student_id}' was added successfully.")
    else:
        print("Could not add the student. The student ID may already exist or input was invalid.")


def add_multiple_students_flow(manager: StudentManager) -> None:
    print("\nEnter student records one at a time. Leave the student name blank to stop.")
    while True:
        name = input("Student name: ").strip()
        if not name:
            print("Finished adding multiple students.")
            break
        student_id = prompt_nonempty_string("Student ID: ")
        if student_id is None:
            continue
        if manager.add_student(name, student_id):
            print(f"Added '{name.title()}' (ID: {student_id}).")
        else:
            print(f"Could not add '{name.title()}'. The ID may already exist.")


def remove_student_flow(manager: StudentManager) -> None:
    student_id = prompt_nonempty_string("Student ID to remove: ")
    if student_id is None:
        return
    if manager.remove_student(student_id):
        print(f"Removed student with ID '{student_id}'.")
    else:
        print("Student not found. Please verify the student ID.")


def update_scores_flow(manager: StudentManager) -> None:
    student_id = prompt_nonempty_string("Student ID: ")
    if student_id is None:
        return
    scores = prompt_three_scores()
    if scores is None:
        return
    if manager.update_scores(student_id, scores):
        print(f"Scores updated for student ID '{student_id}'.")
    else:
        print("Student not found. Please verify the student ID.")


def view_student_report_flow(manager: StudentManager) -> None:
    student_id = prompt_nonempty_string("Student ID: ")
    if student_id is None:
        return
    student = manager.get_student(student_id)
    if student:
        print_student_report(student)
    else:
        print("Student not found. Please verify the student ID.")


def list_students_flow(manager: StudentManager) -> None:
    students = manager.list_students()
    if not students:
        print("No students registered.")
        return
    print("\nRegistered Students:")
    for student in students:
        avg_text = f"{student.average:.2f}"
        print(f"  {student.name} ({student.student_id}): average={avg_text}, grade={student.grade}")


def print_student_report(student: StudentRecord) -> None:
    print(f"\nStudent: {student.name}")
    print(f"Student ID: {student.student_id}")
    print("Scores:")
    for index, score in enumerate(student.scores, start=1):
        print(f"  Test {index}: {score:.2f}")
    print(f"Average: {student.average:.2f}")
    print(f"Letter grade: {student.grade}")


def main() -> None:
    manager = StudentManager()

    while True:
        print_main_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_student_flow(manager)
        elif choice == "2":
            add_multiple_students_flow(manager)
        elif choice == "3":
            remove_student_flow(manager)
        elif choice == "4":
            update_scores_flow(manager)
        elif choice == "5":
            view_student_report_flow(manager)
        elif choice == "6":
            list_students_flow(manager)
        elif choice == "7":
            if manager.save():
                print("Student records saved successfully. Exiting.")
            else:
                print("Student records could not be saved. Exiting without saving.")
            break
        else:
            print("Invalid option. Please choose a number from 1 to 7.")


if __name__ == "__main__":
    main()
