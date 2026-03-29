"""
Database Models for CRM Digital FTE
SQLAlchemy ORM models for PostgreSQL database
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey, DECIMAL, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()


# ==================== CUSTOMERS ====================
class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True)
    phone = Column(String(20), unique=True)
    name = Column(String(255), nullable=False)
    company = Column(String(255))
    country = Column(String(100))
    timezone = Column(String(50), default='UTC')
    language = Column(String(10), default='en')
    customer_type = Column(String(50), default='individual')
    status = Column(String(20), default='active')
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    tickets = relationship('Ticket', back_populates='customer', cascade='all, delete-orphan')
    conversations = relationship('Conversation', back_populates='customer', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Customer {self.name} ({self.email})>"


# ==================== TICKETS ====================
class Ticket(Base):
    __tablename__ = 'tickets'
    
    id = Column(String(50), primary_key=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id', ondelete='CASCADE'))
    subject = Column(String(500), nullable=False)
    description = Column(Text)
    status = Column(String(50), default='open')
    priority = Column(String(20), default='medium')
    escalation_level = Column(String(10), default='L1')
    escalation_reason = Column(Text)
    assigned_to = Column(String(255))
    resolved_by = Column(String(255))
    resolution_summary = Column(Text)
    channel = Column(String(20), nullable=False)
    source = Column(String(100))
    tags = Column(ARRAY(String))
    sla_deadline = Column(DateTime(timezone=True))
    sla_status = Column(String(20), default='on_track')
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))
    
    # Relationships
    customer = relationship('Customer', back_populates='tickets')
    messages = relationship('Message', back_populates='ticket', cascade='all, delete-orphan')
    escalations = relationship('Escalation', back_populates='ticket', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Ticket {self.id} - {self.subject}>"


# ==================== MESSAGES ====================
class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(String(50), ForeignKey('tickets.id', ondelete='CASCADE'))
    sender_type = Column(String(20), nullable=False)  # customer, ai, agent
    sender_id = Column(String(255))
    content = Column(Text, nullable=False)
    content_html = Column(Text)
    channel = Column(String(20), nullable=False)
    message_type = Column(String(20), default='text')
    attachment_urls = Column(ARRAY(String))
    sentiment = Column(String(20))
    sentiment_score = Column(DECIMAL(3, 2))
    is_internal = Column(Boolean, default=False)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    ticket = relationship('Ticket', back_populates='messages')
    
    def __repr__(self):
        return f"<Message {self.id[:8]}... for Ticket {self.ticket_id}>"


# ==================== CONVERSATIONS ====================
class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id', ondelete='CASCADE'))
    ticket_id = Column(String(50), ForeignKey('tickets.id', ondelete='SET NULL'))
    summary = Column(Text)
    overall_sentiment = Column(String(20))
    sentiment_trend = Column(String(20))
    topics = Column(ARRAY(String))
    resolution_status = Column(String(50), default='unresolved')
    customer_satisfaction = Column(Integer)
    feedback = Column(Text)
    duration_seconds = Column(Integer)
    message_count = Column(Integer, default=0)
    metadata = Column(JSONB, default={})
    started_at = Column(DateTime(timezone=True), default=func.now())
    ended_at = Column(DateTime(timezone=True))
    
    # Relationships
    customer = relationship('Customer', back_populates='conversations')
    ticket = relationship('Ticket', back_populates='conversations')
    
    def __repr__(self):
        return f"<Conversation {self.id[:8]}... for Customer {self.customer_id}>"


# ==================== KNOWLEDGE BASE ====================
class KnowledgeBase(Base):
    __tablename__ = 'knowledge_base'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True)
    content = Column(Text, nullable=False)
    content_html = Column(Text)
    category = Column(String(100))
    subcategory = Column(String(100))
    tags = Column(ARRAY(String))
    author = Column(String(255))
    status = Column(String(20), default='draft')
    views = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    embedding = Column('embedding', String)  # Using String for compatibility, use VECTOR(1536) with pgvector
    version = Column(Integer, default=1)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('knowledge_base.id'))
    metadata = Column(JSONB, default={})
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<KnowledgeBase {self.title}>"


# ==================== ESCALATIONS ====================
class Escalation(Base):
    __tablename__ = 'escalations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(String(50), ForeignKey('tickets.id', ondelete='CASCADE'))
    from_level = Column(String(10), nullable=False)
    to_level = Column(String(10), nullable=False)
    reason = Column(Text, nullable=False)
    triggered_by = Column(String(50), nullable=False)
    triggered_by_id = Column(String(255))
    assigned_to = Column(String(255))
    status = Column(String(20), default='pending')
    priority = Column(String(20), default='medium')
    notes = Column(Text)
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    ticket = relationship('Ticket', back_populates='escalations')
    
    def __repr__(self):
        return f"<Escalation {self.id[:8]}... for Ticket {self.ticket_id}>"


# ==================== CHANNEL CONFIGS ====================
class ChannelConfig(Base):
    __tablename__ = 'channel_configs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_name = Column(String(50), nullable=False, unique=True)
    enabled = Column(Boolean, default=True)
    config = Column(JSONB, nullable=False, default={})
    webhook_url = Column(String(500))
    last_sync_at = Column(DateTime(timezone=True))
    status = Column(String(20), default='active')
    error_message = Column(Text)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ChannelConfig {self.channel_name}>"


# ==================== ANALYTICS ====================
class Analytics(Base):
    __tablename__ = 'analytics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False)
    event_data = Column(JSONB, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    ticket_id = Column(String(50), ForeignKey('tickets.id'))
    channel = Column(String(20))
    metric_name = Column(String(100))
    metric_value = Column(DECIMAL(10, 2))
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    def __repr__(self):
        return f"<Analytics {self.event_type} at {self.created_at}>"


# ==================== AGENTS ====================
class Agent(Base):
    __tablename__ = 'agents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default='support')
    team = Column(String(100))
    escalation_level = Column(String(10), default='L2')
    max_concurrent_tickets = Column(Integer, default=10)
    status = Column(String(20), default='active')
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Agent {self.name} ({self.email})>"


# ==================== SLA CONFIG ====================
class SLAConfig(Base):
    __tablename__ = 'sla_config'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    priority = Column(String(20), nullable=False, unique=True)
    first_response_minutes = Column(Integer, nullable=False)
    resolution_hours = Column(Integer, nullable=False)
    business_hours_only = Column(Boolean, default=False)
    description = Column(Text)
    
    def __repr__(self):
        return f"<SLAConfig {self.priority}>"


# ==================== DATABASE CONNECTION ====================

def get_database_url() -> str:
    """Get database URL from environment or return default"""
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    return os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/crm_digital_fte'
    )


def create_engine_and_session():
    """Create SQLAlchemy engine and session"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return engine, SessionLocal


# Create all tables
def init_db():
    """Initialize database - create all tables"""
    from sqlalchemy import create_engine
    from dotenv import load_dotenv
    load_dotenv()
    import os
    
    engine = create_engine(get_database_url())
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


if __name__ == '__main__':
    init_db()
