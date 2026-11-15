# Rhythm

Press inputs in time with a song; the core verb is hit on the beat.

**Camera (Unity):** one fixed orthographic camera on flat lanes; a fixed perspective camera on a 3D note highway;
a top-down camera for moving on a grid to the beat.

## Defaults

- **first-song-teaches**: The first song starts with single notes on the strong beats, then adds off-beats
  and holds, and ends on a burst. Why: the player learns the song's language within one song. Break it when:
  an expert chart for players who know the genre.
- **tap-to-calibrate**: A short tap test before the first song sets this device's delay, and the delay moves
  the judging, not only the sound. Why: TVs, Bluetooth headphones and phone audio add delay that makes every
  hit feel late. Break it when: the windows are so wide a small delay cannot be felt.
- **combo-counter**: A combo count and the score sit beside the notes, and a miss resets the combo. Why:
  a streak becomes something to protect. Break it when: each short scene is graded pass or fail as a whole.
- **song-results**: The song ends on a results screen with a grade, the accuracy and the best combo, and one
  press plays it again. Why: the player sees how they did and goes straight back in. Break it when: songs are
  stages of a story and the next one follows at once.

## Feel

- **song-clock**: Start the song with `AudioSource.PlayScheduled` and move notes by `AudioSettings.dspTime`, never
  `Time.time` or the frame count. Judge each press at its Input System event time (`context.time`), not the frame
  it is read in; that clock is `Time.realtimeSinceStartup`, so map it to DSP time with an offset sampled each
  frame *(verify)*. Why: a note that looks on the beat is on the beat, all song long. Break it when: the beat
  only paces the world and no press is judged in time.
- **graded-hits**: Each press gets a grade by how close it was, perfect, good or miss, flashed at the hit line
  the instant you press. Why: the player sees how close they came. Break it when: a relaxed game for anyone,
  with wide windows and no grades.
- **music-swells**: A streak adds layers to the song, drums then bass then melody, and a miss drops one, each
  change on the bar line (layers are synced AudioSources scheduled on the same DSP time). Why: the soundtrack
  celebrates the player's run. Break it when: the song plays the same for everyone.

## Variants

- **strict**: Tight windows, dense charts, a miss costs the whole combo.
- **groove**: Wide windows, notes on the strong beats, a miss only dims the music.
- **beat-fight**: You move and strike on the beat, and enemies move to the music.

## Choices that shape the pitch

- **What you press:** notes down lanes on a few inputs (default) · circles to tap where they appear · moves
  on a grid on the beat, fighting monsters.
- **Failure:** a health bar that misses drain, ending the song early (default) · no failing, only a grade at
  the end · one miss ends it, a challenge mode.
- **The song:** one original song, no licensed music (default) · a few short songs of rising difficulty · a
  beat that speeds up until you miss, an endless mode.
- **View:** flat lanes, fixed camera (default) · a 3D note highway · a grid seen from above.
- **Feeling:** the player feels in the groove by hitting a run of notes without thinking, because each press is
  judged against the song they hear and the music swells with the streak.

## Platforms

- PC: lanes on D F J K or arrows; the mouse for circle tapping.
- Touch: each lane is a screen zone, judged on each finger's touch-down through `EnhancedTouch` (Pointer
  only sees the primary touch);
  portrait suits vertical lanes *(guess)*. Set Project Settings > Audio > DSP Buffer Size to Best latency,
  and always offer calibration on phones.
- Session: one song is 2-4 minutes on both.

## Later

- A song editor and charting tool
- The player's own music, with notes found from its beats
- Licensed songs and a song list
- Leaderboards per song (needs a server)
- Haptics on each hit (Nice Vibrations)
- Drums, guitars or motion controllers
- Modifiers: faster notes, hidden notes
- Two players on one keyboard, a versus song

## In a mashup

Rhythm leads judgement timing and the music clock. Action leads responsive input and what a hit does, and input
is never held back to land on a beat. A roguelike leads the run, a dungeon moved through on the beat. A story
half leads the scenes between songs. A platformer half leads movement, and the beat shapes only the hazards.
