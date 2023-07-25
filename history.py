from typing import List

HISTORY_FILE = 'history.txt'


def get_history(username: str) -> str:
    """ Get History by Username """
    results = []
    with open(HISTORY_FILE) as fr:
        for line in fr:
            if username in line:
                results.append(line)
    return ''.join(results)


def add_command(username: str, command: str) -> None:
    """ Add Command to a History file """
    with open(HISTORY_FILE, 'a') as fw:
        fw.write('%s: %s' % (username, command))


def history(username: str) -> str:
    """ Main function """
    return 'OK'
