class Person:
    def __init__(self, firstName, lastName, idNumber):
        self.firstName = firstName
        self.lastName = lastName
        self.idNumber = idNumber

    def printPerson(self):
        print("Name:", self.lastName + ",", self.firstName)
        print("ID:", self.idNumber)


class Student(Person):
    #   Class Constructor
    #
    #   Parameters:
    #   firstName - A string denoting the Person's first name.
    #   lastName - A string denoting the Person's last name.
    #   id - An integer denoting the Person's ID number.
    #   scores - An array of integers denoting the Person's test scores.
    #
    # Write your constructor here
    def __init__(self, firstName, lastName, idNumber, scores):
        super().__init__(firstName, lastName, idNumber)
        self.scores = scores

    #   Function Name: calculate
    #   Return: A character denoting the grade.
    #
    # Write your function here
    def calculate(self):
        # Score is a list; need to add all the elements up and average
        avg_score = int(sum(self.scores) / len(self.scores))
        if 90 <= avg_score <= 100:
            grade = 'O'
        elif 80 <= avg_score < 90:
            grade = 'E'
        elif 70 <= avg_score < 80:
            grade = 'A'
        elif 55 <= avg_score < 70:
            grade = 'P'
        elif 40 <= avg_score < 55:
            grade = 'D'
        elif avg_score < 40:
            grade = 'T'
        return grade


if __name__ == '__main__':
    # line = input().split()
    # firstName = line[0]
    # lastName = line[1]
    # idNum = line[2]
    # numScores = int(input()) # not needed for Python
    # scores = list(map(int, input().split()))
    s1 = Student('Heraldo', 'Memelli', '8135627', [100, 80])
    s1.printPerson()
    print("Grade:", s1.calculate())

    s2 = Student('Aakansha', 'Doshi', '7825621', [31, 32, 34, 35])
    s2.printPerson()
    print("Grade:", s2.calculate())

    s3 = Student('John', 'Smith', '8342756', [67, 75, 83, 73])
    s3.printPerson()
    print("Grade:", s3.calculate())