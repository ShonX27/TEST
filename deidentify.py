import pandas as pd
import numpy as np
import re

def apply_age_bands(age):
    """Converts exact ages into predefined bands."""
    if pd.isna(age):
        return np.nan
    try:
        age = float(age)
        if 0 <= age <= 17:
            return '0-17'
        elif 18 <= age <= 40:
            return '18-40'
        elif 41 <= age <= 64:
            return '41-64'
        elif age >= 65:
            return '65+'
        else:
            return 'Unknown'
    except ValueError:
        return 'Unknown'

def detect_sensitive_columns(df):
    """
    Automatically detects sensitive columns (identifiers, free-text) 
    based on column names and basic patterns.
    """
    # Extremely comprehensive dictionary covering PII, PHI, PCI, and general identifiers
    extensive_pii_dict = [
        # Identity & Names
        "name", "firstname", "lastname", "middlename", "surname", "givenname", "nickname", 
        "maidenname", "fullname", "username", "initials", "suffix", "prefix", "title", 
        "dob", "dateofbirth", "birthdate", "birthday", "birthyear", "age", "gender", 
        "sex", "race", "ethnicity", "nationality", "citizenship", "maritalstatus", 
        "religion", "politicalaffiliation", "ssn", "socialsecurity", "socialsecuritynumber", 
        "nationalid", "passport", "passportnumber", "driverlicense", "driverslicense", 
        "stateid", "voterid", "taxid", "sin", "nino", "aadhar", "identitynumber",

        # Contact & Location
        "email", "emailaddress", "phone", "phonenumber", "mobile", "cell", "cellphone", 
        "telephone", "fax", "pager", "address", "street", "streetaddress", "city", 
        "state", "province", "region", "zip", "zipcode", "postal", "postalcode", 
        "country", "location", "coordinate", "latitude", "longitude", "gps", "ip", 
        "ipaddress", "mac", "macaddress", "homephone", "workphone", "apartment", "suite",

        # Financial (PCI)
        "bankaccount", "checkingaccount", "savingsaccount", "routingnumber", "creditcard", 
        "debitcard", "ccnumber", "cvv", "cvc", "expirationdate", "cardholder", "pan", 
        "iban", "swift", "bic", "sortcode", "accountbalance", "salary", "income", 
        "wage", "taxbracket", "creditscore", "loannumber", "mortgage", "paymentinfo",

        # Health & Medical (PHI)
        "patientid", "medicalrecord", "mrn", "healthplan", "healthinsurance", "medicare", 
        "medicaid", "treatment", "diagnosis", "prescription", "medication", "doctor", 
        "hospital", "clinic", "bloodtype", "biometrics", "fingerprint", "retinascan", 
        "dna", "medicalhistory", "disability", "healthcondition", "policyholder",

        # Online, Tech & Auth
        "password", "passhash", "secret", "token", "authtoken", "cookie", "sessionid", 
        "deviceid", "imei", "meid", "advertisingid", "profileurl", "socialmedia", 
        "facebook", "twitter", "linkedin", "instagram", "website", "domain", "authid", 
        "authproviderid", "resettoken", "alias",

        # Employment & Education
        "employer", "employerid", "employeeid", "company", "occupation", "jobtitle", 
        "department", "manager", "studentid", "school", "university", "degree", 
        "graduationyear", "gpa", "transcript", "alumni",

        # OBA Capstone Specific & Free-text
        "story", "description", "note", "comment", "message", "reference", "wire", 
        "social", "contact", "designation", "memo", "feedback"
    ]
    
    sensitive_keywords = list(set(extensive_pii_dict))
    
    # Exclude these from being auto-dropped even if they match a keyword
    safe_keywords = [
        'date', 'amount', 'category', 'location', 'currency', 'status', 'count', 'campaign'
    ]
    
    cols_to_drop = []
    
    for col in df.columns:
        col_lower = str(col).lower()
        
        # 1. Check against safe keywords first
        if any(safe in col_lower for safe in safe_keywords):
            # 'location' might be safe, but 'location id' might not. We prioritize safe keywords.
            continue
            
        # 2. Check against sensitive keyword dictionary
        if any(keyword in col_lower for keyword in sensitive_keywords):
            cols_to_drop.append(col)
            continue
            
        # 3. Basic content inspection (Regex for emails/phones in a small sample)
        sample_data = df[col].dropna().head(100).astype(str)
        if not sample_data.empty:
            # Check for emails
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if sample_data.str.match(email_pattern).any():
                cols_to_drop.append(col)
                continue
                
    return list(set(cols_to_drop))

def deidentify_data(df, id_cols=None, text_cols=None, age_col=None, keep_cols=None, auto_detect=True):
    """
    De-identifies a pandas DataFrame according to the OBA Capstone rules.
    
    Args:
        df (pd.DataFrame): The raw dataframe.
        id_cols (list): (Optional) Manual list of identifier columns to drop.
        text_cols (list): (Optional) Manual list of free-text columns to drop.
        age_col (str): The name of the age column to convert to bands.
        keep_cols (list): Strict list of columns to keep. If provided, ignores drops and only keeps these.
        auto_detect (bool): If True, automatically detects and removes sensitive columns.
        
    Returns:
        pd.DataFrame: A de-identified dataframe.
    """
    df_cleaned = df.copy()
    
    # 1. Determine columns to drop
    cols_to_drop = []
    if id_cols:
        cols_to_drop.extend(id_cols)
    if text_cols:
        cols_to_drop.extend(text_cols)
        
    if auto_detect:
        auto_detected_cols = detect_sensitive_columns(df)
        cols_to_drop.extend(auto_detected_cols)
        
    cols_to_drop = [col for col in cols_to_drop if col in df_cleaned.columns]
    
    # 2. Filter strictly to keep_cols if provided (overrides drop logic)
    if keep_cols:
        existing_keep_cols = [col for col in keep_cols if col in df_cleaned.columns]
        df_cleaned = df_cleaned[existing_keep_cols]
    elif cols_to_drop:
        # Otherwise, drop the identified sensitive columns
        df_cleaned = df_cleaned.drop(columns=cols_to_drop)
        
    # 3. Convert exact ages to bands
    if age_col and age_col in df_cleaned.columns:
        df_cleaned[age_col] = df_cleaned[age_col].apply(apply_age_bands)
        
    return df_cleaned
