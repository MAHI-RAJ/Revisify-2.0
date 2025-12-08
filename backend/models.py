"""SQLAlchemy models for Revisify 2.0"""
from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

class User(db.Model):
    """User model"""
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = db.relationship("Document", back_populates="user", lazy="dynamic")
    attempts = db.relationship("Attempt", back_populates="user", lazy="dynamic")
    step_progresses = db.relationship("StepProgress", back_populates="user", lazy="dynamic")
    hints = db.relationship("Hint", back_populates="user", lazy="dynamic")
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        """Generate email verification token"""
        self.verification_token = secrets.token_urlsafe(32)
        return self.verification_token

class Document(db.Model):
    """Document model"""
    __tablename__ = "documents"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))  # pdf, pptx, docx
    status = db.Column(db.String(50), default="processing")  # processing, ready, error
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", back_populates="documents")
    chunks = db.relationship("Chunk", back_populates="document", lazy="dynamic")
    concepts = db.relationship("Concept", back_populates="document", lazy="dynamic")
    roadmap_steps = db.relationship("RoadmapStep", back_populates="document", lazy="dynamic")
    prereq_edges = db.relationship("PrereqEdge", back_populates="document", lazy="dynamic")

class Chunk(db.Model):
    """Text chunk model"""
    __tablename__ = "chunks"
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False)
    chunk_text = db.Column(db.Text, nullable=False)
    page_number = db.Column(db.Integer)
    slide_number = db.Column(db.Integer)
    chunk_index = db.Column(db.Integer)  # Order within document
    embedding = db.Column(db.PickleType)  # Store embedding vector
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    document = db.relationship("Document", back_populates="chunks")

class Concept(db.Model):
    """Concept model"""
    __tablename__ = "concepts"
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    canonical_name = db.Column(db.String(255))  # For deduplication
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    document = db.relationship("Document", back_populates="concepts")
    roadmap_steps = db.relationship("RoadmapStep", back_populates="concept", lazy="dynamic")
    prereq_edges_as_concept = db.relationship("PrereqEdge", foreign_keys="PrereqEdge.concept_id", back_populates="concept", lazy="dynamic")
    prereq_edges_as_prereq = db.relationship("PrereqEdge", foreign_keys="PrereqEdge.prerequisite_id", back_populates="prerequisite", lazy="dynamic")

class PrereqEdge(db.Model):
    """Prerequisite relationship model"""
    __tablename__ = "prereq_edges"
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False)
    concept_id = db.Column(db.Integer, db.ForeignKey("concepts.id"), nullable=False)
    prerequisite_id = db.Column(db.Integer, db.ForeignKey("concepts.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    document = db.relationship("Document", back_populates="prereq_edges")
    concept = db.relationship("Concept", foreign_keys=[concept_id], back_populates="prereq_edges_as_concept")
    prerequisite = db.relationship("Concept", foreign_keys=[prerequisite_id], back_populates="prereq_edges_as_prereq")
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint("concept_id", "prerequisite_id", name="unique_prereq_edge"),)

class RoadmapStep(db.Model):
    """Roadmap step model"""
    __tablename__ = "roadmap_steps"
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False)
    concept_id = db.Column(db.Integer, db.ForeignKey("concepts.id"), nullable=False)
    order = db.Column(db.Integer, nullable=False)  # Order in roadmap
    step_type = db.Column(db.String(50), default="concept")  # concept, prerequisite
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    document = db.relationship("Document", back_populates="roadmap_steps")
    concept = db.relationship("Concept", back_populates="roadmap_steps")
    mcq_sets = db.relationship("MCQSet", back_populates="roadmap_step", lazy="dynamic")
    step_progresses = db.relationship("StepProgress", back_populates="roadmap_step", lazy="dynamic")
    hints = db.relationship("Hint", back_populates="roadmap_step", lazy="dynamic")

class MCQSet(db.Model):
    """MCQ set model"""
    __tablename__ = "mcq_sets"
    
    id = db.Column(db.Integer, primary_key=True)
    roadmap_step_id = db.Column(db.Integer, db.ForeignKey("roadmap_steps.id"), nullable=False)
    question_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    roadmap_step = db.relationship("RoadmapStep", back_populates="mcq_sets")
    mcqs = db.relationship("MCQ", back_populates="mcq_set", lazy="dynamic")
    attempts = db.relationship("Attempt", back_populates="mcq_set", lazy="dynamic")

class MCQ(db.Model):
    """MCQ question model"""
    __tablename__ = "mcqs"
    
    id = db.Column(db.Integer, primary_key=True)
    mcq_set_id = db.Column(db.Integer, db.ForeignKey("mcq_sets.id"), nullable=False)
    question_number = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text)
    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, or D
    explanation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    mcq_set = db.relationship("MCQSet", back_populates="mcqs")

class Attempt(db.Model):
    """MCQ attempt model"""
    __tablename__ = "attempts"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mcq_set_id = db.Column(db.Integer, db.ForeignKey("mcq_sets.id"), nullable=False)
    score = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    correct_count = db.Column(db.Integer, nullable=False)
    total_count = db.Column(db.Integer, nullable=False)
    answers_json = db.Column(db.Text)  # Store answers as JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", back_populates="attempts")
    mcq_set = db.relationship("MCQSet", back_populates="attempts")

class StepProgress(db.Model):
    """Step progress model"""
    __tablename__ = "step_progress"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    roadmap_step_id = db.Column(db.Integer, db.ForeignKey("roadmap_steps.id"), nullable=False)
    concept_id = db.Column(db.Integer, db.ForeignKey("concepts.id"))
    status = db.Column(db.String(50), default="locked")  # locked, unlocked, cleared
    mastery_score = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", back_populates="step_progresses")
    roadmap_step = db.relationship("RoadmapStep", back_populates="step_progresses")
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint("user_id", "roadmap_step_id", name="unique_user_step_progress"),)

class Hint(db.Model):
    """Hint model"""
    __tablename__ = "hints"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    roadmap_step_id = db.Column(db.Integer, db.ForeignKey("roadmap_steps.id"), nullable=False)
    hint_number = db.Column(db.Integer, nullable=False)  # 1, 2, or 3
    hint_text = db.Column(db.Text, nullable=False)
    micro_question = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", back_populates="hints")
    roadmap_step = db.relationship("RoadmapStep", back_populates="hints")

class Note(db.Model):
    """Note/explanation model"""
    __tablename__ = "notes"
    
    id = db.Column(db.Integer, primary_key=True)
    roadmap_step_id = db.Column(db.Integer, db.ForeignKey("roadmap_steps.id"), nullable=False)
    summary = db.Column(db.Text)
    explanation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    roadmap_step = db.relationship("RoadmapStep", lazy="dynamic")

class Flashcard(db.Model):
    """Flashcard model"""
    __tablename__ = "flashcards"
    
    id = db.Column(db.Integer, primary_key=True)
    roadmap_step_id = db.Column(db.Integer, db.ForeignKey("roadmap_steps.id"), nullable=False)
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)
    card_order = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    roadmap_step = db.relationship("RoadmapStep", lazy="dynamic")

