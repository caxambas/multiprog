from wtforms import Form, SelectField, BooleanField, DecimalField

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
    
def recursive_calc(form_data):
    #print 'form_data', form_data 
    bool_field_list = []
    for i in form_data:
        if i != 'PPS' and i != 'final_score_field':
            bool_field_list.append(i)
    #print bool_field_list

    #This calculates the number of positive late signs in the boolean lists
    num_late_signs = 0
    for i in bool_field_list:
        if form_data[i] == True:
            num_late_signs += 1
    #print num_late_signs
    
    #print 'PPS', form.PPS.data
    #print form.nasolabial_field.data
    #print "Posted successfully"
    PPS = int(form_data['PPS'])
    if PPS <= 20:
        if form_data['nasolabial_field'] == True:
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
                
    return post_test_prob
