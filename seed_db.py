from website import create_app, db
from website.models import User, SchoolClass, Student, Subject, Grade
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Create a test teacher
    teacher = User(email='teacher@example.com', password=generate_password_hash('password', method='sha256'), firstName='TestTeacher')
    db.session.add(teacher)
    db.session.commit()

    # Create classes
    class1 = SchoolClass(name='Class 1A', teacher_id=teacher.id)
    class2 = SchoolClass(name='Class 2B', teacher_id=teacher.id)
    db.session.add_all([class1, class2])
    db.session.commit()

    # Create students
    student1 = Student(first_name='Alice', last_name='Muster', class_id=class1.id)
    student2 = Student(first_name='Bob', last_name='Beispiel', class_id=class1.id)
    student3 = Student(first_name='Charlie', last_name='Test', class_id=class2.id)
    db.session.add_all([student1, student2, student3])
    db.session.commit()

    # Create 5 subjects
    subject_names = [
        'Mathematik', 'Deutsch', 'Englisch', 'Biologie', 'Chemie'
    ]
    subjects = [Subject(name=n) for n in subject_names]
    db.session.add_all(subjects)
    db.session.commit()

    # Create grades for the first 3 subjects for each student as example
    for student in [student1, student2, student3]:
        for i, subject in enumerate(subjects[:3]):
            db.session.add(Grade(
                value=(i+2)%6+1,  # 2,3,4
                weight=1.0 + i,
                note_type='Schulaufgabe',
                student_id=student.id,
                subject_id=subject.id,
                date=datetime(2024, 5, 10 + i*5),
                kommentar=f'{subject.name} Test'
            ))
    db.session.commit()

    print('Dummy data with integer grades inserted!') 