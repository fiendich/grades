from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify, abort
from flask_login import login_required, current_user
from . import db
from .models import SchoolClass, Student, Subject, Grade
from datetime import datetime

views = Blueprint('views',__name__)

@views.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('views.students_page'))
    else:
        return redirect(url_for('auth.login'))

@views.route('/grades/class', methods=['GET'])
@login_required
def class_selection():
    classes = SchoolClass.query.filter_by(teacher_id=current_user.id).all()
    return render_template('klassenwahl.html', classes=classes, user=current_user)

@views.route('/students', methods=['GET'])
@login_required
def students_page():
    classes = SchoolClass.query.filter_by(teacher_id=current_user.id).all()
    selected_class_id = request.args.get('class_id', type=int)
    students = []
    if selected_class_id:
        students = Student.query.filter_by(class_id=selected_class_id).all()
    return render_template('students.html', classes=classes, students=students, selected_class_id=selected_class_id, user=current_user)

@views.route('/api/students')
@login_required
def api_students():
    class_id = request.args.get('class_id', type=int)
    students = []
    if class_id:
        school_class = SchoolClass.query.get(class_id)
        if not school_class or school_class.teacher_id != current_user.id:
            abort(403)
        students = Student.query.filter_by(class_id=class_id).all()
    return jsonify({
        'students': [
            {'id': s.id, 'first_name': s.first_name, 'last_name': s.last_name} for s in students
        ]
    })

@views.route('/grades/table', methods=['GET'])
@login_required
def grades_table():
    selected_class_id = request.args.get('class_id', type=int)
    selected_student_id = request.args.get('student_id', type=int)
    selected_subject_id = request.args.get('subject_id', type=int)
    if not selected_class_id or not selected_student_id:
        return redirect(url_for('views.class_selection'))
    selected_class = SchoolClass.query.get(selected_class_id)
    if not selected_class or selected_class.teacher_id != current_user.id:
        abort(403)
    selected_student = Student.query.get(selected_student_id)
    if not selected_student or selected_student.class_id != selected_class_id:
        abort(403)
    grades = Grade.query.filter_by(student_id=selected_student_id).all()
    subjects = Subject.query.all()
    return render_template(
        'noten.html',
        grades=grades,
        selected_student=selected_student,
        selected_class_id=selected_class_id,
        subjects=subjects,
        user=current_user,
        today=datetime.now().strftime('%d.%m.%Y'),
        selected_subject_id=selected_subject_id
    )

@views.route('/grades/add', methods=['POST'])
@login_required
def add_grade():
    from .models import Grade
    student_id = request.form.get('student_id', type=int)
    subject_id = request.form.get('subject_id', type=int)
    value = request.form.get('value', type=float)
    weight = request.form.get('weight', type=float)
    student = Student.query.get(student_id)
    if not student:
        abort(403)
    school_class = SchoolClass.query.get(student.class_id)
    if not school_class or school_class.teacher_id != current_user.id:
        abort(403)
    new_grade = Grade(
        student_id=student_id,
        subject_id=subject_id,
        value=value,
        weight=weight
    )
    db.session.add(new_grade)
    db.session.commit()
    flash("Note hinzugefügt!", category="success")
    return redirect(url_for('views.grades_table', class_id=student.class_id, student_id=student_id, subject_id=subject_id))

@views.route('/grades/edit/<int:grade_id>', methods=['POST'])
@login_required
def edit_grade(grade_id):
    grade = Grade.query.get_or_404(grade_id)
    student = grade.student
    school_class = SchoolClass.query.get(student.class_id)
    if not school_class or school_class.teacher_id != current_user.id:
        abort(403)
    value = request.form.get('value', type=float)
    weight = request.form.get('weight', type=float)
    if value is not None:
        grade.value = value
    if weight is not None:
        grade.weight = weight
    db.session.commit()
    flash('Note aktualisiert!', category='success')
    class_id = grade.student.class_id
    student_id = grade.student.id
    return redirect(url_for('views.grades_table', class_id=class_id, student_id=student_id))

@views.route('/grades/delete/<int:grade_id>', methods=['POST'])
@login_required
def delete_grade(grade_id):
    grade = Grade.query.get_or_404(grade_id)
    student = grade.student
    school_class = SchoolClass.query.get(student.class_id)
    if not school_class or school_class.teacher_id != current_user.id:
        abort(403)
    student_id = grade.student_id
    class_id = grade.student.class_id
    subject_id = grade.subject_id
    db.session.delete(grade)
    db.session.commit()
    flash('Note gelöscht!', category='success')
    return redirect(url_for('views.grades_table', class_id=class_id, student_id=student_id, subject_id=subject_id))


