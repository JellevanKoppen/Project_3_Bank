values = "0123456789ABCD*#"

def checkKey(k):
    if(k in values):
        print("Good value")
    else:
        print("Wrong Value!")

while True:
    result = input("Key: ")
    checkKey(result)
