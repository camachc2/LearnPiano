import pygame
#from pygame.locals import *
from pygame import Color
from pygame import midi
import GameModes
import sys


WIDTH = 1000
HEIGHT = 500
NO_DEVICE_FOUND = -1
OFFSET = 21         # My midi 66 key piano device makes my starting key C1 intger value 36. C1 is key 15.
BUFFER = 10
MAX_FRAMES_PER_SECOND = 100

DEBUG_TRACE = False

def map_keyboard():
    result = dict()
    numberOfKeys = input('Enter the number of keys: ')
    startingLetter = input('Enter the starting letter: ')
    Octive = input('Enter the starting octive: ')
    return result

class NoPianoDetectedException(Exception):
    pass

class LearnPianoApplication:
    def __init__(self):
        self.mapped_keys = dict()
        self.device_id = 0
        self.is_running = True
        self._keystrokes = []
        self._game = None
        
    def run(self):
        pygame.midi.init()
        self.device_id = midi.get_default_input_id()
        
        if self.device_id == NO_DEVICE_FOUND:
            raise NoPianoDetectedException('Device not detected.')
        
        self.midiObject = midi.Input(self.device_id)
        
        pygame.init()
        self._resize_surface((WIDTH, HEIGHT))
        clock = pygame.time.Clock()
        
        if DEBUG_TRACE:
            interface, name, is_input, is_output, is_open = midi.get_device_info(self.device_id)
            print('Device Interface: ', interface)
            print('Device Name: ', name)
            print('Device IsInput: ', is_input == 1)
            print('Device IsOutput: ', is_output == 1)
            print('Device Open: ', is_open == 1)

        self._game = GameModes.PressNext((WIDTH, HEIGHT))
        
        while(True):
            clock.tick(MAX_FRAMES_PER_SECOND)
            self._event_handler()
            
        self.midiObject.close()
        midi.quit()
        
    def _event_handler(self):
        piano_events = midi.midis2events(self.midiObject.read(BUFFER),1)    # .read(buffer size)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit();
            elif event.type == pygame.VIDEORESIZE:
                self._resize_surface(event.size)
            #Need to see if i can figure out how to use keyup and keydown to make it more readable
            '''elif event.type == pygame.locals.KEYUP:
                print('Key is up.')
            elif event.type == pygame.locals.KEYDOWN:
                print('Key is up.')'''
        self._handle_piano_events(piano_events)
        self._draw()
            

    def _handle_piano_events(self, piano_events):
        for event in piano_events:
            if event.data2 == 100:   #I am not sure if 100 is universally the number used to differentiate a keyboard press from a release
                self._keystrokes.append(event.data1-OFFSET)
            elif event.data2 == 64:
                if event.data1-OFFSET in self._keystrokes:
                    self._keystrokes.remove(event.data1-OFFSET)

        if DEBUG_TRACE:
            print(self._keystrokes)

    def _draw(self):
        surface = pygame.display.get_surface()
        surface.fill(Color('White'))
        self._game.play(surface, self._keystrokes)           
        pygame.display.flip()
        
    def _resize_surface(self, size: (int, int)) -> None:
        pygame.display.set_mode(size, pygame.RESIZABLE)

        
        

if __name__ == '__main__':
    LearnPianoApplication().run()
