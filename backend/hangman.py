import random
import json

class Hangman:
    def __init__(self, difficulty="medium"):
        self.difficulty = difficulty.lower()
        self.words = self.load_words()
        self.question, self.word, self.hint = self.choose_word()
        self.guessed_letters = set()
        self.turns_left = 8 if self.difficulty == "hard" else 10
        self.stage = 0
        self.hints_used = 0
        self.max_hints = 2

    def load_words(self):
        try:
            with open("words.txt", "r") as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Failed to load words: {str(e)}")

    def choose_word(self):
        valid_words = [entry for entry in self.words if entry["difficulty"] == self.difficulty]
        if not valid_words:
            valid_words = self.words  # Fallback to all words
        choice = random.choice(valid_words)
        return choice["question"], choice["word"], choice["hint"]

    def display_word(self):
        return " ".join(letter if letter in self.guessed_letters else "_" for letter in self.word)

    def guess(self, letter):
        letter = letter.upper()
        if len(letter) != 1 or not letter.isalpha():
            return False, "Please enter a single letter."
        if letter in self.guessed_letters:
            return False, "You already guessed that letter."
        
        self.guessed_letters.add(letter)
        if letter not in self.word:
            self.turns_left -= 1
            self.stage = max(0, min(10 - self.turns_left, 10))
            return False, "Wrong guess!"
        return True, "Correct guess!"

    def use_hint(self):
        if self.turns_left <= 1:
            return False, "Not enough turns to use a hint!"
        if self.hints_used >= self.max_hints:
            return False, "No hints left!"
        
        self.hints_used += 1
        self.turns_left -= 1
        self.stage = max(0, min(10 - self.turns_left, 10))
        return True, f"Hint revealed: {self.hint}"

    def is_game_over(self):
        if self.turns_left <= 0:
            return True, f"You lose! The answer was {self.word}."
        if all(letter in self.guessed_letters for letter in self.word):
            return True, "Congratulations, you win!"
        return False, ""

    def get_turns_left(self):
        return f"{self.turns_left} turns left"

    def get_stage(self):
        return self.stage

    def get_hint(self):
        return self.hint if self.hints_used > 0 else "Use a hint to reveal more!"

    def get_question(self):
        return self.question