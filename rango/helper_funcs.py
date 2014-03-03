__author__ = 'admin'

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from datetime import datetime
from rango.models import Category




def endecode(str):
    if "_" in str:
        flip = str.replace('_', ' ')
    else:
        flip = str.replace(' ', '_')

    return flip

def get_all_logged_in_users():
    # Query all non-expired sessions
    sessions = Session.objects.filter(expire_date__gte=datetime.now())
    uid_list = []

    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))

    # Query all logged in users based on id list
    return User.objects.filter(id__in=uid_list)

def get_5_categories():
    try:
        category_list = Category.objects.order_by('-likes')[:5]
        for category in category_list:
            category.url = endecode(category.name)
        return category_list
    except Category.DoesNotExist:
        pass

def get_category_list(max_results=0, starts_with=''):
        cat_list = []
        if starts_with:
                cat_list = Category.objects.filter(name__istartswith=starts_with)
        else:
                cat_list = Category.objects.all()

        if max_results > 0:
                if len(cat_list) > max_results:
                        cat_list = cat_list[:max_results]

        for cat in cat_list:
                cat.url = endecode(cat.name)

        return cat_list

