from emoji import emojize
from aiogram.types import InlineKeyboardButton


def btn_back(code : str):
    btn_back = [emojize(':arrow_left: Назад', language='alias'), f'btn_{code}']
    return btn_back

def btn_prevnext(length, text_and_data, schema, page, name):
    #if length % 10 == 0:
    #    num_pages = length/10
    #    del text_and_data[page * 10 - 10:page * 10]
    #    del schema[page * 10 - 10:page * 10]
    #if length % 10 > 0:
    num_pages = length//10 + 1
    # первая страница
    if page == 1:
        del text_and_data[10:]
        del schema[10:]
    # последняя страница
    elif page == num_pages:
        del text_and_data[:page * 10 - 10]
        del schema[:page * 10 - 10]
    # промежуточные страницы
    else:
        del text_and_data[(page * 10):]
        del text_and_data[:page * 10 - 10]
        del schema[(page * 10):]
        del schema[:page * 10 - 10]
            
    btn_prev = f'btn_{name}_{page - 1}'
    btn_next = f'btn_{name}_{page + 1}'
    if page - 1 < 1:
        btn_prev = f'btn_{name}_{num_pages}'
    if page + 1 > num_pages:
        btn_next = f'btn_{name}_1'
        
    text_and_data += [
        [emojize(':arrow_backward:', language='alias'), btn_prev],
        [f'[{page} из {num_pages}]', 'btn_pass'],
        [emojize(':arrow_forward:', language='alias'), btn_next]
    ]
    schema.append(3)
    return text_and_data, schema

def btn_admin():
    btn_admin = InlineKeyboardButton(text=emojize(':briefcase: Админка :briefcase:', language='alias'), callback_data=f'btn_admin')
    return btn_admin