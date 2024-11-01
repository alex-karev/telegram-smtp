from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Set up the SQLite database and create a new session
engine = create_engine('sqlite:///storage.db')
Session = sessionmaker(bind=engine)
session = Session()

# Define a base class for the table
Base = declarative_base()

# Define the table
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    email = Column(String, unique=False, nullable=True)

# Create the table in the database
Base.metadata.create_all(engine)

# Function to add new user/change user's email
def update_user(chat_id, email):
    # Try to find an existing user
    user = session.query(User).filter_by(chat_id=chat_id).first()
    # Update user
    if user:
        # Check if email is already taken
        other = session.query(User).filter_by(email=email).first()
        if other and other != user:
            return None
        # Change email
        user.email = email
        session.commit()
        return user
    # Add new user
    new_user = User(chat_id=chat_id, email=email)
    session.add(new_user)
    session.commit()
    return new_user

# Find chat by email
def find_chat(email):
    user = session.query(User).filter_by(email=email).first()
    if not user:
        return False
    return user.chat_id
