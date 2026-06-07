
import bcrypt
from classes.gclass import Gclass


class Userlogin(Gclass):
    """Class for managing user authentication and user groups"""
    
    # Class attributes for storing all user objects
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    
    # Class attributes - id' must be the first one on the List
    att = ['_id', '_user', '_usergroup', '_password']
    
    # Class header title
    header = 'Users'
    
    # Field description for use in forms
    des = ['Id', 'User', 'User group', 'Password']
    
    username = ''
    user_id = 0
    
    def __init__(self, id, user, usergroup, password):
        """
        Constructor: Called when an object is instantiated
        """
        super().__init__(id)
        
        # Object attributes
        self._id = Userlogin.get_id(id)
        self._user = user
        self._usergroup = usergroup
        self._password = password
        
        # Add the new object to the dictionary of objects
        Userlogin.obj[self._id] = self
        
        # Add the code to the list of object codes
        Userlogin.lst.append(self._id)
    
    # id property getter method
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value
    
    # user property getter method
    @property
    def user(self):
        return self._user
    
    # usergroup property getter method
    @property
    def usergroup(self):
        return self._usergroup
    
    @usergroup.setter
    def usergroup(self, usergroup):
        """Set usergroup - must be 'admin' or 'user_only'"""
        if usergroup not in ['admin', 'user_only']:
            raise ValueError("Usergroup must be 'admin' or 'user_only'")
        self._usergroup = usergroup
    
    # password property
    @property
    def password(self):
        return ""
    
    @password.setter
    def password(self, password):
        self._password = password
    
    # ─────────────────────────────
    # Hash and verify password methods
    # ─────────────────────────────
    
    def hash_password(self, password):
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    def verify_password(self, password):
        """Verify if the provided password matches the stored hash"""
        try:
            return bcrypt.checkpw(password.encode("utf-8"), self._password.encode("utf-8"))
        except:
            return False
    
    def set_hashed_password(self, password):
        """Set password by hashing it first"""
        self._password = self.hash_password(password)
    
    # ─────────────────────────────
    # User type checking methods
    # ─────────────────────────────
    
    def is_admin(self):
        """Check if user is admin"""
        return self._usergroup == 'admin'
    
    def is_user_only(self):
        """Check if user is regular user"""
        return self._usergroup == 'user_only'
    
    @staticmethod
    def get_id(id):
        """Get or generate ID"""
        if id is None or id == 0:
            if Userlogin.lst:
                return max(Userlogin.lst) + 1
            return 1
        return id
    
    @classmethod
    def get_user_id(cls, user):
        """Get user_id from a username"""
        user_id = 0
        lsobj = cls.find(user, 'user')
        if len(lsobj) == 1:
            obj = lsobj[0]
            user_id = obj.id
        return user_id
    
    @classmethod
    def chk_password(cls, user, password):
        """Check if password is correct for a given username"""
        cls.username = ''
        user_id = cls.get_user_id(user)
        message = ''
        if user_id != 0:
            obj = cls.obj[user_id]
            valid = bcrypt.checkpw(password.encode("utf-8"), obj._password.encode("utf-8"))
            if valid:
                cls.user_id = obj.id
                cls.username = obj.user
                message = "Valid"
            else:
                message = "Wrong password"
        else:
            message = "No existent user"
        return message
    
    @classmethod
    def set_password(cls, password):
        """Hash and return a password"""
        passencrypted = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return passencrypted.decode()
    
    @staticmethod
    def find(value, attribute='user'):
        """Find objects by attribute value"""
        result = []
        for obj in Userlogin.obj.values():
            if attribute == 'user' and obj._user == value:
                result.append(obj)
            elif attribute == 'id' and obj._id == value:
                result.append(obj)
            elif attribute == 'usergroup' and obj._usergroup == value:
                result.append(obj)
        return result
    
    def __str__(self):
        return f"Id:{self._id}, User:{self._user}, Usergroup:{self._usergroup}"
    
    def __repr__(self):
        return f"Userlogin({self._id}, {self._user}, {self._usergroup})"
    
    def to_dict(self):
        """Convert user to dictionary (without password)"""
        return {
            'id': self._id,
            'user': self._user,
            'usergroup': self._usergroup
        }
