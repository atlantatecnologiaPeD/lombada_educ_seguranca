from datetime import datetime
now = datetime.now() # current date and time
print("date and time:",now.strftime("%d/%m/%Y %H:%M:%S.%f")[:-3])