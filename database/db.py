from database.models import *


db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)



#with db_session:
"""
if not Category.exists(name='VALENTINO'):
    Category(name='VALENTINO', phone='valentino', margin=30)
if not Category.exists(name='LeSILLA'):
    Category(name='LeSILLA', phone='lesilla', margin=30)
if not Category.exists(name='NIKE'):
    Category(name='NIKE', phone='nike', margin=30)
if not Category.exists(name='NIKE Outlet'):
    Category(name='NIKE Outlet', phone='nikeoutlet', margin=30)
if not Category.exists(name='Dolce&Gabanna'):
    Category(name='Dolce&Gabanna', phone='dolcegabanna', margin=30)
if not Category.exists(name='COACH'):
    Category(name='COACH', phone='coach', margin=30)
if not Category.exists(name='Asics'):
    Category(name='Asics', phone='asics', margin=30)
if not Category.exists(name='Underarmour'):
    Category(name='Underarmour', phone='underarmour', margin=30)
"""



