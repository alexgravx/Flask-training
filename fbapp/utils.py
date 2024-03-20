import random

from fbapp.models import Content, Gender

def find_content(gender):
    contents = Content.query.filter(Content.gender == gender).all()
    return random.choice(contents)