from sqlalchemy import Column, Integer, String, JSON
from database import Base

class ForensicTool(Base):
    __tablename__ = "forensic_tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    vendor = Column(String, nullable=False)
    capability_tags = Column(JSON, nullable=False) 
    jurisdictional_legality = Column(String, nullable=False)
    evidentiary_admissibility = Column(String, nullable=False)
    cost_and_licensing = Column(String, nullable=False)
    access_restrictions = Column(String, nullable=False)
    skill_level = Column(String, nullable=False)
    platform_and_integration = Column(String, nullable=False)
    last_verified = Column(String, nullable=False)
    documentation_and_support = Column(String, nullable=False)
    additional_metadata = Column(JSON, nullable=True)
    url = Column(String, nullable=True)
    region = Column(String, nullable=True)
    investigation_type = Column(String, nullable=True)

    def __repr__(self):
        return f"<ForensicTool(name='{self.name}', vendor='{self.vendor}')>"