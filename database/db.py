from database.models import *

db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

 
with db_session:
    if not Category.exists(name='VALENTINO'):
        Category(name='VALENTINO', catalog=Catalog(phone='valentino', link='none', margin=30))
    if not Category.exists(name='VALENTINO'):
        Category(name='LeSILLA', catalog=Catalog(phone='lesilla', link='none', margin=30))

