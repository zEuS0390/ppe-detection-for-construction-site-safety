from sqlalchemy.orm import registry, relationship
from sqlalchemy import (
    Column, Integer, 
    String, DateTime, 
    ForeignKey
)

mapper_registry = registry()

@mapper_registry.mapped
class PPEClass:
    __tablename__="ppeclass"
    ppeclass_id = Column(Integer, primary_key=True)
    name = Column(String(length=250))
    def __str__(self):
        return f"PPEClass(id='{self.id}', name='{self.name}')"

@mapper_registry.mapped
class Violator:
    __tablename__="violator"
    violator_id = Column(Integer, primary_key=True)
    name = Column(String(length=250))
    position = Column(Integer)
    detectedppeclasses = Column(Integer, ForeignKey("ppeclass.ppeclass_id"))
    detectedppeclasses = relationship("PPEClass")
    violationdetails_id = Column(Integer, ForeignKey("violationdetails.violationdetails_id", ondelete="CASCADE"))
    violationdetails = relationship("ViolationDetails", back_populates="violators")
    def __str__(self):
        return f"Violator(id={self.id}, name='{self.name}', position='{self.position}', ppeclasses='{self.ppeclasses}')"

@mapper_registry.mapped
class ViolationDetails:
    __tablename__ = "violationdetails"
    violationdetails_id = Column(Integer, primary_key=True)
    image = Column(String(length=250))
    violators = relationship("Violator", back_populates="violationdetails", cascade="all, delete")
    timestamp = Column(DateTime)
    def __str__(self):
        return f"ViolationDetails(id={self.id},image='{self.image}',detected_ppe='{self.violators}')"