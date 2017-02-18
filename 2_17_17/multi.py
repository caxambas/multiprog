from wtforms import Form, SelectField, validators, ValidationError

"""
Master TODO List:

2/17/17:
TODO:

-Does Maltoni have a CI for median survival data?
-Probabilities multiple issues (see separate doc)
-Add disclaimer at bottom?
-change review input
-Add nav bar at bottom?
-Add caveat note regarding Baba estimations?
-Clean up "insufficient input for models...", make it one line
-place code on github
-Style
    -Better title?   
    -Make text similar in all outputs *DONE
    -determine which kind of license (MIT open license?) in footer*DONE
    -add link to github source
-figure out hosting

Pending discussion:
-Wait to hear about validation for PPS/KPS/ECOG

DONE:
-Clean up my approx Baba median survival dates, make it similar to Dr. Hui *DONE, only one caveat
-Add caveat for WBC/lymph in Maltoni/Scarpi papers (up front) *DONE
-Add sources at the bottom of results.html *DONE
-Add PS-PPI
    -add req text to first page inputs *DONE
    -create scoring method *DONE
    -create model class *DONE
    -create paper class *DONE
    -add displaying html to POST method and results.html *DONE
-Make the form validate so user has to enter something (at least one model) *DONE
-Add notes to the studies (# pts, % cancer, any caveats like solid tumors only)*DONE
-make a function that creates range of s_median (going to be under ModelOutput class) *DONE
-rework the "days to weeks" etc... function *DONE
-rework communicating with families() to work with median range *DONE
-Make clinical prediction only show up if given *DONE
-add simplified median survival outputs to papers *DONE
-Update delirium input *DONE
-Remove setting input *DONE
-Change clinical guess output to days/weeks/months *DONE
-Make insufficient models clump at bottem so display is nicer in details *DONE

OLD TODO:
Secondary:
-Consider adding a graphical output showing median survival time between models/studies
-Adding a warning if the ECOG, PPS, or KPS are significantly different
-Find a paper for probabilistic survival with PPS, ECOG, KPS (exists?)

Finished:
-Need to work on output display (general first, have each one available say days/weeks/months)*DONE
-Changing .group to be part of ModelOutput since it remains the same in each paper (unless I want to do some hard cutoffs and change things around like with the Morita paper). *DONE
-fix *_prior_input()'s display so it is more compact *DONE
-Add PPS (and KPS, ECOG too from Jang paper) *DONE
-Will need to create a separate output page because the output is going to be too big, initially will add input values for debugging *DONE
-Maybe change output strings from nested dictionary to a class *DONE
-Need to add link for PPS, KPS, ECOG tables for reference *DONE
-Add Baba paper probabilistic data *DONE
-Derive Baba median survival data if I don't hear from them manually *DONE
-make Paper.cite display citations correctly to limit string length *DONE
-Clarify PPS instructions (define self-care, how exactly do you change deciles and err) *DONE

"""

def score_available(reqs, fd):
    """Checks if all fields in model_reqs are given (ie, not empty), returns True if complete"""
    is_model_complete = True
    for i in reqs:
        if fd[i] == 'empty':
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
    
    if not score_available(pps_model_reqs, form.data) and not score_available(ecog_model_reqs, form.data) and not score_available(kps_model_reqs, form.data) and not score_available(ppi_model_reqs, form.data) and not score_available(pap_model_reqs, form.data) and not score_available(dpap_model_reqs, form.data) and not score_available(psppi_model_reqs, form.data):
        form.errors['same_input'] = 'Please select enough inputs to complete at least one model.'
        result = False
    #print 'validate result:', result
    print form.errors
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
    if form_data['Clinical_Prediction_f'] == 'empty':
        clinical_guess = ""
    else:
        cg = form_data['Clinical_Prediction_f'] 
        if cg in ['>12', '11-12', '9-10']:
            clinical_guess = cg + ' weeks' + ' (ie months)'
        elif cg == '1-2':
            clinical_guess = cg + ' weeks' + ' (ie days to weeks)' # Note this may change if days 10 vs 14
        else:
            clinical_guess = cg + ' weeks' + ' (ie weeks)'
    
    #print pps.output
    #print ppi.output        
    review = display_prior_input(form_data)
    #print review
    #print 'pps papers in main():', pps.output.papers
    #print 'num_papers for pps in main()', pps.output.num_papers
    #print ppi.output.num_papers
    
    models = [pps, kps, ecog, ppi, psppi, pap, dpap]
    incomplete_models = ''
    for i in models:
        if not i.is_complete:
            incomplete_models = incomplete_models + i.name + ', '
    incomplete_models = incomplete_models[:-2] # remove the last two characters, ie ', '
    print 'incomplete models:', incomplete_models
    
    
    return pps.output, ecog.output, kps.output, ppi.output, psppi.output, pap.output, dpap.output, clinical_guess, review, incomplete_models

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
        choices['Oral Intake'] = 'Normal'
    elif oi == '2.5':
        choices['Oral Intake'] = 'Reduced but more than mouthfuls'
    elif oi == '4.0':
        choices['Oral Intake'] = 'Mouthfuls or less'
    
    e = str(form_data['Edema_f'])
    if e == 'empty':
        choices['Edema'] = 'empty'
    elif e == '0.0':
        choices['Edema'] = 'No'
    elif e == '1.0':
        choices['Edema'] = 'Yes'
                   
    a = str(form_data['Anorexia_f'])
    if a == 'empty':
        choices['Anorexia'] = 'empty'
    elif a == '0.0':
        choices['Anorexia'] = 'No'
    elif a == '1.0':
        choices['Anorexia'] = 'Yes'
        
    w = str(form_data['WBC_f'])
    if w == 'empty':
        choices['WBC'] = 'empty'
    elif w == '0.0':
        choices['WBC'] = 'Normal (4,800-8,500)'
    elif w == '0.5':
        choices['WBC'] = 'High (8,501-11,000)'
    elif w == '1.5':
        choices['WBC'] = 'Very High (>11,000)'
    
    l = str(form_data['Lymphocyte_f'])
    if l == 'empty':
        choices['Lymphocyte'] = 'empty'
    elif l == '0.0':
        choices['Lymphocyte'] = 'Normal (20.0-40.0%)'
    elif l == '1.0':
        choices['Lymphocyte'] = 'Low (12.0-19.9%)'
    elif l == '2.5':
        choices['Lymphocyte'] = 'Very Low (0-11.9%)'
        
    choices['Dyspnea'] = str(form_data['Dyspnea_f'])
    choices['PPS'] = str(form_data['PPS_f'])
    choices['KPS'] = str(form_data['KPS_f'])
    choices['ECOG'] = str(form_data['ECOG_f'])
    choices['Delirium'] = str(form_data['Delirium_f'])
    choices['Clinical Prediction'] = str(form_data['Clinical_Prediction_f'])
    
    for i in choices: # Change the term empty to '-' to make it easier to read
        if choices[i] == 'empty':
            choices[i] = '-'
            
    return choices
      
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
            if self.fd[i] == 'empty':
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
        10      days
        11-60   weeks
        61 +    months
        """
        l = []
        for i in self.output.papers:
            l.append(i.s_median)
        if len(l) == 1: # Only one paper, hence not really a range
            sole_median = l[0]
            self.output.s_median_range = str(sole_median) + ' days.'
            
            # Now for communicate
            if sole_median <= 10:
                self.output.communicate = 'Predicts days.'
            elif 11 <= sole_median <= 60:
                self.output.communicate = 'Predicts weeks.'
            elif 61 <= sole_median:
                self.output.communicate = 'Predicts months.'
        else: # More than one paper
            top = max(l)
            bottom = min(l)
            
            print 'bottom, top: ', bottom, top
            self.output.s_median_range = str(bottom) + ' to ' + str(top) + ' days.'
            
            # Now for the communicate
            # First take care of the three easy cases where they all agree
            if top <= 10: # by definition bottom would be less as well
                self.output.communicate = 'Predicts days.'
            elif bottom >= 61: # by def top would be more too
                self.output.communicate = 'Predicts months.'
            elif 11 <= top <= 60 and 11 <= bottom <= 60:
                self.output.communicate = 'Predicts weeks.'
            
            # Now for two small spread
            elif bottom <= 10 and 11 <= top <= 60:
                self.output.communicate = 'Predicts days to weeks.'
            elif 11 <= bottom <= 60 and 60 <= top:
                self.output.communicate = 'Predicts weeks to months.'
                
            # And the one wide spread
            elif bottom <= 10 and top >= 61:
                self.output.communicate = 'Predicts days to months (not reliable).'
            print self.output.communicate
        
                                                       
    def pps_scorer(self):
        score = int(self.fd['PPS_f'])
        self.output.score = score
    
    def ecog_scorer(self):
        score = int(self.fd['ECOG_f'])
        self.output.score = score
    
    def kps_scorer(self):
        score = int(self.fd['KPS_f'])
        self.output.score = score
            
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
        print 'psppi score', psppi_score_total
        self.output.score = psppi_score_total
              
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
        
        cp = self.fd['Clinical_Prediction_f']
        if cp == '>12':
            clin_prediction_ps = 0.0
        elif cp == '11-12':
            clin_prediction_ps = 2.0
        elif cp == '9-10':
            clin_prediction_ps = 2.5
        elif cp == '7-8':
            clin_prediction_ps = 2.5
        elif cp == '5-6':
            clin_prediction_ps = 4.5
        elif cp == '3-4':
            clin_prediction_ps = 6.0
        elif cp == '1-2':
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
            self.output.s_prob = '-'
            self.pps_scorer() 
            self.Pps_Jang_2014()
            
            self.s_output_maker()
            
        else:
            self.output.unavailable('Insufficient data to calculate PPS')
            #self.output.score = 'Insufficient data to calculate PPS'
               
        
                    
    def Pps_Jang_2014(self):
        c = Paper()
        c.location = 'palliative care clinic' 
        c.cite = '(Jang, 2014)'
        c.notes = "All advanced cancer, one third still receiving active treatment, 1655 pts, relatively few with poor performance status."
        #c.is_original = True
        if self.output.score >= 80:
            c.median = "221 days (197-244 in the 95% CI)"
            c.group = 'A'
            c.s_median = 221
        elif 60 <= self.output.score <=70:
            c.median = "115 days (105-131 in the 95% CI)"
            c.group = 'A'
            c.s_median = 115
        elif 40 <= self.output.score <=50:
            c.median = "51 days (44-60 in the 95% CI)"
            c.group = 'B'
            c.s_median = 51
        elif self.output.score <=30: 
            c.median = "22 days (12-102 in the 95% CI)"
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
        c.cite, d.cite, e.cite = '(Yamada, 2016)', '(Yamada, 2016)', '(Yamada, 2016)'  
        
        c.notes = 'All advanced cancer, ~40% on chemotherapy, 906 pts'
        d.notes = 'All advanced cancer, 8.5% on chemotherapy, 892 pts'
        e.notes = 'All advanced cancer, 14% on chemotherapy, 548 pts'
        
        # Probabilities
        if 6.0 <= self.output.score:
            self.output.s_prob = 'Predicted survival <= 21 days. Sens 81%, Spec 61.3%, PPV 53.2%, NPV 85.6%'
            c.prob = 'Predicted survival < 21 days. Sens 79.4%, Spec 68.2%, PPV 50.4%, NPV 71.1%'
            d.prob = 'Predicted survival < 21 days. Sens 85.0%, Spec 51.8%, PPV 58.3%, NPV 81.4%'
            e.prob = 'Predicted survival < 21 days. Sens 74.0%, Spec 63.6%, PPV 47.5%, NPV 84.6%'
            
        if 4.0 <= self.output.score < 6.0 :
            self.output.s_prob = 'Predicted survival <= 42 days. Sens 92.5%, Spec 40.3%, PPV 66.8%, NPV 80.6%'
            c.prob = 'Predicted survival < 42 days. Sens 76.7%, Spec 86.4%, PPV 83.5%, NPV 80.5%'
            d.prob = 'Predicted survival < 42 days. Sens 94.2%, Spec 24.7%, PPV 72.4%, NPV 67.0%'
            e.prob = 'Predicted survival < 42 days. Sens 92.8%, Spec 32.7%, PPV 60.9%, NPV 80.0%'
        
        if self.output.score < 4.0 : #??? Should I include this
            self.output.s_prob = 'PSPPI < 4, predicted survival > 42 days. ??? Sens/Spec/PPV/NPV'
            c.prob = 'PSPPI < 4, predicted survival > 42 days. ??? Sens/Spec/PPV/NPV'
            d.prob = 'PSPPI < 4, predicted survival > 42 days. ??? Sens/Spec/PPV/NPV'
            e.prob = 'PSPPI < 4, predicted survival > 42 days. ??? Sens/Spec/PPV/NPV'    
            
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

        c.cite, d.cite, e.cite = '(Baba, 2015)', '(Baba, 2015)', '(Baba, 2015)'
        c.notes = 'All metastatic cancer, no chemotherapy, 554 pts'
        d.notes = 'All metastatic cancer, no chemotherapy, 820 pts'
        e.notes = 'All metastatic cancer, no chemotherapy, 472 pts'
        
        # Probabilities
        if 6.0 <= self.output.score:
            c.prob = 'Predicted survival < 21 days. Sens 69.1%, Spec 80.4%, PPV 64.7%, NPV 83.4%'
            d.prob = 'Predicted survival < 21 days. Sens 65.8%, Spec 71.5%, PPV 64.6%, NPV 72.6%'
            e.prob = 'Predicted survival < 21 days. Sens 50.0%, Spec 84.1%, PPV 57.7%, NPV 79.5%'
            
        if 4.0 <= self.output.score < 6.0: #???
            c.prob = 'Predicted survival < 42 days. Sens 72.5%, Spec 76.6%, PPV 72.8%, NPV 76.4%'
            d.prob = 'Predicted survival < 42 days. Sens 61.4%, Spec 77.4%, PPV 56.4%, NPV 80.7%'
            e.prob = 'Predicted survival < 42 days. Sens 71.9%, Spec 67.1%, PPV 65.3%, NPV 73.5%'
            
        if self.output.score < 4.0: #???
            c.prob = 'PPI < 4.0. ?Predicted survival > 42 days. ??? Sens/Spec/PPV/NPV'
            d.prob = 'PPI < 4.0. ?Predicted survival > 42 days. ??? Sens/Spec/PPV/NPV'
            e.prob = 'PPI < 4.0. ?Predicted survival > 42 days. ??? Sens/Spec/PPV/NPV'
            
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
        c.cite = '(Morita, 1999)'
        c.notes = "All cancer, admitted to inpatient hospice, 350 pts in training cohort, 95 in validation cohort."
        #c.is_original = True
        if self.output.score <= 2.0:
            c.median = "134 days (123-145 in the 95% CI)"
            c.group = 'A'
            c.s_median = 134
        if 2.0 < self.output.score <= 4.0:
            c.median = "89 days (82-96 in the 95% CI)" 
            c.group = 'B'
            c.s_median = 89
        if self.output.score > 4.0:
            c.median = "23 days (20-26 in the 95% CI)"
            c.group = 'C'
            c.s_median = 23

        #Now the PPI probabilities 
        if 6.0 <= self.output.score:
            c.prob = "Expected survival less than 21 days. Sens 83%, Spec 85%, PPV 80%, NPV 87%"
            self.output.s_prob = "Survival less than 21 days: 80% ???"
        if 4.0 <= self.output.score < 6.0:
            c.prob = "Expected survival less than 42 days. Sens 79%, Spec 77%, PPV 83%, NPV 71%"
            self.output.s_prob = "Survival less than 42 days: 83% ???" 

        if self.output.score < 4.0:
            c.prob = 'Survival more than 42 days: ???'
            self.output.s_prob = 'Survival more than 42 days: ???'
        
            
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
        c.cite = '(Maltoni, 1999)'
        c.notes = "Advanced solid cancers only, enrolled in hospice, 451 pts in validation cohort."
        #c.is_original = True
        
        if self.output.score <= 5.5:
            c.prob = "Survival at 30 days is 86.6%"
            self.output.s_prob = "Survival at 30 days: 86.6%"
            c.median = "76 days"
            c.group = 'A'
            c.s_median = 76
        elif 5.6 <= self.output.score <= 11.0:
            c.prob = "Predicted survival at 30 days probability is 51.6%"
            self.output.s_prob = "Survival at 30 days: 51.6%"
            c.median = "32 days"
            c.group = 'B'
            c.s_median = 32
        elif self.output.score >= 11.1:
            c.prob = "Predicted survival at 30 days probability is 16.9%"
            self.output.s_prob = "Survival at 30 days: 16.9%"
            c.median = "14 days"
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

        c.cite, d.cite, e.cite = '(Baba, 2015)', '(Baba, 2015)', '(Baba, 2015)'
        c.notes = 'All metastatic cancer, no chemotherapy, 554 pts'
        d.notes = 'All metastatic cancer, no chemotherapy, 820 pts'
        e.notes = 'All metastatic cancer, no chemotherapy, 472 pts'
        
        # First do probabilistic
        # ??? PaP Baba cutoffs also hard or soft?
            # They refer to Pirovani paper, which uses different probabilities, and uses hard upper bounds for group A [0-5.5], group B: [5.6 - 11.0], group C: [11.1-15.0]
            # However, Baba only gives two groups (short and long)
        
        if 9.0 < self.output.score: #short survival
            c.prob = 'Predicted survival <= 21 days. Sens 80.4%, Spec 81.6%, PPV 70.6%, NPV 88.3%'
            d.prob = 'Predicted survival <= 21 days. Sens 79.2%, Spec 69.0%, PPV 66.8%, NPV 80.8%'
            e.prob = 'Predicted survival <= 21 days. Sens 74.1%, Spec 70.6%, PPV 55.1%, NPV 84.8%'
        
        if 5.5 < self.output.score <= 9.0: #???
            c.prob = 'Prob survival not explicitely defined in (Baba, 2015) for PaP score range 5.6-9.0. Could reasonably say 21-30 days???'
            d.prob = 'Prob survival not explicitely defined in (Baba, 2015) for PaP score range 5.6-9.0. Could reasonably say 21-30 days???'
            e.prob = 'Prob survival not explicitely defined in (Baba, 2015) for PaP score range 5.6-9.0. Could reasonably say 21-30 days???'
               
        if self.output.score <= 5.5:
            c.prob = 'Predicted survival >= 30 days. Sens 61.9%, Spec 91.6%, PPV 89.9%, NPV 66.5%'
            d.prob = 'Predicted survival >= 30 days. Sens 42.8%, Spec 95.4%, PPV 88.3%, NPV 67.4%'
            e.prob = 'Predicted survival >= 30 days. Sens 53.6%, Spec 90.0%, PPV 86.7%, NPV 61.5%'
            
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
        c.cite = '(Scarpi, 2011)'
        c.notes = "All advanced solid cancers only, enrolled in hospice, retrospective 362 pts."
        #c.is_original = True
        if self.output.score <= 7.0:
            c.prob = "30 day survival probability is 83% (77-90% in the 95% CI)"
            self.output.s_prob = "Survival at 30 days: 83%"
            c.median = "73 days (59-83 in the 95% CI)"
            c.group = 'A'
            c.s_median = 73
            
        elif 7.1 <= self.output.score <= 12.5:
            c.prob = "30 day survival probability is 50% (42-58% in the 95% CI)"
            self.output.s_prob = "Survival at 30 days: 50%"
            c.median = "30 days (25-39 in the 95% CI)"
            c.group = 'B'
            c.s_median = 30
            
        elif self.output.score >= 12.6:
            c.prob = "30 day survival probability is 9% (3-15% in the 95% CI)"
            self.output.s_prob = "Survival at 30 days: 9%"
            c.median = "11 days (8-17 in the 95% CI)"
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

        c.cite, d.cite, e.cite = '(Baba, 2015)', '(Baba, 2015)', '(Baba, 2015)'
        c.notes = 'All metastatic cancer, no chemotherapy, 554 pts'
        d.notes = 'All metastatic cancer, no chemotherapy, 820 pts'
        e.notes = 'All metastatic cancer, no chemotherapy, 472 pts'
        
        # First do probabilistic
        # See discussion under PaP_Baba probabilities
        
        if self.output.score > 9.0: #short survival
            c.prob = 'Predicted survival <= 21 days. Sens 82.3%, Spec 78.8%, PPV 68.1%, NPV 89.0%'
            d.prob = 'Predicted survival <= 21 days. Sens 84.0%, Spec 66.2%, PPV 66.1%, NPV 84.1%'
            e.prob = 'Predicted survival <= 21 days. Sens 81.0%, Spec 68.6%, PPV 56.0%, NPV 88.0%'
        
        if 7.0 < self.output.score <= 9.0: #???Medium survival
            c.prob = 'Prob survival not explicitely defined in Baba 2015 for D-PaP score range 7.1-9.0, 21-30 days???'
            d.prob = 'Prob survival not explicitely defined in Baba 2015 for D-PaP score range 7.1-9.0, 21-30 days???'
            e.prob = 'Prob survival not explicitely defined in Baba 2015 for D-PaP score range 7.1-9.0, 21-30 days???'
            
        if self.output.score <= 7.0: #long survival
            c.prob = 'Predicted survival >= 30 days. Sens 71.3%, Spec 87.1%, PPV 87.0%, NPV 71.5%'
            d.prob = 'Predicted survival >= 30 days. Sens 59.0%, Spec 89.8%, PPV 82.3%, NPV 73.0%'
            e.prob = 'Predicted survival >= 30 days. Sens 62.5%, Spec 83.8%, PPV 82.2%, NPV 65.0%'

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
            self.output.s_prob = '-'
            self.ecog_scorer()
            self.Ecog_Jang_2014()
            
            self.s_output_maker()
        else:
            self.output.unavailable('Insufficient data to calculate ECOG')  

    
    def Ecog_Jang_2014(self):
        #print 'self.output.score', self.output.score
        c = Paper()
        c.location = 'palliative care clinic'
        c.cite = '(Jang, 2014)'
        c.notes = "All advanced cancer, one third still receiving active treatment, 1655 pts, relatively few with poor performance status."
        if self.output.score == 0:
            c.median = "293 days (242-403 in the 95% CI)"
            c.group = 'A'
            c.s_median = 293
            
        elif self.output.score == 1:
            c.median = "197 days (183-219 in the 95% CI)"
            c.group = 'A'
            c.s_median = 197
        elif self.output.score == 2:
            c.median = "104 days (90-118 in the 95% CI)"
            c.group = 'A'
            c.s_median = 104
        elif self.output.score == 3:
            c.median = "55 days (46-66 in the 95% CI)"
            c.group = 'B'
            c.s_median = 55
        elif self.output.score == 4:
            c.median = "25.5 days (17-51 in the 95% CI)"
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
            self.output.s_prob = '-'
            self.kps_scorer()
            self.Kps_Jang_2014()
            
            self.s_output_maker()
        else:
            self.output.unavailable('Insufficient data to calculate KPS')
    
    def Kps_Jang_2014(self):
        c = Paper()
        c.location = 'palliative care clinic'
        c.cite = '(Jang, 2014)'
        c.notes = "All advanced cancer, one third still receiving active treatment, 1655 pts, relatively few with poor performance status."
        #c.is_original = True
        
        if 80 <= self.output.score <= 100:
            c.median = "215 days (190-241 in the 95% CI)"
            c.group = 'A'
            c.s_median = 215
        elif 60 <= self.output.score <= 70:
            c.median = "119 days (106-132 in the 95% CI)"
            c.group = 'A'
            c.s_median = 119
        elif 40 <= self.output.score <= 50:
            c.median = "49 days (43-59 in the 95% CI)"
            c.group = 'B'
            c.s_median = 49
        elif self.output.score <= 30:
            c.median = "29 days (22-144 in the 95% CI)"
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
    Clinical_Prediction_f = SelectField("Clinician's prediction of survival: ", choices= (('empty', 'Unavailable'), ('>12','>12 weeks'), ('11-12','11-12 weeks'), ('9-10','9-10 weeks'), ('7-8','7-8 weeks'), ('5-6','5-6 weeks'), ('3-4','3-4 weeks'), ('1-2','0-2 weeks'))) 
    WBC_f = SelectField('Total WBC (cell/cc): ', choices=(('empty', 'Unavailable'), (0.0, 'Normal (4,800-8,500)'), (0.5, 'High (8,501-11,000)'), (1.5, 'Very High (>11,000)'))) # The values are the pts in PaP/D-PaP, what did they do with low WBCs?
    Lymphocyte_f = SelectField('Lymphocyte Percentage: ', choices=[('empty', 'Unavailable'), (0.0, 'Normal (20.0-40.0%)'), (1.0, 'Low (12.0-19.9%)'), (2.5, 'Very Low (0-11.9%)')]) # The values are the pts in PaP/D-PaP, what to do with very high lymphs?

   
       

