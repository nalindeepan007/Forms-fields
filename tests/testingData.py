from typing import Dict, List, Any
from sqlalchemy.orm import Session

from app.db.dbModel import Form, Field, Submission, FieldData


def addTestData(db: Session) -> Dict[str, Any]:
    """
    operating test data to test db
    """
    # Create Form 1
    form1 = Form(name="Form 1")
    db.add(form1)
    db.flush()
    
    # Create fields for Form 1
    field1 = Field(name="Field 1", type="text")
    field2 = Field(name="Field 2", type="text")
    field3 = Field(name="Field 3", type="number")
    
    db.add_all([field1, field2, field3])
    db.flush()
    
    
    form1.fields.extend([field1, field2, field3])
    
    # Form2 fields
    form2 = Form(name="Form 2")
    db.add(form2)
    db.flush()
    
    # Create Field 4
    field4 = Field(name="Field 4", type="date")
    db.add(field4)
    db.flush()
    
    # Create fields that reference Field 2 and Field 3
    field2Ref = Field(
        name="Referenced Field 2", 
        type="text",
        refer_field_id=field2.id
    )
    
    field3Ref = Field(
        name="Referenced Field 3", 
        type="number",
        refer_field_id=field3.id
    )
    
    db.add_all([field2Ref, field3Ref])
    db.flush()
    
    # link fields with Form 2
    form2.fields.extend([field4, field2Ref, field3Ref])
    
    # submission for Form 1
    submission1 = Submission(form_id=form1.id)
    db.add(submission1)
    db.flush()
    
    # Create field values for submission 1
    fieldValue1 = FieldData(
        submission_id=submission1.id,
        field_id=field1.id,
        value="Sample Text for Field 1"
    )
    
    fieldValue2 = FieldData(
        submission_id=submission1.id,
        field_id=field2.id,
        value="Sample Text for Field 2"
    )
    
    fieldValue3 = FieldData(
        submission_id=submission1.id,
        field_id=field3.id,
        value=42
    )
    
    db.add_all([fieldValue1, fieldValue2, fieldValue3])
    
    # submit from form2
    submission2 = Submission(form_id=form2.id)
    db.add(submission2)
    db.flush()
    
    # Create field values for submission 2
    fieldValue4 = FieldData(
        submission_id=submission2.id,
        field_id=field4.id,
        value="2023-03-22"
    )
    
    fieldValue5 = FieldData(
        submission_id=submission2.id,
        field_id=field2Ref.id,
        value="Referenced Text for Field 2"
    )
    
    fieldValue6 = FieldData(
        submission_id=submission2.id,
        field_id=field3Ref.id,
        value=100
    )
    
    db.add_all([fieldValue4, fieldValue5, fieldValue6])
    
    db.commit()
    
    return {
        "form1": form1,
        "form2": form2,
        "field1": field1,
        "field2": field2,
        "field3": field3,
        "field4": field4,
        "field2_ref": field2Ref,
        "field3_ref": field3Ref,
        "submission1": submission1,
        "submission2": submission2
    }


def clearData(db: Session) -> None:
    """Clear all data from the database"""
    db.query(FieldData).delete()
    db.query(Submission).delete()
    db.query(Field).delete()
    db.query(Form).delete()
    db.commit()