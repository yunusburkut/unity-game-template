# Parking what Now already holds

Loaded from pipeline phase 1 when PLAN.md Now already holds another card, or a `prototype <Name>: <question>` line (a
`gamekit:prototype` spike waiting for its verdict), and the user asks for something new.

Ask whether to finish it (`devam`; a spike: play it, then PROCEED / PIVOT / KILL, `gamekit:prototype`) or park it, and
never write a card over it.

- **Parking a card** commits the card as it stands (ticks included), then puts Now back to its TODO line and adds one
  line to Next, `<goal> - parked, card at <short sha>` (that commit; asking for that goal later brings it back from
  `git show <sha>:PLAN.md`); commit, then write the new card.
- **Parking a prototype line** commits nothing new and keeps its folder: Now goes back to its TODO line and Next gets
  the line as it stands (its `, first scene was <path>` note included) plus ` - parked, folder kept`; `devam` on that
  Next line moves it back to Now. Then write the new card.
