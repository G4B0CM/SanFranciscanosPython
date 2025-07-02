from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from bson import ObjectId
from datetime import datetime
from SanFranciscanos.forms import DataSheetForm, DeleteForm

bp = Blueprint('Students', __name__, url_prefix='/students')

@bp.route('/')
def index():
    students = current_app.mongo_db.datasheets.find()
    delete_form = DeleteForm()
    return render_template('students/list_students.html', students=students, delete_form=delete_form)

@bp.route('/new', methods=['GET', 'POST'])
def new():
    form = DataSheetForm()
    if form.validate_on_submit():
        student = {
            'firstName': form.c_firstName.data,
            'secondName': form.c_secondName.data,
            'lastName': form.c_lastName.data,
            'secondLastName': form.c_secondLastName.data,
            'sex': form.c_sex.data,
            'birthdate': form.c_birthdate.data.strftime('%Y-%m-%d'),
            'bloodType': form.c_bloodType.data,
            'alergies': form.c_alergies.data,
            'emergencyContactName': form.c_emergencyContactName.data,
            'emergencyContactPhone': form.c_emergencyContactPhone.data,
            'details': form.c_details.data,
            'idInstitution': form.c_idInstitution.data,
            'ds_sonNumbr': form.ds_sonNumbr.data,
            'ds_numbrBrothers': form.ds_numbrBrothers.data,
            'ds_livesWith': form.ds_livesWith.data,
            'ds_residentialPhone': form.ds_residentialPhone.data,
            'ds_mainAddress': form.ds_mainAddress.data,
            'ds_idInstitution': form.ds_idInstitution.data,
            'ds_idCertificate': form.ds_idCertificate.data,
            'ds_idLevel': form.ds_idLevel.data,
            'ds_schoolsName': form.ds_schoolsName.data,
            'ds_schoolGrade': form.ds_schoolGrade.data,
            'createdAt': datetime.now(),
            'updatedAt': datetime.now()
        }
        current_app.mongo_db.datasheets.insert_one(student)
        return redirect(url_for('Students.index'))
    
    return render_template('students/student_form.html', form=form, title='Nuevo Catequizado')

@bp.route('/<id>')
def detail(id):
    student = current_app.mongo_db.datasheets.find_one({'_id': ObjectId(id)})
    return render_template('students/detail_student.html', student=student)

@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    student = current_app.mongo_db.datasheets.find_one({'_id': ObjectId(id)})
    form = DataSheetForm(data={
        'c_firstName': student.get('firstName'),
        'c_secondName': student.get('secondName'),
        'c_lastName': student.get('lastName'),
        'c_secondLastName': student.get('secondLastName'),
        'c_sex': student.get('sex'),
        'c_birthdate': student.get('birthdate'),
        'c_bloodType': student.get('bloodType'),
        'c_alergies': student.get('alergies'),
        'c_emergencyContactName': student.get('emergencyContactName'),
        'c_emergencyContactPhone': student.get('emergencyContactPhone'),
        'c_details': student.get('details'),
        'c_idInstitution': student.get('idInstitution'),
        'ds_sonNumbr': student.get('ds_sonNumbr'),
        'ds_numbrBrothers': student.get('ds_numbrBrothers'),
        'ds_livesWith': student.get('ds_livesWith'),
        'ds_residentialPhone': student.get('ds_residentialPhone'),
        'ds_mainAddress': student.get('ds_mainAddress'),
        'ds_idInstitution': student.get('ds_idInstitution'),
        'ds_idCertificate': student.get('ds_idCertificate'),
        'ds_idLevel': student.get('ds_idLevel'),
        'ds_schoolsName': student.get('ds_schoolsName'),
        'ds_schoolGrade': student.get('ds_schoolGrade')
    })

    if form.validate_on_submit():
        updated_data = {
            'firstName': form.c_firstName.data,
            'secondName': form.c_secondName.data,
            'lastName': form.c_lastName.data,
            'secondLastName': form.c_secondLastName.data,
            'sex': form.c_sex.data,
            'birthdate': form.c_birthdate.data.strftime('%Y-%m-%d'),
            'bloodType': form.c_bloodType.data,
            'alergies': form.c_alergies.data,
            'emergencyContactName': form.c_emergencyContactName.data,
            'emergencyContactPhone': form.c_emergencyContactPhone.data,
            'details': form.c_details.data,
            'idInstitution': form.c_idInstitution.data,
            'ds_sonNumbr': form.ds_sonNumbr.data,
            'ds_numbrBrothers': form.ds_numbrBrothers.data,
            'ds_livesWith': form.ds_livesWith.data,
            'ds_residentialPhone': form.ds_residentialPhone.data,
            'ds_mainAddress': form.ds_mainAddress.data,
            'ds_idInstitution': form.ds_idInstitution.data,
            'ds_idCertificate': form.ds_idCertificate.data,
            'ds_idLevel': form.ds_idLevel.data,
            'ds_schoolsName': form.ds_schoolsName.data,
            'ds_schoolGrade': form.ds_schoolGrade.data,
            'updatedAt': datetime.now()
        }
        current_app.mongo_db.datasheets.update_one({'_id': ObjectId(id)}, {'$set': updated_data})
        return redirect(url_for('Students.index'))

    return render_template('students/student_form.html', form=form, title='Editar Catequizado')

@bp.route('/delete/<id>', methods=['POST'])
def delete(id):
    current_app.mongo_db.datasheets.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('Students.index'))
