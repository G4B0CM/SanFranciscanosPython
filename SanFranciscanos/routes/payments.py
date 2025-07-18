from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson import ObjectId
from datetime import datetime
from SanFranciscanos.forms import PaymentForm, DeleteForm
from SanFranciscanos.db import get_mongo_db

bp = Blueprint('payments', __name__, url_prefix='/payments')

@bp.route('/')
def index():
    db = get_mongo_db()
    payments = list(db.payments.find())
    delete_form = DeleteForm()
    return render_template('payments/list_payments.html', payments=payments, delete_form=delete_form)


@bp.route('/new', methods=['GET', 'POST'])
def create_payment():
    db = get_mongo_db()
    form = PaymentForm()

    # Validar si viene de un flujo guiado
    person_id = request.args.get('person_id')
    
    if person_id:
        person = db.students.find_one({'_id': ObjectId(person_id)})
        if not person:
            flash("Catequizado no válido para el pago.", "danger")
            return redirect(url_for('students.list_students'))

        # Validar si ya tiene un pago registrado
        existing_payment = db.payments.find_one({'person_id': ObjectId(person_id)})
        if existing_payment:
            flash("Este catequizado ya tiene un pago registrado.", "info")
            return redirect(url_for('students.create_student', person_id=person_id))

        # Limitar el formulario a este catequizado
        form.person_id.choices = [(person_id, f"{person.get('firstName', '')} {person.get('lastName', '')}")]
        form.person_id.data = person_id
    else:
        # Mostrar todos si se accede directamente
        form.person_id.choices = [(str(p['_id']), f"{p.get('firstName', '')} {p.get('lastName', '')}") for p in db.students.find()]

    if form.validate_on_submit():
        payment = {
            'person_id': ObjectId(form.person_id.data),
            'amount': float(form.amount.data),
            'method': form.method.data,
            'date': form.date.data,
            'notes': form.notes.data,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        db.payments.insert_one(payment)
        flash("Pago registrado exitosamente.", "success")

        # Redirigir al registro del catequizado
        return redirect(url_for('students.create_student', person_id=form.person_id.data))

    return render_template('payments/payment_form.html', form=form, title="Nuevo Pago")


@bp.route('/<id>')
def detail_payment(id):
    db = get_mongo_db()
    payment = db.payments.find_one({'_id': ObjectId(id)})
    student = db.students.find_one({'_id': payment.get('person_id')}) if payment else None
    return render_template('payments/detail_payment.html', payment=payment, student=student)


@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit_payment(id):
    db = get_mongo_db()
    payment = db.payments.find_one({'_id': ObjectId(id)})
    if not payment:
        flash("Pago no encontrado.", "danger")
        return redirect(url_for('payments.index'))

    form = PaymentForm(
        person_id=str(payment['person_id']),
        amount=payment['amount'],
        method=payment['method'],
        date=payment['date'],
        notes=payment['notes']
    )

    form.person_id.choices = [(str(p['_id']), f"{p.get('firstName', '')} {p.get('lastName', '')}") for p in db.students.find()]

    if form.validate_on_submit():
        updates = {
            'person_id': ObjectId(form.person_id.data),
            'amount': float(form.amount.data),
            'method': form.method.data,
            'date': form.date.data,
            'notes': form.notes.data,
            'updatedAt': datetime.utcnow()
        }
        db.payments.update_one({'_id': ObjectId(id)}, {'$set': updates})
        flash("Pago actualizado correctamente.", "success")
        return redirect(url_for('payments.index'))

    return render_template('payments/payment_form.html', form=form, title="Editar Pago")


@bp.route('/delete/<id>', methods=['POST'])
def delete_payment(id):
    db = get_mongo_db()
    db.payments.delete_one({'_id': ObjectId(id)})
    flash("Pago eliminado correctamente.", "success")
    return redirect(url_for('payments.index'))
