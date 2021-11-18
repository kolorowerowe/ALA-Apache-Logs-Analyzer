from fastapi import FastAPI
import uvicorn
import os
import sys

currentdir = os.path.dirname(__file__)
print(currentdir)
sys.path.insert(0, currentdir)

from reader import file_reader

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}




if __name__ == '__main__':
    print('ALA is starting... ')

    file_reader.read_logs_file()
    #file_reader.read_logs_file('short1')

    uvicorn.run(app, host="0.0.0.0", port=8000)


