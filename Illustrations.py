import pygame
import point


TREBLE_CLEFF = 0
BASS_CLEFF = 1
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)


class NoteSketch:
    def __init__(self, centerPoint: 'Point', surfaceDimensions: '(width,height)', radius: 'radius', duration = .25, line_up = False, color = BLACK):
        self._radius = radius
        self._center = centerPoint.pixel(surfaceDimensions[0], surfaceDimensions[1]) #(width, height)
        self._duration = duration
        self._isFacingUp = line_up
        self._color = color
        
        self._hallow = duration >= .5
        self._hasline = duration <= .5
        
        self._number_of_flags = self.get_number_of_flags(duration)
        
    def draw(self, surface):
        #circle(Surface, color, pos, radius, width=0) -> Rect
        #draw circle
        pygame.draw.circle(surface, self._color, self._center, self._radius, self._hallow) # 0 == filled

        #draw line
        lineStartingPosition = (0,0)
        lineEndingPosition = (0,0)
        if self._hasline:
            if self._isFacingUp:
                lineStartingPosition = (self._center[0]+self._radius,self._center[1]) #(Width-radius/2, Height)
                lineEndingPosition = (self._center[0]+self._radius,self._center[1]-self._radius*5) #(Width+radius/2, Height*5)
            else:
                lineStartingPosition = (self._center[0]-self._radius,self._center[1]) #(Width+radius/2, Height)
                lineEndingPosition = (self._center[0]-self._radius,self._center[1]+self._radius*5) #(Width+radius/2, Height*5)
            pygame.draw.line(surface, self._color, lineStartingPosition, lineEndingPosition, 1)

        #draw flags
        line_x1, line_y1 = lineStartingPosition
        line_x2, line_y2 = lineEndingPosition

        flag_width = self._radius
        flag_height = (line_y2-line_y1)
        for i in range(self._number_of_flags):
            if self._isFacingUp:
                pygame.draw.polygon(surface, self._color, [[line_x2, line_y2], [line_x2-flag_width, line_y2-(flag_height*.2)], [line_x2, line_y2-(flag_height*.1)]], 0)
            else:
                pygame.draw.polygon(surface, self._color, [[line_x2, line_y2], [line_x2+flag_width, line_y2-(flag_height*.2)], [line_x2, line_y2-(flag_height*.1)]], 0)
            line_y2 = line_y2-(flag_height*.15)


    def get_number_of_flags(self, duration):
        result = 0
        while duration < .25:
            result += 1
            duration *= 2
        return result
    
    def get_connection_points(self):
        pass


class TimeError(Exception):
    pass

#, notes: '[(played_at, note_value), ...]'
class MeasureSketch:
    def __init__(self, top_left: 'Point', bottom_right: 'Point', dimensions: '(width,height)', raw_notes = dict(),
                 color = BLACK, time_signature = (4, .25), current_note_time = -1):
        '''raw_notes = {time: (measure_pitch_value, duration)} time needs to start at zero'''
        # Measure Attributes
        self._color = color
        self._time_signature = time_signature
        self._measure_current_value = 0
        self._measure_max_value = self._time_signature[0]*self._time_signature[1]
        self._current_note_time = current_note_time
        self._raw_notes = raw_notes
        
        # Coordinates
        self._window_width, self._window_height = (0,0)
        self._top_left_point = top_left
        self._bottom_right_point = bottom_right
        self._adjust_coordinates(dimensions)

    def _adjust_coordinates(self, dimensions):
        ''' Calculate pixel coordinates based on the current dimension of the surface. '''
        if (self._window_width, self._window_height) != dimensions:
            self._window_width, self._window_height = dimensions #need the window size to go from fractional coordinates to actual pixels
            self._x1, self._y1 = self._top_left_point.pixel(self._window_width, self._window_height)  #(x1, y1)
            self._x2, self._y2 = self._bottom_right_point.pixel(self._window_width,self._window_height)
            self._measure_width = self._x2 - self._x1
            self._measure_height = self._y2 - self._y1

            self._line_points = self._line_cordinates(self._top_left_point.pixel(self._window_width, self._window_height),
                                                      self._bottom_right_point.pixel(self._window_width,self._window_height))
            self._pitch_y_coords = [self._line_points[i][0][1] for i in range(len(self._line_points))]
            #self._raw_notes = raw_notes
            self._note_sketches = []
            if len(self._raw_notes) != 0:
                self._create_notes()

    def _line_cordinates(self, top_left: '(x1, y1)', bottom_right: '(x2, y2)') -> '[((x1,y1),(x2,y2)), ..., ((x(n-1),y(n-1),(xn,yn))]' :
        ''' Return a list two point tuples representing the points of the lines in a measure.'''
        NUMBER_OF_PITCHES = 9
        x1, y1 = top_left
        x2, y2 = bottom_right
        step = abs(y2-y1)/(NUMBER_OF_PITCHES-1) #9 pitches, 8 steps between pitches
        step_sum = 0
        result = []
        for i in range(NUMBER_OF_PITCHES):
            result.append(((x1,round(y1+step_sum)),(x2,round(y1+step_sum))))
            step_sum += step
        return result
    
     # this function forces every value in the measure to be occupied. Making the need for rests if i want account for silence. 
    def _create_notes(self):
        # Input: {time: (pitch, duration)}
        # Output: [NoteSketch]
        OFFSET = .05
        beats_per_measure, beat_value = self._time_signature
        measure_remaining_value = beats_per_measure*beat_value
        next_x_position = self._x1
        for played_at, (pitch, duration) in self._raw_notes.items():
            if duration > measure_remaining_value:
                raise TimeError()
            measure_remaining_value -= duration
            note_center_point = point.from_pixel(round(next_x_position + (OFFSET*self._measure_width)), self._pitch_y_coords[pitch], self._measure_width, self._measure_height)
            if(self._current_note_time == played_at):   
                self._note_sketches.append(NoteSketch(note_center_point, (self._measure_width, self._measure_height), self._measure_height//8, duration, line_up = self._is_note_line_up(pitch), color = RED))
            else:
                self._note_sketches.append(NoteSketch(note_center_point, (self._measure_width, self._measure_height), self._measure_height//8, duration, line_up = self._is_note_line_up(pitch)))

            used_space = (duration/beat_value/beats_per_measure)*self._measure_width
            next_x_position += used_space

    def update_current_note(self, time):
        if time != self._current_note_time:
            self._current_note_time = time
            self._create_notes()
      
    def draw(self, surface):
        '''Draw the staff from a given upper left point and a bottom right point.'''
        self._adjust_coordinates(surface.get_size())
        # Horizontal Lines
        for i in range(0,len(self._line_points),2):
            left_point, right_point = self._line_points[i]
            pygame.draw.line(surface, self._color, left_point, right_point, 1)

        # Vertical Lines
        #line(Surface, color, start_pos, end_pos, width=1) -> Rect
        pygame.draw.line(surface, self._color, self._line_points[0][0], self._line_points[-1][0], 1)
        pygame.draw.line(surface, self._color, self._line_points[0][1], self._line_points[-1][1], 1)

        # Draw Notes
        for note in self._note_sketches:
            note.draw(surface)

        
    def get_height(self) -> int:
        ''' Get the height of the measure.'''
        return self._measure_height

    def get_width(self) -> int:
        ''' Return the width of the measure.''' 
        return self._measure_width

    def get_vertical_pitch_coordinate(self, n) -> int:
        '''[0,8] pitches where 0 is the y coordinate of the top line and 8 is the y coordinate of the bottom line.''' 
        return self._pitch_y_coords[n]

    def get_horizontal_pitch_coordinate(self, n) -> int:
        pass

    def _is_note_line_up(self, pitch):
        return pitch > 5

    def increment_current_note_time(self, time):
        self._current_note_time = time
        




class StaffSketch():
    def __init__(self, top_left: 'Point', bottom_right: 'Point', dimensions: '(width,height)', raw_dict_notes = [dict()], color = BLACK,
                 time_signature = (4, .25), current_note_time = -1 ,number_of_measures = 4):
        
        if len(raw_dict_notes) != number_of_measures:
            raise TimeError()

        # Coordinates
        self._window_width, self._window_height = dimensions  #need the window size to go from fractional coordinates to actual pixels
        self._x1, self._y1 = top_left.pixel(self._window_width, self._window_height)  #(x1, y1)
        self._x2, self._y2 = bottom_right.pixel(self._window_width,self._window_height)
        self._staff_width = self._x2 - self._x1
        self._staff_height = self._y2 - self._y1

        # Measures
        self._current_note_time = current_note_time
        self._measure_frac_width = (bottom_right.frac()[0] - top_left.frac()[0]) / number_of_measures
        self._measures = []
        for i, measure_notes in enumerate(raw_dict_notes):
            temp_top_left_point = point.from_frac(top_left.frac()[0]+ (self._measure_frac_width * i), top_left.frac()[1])
            temp_bottom_right_point = point.from_frac(top_left.frac()[0]+ (self._measure_frac_width * (i+1)), bottom_right.frac()[1])
            self._measures.append(MeasureSketch(temp_top_left_point, temp_bottom_right_point, dimensions, measure_notes, color, time_signature, current_note_time))

    def draw(self, surface):
        for measure in self._measures:
            measure.draw(surface)

    def update_current_note(self, time):
        if time != self._current_note_time:
            self._current_note_time = time
            for measure in self._measures:
                measure.update_current_note(time)









