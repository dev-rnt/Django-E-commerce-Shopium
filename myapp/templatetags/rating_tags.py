# myapp/templatetags/rating_tags.py
from django import template

register = template.Library()

@register.filter(name='stars')
def stars(value):
    full_stars = int(value)
    half_star = int((value - full_stars) * 2)
    empty_stars = 5 - full_stars - half_star

    return list(range(full_stars)) + [0.5] * half_star + [0] * empty_stars
