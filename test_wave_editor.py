import os
import sys
import hashlib

import wave_editor
from wave_editor import *
import wave_helper

global _inputs
global _index
_index = -1

# !!!!!!!!!! CHANGE HERE !!!!!!!!!!
REVERSE_FUNC = wave_editor.reverse
SLOW_FUNC = wave_editor.slow
FAST_FUNC = wave_editor.fast
VOLUME_UP_FUNC = wave_editor.volume_up
VOLUME_DOWN_FUNC = wave_editor.volume_down
BLUR_FUNC = wave_editor.blur
# Turn to False if the above functions get the wav without frame-rate element.
WITH_FRAME_RATE = True
# Turn to False if the above functions get a multiplier parameter.
WITH_PARAM = True

GET_WAV_FUNC = wave_editor.get_wav
COMPOSE_BY_FILE_FUNC = wave_editor.compose_by_file
CALCULATE_SAMPLE_FUNC = wave_editor.calculate_sample
EXIT_MENU_FUNC = wave_editor.exit_menu
MAIN_FUNC = wave_editor.main_menu
# Use sys.exit for exit option (3 in main menu)
USE_SYS_EXIT = True


# !!!!!!!!!! CHANGE HERE END !!!!!!!!!!


def decorate(func):
    def inner_func(wav, *args):
        frame_rate, audio_data = wav
        audio_data = func(audio_data, *args)
        return [frame_rate, audio_data]

    return inner_func


if not WITH_FRAME_RATE:
    REVERSE_FUNC = decorate(REVERSE_FUNC)
    SLOW_FUNC = decorate(SLOW_FUNC)
    FAST_FUNC = decorate(FAST_FUNC)
    VOLUME_UP_FUNC = decorate(VOLUME_UP_FUNC)
    VOLUME_DOWN_FUNC = decorate(VOLUME_DOWN_FUNC)
    BLUR_FUNC = decorate(BLUR_FUNC)


def my_exit(status=0):
    raise SystemExit(status)


def my_input(*args):
    global _index
    _index += 1
    print(end='', *args)
    return _inputs[_index]


def test_get_input():
    temp_input = __builtins__['input']
    __builtins__['input'] = my_input

    global _inputs
    _inputs = [
        '1',
        '',
        'a', '!', '55f', '3',
        'c:\\windows', 'c:\\windows\\write.exe\\', 'c:\\windows\\write.exe',
        'a', 'range ', 'builtins', 'input',
        '4',
        'a', '!', '55f', '5',
        'a', '!', '55f', '6',
    ]
    assert get_input('hi') == '1'
    assert get_input('hi') == ''
    assert get_input('hi', str.isdigit) == '3'
    assert get_input('hi', os.path.isfile) == 'c:\\windows\\write.exe'
    assert get_input('hi', lambda k: k in __builtins__) == 'input'
    assert get_input('hi', error_message='g') == '4'
    assert get_input('hi', str.isdigit, error_message='g') == '5'
    assert get_input('hi', lambda k, d: k in d, '', list(map(str, range(7)))) \
           == '6'

    __builtins__['input'] = temp_input


def test_manage_menu(capsys):
    temp_choose_menu_key = wave_editor.choose_menu_key
    wave_editor.choose_menu_key = lambda k: list(k)[0]

    menu = OrderedDict((
        ('OPTION', {FUNC_KEY: locals}),
    ))
    wave_editor.manage_menu(menu)
    captured = capsys.readouterr()
    assert captured.out == 'OPTION. locals\n'

    menu = OrderedDict((
        ('OPTION', {FUNC_KEY: locals}),
        (2, {FUNC_KEY: range}),
    ))
    wave_editor.manage_menu(menu)
    captured = capsys.readouterr()
    assert captured.out == 'OPTION. locals\n2. range\n'

    menu = OrderedDict((
        ('OPTION', {FUNC_KEY: locals}),
    ))
    wave_editor.manage_menu(menu, 'TITLE')
    captured = capsys.readouterr()
    assert captured.out == 'TITLE\nOPTION. locals\n'

    menu = OrderedDict((
        ('OPTION', {FUNC_KEY: lambda i: i + 1}),
    ))
    ret = wave_editor.manage_menu(menu, 'TITLE', 3)
    captured = capsys.readouterr()
    assert captured.out == 'TITLE\nOPTION. <lambda>\n'
    assert ret == 4

    menu = OrderedDict((
        ('MIN', {FUNC_KEY: min}),
    ))
    ret = wave_editor.manage_menu(menu, 'TITLE', 13, 7)
    captured = capsys.readouterr()
    assert captured.out == 'TITLE\nMIN. min\n'
    assert ret == 7

    menu = OrderedDict((
        ('MIN', {FUNC_KEY: min}),
    ))
    ret = wave_editor.manage_menu(menu, 'TITLE', 7, 13)
    captured = capsys.readouterr()
    assert captured.out == 'TITLE\nMIN. min\n'
    assert ret == 7

    menu = OrderedDict((
        ('OPTION', {FUNC_KEY: print}),
    ))
    ret = wave_editor.manage_menu(menu, 'TITLE', 3, 4, 5)
    captured = capsys.readouterr()
    assert captured.out == 'TITLE\nOPTION. print\n3 4 5\n'
    assert ret is None

    wave_editor.choose_menu_key = temp_choose_menu_key


def test_get_wav(capsys):
    temp_input = __builtins__['input']
    __builtins__['input'] = my_input

    global _index
    _index = -1
    global _inputs
    _inputs = [
        # good
        'Test Samples\\batman_theme_x.wav',
        # non existent files, directory
        'no_file', 'no_dir\\no_file', 'batman_theme_x.wav',
        'Test Samples', 'Test Samples\\batman_theme_x.wav',
        # empty wav
        'Test Samples/empty.wav',
        # wrong suffix - it's OK
        'Test Samples/empty.wav1',
        # absolute path
        os.path.realpath('Test Samples/empty.wav'),
        # bad wav
        'Test Samples/bad1.wav', 'Test Samples/bad2.wav',
        'Test Samples/bad3.wav', 'Test Samples/bad4.wav',
        'Test Samples/empty.txt', 'Test Samples/empty.wav',
    ]
    # good
    ret = GET_WAV_FUNC()
    captured = capsys.readouterr()
    assert captured.out == LOAD_PATH_MESSAGE
    assert ret[0] == 11025
    assert len(ret[1]) == 70464

    # non existent files, directory
    ret = GET_WAV_FUNC()
    captured = capsys.readouterr()
    assert captured.out == \
           (LOAD_PATH_MESSAGE + WRONG_PATH_OR_BAD_WAV_MESSAGE + '\n') * 4 + \
           LOAD_PATH_MESSAGE
    assert ret[0] == 11025
    assert len(ret[1]) == 70464

    # empty wav
    ret = GET_WAV_FUNC()
    captured = capsys.readouterr()
    assert captured.out == LOAD_PATH_MESSAGE
    assert ret[0] == 44100
    assert len(ret[1]) == 0

    # wrong suffix - it's OK
    ret = GET_WAV_FUNC()
    captured = capsys.readouterr()
    assert captured.out == LOAD_PATH_MESSAGE
    assert ret[0] == 44100
    assert len(ret[1]) == 0

    # absolute path
    ret = GET_WAV_FUNC()
    captured = capsys.readouterr()
    assert captured.out == LOAD_PATH_MESSAGE
    assert ret[0] == 44100
    assert len(ret[1]) == 0

    # bad wav
    ret = GET_WAV_FUNC()
    captured = capsys.readouterr()
    assert captured.out == (
            LOAD_PATH_MESSAGE + WRONG_PATH_OR_BAD_WAV_MESSAGE + '\n') * 5 + \
           LOAD_PATH_MESSAGE
    assert ret[0] == 44100
    assert len(ret[1]) == 0

    __builtins__['input'] = temp_input


def test_exit_menu(capsys):
    temp_input = __builtins__['input']
    __builtins__['input'] = my_input

    global _index
    _index = -1
    global _inputs
    _inputs = [
        # good
        'Test Samples\\out.wav',
        # non existent dir, existent file
        'no_dir\\no_file', 'Test Samples\\out.wav',
        # empty wav
        'Test Samples\\out.wav',
        # wrong suffix - it's OK
        'Test Samples\\out',
        # absolute path
        os.path.realpath('Test Samples\\out.wav'),
        # bad wav
        'Test Samples\\out.wav', 'Test Samples\\out.wav',
        'Test Samples\\out.wav', 'Test Samples\\out.wav',
    ]

    good_wav = wave_helper.load_wave('Test Samples\\batman_theme_x.wav')
    bad_wav = [good_wav[0], good_wav[:-1]]

    try:
        # good
        ret = EXIT_MENU_FUNC(good_wav)
        captured = capsys.readouterr()
        assert captured.out == SAVE_PATH_MESSAGE

        # non existent dir, existent file
        ret = EXIT_MENU_FUNC(good_wav)
        captured = capsys.readouterr()
        assert captured.out == SAVE_PATH_MESSAGE + BAD_PARAMETERS_MESSAGE + \
               '\n' + SAVE_PATH_MESSAGE

        # empty wav
        ret = EXIT_MENU_FUNC([44100, []])
        captured = capsys.readouterr()
        assert captured.out == SAVE_PATH_MESSAGE

        # wrong suffix - it's OK
        ret = EXIT_MENU_FUNC(good_wav)
        captured = capsys.readouterr()
        assert captured.out == SAVE_PATH_MESSAGE

        # absolute path
        ret = EXIT_MENU_FUNC(good_wav)
        captured = capsys.readouterr()
        assert captured.out == SAVE_PATH_MESSAGE

        # bad wav
        try:
            ret = EXIT_MENU_FUNC(bad_wav)
        except IndexError:
            captured = capsys.readouterr()
            assert captured.out == (
                    SAVE_PATH_MESSAGE + BAD_PARAMETERS_MESSAGE + \
                    '\n') * 4 + SAVE_PATH_MESSAGE
        else:
            raise AssertionError('Should throw because wav data is incorrect')

    finally:
        for f in ['Test Samples/out.wav', 'Test Samples/out']:
            if os.path.isfile(f):
                os.remove(f)

        __builtins__['input'] = temp_input


def test_compose_by_file():
    ret = COMPOSE_BY_FILE_FUNC('Test Samples/compose1.txt')
    assert len(ret) == 52 * 125
    assert all([i1 == i2 for i1, i2 in ret])
    assert ret[:5] == [[0, 0], [31550, 31550], [-17032, -17032],
                       [-22355, -22355], [29101, 29101]]
    assert ret[-5:] == [[32186, 32186], [-2776, -2776], [-30687, -30687],
                        [19343, 19343], [20245, 20245]]
    to_hash = tuple(map(tuple, ret))
    assert hashlib.md5(bytes(str(to_hash), 'utf8')).hexdigest() == \
           '348b797999cb06c5767d55e4978349d9'

    ret = COMPOSE_BY_FILE_FUNC('Test Samples/compose2.txt')
    assert len(ret) == 56 * 125
    assert all([i1 == i2 for i1, i2 in ret])
    assert ret[:5] == [[0, 0], [20567, 20567], [-32022, -32022],
                       [29288, 29288], [-13577, -13577]]
    assert ret[-5:] == [[8148, 8148], [13577, 13577], [-29288, -29288],
                        [32022, 32022], [-20567, -20567]]
    to_hash = tuple(map(tuple, ret))
    assert hashlib.md5(bytes(str(to_hash), 'utf8')).hexdigest() == \
           '73fb5a5a4cd98a5fc35b4e730ce34ea0'

    ret = COMPOSE_BY_FILE_FUNC('Test Samples/compose3.txt')
    assert ret == []

    ret = COMPOSE_BY_FILE_FUNC('Test Samples/compose4.txt')
    assert ret == []


def test_read_composing_file():
    ret = read_composing_file('Test Samples/compose1.txt')
    assert ret == [('D', 3), ('D', 1), ('E', 4), ('Q', 4), ('F', 4), ('E', 8),
                   ('D', 3), ('D', 1), ('E', 4), ('D', 4), ('A', 4), ('F', 8),
                   ('D', 3), ('D', 1)]

    ret = read_composing_file('Test Samples/compose2.txt')
    assert ret == [('G', 4), ('G', 4), ('C', 4), ('C', 4), ('D', 4), ('D', 4),
                   ('C', 8), ('B', 4), ('B', 4), ('A', 4), ('A', 4), ('G', 8)]

    ret = read_composing_file('Test Samples/compose3.txt')
    assert ret == []

    ret = read_composing_file('Test Samples/compose4.txt')
    assert ret == []


def test_reverse():
    assert REVERSE_FUNC(
        [1000, [[10, 20], [30, 40], [50, 60], [70, 80]]]) == \
           [1000, [[70, 80], [50, 60], [30, 40], [10, 20]]]
    assert REVERSE_FUNC([0, [[10, 20]]]) == \
           [0, [[10, 20]]]
    assert REVERSE_FUNC([3200, [[-100, 100], [-2, -2], [0, 0]]]) == \
           [3200, [[0, 0], [-2, -2], [-100, 100]]]
    assert REVERSE_FUNC([1, [[1, 1], [0, 0]]]) == \
           [1, [[0, 0], [1, 1]]]
    assert REVERSE_FUNC([1, [[111111, 30000], [30000, 111111]]]) == \
           [1, [[30000, 111111], [111111, 30000]]]
    assert REVERSE_FUNC([1, [[1, 0]]]) == \
           [1, [[1, 0]]]
    assert REVERSE_FUNC([1, []]) == \
           [1, []]


def test_slow():
    assert SLOW_FUNC([1000, [[10, 20], [30, 40], [50, 60], [70, 80]]]) == \
           [1000, [[10, 20], [20, 30], [30, 40], [40, 50], [50, 60], [60, 70],
                   [70, 80]]]
    assert SLOW_FUNC([0, [[0, 0], [0, 0], [0, 0], [0, 0]]]) == \
           [0, [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]]
    assert SLOW_FUNC([0, [[-32768, -32768], [32767, 32767]]]) == \
           [0, [[-32768, -32768], [0, 0], [32767, 32767]]]
    assert SLOW_FUNC([0, [[-32768, -32768], [-32768, -32768]]]) == \
           [0, [[-32768, -32768], [-32768, -32768], [-32768, -32768]]]
    assert SLOW_FUNC([0, [[0, 5], [5, 0]]]) == \
           [0, [[0, 5], [2, 2], [5, 0]]]
    assert SLOW_FUNC([0, [[0, 5], [5, 0]]]) == \
           [0, [[0, 5], [2, 2], [5, 0]]]
    assert SLOW_FUNC([0, [[0, 5]]]) == \
           [0, [[0, 5]]]
    assert SLOW_FUNC([0, [[]]]) == \
           [0, [[]]]
    # For divder bigger than 2:
    if WITH_PARAM:
        assert SLOW_FUNC([0, [[0, 5], [5, 0]]], 3) == \
               [0, [[0, 5], [1, 3], [3, 1], [5, 0]]]


def test_fast():
    assert FAST_FUNC([1000, [[10, 20], [30, 40], [50, 60], [70, 80]]]) == \
           [1000, [[10, 20], [50, 60]]]
    assert FAST_FUNC([0, [[1, 1], [0, 0]]]) == \
           [0, [[1, 1]]]
    assert FAST_FUNC([0, [[0, 0]]]) == \
           [0, [[0, 0]]]
    assert FAST_FUNC([0, []]) == \
           [0, []]
    # Multiplier x3
    if WITH_PARAM:
        assert FAST_FUNC([0, [[0, 0], [1, 1], [2, 2], [3, 3]]], 3) == \
               [0, [[0, 0], [3, 3]]]


def test_volume_up():
    assert VOLUME_UP_FUNC([1000, [[10, 20], [30, 40], [50, 60], [70, 80]]]) == \
           [1000, [[12, 24], [36, 48], [60, 72], [84, 96]]]
    assert VOLUME_UP_FUNC([5, [[1, 1], [0, 0]]]) == \
           [5, [[1, 1], [0, 0]]]
    assert VOLUME_UP_FUNC([3, [[32766, -32766], [0, 1], [5, -5]]]) == \
           [3, [[32767, -32768], [0, 1], [6, -6]]]
    assert VOLUME_UP_FUNC([3, [[32766, 32766], [-32760, -32750]]]) == \
           [3, [[32767, 32767], [-32768, -32768]]]
    assert VOLUME_UP_FUNC([3, [[1, 1]]]) == \
           [3, [[1, 1]]]
    assert VOLUME_UP_FUNC([3, [[]]]) == \
           [3, [[]]]
    # With Parameter:
    if WITH_PARAM:
        assert VOLUME_UP_FUNC([3, [[32766, -32766], [0, 1], [5, -5]]], 10) == \
               [3, [[32767, -32768], [0, 10], [50, -50]]]


def test_volume_down():
    assert VOLUME_DOWN_FUNC(
        [1000, [[10, 20], [30, 40], [50, 60], [70, 80]]]) == \
           [1000, [[8, 16], [25, 33], [41, 50], [58, 66]]]
    assert VOLUME_DOWN_FUNC([5, [[1, 1], [0, 0]]]) == \
           [5, [[0, 0], [0, 0]]]
    assert VOLUME_DOWN_FUNC([3, [[32767, -32768], [5, -5]]]) == \
           [3, [[27305, -27306], [4, -4]]]
    assert VOLUME_DOWN_FUNC([16, [[32767, 32767], [-32768, -32768]]]) == \
           [16, [[27305, 27305], [-27306, -27306]]]
    assert VOLUME_DOWN_FUNC([16, [[1, 1]]]) == \
           [16, [[0, 0]]]
    assert VOLUME_DOWN_FUNC([16, [[]]]) == \
           [16, [[]]]
    # With Parameter:
    if WITH_PARAM:
        assert VOLUME_DOWN_FUNC([3, [[32767, -32768], [5, -5]]], 10) == \
               [3, [[3276, -3276], [0, 0]]]


def test_blur():
    assert BLUR_FUNC([1000, [[10, 20], [30, 40], [50, 60], [70, 80]]]) == \
           [1000, [[20, 30], [30, 40], [50, 60], [60, 70]]]
    assert BLUR_FUNC([1000, [[0, 0], [0, 0], [0, 0]]]) == \
           [1000, [[0, 0], [0, 0], [0, 0]]]
    assert BLUR_FUNC([1000, [[1, 1], [1, 1], [1, 1]]]) == \
           [1000, [[1, 1], [1, 1], [1, 1]]]
    assert BLUR_FUNC([1000, [[1, 1], [0, 0]]]) == \
           [1000, [[0, 0], [0, 0]]]
    assert BLUR_FUNC([3, [[32766, -32766], [0, 1], [5, -5]]]) == \
           [3, [[16383, -16382], [10923, -10923], [2, -2]]]
    assert BLUR_FUNC([1000, [[1, 1]]]) == \
           [1000, [[1, 1]]]
    assert BLUR_FUNC([1000, [[]]]) == \
           [1000, [[]]]


def test_calculate_sample():
    assert CALCULATE_SAMPLE_FUNC(frequency=440, index=0, sample_rate=2000,
                                 max_volume=32767) == \
           [0, 0]
    assert CALCULATE_SAMPLE_FUNC(440, 1, 2000, 32767) == \
           [32186, 32186]
    assert CALCULATE_SAMPLE_FUNC(659, 125, 2000, 32767) == \
           [30272, 30272]
    assert CALCULATE_SAMPLE_FUNC(784, 2000, 2000, 32767) == \
           [0, 0]

    # NO OPTIONAL PARAMETERS:
    assert CALCULATE_SAMPLE_FUNC(784, 2000) == \
           [0, 0]
    assert CALCULATE_SAMPLE_FUNC(659, 125) == \
           [30272, 30272]


def test_main(capsys):
    temp_input = __builtins__['input']
    __builtins__['input'] = my_input

    global _index
    _index = -1
    global _inputs
    _inputs = [
        '2',  # compose
        'test samples/hatikva.txt',  # composition path
        '1',  # reverse
        '1',  # reverse
        '2',  # fast
        '3',  # slow
        '4',  # volume up
        '5',  # volume down
        '6',  # blur
        '7',  # exit
        'test samples/hatikva.wav',  # save path
        '3',  # exit all
    ]

    try:
        temp_exit = sys.exit
        sys.exit = my_exit
        MAIN_FUNC()
        sys.exit = temp_exit
    except SystemExit:
        pass
    else:
        if USE_SYS_EXIT:
            raise AssertionError('Should throw on exit.')
    finally:
        try:
            wav = wave_helper.load_wave('test samples/hatikva.wav')
            assert wav[0] == 2000
            to_hash = tuple(map(tuple, wav[1]))
            assert hashlib.md5(bytes(str(to_hash), 'utf8')).hexdigest() == \
                   '15e7c1491799590c6cdc754ebcf24b30'
        finally:
            if os.path.exists('test samples/hatikva.wav'):
                os.remove('test samples/hatikva.wav')

    _index = -1
    _inputs = [
        '2',  # compose
        'test samples/hatikva.txt',  # composition path
        '4',  # volume up
        '7',  # exit
        'test samples/hatikva.wav',  # save path
        '3',  # exit all
    ]

    try:
        temp_exit = sys.exit
        sys.exit = my_exit
        MAIN_FUNC()
        sys.exit = temp_exit
    except SystemExit:
        pass
    else:
        if USE_SYS_EXIT:
            raise AssertionError('Should throw on exit.')
    finally:
        try:
            wav = wave_helper.load_wave('test samples/hatikva.wav')
            assert wav[0] == 2000
            to_hash = tuple(map(tuple, wav[1]))
            assert hashlib.md5(bytes(str(to_hash), 'utf8')).hexdigest() == \
                   '8ddae2be83f75e0d274eeffc04a8c3fd'
        finally:
            if os.path.exists('test samples/hatikva.wav'):
                os.remove('test samples/hatikva.wav')

    __builtins__['input'] = temp_input
