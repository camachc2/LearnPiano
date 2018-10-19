import SheetMusicModels
import Illustrations
import point
import queue

NORMAL_TREBLE_PTICHES = [56, 55, 53, 51, 50, 48, 46, 44, 43]

def model_to_illustration_notes(notes: '{time: PianoNote}', measure_value) -> '{time: (pitch [0-9], duration)}':
    result = []
    total_time = 0
    temp_time = 0
    temp_dict = dict()
    for time, note in notes.items():
        temp_dict[time] = (note.get_pitch(), note.get_duration_time())
        total_time += note.get_duration_time()
        temp_time += note.get_duration_time()
        if temp_time >= measure_value:
            temp_time = 0
            result.append(temp_dict)
            temp_dict = dict()
    return result

def collapse_measures(measures):
    result = dict()
    for dictionary in measures:
        for key, value in dictionary.items():
            result[key] = value
    return result

class PressNext:
    _NUMBER_OF_MEASURES = 4
    _NUMBER_OF_STAFFS = 3
    _BEATS_PER_MEASURE = 4
    _BEAT = .25
    def __init__(self, dimensions: '(surface width, surface height)'):
        self._dimensions = dimensions
        self._current_note_time = 0
        self._next_time = 0
        self._staff_models = []
        self._staff_sketches = []
        self._note_queue = queue.Queue()
        self._current_play_time = 0
        self._last_keys_played = []
        self._last_member_queued = False

        self._set_up_notes()

        self._current_note = self._note_queue.get()
        self._current_play_time = self._current_note.get_played_time()

    def _set_up_notes(self):
        staff_x_frac_cord_starting_point = .05
        staff_y_frac_cord_starting_point = .2
        staff_seperation = .05

        staff_frac_width = .9
        staff_fract_height = .1
        for i in range(PressNext._NUMBER_OF_STAFFS):
            # Model
            measure_value = PressNext._BEATS_PER_MEASURE*PressNext._BEAT
            duration = SheetMusicModels.Duration(PressNext._BEAT)
            
                    # This line calls random measure _NUMBER_OF_MEASURES times to avoid notes overflowing into neighboring measures
            model_notes = collapse_measures([SheetMusicModels.random_measure(self._next_time + (i*measure_value), PressNext._BEATS_PER_MEASURE, duration)
                                             for i in range(PressNext._NUMBER_OF_MEASURES)])
            #self._note_times.extend(model_notes.keys())
            ModelStaff = SheetMusicModels.Staff(self._next_time, PressNext._BEATS_PER_MEASURE, duration, PressNext._NUMBER_OF_MEASURES-1, model_notes)
            self._staff_models.append(ModelStaff)
            self._next_time += ModelStaff.get_staff_value()

            # set up a fifo queue of the uncomming notes
            for note in ModelStaff:
                self._note_queue.put(note)
            
            
            # View
            view_notes = model_to_illustration_notes(model_notes, measure_value)  # convert notes
            upper_left_point = point.Point(staff_x_frac_cord_starting_point, staff_y_frac_cord_starting_point)   # Staff placement
            bottom_right_point = point.Point(staff_x_frac_cord_starting_point+staff_frac_width, staff_y_frac_cord_starting_point + staff_fract_height)
            staff_y_frac_cord_starting_point += staff_fract_height + staff_seperation
            
            StaffView = Illustrations.StaffSketch(upper_left_point, bottom_right_point, self._dimensions, view_notes, current_note_time = self._current_note_time)
            self._staff_sketches.append(StaffView)
        

    #force the user to press a single key
    def _handle_keys_pressed(self, keys_pressed):        
        current_key = NORMAL_TREBLE_PTICHES[self._current_note.get_pitch()]
        if len(keys_pressed) == 1  and current_key in keys_pressed and len(self._last_keys_played) == 0:
            if self._last_member_queued:
                self.__init__(self._dimensions) #Restarted using init to eliminate previous surface state drawn on surface
            self._current_note = self._note_queue.get()
            self._current_play_time = self._current_note.get_played_time()

        if self._note_queue.empty():
            self._last_member_queued = True

        self._last_keys_played = keys_pressed.copy()



    def play(self, surface, keys):
        for staff in self._staff_sketches:
            self._handle_keys_pressed(keys)
            staff.update_current_note(self._current_play_time)
            staff.draw(surface)
            
            
        
    def get_time(self):
        return self._time
    
