from flask import Flask, request, render_template
from flask_sslify import SSLify

from multi import *
from recursive import *
from prepost import *

app = Flask(__name__)
sslify = SSLify(app) # to redirect everything to https

@app.route('/list', methods=['GET'])
def list():
    return render_template('list.html')
    
@app.route('/', methods=['GET', 'POST'])
def multi():
    """
    This is the flash view function for /multi, takes GET and POST methods
    """   
    form = MultiForm(request.form)

    if request.method == 'GET':

        pps_output, ecog_output, kps_output, ppi_output, psppi_output, pap_output, dpap_output = {},{},{},{},{},{},{}
        clinical_guess = ''
        incomplete_models = []
        cg_is_days = False
        
        #print form.validate()
        return render_template('multi.html', form=form, pps_output=pps_output, ecog_output=ecog_output, kps_output=kps_output, ppi_output=ppi_output, psppi_output=psppi_output, pap_output=pap_output, dpap_output=dpap_output, clinical_guess=clinical_guess, error='', incomplete_models=incomplete_models, cg_is_days=cg_is_days)
        
    # POST method gets data from form fields, sends to the functions in multi.py and returns main_function
    elif request.method == 'POST' and validate_models(form):
        #print 'posted and validated'
        pps_output, ecog_output, kps_output, ppi_output, psppi_output, pap_output, dpap_output, clinical_guess, review, incomplete_models, cg_is_days = main_function(form.data) 

        return render_template('results.html', form=form, pps_output=pps_output, ecog_output=ecog_output,  kps_output=kps_output, ppi_output=ppi_output, psppi_output=psppi_output, pap_output=pap_output, dpap_output=dpap_output, clinical_guess=clinical_guess, review=review, error='', incomplete_models=incomplete_models, cg_is_days=cg_is_days)
        
    elif request.method == 'POST' and not validate_models(form): # tried to POST but form didn't validate
        #print 'else'
        #print form.errors 
        pps_output, ecog_output, kps_output, ppi_output, psppi_output, pap_output, dpap_output = {},{},{},{},{},{},{}
        clinical_guess = ''
        incomplete_models = []
        cg_is_days = False
        
        return render_template('multi.html', form=form, pps_output=pps_output, ecog_output=ecog_output, kps_output=kps_output, ppi_output=ppi_output, psppi_output=psppi_output, pap_output=pap_output, dpap_output=dpap_output, clinical_guess=clinical_guess, error=form.errors, incomplete_models=incomplete_models, cg_is_days=cg_is_days)

@app.route('/impendingmodel', methods=['GET','POST'])
def impending_model():

    rec_form = RecursiveForm(request.form)
    
    if request.method == 'POST':
        
        model_prob = recursive_calc(rec_form.data)
        model_prob = str(model_prob) + '%'
        #print "recursive", model_prob
               
        return render_template('impendingmodel.html', rec_form=rec_form, model_prob=model_prob)

    elif request.method == 'GET':
        #print "Recursive GET ok"
        model_prob = ''
        return render_template('impendingmodel.html', rec_form=rec_form, model_prob=model_prob)

@app.route('/impendingprepost', methods=['GET','POST'])
def impending_pp():

    pp_form = PrePostForm(request.form)
    
    if request.method == 'POST' and validate_pp(pp_form):
        pp_prob = pp_calc(pp_form.data)       
        pp_prob = str(pp_prob)
        pp_prob = pp_prob[:4] # cutoff trailing decimals
        return render_template('impendingprepost.html', pp_form=pp_form, pp_prob=pp_prob, error='')
    
    elif request.method == 'POST' and not validate_pp(pp_form):
        pp_prob = ''
        return render_template('impendingprepost.html', pp_form=pp_form, pp_prob=pp_prob, error=pp_form.errors) 
    
    elif request.method == 'GET':
        #print "Recursive GET ok"
        pp_prob = ''
        return render_template('impendingprepost.html', pp_form=pp_form, pp_prob=pp_prob, error='')   
                 
@app.route('/reference', methods=['GET'])
def reference():
    return render_template('reference.html')
    
@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')
    
@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')
    

              



