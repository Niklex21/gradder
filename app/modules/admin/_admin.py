from app import db
from app.logs import user_logger
from app.modules._classes import User, Classes
from app.modules.student._student import Student
from app.modules.teacher._teacher import Teacher
from bson import ObjectId
from re import match
from app.logs import user_logger
import regex 



class Admin(User):
    USERTYPE = 'Admin'

    def __init__(self, email: str, first_name: str, last_name: str, classes: list = None, ID: str = None):
        r"""Creates a user with Admin access

        This class is used for school admins that will have access to managing their school and teachers, 
        but with no access to grades or homework.

        Parameters
        ----------
        email : str
            Admin's email
        first_name : str
            Admin's first name as entered by him/herself
        last_name : str
            Admin's last name as entered by him/herself
        ID : str, optional
            This user's ID, set automatically if not specified
        """
        super().__init__(email=email, first_name=first_name, last_name=last_name, ID=ID)
        self.classes = classes if classes is not None else list()

    def __repr__(self):
        return f'<Admin {self.ID}> '

    def to_json(self):
        json_user = super().to_json()
        return json_user

    def to_dict(self):
        return self.to_json()

    @staticmethod
    def from_dict(dictionary: dict):
        user = Admin(email=dictionary['email'],
                     first_name=dictionary['first_name'],
                     last_name=dictionary['last_name'],
                     ID=str(dictionary['_id']) if '_id' in dictionary else None)
        if 'password' in dictionary:
            user.set_password(dictionary['password'])

        if 'secret_question' in dictionary and 'secret_answer' in dictionary:
            user.set_secret_question(
                dictionary['secret_question'], dictionary['secret_answer'])

        return user

    @staticmethod
    def get_by_id(id: str):
        return Admin.from_dict(super(Admin, Admin).get_by_id(id))

    @staticmethod
    def get_by_name(first_name: str, last_name: str):
        return Admin.from_dict(super(Admin, Admin).get_by_name('Admin', first_name, last_name))

    @staticmethod
    def get_by_email(email: str):
        return Admin.from_dict(super(Admin, Admin).get_by_email(email))

    @staticmethod
    def add_student(class_id: str, email: str):
        student = Student.get_by_email(email)
        
        db.classes.update_one({"_id": ObjectId(class_id)}, {"$push": {"students": ObjectId(student.ID)}})
        

    @staticmethod
    def add_teacher(class_id: str, email: str):
        teacher = Teacher.get_by_email(email)
        db.classes.update_one({"_id": ObjectId(class_id)}, {"$set": {"teacher": ObjectId(teacher.ID)}})

    @staticmethod
    def add_class(classes: Classes):
        try:
            dictionary = classes.to_dict()
            dictionary["_id"] = ObjectId()
            dictionary["students"] = list()
            dictionary["syllabus"] = list()
            dictionary["assignments"] = list()
            db.classes.insert_one(dictionary)
        except BaseException as e:
            print(f"Error while adding class {classes.ID}: {e}")
    
    def get_class_names(self):
        temp = list()
        print("1")

        for document_ in db.classes.find():
            tempstr = document_.get("_id")
            tempobjectid = ObjectId(tempstr)
            temp.append((tempobjectid))
            print("2")
        

        classes = list()
        for class_ in temp:
            classes.append((class_))


        return classes

