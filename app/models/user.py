from app import db

class User(db.Model):
    id 	 = db.Column(db.Integer, primary_key=True)

    def roles(self):
        return []
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return 1
