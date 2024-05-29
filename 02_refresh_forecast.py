import os




REFRESH = os.getenv('REFRESH')

print(REFRESH)

if REFRESH == "True":
    print("New data is available")
elif REFRESH == "False":
    print("The data is up-to-date")
else: 
    print("The xcom value is invalid, please check the logs")