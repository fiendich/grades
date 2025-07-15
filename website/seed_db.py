from website import db
from website.models import SchoolClass, Student, Subject, Grade
from main import app

with app.app_context():
    db.drop_all()
    db.create_all()

    # Example classes
    klasse1 = SchoolClass(name="5A", teacher_id=1)
    klasse2 = SchoolClass(name="6B", teacher_id=1)
    db.session.add_all([klasse1, klasse2])
    db.session.commit()

    # Example students
    s1 = Student(first_name="Max", last_name="Mustermann", class_id=klasse1.id)
    s2 = Student(first_name="Julia", last_name="Schmidt", class_id=klasse1.id)
    s3 = Student(first_name="Ali", last_name="Yilmaz", class_id=klasse2.id)
    db.session.add_all([s1, s2, s3])
    db.session.commit()

    # Example subjects
    subj1 = Subject(name="Mathe")
    subj2 = Subject(name="Deutsch")
    db.session.add_all([subj1, subj2])
    db.session.commit()

    # Example grades
    g1 = Grade(student_id=s1.id, subject_id=subj1.id, value=2, weight=2.0, note_type="Schulaufgabe")
    g2 = Grade(student_id=s1.id, subject_id=subj2.id, value=3, weight=1.0, note_type="Kurzarbeit")
    g3 = Grade(student_id=s2.id, subject_id=subj1.id, value=1, weight=2.0, note_type="Schulaufgabe")
    db.session.add_all([g1, g2, g3])
    db.session.commit()

print("Seeded database with example data.") 