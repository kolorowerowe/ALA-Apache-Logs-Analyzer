from fastapi import FastAPI
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
from config import Configuration

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    Configuration.load()
    Configuration.ALAprint('ALA is starting... ', 0)

    # Reading & preprocessing logs
    ALparser = ApacheLogParser()
    file_reader.read_logs_file(ALparser, Configuration.logs)

    Configuration.ALAprint('ML Formatter starting', 1)
    start = time.time()
    mldf = ALparser.getMLFormattedLogs()
    if Configuration.verbosityCheck(1):
        mldf.to_csv(Configuration.resultDir + Configuration.mldf_csv)
    end = time.time()
    Configuration.ALAprint('ML Formatter finished', 1)
    Configuration.ALAprint(f"Finished. Ml formatting took: {end-start}s", 2)

    Configuration.ALAprint('ML prediction starting', 1)
    start = time.time()
    logChecker = Checker(mldf, Configuration.model)
    sus_requests = logChecker.predictAndInform()
    end = time.time()
    Configuration.ALAprint('ML prediction finished', 1)
    Configuration.ALAprint(f"Finished. Ml prediction took: {end-start}s", 2)

    email_message = [item for sublist in list(sus_requests.values()) for item in sublist]
    if not email_message:
        email_message = "Wiadomość wygenerowana automatycznie.\nNie wykryto podejrzanych zachowań."
    else:
        email_message.insert(0, "Wiadomość wygenerowana automatycznie.\n\nWykryto podejrzane zahcowania:")
        email_message = "\n".join(email_message)

    Configuration.ALAprint(email_message, 3)

    #Graph
    graphVisualizer = GraphVisualizer(ALparser.getVisualizationFormattedLogs())
    relative_img_path = graphVisualizer.generateBaseGraph()
    graphVisualizer.applyPredictions(sus_requests)

    # Sending email with graph
    emailClient = EmailClient()
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    abs_file_path = os.path.join(script_dir, relative_img_path)
    emailClient.send_message("[ALA] Wizualizacja logów", email_message, [relative_img_path])

    Configuration.ALAprint('My job for now is done!', 0)

