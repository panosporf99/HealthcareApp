import pandas as pd
from app import app, db, Patient

def import_data_from_csv(csv_file):
    with app.app_context():
        # Read CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file)
        print(df.head())

        # Iterate through DataFrame rows and add each patient to the database
        for _, row in df.iterrows():
            patient = Patient(
                name=row['Name'],
                age=row['Age'],
                email=row['Email'],
                gender=row['Gender'],
                blood_type=row['Blood Type'],
                medical_condition=row['Medical Condition'],
                date_of_admission=row['Date of Admission'],
                doctor=row['Doctor'],
                hospital=row['Hospital'],
                insurance_provider=row['Insurance Provider'],
                billing_amount=row['Billing Amount'],
                room_number=row['Room Number'],
                admission_type=row['Admission Type'],
                discharge_date=row['Discharge Date'],
                medication=row['Medication'],
                test_results=row['Test Results']
            )
            db.session.add(patient)

        # Commit changes to the database
        db.session.commit()

if __name__ == '__main__':
    # Provide the path to your CSV file
    csv_file_path = 'healthcare_dataset.csv'
    import_data_from_csv(csv_file_path)
