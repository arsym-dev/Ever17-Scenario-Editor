## Game Flow and SCR File Structure
The game flow is controlled by something outside the scenario files. In regular gameplay, the game will display images, play music, and do transitions. Once it reaches a point where it must display text, it will call the SCR file and request a chunk.

These chunks contain all text that will be displayed between sprite changes/transitions, as well as how to format the text.

A chunk can be as short as one single line if the scene is dynamic with many sprite changes. 

## SCR Bytecode Specifications

| Opcode | Length | Plaintext output     | Description | 
| :--   | :--    | :--:            | :--         |
| 0x00    | 1      |               | End of chunk   |
| 0x01    | 1      | Single newline or {1} | Newline in text    |
| 0x02    | 1      |               | Wait for user acknowledgment |
| 0x03    | 1      |               | Clear textbox and save to history |
| 0x04    | 4 or 5    | ???            | Alternate user input |
| 0x05    | 4      | Double newline | Start of textbox entry |
| 0x0B    | 2 or 4    | {11:x}         | Choice |
| 0x0C    | 1      | {12}           | Continue immediately without waiting for user acknowledgment |
| 0x0D    | 2+string length  | {SE_NAME}      | Play voice clip |
| 0x0E    | 1      |                | Start of chunk |
| 0x10    | 2      | {16:x}         | Centering/NVL clear |
| 0x11    | 2      | {17:x}         | Font size change |
| 0x20+  | 1      | string         | Text. Ignored outside of textbox/NVL mode/choice. |

### Opcode 0x00 : End of chunk
Marks the end of the current chunk. Lines after this point will be read into the next chunk.

### Opcode 0x02 : Wait for user acknowledgment
This is found at the end of lines of dialogue. The game pauses and waits for the user to advance the text. For simplicity, the plaintext output will not display them, but they will be added automatically when the script is compiled **only if {12} doesn't already exist on this line**.

### Opcode 0x03 : Clear textbox and save to history
This is found at the end of lines of dialogue, after a 0x02 or 0x0C command. For simplicity, the plaintext output will not display them, but they will be added automatically when the script is compiled.

### Opcode 0x04 : Alternate user input

Seems to control auto mode and delays before the user regains control. These seem to be the only two valid commands:

```
04 80 00 00    =  Immediately play next transition, then wait for user input
04 A0 xx 00 00 = How long to pause before continuing in auto mode
                 (if xx=0xFF, it's roughly 4 sec. xx=A0 is near instant)
```

### Opcode 0x05 : Entry start

Always appears as a fixed sequence

```
05 80 00 00
```


### Opcode 0x0B : Choice

| Value       | Length | TXT output | Description |
| :--         | :--    | :--:       | :--         |
| 0B 00 xx yy | 4      | {11:0-xx}  | Start of choice menu. `xx yy` is choice id (little endian).<br>Since all choice ids are below 0xFF, `yy` is always zero.<br>Likely used to detemine how many choices the player has reached.|
| 0B 01       | 2      | {11:1}     | Standard choice (always visible) |
| 0B 02 xx yy | 4      | {11:2-}    | Conditional choice |

Choices are always terminated with `0x01`.

To my knowledge, the conditional choice only appears as `0C 02 28 0A A4 xx 14 00`, where `xx` is a value between 0xD0 and 0xD5.

### Opcode 0x0C : Continue immediately without waiting for user acknowledgment
Self-explanatory

### Opcode 0x0D : Play voice clip

The format is:

```
OD <name of voice clip> 00
```

### Opcode 0x0E : Start of chunk

Marks the start of the chunk. I've experimented with omitting it and it doesn't seem to affect anything negatively. In any case, the script will automatically add it when compiling the scenario.

### Opcode 0x10 : Formatting

This command has two main functions: mark text that should be centered, and clear the NVL screen.

It exists in these formats:
```
10 00 - Mark start of centered text (Does nothing)
10 01 - Mark end of centered text (Does nothing)
10 02 - Dark red text???
10 03 - 
10 04 - Clear text, save to history immediately. Good for clearing NVL mode.
```

Regarding `10 00` and `10 01`, they don't actually do anything. They denote centered text, but they don't actually perform any centering.
Instead, centering is done by a tool afterwards that adds in the correct number of space before this text 
to get it in the center of the text box (48 char width, monospaced)

### Opcode 0x11 : Font size change
These tags are used before the text is displayed. They seem to reset after the current entry is displayed.

```
11 03 - Huge font
```

### Opcode 0x20 and beyond: Text
Any opcode that begins with a value greater than or equal to 0x20 is interpreted as a string and will be printed to the screen. Anything that begins with 0x20 or higher is IGNORED if it is not located in a command that controls the textbox/NVL mode/choices.

Text is represented as ANSI. **It is IMPORTANT that you save all files as ANSI**. However, some special characters can be found in the game. Unfortunately I cannot give examples here as they break the default unicode formatting.