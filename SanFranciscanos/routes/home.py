from flask import Blueprint, render_template, request, redirect, url_for, flash
from SanFranciscanos.forms import DataSheetForm
from SanFranciscanos.db import get_mongo_db


bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    form = DataSheetForm()
    return render_template('pagina-inicio.html', form=form)

@bp.route('/login')
def login():
    return render_template('log-in.html')

@bp.route('/datasheet', methods=['POST'])
def datasheet():
    form = DataSheetForm()
    if form.validate_on_submit():
        db = get_mongo_db()
        data = {
            'c_firstName': form.c_firstName.data,
            'c_secondName': form.c_secondName.data,
            'c_lastName': form.c_lastName.data,
            'c_secondLastName': form.c_secondLastName.data,
            'c_sex': form.c_sex.data,
            'ds_sonNumbr': form.ds_sonNumbr.data,
            'ds_numbrBrothers': form.ds_numbrBrothers.data,
            'ds_livesWith': form.ds_livesWith.data,
            'ds_residentialPhone': form.ds_residentialPhone.data,
            'ds_mainAddress': form.ds_mainAddress.data,
            'c_birthdate': form.c_birthdate.data,
            'c_bloodType': form.c_bloodType.data,
            'c_alergies': form.c_alergies.data,
            'c_emergencyContactName': form.c_emergencyContactName.data,
            'c_emergencyContactPhone': form.c_emergencyContactPhone.data,
            'c_details': form.c_details.data,
            'c_idInstitution': form.c_idInstitution.data,
            'ds_idInstitution': form.ds_idInstitution.data,
            'ds_idCatequizando': form.ds_idCatequizando.data,
            'ds_idLevel': form.ds_idLevel.data,
            'ds_schoolsName': form.ds_schoolsName.data,
            'ds_schoolGrade': form.ds_schoolGrade.data,
        }
        db.datasheets.insert_one(data)
        flash("Ficha registrada correctamente", "success")
        return redirect(url_for('home.index'))
    else:
        flash("Ocurrió un error en el registro", "danger")
        return render_template('pagina-inicio.html', form=form)
