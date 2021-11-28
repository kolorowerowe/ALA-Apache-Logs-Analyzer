from fastapi import FastAPI
import uvicorn
import os
import sys

currentdir = os.path.dirname(__file__)
sys.path.insert(0, currentdir)

from reader import file_reader
from report.EmailClient import EmailClient
from ALparser.ALParser import ApacheLogParser
from visualizer.graph_visualizer import GraphVisualizer

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    print('ALA is starting... ')

    # Reading & preprocessing logs
    ALparser = ApacheLogParser()
    # file_reader.read_logs_file(ALparser)
    file_reader.read_logs_file(ALparser, 'apache_logs1_1000')

    #Graph
    graphVisualizer = GraphVisualizer(ALparser.getVisualizationFormattedLogs())
    relative_img_path = graphVisualizer.generateBaseGraph()

    # Sending email with graph
    emailClient = EmailClient()
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    abs_file_path = os.path.join(script_dir, relative_img_path)
    emailClient.send_message("[ALA] Wizualizacja logów", "Wiadomość wygenerowana automatycznie.", [abs_file_path])

    # rest endpoint is not usable now
    # uvicorn.run(app, host="0.0.0.0", port=8000)

    print('My job for now is done!')

