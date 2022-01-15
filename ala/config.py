class Configuration:
    resultDir = 'result/'
    extensionsToRemove = ['css', 'jpg', 'jpeg', 'png', 'gif', 'woff', 'svg', 'ico', 'ttf', 'pdf']
    flow_max = 5
    event_max = 5
    verbosity = 1

    def ALAprint(msg, req):
        if Configuration.verbosity >= req:
            print(msg)
