"""
Utility functions for Teacher app
"""
import re
from USER.models import User
from .models import Classroom


def find_students_for_classroom(classroom):
    """
    Find all students that belong to a given classroom.
    Uses flexible matching to handle different formats:
    - Exact match (case-insensitive): "Grade 10-A" matches "Grade 10-A"
    - Name match: "Grade 10-A" matches "10-A" or "10A"
    - Grade+Section match: Matches by grade and section separately
    - Partial match: "Grade 10-A" matches "10-A" or "10A" or "10"
    
    Args:
        classroom: Classroom instance
        
    Returns:
        QuerySet of User objects (students)
    """
    if not classroom:
        return User.objects.none()
    
    classroom_name = classroom.name.strip() if classroom.name else ""
    classroom_grade = classroom.grade.strip() if classroom.grade else ""
    classroom_section = classroom.section.strip() if classroom.section else ""
    
    # Build a list of possible matches
    all_students = User.objects.filter(role='student')
    matching_students = []
    
    for student in all_students:
        if not student.class_grade:
            continue
            
        student_class = student.class_grade.strip()
        student_class_upper = student_class.upper()
        classroom_name_upper = classroom_name.upper()
        
        # Method 1: Exact match (case-insensitive, whitespace-tolerant)
        if student_class_upper == classroom_name_upper:
            matching_students.append(student)
            continue
        
        # Method 2: Extract grade and section from student class_grade
        # Try patterns like "10-A", "10A", "10 A", "Grade 10-A", etc.
        student_grade = None
        student_section = None
        
        # Try to extract grade and section from student class_grade
        # Pattern 1: "10-A" or "10A"
        match = re.match(r'(\d+)[\s\-]?([A-Za-z])?', student_class)
        if match:
            student_grade = match.group(1)
            if match.group(2):
                student_section = match.group(2).upper()
        
        # Pattern 2: "Grade 10-A" or "Grade 10 A"
        if not student_grade:
            match = re.search(r'(\d+)[\s\-]?([A-Za-z])?', student_class)
            if match:
                student_grade = match.group(1)
                if match.group(2):
                    student_section = match.group(2).upper()
        
        # Method 3: Match by grade and section if available
        if student_grade and classroom_grade:
            if student_grade == classroom_grade:
                # If sections match or one is empty, consider it a match
                if not classroom_section or not student_section or student_section == classroom_section.upper():
                    if student not in matching_students:
                        matching_students.append(student)
                    continue
        
        # Method 4: Partial match - check if classroom name contains student class or vice versa
        if student_class_upper in classroom_name_upper or classroom_name_upper in student_class_upper:
            if student not in matching_students:
                matching_students.append(student)
            continue
        
        # Method 5: Match if grade is in both (for cases like "10" matching "Grade 10-A")
        if student_grade and classroom_grade and student_grade == classroom_grade:
            if student not in matching_students:
                matching_students.append(student)
    
    # Return as a queryset
    if matching_students:
        student_ids = [s.id for s in matching_students]
        return User.objects.filter(id__in=student_ids)
    else:
        return User.objects.none()


