from datetime import datetime
from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Template(db.Model):
    __tablename__ = "templates"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)  # jinja2 source
    owner_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    variables = db.relationship("TemplateVariable", backref="template", cascade="all, delete-orphan")
    generations = db.relationship("Generation", backref="template", cascade="all, delete-orphan")

class TemplateVariable(db.Model):
    __tablename__ = "template_variables"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    template_id = db.Column(db.BigInteger, db.ForeignKey("templates.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), default="string")  # string, number, boolean, enum, json, text
    default_value = db.Column(db.Text)
    required = db.Column(db.Boolean, default=False)
    options = db.Column(db.Text)  # store JSON string if needed
    description = db.Column(db.Text)

    def options_json(self):
        try:
            return json.loads(self.options) if self.options else None
        except Exception:
            return None

class Generation(db.Model):
    __tablename__ = "generations"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    template_id = db.Column(db.BigInteger, db.ForeignKey("templates.id"), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=True)
    input_values = db.Column(db.Text, nullable=False)  # store JSON string
    output_preview = db.Column(db.Text)
    output_path = db.Column(db.String(1024))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
