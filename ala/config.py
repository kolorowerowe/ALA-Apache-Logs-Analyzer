import yaml
import os

class Configuration:
    logs = '-'
    model = '-'
    mldf_csv = '-'
    logscounter_csv = '-'
    bad_users = '-'
    bad_referers = '-'
    resultDir = 'result/'
    modelDir = 'models/'
    dataDir = 'data/'
    testDir = 'data/test/'
    email_address = '-'
    email_password = '-'
    email_recipients = []
    extensionsToRemove = []
    flow_max = 0
    event_max = 0
    verbosity = 0

    def verbosityCheck(req):
        return Configuration.verbosity >= req

    def ALAprint(msg, req):
        if Configuration.verbosityCheck(req):
            print(msg)

    def load():
        with open(os.path.join(os.path.dirname(__file__), "..", "config.yml"), "r") as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
            
            Configuration.logs = cfg['filenames']['logs']
            Configuration.model = cfg['filenames']['model']
            Configuration.mldf_csv = cfg['filenames']['mldf_csv']
            Configuration.logscounter_csv = cfg['filenames']['logscounter_csv']
            Configuration.bad_users = cfg['filenames']['bad_users']
            Configuration.bad_referers = cfg['filenames']['bad_referers']
            Configuration.email_address = cfg['email']['address']
            Configuration.email_password = cfg['email']['password']
            Configuration.email_recipients = cfg['email']['recipients']
            Configuration.extensionsToRemove = cfg['other']['extensionsToRemove']
            Configuration.flow_max = cfg['other']['flow_max']
            Configuration.event_max = cfg['other']['event_max']
            Configuration.verbosity = cfg['other']['verbosity']
