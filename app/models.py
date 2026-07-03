from datetime import datetime

from app import db


class Item(db.Model):
    """Represents a single inventory item held by the retail company."""

    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    barcode = db.Column(db.String(64), unique=True, nullable=True, index=True)
    category = db.Column(db.String(80), nullable=True)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "barcode": self.barcode,
            "category": self.category,
            "description": self.description,
            "quantity": self.quantity,
            "price": self.price,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_from_dict(self, data):
        """Applies a partial update (used by PATCH)."""
        for field in ("name", "barcode", "category", "description", "quantity", "price"):
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return f"<Item {self.id} {self.name!r}>"
