from typing import List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.db.dbModel import Form, Field, Submission, FieldData, form_field
from app.schemas import FormCreate, FormBase, FieldCreate, FormUpdate, SubmissionCreate, SubmissionDetail
from app.utils.logger import getLogger

logger = getLogger()


class FormStore:
    """ CRUD for Forms -> postgresdb """

    @staticmethod
    def createForm(db: Session, formData: FormCreate) -> Form:
        try:
            
            
            form = Form(name=formData.name)
            db.add(form)
            db.flush()
            for fieldData in formData.fields:
                field = FormStore.createGetField(db, fieldData)
                form.fields.append(field)

            db.commit()
            db.refresh(form)
            return form
        
        except Exception as e:
            logger.error(f"Error creating form: {str(e)}")
            db.rollback()
            # take care of safe back measures hameshaaaa!
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create form: {str(e)}"
            )
    
    @staticmethod
    def createGetField(db: Session, fieldData: FieldCreate) -> Field:
        try:
            if fieldData.refer_field_id:
                referencedField = db.query(Field).get(fieldData.refer_field_id)
                if not referencedField:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="data not found for this ref id, contact admin"
                    )

                field = Field(name=fieldData.name,
                            type=fieldData.type,
                            required=fieldData.required,
                            refer_field_id=referencedField.id
                            )
                db.add(field)
                return field

            else:
                field = Field(
                    name=fieldData.name,
                    type=fieldData.type,
                    required=fieldData.required
                )
                db.add(field)
                return field
        
        except HTTPException:
            # Re-raise
            raise
        except Exception as e:
            logger.error(f"Error creating field: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to createnew field: {str(e)}"
            )
        
        

    @staticmethod
    def getForm(db: Session, formId: int) -> Form:
        try:
            form =  db.query(Form).options(
                joinedload(Form.fields).joinedload(Field.refer_field)
            ).filter(Form.id == formId).first()
            if not form:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Form if{formId} not found"
                )
            return form
        
        except HTTPException:           
            raise
        except Exception as e:
            logger.error(f"Error retrieving form with ID {formId}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve form: {str(e)}"
            )
        
    
    @staticmethod
    def updateForm(db: Session, formId: int, formData: FormUpdate) -> Form:
        try:

            form = FormStore.getForm(db, formId)

            if formData.name:
                form.name = formData.name
            
            for fieldEntry in formData.fields_add:
                field = FormStore.createGetField(db, fieldEntry)
                form.fields.append(field)
            
            for fieldId in formData.fields_remove:
                field = db.query(Field).get(fieldId)

                if field and field in form.fields:
                    form.feilds.remove(field)

            for fieldId, fieldData in formData.fields_update.items():
                field = db.query(Field).get(fieldId)


                if field and field in form.fields:
                    if fieldData.name:
                        field.name = fieldData.name
                    if fieldData.type:
                        field.type = fieldData.type
                    if fieldData.required is not None:
                        field.required = fieldData.required
                    if fieldData.refer_field_id is not None:
                        field.refer_field_id = fieldData.refer_field_id

            db.commit()
            db.refresh(form)
            return form
        except HTTPException:
         
            raise
        except Exception as e:
            logger.error(f"Error updating form with ID {formId}: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update form: {str(e)}"
            )
    

    @staticmethod
    def createSubmission(db: Session, submitData: SubmissionCreate) -> Submission:

        try:
            form = db.get(Form, submitData.form_id)
            if not form:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Form with ID {submitData.form_id} not found"
                )
            
            formFields = FormStore.getFormFields(db, form.id)
            formFieldData = {field.id for field in formFields}

            for values in submitData.field_values:
                if values.field_id not in formFieldData:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"requested id not in form ID {form.id}"
                    )
            submission = Submission(form_id= form.id)
            db.add(submission)
            db.flush()

            for value in submitData.field_values:
                fieldValue = FieldData(
                            submission_id= submission.id,
                            field_id = value.field_id,
                            value=value.value
                )
                db.add(fieldValue)

            db.commit()
            db.refresh(submission)
            return submission
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating submission here: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create submission here: {str(e)}"
            )
        
    
    @staticmethod
    def getFormFields(db: Session, formId: int) -> List[Field]:
        """get all fields in a form"""

        try:
            form = db.query(Form).options(
                joinedload(Form.fields).joinedload(Field.refer_field)
            ).filter(Form.id == formId).first()

            if not form:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Form with ID {formId} not found"
                )
            
            fieldsCollection = []
            for field in form.fields:
                fieldsCollection.append(field)
                if field.refer_field:
                    fieldsCollection.append(field.refer_field)
            return fieldsCollection
        
        except HTTPException:
          
            raise
        except Exception as e:
            logger.error(f"Error retrieving fields for form ID {formId}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve form fields: {str(e)}"
            )
    
    @staticmethod
    def getSubmissionValues(db: Session, formId: int, submitId: int) -> Dict[str, Any]:
        try:
            logger.info(f"Getting submission values for form ID: {formId}, submission ID: {submitId}")
            
        
            form = db.get(Form, formId)
            if not form:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Form with ID {formId} not found"
                )
            
            submission =  db.query(Submission).filter(
                Submission.id == submitId,
                Submission.form_id == formId
            ).first()

            if not submission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Submission -> {submitId} for form ID {formId} not found"
                )
            
            
            fieldValues = db.query(FieldData).filter(
                FieldData.submission_id == submitId
            ).all()

            # Get all fields for the form
            
            formFields = db.query(Field).join(
                form_field, Field.id == form_field.c.field_id
            ).filter(
                form_field.c.form_id == formId
            ).all()

            fieldIdName = {field.id: field.name for field in formFields}
            result = {
                "id": submission.id,
                "form_id": submission.form_id,
                "created": submission.created,
                "updated": submission.updated,
                "values": {}
            }
            
            for value in fieldValues:
                field_id = value.field_id
                field_name = fieldIdName.get(field_id, f"field_{field_id}")
                result["values"][field_name] = value.value
            
            return result
        
        except HTTPException:
            
            raise
        except Exception as e:
            logger.error(f"Error retrieving submission values for submission ID={submitId}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve submission values: {str(e)}"
            )
    

    @staticmethod
    def getForms(db: Session, start: int = 0, range: int = 100) -> List[Form]:
        
        try:
            logger.info(f"Getting forms with pagination: start={start}, range={range}")
            
            forms = db.query(Form).offset(start).limit(range).all()
            return forms
        
        except Exception as e:
            logger.error(f"Error retrieving forms: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve forms: {str(e)}"
            )
    
    @staticmethod
    def removeForm(db: Session, formId: int) -> bool:
        try:
            logger.info(f"Removing form with ID: {formId}")
            form = db.query(Form).get(formId)
            
            if not form:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Form  id{formId} not found"
                )
            
            db.delete(form)
            db.commit()
            
            return True
        
        except HTTPException:
           
            raise
        except Exception as e:
            logger.error(f"Error deleting form with ID {formId}: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete form: {str(e)}"
            )
