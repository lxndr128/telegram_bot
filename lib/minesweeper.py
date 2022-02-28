from pymemcache.client.base import Client
from pymemcache import serde
from PIL import Image, ImageDraw
import random
import time
import os
import io
import re

async def module(data_):
    user_id = data_[0]
    sample = ((1, 1), (-1, 1), (1, -1),
              (-1, -1), (0, 1), (1, 0),
              (0, -1), (-1, 0))
    first_move = False

    if data_[1] != None and data_[1].lower() in ["quit", "exit"]:
        client = Client('localhost', serde=serde.pickle_serde)
        client.delete(str(user_id))
        client.close()
        return(["Выход произведён"])


    async def first_start():
        nonlocal first_move
        pattern = r"[1-9]{1}[0-9]?\s[1-9]{1}[0-9]?\s[1-9]{1}[0-9]{0,3}"
        params = data_[1]
        if params == None:
            import lib.help as h
            return [True, await h.module(["", "minesweeper"])]
        if re.fullmatch(pattern, params):
            params = params.split()
            cond = int(params[0]) * int(params[1]) / 2
            if int(params[2]) <= cond <= 450:
                x = int(params[0])+1
                y = int(params[1])+1
                num_of_bombs = int(params[2])
            else:
                return [False]
        else:
            return [False]

        first_move = True
        bombs = []  # Координаты бомб
        labels = {}  # Координаты меток
        main_table = [[0]*(x+1) for _ in range(y+1)]  # Рабочее поле
        field = [["X"]*(x+1) for _ in range(y+1)]  # Видимое поле
        flag = None  # Метка окончания игры

        # Обозначаем края поля
        for i in range(len(field)):
            if i == 0 or i == y:
                field[i] = ["~~"*x+"~"]
            else:
                field[i][0] = "|"
                field[i][-1] = "|"

        # Расставляем бомбы
        for _ in range(num_of_bombs):
            while True:
                x1, y1 = random.randint(1, x-1), random.randint(1, y-1)
                if main_table[y1][x1] == -9:
                    continue
                else:
                    main_table[y1][x1] = -9
                    bombs.append((y1, x1))
                    break

        # Расставляем цифры
        for i in bombs:
            for j in sample:
                main_table[i[0] + j[1]][i[1] + j[0]] += 1

        return [bombs, labels, main_table, field, x, y]

    # Функция, открывающая клетки
    def open_field(y1, x1):
        a = not 1 <= x1 < x or not 1 <= y1 < y
        if a or field[y1][x1] != "X" or main_table[y1][x1] < 0:
            return None
        if main_table[y1][x1] > 0:
            field[y1][x1] = main_table[y1][x1]
        else:
            field[y1][x1] = "."
            for i in sample:
                open_field(y1+i[0], x1+i[1])

    # Функция, устанавливающая метки
    def put_label(y1, x1):
        if field[y1][x1] not in "XB":
            return None
        elif field[y1][x1] == "B":
            del labels[(y1, x1)]
            field[y1][x1] = "X"
        elif field[y1][x1] == "X":
            labels[(y1, x1)] = ""
            field[y1][x1] = "B"

    # Функция отрисовки поля
    def print_field(text = None):

        result = "     " + " ".join([str(i+1)[0] for i in range(x-1)]) + "\n"

        size_x = len(result) + 2
        size_y = y + 3

        if x-1 > 9:
            part = [str(i)[1] if i > 9 else " " for i in range(x)]
            result += "   " + " ".join(part) + "\n"
            size_y += 1
        for i, j in enumerate(field):
            result += "".join(["   ", str(i).ljust(3)][y > i > 0])
            for n in j:
                result += str(n) + " "
            result += "\n"

        if text != None:
            result += text

        im = Image.new('RGB', (int(6 * size_x + size_x / 2 + 3),
                               int(15 * size_y + size_y / 2 + 15)),
                               color=('white'))
        draw_text = ImageDraw.Draw(im)
        draw_text.text((int(size_x / 3 + 3),
                        int(size_y / 3 + 3)), result, fill=('#1C0606'))
        bytes_io = io.BytesIO()
        im.save(bytes_io, format='PNG')

        return bytes_io.getvalue()

    # Функция хода
    def next_turn():
        pattern = r"([mм]\s)?[1-9]{1}[0-9]?\s[1-9]{1}[0-9]?"
        turn = data_[1]
        if turn == None or not re.fullmatch(pattern, turn):
            return None
        turn = turn.split()
        if int(turn[-2]) > x-1 or int(turn[-1]) > y-1:
            return None
        return [True, turn]

    # Функция проверки на проигрыш
    def loose(y1, x1):
        if main_table[y1][x1] < 0:
            field[y1][x1] = "@"
            client.delete(str(user_id))
            return [True, print_field("YOU LOOSE")]
        else:
            return None

    # Функция проверки на победу
    def win():
        if set(bombs) == set(labels.keys()):
            client.delete(str(user_id))
            return [True, print_field("YOU WIN!")]
        else:
            return None

    def not_end(text = ""):
        cache = [bombs, labels, main_table, field, x, y]
        client.set(str(user_id), cache)
        client.close()
        return print_field(text)


    client = Client('localhost', serde=serde.pickle_serde)
    data = client.get(str(user_id))

    if data == None:
        data = await first_start()
        if data[0] == True:
            client.close()
            return [data[1]]
        elif data[0] == False:
            client.close()
            return ["Переданы неподходящие значения."]

    bombs, labels, main_table, field, x, y = data
    flag = None
    turn = next_turn()

    if turn == None:
        if first_move:
            first_move = False
            return [not_end("FIRST TURN"), True]
        else:
            client.close()
            return ["Переданы неподходящие значения, попробуйте ещё раз."]

    if turn[1][0] in "mм":
        put_label(int(turn[1][2]), int(turn[1][1]))
        check = win()
    else:
        open_field(int(turn[1][1]), int(turn[1][0]))
        check = loose(int(turn[1][1]), int(turn[1][0]))

    if check != None:
        flag = check[0]
        client.close()
        return [check[1], True]
    else:
        return [not_end(), True]
