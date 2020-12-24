"""
This is the file for the Sight Words App
"""
import sys
import os
import re
import time
import speech_recognition as sr
import pyaudio
import pyttsx3
import webbrowser as webbrowser
import random as random
from random import shuffle as shuffle
import sightlists as sl

import kivy

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.storage.jsonstore import JsonStore
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.properties import BooleanProperty
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.graphics import Color, Line, Rectangle 
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.dropdown  import DropDown 
from kivy.uix.spinner import Spinner
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.animation import Animation
# from functools import partial

#Globals for use accross all classes
comp_list = [[], [], [], [], [], []]
player = ''
site = ''
confirm_delete = False


class ScreenManagement(ScreenManager):
    pass

class ExitPop(Popup):
    pass

class Redirect(Popup):
    pass    

class DeletePop(Popup):
    pass

class SelectPlayer(Popup):
    pass


class ChapterDropDown(DropDown):
    cdd = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class LessonDropDown(DropDown):
    ldd = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)



class HomeScreen(Screen):
    selected_player = ''
    playing = False

    
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.player_list = player_list = ListProperty()
        self.confirm_delete = confirm_delete


    def load_list(self):
        """
        Gets json data for the current list of readers
        """
        if SightWordsApp.word_data.exists('all_players'):
            self.player_list = SightWordsApp.word_data.get('all_players')['users']
        else:
            self.player_list = []

    
    def add_player(self):
        """
        Method to create a new player and handles a duplicate entry.
        """
        self.load_list()
        if self.ids.add_player.text not in self.player_list:
            if self.ids.add_player.text != '' and self.ids.add_player.text != 'Select a Player':
            
                self.player_list.append(self.ids.add_player.text)
    
    def show_players(self):
        self.load_list()
        self.ids.choose_player.values = self.player_list
        self.ids.remove_player.values = self.player_list+['Cancel']


    def delete_pop(self):
        del_plyr = DeletePop(title = 'Warning!!!', size_hint = (0.75, 0.75), title_align = 'center', auto_dismiss = False)
        del_plyr.open()
        self.selected_player = self.ids.remove_player.text

    def must_select(self):
        need_reader = SelectPlayer(title = 'Select a Reader to Play', size_hint = (0.6, 0.6), title_align = 'center', auto_dismiss = False)
        need_reader.open()
    
    def start_game(self):
        if self.ids.choose_player.text ==  'Select Here':
            self.must_select()
        else:
            self.playing = True
            self.confirm_delete = False
        

    def rem_player(self):
        """
        This method deletes all records of a selcted reader
        """
        player = self.ids.remove_player.text
        print(player)
        print(f'what: {self.selected_player}')
        # if player != self.selected_player:
        #     self.confirm_delete = False
        #     return
        self.load_list()
        if player in self.player_list:
            self.player_list.pop(self.player_list.index(player))

        for plyr in SightWordsApp.wordsscreen.completed_tup:
            remove = player+plyr
            if SightWordsApp.word_data.exists(remove):
                SightWordsApp.word_data.delete(remove)

        self.ids.remove_player.text = 'Select Here'
        self.ids.choose_player.text = 'Select Here'
        self.ids.delete_player.text = 'Confirm Delete'
        self.playing = False
        self.add_list_json()
    
    # def confirmation(self):
    #     self.confirm_delete = True
    
    # def undo_confirm(self):
    #     self.confirm_delete = False

    def delete_control(self):
        """
        Method to control the deletion of a player and handles a popup in case this is pressed by mistake.  3 buttons will need to be pressed to complete the deletion
        """
        # print(f'\n Confirm py: {self.confirm_delete}\nprev version py {SightWordsApp.homescreen.self.confirm_delete}\n')

        
        if self.ids.remove_player.text == 'Cancel':
            self.confirm_delete = False
            return
        elif self.ids.remove_player.text == 'Select Here':
            self.confirm_delete = False
            return            
        if self.confirm_delete == False:
            self.delete_pop()
            self.confirm_delete = True
        else:
            self.rem_player()
            return

            # self.ids.remove_player.text = 'Select Here'

        # if self.ids.remove_player.text == 'Select Here':
        #     return
        # if self.ids.remove_player.text == 'Cancel':
        #     self.ids.remove_player.text = 'Select Here'
        #     self.confirm_delete = False
        #     return
        # if self.confirm_delete == False:
        #     self.delete_pop()
        # else:
        #     self.rem_player()
        #     self.confirm_delete = False 

    def change_label(self):

        player = self.ids.choose_player.text
        self.parent.children[0].ids.plyr_banner.text = 'Hello '+player
        if self.confirm_delete == False:
            self.ids.remove_player.text = 'Select Here'


    def add_list_json(self):
        
        SightWordsApp.word_data.put('all_players', users = self.player_list)



class WordsScreen(Screen):
    chapter = 0
    lesson = 0
    end_lesson = 0
    dropdown = ListProperty([])
    ws = ObjectProperty(None)
    cur_list = ListProperty([])
    cur_lesson = []
    completed_tup = ('chp1', 'chp2', 'chp3', 'chp4', 'chp5', 'chp6')
    plyr_banner =  StringProperty(player)
    homescreen = HomeScreen()
    reading = False
    

    def __init__(self, **kwargs):
        super(WordsScreen, self).__init__(**kwargs)

        self.chap_drop = ChapterDropDown()
        self.less_drop = LessonDropDown()

        self.rec = sr.Recognizer()
        self.rec.pause_threshold = 0.5 #seconds of non-speaking audio before a phrase is considered complete
        self.rec.phrase_threshold = 0.3  # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
        self.rec.non_speaking_duration = 0.5  # seconds of non-speaking audio to keep on both sides of the recording
        self.mic = sr.Microphone()
        self.mic.CHUNK = 768 # The microphone audio is recorded in chunks of ``chunk_size`` samples, at a rate of ``sample_rate`` samples per second (Hertz). If not specified, the value of ``sample_rate`` is determined automatically from the system's microphone settings.


        try:
            self.engine = pyttsx3.init()
            self.voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', self.voices[1].id) #changing index, changes voices. 1 for female 0 for male
            self.volume = self.engine.getProperty('volume')
            self.engine.setProperty('volume',1.0) # setting up volume level between 0 and 1
            self.rate = self.engine.getProperty('rate')
            self.engine.setProperty('rate', 100) # setting up new voice rate
        except:
            pass


        self.chap_drop.bind(on_select = lambda instance, x: setattr(self.ids.chapters, 'text', x))

        self.less_drop.bind(on_select = lambda instance, x: setattr(self.ids.lessons, 'text', x))

        self.completed_tup = ('chp1', 'chp2', 'chp3', 'chp4', 'chp5', 'chp6')
        self.drop_chap = ""
        self.cur_lesson = []


    def exitpop(self):
        exit_app = ExitPop(title = 'Exit Sight Words', size_hint = (0.6, 0.6), title_align = 'center', auto_dismiss = False)
        exit_app.open()


    def preview(self, dt=0):
        """
        Creates a current list of 5 words from the sighlist mod based on the chapter and lesson the user chose.
        """
        if self.ids.chapters.text == 'Chapters' and self.ids.lessons.text == 'Lessons':
            return
        self.every_word = sl.master
        
        self.chapter = int(self.ids.chapters.text[-1])-1
        
        self.lesson = (int(self.ids.lessons.text[-2::])-1)*5
        self.end_lesson = self.lesson+5
        if self.lesson  == 45:
            self.end_lesson = len(self.every_word[self.chapter])

        self.cur_list = self.every_word[self.chapter][self.lesson:self.end_lesson]

        self.ids.preview.values = self.cur_list
        if self.reading ==  True:
            Clock.schedule_once(self.word_label)

    def call_read_list(self):
        if self.ids.chapters.text == 'Chapters' and self.ids.lessons.text == 'Lessons':
            return
        Clock.schedule_interval(self.read_list, 2.3)
        self.call_index = 0


    def read_list(self, dt):
        self.preview()
        if self.call_index == 5:
            self.ids.words.text = 'Get Ready!!!'
            return False
        self.ids.words.text = self.cur_list[self.call_index]
        Clock.schedule_once(self.read_word, 0.3)

    def read_word(self, dt):
        try:
            self.engine.say(self.ids.words.text)
            self.engine.runAndWait()
        except:
            pass
        self.call_index += 1


    
    def word_label(self, dt=0):
        if self.ids.chapters.text != 'Chapters' and self.ids.lessons.text != 'Lessons':
            if len(self.cur_lesson) == 0:
                self.cur_lesson = self.cur_list
            self.ids.words.text = random.choice(self.cur_lesson)
            Clock.schedule_once(self.chooser)

            
    def listen(self, recognizer, microphone):
        """
        Implementation of the SpeechRecognition Module.  Send voice to Google and return Text.
        """

        if not isinstance(recognizer, sr.Recognizer):
            raise TypeError("`recognizer` must be `Recognizer` instance")

        if not isinstance(microphone, sr.Microphone):
            raise TypeError("`microphone` must be `Microphone` instance")

        with self.mic as source:
            self.rec.adjust_for_ambient_noise(source, duration=0.3)
            audio = self.rec.listen(source, phrase_time_limit=4.0)

            if self.rec.phrase_threshold >= 4:
                ###   Popup   ###
                Clock.schedule_once(self.preview)
                return ''
            
        self.spoken = {"success": True, "error": None, "transcription": None}

        try:
            self.spoken["transcription"] = str(recognizer.recognize_google(audio, show_all=True))
            # print(f'\n\nTry:  {str(self.spoken["transcription"].values()[0])}\n\n')
        except sr.RequestError:
            # API was unreachable or unresponsive
            self.spoken["success"] = False
            self.spoken["error"] = "API unavailable"
            #############   POPUP   #################
        except sr.UnknownValueError:
            # speech was unintelligible
            self.spoken["error"] = "Urecognizeable speech"
            #############   POPUP   #################
        finally:
            self.spoken["error"] = ''



        print(f'\n\n{self.spoken["transcription"]}\n\n')
        return self.spoken["transcription"]


    def chooser(self, dt=0):
        """
        Simple method to create a copy of the cur_list to pop(correct word) from the list.
        """
        # self.preview()
        # self.word_label()
        # self.preview()
        if self.ids.chapters.text != 'Chapters' and self.ids.lessons.text != 'Lessons':
        
            # pick = random.choice(range(self.cur_lesson))
            # self.ids.words.text = self.cur_lesson[pick]
            # print(self.cur_list)
            # print(len(self.cur_lesson))

            # if len(self.cur_lesson) == 0 or self.cur_lesson[0] not in self.cur_list:
            if len(self.cur_lesson) == 0:
                self.cur_lesson = self.cur_list
                print(f'chooser...  {self.cur_lesson}')
                # print(len(self.cur_lesson))
            
            # self.ids.words.text = random.choice(self.cur_lesson)
            # print(self.ids.words.text)
            if self.ids.words.text == 'Get Ready!!!':
                return
            #else:
            Clock.schedule_once(self.checker)

        
        # self.checker()

    
    def checker(self, dt=0):
        """
        Takes the text result from speach to text and checks if it matches the current sight word.  If there is a match the word will pop out of the current working list of words for the given lesson.  Once the list is empty the completed lesson method is called.
        """
        # self.ids.words.text = random.choice(self.cur_lesson)
        #Spoken will be text input from speach
        # lesson_list = "'being', 'leave', 'family', 'it\'s', 'afternoon'"  #Replace with self.cur_list
        # lesson_list = self.cur_lesson
        # recognizer = sr.Recognizer()
        # recognizer.operation_timeout = 3
        # microphone = sr.Microphone()
        # if re.search(self.ids.words.text, spoken, re.IGNORECASE):
        # if re.search(self.ids.words.text, self.listen(recognizer, microphone), re.IGNORECASE):
        if re.search(self.ids.words.text, self.listen(self.rec, self.mic), re.IGNORECASE):
        # if self.ids.words.text.lower() == self.listen(recognizer, microphone).lower():
            correct_word = self.ids.words.text.lower()
            try:
                self.cur_lesson.pop(self.cur_lesson.index(correct_word))
            except:
                self.cur_lesson.pop(self.cur_lesson.index(correct_word.capitalize()))
            print(f'checker...  {self.cur_lesson}')
            self.ids.words.text = ''


            if len(self.cur_lesson) == 0:
            #     return 
            # else:
                # print('should add lesson')
                self.ids.words.text = 'Great Job!!!\n Try Another Lesson'
                Clock.schedule_once(self.completed_lesson)
                # self.ids.words.text = 'Great Job!!!\n Try Another Lesson'
                
                # Clock.schedule_once(self.happy_face, 0)
                return
            else:
                # self.ids.words.text = ''
                Clock.schedule_once(self.between_word)
            #     Clock.schedule_once(self.word_label, 0)
            #     Clock.schedule_once(self.chooser, 0)
                return
        else:
            # self.ids.words.text = ''
            Clock.schedule_once(self.between_word)
        #     Clock.schedule_once(self.word_label, 0)
        #     Clock.schedule_once(self.chooser, 0)
            return


    def between_word(self, dt=0):
        self.ids.words.text = ''
        Clock.schedule_once(self.preview, 0.7)


    def completed_lesson(self, dt=0):
        """
        This method checks to see if the current lesson is already in the json file and if not adds it so it can be called from the resource screen on the copleted lesson dropdowns.
        """
        add_to_chap = int(self.ids.chapters.text[-1])-1
        lessson_num = self.ids.lessons.text[-2::]
        add_lbl = 'Lesson '+lessson_num
        player = self.ids.plyr_banner.text[6::]

        if self.ids.chapters.text != 'Chapters' and self.ids.lessons.text != 'Lessons':
            # if add_lbl in comp_list[add_to_chap]:
            #     print('comp less returned lesson already exists')
            #     return
            if add_lbl in comp_list[add_to_chap]:
                Clock.schedule_once(self.happy_face)
                return
            else:
                comp_list[add_to_chap].append(add_lbl)
            new_list = sorted(comp_list[add_to_chap])

            self.drop_chap = player+self.completed_tup[add_to_chap]
            if SightWordsApp.word_data.exists(self.drop_chap):
                # new_list = sorted(comp_list[add_to_chap])
                if new_list[-1] in SightWordsApp.word_data.get(self.drop_chap)['add_less']:
                    print('already in there')
                    Clock.schedule_once(self.happy_face)
                    return
                # next_list = set(new_list)
                # new_list = list(next_list)
                else:
                    print('Adding')
                    new_list.extend(SightWordsApp.word_data.get(self.drop_chap)['add_less'])
            inter_set = set(new_list)
            print(f'inter: {inter_set}')
            final_list = list(inter_set)
            print(f'\nfinal: {final_list}')
                
                # final_list - list(next_list)
            # print(f'comp lesson drop chap {self.drop_chap}')
            SightWordsApp.word_data.put(self.drop_chap, add_less = sorted(final_list))
            print('Completed Lesson Finished')
            self.happy_face()
            # print(f' PUT  {self.drop_chap} ...  {SightWordsApp.word_data}')


    def word_controller(self):
        pass


    def happy_face(self, dt=0):
        """
        This is a simple animation to show completion of a selected lesson.
        """
        self.hp = Image(source = 'smile.png', allow_stretch = True)
        self.hp.pos = self.ids.login.pos
        self.anim_happy = Animation(pos = self.ids.words.pos, size = self.ids.words.size, duration = 1)
        self.anim_happy.start(self.hp)
        self.ids.words.add_widget(self.hp)
        Clock.schedule_once(self.rem_happy, 3)

    def rem_happy(self, dt):
        while len(self.ids.words.children) > 0:
            self.ids.words.remove_widget(self.ids.words.children[0])
            # self.ids.start.disabled = False
            # self.chooser()
            # Clock.schedule_once(self.chooser)
    
    def change_label(self):
        player = self.ids.plyr_banner.text[6::]
        self.parent.children[0].ids.plyr_banner2.text = 'Hello '+player



class ResourceScreen(Screen):
    rs = ObjectProperty()
    
    def __init__(self, *args, **kwargs):
        super(ResourceScreen, self).__init__(*args, **kwargs)
        
    
    def open_wiki(self):
        webbrowser.open('https://en.wikipedia.org/wiki/Sight_word#Word_lists')

    def open_ed(self):
        webbrowser.open('https://www2.ed.gov/parents/academic/help/reader/part9.html')

    def direct(self):
        leave = Redirect(title = 'Open Link In Browser', size_hint = (0.55, 0.55), title_align = 'center', auto_dismiss = False)
        leave.open()
        

    def go_to_site(self):
        if self.site == 'us':
            self.open_ed()
        elif self.site == 'wiki':
            self.open_wiki()


    def complete_less_spinner(self, index):
        """
        A method used to 'Get' the json data placed by the WordsScreen.completed_lesson method and is then assigned to the values of the completed lesson dropdowns given the index argument representing the Chapters.
        """
        if self.ids.plyr_banner2.text[6::] != 'Select a Player':
            player = self.ids.plyr_banner2.text[6::]
        else:
            player = ''
        # print(f'is it the tup? {player+WordsScreen.completed_tup[index]}, what is index {index}')
        # print(f' line 315 {player}')
        if SightWordsApp.word_data.exists(player+WordsScreen.completed_tup[index]):
            # print('ah ha line 317')
            add_spin_vals = SightWordsApp.word_data.get(player+WordsScreen.completed_tup[index])['add_less']
            return add_spin_vals
        # else:
        #     print('oh no line 321')
        return ''

    def exitpop(self):
        exit_app = ExitPop(title = 'Exit Sight Words', size_hint = (0.55, 0.55), title_align = 'center', auto_dismiss = False)
        exit_app.open()


class SightWordsApp(App):
    sightwords = ObjectProperty(None)
    sightlists = ObjectProperty(None)
    homescreen = HomeScreen()
    wordsscreen = WordsScreen()
    chapterdrop = ChapterDropDown()
    resourcescreen = ResourceScreen()
    goto = BooleanProperty(False)
    
    word_data = JsonStore('sightword.json')
  

    def __init__(self, *args, **kwargs):
        super(SightWordsApp, self).__init__(*args, **kwargs)
        self.sightwords = ObjectProperty(None)
        self.sightlists = ObjectProperty(None)
        self.homescreen = HomeScreen()
        self.wordsscreen = WordsScreen()
        self.chapterdrop = ChapterDropDown()
        self.resourcescreen = ResourceScreen()        
        self.goto = BooleanProperty(False)
        self.word_data = JsonStore('sightword.json')        

    def build(self, **kwargs):
        Builder.load_file("main.kv")
        self.sm = ScreenManagement()
        self.sm.add_widget(HomeScreen(name = 'home'))
        self.sm.add_widget(WordsScreen(name = 'words'))
        self.sm.add_widget(ResourceScreen(name = 'resource'))
        self.sm.current = 'home'
        return self.sm
    
    def on_pause(self):
        return True
    
    def on_resume(self):
        pass

mei_files = ['smile.png', 'sightlists.py', 'sightwords.kv', 'sightword.json']

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    for file in mei_files:
        resource_path(file)
    SightWordsApp().run()
