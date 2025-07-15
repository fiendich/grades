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
    note_type = db.Column(db.String(50), nullable=False, default='Schulaufgabe')  # Art der Note
    value = db.Column(db.Integer, nullable=False)  # Note als int (1-6)
    weight = db.Column(db.Float, default=1.0)  # z. B. Schulaufgabe = 2.0
    thema = db.Column(db.String(200), nullable=True)  # Beschreibung/Thema
    kommentar = db.Column(db.String(300), nullable=True)  # Optionaler Kommentar
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    __table_args__ = (
        db.CheckConstraint('value >= 1 AND value <= 6', name='check_note_value_range'),
    )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(150),unique=True)
    password = db.Column(db.String(150))
    firstName = db.Column(db.String(150))
    classes = db.relationship('SchoolClass', backref='teacher')

