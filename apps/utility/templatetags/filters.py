from datetime import date
import json
import uuid
import os


from django import template

register = template.Library()


@register.filter
def get_file_name(invoice):
    try:
        return str(invoice.attachment).split('/')[1]
    except:
        return None
    

@register.filter
def get_file_size(invoice):
    size = invoice.attachment.size
    return size/1000