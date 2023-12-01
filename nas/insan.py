class Insan:
    def __init__(self, id, name, birthdate, gender):
        self.id = id
        self.name = name
        self.birthdate = birthdate
        self.gender = gender
        self.parents = []  # List of Insan objects representing the parents
        self.children = []  # List of Insan objects representing the children
    
    def add_parent(self, parent):
        self.parents.append(parent)
    
    def add_child(self, child):
        self.children.append(child)