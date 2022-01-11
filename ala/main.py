from fastapi import FastAPI
import uvicorn
import os
import sys
import time

currentdir = os.path.dirname(__file__)
sys.path.insert(0, currentdir)

from reader import file_reader
from report.EmailClient import EmailClient
from ALparser.ALParser import ApacheLogParser
from MLs.Checker import Checker
from visualizer.graph_visualizer import GraphVisualizer

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    print('ALA is starting... ')

    # Reading & preprocessing logs
    ALparser = ApacheLogParser()
    file_reader.read_logs_file(ALparser, 'apache_logs1_1000')

    print('ML Formatter starting')
    start = time.time()
    mldf = ALparser.getMLFormattedLogs()
    mldf.to_csv("result/ml_logs.csv")
    end = time.time()
    print('ML Formatter finished')
    print(f"Finished. Ml formatting took: {end-start}s")

    print('ML prediction starting')
    start = time.time()
    logChecker = Checker(mldf, 'model_01')
    sus_requests = logChecker.predictAndInform()
    end = time.time()
    print('ML prediction finished')
    print(f"Finished. Ml prediction took: {end-start}s")

    email_message = list(sus_requests.values())
    if not email_message:
        email_message = "Wiadomość wygenerowana automatycznie.\nNie wykryto podejrzanych zachowań."
    else:
        email_message.insert(0, "Wiadomość wygenerowana automatycznie.\n\nWykryto podejrzane zahcowania:")
        email_message = "\n".join(email_message)

    print(email_message)

    #Graph
    graphVisualizer = GraphVisualizer(ALparser.getVisualizationFormattedLogs())
    relative_img_path = graphVisualizer.generateBaseGraph()

    # Sending email with graph
    emailClient = EmailClient()
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    abs_file_path = os.path.join(script_dir, relative_img_path)
    emailClient.send_message("[ALA] Wizualizacja logów", email_message, [relative_img_path])

    # rest endpoint is not usable now
    # uvicorn.run(app, host="0.0.0.0", port=8000)

    print('My job for now is done!')

