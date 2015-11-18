# -*- coding: utf-8 -*-
def translit(text):
    symbols = (
        'абвгдеёжзийклмнопрстуфхцчшщыэюя',
        'abvgdeejzijklmnoprstufhzcssyeua'
    )
    acceptable_symbols = set(''.join(list(symbols) + [' _-0123456789']))
    tr = {ord(a): ord(b) for a, b in zip(*symbols)}
    tr[ord(' ')] = ord('_')
    text = ''.join([l for l in text.lower().strip() if l in acceptable_symbols])
    return text.translate(tr)

if __name__ == '__main__':
    print(translit('Съешь ещё этих мягких французских булок, да выпей же чаю.'))

