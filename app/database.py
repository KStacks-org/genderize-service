from .extentions import Base, SessionLocal, engine
from .models import GenderizeResult
from .enums import GenderEnum

def init_db():
    Base.metadata.create_all(bind=engine)
    genderize_table = SessionLocal().query(GenderizeResult).first()
    if not genderize_table:
        print("Initializing database with sample data...")
        insert_default_data()

def insert_default_data():
    session = SessionLocal()
    try:
        sample_data = [
            {"name": "John", "gender": GenderEnum.MALE, "probability": 0.99, "source": "dataset"},
        ]
        for data in sample_data:
            existing_entry = session.query(GenderizeResult).filter_by(name=data["name"], source=data["source"]).first()
            if not existing_entry:
                new_entry = GenderizeResult(**data)
                session.add(new_entry)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting dataset data: {e}")
    finally:
        session.close()

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
        gender = GenderEnum.UNKNOWN

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
        