import random
import string
import urllib.request
import urllib.error
import json

# ----------------------------------------------------------------------
# Difficulty configuration: (label, min_len, max_len, max_wrong_attempts)
# ----------------------------------------------------------------------
DIFFICULTY_LEVELS = {
    "1": {"name": "Easy",   "min_len": 3, "max_len": 5, "attempts": 8},
    "2": {"name": "Medium", "min_len": 6, "max_len": 8, "attempts": 6},
    "3": {"name": "Hard",   "min_len": 9, "max_len": 12, "attempts": 5},
}

# Offline fallback word banks (used if the API call fails / no internet)
FALLBACK_WORDS = {
    "Easy": ["cat", "dog", "sun", "book", "tree", "rain", "blue", "game"],
    "Medium": ["python", "guitar", "planet", "orange", "bridge", "castle"],
    "Hard": ["adventure", "chocolate", "wonderful", "beautiful", "hangmanquiz"],
}

# ASCII art stages for the hangman drawing (7 stages, index = wrong guesses)
HANGMAN_STAGES = [
    """
      +---+
      |   |
          |
          |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
          |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|\\  |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|\\  |
     /    |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|\\  |
     / \\  |
          |
    =========""",
]


def fetch_word_from_api(min_len, max_len):
    """
    Try to fetch a random word within the given length range from a public
    word API. Returns None if the API is unreachable or returns nothing
    usable, so the caller can fall back to the offline word bank.
    """
    # Try a couple of lengths within the range so the API has a decent
    # chance of returning a match (some APIs need an exact length).
    for target_len in range(min_len, max_len + 1):
        url = f"https://random-word-api.herokuapp.com/word?number=1&length={target_len}"
        try:
            with urllib.request.urlopen(url, timeout=4) as response:
                data = json.loads(response.read().decode("utf-8"))
                if data and isinstance(data, list):
                    word = data[0].strip().lower()
                    if word.isalpha() and min_len <= len(word) <= max_len:
                        return word
        except (urllib.error.URLError, urllib.error.HTTPError,
                TimeoutError, json.JSONDecodeError, ValueError, IndexError):
            continue
    return None


def get_word(difficulty_name, min_len, max_len):
    """Get a random word from the API, falling back to a local list."""
    word = fetch_word_from_api(min_len, max_len)
    if word:
        return word, "API"
    # Fallback to offline list
    return random.choice(FALLBACK_WORDS[difficulty_name]), "offline list"


def choose_difficulty():
    print("\nChoose a difficulty level:")
    for key, level in DIFFICULTY_LEVELS.items():
        print(f"  {key}. {level['name']}  "
              f"(word length {level['min_len']}-{level['max_len']}, "
              f"{level['attempts']} wrong guesses allowed)")

    while True:
        choice = input("Enter 1, 2, or 3: ").strip()
        if choice in DIFFICULTY_LEVELS:
            return DIFFICULTY_LEVELS[choice]
        print("Invalid choice. Please enter 1, 2, or 3.")


def display_status(word, guessed_letters, wrong_guesses, max_attempts):
    print(HANGMAN_STAGES[min(wrong_guesses, len(HANGMAN_STAGES) - 1)])
    display_word = " ".join(
        letter if letter in guessed_letters else "_" for letter in word
    )
    print(f"\nWord: {display_word}")
    print(f"Attempts left: {max_attempts - wrong_guesses}")
    used = ", ".join(sorted(guessed_letters)) if guessed_letters else "(none yet)"
    print(f"Guessed letters: {used}")


def get_valid_guess(guessed_letters):
    while True:
        guess = input("\nGuess a letter: ").strip().lower()
        if len(guess) != 1 or guess not in string.ascii_lowercase:
            print("Please enter a single letter (a-z).")
            continue
        if guess in guessed_letters:
            print("You already guessed that letter. Try another.")
            continue
        return guess


def play_round(word, max_attempts):
    guessed_letters = set()
    wrong_guesses = 0

    while wrong_guesses < max_attempts:
        display_status(word, guessed_letters, wrong_guesses, max_attempts)

        if all(letter in guessed_letters for letter in word):
            print(f"\nYou won! The word was '{word}'.")
            return True

        guess = get_valid_guess(guessed_letters)
        guessed_letters.add(guess)

        if guess in word:
            print(f"Good guess! '{guess}' is in the word.")
        else:
            wrong_guesses += 1
            print(f"Sorry, '{guess}' is not in the word.")

    display_status(word, guessed_letters, wrong_guesses, max_attempts)
    print(f"\nYou ran out of attempts! The word was '{word}'.")
    return False


def main():
    print("=" * 50)
    print(" Welcome to Advanced Hangman!")
    print("=" * 50)

    wins, losses = 0, 0

    while True:
        level = choose_difficulty()
        print("\nFetching a word for you...")
        word, source = get_word(level["name"], level["min_len"], level["max_len"])
        print(f"(Word source: {source})")

        won = play_round(word, level["attempts"])
        if won:
            wins += 1
        else:
            losses += 1

        print(f"\nScore so far -> Wins: {wins} | Losses: {losses}")

        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != "y":
            print("\nThanks for playing! Final score -> "
                  f"Wins: {wins}, Losses: {losses}")
            break


if __name__ == "__main__":
    main()