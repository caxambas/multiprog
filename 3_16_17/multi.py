from wtforms import Form, SelectField, StringField

"""
Master TODO List:

3/2/17 TODO:

    -Flush out About section *DONE
    -?Add info about each model (basic info on how it is scored, etc...) *LATER

Done:
    -Add Downing paper for PPS *DONE
    -Add Reuben paper for KPS *DONE
    -spell out scores summary table *DONE
    -change median survival to convention: XXX days (95% CI XXX-XXX days) *DONE
    -italicize days/weeks/months and add "of survival" to communicating with families *DONE
    -Change probability to "probability of survival" add survival curve estimate under details *DONE
    -Add disclaimer for nonhealthcare users *DONE
    -?Add logic check for KPS/PPS > 30% difference *DONE
    -?Change links to underlined/blue text, make it open in a new page *DONE
    -?Add link to other calculator if only days left *DONE
        -Will need to spruce up other calculators *DONE     
       
"""

def score_available(reqs, fd):
    """Checks if all fields in model_reqs are given (ie, not empty), returns True if complete"""
    is_model_complete = True
    for i in reqs:
        if fd[i] == 'empty' or fd[i] == '': #added '' for clin_pred_f
            is_model_complete = False
    return is_model_complete
        
def validate_models(form):
    """
    Takes form data and makes sure at least one model is complete.  Returns True if at least one model is complete
    """
    result = True
        
    pps_model_reqs = ['PPS_f'] # should I just make these global?
    ecog_model_reqs = ['ECOG_f']
    kps_model_reqs = ['KPS_f']
    ppi_model_reqs = ['PPS_f', 'Oral_Intake_f', 'Edema_f', 'Dyspnea_f', 'Delirium_f']
    psppi_model_reqs = ['ECOG_f', 'Oral_Intake_f', 'Edema_f', 'Dyspnea_f', 'Delirium_f']
    pap_model_reqs = ['Dyspnea_f', 'Anorexia_f', 'KPS_f', 'Clinical_Prediction_f', 'WBC_f', 'Lymphocyte_f']
    dpap_model_reqs = ['Dyspnea_f', 'Anorexia_f', 'KPS_f', 'Clinical_Prediction_f', 'WBC_f', 'Lymphocyte_f', 'Delirium_f']
    
    # The following checks that at least one score is available
    if not score_available(pps_model_reqs, form.data) and not score_available(ecog_model_reqs, form.data) and not score_available(kps_model_reqs, form.data) and not score_available(ppi_model_reqs, form.data) and not score_available(pap_model_reqs, form.data) and not score_available(dpap_model_reqs, form.data) and not score_available(psppi_model_reqs, form.data):
        form.errors['same_input'] = 'Insufficient Input: Please enter enough inputs to complete at least one model'
        result = False
    #print 'validate result:', result
    #print form.errors
    
    # The following makes sure KPS and PPS are within 30%
    #print 'dif pps kps', abs(int(form.data['PPS_f']) - int(form.data['KPS_f']))
    if form.data['PPS_f'] != 'empty' and form.data['KPS_f'] != 'empty':       
        if abs(int(form.data['PPS_f']) - int(form.data['KPS_f'])) >= 30:
            result = False
            form.errors['pps_kps_dif'] = 'Invalid Input: KPS and PPS differ by 30% or more, please adjust'
    
    #The following makes sure ECOG and KPS are not too different
    if form.data['ECOG_f'] != 'empty' and form.data['KPS_f'] != 'empty':
        """Create grouping and compare to make sure groups are not off by more than 1
        Group   Ecog/KPS 
        (1)     0/100
        (2)     1/80-90
        (3)     2/60-70
        (4)     3/40-50
        (5)     4/10-30"""
        ecog_group = {0:1, 1:2, 2:3, 3:4, 4:5}
        kps_group = {100:1, 90:2, 80:2, 70:3, 60:3, 50:4, 40:4, 30:5, 20:5, 10:5}
        #print ecog_group[int(form.data['ECOG_f'])]
        #print kps_group[int(form.data['KPS_f'])]
        if abs(ecog_group[int(form.data['ECOG_f'])] - kps_group[int(form.data['KPS_f'])]) >=2:
            result = False
            form.errors['ecog_kps_dif'] = "Invalid Input: ECOG and KPS differ too much, see reference"
    
    #The following makes sure ECOG and PPS are not too different
    if form.data['ECOG_f'] != 'empty' and form.data['PPS_f'] != 'empty':
        """Create grouping and compare to make sure groups are not off by more than 1 (see above)"""

        ecog_group = {0:1, 1:2, 2:3, 3:4, 4:5}
        pps_group = {100:1, 90:2, 80:2, 70:3, 60:3, 50:4, 40:4, 30:5, 20:5, 10:5}
        #print ecog_group[int(form.data['ECOG_f'])]
        #print kps_group[int(form.data['PPS_f'])]
        if abs(ecog_group[int(form.data['ECOG_f'])] - pps_group[int(form.data['PPS_f'])]) >=2:
            result = False
            form.errors['ecog_pps_dif'] = "Invalid Input: ECOG and PPS differ too much, see reference"     
    
    #The following validates that a nonnegative number of days was entered into the clinical prediction box
    #print 'cp:', form.data['Clinical_Prediction_f'], len(form.data['Clinical_Prediction_f']), type(form.data['Clinical_Prediction_f'])
    if len(form.data['Clinical_Prediction_f']) != 0: # This sees if the input is blank (if so everything is fine)
        try: # Not blank so see if it is a number
            cp = float(form.data['Clinical_Prediction_f'])
            
        except ValueError: #not a number!
            #print 'valueE'
            result = False
            form.errors['bad_cp_input'] = "Invalid Input: Please enter a nonnegative number for your clinical prediction or leave blank"
        else: # is a number, better not be negative
            if cp < 0: 
                result = False
                form.errors['bad_cp_input'] = "Invalid Input: Please enter a nonnegative number for your clinical prediction or leave blank"
                
    return result 
        
def main_function(form_data):

    """
    Initializes the model objects, runs analyze on each of them, returns the ModelOutput class for the html to render (and does some stuff with clinical prediction
    """
    pps_model_reqs = ['PPS_f']
    ecog_model_reqs = ['ECOG_f']
    kps_model_reqs = ['KPS_f']
    ppi_model_reqs = ['PPS_f', 'Oral_Intake_f', 'Edema_f', 'Dyspnea_f', 'Delirium_f']
    psppi_model_reqs = ['ECOG_f', 'Oral_Intake_f', 'Edema_f', 'Dyspnea_f', 'Delirium_f']
    pap_model_reqs = ['Dyspnea_f', 'Anorexia_f', 'KPS_f', 'Clinical_Prediction_f', 'WBC_f', 'Lymphocyte_f']
    dpap_model_reqs = ['Dyspnea_f', 'Anorexia_f', 'KPS_f', 'Clinical_Prediction_f', 'WBC_f', 'Lymphocyte_f', 'Delirium_f']
    
    
    pps = PPS(form_data, pps_model_reqs)
    ecog = ECOG(form_data, ecog_model_reqs)
    kps = KPS(form_data, kps_model_reqs)
    ppi = PPI(form_data, ppi_model_reqs)
    psppi = PSPPI(form_data, psppi_model_reqs)
    pap = PaP(form_data, pap_model_reqs)
    dpap = DPaP(form_data, dpap_model_reqs)
        
    #Run analyze(), which should create the respective ModelOutput object (each containing a list of Paper Objects) for each respective model
    pps.analyze()
    ecog.analyze()
    kps.analyze()
    ppi.analyze()
    psppi.analyze()
    pap.analyze()
    dpap.analyze()
        
    #print "ecog.output.papers:", ecog.output.papers
    #print ecog.output.papers[0].median

    #Clinical Guess
    #Formats the clinical prediction field input
    clinical_guess = form_data['Clinical_Prediction_f']
    
    if len(clinical_guess) == 0: #if blank ignore
        cg_is_days = False
    else:
        if float(clinical_guess) <= 10: # Check to see if clinical guess includes 'days'
            cg_is_days = True
        else:
            cg_is_days = False
    
     
    review = display_prior_input(form_data)

    #This creates a string of the incomplete models    
    models = [pps, kps, ecog, ppi, psppi, pap, dpap]
    incomplete_models = ''
    for i in models:
        if not i.is_complete:
            incomplete_models = incomplete_models + i.name + ', '
    incomplete_models = incomplete_models[:-2] # remove the last two characters, ie ', '
    #print 'incomplete models:', incomplete_models
    
        
    return pps.output, ecog.output, kps.output, ppi.output, psppi.output, pap.output, dpap.output, clinical_guess, review, incomplete_models, cg_is_days

def display_prior_input(form_data):
    """
    Takes form_data as parameter and checks the choices the user selected, creates a dictionary that is easy for the user to read (not the values because they are sometimes Pap or PPI scores and I don't want to mess with it right now. Can't find a way to access the choice *label* on the field, not the value, which would simplify this greatly.
    """
    choices = {}
    #print form_data
    oi = str(form_data['Oral_Intake_f'])
    if oi == 'empty':
        choices['Oral Intake'] = 'empty'
    elif oi == '0.0':
        choices['Oral Intake'] = 'normal'
    elif oi == '2.5':
        choices['Oral Intake'] = 'reduced but more than mouthfuls'
    elif oi == '4.0':
        choices['Oral Intake'] = 'mouthfuls or less'
    
    e = str(form_data['Edema_f'])
    if e == 'empty':
        choices['Edema'] = 'empty'
    elif e == '0.0':
        choices['Edema'] = 'no'
    elif e == '1.0':
        choices['Edema'] = 'yes'
                   
    a = str(form_data['Anorexia_f'])
    if a == 'empty':
        choices['Anorexia'] = 'empty'
    elif a == '0.0':
        choices['Anorexia'] = 'no'
    elif a == '1.0':
        choices['Anorexia'] = 'yes'
        
    w = str(form_data['WBC_f'])
    if w == 'empty':
        choices['WBC'] = 'empty'
    elif w == '0.0':
        choices['WBC'] = 'normal (4,800-8,500)'
    elif w == '0.5':
        choices['WBC'] = 'high (8,501-11,000)'
    elif w == '1.5':
        choices['WBC'] = 'very High (>11,000)'
    
    l = str(form_data['Lymphocyte_f'])
    if l == 'empty':
        choices['Lymphocyte'] = 'empty'
    elif l == '0.0':
        choices['Lymphocyte'] = 'normal (20.0-40.0%)'
    elif l == '1.0':
        choices['Lymphocyte'] = 'low (12.0-19.9%)'
    elif l == '2.5':
        choices['Lymphocyte'] = 'very Low (0-11.9%)'
        
    choices['Dyspnea'] = str(form_data['Dyspnea_f'])
    choices['PPS'] = str(form_data['PPS_f'])
    choices['KPS'] = str(form_data['KPS_f'])
    choices['ECOG'] = str(form_data['ECOG_f'])
    choices['Delirium'] = str(form_data['Delirium_f'])
       
    # Change empty choices to 'not given'
    for i in choices: 
        if choices[i] == 'empty' or choices[i] == '': #clinical_pred_f empty is ''
            choices[i] = 'not given'
    
    s = ''
    for j in choices:
        #print j, choices[j]
        s += j +': ' + choices[j] + ', '
    
    ss = s[:-2] # strip the last comma and space
            
    return ss
      
class Paper(object):
    """
    This replaces the nested dicts for the output results
    median is a list of median survivals
    prob is a list of probabilistic survivals
    location is a string of the patient cohort location (ie outpatient, inpatient, palliative care inpatient)
    """
    def __init__(self):
        self.median = "" # median string, with CI range
        self.s_median = "" # simplified median, one number only, will be assigned int value
        self.prob = ""
        self.location = ""
        self.group = "" #? Need
        self.cite = ""
            
class ModelOutput(object):
    
    def __init__(self):
        self.score = ""
        self.papers = [] # A list of Paper objects
        self.general_group = [] # Probably can remove this later
        self.communicate = ""
        self.s_median_range = ""
        self.num_papers = 0 # Probably can remove this later?
        self.is_available = True
        self.is_days_survival = False   
        
    def unavailable(self, s): # Maybe should name more specific later?
        """
        Takes s string as output to display for given unavailable string, sets is_available to false
        """
        self.score = s
        self.is_available = False
                             
class PrognosticModel(object):
    """
    This is a Prognostic Model Parent Class   
    """

    def __init__(self, form_data, model_reqs):
        self.output = ModelOutput()
        self.fd = form_data
        self.reqs = model_reqs
        self.is_complete = self.score_available()
                       
    def score_available(self):
        """Checks if all fields in model_reqs are given (ie, not empty), returns True if complete"""
        is_model_complete = True
        for i in self.reqs:
            if self.fd[i] == 'empty' or self.fd[i] == '': #added '' for clinical_pred_f
                is_model_complete = False
        return is_model_complete
    
    def generalizer(self): # Am I using this? remove?
        """
        Takes the Groups that each Paper Obj belongs to and gives the unique values via set().  IE, if all four papers end up being group 'B', self.general_group will just have 'B'
        """
        l = []
        for i in self.output.papers:
            l.append(i.group)
            
        s = set(l)
        self.output.general_group = list(s)
        #print self.output.general_group
    
        
    def s_output_maker(self):
        """
        Looks at a list of s_medians (simplified medians, ints) and does two things: sets self.output.s_median_range to a string and then creates a prediction string for self.output.communicate as well.  If there is only one paper, the range is a single value.
        Current definitions:
        0-10      days
        11-60   weeks
        61 +    months
        """
        l = []
        for i in self.output.papers:
            l.append(i.s_median)
        if len(l) == 1: # Only one paper, hence not really a range
            sole_median = l[0]
            self.output.s_median_range = str(sole_median) + ' days'

            # Now for communicate
            if sole_median <= 10:
                self.output.communicate = 'days'
                self.output.is_days_survival = True
            elif 11 <= sole_median <= 60:
                self.output.communicate = 'weeks'
            elif 61 <= sole_median:
                self.output.communicate = 'months'
                
        else: # More than one paper
            top = max(l)
            bottom = min(l)
            
            #print 'bottom, top: ', bottom, top
            self.output.s_median_range = str(bottom) + ' to ' + str(top) + ' days'
            
            # Now for the communicate
            # First take care of the three easy cases where they all agree
            if top <= 10: # by definition bottom would be less as well
                self.output.communicate = 'days'
                self.output.is_days_survival = True
            elif bottom >= 61: # by def top would be more too
                self.output.communicate = 'months'
            elif 11 <= top <= 60 and 11 <= bottom <= 60:
                self.output.communicate = 'weeks'
            
            # Now for two small spread
            elif bottom <= 10 and 11 <= top <= 60:
                self.output.communicate = 'days to weeks'
                self.output.is_days_survival = True
            elif 11 <= bottom <= 60 and 60 <= top:
                self.output.communicate = 'weeks to months'
                
            # And the one wide spread
            elif bottom <= 10 and top >= 61:
                self.output.communicate = 'days to months'
                self.output.is_days_survival = True
            #print self.output.communicate
        #print 's_prob', self.output.s_prob
        
                                                       
    def pps_scorer(self):
        score = int(self.fd['PPS_f'])
        self.output.score = score
        self.output.s_score = str(self.output.score) + '%' #s_score is an ouput string
    
    def ecog_scorer(self):
        score = int(self.fd['ECOG_f'])
        self.output.score = score
        self.output.s_score = score #s_score is an ouput string
    
    def kps_scorer(self):
        score = int(self.fd['KPS_f'])
        self.output.score = score
        self.output.s_score = str(self.output.score) + '%' #s_score is an ouput string
            
    def ppi_scorer(self):
        """
        Takes dictionary of the data from the form fields as argument.
        Extracts variables as float scores, exception is delirium which has to be parsed a little due to difference btw PPI and D-PaP and PPS which has to be converted from raw percent to PPI pts.
        Returns float of total PPI score
        '_ps' indicates partial score, to keep things consistent
        """
        pps = int(self.fd['PPS_f'])
        # Now convert PPS value to PPI score
        if pps >= 60:
            pps_ps = 0.0
        elif 30 <= pps <= 50:
            pps_ps = 2.5
        elif pps <= 20:
            pps_ps = 4.0
            
        oralintake = float(self.fd['Oral_Intake_f'])
        edema = float(self.fd['Edema_f'])
        
        dyspnea = str(self.fd['Dyspnea_f'])
        if dyspnea == 'present':
            dyspnea_ps = 3.5
        elif dyspnea == 'absent':
            dyspnea_ps = 0.0
            
        delirium = str(self.fd['Delirium_f'])
        if delirium == 'none':
            delirium_ps = 0.0
        elif delirium == 'reversible':
            delirium_ps = 0.0
        elif delirium == 'present':
            delirium_ps = 4.0
            
        ppi_score_total = pps_ps + oralintake + edema + dyspnea_ps + delirium_ps
        #print ppi_score_total
        self.output.score = ppi_score_total
        self.output.s_score = str(self.output.score) + '/15' #s_score is an ouput string        
    
    def psppi_scorer(self):
        """
        Takes dictionary of the data from the form fields as argument.
        Basically does the same as ppi_scorer except it uses ECOG instead of PPS
        """
        e = float(self.fd['ECOG_f'])
        # Now convert ECOG value to PS-PPI score
        if e in [0,1]:
            e_ps = 0.0
        elif e == 2:
            e_ps = 2.5
        elif e in [3,4]:
            e_ps = 4.0
            
        oralintake_ps = float(self.fd['Oral_Intake_f'])
        edema_ps = float(self.fd['Edema_f'])
        
        dyspnea = str(self.fd['Dyspnea_f'])
        if dyspnea == 'present':
            dyspnea_ps = 3.5
        elif dyspnea == 'absent':
            dyspnea_ps = 0.0
            
        delirium = str(self.fd['Delirium_f'])
        if delirium == 'none':
            delirium_ps = 0.0
        elif delirium == 'reversible':
            delirium_ps = 0.0
        elif delirium == 'present':
            delirium_ps = 4.0
        psppi_score_total = e_ps + oralintake_ps + edema_ps + dyspnea_ps + delirium_ps
        #print 'psppi score', psppi_score_total
        self.output.score = psppi_score_total
        self.output.s_score = str(self.output.score) + '/15' #s_score is an ouput string
              
    def pap_scorer(self):
        """
        Takes dictionary of the data from the form fields as argument.
        Extracts variables, alters them to PaP values if shared (like dyspnea or clinical prediction).
        Returns float of score, to be used with the score interpreter
        function
        """
        dyspnea = str(self.fd['Dyspnea_f'])
        if dyspnea == 'present':
            dyspnea_ps = 1.0 
        elif dyspnea == 'absent':
            dyspnea_ps = 0.0
        
        cp_days = float(self.fd['Clinical_Prediction_f'])
        
        cp = cp_days / 7.0 #convert days to weeks
        #print 'cp_d', cp_days, 'cp_wks', cp
        
        #The following open/closed intervals are based on the Maltoni 1999 paper and there is some minor inconsistency in the original paper. For example, it is not clear if the first rank is >= 12 wks or > 12 weeks. It depends on how one demarcates weeks.  In the following intervals 3-4 weeks, for example, would include 4 weeks and 6 days (because the next jump states 5 weeks). 
        if 12 < cp: # 12 weeks or more
            clin_prediction_ps = 0.0
        elif 11.0 <= cp <= 12.0:
            clin_prediction_ps = 2.0
        elif 9.0 <= cp < 11.0:
            clin_prediction_ps = 2.5
        elif 7.0 <= cp < 9.0:
            clin_prediction_ps = 2.5
        elif 5.0 <= cp < 7.0:
            clin_prediction_ps = 4.5
        elif 3.0 <= cp < 5.0:
            clin_prediction_ps = 6.0
        elif 0.0 <= cp < 3:
            clin_prediction_ps = 8.5 
        
        anorexia = float(self.fd['Anorexia_f'])
        kps = int(self.fd['KPS_f']) # Need to translate percent of KPS into the score now
        if kps >= 30:
            kps_score_ps = 0.0
        elif kps <= 20:
            kps_score_ps = 2.5    
        
        wbc = float(self.fd['WBC_f'])
        lymph = float(self.fd['Lymphocyte_f'])
        total = dyspnea_ps + anorexia + kps_score_ps + clin_prediction_ps + wbc + lymph
        self.output.score = total
        self.output.s_score = str(self.output.score) + '/17.5' #s_score is an ouput string
        return total # THis function has to return total because dpap_scorer uses it
    
    def dpap_scorer(self):
        """
        Takes form_data (to get delirium) and takes total PaP score
        Adds delirium score value and returns D-PaP total score
        Bear in mind D-PaP does not allow the exception for delirium
        caused by a single medication.
        """
        delirium = str(self.fd['Delirium_f'])
        if delirium == 'none':
            delirium_ps = 0.0
        elif delirium == 'reversible':
            delirium_ps = 2.0
        elif delirium == 'present':
            delirium_ps = 2.0
        
        pap_score = self.pap_scorer()
        self.output.score = pap_score + delirium_ps
        self.output.s_score = str(self.output.score) + '/19.5' #s_score is an ouput string
    
class PPS(PrognosticModel):
    """
    PPS class, child of PrognosticModel
    """
    
    def analyze(self):  
        """
        This function checks to make sure is_complete is True, and then runs score and available interpretation functions (in this case named after Jang_2014 paper).  If is_complete is False then score is set to 'unavailable
        """
        self.name = 'PPS'
        
        if self.is_complete:
            self.output.s_prob = 'Not reported'
            self.pps_scorer() 
            self.Pps_Jang_2014()
            self.Downing_2007()
            
            self.s_output_maker()
            
        else:
            self.output.unavailable('Insufficient data to calculate PPS')
            #self.output.score = 'Insufficient data to calculate PPS'
               
    def Downing_2007(self):
        c = Paper()
        c.location = 'mixed'
        c.cite = 'Downing, 2007'
        c.notes = "Meta-analysis of PPS studies, 1808 pts, mix of cancer and non-cancer"
        if self.output.score == 10:
            c.median = "2 days (95% CI 2-2 days)"
            c.s_median = 2
        elif self.output.score == 20:
            c.median = "4 days (95% CI 3-5 days)"
            c.s_median = 4
        elif self.output.score == 30:
            c.median = "13 days (95% CI 12-14 days)"
            c.s_median = 13
        elif self.output.score == 40:
            c.median = "24 days (95% CI 21-27 days)"
            c.s_median = 24
        elif self.output.score == 50:
            c.median = "37 days (95% CI 32-42 days)"
            c.s_median = 37
        elif self.output.score == 60:
            c.median = "48 days (95% CI 17-79 days)"
            c.s_median = 48 
        elif self.output.score == 70:
            c.median = "78 days (95% CI 25-131 days)"
            c.s_median = 78
        elif self.output.score >= 80:  
            c.median = "Not reported for PPS 80-100%, but 70% median survival was 78 days so more than 78 days is assumed"
            c.s_median = "not reported" # Note I am giving a string here instead of int!
        self.output.papers.append(c)    
                    
    def Pps_Jang_2014(self):
        c = Paper()
        c.location = 'palliative care clinic' 
        c.cite = 'Jang, 2014'
        c.notes = "All advanced cancer, one third still receiving active treatment, 1655 pts, few pts with poor performance status"
        #c.is_original = True 
        if self.output.score >= 80:
            c.median = "221 days (95% CI 197-244 days)"
            c.group = 'A'
            c.s_median = 221
        elif 60 <= self.output.score <=70:
            c.median = "115 days (95% CI 105-131 days)"
            c.group = 'A'
            c.s_median = 115
        elif 40 <= self.output.score <=50:
            c.median = "51 days (95% CI 44-60 days)"
            c.group = 'B'
            c.s_median = 51
        elif self.output.score <=30: 
            c.median = "22 days (95% CI 12-102 days)"
            c.group = 'C'
            c.s_median = 22
        self.output.papers.append(c)        

class PSPPI(PrognosticModel):
    def analyze(self):
        """
        """
        self.name = 'PS-PPI'
        if self.is_complete:
            self.psppi_scorer()
            self.Yamada_2016()
            self.s_output_maker()
            
        else:
            self.output.unavailable('Insufficient data to calculate PS-PPI')
        
    def Yamada_2016(self):
        c = Paper()
        c.location = 'inpatient with palliative consult'
        
        d = Paper()
        d.location = 'palliative care unit'
        
        e = Paper()
        e.location = 'home palliative care'
        c.cite, d.cite, e.cite = 'Yamada, 2016', 'Yamada, 2016', 'Yamada, 2016'  
        
        c.notes = 'All advanced cancer, ~40% on chemotherapy, 906 pts, median survival approximated from figures'
        d.notes = 'All advanced cancer, 8.5% on chemotherapy, 892 pts, median survival approximated from figures'
        e.notes = 'All advanced cancer, 14% on chemotherapy, 548 pts, median survival approximated from figures'
        
        # Probabilities
        if 6.0 <= self.output.score:
            self.output.s_prob = 'At 21 days: 53.2%' # Just giving PPV for now, full quote as follows in case I change it again: 'At 21 days: Sens 81%, Spec 61.3%, PPV 53.2%, NPV 85.6%'
            c.prob = 'At 21 days: Sens 79.4%, Spec 68.2%, PPV 50.4%, NPV 71.1%'
            d.prob = 'At 21 days: Sens 85.0%, Spec 51.8%, PPV 58.3%, NPV 81.4%'
            e.prob = 'At 21 days: Sens 74.0%, Spec 63.6%, PPV 47.5%, NPV 84.6%'
            
        if 4.0 <= self.output.score < 6.0:
            self.output.s_prob = 'At 42 days: 66.8%' #'At 42 days: Sens 92.5%, Spec 40.3%, PPV 66.8%, NPV 80.6%'
            c.prob = 'At 42 days: Sens 76.7%, Spec 86.4%, PPV 83.5%, NPV 80.5%'
            d.prob = 'At 42 days: Sens 94.2%, Spec 24.7%, PPV 72.4%, NPV 67.0%'
            e.prob = 'At 42 days: Sens 92.8%, Spec 32.7%, PPV 60.9%, NPV 80.0%'
        
        if self.output.score <= 3.5: #??? By cutoff I assume they mean 3.5 or less? pending email This is in Table 8, applies to all patients so I am not giving values based on the location specific papers
            self.output.s_prob = 'At 90 days: 64.0%' #'At 90 days: Sens 91.2%, Spec 40.6%, PPV 64.0%, NPV 79.9%'
            c.prob = 'At 90 days: Sens 91.2%, Spec 40.6%, PPV 64.0%, NPV 79.9% (*all pooled pts)'
            d.prob = 'At 90 days: Sens 91.2%, Spec 40.6%, PPV 64.0%, NPV 79.9% (*all pooled pts)'
            e.prob = 'At 90 days: Sens 91.2%, Spec 40.6%, PPV 64.0%, NPV 79.9% (*all pooled pts)'
            
        # Median Survivals
        if self.output.score <= 2.0: # Group A
            c.median = '~100 days'
            c.s_median = 100
                        
            d.median = '~50 days'
            d.s_median = 50
            d.group = 'A'
            
            e.median = '~70 days'
            e.s_median = 70
            e.group = 'A'
            
        if 2.0 < self.output.score <= 4.0: # Group B
            c.median = '~35 days'
            c.s_median = 35
            c.group = 'B'
            
            d.median = '~25 days'
            d.group = 'B'
            d.s_median = 25
            
            e.median = '~35 days'
            e.group = 'B'
            e.s_median = 35
            
        if 4.0 < self.output.score: # Group C
            c.median = '~15 days'
            c.group = 'C'
            c.s_median = 15
            
            d.median = '~15 days'
            d.group = 'C'
            d.s_median = 15
            
            e.median = '~20 days'
            e.group = 'C'
            e.s_median = 20
        
        self.output.papers.extend((c,d,e))
        
class PPI(PrognosticModel):

    def analyze(self):  
        """
        This function checks to make sure is_complete is True, and then runs score and available interpretation functions.
        """
        
        self.name = 'PPI'
        if self.is_complete:
            self.ppi_scorer()
            self.Morita_1999()
            self.Ppi_Baba_2015()
            
            self.s_output_maker()

        else:
            self.output.unavailable('Insufficient data to calculate PPI')

        
    def Ppi_Baba_2015(self):
        # Will have to treat each location cohort as a separate Paper object
        c = Paper()
        c.location = 'inpatient with palliative care consult'
        d = Paper()
        d.location = 'palliative care unit'
        e = Paper()
        e.location = 'home palliative care'

        c.cite, d.cite, e.cite = 'Baba, 2015', 'Baba, 2015', 'Baba, 2015'
        c.notes = 'All metastatic cancer, no chemotherapy, 554 pts, median survival approximated from figures'
        d.notes = 'All metastatic cancer, no chemotherapy, 820 pts, median survival approximated from figures'
        e.notes = 'All metastatic cancer, no chemotherapy, 472 pts, median survival approximated from figures'
        
        # Probabilities
        if 6.0 <= self.output.score:
            c.prob = '21 days or less: Sens 69.1%, Spec 80.4%, PPV 64.7%, NPV 83.4%'
            d.prob = '21 days or less: Sens 65.8%, Spec 71.5%, PPV 64.6%, NPV 72.6%'
            e.prob = '21 days or less: Sens 50.0%, Spec 84.1%, PPV 57.7%, NPV 79.5%'
            
        if 4.0 <= self.output.score < 6.0: #??? Note that Baba didn't give any data for this, unlike Morita
            c.prob = 'Not reported'
            d.prob = 'Not reported'
            e.prob = 'Not reported'
            
        if self.output.score < 4.0: 
            c.prob = '42 days or more: Sens 72.5%, Spec 76.6%, PPV 72.8%, NPV 76.4%'
            d.prob = '42 days or more: Sens 61.4%, Spec 77.4%, PPV 56.4%, NPV 80.7%'
            e.prob = '42 days or more: Sens 71.9%, Spec 67.1%, PPV 65.3%, NPV 73.5%'
            
        # Median Survivals
        # Reconciled with Dr. Hui's numbers
        if self.output.score <= 2.0: # Group A
            c.median = '~130 days'
            c.s_median = 135
            c.group = 'A'
            
            d.median = '~55 days'
            d.s_median = 55
            d.group = 'A'
            
            e.median = '~85 days'
            e.s_median = 85
            e.group = 'A'
            
        if 2.0 < self.output.score <= 4.0: # Group B
            c.median = '~55 days'
            c.s_median = 55
            c.group = 'B'
            
            d.median = '~47 days'
            d.group = 'B'
            d.s_median = 47
            
            e.median = '~52 days'
            e.group = 'B'
            e.s_median = 52
            
        if 4.0 < self.output.score: # Group C
            c.median = '~18 days'
            c.group = 'C'
            c.s_median = 18
            
            d.median = '~12 days'
            d.group = 'C'
            d.s_median = 12
            
            e.median = '~25 days'
            e.group = 'C'
            e.s_median = 25
        
        self.output.papers.extend((c,d,e))
        
    def Morita_1999(self):
        c = Paper()
        c.location = 'palliative care unit'
        c.cite = 'Morita, 1999'
        c.notes = "All cancer, admitted to inpatient hospice, 350 pts in training cohort, 95 in validation cohort."
        #c.is_original = True
        if self.output.score <= 2.0:
            c.median = "134 days (95% CI 123-145 days)"
            c.group = 'A'
            c.s_median = 134
        if 2.0 < self.output.score <= 4.0:
            c.median = "89 days (95% CI 82-96 days)" 
            c.group = 'B'
            c.s_median = 89
        if self.output.score > 4.0:
            c.median = "23 days (95% CI 20-26 days)"
            c.group = 'C'
            c.s_median = 23

        #Now the PPI probabilities 
        if 6.0 <= self.output.score:
            c.prob = "21 days or less: Sens 83%, Spec 85%, PPV 80%, NPV 87%"
            self.output.s_prob = "21 days or less: 80%" #Sens 83%, Spec 85%, PPV 80%, NPV 87%"
        if 4.0 <= self.output.score < 6.0:
            c.prob = "42 days or less: Sens 79%, Spec 77%, PPV 83%, NPV 71%" 
            self.output.s_prob = "42 days or less: 83%" #Sens 79%, Spec 77%, PPV 83%, NPV 71%"

        if self.output.score < 4.0:
            c.prob = 'More than 42 days: Sens 77%, Spec 79%, PPV 71%, NPV 83%' #??? Inverted
            self.output.s_prob = 'More than 42 days: 71%' # Sens 77%, Spec 79%, PPV 71%, NPV 83%'
                   
        self.output.papers.append(c) # May need to replace this back with append
  
class PaP(PrognosticModel):

    def analyze(self):
        """
        This function checks to make sure is_complete is True, and then runs score and available interpretation functions.
        """
        self.name = 'PaP'
        if self.is_complete:
            self.pap_scorer()
            self.Maltoni_1999()
            self.Pap_Baba_2015()
            
            self.s_output_maker()
        else:
            self.output.unavailable('Insufficient data to calculate PaP')

           
    def Maltoni_1999(self):
        c = Paper()
        c.location = 'mix of outpatient and inpatient hospice' 
        c.cite = 'Maltoni, 1999'
        c.notes = "Advanced solid cancers only, enrolled in hospice, 451 pts in validation cohort."
        #c.is_original = True
        
        if self.output.score <= 5.5:
            c.prob = "30 days or more: 86.6%"
            self.output.s_prob = "30 days or more: 86.6%"
            c.median = "76 days (95% CI 67-87 days)"
            c.group = 'A'
            c.s_median = 76
        elif 5.6 <= self.output.score <= 11.0:
            c.prob = "30 days or more: 51.6%"
            self.output.s_prob = "30 days or more: 51.6%"
            c.median = "32 days (95% CI 28-39 days)"
            c.group = 'B'
            c.s_median = 32
        elif self.output.score >= 11.1:
            c.prob = "30 days or more: 16.9%"
            self.output.s_prob = "30 days or more: 16.9%"
            c.median = "14 days (95% CI 11-18 days)"
            c.group = 'C'
            c.s_median = 14
        
        self.output.papers.append(c)

    def Pap_Baba_2015(self):
        #First probabilistic studies, add median later when I have the data
        # Will have to treat each location cohort as a separate Paper object
        c = Paper()
        c.location = 'inpatient with palliative care consult'
        d = Paper()
        d.location = 'palliative care unit'
        e = Paper()
        e.location = 'home palliative care'

        c.cite, d.cite, e.cite = 'Baba, 2015', 'Baba, 2015', 'Baba, 2015'
        c.notes = 'All metastatic cancer, no chemotherapy, 554 pts, median survival approximated from figures'
        d.notes = 'All metastatic cancer, no chemotherapy, 820 pts, median survival approximated from figures'
        e.notes = 'All metastatic cancer, no chemotherapy, 472 pts, median survival approximated from figures'
        
        # First do probabilistic
        # PaP Baba cutoffs also inclusive or exclusive? *inclusive
            # They refer to Pirovani paper, which uses different probabilities, and uses hard upper bounds for group A [0-5.5], group B: [5.6 - 11.0], group C: [11.1-15.0]
            # However, Baba only gives two groups (short and long)
        
        if 9.0 < self.output.score: #short survival
            c.prob = '21 days or less: Sens 80.4%, Spec 81.6%, PPV 70.6%, NPV 88.3%'
            d.prob = '21 days or less: Sens 79.2%, Spec 69.0%, PPV 66.8%, NPV 80.8%'
            e.prob = '21 days or less: Sens 74.1%, Spec 70.6%, PPV 55.1%, NPV 84.8%'
        
        if 5.5 < self.output.score <= 9.0: #Solved???, will leave undefined
            c.prob = 'Not reported'
            d.prob = 'Not reported'
            e.prob = 'Not reported'
               
        if self.output.score <= 5.5:
            c.prob = '30 days or more: Sens 61.9%, Spec 91.6%, PPV 89.9%, NPV 66.5%'
            d.prob = '30 days or more: Sens 42.8%, Spec 95.4%, PPV 88.3%, NPV 67.4%'
            e.prob = '30 days or more: Sens 53.6%, Spec 90.0%, PPV 86.7%, NPV 61.5%'
            
        # Median Survivals
        if self.output.score <= 5.5: # Group A
            c.median = '~105 days'
            c.group = 'A'
            c.s_median = 105
            
            d.median = '~75 days'
            d.group = 'A'
            d.s_median = 75
            
            e.median = '~90 days'
            e.group = 'A'
            e.s_median = 90
            
        if 5.5 < self.output.score <= 11.0: # Group B
            c.median = '~35 days'
            c.group = 'B'
            c.s_median = 35
            
            d.median = '~25 days'
            d.group = 'B'
            d.s_median = 25
            
            e.median = '~28 days'
            e.group = 'B'
            e.s_median = 28
            
        if 11.0 < self.output.score: # Group C
            c.median = '~7 days'
            c.group = 'C'
            c.s_median = 7
            
            d.median = '~5 days'
            d.group = 'C'
            d.s_median = 5
            
            e.median = '~8 days'
            e.group = 'C'
            e.s_median = 8
        
        self.output.papers.extend((c,d,e))
        
class DPaP(PrognosticModel):
    
    def analyze(self):
        """
        This function checks to make sure is_complete is True, and then runs score and available interpretation functions.
        """
        self.name = 'D-PaP'
        if self.is_complete:
            self.dpap_scorer()
            self.Scarpi_2011()
            self.Dpap_Baba_2015()
            
            self.s_output_maker()
            
        else:
            self.output.unavailable('Insufficient data to calculate D-PaP')


    def Scarpi_2011(self):
        c = Paper()
        c.location = 'mix of outpatient and inpatient hospice' 
        c.cite = 'Scarpi, 2011'
        c.notes = "All advanced solid cancers only, enrolled in hospice, retrospective 362 pts."
        #c.is_original = True
        if self.output.score <= 7.0:
            c.prob = "30 days or more: 83% (95% CI 77-90%)"
            self.output.s_prob = "30 days or more: 83%"
            c.median = "73 days (95% CI 59-83 days)"
            c.group = 'A'
            c.s_median = 73
            
        elif 7.1 <= self.output.score <= 12.5:
            c.prob = "30 days or more: 50% (95% CI 42-58%)"
            self.output.s_prob = "30 days or more: 50%"
            c.median = "30 days (95% CI 25-39 days)"
            c.group = 'B'
            c.s_median = 30
            
        elif self.output.score >= 12.6:
            c.prob = "30 days or more: 9% (95% CI 3-15%)"
            self.output.s_prob = "30 days or more: 9%"
            c.median = "11 days (95% CI 8-17 days)"
            c.group = 'C'
            c.s_median = 11
            
        self.output.papers.append(c)
    
    def Dpap_Baba_2015(self):
        #First probabilistic studies, add median later when I have the data
        # Will have to treat each location cohort as a separate Paper object
        c = Paper()
        c.location = 'inpatient with palliative consult'
        d = Paper()
        d.location = 'palliative care unit'
        e = Paper()
        e.location = 'home palliative care'

        c.cite, d.cite, e.cite = 'Baba, 2015', 'Baba, 2015', 'Baba, 2015'
        c.notes = 'All metastatic cancer, no chemotherapy, 554 pts, median survival approximated from figures'
        d.notes = 'All metastatic cancer, no chemotherapy, 820 pts, median survival approximated from figures'
        e.notes = 'All metastatic cancer, no chemotherapy, 472 pts, median survival approximated from figures'
        
        # First do probabilistic
        # See discussion under PaP_Baba probabilities
        
        if self.output.score > 9.0: #short survival
            c.prob = '21 days or less: Sens 82.3%, Spec 78.8%, PPV 68.1%, NPV 89.0%'
            d.prob = '21 days or less: Sens 84.0%, Spec 66.2%, PPV 66.1%, NPV 84.1%'
            e.prob = '21 days or less: Sens 81.0%, Spec 68.6%, PPV 56.0%, NPV 88.0%'
        
        if 7.0 < self.output.score <= 9.0: 
            c.prob = 'Not reported' #??? What to do about this? Maybe: 'Not reported' ?
            d.prob = 'Not reported'
            e.prob = 'Not reported'
            
        if self.output.score <= 7.0: #long survival
            c.prob = '30 days or more: Sens 71.3%, Spec 87.1%, PPV 87.0%, NPV 71.5%'
            d.prob = '30 days or more: Sens 59.0%, Spec 89.8%, PPV 82.3%, NPV 73.0%'
            e.prob = '30 days or more: Sens 62.5%, Spec 83.8%, PPV 82.2%, NPV 65.0%'

        # Median Survivals
        if self.output.score <= 7.0: # Group A
            c.median = '~85 days'
            c.group = 'A'
            c.s_median = 85
            
            d.median = '~65 days'
            d.group = 'A'
            d.s_median = 65
            
            e.median = '~85 days'
            e.group = 'A'
            e.s_median = 85
            
        if 7.0 < self.output.score <= 12.5: # Group B
            c.median = '~25 days'
            c.group = 'B'
            c.s_median = 25
            
            d.median = '~23 days'
            d.group = 'B'
            d.s_median = 23
             
            e.median = '~27 days'
            e.group = 'B'
            e.s_median = 27
            
        if 12.5 < self.output.score: # Group C
            c.median = '~7 days'
            c.group = 'C'
            c.s_median = 7
            
            d.median = '~7 days'
            d.group = 'C'
            d.s_median = 7
            
            e.median = '~11 days' #??? May wish to remeasure this one
            e.group = 'C'
            e.s_median = 11 # Would be borderline if days 10 vs 14???
        
        self.output.papers.extend((c,d,e))

class ECOG(PrognosticModel):
    
    def analyze(self):
        """
        This function checks to make sure is_complete is True, and then runs score and available interpretation functions.
        """
        self.name = 'ECOG'
        if self.is_complete:
            self.output.s_prob = 'Not reported'
            self.ecog_scorer()
            self.Ecog_Jang_2014()
            
            self.s_output_maker()
        else:
            self.output.unavailable('Insufficient data to calculate ECOG')  

    
    def Ecog_Jang_2014(self):
        #print 'self.output.score', self.output.score
        c = Paper()
        c.location = 'palliative care clinic'
        c.cite = 'Jang, 2014'
        c.notes = "All advanced cancer, one third still receiving active treatment, 1655 pts, few pts with poor performance status"
        if self.output.score == 0:
            c.median = "293 days (95% CI 242-403 days)"
            c.group = 'A'
            c.s_median = 293
            
        elif self.output.score == 1:
            c.median = "197 days (95% CI 183-219 days)"
            c.group = 'A'
            c.s_median = 197
        elif self.output.score == 2:
            c.median = "104 days (95% CI 90-118 days)"
            c.group = 'A'
            c.s_median = 104
        elif self.output.score == 3:
            c.median = "55 days (95% CI 46-66 days)"
            c.group = 'B'
            c.s_median = 55
        elif self.output.score == 4:
            c.median = "25.5 days (95% CI 17-51 days)"
            c.group = 'C'
            c.s_median = 25.5

        self.output.papers.append(c)
            
class KPS(PrognosticModel):
    
    def analyze(self):
        """
        This function checks to make sure is_complete is True, and then runs score and available interpretation functions.
        """
        self.name = 'KPS'
        if self.is_complete:
            self.output.s_prob = 'Not reported'
            self.kps_scorer()
            self.Kps_Jang_2014()
            self.Reuben_1988()
            
            self.s_output_maker()
        else:
            self.output.unavailable('Insufficient data to calculate KPS')
    
    def Reuben_1988(self):
        c = Paper()
        c.location = 'mixed'
        c.cite = 'Reuben, 1988'
        c.notes = 'All advanced cancer, 1592 pts, grouped patients by KPS 10-20%, 30-40% and 50% or more'
        
        if 10 <= self.output.score <=20:
            c.median = "16.8 days"
            c.s_median = 16.8
        elif 30 <= self.output.score <= 40:
            c.median = "49.8 days"
            c.s_median = 49.8
        elif 50 <= self.output.score:
            c.median = "86.1 days"
            c.s_median = 86.1
        self.output.papers.append(c)
        
    def Kps_Jang_2014(self):
        c = Paper()
        c.location = 'palliative care clinic'
        c.cite = 'Jang, 2014'
        c.notes = "All advanced cancer, one third still receiving active treatment, 1655 pts, few pts with poor performance status"
        #c.is_original = True
        
        if 80 <= self.output.score <= 100:
            c.median = "215 days (95% CI 190-241 days)"
            c.group = 'A'
            c.s_median = 215
        elif 60 <= self.output.score <= 70:
            c.median = "119 days (95% CI 106-132 days)"
            c.group = 'A'
            c.s_median = 119
        elif 40 <= self.output.score <= 50:
            c.median = "49 days (95% CI 43-59 days)"
            c.group = 'B'
            c.s_median = 49
        elif self.output.score <= 30:
            c.median = "29 days (95% CI 22-144 days)"
            c.group = 'C'
            c.s_median = 29
        self.output.papers.append(c)          

    
              
# This is the class for the wtforms           
class MultiForm(Form):
        
    ECOG_f = SelectField('ECOG: ', choices=(('empty', 'Unavailable'), (0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4')))
    PPS_f = SelectField('PPS: ', choices=(('empty', 'Unavailable'), (100, '100%'),(90, '90%'), (80, '80%'), (70, '70%'), (60, '60%'), (50, '50%'), (40, '40%'), (30, '30%'), (20, '20%'), (10, '10%'))) # Values are numbers, will need to correlate to points for the PPI and PPS models
    Oral_Intake_f = SelectField('Oral Intake: ', choices=(('empty', 'Unavailable'),(0.0, 'Normal'), (2.5, 'Reduced but more than mouthfuls'), (4.0, 'Mouthfuls or less')))
    Edema_f = SelectField('Edema: ', choices=(('empty', 'Unavailable'), (0.0, 'No'), (1.0, 'Yes'))) # Values are pts in PPI
    Dyspnea_f = SelectField('Dyspnea at rest:', choices=(('empty', 'Unavailable'), ('absent', 'No'), ('present', 'Yes'))) # For PaP, dyspnea + if present during time of assessment, for PPI if dyspnea at rest.  Added note
    Delirium_f = SelectField('Delirium:', choices=(('empty', 'Unavailable'), ('none', 'No'), ('reversible', 'Yes, but solely from one medication'), ('present', 'Yes, and not from one medication'))) # For PPI Delirium was absent if caused by one med and potentially reversible, for D-Pap it was positive if CAM positive. Added note

    """PaP and D-PaP Fields, not already covered by PPI"""
    Anorexia_f = SelectField('Anorexia:', choices=(('empty', 'Unavailable'), ('0.0', 'No'), (1.0, 'Yes'))) # Defined as the symptom (ie, lack of appetite).
    KPS_f = SelectField('Karnofsky Performance Status: ', choices=(('empty', 'Unavailable'), (100, '100%'), (90, '90%'), (80, '80%'), (70, '70%'), (60, '60%'), (50, '50%'), (40, '40%'), (30, '30%'), (20, '20%'), (10, '10%'))) 
    WBC_f = SelectField('Total WBC (cell/cc): ', choices=(('empty', 'Unavailable'), (0.0, 'Normal (4,800-8,500)'), (0.5, 'High (8,501-11,000)'), (1.5, 'Very High (>11,000)'))) # The values are the pts in PaP/D-PaP, what did they do with low WBCs?
    Lymphocyte_f = SelectField('Lymphocyte Percentage: ', choices=[('empty', 'Unavailable'), (0.0, 'Normal (20.0-40.0%)'), (1.0, 'Low (12.0-19.9%)'), (2.5, 'Very Low (0-11.9%)')]) # The values are the pts in PaP/D-PaP, what to do with very high lymphs?
    
    Clinical_Prediction_f = StringField("Clinician's prediction of survival: ") 

   
       

