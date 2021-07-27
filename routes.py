from HospitalSystem import app, db, models
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, Response
from flask_login import current_user, login_user, logout_user, login_required
from HospitalSystem.form import LoginForm, AddPatientForm, ViewPatientForm, AddMedicineForm, CreateTestForm, IssueTestForm, IssueMedicineForm, DischargeForm
from HospitalSystem.models import Employee, Patient, Diag, Diagnostics, Med, Medicines
import json


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Employee.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


##################################################################################################
# Receptionist routes

@app.route("/receptionist/create_patient.html", methods=["GET", "POST"])
@login_required
def create_patient():
    if current_user.is_authenticated:
        form = AddPatientForm()
        if form.validate_on_submit():
            patient = Patient(
                ssn=form.ssn.data,
                pat_id=form.pat_id.data,
                pat_name=form.pat_name.data,
                adrs=form.adrs.data,
                age=form.age.data,
                doj=form.doj.data,
                rtype=form.rtype.data,
                status=form.status.data,
            )
            try:
                db.session.add(patient)
                db.session.commit()
                flash('Patient created successfully', 'success')
            except Exception as e:
                print(e)
                flash('Error - Patient with same Patient_id already exists', 'warning')
            return redirect(url_for('home'))
        return render_template('receptionist/create_patient.html', home_route="active", form=form)
    else:
        return redirect(url_for('login'))


@app.route("/delete_patient/<int:id>", methods=["GET", "POST"])
@login_required
def delete_patient(id):
    patient = db.session.query(Patient).filter_by(pat_id=id).first()
    print(patient)
    if patient:
        patient.status = models.PATIENT_STATUS['D']
        db.session.commit()
        flash('Patient Deleted successfully', 'success')
        return redirect(url_for('home'))
    return render_template('receptionist/patient_details.html', operation='delete')


@app.route("/update_patient/<int:id>", methods=["GET", "POST"])
@login_required
def update_patient(id):
    patient = db.session.query(Patient).filter_by(pat_id=id).first()
    form = AddPatientForm(obj=patient)
    if form.validate_on_submit():
        patient.ssn = form.ssn.data
        patient.pat_id = form.pat_id.data
        patient.pat_name = form.pat_name.data
        patient.adrs = form.adrs.data
        patient.age = form.age.data
        patient.doj = form.doj.data
        patient.rtype = form.rtype.data
        patient.status = form.status.data
        try:
            db.session.commit()
            flash('Patient Updated successfully', 'success')
        except Exception:
            flash('Error - Patient with same Id already exists', 'warning')
        return redirect(url_for('home'))
    return render_template("receptionist/create_patient.html", form=form, title="Update Account")


@app.route("/patient_details")
@login_required
def view_pat():
    return render_template('receptionist/patient_details.html')


@app.route("/pat_details")
@login_required
def view_patient():
    if current_user.is_authenticated:
        return render_template('receptionist/pat.html', operation=request.args.get('operation'))
    else:
        return redirect(url_for('login'))


@app.route('/billing', methods=["POST", "GET"])
@login_required
def billing():
    if request.method == "POST":
        id = request.form['id']
        amt = request.form['amt']
        patient = db.session.query(Patient).filter_by(
            pat_id=id, status=models.PATIENT_STATUS['A']).first()
        if patient:
            patient.status = models.PATIENT_STATUS['D']
            patient.amt = amt
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('receptionist/patient_bill.html')


@app.route("/api/patient_details/<int:id>", methods=["GET"])
@login_required
def pat_details(id):
    patient_activities = db.session.query(Patient).filter_by(
        pat_id=id, status=models.PATIENT_STATUS['A']).first()
    if patient_activities:
        return jsonify(patient_activities.serialize())
    return jsonify("NO")


@app.route("/api/all_patient", methods=["GET"])
@login_required
def all_pat():
    patient = db.session.query(Patient).all()
    all_pat = [{'id': k.pat_id, 'ssn': k.ssn, 'name': k.pat_name, 'adrs': k.adrs, 'age': k.age,
                'doj': k.doj, 'rtype': k.rtype, 'status': k.status, 'amt': k.amt} for k in patient]
    print(all_pat)
    if all_pat:
        return jsonify(all_pat)
    return jsonify("NO")


#######################################################################################################
# Pharmacist routes

@app.route("/medicine_list.html", methods=['GET', 'POST'])
def medicine_list():
    if current_user.is_authenticated and current_user.is_pharmacist:
        form = AddMedicineForm()
        if form.validate_on_submit():
            medicine = Med(
                # id = form.id.data,
                med_name=form.med_name.data,
                med_qty=form.med_qty.data,
                med_price=form.med_price.data,
            )
            try:
                db.session.add(medicine)
                db.session.commit()
                flash('Medicine added successfully', 'success')
            except Exception as e:
                print(e)
                flash('Error - Medicine with same id already exists', 'warning')
            return redirect(url_for('medicine_list'))

        query = models.Med.query.all()
        return render_template('pharmacist/medicine_list.html', home_route="active", query=query, form=form, title="Add Medicine")
    else:
        return redirect(url_for('login'))


@app.route("/issue_medicine.html", methods=["GET", "POST"])
@login_required
def issue_medicine():
    form = IssueMedicineForm()
    a = db.session.query(Medicines).filter_by(
        pat_id=form.pat_id.data, med_id=form.med_id.data).first()
    if form.validate_on_submit():
        update = db.session.query(Med).filter_by(
            id=form.med_id.data).first()
        if a:
            try:
                if update.med_qty < form.qty.data:
                    flash("Only {} {} is/are available".format(
                        str(update.med_qty), str(update.med_name)))
                else:
                    update.med_qty -= form.qty.data
                    a.qty += form.qty.data
                    db.session.commit()
                    flash('Medicine issued successfully', 'success')
            except Exception as e:
                print(e)
                flash('Error - Medicine with same Patient_id already exists', 'warning')
            return redirect("/issue_medicine.html")
        else:
            med = Medicines(
                pat_id=form.pat_id.data,
                med_id=form.med_id.data,
                qty=form.qty.data
            )
            try:
                if update.med_qty < form.qty.data:
                    flash("Only {} {} is/are available".format(
                        str(update.med_qty), update.med_name), 'warning')
                else:
                    update.med_qty -= form.qty.data
                    db.session.add(med)
                    db.session.commit()
                    flash('Medicine issued successfully', 'success')
            except Exception as e:
                print(e)
                flash('Error - Medicine with same Patient_id already exists', 'warning')
            return redirect("/issue_medicine.html")
    return render_template("pharmacist/issue_medicine.html", form=form)


@app.route("/api/medicine_details/<int:id>", methods=["GET"])
@login_required
def medicine_details(id):
    k = []
    result = {}
    patient_medicines = db.session.query(Medicines).filter_by(pat_id=id).all()
    all_medicines = [{'pat_id': k.pat_id, 'med_id': k.med_id,
                      'qty': k.qty} for k in patient_medicines]
    for key in all_medicines:
        k.append(key['med_id'])
    for key in k:
        r = {}
        med = db.session.query(Med).filter_by(id=key).first()
        r['name'] = med.med_name
        r['quantity'] = int(next(item['qty']
                                 for item in all_medicines if item['med_id'] == key))
        r['price'] = int(med.med_price)
        r['amount'] = r['quantity']*r['price']
        result[key] = r
    if patient_medicines:
        return jsonify(result)
    return jsonify("NO")

########################################################################################################
# Diagnostics routes


@app.route("/diagnostics/add_diagnostics.html")
def add_diagnostics():
    if current_user.is_authenticated and current_user.is_diagnostic:
        return render_template('diagnostics/add_diagnostics.html', home_route="active")
    else:
        return redirect(url_for('login'))


@app.route("/create_test", methods=["GET", "POST"])
@login_required
def create_test():
    form = CreateTestForm()
    if form.validate_on_submit():
        diag = Diag(
            diagn=form.diagn.data,
            diagn_price=form.diagn_price.data,
        )
        try:
            db.session.add(diag)
            db.session.commit()
            flash('Test created successfully', 'success')
        except Exception as e:
            print(e)
            flash('Error - Patient with same Patient_id already exists', 'warning')
        return redirect('create_test')

    query = models.Diag.query.all()
    return render_template('diagnostics/create_test.html', form=form, title="Create Test", query=query)


@app.route("/issue_test.html", methods=["GET", "POST"])
@login_required
def issue_test():
    form = IssueTestForm()
    if form.validate_on_submit():
        diag = Diagnostics(
            pat_id=form.pat_id.data,
            diagn_id=form.diagn_id.data
        )
        try:
            db.session.add(diag)
            db.session.commit()
            flash('Test issued successfully', 'success')
        except Exception as e:
            print(e)
            flash('Error - Patient with same Patient_id already exists', 'warning')
        return redirect("/issue_test.html")
    return render_template("diagnostics/issue_test.html", form=form)


@app.route("/api/test_details/<int:id>", methods=["GET"])
@login_required
def test_details(id):
    k = []
    result = {}
    patient_activities = db.session.query(
        Diagnostics).filter_by(pat_id=id).all()
    all_users = [{'pat_id': k.pat_id, 'diagn_id': k.diagn_id}
                 for k in patient_activities]
    for key in all_users:
        k.append(key['diagn_id'])
    for key in k:
        r = {}
        diag = db.session.query(Diag).filter_by(id=key).first()
        r['name'] = diag.diagn
        r['price'] = diag.diagn_price
        result[key] = r
    if patient_activities:
        return jsonify(result)
    return jsonify("NO")

########################################################################################################


@app.route("/")
@app.route("/homepage", methods=['GET', 'POST'])
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if current_user.is_pharmacist:
        return render_template('pharmacist/home.html', home_route="active")
    elif current_user.is_diagnostic:
        return render_template('diagnostics/home.html', home_route="active")
    return render_template('receptionist/home.html', home_route="active")
