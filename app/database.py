from app.models.Setting import Setting

from .extensions import Base, SessionLocal, engine
from .models import GenderizeResult
from .enums import GenderEnum
import csv
import os

from .constants import DEFAULT_DATA_PATH, DEFAULT_DATA_SOURCE_NAME

def init_db():
    Base.metadata.create_all(bind=engine)
    genderize_table = SessionLocal().query(GenderizeResult).first()
    if not genderize_table:
        print("Initializing database with sample data...")
        insert_default_data()

def insert_default_data():
    if not os.path.exists(DEFAULT_DATA_PATH):
        print("No default data file found. Skipping initialization.")
        return
    with open(DEFAULT_DATA_PATH, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            probability = float(row['probability']) if 'probability' in row and row['probability'] else 1.0
            save_result(name=row['name'], gender=row['gender'], probability=probability, source=DEFAULT_DATA_SOURCE_NAME)

def get_result_by_name(name: str) -> GenderizeResult:
    session = SessionLocal()
    try:
        result = session.query(GenderizeResult).filter_by(name=name).first()
        return result
    except Exception as e:
        print(f"Error fetching result: {e}")
        return None
    finally:
        session.close()

def update_result(name: str, gender: str, probability: float, source: str):
    session = SessionLocal()
    try:
        result = session.query(GenderizeResult).filter_by(name=name, source=source).first()
        if result:
            result.gender = gender
            result.probability = probability
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error updating result: {e}")
    finally:
        session.close()

def save_result(name: str, gender: str, probability: float, source: str):
    result = get_result_by_name(name)
    
    if result:
        print(f"Result for {name} already exists in dataset. Skipping save.")
        return
    
    if gender == "male":
        gender = GenderEnum.MALE
    elif gender == "female":
        gender = GenderEnum.FEMALE
    else:
        gender = None

    session = SessionLocal()
    try:
        new_result = GenderizeResult(name=name, gender=gender, probability=probability, source=source)
        session.add(new_result)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error saving result: {e}")
    finally:
        session.close()
        

def add_or_update_settings(key: str, value: str):
    session = SessionLocal()
    try:
        setting = session.query(Setting).filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            session.add(setting)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error saving setting: {e}")
    finally:
        session.close()

def get_settings(key: str) -> str:
    session = SessionLocal()
    try:
        setting = session.query(Setting).filter_by(key=key).first()
        return setting.value if setting else None
    except Exception as e:
        print(f"Error fetching setting: {e}")
        return None
    finally:
        session.close()