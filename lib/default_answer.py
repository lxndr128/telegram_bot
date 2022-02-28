import os

IGNORE_LIST = ['default_answer.py', 'database.py', 'weather.py']

async def module(*args):
    lib_list = os.listdir(os.environ["PATH_TO_BOT"] + '/lib')
    functions = []
    for i in lib_list:
        if ".py" in i and i not in IGNORE_LIST:
            functions.append(i[:-3])
    list_ = "\n- ".join(sorted(functions))
    return [f"Список функций: \n- { list_ }\n \n Для справки введите: 'help'"]
