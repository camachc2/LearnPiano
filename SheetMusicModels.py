import random
from enum import Enum
'''Initial thoughts:
# 1. I want this class to keep the state of the staff
   what does that mean?
    -That means that I want the staff to keep track of which notes it currently has
    - I want the staff to to create random notes
        Do i need to a source of entropy or is a ramdom number generator/time(0) good enough?

    - Diffiulty?
        how many notes per staff'
            i guess that would depend on the time signature

    2. What do i want it to look like
        -I could make seperate rows of staffs 
            freeze the staff and show the location of the current note

    3. Ticks?
        How many ticks per staff?
        every tick the staff needs to be updated. 
        advance tick function
        tempo and ticks?

        So if i want to lock the staff to 4 mearsures per staff
        Whats the max amount of notes that can be played on those 4 measures.
            That has to do with the amount of 

    4. How do i pass it which notes are currently pressed.
        pass the array of notes at every tick

    5. Locator: What note is currently is currently being pressed
            - do i need a range of where it is acceptable to click ?
    Plan of attack:
        Note class should keep a time interval of when it should be played
            If within time interval and is_pressed
                keep how much of it was correct (stats)
        StaffState should have a dicationary with the key value of when the note should be played and the note itself
            you can figure out how long the note should be played based on the lendth.
        
        '''
NORMAL_TREBLE_PTICHES = [43, 44, 46, 48, 50, 51, 53, 55, 56]
DURATIONS = [1, .5, .25, .125, .0625]
Console_ON = False

class InvalidPitch(Exception):
    pass

class InvalidDuration(Exception):
    pass

class UnfillableMeasure(Exception):
    pass



class Pitch(Enum):
    A = 0
    A_SHARP_B_FLAT = 1
    B = 2
    C = 3
    C_SHARP_D_FLAT = 4
    D = 5
    D_SHARP_E_FLAT = 6
    E = 7
    F = 8
    F_SHARP_G_FLAT = 9
    G = 10
    G_SHARP_A_FLAT = 11


class Duration(Enum):
    Whole = 1
    Half = .5
    Quarter = .25
    Eighth = .125
    Sixteenth = .0625
    Default = 0



''' The Note class has two parameters:
        1. Pitch
            - integer value in the set [0-88)
            - e.g. A0 = 0, A#Bb = 1, ... B8 = 87,C8 = 87, 
        2. Duraton
            - Duration object reprenenting the duration of a note 
            - e.g.
'''
class PianoNote:
    def __init__(self, pitch: int, duration = Duration(Duration.Default), played_at = 0):
        if type(pitch) == int:
           if (0 >  pitch >= 88):
               raise InvalidPitch('Pitch has to be an integer between 0 and 88 inclusive. The out of bounds value was {}.'.format(pitch))
        else:
            raise TypeError('Pitch must be of type int. The inccorect type was {}.'.format(type(pitch)))

        if type(duration) in (float, int):
            if duration not in DURATIONS+[0]:
                raise InvalidDuration('Duration amount is not a standard note duration ie. 1 (whole), 0.5 (half), ... , 0.0625 (sixteenth)')
        elif type(duration) == type(Duration):
            pass
        else:
            raise TypeError('Duration must be of type Duration or int. The inccorect type was {}.'.format(type(Duration)))

        self._pitch = Pitch(pitch % 12)
        self._octive = pitch // 12
        self._played_at = played_at
        
        if type(duration) == Duration:
            self._duration = duration
        else:
            self._duration = Duration(duration)
                            
    def __str__(self):
        return '{}{}'.format(self._pitch.name, self._octive)

    def __reprt__(self):
        return 'PianoNote({},{})'.format(str(self._pitch.value+(self._octive*12)), str(self._duration.value))

    def get_pitch(self) -> int:
        return self._pitch.value

    def get_octive(self) -> str:
        return self._octive
                            
    def get_duration_time(self) -> int:
        return self._duration.value

    def get_duration_name(self) -> str:
        return self._duration.name

    def get_letter(self) -> str:
        return self._pitch.name
    
    def is_black_key(self) ->bool:
        len(self._pitch.name) > 1
                            
    def is_white_key(self) -> bool:
        len(self._pitch.name) == 1
        
    def get_played_time(self):
        return self._played_at


def get_note(n: int)-> str:
    pitch = Pitch(n % 12)
    octive = n // 12
    return str(pitch.name)+ str(octive)


def random_measure(time: int, beats_per_measure: int, beat: Duration) -> 'dict: key = float, value = Note': 
    ''' Return a dictionary containing a key float value represnting the momonet a key is played.
        Note on beat will advance the time by 1. The value will be a PianoNote object.'''
    result = dict()
    remaining_measure_sum = beat.value*beats_per_measure
    # Possible pitches range from [0,87] representing an 88 key piano
    # Treble clef's (Right Hand) ranges from 40 (E3) to 53 (F4) (bottom line to the top line)
        # - note that this includes sharps and flats
        # - note class might need to implement a sharp/flat neutralizer
    # Bass clef's (left hand) ranges from 19 (G1) to 32 (A2)
    while(remaining_measure_sum >= min(DURATIONS)):
        #create a random note that doesn't overflow the measure
        random_duration = DURATIONS[random.randint(0, len(DURATIONS) - 1)]
        #random_pitch = NORMAL_TREBLE_PTICHES[random.randint(0, len(NORMAL_TREBLE_PTICHES) - 1)]
        random_pitch = random.randint(0, len(NORMAL_TREBLE_PTICHES) - 1)

        if(random_duration <= remaining_measure_sum):
            result[time] = PianoNote(random_pitch, random_duration, time)
            time += random_duration
            remaining_measure_sum -=  random_duration
            
    if(remaining_measure_sum != 0):
        raise UnfillableMeasure('The remaining value '+ str(remaining_measure_sum)+ ' of the measure is smaller than any Duration')

    return result


class Measure:
    def __init__(self, time = 0, beats_per_measure = 4, beat = Duration.Quarter, notes = dict()):
        '''4/4 = Four quarter notes per measure, quarter note gets the beat.
           6/8 = Six eighth notes per measure, eighth note gets the beat.'''

        if type(time) in (float, int):
            if time < 0:
                raise ValueError('Time error. time needs to be a non-negative number. The number given was {}.'.format(time))
        else:
            raise TypeError('Time needs to be of type int or float. The given type for time was {}'.format(type(time)))

        if type(beats_per_measure) == int:
            if beats_per_measure < 0:
                raise ValueError('Beats per measure is invalid. Beats per measure needs to be a non-negative integer. The given value was {}.'.format(beats_per_measure))
        else:
            raise TypeError('Error, the type of beats_per_measure needs to be of type integer. The given type was {}.'.format(type(beats_per_measure)))
        
        
        self._time = time
        self._beat = beat
        self._beats_per_measure = beats_per_measure
        self._total = beats_per_measure*beat.value   # intially this number was zero
        self._notes = notes

        if len(notes) == 0:
            self._notes = random_measure(time, beats_per_measure, beat)
        else:
            #   still have to make sure that notes given in the dictionary are valid
            #   make sure that the total value of the measure is valid
            #   format needs to make sure it works
            self._notes = notes

    def __iter__(self):
        for note in self._notes.values():
            yield note

    def get_starting_time(self):
        return self._time
    
    def get_beat(self):
        return self._beat

    def get_beats_per_measure(self):
        return self._beats_per_measure

    def get_total_measure_value(self):
        '''Get the total measure value based on the beat value and beats/measure.'''
        return self._total

    # Im not sure if i want to implement this 
    def collapse_notes(self):
        '''Makes a deep copy of the underlying dictionary conatining (time played - note) pairs.
        This function could be potentially expensive depending on the amount of information stored in the Measure object.''' 
        pass


class Staff(Measure):
    def __init__(self, time = 0, beats_per_measure = 4, beat = Duration.Quarter, bars = 3, notes = dict()):
        Measure.__init__(self, time, beats_per_measure*(bars+1), beat, notes)
        self._bars = bars    # 3 bars per row (4 measures)
        self._max_staff_value = beats_per_measure*(beat.value)*(bars+1)
        
        
    def get_bars(self):
        return self._bars

    # this function needs further testing
    # additionally this might be an expensive function to implement
    # might want to trade off space for time
    def get_measure_number(self, note: PianoNote):
        '''Zero means that the note is not played in this staff'''
        if note.get_played_time() < self.get_starting_time() or note.get_played_time() > time + self._max_staff_value:
            return 0
        return (note.get_played_time() - self.get_starting_time()) // (bars+1)

    def get_staff_value(self):
        return self.get_total_measure_value()



