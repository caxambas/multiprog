from flask import Flask, request, render_template, redirect, flash
from wtforms import Form, StringField, SelectField, DecimalField, RadioField, BooleanField, validators, ValidationError
from multi import *
app = Flask(__name__)

"""
Ideally, this will be the flask app function with the view functions, maybe also the form classes.
"""

"""
Master To Do List (for multi-prog)
1/10:
-Need to figure out the secret key thing

"""
app.secret_key = 'llama' # which one of these do I need, if any?
SECRET_KEY = 'testing'

LR_dict = {'death_rattle': [9.0, 0.8],'pulseless_radial': [15.6, 0.89],'mandibular': [10.0, 0.8], 'decreased_uop': [15.2, 0.77], 'cheyne_stokes': [12.4, 0.9], 'nr_pupils': [16.7, 0.86], 'decreased_verbal': [8.3, 0.73], 'decreased_visual': [6.7, 0.72], 'eyelids':[13.6, 0.8], 'nasolabial': [8.3, 0.69], 'hyper_neck': [7.3, 0.82], 'grunting': [11.8, 0.82], 'ugib': [10.3, 0.97]}

def flash_errors(form): #Is this even being used?
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

class PrePostForm(Form):
    pretest = DecimalField('Pretest Probability (in percent)',  [validators.Required(), validators.NumberRange(min=0, max=100, message='Must be between 0 and 100')])

    death_rattle = RadioField('Death Rattle:', choices=[('present', 'Present'), ('absent', 'Absent'), ('na', 'Not Applicable')], default='na')
    pulseless_radial = RadioField('Pulseless Radial Artery (either side):', choices=[('present', 'Present'), ('absent', 'Absent'), ('na', 'Not Applicable')], default='na')
    mandibular = RadioField('Respirations with Mandibular Movement:', choices=[('present', 'Present'), ('absent', 'Absent'), ('na', 'Not Applicable')], default='na')
    decreased_uop = RadioField('Decreased Urine Output (< 100 cc in 12 hrs):', choices=[('present', 'Present'), ('absent', 'Absent'), ('na', 'Not Applicable')], default='na')
    cheyne_stokes = RadioField('Cheyne-Stokes Breathing: ', choices=[('present', 'Present'), ('absent', 'Absent'), ('na', 'Not Applicable') ], default='na')

    nr_pupils = RadioField('Non-reactive Pupils: ', choices=[('present', 'Present'), ('absent', 'Absent'), ('na', 'Not Applicable')], default='na')
    decreased_verbal = RadioField('Decreased Response to Verbal Stimuli: ', choices=[('present', 'Present'), ('absent', 'Absent'), ('na', 'Not Applicable')], default='na')
    decreased_visual = RadioField('Decreased Response to Visual Stimuli: ', choices=[('present', 'Present'), ('absent', 'Absent'), ('na', 'Not Applicable')], default='na')
    eyelids = RadioField('Inability to Close Eyelids: ', choices=[('present', 'Present'), ('absent', 'Absent'), ('na', 'Not Applicable')], default='na')
    nasolabial = RadioField('Drooping of Nasolabial Fold: ', choices=[('present', 'Present'), ('absent', 'Absent'), ('na', 'Not Applicable')], default='na')
    hyper_neck = RadioField('Hyperextension of the Neck: ', choices=[('present', 'Present'), ('absent', 'Absent'), ('na', 'Not Applicable')], default='na')
    grunting = RadioField('Vocal Cord Grunting: ', choices=[('present', 'Present'), ('absent', 'Absent'), ('na', 'Not Applicable')], default='na')
    ugib = RadioField('Upper GI Bleed: ', choices=[('present', 'Present'), ('absent', 'Absent'), ('na', 'Not Applicable')], default='na')

    posttest = DecimalField('Post Test Probability (in percent): ')

class RecursiveForm(Form):

    PPS = SelectField('PPS: ', choices=((10, '10%'), (20, '20%'), (30, '30%'), (40, '40%'), (50, '50%'), (60, '60%'), (70, '70%'), (80, '80%'),(90, '90%'), (100, '100%')))

    nasolabial_field = BooleanField('Drooping of Nasolabial Fold: ')
    death_rattle = BooleanField('Death Rattle:')
    pulseless_radial = BooleanField('Pulseless Radial Artery (either side):')
    mandibular = BooleanField('Respirations with Mandibular Movement:')
    cheyne_stokes = BooleanField('Cheyne-Stokes Breathing: ')

    nr_pupils = BooleanField('Non-reactive Pupils: ')
    decreased_verbal = BooleanField('Decreased Response to Verbal Stimuli: ')
    decreased_visual = BooleanField('Decreased Response to Visual Stimuli: ')
    eyelids = BooleanField('Inability to Close Eyelids: ')
    hyper_neck = BooleanField('Hyperextension of the Neck: ')
    grunting = BooleanField('Vocal Cord Grunting: ')
    ugib = BooleanField('Upper GI Bleed: ')
    cyanosis = BooleanField('Peripheral Cyanosis: ')

    final_score_field = DecimalField('Chance of death in the next 72 hrs (in percent): ')

@app.route('/')
def index():
    #print "I'm back at Index()!"
    return render_template('start.html')

@app.route('/recursive', methods=['GET','POST'])
def recursive():

    post_test_prob = 0
    form = RecursiveForm(request.form)

    bool_field_list = []
    for i in form:
        if i.name != 'PPS' and i.name != 'final_score_field':
            bool_field_list.append(i)
    #print bool_field_list

    #This calculates the number of positive late signs in the boolean lists
    num_late_signs = 0
    for i in bool_field_list:
        if i.data == True:
            num_late_signs += 1
    #print num_late_signs

    #Now begins the POST request and basic calculator
    if request.method == 'POST':
        #print 'PPS', form.PPS.data
        #print form.nasolabial_field.data
        #print "Posted successfully"
        PPS = int(form.PPS.data)
        if PPS <= 20:
            if form.nasolabial_field.data == True:
                post_test_prob = 94
            else:
                if num_late_signs >= 2:
                    post_test_prob = 62
                else:
                    post_test_prob = 32
        elif PPS >= 30:
            if PPS >= 70:
                post_test_prob = 3 #percent
            else: # PPS 30-60%
                if num_late_signs >= 2:
                    post_test_prob = 26
                else:
                    post_test_prob = 14

        return render_template('imp2.html',form=form, post_test_prob=post_test_prob)

    elif request.method == 'GET':
        #print "Recursive GET ok"
        return render_template('imp2.html', form=form, post_test_prob=post_test_prob)
    else:
        flash_errors(form)
        #print form.data
        return render_template('imp2.html', form=form, post_test_prob=post_test_prob)

@app.route('/prepost', methods=['GET', 'POST'])
def prepost():

# Dictionary of LR ratios, key is shortened name, value is a list with first entry is positive LR, second is the negative LR
    post_test_prob = 0
    #print 'testing'
    form = PrePostForm(request.form) # maybe needs request.form in here
    form_list = []
    for i in form:
        if i.name != 'pretest' and i.name != 'posttest':
            form_list.append(i)

    #print form_list
    #print request.method
    #print form.data
    #print "form.validate() is", form.validate()
    #print request.form

    if request.method == 'POST' and form.validate():
        #print "Posted and validated!"
        pretest_prob = float(form.pretest.data)/ 100.0
        pretest_odds = pretest_prob / (1.0 - pretest_prob) # Need odds to apply LR
        #print 'pretest_odds', pretest_odds
        # The following calculates a multiplier for the odds ratio, looks in form_list (which contains the LR forms), sees if i.data is present, absent or na and then adjusts it by the appropriate LR via LR_dict
        multiplier = 1.0
        for i in form_list:
            #print 'i.data', i.data
            if i.data == 'present':
                #print LR_dict[i.name][0]
                multiplier *= LR_dict[i.name][0] #[0] is the + LR
            elif i.data == 'absent':
                multiplier *= LR_dict[i.name][1] #[1] is the - LR
            else:
                continue
        print multiplier
        post_odds = pretest_odds * multiplier
        post_prob = post_odds * 100.0 / (1.0 + post_odds) # Gets post probability from odds

        return render_template('impending.html', form=form, post_test_prob=post_prob)

    elif request.method == 'GET':
       return render_template('impending.html', form=form, post_test_prob=post_test_prob)
    else:
        flash_errors(form)
        return render_template('impending.html', form=form, post_test_prob=post_test_prob)

@app.route('/multi', methods=['GET', 'POST'])
def multi():
    """
    This is the flash view function for /multi, takes GET and POST methods
    """   
    form = MultiForm(request.form)

    if request.method == 'GET':

        pps_output, ecog_output, kps_output, ppi_output, psppi_output, pap_output, dpap_output = {},{},{},{},{},{},{}
        clinical_guess = ''
        incomplete_models = []
        #print form.validate()
        return render_template('multi.html', form=form, pps_output=pps_output, ecog_output=ecog_output, kps_output=kps_output, ppi_output=ppi_output, psppi_output=psppi_output, pap_output=pap_output, dpap_output=dpap_output, clinical_guess=clinical_guess, error='', incomplete_models=incomplete_models)
        
    # POST method gets data from form fields, sends to the functions in multi.py and returns main_function
    elif request.method == 'POST' and validate_models(form):
        print 'posted and validated'
        pps_output, ecog_output, kps_output, ppi_output, psppi_output, pap_output, dpap_output, clinical_guess, review, incomplete_models = main_function(form.data) 

        return render_template('results.html', form=form, pps_output=pps_output, ecog_output=ecog_output,  kps_output=kps_output, ppi_output=ppi_output, psppi_output=psppi_output, pap_output=pap_output, dpap_output=dpap_output, clinical_guess=clinical_guess, review=review, error='', incomplete_models=incomplete_models)
    else: # tried to POST but form didn't validate
        print 'else'
        print form.errors 
        pps_output, ecog_output, kps_output, ppi_output, psppi_output, pap_output, dpap_output = {},{},{},{},{},{},{}
        clinical_guess = ''
        incomplete_models = []
        return render_template('multi.html', form=form, pps_output=pps_output, ecog_output=ecog_output, kps_output=kps_output, ppi_output=ppi_output, psppi_output=psppi_output, pap_output=pap_output, dpap_output=dpap_output, clinical_guess=clinical_guess, error=form.errors, incomplete_models=incomplete_models)

    

    
@app.route('/reference', methods=['GET'])
def reference():
    return render_template('reference.html')
    

              



