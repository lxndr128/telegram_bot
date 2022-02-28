async def module(function):
    helpdict = {
                None: "Бот, который делает всякое.\n\nЧтобы узнать о конкретной"
                  " функции, напишите: 'help имя_функции'.\n\n"
                  "Чтобы увидеть список функций, напишите что-то кроме.",

                "cat": "Функция, которая присылает разные картинки.\n\n"
                 "'cat something' пришлёт случайное изображение на тему 'something'. ",

                "weather": "Функция, которая присылает информацию о погоде.\n\n"
                 "Ещё не доделана.\n\nПринимает имена городов на английском языке,"
                 " например 'weather London'. Пользуйтесь на свой стах и риск. ",

                "echo": "Функция, которая возвращает текст, что вы ей передали.\n\n"
                 "'echo some_text' вернёт 'some_text'. ",

                "help": "Очень умно.",

                "default_answer": "Присылает список функций. Вызывается всякий "
                 "раз, когда вы пишете что-то непонятное.",

                "minesweeper": "Игра 'Сапёр'. Чтобы начать, напишите:\n\n"
                 "  minesweeper x y z\n\n"
                 "Например:\n\n  minesweeper 20 25 40\n\n"
                 "x - размер поля по горизонтали\n"
                 "y - размер поля по вертикали\n"
                 "z - количество бомб\n"
                 "x и y - числа с одним или двумя знаками\n"
                 "Должно соблюдаться условие:\nz <= (x * y / 2) <= 450\n\n"
                 "Чтобы открыть клетку, напишите:\n\n"
                 "  x y\n\n"
                 "Например:\n\n  11 15\n\n"
                 "Чтобы поставить или снять метку, напишите:\n\n"
                 "  'm' или 'м' x y\n\n"
                 "Например:\n\n  m 9 11\n\n"
                 "Чтобы выйти, напишите:\n\n"
                 "  quit"
                }
    return [helpdict.get(function[1], "Такой функции ещё нет.")]
