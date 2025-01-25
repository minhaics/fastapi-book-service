class Parent:
    @staticmethod
    def greet(self):
        print("Hello from Parent!", self)
        
class Child(Parent):
    @staticmethod
    def greet(self):
        print("Hello from Child!")
        super().greet(self)  
        
class Person(Child):
    pass

Child.greet(Person())
