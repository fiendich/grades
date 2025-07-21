from website import db
from website.models import SchoolClass, Student, Subject, Grade, User, encrypt_note
from main import app
from werkzeug.security import generate_password_hash
from datetime import datetime

with app.app_context():
    # Lehrer mit Kürzel anlegen
    lehrer1 = User(email="szt@schule.de", password="demo", kuerzel="szt")
    lehrer2 = User(email="sst@schule.de", password="demo", kuerzel="sst")
    db.session.add_all([lehrer1, lehrer2])
    db.session.commit()

    # Beispiel-Klassen
    klasse1 = SchoolClass(name="5A", teacher_id=lehrer1.id)
    klasse2 = SchoolClass(name="6B", teacher_id=lehrer2.id)
    db.session.add_all([klasse1, klasse2])
    db.session.commit()

    # 10 Schüler pro Klasse
    schueler_1 = [Student(first_name=f"Max{i+1}", last_name=f"Mustermann{i+1}", class_id=klasse1.id) for i in range(10)]
    schueler_2 = [Student(first_name=f"Julia{i+1}", last_name=f"Schmidt{i+1}", class_id=klasse2.id) for i in range(10)]
    db.session.add_all(schueler_1 + schueler_2)
    db.session.commit()

    # Beispiel-Fächer
    subj1 = Subject(name="Mathe")
    subj2 = Subject(name="Deutsch")
    db.session.add_all([subj1, subj2])
    db.session.commit()

    # Beispiel-Noten für die ersten 2 Schüler jeder Klasse
    grades = []
    # Für Klasse 1
    for idx, s in enumerate(schueler_1[:2]):
        grades.append(Grade(
            student_id=s.id,
            subject_id=subj1.id,
            value=encrypt_note(2+idx, idx+1, subj1.id, lehrer1.id),
            weight=2.0,
            note_type="Schulaufgabe",
            kommentar="SA 1",
            created_by=lehrer1.id
        ))
        grades.append(Grade(
            student_id=s.id,
            subject_id=subj2.id,
            value=encrypt_note(3+idx, idx+2, subj2.id, lehrer1.id),
            weight=1.0,
            note_type="Kurzarbeit",
            kommentar="KA 1",
            created_by=lehrer1.id
        ))
    # Für Klasse 2
    for idx, s in enumerate(schueler_2[:2]):
        grades.append(Grade(
            student_id=s.id,
            subject_id=subj1.id,
            value=encrypt_note(1+idx, idx+3, subj1.id, lehrer2.id),
            weight=2.0,
            note_type="Schulaufgabe",
            kommentar="SA 1",
            created_by=lehrer2.id
        ))
        grades.append(Grade(
            student_id=s.id,
            subject_id=subj2.id,
            value=encrypt_note(4+idx, idx+4, subj2.id, lehrer2.id),
            weight=1.0,
            note_type="Ex",
            kommentar="Ex 1",
            created_by=lehrer2.id
        ))
    db.session.add_all(grades)
    db.session.commit()

    print("Seeded database with 2 Klassen, je 10 Schüler, und Beispielnoten.") 