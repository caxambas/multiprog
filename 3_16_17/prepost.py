from wtforms import Form, SelectField, DecimalField, RadioField, validators, ValidationError

class PrePostForm(Form):
    pretest = DecimalField('Pretest Probability (in percent)')

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


def validate_pp(pp_form):
    # Checks to make sure the input in pretest field is a percent between 0 and 100
    b = 0.0
    t = 100.0
    if b < pp_form.data['pretest'] < t:
        return True
    else:
        #print pp_form.data['pretest']
        pp_form.errors['incorrect pretest input'] = 'Please enter a pretest probability that is a number between 0 and 100'
        #print 'Error'
        return False
        
def pp_calc(form_data):
# Dictionary of LR ratios, key is shortened name, value is a list with first entry is positive LR, second is the negative LR
    LR_dict = {'death_rattle': [9.0, 0.8],'pulseless_radial': [15.6, 0.89],'mandibular': [10.0, 0.8], 'decreased_uop': [15.2, 0.77], 'cheyne_stokes': [12.4, 0.9], 'nr_pupils': [16.7, 0.86], 'decreased_verbal': [8.3, 0.73], 'decreased_visual': [6.7, 0.72], 'eyelids':[13.6, 0.8], 'nasolabial': [8.3, 0.69], 'hyper_neck': [7.3, 0.82], 'grunting': [11.8, 0.82], 'ugib': [10.3, 0.97]}
    
    post_test_prob = 0
    #print 'testing'
    form_list = []
    
    for i in form_data: # Exclude pretest and posttest fields from calculation
        if i != 'pretest' and i != 'posttest':
            form_list.append(i)
    #print "form_list in pp", form_list
    #print 'pretest', form_data['pretest']
    pretest_prob = float(form_data['pretest'])/ 100.0
    pretest_odds = pretest_prob / (1.0 - pretest_prob) # Need odds to apply LR
    
    #print 'pretest_odds', pretest_odds
    # The following calculates a multiplier for the odds ratio, looks in form_list (which contains the LR forms), sees if i.data is present, absent or na and then adjusts it by the appropriate LR via LR_dict
    multiplier = 1.0
    for i in form_list:
        #print 'i.data', i.data
        if form_data[i] == 'present':
            #print LR_dict[i.name][0]
            multiplier *= LR_dict[i][0] #[0] is the + LR
        elif form_data[i] == 'absent':
            multiplier *= LR_dict[i][1] #[1] is the - LR
        else:
            continue
    #print multiplier
    post_odds = pretest_odds * multiplier
    post_prob = post_odds * 100.0 / (1.0 + post_odds) # Gets post probability from odds
    return post_prob
