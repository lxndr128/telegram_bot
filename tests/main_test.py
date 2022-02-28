import pytest
import pytest_asyncio
import requests
import asyncio
import io
from unittest import mock
import sys
sys.path.append("..")
from main import get_messages, process_messages
from lib.help import module as help
from lib.default_answer import module as default_answer


@pytest.fixture()
def for_post():
    class RightJson():
        def json(*args):
            return({'result': 1})

    class WrongJson():
        def json(*args):
            raise Exception("Test")
    return [RightJson(), WrongJson()]

@pytest.fixture()
def for_open():
    class Open():
        def __enter__(self, *args):

            class Write():
                def write(*arg):
                    global text_exc
                    text_exc = arg[1]

            self.result = Write()
            return self.result
        def __exit__(*args):
            pass
    return Open()

@pytest.fixture
def messages_cases(event_loop):
    global RESULTS
    RESULTS = []
    texts = []

    async def help_():
        nonlocal texts
        texts.append(await help(['', None]))
        texts.append(await help(['', 'minesweeper']))
        texts.append(await default_answer())

    event_loop.run_until_complete(help_())

    case_1 = [{'update_id': 22, 'message': {'from':{'id': 1}, 'text':"echo"}},
              {'update_id': 23, 'message': {'from':{'id': 2}, 'text':"help"}},
              {'update_id': 24, 'message': {'from':{'id': 3}, 'text':"minesweeper"}},
              {'update_id': 25, 'message': {'from':{'id': 4}, 'text':"8H38fhn"}},
              {'update_id': 26, 'not_message': "12345"}]

    result_case_1 = [[1, 'echo'],
                     [2,  *texts[0]],
                     [3,  texts[1]],
                     [4,  *texts[2]]]

    return [case_1, result_case_1]

@pytest.fixture()
def for_send_response():
    async def resp(id, text):
        RESULTS.append([id, text])
        return True
    return resp

@mock.patch('requests.post')
def test_get_messages_normal(req_p, for_post):
    req_p.return_value = for_post[0]
    assert get_messages() == 1

@mock.patch('requests.post')
@mock.patch('builtins.open')
def test_get_messages_deviation(open_, req_p, for_post, for_open):
    open_.return_value = for_open
    req_p.return_value = for_post[1]
    assert get_messages() == []
    assert text_exc[:4] == "Test"

@mock.patch('main.send_response')
def test_process_messages(send_r, messages_cases, for_send_response):
    send_r.side_effect = for_send_response
    process_messages(messages_cases[0])
    assert messages_cases[1] == RESULTS
