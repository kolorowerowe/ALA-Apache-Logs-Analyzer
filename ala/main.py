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

    ALparser = ApacheLogParser()
    file_reader.read_logs_file(ALparser)
    # file_reader.read_logs_file('short1')

    #Graph
    graphVisualizer = GraphVisualizer(ALparser.getVisualizationFormattedLogs())
    graphVisualizer.generateBaseGraph()

    # Example of EmailClient usage:
    # emailClient = EmailClient()
    # script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    # relative_file_path = '../data/short1'
    # abs_file_path = os.path.join(script_dir, relative_file_path)
    # emailClient.send_message("Tytuł", "Hej, co tam", [abs_file_path])

    uvicorn.run(app, host="0.0.0.0", port=8000)


