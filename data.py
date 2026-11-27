# toy dataset with made-up prices and simplified interactions
# for our algorithms class project (not real medical advice)

# name, drug class, typical daily dose in mg, monthly cost in dollars
DRUGS = [
    ("metformin", "diabetes", 1000, 12),
    ("lisinopril", "ACE inhibitor", 10, 8),
    ("losartan", "ARB", 50, 9),
    ("atorvastatin", "statin", 20, 15),
    ("simvastatin", "statin", 20, 10),
    ("amlodipine", "calcium channel blocker", 5, 9),
    ("metoprolol", "beta blocker", 50, 10),
    ("hydrochlorothiazide", "diuretic", 25, 7),
    ("spironolactone", "diuretic", 25, 12),
    ("potassium chloride", "supplement", 20, 8),
    ("omeprazole", "acid reducer", 20, 14),
    ("sertraline", "SSRI", 50, 13),
    ("fluoxetine", "SSRI", 20, 12),
    ("gabapentin", "nerve pain", 300, 18),
    ("tramadol", "opioid", 50, 17),
    ("alprazolam", "benzodiazepine", 1, 15),
    ("ibuprofen", "NSAID", 400, 6),
    ("aspirin", "antiplatelet", 81, 4),
    ("clopidogrel", "antiplatelet", 75, 16),
    ("warfarin", "blood thinner", 5, 11),
    ("prednisone", "steroid", 10, 9),
    ("clarithromycin", "antibiotic", 500, 22),
    ("ciprofloxacin", "antibiotic", 500, 19),
    ("sildenafil", "ED / PAH", 50, 20),
]

# drug a, drug b, severity, note
INTERACTIONS = [
    ("warfarin", "aspirin", "major", "much higher bleeding risk"),
    ("warfarin", "ibuprofen", "major", "bleeding risk goes up"),
    ("warfarin", "ciprofloxacin", "major", "can raise INR, bleeding risk"),
    ("warfarin", "fluoxetine", "moderate", "may increase bleeding"),
    ("clopidogrel", "omeprazole", "moderate", "clopidogrel may work less well"),
    ("clopidogrel", "aspirin", "moderate", "more bleeding risk"),
    ("simvastatin", "clarithromycin", "major", "muscle damage risk"),
    ("atorvastatin", "clarithromycin", "major", "muscle damage risk"),
    ("amlodipine", "simvastatin", "moderate", "higher statin levels"),
    ("lisinopril", "ibuprofen", "moderate", "kidney strain, weaker BP effect"),
    ("lisinopril", "spironolactone", "major", "high potassium"),
    ("lisinopril", "potassium chloride", "major", "high potassium"),
    ("lisinopril", "hydrochlorothiazide", "minor", "common combo, watch BP"),
    ("losartan", "potassium chloride", "major", "high potassium"),
    ("losartan", "spironolactone", "major", "high potassium"),
    ("sertraline", "tramadol", "major", "serotonin syndrome risk"),
    ("fluoxetine", "tramadol", "major", "serotonin syndrome risk"),
    ("sertraline", "ibuprofen", "moderate", "stomach bleeding risk"),
    ("sertraline", "aspirin", "moderate", "stomach bleeding risk"),
    ("alprazolam", "tramadol", "major", "heavy sedation, breathing risk"),
    ("alprazolam", "gabapentin", "moderate", "extra drowsiness"),
    ("metformin", "ciprofloxacin", "moderate", "blood sugar swings"),
    ("metformin", "prednisone", "moderate", "steroid raises blood sugar"),
    ("prednisone", "ibuprofen", "moderate", "stomach ulcer risk"),
    ("metoprolol", "amlodipine", "minor", "lower heart rate and BP"),
    ("sildenafil", "amlodipine", "moderate", "blood pressure can drop too far"),
    ("sildenafil", "metoprolol", "minor", "small extra BP drop"),
]

# preloaded sample patients (fake)
PATIENTS = {
    "Patient A (heart + pain)": ["warfarin", "aspirin", "lisinopril", "atorvastatin", "ibuprofen"],
    "Patient B (mood + pain)": ["sertraline", "tramadol", "gabapentin", "omeprazole"],
    "Patient C (blood pressure - minor interaction)": ["metoprolol", "amlodipine"],
    "Patient D (diabetes - no interactions)": ["metformin", "atorvastatin", "losartan", "hydrochlorothiazide"],
}
