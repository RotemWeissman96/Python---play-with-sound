from wave_helper import *
import math
import os

EDIT_MENU = {"REVERS": "1", "MINUS": "2", "FAST FORWARD": "3", "SLOW_DOWN":
             "4", "VOLUME_UP": "5", "VOLUME_DOWN": "6", "LOW_PASS_FILTER": "7",
             "FINISH_EDIT": "8"}
START_MENU = {"EDIT_AUDIO": "1", "CREATE_AUDIO": "2", "CLOSE": "3"}
FREQUENCY_DIC = {"A": 440, "B": 494, "C": 523, "D": 587, "E": 659, "F": 698,
                 "G": 784, "Q": 0}
PI = math.pi
DEFAULT_SAMPLE_RATE = 2000
MAX_VALUE = 32767
MIN_VALUE = -32768


def get_existing_file_content():
    """
    asks the user to enter a file name to load. check if the file name is
    valid, if the file name is valid, the function will read it and return a
    list of pairs with the instructions to create a wav file
    :return: list of pairs containing the instructions to create new wav file
    """
    while True:
        file_name = input("Enter txt file name to get the instruction list")
        if not os.path.isfile(file_name):
            print("wrong file name")
            continue
        with open(file_name, "r") as f:
            sound_list = f.read().split()
        break
    return sound_list


def read_input_file():
    """
    read a file and save it's content in a list of list of pairs
    check that all the content is valid
    :return: the complete list of instructions in order to create wav file
    """
    instructions = []
    sound_list = get_existing_file_content()
    for i in range(0, len(sound_list), 2):
        instructions.append([sound_list[i], int(sound_list[i+1])])
    return instructions


def adding_single_sound(audio_data, new_pair):
    """
    adds a new sound for the list of sounds from 1 pair of frequency and
    time data.
    :param audio_data: the current list of data (list of lists)
    :param new_pair: pair of the new frequency and time data we want to add
    (list)
    :return: None
    """
    number_of_samples = int(new_pair[1] * DEFAULT_SAMPLE_RATE / 16)
    if new_pair[0] == "Q":
        for i in range(number_of_samples):
            audio_data.append([0, 0])
    else:
        samples_per_second = DEFAULT_SAMPLE_RATE/FREQUENCY_DIC[new_pair[0]]
        for i in range(number_of_samples):
            value = int(MAX_VALUE*(math.sin((PI*2*i)/samples_per_second)))
            audio_data.append([value, value])


def create_audio():
    """
    create a new audio file from a given txt file full of instructions
    then send the user to the edit menu to edit the wav file that was created
    :return: None
    """
    audio_data = []
    instructions = read_input_file()
    for pair in instructions:
        adding_single_sound(audio_data, pair)
    edit_menu(audio_data)


def average_pairs(list_of_lists):
    """
    gets list of pairs and calculate the average of all the first argument
    in all pairs as well as the second one
    returns a pair with the averages
    :param list_of_lists: list of lists
    :return: average (list)
    """
    if not list_of_lists:  # if list is empty
        return []
    average = [0, 0]
    for pair in range(len(list_of_lists)):
        average[0] += list_of_lists[pair][0]
        average[1] += list_of_lists[pair][1]
    average[0] = int(average[0]/len(list_of_lists))
    average[1] = int(average[1]/len(list_of_lists))
    return average


def change_volume(audio_data, coefficient):
    """
    change the volume of the data according to a given coefficient
    :param audio_data: original data
    :param coefficient: coefficient to multiply with
    :return: the changed list of data
    """
    changed_data = []
    for pair in audio_data:
        changed_data.append([int(pair[0] * coefficient), int(pair[1] *
                                                             coefficient)])
    return changed_data


def reverse_filter(audio_data):
    """
    reverse the order of the values in the audio data list
    :param audio_data: list of lists
    :return: reversed_audio_data (list of lists)
    """
    new_audio_data = audio_data[::-1]
    return new_audio_data


def minus_filter(audio_data):
    """
    replace all the audio data with minus of the current audio data
    :param audio_data:
    :return: the new negated audio data list
    """
    minus_audio_data = []
    for pair in audio_data:
        pair = [MAX_VALUE if i == MIN_VALUE else i * -1 for i in pair]
        # negate the values and make sure that the values won't exceed the
        # value limit
        minus_audio_data.append(pair)
    return minus_audio_data


def fast_forward_filter(audio_data):
    """
    deleting every second pair of values, "passing" the odd indexes.
    :param audio_data:
    :return: the new faster audio data list
    """
    new_audio_data = audio_data[::2]
    return new_audio_data


def slow_down_filter(audio_data):
    """
    adds the average of every pair of values between them. The first one is
    the average of the firsts ones and the second of the seconds.
    :param audio_data: list of lists
    :return: new_audio_data: list of lists
    """
    new_audio_data = []
    for i in range(len(audio_data)*2 - 1):
        if i % 2 == 0:
            new_audio_data.append(audio_data[i//2])
        else:
            new_audio_data.append(average_pairs([audio_data[i//2],
                                                 audio_data[i//2 + 1]]))
    return new_audio_data


def volume_up_filter(audio_data):
    """
    turn up the audio by 1.2 (multiplying the data in the list)
    :param audio_data: list of lists
    :return: changed audio data
    """
    changed_data = change_volume(audio_data, 1.2)
    for pair in range(len(changed_data)):  # check if all the values are valid
        if changed_data[pair][0] > MAX_VALUE:
            changed_data[pair][0] = MAX_VALUE
        elif changed_data[pair][0] < MIN_VALUE:
            changed_data[pair][0] = MIN_VALUE
        if changed_data[pair][1] > MAX_VALUE:
            changed_data[pair][1] = MAX_VALUE
        elif changed_data[pair][1] < MIN_VALUE:
            changed_data[pair][1] = MIN_VALUE
    return changed_data


def volume_down_filter(audio_data):
    """
    turn down the audio by 1.2 (dividing the data in the list)
    :param audio_data: list of pairs
    :return: changed audio data
    """
    return change_volume(audio_data, 1/1.2)


def low_pass_filter(audio_data):
    """
     changes the audio data into an averages version of it. changing "i" index
     pair into the average pair of "i","i-1" and "i+1" pairs.
    :return: changed audio data
     """
    if len(audio_data) <= 1:
        return audio_data
    new_audio_data = [average_pairs(audio_data[:2])]  # first in new list
    for i in range(1, len(audio_data)-1):
        new_audio_data.append(average_pairs(audio_data[i-1:i+2]))
    new_audio_data.append(average_pairs((audio_data[-2:])))  # last in new list
    return new_audio_data


def finish_and_save(final_audio_data, sample_rate):
    """
    saves the file after the changes
    :param final_audio_data: list of the data (list of lists)
    :param sample_rate: number of pairs in second (default 2000) (int)
    :return: None
    """
    while save_wave(sample_rate, final_audio_data,
                    input("Enter filename to save the wav file")) == -1:
        print("there was a problem with your file name")


def load_audio():
    """
    loads the audio data and the sample rate from the given file. if the
    file. it checks if the file doesnt exists and if the file is ok (using
    the function load_wave)
    :return: file_data - the data from the given file. (list)
    """
    while True:
        filename = input("Please enter the name of the file you want to "
                         "modify")
        file_data = load_wave(filename)
        if file_data == -1:
            print("there was a problem with your file content or type")
            continue
        return file_data


def edit_menu(audio_data=None, sample_rate=DEFAULT_SAMPLE_RATE):
    """
    gets the user's file and present the menu of changes the user can do in
    his file. activate the wanted function until the user choose to stop
    modifying his file.
    :param audio_data: the current audio data, if the user hasn't given the
    filename yet the default is None and the function asks for the filename
    (list of lists)
    :param sample_rate: the sample rate of the given file if already given,
    if not given it's default is 2000 (int)
    :return: None
    """
    if audio_data is None:
        sample_rate, audio_data = load_audio()
    while True:
        while True:
            choose = input("Choose the way you want to modify your file: ("
                           "enter the number of the option)\n1. Reverse\n2. "
                           "Negation\n3. Fast Forward\n4. Slow Down\n5. "
                           "Volume Up\n6. Volume Down\n7. Low Pass\n8. Back "
                           "To Start Menu")
            if choose in EDIT_MENU.values():  # if input is valid proceed
                # beyond the while loop
                break
            print("Please enter a number between 1-8")
        if choose == EDIT_MENU["REVERS"]:
            audio_data = reverse_filter(audio_data)
            print("Successfully done the Reverse change")
        elif choose == EDIT_MENU["MINUS"]:
            audio_data = minus_filter(audio_data)
            print("Successfully done the Negation change")
        elif choose == EDIT_MENU["FAST FORWARD"]:
            audio_data = fast_forward_filter(audio_data)
            print("Successfully done the Fast Forward change")
        elif choose == EDIT_MENU["SLOW_DOWN"]:
            audio_data = slow_down_filter(audio_data)
            print("Successfully done the Slow Down change")
        elif choose == EDIT_MENU["VOLUME_UP"]:
            audio_data = volume_up_filter(audio_data)
            print("Successfully done the Volume Up change")
        elif choose == EDIT_MENU["VOLUME_DOWN"]:
            audio_data = volume_down_filter(audio_data)
            print("Successfully done the Volume down change")
        elif choose == EDIT_MENU["LOW_PASS_FILTER"]:
            audio_data = low_pass_filter(audio_data)
            print("Successfully done the Low Pass change")
        else:
            finish_and_save(audio_data, sample_rate)
            break
        print(audio_data)


def start_menu():
    """
    the main menu. opened when the user starts the program and when he
    finishes editing a file.
    giving the user options to edit sound, to create sound or to exit the
    program.
    :return: None
    """
    while True:
        while True:
            print("Welcome to the wave editor.\nPlease select one of the "
                  "options below:(enter the number of the option).\n1. "
                  "Change wav file.\n2. Compose new melody in wav "
                  "format.\n3. Exit "
                  "the program")
            choose = input()
            if choose in START_MENU.values():  # if input is valid proceed
                # beyond the while loop
                break
            print("Please enter a number between 1-3")
        if choose == START_MENU['EDIT_AUDIO']:
            edit_menu()
        elif choose == START_MENU['CREATE_AUDIO']:
            create_audio()
        else:
            break


if __name__ == '__main__':
    edit_menu([[555, 333], [2222, 10000]], 2000)