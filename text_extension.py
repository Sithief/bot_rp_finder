from Keys import Keys


def gender_msg(male_text, female_text, is_female):
    if is_female:
        return female_text
    else:
        return male_text


def default_input_error(is_female):
    return [sticker('input_error')]


def art_price(price):
    if price > 0:
        return str(price) + 'р.'
    else:
        return 'цена не установлена'


def is_active(current_item_number, active_item_number):
    if current_item_number == active_item_number:
        return ' ● '
    else:
        return 'ᅠ'


def line_break(text):
    if len(text) < 15:
        return text
    else:
        return '\n' + text


def separate():
    return '__________________________________'


def highlighting(text):
    return '### ' + text + ' ###'


def line_cut(text, text_len=20):
    symbols = '1234567890 abcdefghijklmnopqrstuvwxyz!/\|.,(){}[]*-+абвгдейжзийклмнопрстуфхцчшщьыъэюя'
    new_text = ''
    new_text_len = 0
    while new_text_len < text_len and text:
        new_text += text[0]
        new_text_len += 1 if text[0].lower() in symbols else 2
        text = text[1:]
    if new_text_len >= text_len:
        return new_text + '...'
    else:
        return new_text


def mention(text):
    text = text.replace('[', '⁅').replace(']', '⁆').replace('(', '❨').replace(')', '❩')
    text = text.replace('#', '♯').replace('@', 'α').replace('*', '⚹').replace('\n', ' ').replace('.', '․')
    return text


def sticker(sticker_id):
    if Keys().is_testing:
        stickers = {'input_error': 'doc-171562655_491406160',
                    'goodbye': 'doc-171562655_491406204',
                    'upload': 'doc-171562655_491406230',
                    'msg_left0': 'doc-171562655_491406392',
                    'msg_left10': 'doc-171562655_491406427',
                    'msg_left20': 'doc-171562655_491406462',
                    'msg_left40': 'doc-171562655_491406505'}
    else:
        stickers = {'input_error': 'doc-171562655_491406160',
                    'goodbye': 'doc-171562655_491406204',
                    'upload': 'doc-171562655_491406230',
                    'msg_left0': 'doc-171562655_491406392',
                    'msg_left10': 'doc-171562655_491406427',
                    'msg_left20': 'doc-171562655_491406462',
                    'msg_left40': 'doc-171562655_491406505'}
    if sticker_id in stickers.keys():
        return stickers[sticker_id]
    else:
        return ''


def tags():
    tag_list = ['DigitalArt', 'PixelArt', 'Animation', 'Vector', 'PhotoArt',
                'TraditionalArt',
                'Anthro', 'Furry', 'Brony', 'Humanization',
                'Anime',
                'Comics',
                'FanArt']
    return tag_list

