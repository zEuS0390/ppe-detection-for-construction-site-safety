from sqlalchemy.orm import registry, relationship
from sqlalchemy import (
    Column, Integer, 
    String, DateTime, 
    ForeignKey
)
from datetime import datetime

mapper_registry = registry()

# These are PPE detection tables for construction

@mapper_registry.mapped
class Person:
    __tablename__="person"
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer)
    first_name = Column(String(length=250))
    middle_name = Column(String(length=250))
    last_name = Column(String(length=250))
    job_title = Column(String(length=250))
    people = relationship("Violator", back_populates="person", cascade="all, delete")
    def __str__(self):
        return f"Person(first_name='{self.first_name}', middle_name='{self.middle_name}', last_name='{self.last_name}', job_title='{self.job_title}')"
    def __repr__(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"

@mapper_registry.mapped
class PPEClass:
    """
        A mapped class that defines a table that holds classes of PPE for construction.
    """
    __tablename__="ppeclass"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=250))
    detectedppeclasses = relationship("DetectedPPEClass", back_populates="ppeclass")
    def __str__(self):
        return f"PPEClass(id={self.id}, name='{self.name}')"
    def __repr__(self):
        return f"'{self.name}'"

# Associative table for PPEClass and violator
@mapper_registry.mapped
class DetectedPPEClass:
    """
        A mapped class that defines a table that asoociates both PPEClass and Violator.
    """
    __tablename__ = "detectedppeclass"
    id = Column(Integer, primary_key=True)
    violator_id = Column(Integer, ForeignKey("violator.id", ondelete="CASCADE"))
    ppeclass_id = Column(Integer, ForeignKey("ppeclass.id", ondelete="CASCADE"))
    violator = relationship("Violator", back_populates="detectedppeclasses",)
    ppeclass = relationship("PPEClass", back_populates="detectedppeclasses")
    def __str__(self):
        return f"DetectedPPEClass(violator='{self.violator}',ppeclass='{self.ppeclass}')"
    def __repr__(self):
        return f"{self.ppeclass}"

@mapper_registry.mapped
class Violator:
    """
        A mapped class that defines a table which contains information about the violator and its detected PPE classes.
    """
    __tablename__="violator"
    id = Column(Integer, primary_key=True)
    x1 = Column(Integer)
    y1 = Column(Integer)
    x2 = Column(Integer)
    y2 = Column(Integer)
    person_id = Column(Integer, ForeignKey("person.id", ondelete="CASCADE"))
    person = relationship("Person", back_populates="people")
    detectedppeclasses = relationship("DetectedPPEClass", back_populates="violator", cascade="all, delete")
    violationdetails_id = Column(Integer, ForeignKey("violationdetails.id", ondelete="CASCADE"))
    violationdetails = relationship("ViolationDetails", back_populates="violators")
    def __str__(self):
        return f"Violator(id={self.id}, name='{self.person}', detectedppeclasses={self.detectedppeclasses})"
    def __repr__(self):
        return f"{self.person}"

@mapper_registry.mapped
class ViolationDetails:
    __tablename__ = "violationdetails"
    id = Column(Integer, primary_key=True)
    image = Column(String(length=250))
    violators = relationship("Violator", back_populates="violationdetails", cascade="all, delete")
    timestamp = Column(DateTime, default=datetime.now())
    def __str__(self):
        return f"ViolationDetails(id={self.id},image='{self.image}',violators='{self.violators}',timestamp={self.timestamp})"
    def __repr__(self):
        return f"ViolationDetails(id={self.id},image='{self.image}',violators='{self.violators}',timestamp={self.timestamp})"
