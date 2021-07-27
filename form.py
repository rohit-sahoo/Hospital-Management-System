from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextField, SelectField, IntegerField, DateTimeField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.fields.html5 import DateField
from HospitalSystem import models, db
from datetime import date


class LoginForm(FlaskForm):
    login_as = SelectField('Login As', choices=[(
        v, v) for k, v in models.USER_TYPE.items()], validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class AddPatientForm(FlaskForm):
    pat_id = IntegerField('Patient ID', validators=[DataRequired()])
    ssn = IntegerField('SSN', validators=[DataRequired()])
    pat_name = StringField('Patient Name', validators=[DataRequired()])
    adrs = StringField('Patient Address', validators=[DataRequired()])
    age = IntegerField('Patient Age', validators=[DataRequired()])
    doj = DateField('Date of Joinig', format="%Y-%m-%d",
                    default=date.today(), validators=[DataRequired()])
    rtype = SelectField('Room Type', choices=[
                        (v, v) for k, v in models.ROOM_TYPE.items()])
    status = SelectField('Status', choices=[
                         (v, v) for k, v in models.PATIENT_STATUS.items()])
    submit = SubmitField('Submit')


class CreateTestForm(FlaskForm):
    diagn = StringField("Diagnosis Test", validators=[DataRequired()])
    diagn_price = IntegerField("Test Price", validators=[DataRequired()])
    submit = SubmitField('Submit')


class IssueTestForm(FlaskForm):
    pat_id = IntegerField("Patient ID", validators=[DataRequired()])
    # diagn_id = QuerySelectField(query_factory=lambda: models.Diag.query.all(),get_label='diagn',get_pk=lambda x: x.id,allow_blank=True)
    diagn_id = SelectField(coerce=int)
    submit = SubmitField('Issue')

    def __init__(self):
        super(IssueTestForm, self).__init__()
        self.diagn_id.choices = [(k.id, k.diagn)
                                 for k in db.session.query(models.Diag).all()]


class ViewPatientForm(FlaskForm):
    ws_pat_id = IntegerField("Patient ID", validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddMedicineForm(FlaskForm):
    # id = IntegerField('Medicine ID', validators=[DataRequired()])
    med_name = StringField('Medicine Name', validators=[DataRequired()])
    med_qty = IntegerField('Medicine Quantity', validators=[DataRequired()])
    med_price = IntegerField('Medicine Price', validators=[DataRequired()])
    submit = SubmitField('Add')


class IssueMedicineForm(FlaskForm):
    pat_id = IntegerField("Patient ID", validators=[DataRequired()])
    med_id = SelectField(coerce=int)
    qty = IntegerField("Quantity", validators=[DataRequired()])
    submit = SubmitField('Issue')

    def __init__(self):
        super(IssueMedicineForm, self).__init__()
        self.med_id.choices = [(k.id, k.med_name)
                               for k in db.session.query(models.Med).all()]

    def validate_med_id(self, med_id):
        med = db.session.query(models.Med).filter_by(id=med_id.data).first()
        if med.med_qty <= 0:
            raise ValidationError(
                "Medicine is not available. Select a different medicine.")


class DischargeForm(FlaskForm):
    id = IntegerField('id', validators=[DataRequired()])
    submit = SubmitField('Discharge')
