# /// script
# dependencies = [
#   "nltk",
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
import nltk
from nltk.corpus import words

TODAY_YMD = datetime.now().strftime('%Y-%m-%d')


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
    word_list: list[str],
    correct_positions: dict[str, int | list[int]],
    incorrect_positions: dict[str, int | list[int]],
    include_letters: list[str],
    excluded_letters: list[str],
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

    def is_valid_word(word: str) -> bool:
        if len(word) != 5 or not word.islower():
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
                if all(word[pos - 1] != letter for pos in positions):
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


def retrieve_word_list():
    """
    Retrieves the list of valid words from a remote source or falls back to NLTK.
    """
    try:
        httpx_client = httpx.Client(follow_redirects=True)
        req = httpx_client.get(
            'https://gist.github.com/dracos/dd0668f281e685bad51479e5acaadb93/raw/6bfa15d263d6d5b63840a8e5b64e04b382fdb079/valid-wordle-words.txt',
        )
        req.raise_for_status()
        return list(req.text.splitlines())
    except httpx.HTTPStatusError:
        print('Reverting to NLTK Word List...')
        nltk.download('words', quiet=True)
        return sorted([word for word in words.words() if len(word) == 5])


def main():
    args = argparse.ArgumentParser(description='Wordle Helper')
    args.add_argument(
        '-c',
        '--config',
        type=existing_file,
        default=f'{Path(__file__).stem}.json',
        help='Path to the game configuration file.',
    )
    args.add_argument(
        '-a', '--answer', action='store_true', help='Get the answer for today.'
    )
    config = args.parse_args()

    if config.answer:
        asyncio.run(get_today())
        return

    try:
        game_config = json.load(open(config.config, 'r'))
    except json.decoder.JSONDecodeError as e:
        print(f'Error reading JSON file: {e}')
        return

    word_list = retrieve_word_list()

    correct_positions = game_config.get('correct_positions', {})
    incorrect_positions = game_config.get('incorrect_positions', {})

    include_letters = list(incorrect_positions.keys()) + list(correct_positions.keys())

    valid_words = check_possible_words(
        word_list,
        correct_positions=correct_positions,
        incorrect_positions=incorrect_positions,
        include_letters=include_letters,
        excluded_letters=game_config.get('excluded_letters', []),
        required_letter_counts=game_config.get('required_letter_counts', {}),
    )
    print(f'Possible Words ({len(valid_words)}):')
    for word in valid_words:
        print(f'- {word.upper()}')


if __name__ == '__main__':
    main()
