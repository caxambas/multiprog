from flask import Flask, request, render_template, redirect, flash
from wtforms import Form, SelectField, validators, ValidationError
from multi import *
app = Flask(__name__)

"""
Ideally, this will be the flask app function with the view functions, maybe also the form classes.
TODO:
-Is there a cleaner way of passing the arguments that I pass with the html file to render_template, and do I really have to define them if they are not passed?
"""

@app.route('/') # This will need to have a different start file
def index():
    #print "I'm back at Index()!"
    return render_template('start.html')

@app.route('/multi', methods=['GET', 'POST'])
def multi():
    """
    This is the flash view function for /multi, takes GET and POST methods
    """   
    form = MultiForm(request.form)

    if request.method == 'GET':

        pps_output, ecog_output, kps_output, ppi_output, pap_output, dpap_output = {},{},{},{},{},{}
        clinical_guess = ''
        #print form.validate()
        return render_template('multi.html', form=form, pps_output=pps_output, ecog_output=ecog_output, kps_output=kps_output, ppi_output=ppi_output, pap_output=pap_output, dpap_output=dpap_output, clinical_guess=clinical_guess, error='')
        
    # POST method gets data from form fields, sends to the functions in multi.py and returns main_function
    elif request.method == 'POST' and validate_models(form):
        print 'posted and validated'
        pps_output, ecog_output, kps_output, ppi_output, pap_output, dpap_output, clinical_guess, review = main_function(form.data) 

        return render_template('results.html', form=form, pps_output=pps_output, ecog_output=ecog_output,  kps_output=kps_output, ppi_output=ppi_output, pap_output=pap_output, dpap_output=dpap_output, clinical_guess=clinical_guess, review=review, error='')
    else: # tried to POST but form didn't validate
        print 'else'
        print form.errors 
        pps_output, ecog_output, kps_output, ppi_output, pap_output, dpap_output = {},{},{},{},{},{}
        clinical_guess = ''
        return render_template('multi.html', form=form, pps_output=pps_output, ecog_output=ecog_output, kps_output=kps_output, ppi_output=ppi_output, pap_output=pap_output, dpap_output=dpap_output, clinical_guess=clinical_guess, error=form.errors)

   
@app.route('/reference', methods=['GET'])
def reference():
    return render_template('reference.html')
    

              



