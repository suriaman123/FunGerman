#  FunGerman

Fun German is a colourful and interactive language-learning gaming platform, focused on helping users learn German through fun mini-games.

The first game in the platform is ** Atlas**, a competitive word-chain game where users battle against an AI opponent using German vocabulary.

The project is designed to eventually expand into:
- Multiple language-learning games
- Mobile applications
- Multiplayer mode
- AI-powered learning assistant
- Vocabulary tracking and progress systems

---

# ✨ Features

## 🎯 German Atlas Game

### Core Gameplay
- User vs Computer
- Coin toss decides who starts
- Word-chain gameplay:
  - Every new word must start with the final letter of the previous word
- Time-based gameplay:
  - Users have **60 seconds** to answer
- 3-heart life system
- Surrender option

---

# 🧠 Difficulty Levels

The AI opponent only uses vocabulary from the selected CEFR German level and below:
- A1
- A2
- B1
- B2
- C1
- C2

Example:
If AI difficulty is set to A2, the computer can ONLY use A2 and lower vocabulary.

Users can use:
- Any valid German word
- Regardless of level

---

# 🪙 Coin Toss System

Before the match:
1. User chooses Heads or Tails
2. Coin flips
3. Winner starts

If User Wins:
- User receives 5 random German starting letters
- User chooses a starting word

If Computer Wins:
- The computer provides the first word

---

# ❤️ Life System

Users start with:
❤️ ❤️ ❤️

User loses one heart when:
- Word is invalid
- Word does not start with the correct letter
- Timer reaches 0

Game Over after losing all 3 hearts.

---

# 🤖 Smart AI Rules

The AI:
- Uses only words from the selected CEFR level
- Searches for valid next words
- Concedes if no valid word exists

---

# 📖 Interactive Vocabulary Cards

When users click on a computer-generated word:

A  vocabulary pop-up card appears with:
- German word
- English translation
- Word type (noun, verb, adjective)
- Example sentence
- Pronunciation
- Audio playback
- Difficulty level
- Optional image/illustration

Example:

Word: Hund  
Meaning: Dog  
Sentence: "Der Hund spielt im Garten."

---








# 🧩 Additional Features (Working on it)

## 🔊 Pronunciation Audio
Click any word to hear native pronunciation.

---

## 🏆 XP & Leveling System
Users earn:
- XP
- Coins
- Streak bonuses
- Achievements

---

## 🔥 Daily Streaks
Reward users for daily practice.

---

## 🧠 Smart Hints
Players can use hint tokens to:
- Reveal first letter
- Show possible words

---

## 🌍 Multiplayer Mode (Future)
- Real-time battles
- Friends leaderboard
- Ranked matches

---

## 👦 Kids Mode
- Simpler words
- Slower timer
- Bigger buttons
- Friendly animations

---

#  Tech Stack

## Frontend
- React.js
- Next.js
- CSS
- Framer Motion

## Backend
- Node.js
- Express.js

## Database
- SQL

## AI / Language Processing
- OpenAI API
- German dictionary APIs
- CEFR vocabulary datasets

---

# 🧠 Word Validation Logic

When user enters a word:

## Validation Steps
1. Check if timer expired
2. Check if word starts with required letter
3. Check if word exists in German dictionary
4. Check if word was already used
5. Save move history
6. Generate AI response

