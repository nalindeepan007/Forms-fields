from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Table, JSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func



Base = declarative_base()

form_field = Table(
    "form_field_relation",
    Base.metadata,
    Column("form_id", Integer, ForeignKey("form.id"), primary_key=True),
    Column("field_id", Integer, ForeignKey("field.id"), primary_key=True),
)  

class Form(Base):
    __tablename__ = "form"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())

    fields = relationship("Field", secondary=form_field, back_populates="forms")
    submissions = relationship("Submission", back_populates="form")

class Field(Base):
    __tablename__ = "field"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    required = Column(Boolean, default=False)
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())

    forms = relationship("Form", secondary=form_field, back_populates="fields")
    values = relationship("FieldData", back_populates="field")

    refer_field_id = Column(Integer, ForeignKey("field.id"), nullable=True)
    refer_field = relationship("Field", remote_side=[id], backref="referencing_fields")

class Submission(Base):
    __tablename__ = "submission"
    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("form.id"), nullable=False, index=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())

    form = relationship("Form", back_populates= "submissions")
    field_values = relationship("FieldData", back_populates="submission")


class FieldData(Base):
    """handling values in submitted form fields"""
    __tablename__ = "field_data"
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submission.id"), nullable=False, index=True)
    field_id = Column(Integer, ForeignKey("field.id"), nullable=False)
    value = Column(JSON, nullable=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())

    submission = relationship("Submission", back_populates="field_values")
    field = relationship("Field", back_populates="values")

 


    

