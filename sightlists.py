"""
Module to initiate sight words, place them into managable lists, and call each word at random
"""

import random

sight_list_1 = ['the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 'for', 'on', 'are', 'as', 'with', 'his', 'they', 'I', 'at', 'be', 'this', 'have', 'from', 'or', 'one', 'had', 'by', 'word', 'but', 'not', 'what', 'all', 'we\'re', 'we', 'when', 'your', 'can', 'said', 'there', 'use', 'an', 'each', 'which', 'she', 'do', 'how', 'their', 'if']

sight_list_2 = ['will', 'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'him', 'into', 'time', 'has', 'look', 'two', 'more', 'write', 'go', 'see', 'number', 'no', 'way', 'could', 'people', 'my', 'than', 'first', 'water', 'been', 'call', 'who', 'oil', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come','made', 'may', 'part', 'over']

sight_list_3 = ['new', 'sound', 'take', 'only', 'little', 'work', 'know', 'place', 'year', 'live', 'me', 'back','give', 'most', 'very', 'after', 'thing', 'our', 'just', 'name', 'good', 'sentence', 'man', 'think', 'say', 'great', 'where', 'help', 'through', 'much', 'before', 'line', 'right', 'too', 'mean', 'old', 'any', 'same', 'tell', 'boy', 'follow', 'came', 'want', 'show', 'also', 'around', 'farm', 'three', 'small', 'set']

sight_list_4 = ['put', 'end', 'does', 'another', 'well', 'large', 'must', 'big', 'even', 'such', 'because', 'turn', 'here', 'why', 'ask', 'went', 'men', 'read', 'need', 'land', 'different', 'home', 'us', 'move', 'try', 'kind', 'hand', 'picture', 'again', 'change', 'off', 'play', 'spell', 'air', 'away', 'animal', 'house', 'point', 'page', 'letter', 'mother', 'answer', 'found', 'study', 'still', 'learn', 'should', 'America', 'world', 'high']

sight_list_5 = ['every', 'near', 'add', 'food', 'between', 'own', 'below', 'country', 'plant', 'last', 'school', 'father', 'keep', 'tree', 'never', 'start', 'city', 'earth', 'eye', 'light', 'thought', 'head', 'under', 'story', 'saw', 'left', 'don\'t', 'few', 'while', 'along', 'might', 'close', 'something', 'seem', 'next', 'hard', 'open', 'example', 'begin', 'life', 'always', 'those', 'both', 'paper', 'together', 'got', 'group', 'often', 'run', 'important']

sight_list_6 = ['until', 'children', 'side', 'feet', 'car', 'mile', 'night', 'walk', 'white', 'sea', 'began', 'grow', 'took', 'river', 'four', 'carry', 'state', 'once', 'book', 'hear', 'stop', 'without', 'second', 'late', 'miss', 'idea', 'enough', 'eat', 'face', 'watch', 'far', 'country', 'real', 'almost', 'let', 'above', 'girl', 'sometimes', 'mountain', 'cut', 'young', 'talk', 'soon', 'list', 'song', 'being', 'leave', 'family', 'it\'s', 'afternoon']

master = [sight_list_1, sight_list_2, sight_list_3, sight_list_4, sight_list_5, sight_list_6]

pick_word = ''
word = []

def word_choose(array, indexes, subindex1, subindex2):
    """Chooses a random word from pre-defined sight word lists, 6 lists in master list.  Argument 'array' defaults to master, Arguments 'indexes, subindex1 and subindex2' are slices::: sub-list of master, then slices of the sub-list.  """
    word = array[indexes]
    pick_word = random.choice(word[subindex1:subindex2])

    return pick_word
    

def correct(word):
    master.index(word_choose.word).pop(pick_word)


    

