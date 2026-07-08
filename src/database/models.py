from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class App(Base):
    __tablename__ = "apps"
    
    id = Column(String(36), primary_key=True)
    app_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(255))
    bundle_id = Column(String(255))
    category = Column(String(100))
    country = Column(String(10))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    reviews = relationship("Review", back_populates="app")
    version_plans = relationship("VersionPlan", back_populates="app")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(String(36), primary_key=True)
    review_id = Column(String(255), unique=True, nullable=False)
    app_id = Column(String(36), ForeignKey("apps.id"))
    username = Column(String(255))
    rating = Column(Integer)
    title = Column(Text)
    content = Column(Text)
    version = Column(String(50))
    country = Column(String(10))
    sentiment_score = Column(Float)
    sentiment_label = Column(String(20))
    category = Column(String(50))
    source = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    app = relationship("App", back_populates="reviews")
    requirements = relationship("Requirement", secondary="requirement_review", back_populates="reviews")

class Requirement(Base):
    __tablename__ = "requirements"
    
    id = Column(String(36), primary_key=True)
    req_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(255))
    description = Column(Text)
    type = Column(String(20))
    priority = Column(Integer)
    impact = Column(String(10))
    effort = Column(String(10))
    plan_id = Column(String(36), ForeignKey("version_plans.id"))
    created_at = Column(DateTime, default=datetime.now)
    
    plan = relationship("VersionPlan", back_populates="requirements")
    reviews = relationship("Review", secondary="requirement_review", back_populates="requirements")
    test_cases = relationship("TestCase", back_populates="requirement")

class RequirementReview(Base):
    __tablename__ = "requirement_review"
    
    requirement_id = Column(String(36), ForeignKey("requirements.id"), primary_key=True)
    review_id = Column(String(36), ForeignKey("reviews.id"), primary_key=True)

class VersionPlan(Base):
    __tablename__ = "version_plans"
    
    id = Column(String(36), primary_key=True)
    version = Column(String(50))
    focus = Column(String(255))
    app_id = Column(String(36), ForeignKey("apps.id"))
    status = Column(String(20), default="draft")
    created_at = Column(DateTime, default=datetime.now)
    
    app = relationship("App", back_populates="version_plans")
    requirements = relationship("Requirement", back_populates="plan")

class TestCase(Base):
    __tablename__ = "test_cases"
    
    id = Column(String(36), primary_key=True)
    test_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(255))
    description = Column(Text)
    test_type = Column(String(20))
    priority = Column(String(10))
    steps = Column(JSON)
    expected_result = Column(Text)
    requirement_id = Column(String(36), ForeignKey("requirements.id"))
    created_at = Column(DateTime, default=datetime.now)
    
    requirement = relationship("Requirement", back_populates="test_cases")

class AnalysisSummary(Base):
    __tablename__ = "analysis_summaries"
    
    id = Column(String(36), primary_key=True)
    app_id = Column(String(36), ForeignKey("apps.id"))
    distribution = Column(JSON)
    key_issues = Column(JSON)
    feature_requests = Column(JSON)
    trends = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    
    app = relationship("App")
