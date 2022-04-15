import os
import sys


def start():
    while True:
        choice = int(input("Enter number: 1 - en, 2 - de, 3 - quit\n"))

        if choice == 1:
            encrypt()
        elif choice == 2:
            decrypt()
        elif choice == 3:
            break
        else:
            print("Unknown command")


def encrypt():
    # Степень кодировки (сколько бит кодировки цвета меняется под шифровку)
    degree = int(input("Enter degree of encoding: 1/2/4/8:\n"))

    # Размеры текста и картинки
    text_len = os.stat('text.txt').st_size
    img_len = os.stat('img.bmp').st_size
    if text_len >= img_len * degree/8 - 54:
        print("Too long text")
        return

    # Открытие всех файлов
    text = open('text.txt', 'r')
    start_bmp = open('img.bmp', 'rb')
    encode_bmp = open('img_.bmp', 'wb')

    # Первые 54 бита картинки(bmp) изменять нельзя,
    # поэтому записываем их в новую картинку без изменений
    first54 = start_bmp.read(54)
    encode_bmp.write(first54)

    # Сохраняем маски в переменные
    text_mask, img_mask = create_mask(degree)
    print("text: {0:b}; image: {1:b}".format(text_mask, img_mask))

    # Все необходимые проверки пройдены, запускаем цикл
    while True:
        # Считываем один байт(8 бит) из текста, это один символ
        symbol = text.read(1)
        # Если нет символа, выходим из цикла
        if not symbol:
            break

        print("\nsymbol {0}, bin {1:b}".format(symbol, ord(symbol)))

        symbol = ord(symbol)
        # Проходимся во всем битам(8) с шагом в степень
        for _ in range(0, 8, degree):
            # Читаем один байт картинки, переводим его из байтов в числовой тип и применяем маску
            img_byte = int.from_bytes(start_bmp.read(1), sys.byteorder) & img_mask
            # Применяем к символу маску и смещаем так, чтобы получить 2 его первых бита
            bits = symbol & text_mask
            bits >>= (8-degree)

            print("img {0}, bits {1:b}, num {1:d}".format(img_byte, bits))

            # Добавляем два первых бита от символа в конец битов картинки
            img_byte |= bits

            print("Encoded " + str(img_byte))

            encode_bmp.write(img_byte.to_bytes(1, sys.byteorder))
            symbol <<= degree

    print(start_bmp.tell())

    encode_bmp.write(start_bmp.read())

    # Закрытие всех файлов
    text.close()
    start_bmp.close()
    encode_bmp.close()


def decrypt():
    # Степень кодировки (сколько бит кодировки цвета меняется под шифровку)
    degree = int(input("Enter degree of encoding: 1/2/4/8:\n"))
    # Сколько символов прочитать
    to_read = int(input("How many symbols to read: \n"))
    img_len = os.stat('img_.bmp').st_size

    # Если запрос на количество символов для прочтения больше чем размер возможных мест кодировки
    if to_read >= img_len * degree / 8 - 54:
        print("Too long text")
        return

    # Файл, куда запишем расшифровку
    text = open('text_.txt', 'w')
    encoded_bmp = open('img_.bmp', 'rb')
    # Пропускаем чтение первых 54 символов
    encoded_bmp.seek(54)

    text_mask, img_mask = create_mask(degree)
    # Делаем логическое отрицание
    img_mask = ~img_mask
    # Обнуляем все биты у байта картинки кроме последних degree (до этого обнуляли последние degree)

    # Счётчик прочтённых символов
    read = 0
    while read < to_read:
        symbol = 0
        # Проходимся во всем битам(8) с шагом в степень
        for _ in range(0, 8, degree):
            # Читаем один байт картинки, переводим его из байтов в числовой тип и применяем маску
            img_byte = int.from_bytes(encoded_bmp.read(1), sys.byteorder) & img_mask

            # Смещаем биты символа в лево на degree и делаем логическое или (добавляем биты из картинки в биты символа)
            symbol <<= degree
            symbol |= img_byte

        print("Symbol #{0} is {1:c}".format(read, symbol))
        read += 1
        text.write(chr(symbol))

    text.close()
    encoded_bmp.close()


def create_mask(degree):
    text_mask = 0b11111111
    img_mask = 0b11111111
    # Логический сдвиг
    text_mask <<= (8 - degree)
    text_mask %= 256
    img_mask <<= degree

    return text_mask, img_mask

    # Получается так, что мы убрали degree последних битов у байта картинки,
    # и взяли первые degree битов у байта символа из текста


start()
