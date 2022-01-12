from fastapi import FastAPI
from pydantic import BaseModel
from threading import Thread
import time 
from main import *





#Start das threads        
mainThread = Thread(target=main_code)
mainThread.daemon = True
mainThread.start()

'''
sensorThread = Thread(target=sensor_data)
sensorThread.daemon = True
sensorThread.start()
'''

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/about")
def about():
    return {"Data": "about"}



