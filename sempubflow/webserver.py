'''
Created on 2023-06-19

@author: wf
'''
from nicegui import ui

class WebServer:
    '''
    webserver 
    '''
    
    def __init__(self):
        '''
        constructor
        '''
        pass
    
    def run(self):
        '''
        run the ui
        '''
        ui.input(label='homepage', placeholder='''url of the event's homepage''',
                 on_change=lambda e: result.set_text('you typed: ' + e.value),
                 validation={'Input too long': lambda value: len(value) < 20})
        result = ui.label()
        
        ui.run()
