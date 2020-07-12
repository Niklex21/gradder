from app import db


class Subscriber:
    def __init__(self, email: str, ID: str = ''):
        self.email = email
        self.ID = ID
    
    def __repr__(self):
        return f'<Subscriber { self.ID }>'
    
    def to_dict(self):
        return {
            '_id': self.ID,
            'email': self.email
        }
    
    def to_json(self):
        return self.to_dict()

    @staticmethod
    def from_dict(dictionary: dict):
        return Subscriber(**dictionary)

    def add(self):
        try:
            self.ID = db.subscribers.insert_one(self.to_dict()).inserted_id
            # TODO: logger
            return True
        except BaseException as e:
            # TODO: logger
            return False

    def update(self, email: str):
        try:
            db.subscribers.find_one_and_update({"_id": self.ID}, {"$set": {"email": self.email}})
            # TODO: logger
            return True
        except BaseException as e:
            # TODO: logger
            return False
    
    def remove(self):
        try:
            db.subscribers.delete_one({"_id": self.ID})
            # TODO: logger
            return True
        except BaseException as e:
            # TODO: logger
            return False