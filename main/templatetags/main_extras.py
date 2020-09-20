from django import template

register = template.Library()

@register.filter
def addstr(arg1, arg2):
    """
        concatenate arg1 & arg2
        karena kalau pakai |add biasa, variabel integer gak bisa
    """
    return str(arg1) + str(arg2)