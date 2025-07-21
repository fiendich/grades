from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify, abort
from flask_login import login_required, current_user
from . import db
from .models import SchoolClass, Student, Subject, Grade
from .models import User
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo
import random
from .models import encrypt_note

views = Blueprint('views',__name__)

@views.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('views.students_page'))
    else:
        return redirect(url_for('auth.login'))

@views.route('/students', methods=['GET'])
@login_required
def students_page():
    classes = SchoolClass.query.filter_by(teacher_id=current_user.id).all()
    selected_class_id = request.args.get('class_id', type=int)
    students = []
    if selected_class_id:
        students = Student.query.filter_by(class_id=selected_class_id).all()
    subjects = Subject.query.all()
    return render_template('students.html', classes=classes, students=students, selected_class_id=selected_class_id, user=current_user, subjects=subjects)

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
    # Decrypt grades for display
    for g in grades:
        g.decrypted_value = g.get_note()
    subjects = Subject.query.all()
    users = User.query.all()

    # Prepare overview data per subject
    overview_data = []
    for subject in subjects:
        subject_grades = [g for g in grades if g.subject_id == subject.id]
        schulaufgaben = [g for g in subject_grades if g.note_type == 'Schulaufgabe']
        ex_kurz = [g for g in subject_grades if g.note_type in ['Ex', 'Kurzarbeit']]
        # Grades as comma-separated strings
        schulaufgaben_str = ', '.join(str(g.decrypted_value) for g in schulaufgaben)
        ex_kurz_str = ', '.join(str(g.decrypted_value) for g in ex_kurz)
        # Calculate average (weighted average of all grades)
        total = sum(g.decrypted_value * g.weight for g in subject_grades)
        weight_sum = sum(g.weight for g in subject_grades)
        avg = (total / weight_sum) if weight_sum > 0 else None
        # Final grade: round average to better grade (e.g. 2.5 -> 2)
        abschluss = None
        if avg is not None:
            # Rounding: x.5 always round down (better grade), >x.5 round up
            if avg - int(avg) <= 0.5:
                abschluss = int(avg)
            else:
                abschluss = int(avg) + 1
        overview_data.append({
            'subject': subject.name,
            'schulaufgaben': schulaufgaben_str,
            'ex_kurz': ex_kurz_str,
            'avg': round(avg, 2) if avg is not None else '-',
            'abschluss': abschluss if abschluss is not None else '-'
        })

    return render_template(
        'noten.html',
        grades=grades,
        selected_student=selected_student,
        selected_class_id=selected_class_id,
        subjects=subjects,
        user=current_user,
        today=datetime.now().strftime('%d.%m.%Y'),
        selected_subject_id=selected_subject_id,
        overview_data=overview_data,
        users=users
    )

@views.route('/grades/add', methods=['POST'])
@login_required
def add_grade():
    from .models import Grade, encrypt_note
    student_id = request.form.get('student_id', type=int)
    subject_id = request.form.get('subject_id', type=int)
    value = request.form.get('value', type=float)
    weight = request.form.get('weight', type=float)
    note_type = request.form.get('note_type')
    kommentar = request.form.get('kommentar')
    date_str = request.form.get('date')
    # Parse date if provided, else None
    date = None
    if date_str:
        try:
            date = datetime.strptime(date_str, '%d.%m.%Y')
        except Exception:
            date = None
    # Ensure weight for 'Ex' is 1.0
    if note_type == 'Ex':
        weight = 1.0
    student = Student.query.get(student_id)
    if not student:
        abort(403)
    school_class = SchoolClass.query.get(student.class_id)
    if not school_class or school_class.teacher_id != current_user.id:
        abort(403)
    # Temporary ID for encryption (set after commit)
    temp_id = random.randint(100000, 999999)
    enc_value = encrypt_note(value, temp_id, subject_id, current_user.id)
    new_grade = Grade(
        student_id=student_id,
        subject_id=subject_id,
        value=enc_value,
        weight=weight,
        note_type=note_type,
        kommentar=kommentar,
        date=date,
        created_by=current_user.id,
        created_at=datetime.now(ZoneInfo('Europe/Berlin'))
    )
    db.session.add(new_grade)
    db.session.commit()
    # After commit: ID is set, re-encrypt value
    new_grade.value = encrypt_note(value, new_grade.id, subject_id, current_user.id)
    db.session.commit()
    flash("Note added!", category="success")
    return redirect(url_for('views.grades_table', class_id=student.class_id, student_id=student_id, subject_id=subject_id))

@views.route('/grades/edit/<int:grade_id>', methods=['POST'])
@login_required
def edit_grade(grade_id):
    from .models import encrypt_note
    grade = Grade.query.get_or_404(grade_id)
    student = grade.student
    school_class = SchoolClass.query.get(student.class_id)
    if not school_class or school_class.teacher_id != current_user.id:
        abort(403)
    value = request.form.get('value', type=float)
    weight = request.form.get('weight', type=float)
    if value is not None:
        grade.value = encrypt_note(value, grade.id, grade.subject_id, grade.created_by)
    if weight is not None:
        grade.weight = weight
    db.session.commit()
    flash('Grade updated!', category='success')
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
    flash('Grade deleted!', category='success')
    return redirect(url_for('views.grades_table', class_id=class_id, student_id=student_id, subject_id=subject_id))

@views.route('/grades/bulk_add', methods=['POST'])
@login_required
def bulk_add_grades():
    data = request.get_json()
    class_id = data.get('class_id')
    subject_id = data.get('subject_id')
    note_type = data.get('note_type')
    date_str = data.get('date')
    weight = data.get('weight')
    kommentar = data.get('kommentar')
    notes = data.get('notes', [])

    # Parse date
    date = None
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        except Exception:
            date = None

    # Class and teacher check
    school_class = SchoolClass.query.get(class_id)
    if not school_class or school_class.teacher_id != current_user.id:
        return jsonify({'success': False, 'message': 'No permission for this class!'}), 403

    # Save grades
    for note in notes:
        student_id = note.get('student_id')
        value = note.get('value')
        if value is None or value == '':
            continue  # No grade for this student
        student = Student.query.get(student_id)
        if not student or student.class_id != int(class_id):
            continue
        # Encrypt as in single add
        temp_id = random.randint(100000, 999999)
        enc_value = encrypt_note(float(value), temp_id, int(subject_id), current_user.id)
        new_grade = Grade(
            student_id=student_id,
            subject_id=subject_id,
            value=enc_value,
            weight=weight,
            note_type=note_type,
            kommentar=kommentar,
            date=date,
            created_by=current_user.id,
            created_at=datetime.now(ZoneInfo('Europe/Berlin'))
        )
        db.session.add(new_grade)
        db.session.flush()  # So that ID is set
        new_grade.value = encrypt_note(float(value), new_grade.id, int(subject_id), current_user.id)
    db.session.commit()
    return jsonify({'success': True})


