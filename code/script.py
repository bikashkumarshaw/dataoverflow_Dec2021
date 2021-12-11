import os
import pandas as pd
from datetime import datetime

VALID_VACCINES = ['a', 'b', 'c']
START_DATE = datetime.strptime('01-02-2020', "%d-%m-%Y")
END_DATE = datetime.strptime('30-11-2021', "%d-%m-%Y")

def covid_vaccine(vaccination_status_files, user_meta_file, output_file):
    df = pd.DataFrame()
    for fl in vaccination_status_files:
        if not os.path.exists(fl):
            continue
        vaccine_df = pd.read_csv(fl, sep='\t', header=0)
        for idx, row in vaccine_df.iterrows():
            user, vaccine, date = row
            if not is_vaccine_data_valid(user, vaccine, date):
                vaccine_df.drop(idx, inplace=True)

        df = pd.concat([df, vaccine_df], ignore_index=True)

    user_df = pd.read_csv(user_meta_file, sep='\t', header=0)
    for idx, row in user_df.iterrows():
        user, gender, city, state = row

        if not is_user_data_valid(user, gender, city, state):
            user_df.drop(idx, inplace=True)

    if df.empty:
        df.to_csv(output_file, index=False, sep='\t')
        return

    df = df.set_index('user')
    user_df = user_df.set_index('user')
    df.pop('date')
    my_df = df.join(user_df, how='inner', on='user')
    my_df = my_df.reset_index().drop_duplicates()
    my_df.pop('user')
    my_df = my_df.groupby(['city', 'state', 'vaccine', 'gender'], as_index=True).size()
    my_df = my_df.reset_index()
    my_df.rename(columns={"size": "unique_vaccinated_people"}, inplace=True)
    my_df.to_csv(output_file, index=False, sep='\t')

def is_user_data_valid(user, gender, city, state):
    if not (isinstance(gender, str) and isinstance(city, str) and isinstance(state, str)):
        return False

    # Try typecasting
    try:
        int(user)
    except:
        return False

    return True

def is_vaccine_data_valid(user, vaccine, date):
    if not isinstance(vaccine, str):
        return False

    # Try typecasting
    try:
        int(user)
    except:
        return False

    try:
        date = datetime.strptime(date, "%d-%m-%Y")
    except:
        return False

    if vaccine.lower() not in VALID_VACCINES:
        return False

    if date < START_DATE or date > END_DATE:
        return False

    return True
