# /// script
# dependencies = [
#   "httpx",
# ]
# ///

import argparse
import asyncio
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

import httpx

TODAY_YMD = datetime.now().strftime('%Y-%m-%d')

# From https://gist.github.com/dracos/dd0668f281e685bad51479e5acaadb93#file-valid-wordle-words-txt
ALL_WORDS_PATH = Path(__file__).parent / 'wordle_valid_answers.txt'
DONE_WORDS_PATH = Path(__file__).parent / 'wordle_previous_answers.txt'


def existing_file(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f'File does not exist: {path}')
    return path


async def get_today():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'https://www.nytimes.com/svc/wordle/v2/{TODAY_YMD}.json'
        )

        solution = response.json()['solution']
        print(f'Todays Answer: {solution.upper()}')


def check_possible_words(
    word_list: set[str],
    correct_positions: dict[str, int | list[int]],
    incorrect_positions: dict[str, int | list[int]],
    excluded_letters: set[str],
    required_letter_counts: dict[str, int],
) -> list[str]:
    """
    Filters the word list based on required and forbidden letter positions, included and excluded letters.

    Args:
        word_list (list[str]): List of words to filter.
        correct_positions (dict[str, int | list[int]]): Dictionary of letters with required positions.
        incorrect_positions (dict[str, int | list[int]]): Dictionary of letters with forbidden positions.
        include_letters (list[str]): List of letters that must be included in the word.
        excluded_letters (list[str]): List of letters that must not be included in the word.

    Returns:
        list[str]: List of words that match the criteria.
    """

    correct_positions = {
        letter.upper(): positions for letter, positions in correct_positions.items()
    }
    incorrect_positions = {
        letter.upper(): positions for letter, positions in incorrect_positions.items()
    }
    include_letters = list(incorrect_positions.keys()) + list(correct_positions.keys())
    excluded_letters = {letter.upper() for letter in excluded_letters}

    required_letter_counts = {
        letter.upper(): count for letter, count in required_letter_counts.items()
    }

    def is_valid_word(word: str) -> bool:
        if len(word) != 5:
            return False

        if any(letter in word for letter in excluded_letters):
            return False

        if any(letter not in word for letter in include_letters):
            return False

        word_counter = Counter(word)
        for letter, required_count in required_letter_counts.items():
            if word_counter[letter] != required_count:
                return False

        # Check required positions
        for letter, positions in correct_positions.items():
            if isinstance(positions, int):
                if word[positions - 1] != letter:
                    return False
            elif isinstance(positions, list):
                if any(word[pos - 1] != letter for pos in positions):
                    return False

        # Check forbidden positions
        for letter, positions in incorrect_positions.items():
            if isinstance(positions, int):
                if word[positions - 1] == letter:
                    return False
            elif isinstance(positions, list):
                if any(word[pos - 1] == letter for pos in positions):
                    return False

        return True

    return sorted(word for word in word_list if is_valid_word(word))


def get_args() -> argparse.Namespace:
    args = argparse.ArgumentParser(description='Wordle Helper')
    args.add_argument(
        '-c',
        '--config',
        type=existing_file,
        default=f'{Path(__file__).stem}.json',
        help='Path to the game configuration file.',
    )
    args.add_argument(
        '-e',
        '--exclude-file',
        type=existing_file,
        default=DONE_WORDS_PATH.resolve(),
        help='Path to the excluded letters file.',
    )
    args.add_argument(
        '-a', '--answer', action='store_true', help='Get the answer for today.'
    )
    return args.parse_args()


def main():
    config = get_args()

    if config.answer:
        asyncio.run(get_today())
        return

    try:
        game_config = json.load(open(config.config, 'r'))
    except json.decoder.JSONDecodeError as e:
        print(f'Error reading JSON file: {e}')
        return

    valid_word_list = {word.strip() for word in ALL_WORDS_PATH.open('r').readlines()}

    valid_words = check_possible_words(
        valid_word_list,
        correct_positions=game_config.get('correct_positions', {}),
        incorrect_positions=game_config.get('incorrect_positions', {}),
        excluded_letters=set(game_config.get('excluded_letters', [])),
        required_letter_counts=game_config.get('required_letter_counts', {}),
    )
    if config.exclude_file:
        with open(config.exclude_file, 'r') as f:
            excluded_words = {line.strip().upper() for line in f.readlines()}
            print(excluded_words)
            valid_words = sorted(
                word for word in valid_words if word not in excluded_words
            )

    print(f'Possible Words ({len(valid_words)}):')
    for word in valid_words:
        print(f'- {word.upper()}')


if __name__ == '__main__':
    main()
