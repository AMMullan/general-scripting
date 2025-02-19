# /// script
# dependencies = [
#   "nltk",
#   "httpx",
# ]
# ///

import asyncio
import json
from datetime import datetime

import httpx
import nltk
from nltk.corpus import words

game_config = json.load(open('wordle_game_config.json', 'r'))


async def get_today():
    async with httpx.AsyncClient() as client:
        today_ymd = datetime.now().strftime('%Y-%m-%d')
        response = await client.get(
            f'https://www.nytimes.com/svc/wordle/v2/{today_ymd}.json'
        )

        solution = response.json()['solution']
        print(f'Todays Answer: {solution}')


httpx_client = httpx.Client(follow_redirects=True)

req = httpx_client.get(
    'https://gist.github.com/dracos/dd0668f281e685bad51479e5acaadb93/raw/6bfa15d263d6d5b63840a8e5b64e04b382fdb079/valid-wordle-words.txt',
)
req.raise_for_status()
word_list = list(req.text.splitlines())
if not word_list:
    print('Reverting to NLTK Word List...')
    nltk.download('words', quiet=True)
    word_list = words.words()


def check_possible_words(
    word_list: list[str],
    required_positions: dict[str, int | list[int]],
    forbidden_positions: dict[str, int | list[int]],
    include_letters: list[str],
    excluded_letters: list[str],
) -> list[str]:
    """
    Filters the word list based on required and forbidden letter positions, included and excluded letters.

    Args:
        word_list (list[str]): List of words to filter.
        required_positions (dict[str, int | list[int]]): Dictionary of letters with required positions.
        forbidden_positions (dict[str, int | list[int]]): Dictionary of letters with forbidden positions.
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

        # Check required positions
        for letter, positions in required_positions.items():
            if isinstance(positions, int):
                if word[positions - 1] != letter:
                    return False
            elif isinstance(positions, list):
                if all(word[pos - 1] != letter for pos in positions):
                    return False

        # Check forbidden positions
        for letter, positions in forbidden_positions.items():
            if isinstance(positions, int):
                if word[positions - 1] == letter:
                    return False
            elif isinstance(positions, list):
                if any(word[pos - 1] == letter for pos in positions):
                    return False

        return True

    return sorted(word for word in word_list if is_valid_word(word))


valid_words = check_possible_words(
    word_list,
    required_positions=game_config.get('required_positions', {}),
    forbidden_positions=game_config.get('forbidden_positions', {}),
    include_letters=game_config.get('include_letters', []),
    excluded_letters=game_config.get('excluded_letters', []),
)
for word in valid_words:
    print(f'- {word}')


want_answer = input('\nWant Todays Word? [Y|n] (default: n): ')
if want_answer == 'Y':
    asyncio.run(get_today())
