### Utility
- Custom %help command
- Reminders (Like Kitchen Sink bot)
- YouTube search
- MAL search
- NUSMods check
  - check number of vacancies in a module (luna)
  - suggestion: %nusmods MA5202 list → list all AYs that it's offered (htns)
- Avy (retrieve pfp of a discord user)

### Games
- Tic Tac Toe
- Ultimate Tic Tac Toe
- Posoydos
- Bridge

### Misc
- Max0r quotes
- Fixing code style
- Reverse a string
- Zalgo-ify a text



### Tic Tac Toe Improvements/Thoughts (as of 2024-04-18)
- In the current planned implementation , %tictactoe does not take into 
  consideration the channels in which the messages are sent. This means 
  that it is possible to play with other people even if they share no 
  servers in common.
- This means that technically, the bot could be used to play tic tac toe with 
  complete strangers and function as some global server to run tictactoe games.
- This could either be encouraged by having a command to list existing 
  unfilled lobby ids while keeping the current method of generating lobby ids 
  (MEX) or discouraged by not adding such a function and using a randomly 
  generated integer instead for lobby ids.
- If it is encouraged, then private lobbies could also still be implemented by 
  possibly making a private lobby class that either requires a password to 
  join or randomly generate lobby ids big enough to not ever be reached by 
  MEX and not include them in the list when searching for all available 
  lobbies.
