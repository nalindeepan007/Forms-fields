from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import getDb
from app.db.store import FormStore
from app.schemas import (
    FormCreate, FormUpdate, FormInDB,
    SubmissionCreate, SubmissionInDB, SubmissionDetail
)
from app.utils.logger import getLogger

logger = getLogger()
router = APIRouter()


@router.post("/forms", response_model=FormInDB, status_code=status.HTTP_201_CREATED)
def createForm(
    formData: FormCreate,
    db: Session = Depends(getDb)
):
    try:
        
        formCreated = FormStore.createForm(db, formData)
        return formCreated
    
    except Exception as e:
        logger.error(f"API crud: error in createForm: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"unexpected error occurred while creating form: {str(e)}"
        )


@router.get("/forms/{formId}", response_model=FormInDB)
def getForm(
    formId: int = Path(..., gt=0),
    db: AsyncSession = Depends(getDb)
):
    """
    Get form details by ID
    """
    try:
        form = FormStore.getForm(db, formId)
        return form
    
    except Exception as e:
        logger.error(f"API: Unexpected error in getForm: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while retrieving form: {str(e)}"
        )

@router.put("/forms/{formId}", response_model=FormInDB)
def updateForm(
    formData: FormUpdate,
    formId: int = Path(..., gt=0),
    db: AsyncSession = Depends(getDb)
):
    """
    Update form and its fields
    """

    try:
        formUpdated = FormStore.updateForm(db, formId, formData)
        return formUpdated
    
    except Exception as e:
        logger.error(f"API: Unexpected error in updateForm: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while updating form: {str(e)}"
        )



@router.post("/forms/{formId}/submissions", response_model=SubmissionInDB, status_code=status.HTTP_201_CREATED)
def createSubmission(
    submissionData: SubmissionCreate,
    formId: int = Path(..., gt=0),
    db: AsyncSession = Depends(getDb)
):
    """
    Create a new submission for a form
    """
    try:
        if submissionData.form_id != formId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Form ID in the path must match the one in the request body"
            )
        
        return FormStore.createSubmission(db, submissionData)
    
    except Exception as e:
        logger.error(f"API: Unexpected error in createSubmission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while creating submission: {str(e)}"
        )


@router.get("/forms/{formId}/submissions/{submissionId}", response_model=SubmissionDetail)
def getSubmissions(
    formId: int = Path(..., gt=0),
    submissionId: int = Path(..., gt=0),
    db: AsyncSession = Depends(getDb)
):
    """
    Get submission details by sub ID
    """
    try:
        submission = FormStore.getSubmissionValues(db, formId, submissionId)
        return submission
    
    except Exception as e:
        logger.error(f"API: Unexpected error in getSubmission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while retrieving submission: {str(e)}"
        )


@router.get("/forms", response_model=List[FormInDB])
def getForms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(getDb)
):
    """
    get forms with pagination
    """


    try:
        forms = FormStore.getForms(db, skip, limit)
        return forms
    
    except Exception as e:
        logger.error(f"API getforms: Unexpected error in getForms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error occurred while retrieving forms: {str(e)}"
        )



@router.delete("/forms/{formId}", status_code=status.HTTP_204_NO_CONTENT)
def deleteForm(
    formId: int = Path(..., gt=0),
    db: AsyncSession = Depends(getDb)
):
    try:
        FormStore.removeForm(db, formId)

        logger.info(f"API: Form deleted successfully: ID={formId}")
        return None
    
    except Exception as e:
        logger.error(f"API: Unexpected error in deleteForm: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while deleting form: {str(e)}"
        )