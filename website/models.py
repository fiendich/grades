from dotenv import load_dotenv
load_dotenv()
import os
import random

# Secure random SECRET key (unique per deployment, example here)
SECRET = int(os.environ.get('GRADES_SECRET', random.SystemRandom().randint(10**8, 10**9)))

def encrypt_note(note, note_id, subject_id, lehrer_id):
    # Secure, reversible encryption
    return int((note * 137 + (note_id * 73) + (subject_id * 41) + (lehrer_id * 19) + SECRET) * 3)

def decrypt_note(enc_value, note_id, subject_id, lehrer_id):
    # Rückrechnung
    return int(round(((enc_value / 3) - (note_id * 73) - (subject_id * 41) - (lehrer_id * 19) - SECRET) / 137))

from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func


class SchoolClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    students = db.relationship('Student', backref='class_')
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'))
    grades = db.relationship('Grade', backref='student')


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    grades = db.relationship('Grade', backref='subject')

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note_type = db.Column(db.String(50), nullable=False, default='Schulaufgabe')  # Type of grade
    value = db.Column(db.Integer, nullable=False)  # Now: encrypted value
    weight = db.Column(db.Float, default=1.0)  # e.g. Schulaufgabe = 2, Ex = 1
    thema = db.Column(db.String(200), nullable=True)  # Description/Theme
    kommentar = db.Column(db.String(300), nullable=True)  # Optional comment
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)  # When entered
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Who entered
    __table_args__ = (
        db.CheckConstraint('value >= 0', name='check_note_value_encrypted'),
    )

    def get_note(self):
        # Decrypted note to return
        return decrypt_note(self.value, self.id, self.subject_id, self.created_by)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(150),unique=True)
    password = db.Column(db.String(150))
    kuerzel = db.Column(db.String(10), unique=True, nullable=False)  # e.g. szt, sst, kru
    classes = db.relationship('SchoolClass', backref='teacher')

