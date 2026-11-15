# Trivia quiz

Answer factual questions against a clock or other players; the core verb is pick the answer before time runs out.
Like Kahoot, Trivia Murder Party or You Don't Know Jack.

**Camera (Unity):** no world camera needed: a Screen Space - Overlay canvas where the question and the answer
choices fill the screen.

**Online:** the first slice is one screen, played alone or by friends taking turns. Phone controllers, remote players
and hosted live shows need a server.

## Defaults

- **choose-an-answer**: A question comes with answer alternatives to choose from. Why: the player answers by
  recognising the fact, with no typing test. Break it when: recall without prompts is the challenge. [kahoot-1]
- **time-to-think**: Each question has an answer timer suited to its complexity. Why: a harder question needs room for
  thought. Break it when: the pitch is an untimed practice quiz. [kahoot-2]
- **checked-answers**: Questions live in a data asset (a ScriptableObject or a localised table), each with its one
  accepted answer checked by hand. Why: one wrong answer key breaks trust in every question. Break it when: there is
  no right answer, a poll of opinions. *(guess)*

## Feel

- **answer-reveal**: The correct answer shows after the question resolves. Why: uncertainty turns into confirmation or
  something learned. Break it when: answers stay hidden until a connected set of questions ends. [kahoot-3]
- **answer-sounds**: Correct and incorrect answers have distinct sounds, with a sound toggle. Why: the result is heard
  as well as read. Break it when: the quiz is silent on purpose. [kahoot-4]
- **finish-with-score**: The quiz ends on the player's final score. Why: the session has a clear result to react to.
  Break it when: the quiz is practice without scoring. [kahoot-5]

## Variants

- **quickfire**: an answer clock keeps each question moving toward its reveal. [kahoot-2], [kahoot-3]
- **reflective**: no timer; the player has time to weigh the alternatives. [kahoot-6]

## Choices that shape the pitch

- **Answering:** choose from written options (default) · type an answer · buzz in before local opponents.
- **Who plays:** alone (default) · local players take turns · local teams discuss an answer · remote players, later.
- **Stakes:** a score at the end (default) · practice without points · wrong answers lead to a separate minigame,
  later.
- **Tone:** a plain quiz (default) · a comic host · a themed game show.
- **Feeling:** the player feels capable by recalling an answer before the reveal confirms it ([kahoot-3]).

## Platforms

- PC: click an answer, or press 1-4. Touch: tap an answer; the answer buttons sit in the lower half, in thumb reach.
- Phone: portrait. Long questions and long translations must fit the box (TMP auto-size with a minimum size).
- A quiz is 3-10 min on both *(guess)*.

## Later

- More topics, difficulty bands and fresh question sets.
- Local buzzers and team turns.
- Spoken hosting and jokes tied to answers.
- Typed answers that accept spelling and phrasing alternatives.
- Elimination minigames and a comeback finale.
- Phone controllers, remote matches and live shows (needs a server).

## In a mashup

The quiz leads questions, accepted answers and the reveal. A party half leads joining and round scores. A horror half
leads the host and consequences. An adventure half supplies places and topics. A word half leads spelling when
answers are typed; factual knowledge and spelling need separate rules, so the player knows what the question tests.
