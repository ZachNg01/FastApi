from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Student Information
    student_id = Column(String(50), nullable=True)
    program = Column(String(100), nullable=False)
    semester = Column(String(50), nullable=False)
    
    # Survey Questions (1-5 scale)
    instructor_effectiveness = Column(Integer, nullable=False)
    curriculum_quality = Column(Integer, nullable=False)
    facility_rating = Column(Integer, nullable=False)
    equipment_quality = Column(Integer, nullable=False)
    support_services = Column(Integer, nullable=False)
    overall_satisfaction = Column(Integer, nullable=False)
    
    # Open-ended feedback
    positive_comments = Column(Text)
    improvement_suggestions = Column(Text)
    additional_comments = Column(Text)
    
    # Demographic info (optional)
    age_group = Column(String(20))
    prior_experience = Column(String(50))
    
    # Contact permission
    follow_up_permission = Column(Boolean, default=False)

    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "student_id": self.student_id,
            "program": self.program,
            "semester": self.semester,
            "instructor_effectiveness": self.instructor_effectiveness,
            "curriculum_quality": self.curriculum_quality,
            "facility_rating": self.facility_rating,
            "equipment_quality": self.equipment_quality,
            "support_services": self.support_services,
            "overall_satisfaction": self.overall_satisfaction,
            "positive_comments": self.positive_comments,
            "improvement_suggestions": self.improvement_suggestions,
            "additional_comments": self.additional_comments,
            "age_group": self.age_group,
            "prior_experience": self.prior_experience,
            "follow_up_permission": self.follow_up_permission
        }