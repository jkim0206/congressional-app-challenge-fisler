from cmath import log
from venv import create
import firebase_admin
from firebase_admin import db
from tabulate import tabulate

cred_obj = firebase_admin.credentials.Certificate("academic-ly-private-key.json")
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': "https://academic-ly-default-rtdb.firebaseio.com/"
    })

global ref
global username
global password
global log_in_status
global classes
global assignments

ref = db.reference("/")
classes = []
log_in_status = False

def giveOptions(*options):
    i = 0
    print("\nWhat would you like to do?\n")
    for option in options: 
        print(f"{i+1}) {option}")
        i += 1

    while True:
        try:
            option = int(input("\n"))
            if 0 < option <= i:
                break
            raise Exception()
        except:
            print(f"\nHm, that answer doesn't seem valid. Make sure your answer is a number between 1 and {i}. Here's the options again:\n")
            i = 1
            for option in options: print(f"{i}) {option}"); i += 1

    return option

def createUser(username, password, classes):
    ref = db.reference("/" + username)
    ref.set({
        'password': password,
    })
    for subject in classes:
        ref.child("classes").child(subject).child("weights").update({"main":1})

def createAssignment(username, subject, name, pointsEarned, totalPoints):
    ref = db.reference(f"/{username}/classes/{subject}/{name}")
    score = round(pointsEarned/totalPoints, 3)
    if 0 <= score < 0.6:
        grade = "F"
    
    elif 0.6 <= score < 0.7:
        grade = "D"

    elif 0.7 <= score < 0.8:
        grade = "C"

    elif 0.8 <= score < 0.9:
        grade = "B"

    elif 0.9 <= score:
        grade = "A"

    else:
        grade = "An error has occured."

    ref.set({
        'pointsEarned': pointsEarned,
        'totalPoints': totalPoints,
        'score': score,
        'grade': grade
    })

def createCategory(username, subject, name, weight):
    pass

def validateNum(question, onError, checkInt, lowerRange=None, higherRange=None):
    while True:
        try:
            if checkInt:
                answer = int(input(question))
            else:
                answer = float(input(question))

            if lowerRange != None and higherRange != None:
                if lowerRange < answer < higherRange:
                    break

            elif lowerRange != None and higherRange == None:
                if lowerRange < answer:
                    break

            elif lowerRange == None and higherRange != None:
                if answer < higherRange:
                    break

            else:
                break
            
            raise Exception()
        except:
            print(onError)

    return answer

def validateInput(question, onError, disabledCharacters, disabledWords):
    while True:
        option = input(question)
        try:
            for i in disabledCharacters:
                if i in option:
                    raise Exception()
            for i in disabledWords:
                if i == option:
                    raise Exception()

            break
        except:
            print(f"\n{onError}")

    return option

def getAssignments(username, subject):
    data = [["Name", "Grade", "Points Earned", "Total Points", "Percent"]]
    for i in ref.child(subject).get():
        if i == "weights":
            continue
        tempRef = db.reference(f"/{username}/classes/{subject}/{i}")
        while True:
            try:
                assignment = [i, tempRef.get()["grade"], tempRef.get()["pointsEarned"], tempRef.get()["totalPoints"], "{:.1%}".format(tempRef.get()["score"])]
                break
            except:
                continue

        data.append(assignment)

    return "\n" + tabulate(data, headers='firstrow')

def getTotalGrade(username, subject, percent):
    pointsEarned = 0
    totalPoints = 0
    for i in ref.child(subject).get():
        if i == "weights":
            continue
        tempRef = db.reference(f"/{username}/classes/{subject}/{i}")
        pointsEarned += int(tempRef.get()["pointsEarned"])
        totalPoints += int(tempRef.get()["totalPoints"])

    try: 
        return "{:.1%}".format(pointsEarned/totalPoints) if percent else pointsEarned/totalPoints
    except ZeroDivisionError:
        return "--"

def getPoints(username, subject):
    pointsEarned = 0
    totalPoints = 0
    for i in ref.child(subject).get():
        if i == "weights":
            continue
        tempRef = db.reference(f"/{username}/classes/{subject}/{i}")
        pointsEarned += int(tempRef.get()["pointsEarned"])
        totalPoints += int(tempRef.get()["totalPoints"])
    
    return (pointsEarned, totalPoints)


print("Welcome to Academic.ly!")
print("Created by Joshua Kim and Kevin Luo.\n")

while True:
    choice = giveOptions("Log In", "Sign Up")

    match choice:
        case 1:
            while True:
                username = input("\nUsername: ")
                password = input("Password: ")
                if username in ref.get() and password == ref.child(username).get()["password"]:
                    print("\nYou're logged in!")
                    log_in_status = True
                    break

                elif username in ref.get() and password != ref.child(username).get()["password"]:
                    print("\nIncorrect password. Try again.")

                elif username not in ref.get():
                    print(f"\nThe account {username} does not exist. Do you need to create a new account?")

                option = giveOptions("Go Home", "Try Again")

                match option:
                    case 1:
                        break
                    case 2:
                        continue

        case 2:
            while True:
                username = input("\nWhat would you like your username to be? Please note that spaces and forward slashes are not allowed. ")
                if " " in username:
                    print("\nSpaces are not allowed. Please choose a different username.")

                elif "/" in username:
                    print("\nSlashes are not allowed. Please choose a different username.")

                elif username in ref.get():
                    print("\nThis username is taken. Please choose a different username. It's possible you might already have an account.")
                    option = giveOptions("Go Home", "Try Again")

                    match option:
                        case 1:
                            break
                        case 2:
                            continue

                else: 
                    break
            
            while True: 
                password = input("\nWhat would you like your password to be? Please note that spaces and forward slashes are not allowed. ")

                if " " in password:
                    print("\nSpaces are not allowed. Please choose a different password.")

                elif "/" in password:
                    print("\nSlashes are not allowed. Please choose a different username.")

                else: 
                    break
            
            classNum = validateNum("\nHow many classes do you have? ", "Make sure your answer is a number.", True)
            classList = []
            for i in range(classNum):
                classList.append(input(f"What is your {i+1} class? "))

            createUser(username, password, classList)

            print("\nYour account has been created! Please log in with your new account.")

    if log_in_status:
        break
    else:
        continue

print(f"\nWelcome, {username}!")
ref = db.reference(f"/{username}/classes")

for item in ref.get():
    classes.append(item)

while True:
    option = giveOptions(*classes, "Settings", "User Guide")

    match option:
        case option if option <= len(classes):
            subject = classes[int(option-1)]
            assignments = []
            for item in ref.child(subject).get():
                assignments.append(item)

            while True:
                print("\nTotal grade:", getTotalGrade(username, subject, True))
                print("\n", getAssignments(username, subject))
                option = giveOptions("Add assignment", "Delete assignment", "How many points will I need to get a __?")
                match option:
                    case 1:
                        name = validateInput("\nWhat is the name of your assignment? It cannot contain slashes. ", 
                        f"It looks like you either have a slash in your name or already have an assignment named this.", 
                        ["/"], ["weights"] + assignments)
                        pointsEarned = validateNum("How many points did you earn? ", "Make sure your answer is a number is 0 or greater.", True, 0)
                        totalPoints = validateNum("How many points was this assignment worth? ", "Make sure your answer is a number is 0 or greater.", True, 0)
                        createAssignment(username, subject, name, pointsEarned, totalPoints)

                    case 2:
                        name = validateInput("\nWhat assignment would you like to delete? It cannot contain slashes. ", 
                        f"It looks like you have a slash in your name.", 
                        ["/"], ["weights"])
                        ref.child(subject).child(name).set({})

                    case 3:
                        grade = validateNum("\nWhat do you need your final grade to be? Please do not include the percent sign (Ex: 98% becomes just 98) ", 
                        "Make sure you have put in a number that's 0 or above.", True, 0)
                        points = validateNum("How many points is your next assignment worth? ", 
                        "Make sure you have put in a number that's 0 or above", True, 0)

                        pt1, pt2 = getPoints(username, subject)

                        pt2 += points
                        print(grade/100*pt2-pt1)
                        

