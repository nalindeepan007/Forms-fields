from datetime import datetime
from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field, ConfigDict


# Field schemas--------------------------------------
class FieldBase(BaseModel):
    
    name: str
    type: str
    required: bool = False


class FieldCreate(FieldBase):

    refer_field_id: Optional[int] = None


class FieldUpdate(BaseModel):

    name: Optional[str] = None
    type: Optional[str] = None
    required: Optional[bool] = None
    refer_field_id: Optional[int] = None


class FieldInDB(FieldBase):
    """Field in database"""
    id: int
    created: datetime
    updated: Optional[datetime] = None
    refer_field_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# Form schema----------------------------------
class FormBase(BaseModel):
    name: str


class FormCreate(FormBase):
  
    fields: List[FieldCreate] = []


class FormUpdate(BaseModel):
    
    name: Optional[str] = None
    fields_add: List[FieldCreate] = []
    fields_remove: List[int] = []
    fields_update: Dict[int, FieldUpdate] = {}


class FormInDB(FormBase):
    """Form values in database"""
    id: int
    created: datetime
    updated: Optional[datetime] = None
    fields: List[FieldInDB] = []

    model_config = ConfigDict(from_attributes=True)


# Field Value relationship schemas
class FieldDataBase(BaseModel):
    """Base schema for FieldValue"""
    field_id: int
    value: Any


class FieldValueCreate(FieldDataBase):
    """Schema for creating a FieldValue"""
    pass


class FieldDataInDB(FieldDataBase):
    
    id: int
    submission_id: int
    created: datetime
    updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Submission schemas-----------------------
class SubmissionBase(BaseModel):
    """Base schema for Submission"""
    form_id: int





class FieldDataCreate(FieldDataBase):
    """Schema for creating a FieldValue"""
    pass





class SubmissionCreate(SubmissionBase):
    field_values: List[FieldDataCreate]


class SubmissionInDB(SubmissionBase):
    """Submission in database"""
    id: int
    created: datetime
    updated: Optional[datetime] = None
    field_values: List[FieldDataInDB] = []

    model_config = ConfigDict(from_attributes=True)


class SubmissionDetail(BaseModel):
    
    id: int
    form_id: int
    created: datetime
    updated: Optional[datetime] = None
    values: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)