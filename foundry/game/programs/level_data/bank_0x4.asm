; Bank 4

; Level_8_W7
; Object Set 1
Level_8_W7_generators:
Level_8_W7_header:
	.byte $50; Next Level
	.byte LEVEL1_SIZE_13 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_13; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	.byte $00 | $1A, $00, $C0, $27; Flat Ground
	.byte $00 | $12, $03, $E3; Background Clouds
	.byte $00 | $13, $08, $E2; Background Clouds
	.byte $00 | $19, $00, $92; Background Bushes
	.byte $00 | $12, $0A, $02; Background Hills C
	.byte $00 | $16, $06, $00; Background Hills A
	.byte $00 | $17, $03, $01; Background Hills B
	.byte $00 | $17, $0D, $01; Background Hills B
	.byte $00 | $13, $11, $E2; Background Clouds
	.byte $00 | $11, $1A, $E2; Background Clouds
	.byte $00 | $19, $17, $96; Background Bushes
	.byte $00 | $17, $13, $01; Background Hills B
	.byte $00 | $16, $18, $00; Background Hills A
	.byte $20 | $16, $15, $23; '?' Blocks with single coins
	.byte $20 | $18, $11, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $14, $15, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $14, $17, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $15, $1E, $A4; Downward Pipe (CAN'T go down)
	.byte $00 | $12, $20, $02; Background Hills C
	.byte $00 | $11, $25, $E2; Background Clouds
	.byte $00 | $15, $28, $E2; Background Clouds
	.byte $20 | $08, $29, $27; '?' Blocks with single coins
	.byte $20 | $0B, $28, $43; Wooden Blocks
	.byte $20 | $0B, $2E, $43; Wooden Blocks
	.byte $20 | $0C, $29, $D5; Upward Pipe (CAN'T go up)
	.byte $20 | $0C, $2F, $D5; Upward Pipe (CAN'T go up)
	.byte $20 | $17, $26, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $2C, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $1A, $32, $C0, $5A; Flat Ground
	.byte $00 | $15, $30, $E2; Background Clouds
	.byte $00 | $14, $36, $92; Background Bushes
	.byte $00 | $19, $3E, $92; Background Bushes
	.byte $20 | $12, $33, $11; Bricks
	.byte $20 | $14, $3E, $10; Bricks
	.byte $20 | $17, $3F, $12; Bricks
	.byte $20 | $12, $37, $21; '?' Blocks with single coins
	.byte $20 | $17, $32, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $13, $3C, $A6; Downward Pipe (CAN'T go down)
	.byte $20 | $12, $36, $02; '?' with Star
	.byte $20 | $17, $3E, $07; Brick with Leaf
	.byte $00 | $15, $35, $44; Blue Block Platform (Extends to ground)
	.byte $00 | $17, $38, $22; Orange Block Platform (Extends to ground)
	.byte $00 | $13, $41, $E3; Background Clouds
	.byte $00 | $11, $4B, $E2; Background Clouds
	.byte $00 | $19, $42, $92; Background Bushes
	.byte $00 | $16, $4E, $00; Background Hills A
	.byte $00 | $17, $4B, $01; Background Hills B
	.byte $20 | $15, $4B, $16; Bricks
	.byte $20 | $18, $45, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $47, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $14, $49, $A5; Downward Pipe (CAN'T go down)
	.byte $20 | $15, $4E, $0B; Brick with 1-up
	.byte $00 | $11, $5A, $E3; Background Clouds
	.byte $00 | $13, $51, $E2; Background Clouds
	.byte $00 | $17, $55, $92; Background Bushes
	.byte $00 | $17, $5A, $90; Background Bushes
	.byte $00 | $19, $5F, $98; Background Bushes
	.byte $00 | $18, $54, $17; White Block Platform (Extends to ground)
	.byte $20 | $08, $59, $0A; Multi-Coin Brick
	.byte $20 | $0B, $58, $41; Wooden Blocks
	.byte $20 | $0C, $58, $D9; Upward Pipe (CAN'T go up)
	.byte $20 | $16, $5D, $A3; Downward Pipe (CAN'T go down)
	.byte $00 | $03, $5D, $E2; Background Clouds
	.byte $40 | $13, $5A, $07; Red Invisible Note Block
	.byte $00 | $05, $64, $E2; Background Clouds
	.byte $00 | $09, $60, $E2; Background Clouds
	.byte $20 | $00, $62, $D1; Upward Pipe (CAN'T go up)
	.byte $00 | $12, $60, $02; Background Hills C
	.byte $00 | $11, $6A, $E2; Background Clouds
	.byte $00 | $13, $66, $E2; Background Clouds
	.byte $00 | $19, $6E, $91; Background Bushes
	.byte $20 | $18, $68, $B1; Downward Pipe (CAN go down, ignores pointers)
	.byte $20 | $18, $6A, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $17, $6C, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $17, $66, $10; Bricks
	.byte $20 | $17, $67, $0A; Multi-Coin Brick
	.byte $00 | $12, $71, $02; Background Hills C
	.byte $00 | $16, $70, $00; Background Hills A
	.byte $00 | $17, $74, $01; Background Hills B
	.byte $00 | $11, $7D, $E2; Background Clouds
	.byte $20 | $0B, $78, $41; Wooden Blocks
	.byte $40 | $16, $7A, $43; Bridge
	.byte $40 | $16, $7F, $40; Bridge
	.byte $20 | $19, $7A, $05; Muncher
	.byte $20 | $19, $7B, $05; Muncher
	.byte $20 | $19, $7C, $05; Muncher
	.byte $20 | $19, $7D, $05; Muncher
	.byte $20 | $19, $7E, $05; Muncher
	.byte $20 | $19, $7F, $05; Muncher
	.byte $20 | $0C, $78, $D5; Upward Pipe (CAN'T go up)
	.byte $20 | $15, $78, $A4; Downward Pipe (CAN'T go down)
	.byte $00 | $12, $82, $E3; Background Clouds
	.byte $00 | $14, $87, $E2; Background Clouds
	.byte $40 | $16, $81, $40; Bridge
	.byte $40 | $16, $83, $40; Bridge
	.byte $40 | $16, $85, $40; Bridge
	.byte $20 | $19, $81, $05; Muncher
	.byte $20 | $19, $83, $05; Muncher
	.byte $20 | $19, $84, $05; Muncher
	.byte $20 | $19, $85, $05; Muncher
	.byte $20 | $19, $86, $05; Muncher
	.byte $20 | $19, $87, $05; Muncher
	.byte $20 | $19, $89, $05; Muncher
	.byte $20 | $19, $8A, $05; Muncher
	.byte $20 | $16, $8B, $A3; Downward Pipe (CAN'T go down)
	.byte $00 | $1A, $92, $C0, $3D; Flat Ground
	.byte $00 | $11, $9A, $E2; Background Clouds
	.byte $00 | $12, $90, $E3; Background Clouds
	.byte $00 | $14, $94, $E2; Background Clouds
	.byte $00 | $18, $9A, $37; Green Block Platform (Extends to ground)
	.byte $00 | $17, $9B, $92; Background Bushes
	.byte $00 | $17, $9F, $91; Background Bushes
	.byte $00 | $17, $94, $01; Background Hills B
	.byte $20 | $17, $92, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $98, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $13, $A5, $E2; Background Clouds
	.byte $00 | $19, $AA, $97; Background Bushes
	.byte $00 | $16, $A5, $00; Background Hills A
	.byte $20 | $15, $A3, $A4; Downward Pipe (CAN'T go down)
	.byte $20 | $13, $AC, $16; Bricks
	.byte $20 | $17, $AE, $12; Bricks
	.byte $20 | $13, $AE, $22; '?' Blocks with single coins
	.byte $20 | $13, $AF, $0B; Brick with 1-up
	.byte $20 | $17, $AC, $21; '?' Blocks with single coins
	.byte $00 | $12, $B4, $02; Background Hills C
	.byte $00 | $17, $B2, $01; Background Hills B
	.byte $00 | $19, $BA, $91; Background Bushes
	.byte $20 | $17, $B1, $21; '?' Blocks with single coins
	.byte $40 | $00, $BC, $09; Level Ending
	; Pointer on screen $05
	.byte $E0 | $05, $70 | $07, 80; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $06
	.byte $E0 | $06, $50 | $02, 20; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_8_W7_objects:
	.byte $A0, $11, $18; Green Piranha Plant (upward)
	.byte $A4, $15, $14; Green Venus Fire Trap (upward)
	.byte $A6, $17, $14; Red Venus Fire Trap (upward)
	.byte $A0, $1E, $15; Green Piranha Plant (upward)
	.byte $A0, $26, $17; Green Piranha Plant (upward)
	.byte $A3, $29, $11; Red Piranha Plant (downward)
	.byte $A0, $2C, $18; Green Piranha Plant (upward)
	.byte $A3, $2F, $11; Red Piranha Plant (downward)
	.byte $A0, $32, $17; Green Piranha Plant (upward)
	.byte $A6, $3C, $13; Red Venus Fire Trap (upward)
	.byte $A0, $45, $18; Green Piranha Plant (upward)
	.byte $A2, $47, $16; Red Piranha Plant (upward)
	.byte $A4, $49, $14; Green Venus Fire Trap (upward)
	.byte $39, $4C, $14; Walking Nipper Plant
	.byte $A3, $58, $15; Red Piranha Plant (downward)
	.byte $2A, $5C, $18; Ptooie
	.byte $A2, $5D, $16; Red Piranha Plant (upward)
	.byte $2A, $6A, $16; Ptooie
	.byte $A6, $6C, $17; Red Venus Fire Trap (upward)
	.byte $39, $6F, $19; Walking Nipper Plant
	.byte $A7, $78, $11; Red Venus Fire Trap (downward)
	.byte $A0, $78, $15; Green Piranha Plant (upward)
	.byte $33, $80, $19; Nipper Plant
	.byte $33, $82, $19; Nipper Plant
	.byte $33, $88, $19; Nipper Plant
	.byte $A2, $8B, $16; Red Piranha Plant (upward)
	.byte $46, $98, $16; Pipe Ptooie
	.byte $2A, $A0, $18; Ptooie
	.byte $A6, $A3, $15; Red Venus Fire Trap (upward)
	.byte $33, $AD, $19; Nipper Plant
	.byte $3D, $AF, $16; Walking Ptooie (spits fireballs)
	.byte $41, $C8, $15; Goal Card
	.byte $FF
; Default_Level_264
; Object Set 14
Default_Level_264_generators:
Default_Level_264_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_0F0; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $60 | $0F, $00, $E4; Hilly Wall - Right Side
	.byte $80 | $14, $00, $56, $00; Hilly Fill
	.byte $80 | $14, $01, $86, $01; Flat Land - Hilly
	.byte $00 | $14, $02, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $15, $02, $E0; Hilly Wall - Right Side
	.byte $80 | $16, $03, $84, $01; Flat Land - Hilly
	.byte $00 | $16, $04, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $17, $04, $E0; Hilly Wall - Right Side
	.byte $80 | $18, $05, $82, $05; Flat Land - Hilly
	.byte $80 | $16, $0B, $84, $01; Flat Land - Hilly
	.byte $00 | $16, $0B, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $17, $0B, $E0; Hilly Wall - Left Side
	.byte $80 | $14, $0D, $86, $01; Flat Land - Hilly
	.byte $00 | $14, $0D, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $15, $0D, $E0; Hilly Wall - Left Side
	.byte $80 | $14, $0F, $56, $00; Hilly Fill
	.byte $00 | $0F, $0F, $E4; Hilly Wall - Left Side
	.byte $80 | $0F, $03, $B1, $09; Ceiling - Hilly
	.byte $00 | $0F, $03, $E0; Hilly Wall - Left Side
	.byte $00 | $10, $03, $07; Lower Left Corner - Hilly
	.byte $60 | $0F, $0C, $E0; Hilly Wall - Right Side
	.byte $00 | $10, $0C, $0A; Lower Right Hill Corner
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $0F, $0D, $C1; Upward Pipe (CAN go up)
	.byte $FF
Default_Level_264_objects:
	.byte $25, $02, $0A; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_9_W7
; Object Set 9
Level_9_W7_generators:
Level_9_W7_header:
	.byte $52; Next Level
	.byte LEVEL1_SIZE_10 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_09; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $09; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $60 | $06, $00, $A9; Pipe Boxes A
	.byte $60 | $06, $00, $BF; 1 Plain Background (used to block out stuff)
	.byte $60 | $06, $00, $C7; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0A, $00, $C7; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0E, $00, $C7; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $12, $00, $C7; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $12, $09, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $16, $00, $C7; Horizontal Plain Background B (used to block out stuff)
	.byte $00 | $06, $0C, $08; Cracked Pipe
	.byte $00 | $0E, $0C, $08; Cracked Pipe
	.byte $40 | $0B, $08, $E0; White Turtle Bricks
	.byte $40 | $0C, $08, $E0; White Turtle Bricks
	.byte $40 | $0D, $08, $E0; White Turtle Bricks
	.byte $20 | $12, $0B, $22; '?' blocks with single coins
	.byte $20 | $12, $0C, $00; '?' with flower
	.byte $20 | $19, $00, $15; Bricks
	.byte $00 | $05, $02, $0A; Oval Background Cloud
	.byte $00 | $13, $05, $0A; Oval Background Cloud
	.byte $00 | $03, $0C, $0A; Oval Background Cloud
	.byte $00 | $0A, $1D, $08; Cracked Pipe
	.byte $00 | $0E, $1A, $08; Cracked Pipe
	.byte $60 | $16, $19, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $40 | $07, $10, $E0; White Turtle Bricks
	.byte $40 | $08, $10, $E0; White Turtle Bricks
	.byte $40 | $09, $10, $E0; White Turtle Bricks
	.byte $40 | $07, $18, $E0; White Turtle Bricks
	.byte $40 | $08, $18, $E0; White Turtle Bricks
	.byte $40 | $09, $18, $E0; White Turtle Bricks
	.byte $20 | $0E, $14, $10; Bricks
	.byte $20 | $12, $14, $10; Bricks
	.byte $00 | $12, $1C, $08; Cracked Pipe
	.byte $40 | $13, $10, $E0; White Turtle Bricks
	.byte $40 | $14, $10, $E0; White Turtle Bricks
	.byte $40 | $15, $10, $E0; White Turtle Bricks
	.byte $20 | $0B, $11, $86; Coins
	.byte $20 | $0C, $11, $86; Coins
	.byte $20 | $0D, $11, $86; Coins
	.byte $20 | $16, $1B, $62; Note Blocks - movable two directions
	.byte $40 | $16, $1C, $01; Note Block with Flower
	.byte $20 | $19, $19, $40; Wooden blocks
	.byte $20 | $19, $1F, $40; Wooden blocks
	.byte $60 | $07, $20, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $0B, $28, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $0F, $28, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $13, $28, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $06, $29, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0A, $29, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $40 | $0F, $20, $E0; White Turtle Bricks
	.byte $40 | $10, $20, $E0; White Turtle Bricks
	.byte $40 | $11, $20, $E0; White Turtle Bricks
	.byte $20 | $09, $2B, $42; Wooden blocks
	.byte $20 | $14, $21, $8E; Coins
	.byte $20 | $14, $2C, $0F; Invisible 1-up
	.byte $00 | $04, $2C, $0A; Oval Background Cloud
	.byte $60 | $06, $30, $B7; 1 Plain Background (used to block out stuff)
	.byte $60 | $0F, $30, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $13, $30, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $0B, $38, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $07, $40, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $06, $30, $C7; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0A, $30, $C7; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $12, $39, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $16, $39, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $20 | $16, $34, $10; Bricks
	.byte $00 | $17, $30, $09; Bottom post of pipe structure
	.byte $20 | $07, $39, $87; Coins
	.byte $20 | $09, $33, $42; Wooden blocks
	.byte $20 | $0B, $30, $40; Wooden blocks
	.byte $20 | $14, $30, $87; Coins
	.byte $60 | $0F, $48, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $0A, $41, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $00 | $0A, $4C, $08; Cracked Pipe
	.byte $60 | $0E, $41, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $00 | $16, $4C, $08; Cracked Pipe
	.byte $40 | $07, $48, $E0; White Turtle Bricks
	.byte $40 | $08, $48, $E0; White Turtle Bricks
	.byte $40 | $09, $48, $E0; White Turtle Bricks
	.byte $20 | $16, $44, $10; Bricks
	.byte $20 | $0B, $42, $40; Wooden blocks
	.byte $20 | $0B, $46, $40; Wooden blocks
	.byte $20 | $0E, $44, $40; Wooden blocks
	.byte $20 | $13, $43, $82; Coins
	.byte $00 | $03, $46, $0A; Oval Background Cloud
	.byte $60 | $0F, $50, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $0F, $58, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $06, $51, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0A, $51, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $12, $59, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $40 | $0B, $50, $E0; White Turtle Bricks
	.byte $40 | $0C, $50, $E0; White Turtle Bricks
	.byte $40 | $0D, $50, $E0; White Turtle Bricks
	.byte $40 | $0B, $58, $E0; White Turtle Bricks
	.byte $40 | $0C, $58, $E0; White Turtle Bricks
	.byte $40 | $0D, $58, $E0; White Turtle Bricks
	.byte $40 | $13, $50, $E0; White Turtle Bricks
	.byte $40 | $14, $50, $E0; White Turtle Bricks
	.byte $40 | $15, $50, $E0; White Turtle Bricks
	.byte $20 | $16, $54, $10; Bricks
	.byte $00 | $17, $50, $09; Bottom post of pipe structure
	.byte $20 | $08, $52, $60; Note Blocks - movable two directions
	.byte $20 | $08, $56, $60; Note Blocks - movable two directions
	.byte $20 | $0B, $53, $62; Note Blocks - movable two directions
	.byte $20 | $07, $5B, $82; Coins
	.byte $20 | $0B, $5B, $82; Coins
	.byte $20 | $10, $5B, $22; '?' blocks with single coins
	.byte $20 | $10, $5C, $00; '?' with flower
	.byte $60 | $07, $68, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $0B, $68, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $13, $60, $B2; 1 Plain Background (used to block out stuff)
	.byte $00 | $12, $64, $08; Cracked Pipe
	.byte $00 | $16, $64, $08; Cracked Pipe
	.byte $40 | $07, $60, $E0; White Turtle Bricks
	.byte $40 | $08, $60, $E0; White Turtle Bricks
	.byte $40 | $09, $60, $E0; White Turtle Bricks
	.byte $20 | $0A, $64, $10; Bricks
	.byte $20 | $0E, $6C, $10; Bricks
	.byte $40 | $0F, $68, $E0; White Turtle Bricks
	.byte $40 | $10, $68, $E0; White Turtle Bricks
	.byte $40 | $11, $68, $E0; White Turtle Bricks
	.byte $20 | $0C, $62, $85; Coins
	.byte $20 | $0C, $69, $85; Coins
	.byte $20 | $14, $6A, $85; Coins
	.byte $00 | $02, $66, $0A; Oval Background Cloud
	.byte $60 | $07, $70, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $07, $78, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $13, $70, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $13, $78, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $0A, $71, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0E, $71, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0E, $79, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $00 | $12, $7C, $08; Cracked Pipe
	.byte $00 | $17, $70, $09; Bottom post of pipe structure
	.byte $40 | $0F, $70, $E0; White Turtle Bricks
	.byte $40 | $10, $70, $E0; White Turtle Bricks
	.byte $40 | $11, $70, $E0; White Turtle Bricks
	.byte $20 | $0A, $72, $41; Wooden blocks
	.byte $20 | $0A, $75, $41; Wooden blocks
	.byte $20 | $0E, $73, $42; Wooden blocks
	.byte $20 | $0E, $7A, $00; '?' with flower
	.byte $20 | $14, $70, $8B; Coins
	.byte $00 | $01, $7A, $0A; Oval Background Cloud
	.byte $60 | $0F, $88, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $06, $89, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0A, $81, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $00 | $12, $84, $08; Cracked Pipe
	.byte $40 | $07, $80, $E0; White Turtle Bricks
	.byte $40 | $08, $80, $E0; White Turtle Bricks
	.byte $40 | $09, $80, $E0; White Turtle Bricks
	.byte $40 | $0B, $80, $E0; White Turtle Bricks
	.byte $40 | $0C, $80, $E0; White Turtle Bricks
	.byte $40 | $0D, $80, $E0; White Turtle Bricks
	.byte $40 | $13, $80, $E0; White Turtle Bricks
	.byte $40 | $14, $80, $E0; White Turtle Bricks
	.byte $40 | $15, $80, $E0; White Turtle Bricks
	.byte $00 | $17, $80, $09; Bottom post of pipe structure
	.byte $20 | $0A, $83, $82; Coins
	.byte $60 | $12, $89, $C7; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $16, $89, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $20 | $18, $8C, $91; Downward Pipe (CAN go down)
	.byte $60 | $06, $90, $B3; 1 Plain Background (used to block out stuff)
	.byte $60 | $0F, $90, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $13, $90, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $06, $98, $B7; 1 Plain Background (used to block out stuff)
	.byte $60 | $06, $90, $CF; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0A, $91, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $12, $91, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0A, $99, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0E, $99, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $12, $99, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $16, $99, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $20 | $12, $91, $85; Coins
	.byte $00 | $17, $90, $09; Bottom post of pipe structure
	.byte $20 | $12, $99, $40; Wooden blocks
	.byte $20 | $16, $99, $41; Wooden blocks
	.byte $00 | $06, $90, $0A; Oval Background Cloud
	.byte $60 | $06, $A0, $BF; 1 Plain Background (used to block out stuff)
	.byte $60 | $16, $A0, $B0; 1 Plain Background (used to block out stuff)
	; Pointer on screen $08
	.byte $E0 | $08, $70 | $01, 96; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_9_W7_objects:
	.byte $6E, $0A, $14; Green Koopa Paratroopa (bounces)
	.byte $72, $11, $05; Goomba
	.byte $72, $1B, $05; Goomba
	.byte $73, $1F, $09; Para-Goomba
	.byte $72, $25, $05; Goomba
	.byte $72, $29, $11; Goomba
	.byte $72, $2D, $11; Goomba
	.byte $73, $3A, $16; Para-Goomba
	.byte $73, $3D, $16; Para-Goomba
	.byte $6E, $55, $11; Green Koopa Paratroopa (bounces)
	.byte $72, $61, $05; Goomba
	.byte $72, $6B, $05; Goomba
	.byte $72, $75, $05; Goomba
	.byte $72, $7F, $05; Goomba
	.byte $41, $B8, $15; Goal Card
	.byte $FF
; Dungeon__2_W7
; Object Set 2
Dungeon__2_W7_generators:
Dungeon__2_W7_header:
	.byte $53; Next Level
	.byte LEVEL1_SIZE_09 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $07, $00, $3F, $8F; Blank Background (used to block out stuff)
	.byte $60 | $17, $00, $33, $8F; Blank Background (used to block out stuff)
	.byte $00 | $00, $00, $E6, $8F; Horizontally oriented X-blocks
	.byte $60 | $1A, $08, $40, $84; Lava
	.byte $00 | $16, $00, $E4, $04; Horizontally oriented X-blocks
	.byte $00 | $17, $05, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $06, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $19, $07, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $19, $0C, $E1, $01; Horizontally oriented X-blocks
	.byte $20 | $14, $0C, $A4; Downward Pipe (CAN'T go down)
	.byte $00 | $19, $13, $E1, $01; Horizontally oriented X-blocks
	.byte $00 | $16, $18, $E4, $00; Horizontally oriented X-blocks
	.byte $00 | $19, $1D, $E1, $02; Horizontally oriented X-blocks
	.byte $00 | $15, $18, $02; Rotodisc block
	.byte $20 | $17, $13, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $15, $1D, $A3; Downward Pipe (CAN'T go down)
	.byte $00 | $19, $25, $E1, $01; Horizontally oriented X-blocks
	.byte $00 | $19, $28, $E1, $03; Horizontally oriented X-blocks
	.byte $20 | $16, $25, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $13, $2A, $A5; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $20, $08; Brick with Star
	.byte $20 | $16, $22, $10; Bricks
	.byte $00 | $07, $34, $E7, $02; Horizontally oriented X-blocks
	.byte $00 | $0F, $34, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $1A, $31, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $19, $35, $E1, $01; Horizontally oriented X-blocks
	.byte $00 | $19, $39, $E1, $08; Horizontally oriented X-blocks
	.byte $20 | $18, $31, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $17, $35, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $14, $39, $A4; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $40, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $48, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $4A, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $4C, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $4E, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $19, $58, $E1, $01; Horizontally oriented X-blocks
	.byte $20 | $18, $50, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $15, $58, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $17, $55, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $5B, $A4; Downward Pipe (CAN'T go down)
	.byte $20 | $07, $58, $DA; Upward Pipe (CAN'T go up)
	.byte $20 | $14, $60, $A6; Downward Pipe (CAN'T go down)
	.byte $00 | $19, $66, $E1, $01; Horizontally oriented X-blocks
	.byte $00 | $1A, $6E, $E0, $01; Horizontally oriented X-blocks
	.byte $20 | $16, $66, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $6E, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $12, $67, $01; '?' with leaf
	.byte $00 | $07, $71, $E7, $02; Horizontally oriented X-blocks
	.byte $00 | $0F, $71, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $19, $72, $E1, $06; Horizontally oriented X-blocks
	.byte $00 | $19, $7E, $E1, $01; Horizontally oriented X-blocks
	.byte $20 | $17, $72, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $13, $77, $A5; Downward Pipe (CAN'T go down)
	.byte $20 | $15, $7E, $A3; Downward Pipe (CAN'T go down)
	.byte $00 | $07, $8D, $F2, $13; Vertically oriented X-blocks
	.byte $00 | $14, $85, $E6, $01; Horizontally oriented X-blocks
	.byte $00 | $14, $87, $E0, $01; Horizontally oriented X-blocks
	.byte $20 | $19, $87, $91; Downward Pipe (CAN go down)
	; Pointer on screen $08
	.byte $E0 | $08, $50 | $02, 16; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__2_W7_objects:
	.byte $A2, $0C, $14; Red Piranha Plant (upward)
	.byte $A2, $13, $17; Red Piranha Plant (upward)
	.byte $2F, $14, $10; Boo Buddy
	.byte $5B, $18, $15; Single Rotodisc (rotates counterclockwise)
	.byte $A2, $1D, $15; Red Piranha Plant (upward)
	.byte $A6, $25, $16; Red Venus Fire Trap (upward)
	.byte $A2, $2A, $13; Red Piranha Plant (upward)
	.byte $A2, $31, $18; Red Piranha Plant (upward)
	.byte $8A, $35, $0F; Thwomp (normal)
	.byte $A2, $39, $14; Red Piranha Plant (upward)
	.byte $2F, $46, $16; Boo Buddy
	.byte $A2, $48, $18; Red Piranha Plant (upward)
	.byte $A2, $4C, $18; Red Piranha Plant (upward)
	.byte $A0, $58, $15; Green Piranha Plant (upward)
	.byte $A3, $58, $11; Red Piranha Plant (downward)
	.byte $A6, $60, $14; Red Venus Fire Trap (upward)
	.byte $A2, $66, $16; Red Piranha Plant (upward)
	.byte $8A, $72, $0F; Thwomp (normal)
	.byte $2F, $7F, $10; Boo Buddy
	.byte $2F, $83, $14; Boo Buddy
	.byte $A2, $87, $19; Red Piranha Plant (upward)
	.byte $FF
; Pipe_3_End_2_W7
; Object Set 14
Pipe_3_End_2_W7_generators:
Pipe_3_End_2_W7_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_D8 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $19, $00, $51, $0F; Hilly Fill
	.byte $60 | $0F, $00, $E9; Hilly Wall - Right Side
	.byte $80 | $19, $01, $81, $0D; Flat Land - Hilly
	.byte $00 | $0F, $0F, $E9; Hilly Wall - Left Side
	.byte $80 | $0F, $03, $B4, $09; Ceiling - Hilly
	.byte $80 | $0F, $06, $54, $04; Hilly Fill
	.byte $00 | $0F, $03, $E3; Hilly Wall - Left Side
	.byte $00 | $13, $03, $07; Lower Left Corner - Hilly
	.byte $60 | $0F, $0C, $E3; Hilly Wall - Right Side
	.byte $00 | $13, $0C, $0A; Lower Right Hill Corner
	.byte $00 | $14, $06, $71; 45 Degree Hill - Up/Left
	.byte $00 | $14, $0A, $80; 45 Degree Hill - Up/Right
	.byte $80 | $14, $08, $B2, $01; Ceiling - Hilly
	.byte $00 | $16, $08, $07; Lower Left Corner - Hilly
	.byte $60 | $15, $09, $E0; Hilly Wall - Right Side
	.byte $00 | $16, $09, $0A; Lower Right Hill Corner
	.byte $20 | $0F, $01, $C6; Upward Pipe (CAN go up)
	.byte $20 | $0F, $0D, $C6; Upward Pipe (CAN go up)
	.byte $FF
Pipe_3_End_2_W7_objects:
	.byte $25, $02, $07; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Piranha_Plant__2_W7
; Object Set 5
Piranha_Plant__2_W7_generators:
Piranha_Plant__2_W7_header:
	.byte $54; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_05; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $05; Start action | Graphic set
	.byte $80 | $00; Time | Music
	.byte $20 | $16, $02, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $17, $02, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $19, $00, $F4; Rightward Pipe (CAN'T go in)
	.byte $40 | $19, $05, $25; Leftward Pipe (CAN'T go in)
	.byte $40 | $19, $0B, $2D; Leftward Pipe (CAN'T go in)
	.byte $00 | $15, $0E, $A3; Piranha Plant Small Downward Pipe A
	.byte $00 | $13, $0F, $B5; Piranha Plant Small Downward Pipe B
	.byte $20 | $17, $05, $F1; Rightward Pipe (CAN'T go in)
	.byte $40 | $17, $07, $21; Leftward Pipe (CAN'T go in)
	.byte $20 | $13, $0C, $A4; Downward Pipe (CAN'T go down)
	.byte $00 | $14, $0E, $00; Piranha Plant Muncher A
	.byte $00 | $12, $0F, $01; Piranha Plant Muncher B
	.byte $20 | $17, $0C, $D1; Upward Pipe (CAN'T go up)
	.byte $00 | $14, $10, $A4; Piranha Plant Small Downward Pipe A
	.byte $00 | $16, $11, $B2; Piranha Plant Small Downward Pipe B
	.byte $00 | $16, $12, $A2; Piranha Plant Small Downward Pipe A
	.byte $00 | $16, $13, $B2; Piranha Plant Small Downward Pipe B
	.byte $00 | $16, $14, $A2; Piranha Plant Small Downward Pipe A
	.byte $20 | $14, $15, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $0B, $1A, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $0B, $1C, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $0B, $1E, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $0F, $1A, $D4; Upward Pipe (CAN'T go up)
	.byte $20 | $0F, $1C, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $0F, $1E, $D4; Upward Pipe (CAN'T go up)
	.byte $40 | $19, $19, $2D; Leftward Pipe (CAN'T go in)
	.byte $00 | $13, $10, $00; Piranha Plant Muncher A
	.byte $00 | $15, $11, $01; Piranha Plant Muncher B
	.byte $00 | $15, $12, $00; Piranha Plant Muncher A
	.byte $00 | $15, $13, $01; Piranha Plant Muncher B
	.byte $00 | $15, $14, $00; Piranha Plant Muncher A
	.byte $20 | $17, $15, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $0B, $20, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $0F, $20, $D6; Upward Pipe (CAN'T go up)
	.byte $20 | $15, $25, $A2; Downward Pipe (CAN'T go down)
	.byte $40 | $19, $20, $26; Leftward Pipe (CAN'T go in)
	.byte $00 | $19, $27, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $28, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $29, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $2A, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $2B, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $2C, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $2D, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $2E, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $2F, $A1; Piranha Plant Small Downward Pipe A
	.byte $20 | $14, $29, $60; Note Blocks - movable two directions
	.byte $20 | $15, $2D, $60; Note Blocks - movable two directions
	.byte $00 | $18, $27, $00; Piranha Plant Muncher A
	.byte $00 | $18, $28, $01; Piranha Plant Muncher B
	.byte $00 | $18, $29, $00; Piranha Plant Muncher A
	.byte $00 | $18, $2A, $01; Piranha Plant Muncher B
	.byte $00 | $18, $2B, $00; Piranha Plant Muncher A
	.byte $00 | $18, $2C, $01; Piranha Plant Muncher B
	.byte $00 | $18, $2D, $00; Piranha Plant Muncher A
	.byte $00 | $18, $2E, $01; Piranha Plant Muncher B
	.byte $00 | $18, $2F, $00; Piranha Plant Muncher A
	.byte $20 | $17, $25, $D1; Upward Pipe (CAN'T go up)
	.byte $00 | $19, $30, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $31, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $32, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $33, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $34, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $35, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $36, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $37, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $38, $B1; Piranha Plant Small Downward Pipe B
	.byte $20 | $15, $39, $A5; Downward Pipe (CAN'T go down)
	.byte $20 | $13, $3B, $97; Downward Pipe (CAN go down)
	.byte $20 | $15, $3D, $A5; Downward Pipe (CAN'T go down)
	.byte $00 | $09, $3F, $A8; Piranha Plant Small Downward Pipe A
	.byte $00 | $12, $3F, $A8; Piranha Plant Small Downward Pipe A
	.byte $20 | $13, $30, $60; Note Blocks - movable two directions
	.byte $20 | $14, $36, $60; Note Blocks - movable two directions
	.byte $00 | $18, $30, $01; Piranha Plant Muncher B
	.byte $00 | $18, $31, $00; Piranha Plant Muncher A
	.byte $00 | $18, $32, $01; Piranha Plant Muncher B
	.byte $00 | $18, $33, $00; Piranha Plant Muncher A
	.byte $00 | $18, $34, $01; Piranha Plant Muncher B
	.byte $00 | $18, $35, $00; Piranha Plant Muncher A
	.byte $00 | $18, $36, $01; Piranha Plant Muncher B
	.byte $00 | $18, $37, $00; Piranha Plant Muncher A
	.byte $00 | $18, $38, $01; Piranha Plant Muncher B
	; Pointer on screen $03
	.byte $E0 | $03, $00 | $02, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Piranha_Plant__2_W7_objects:
	.byte $A2, $0C, $13; Red Piranha Plant (upward)
	.byte $A6, $15, $14; Red Venus Fire Trap (upward)
	.byte $A5, $1C, $10; Green Venus Fire Trap (downward)
	.byte $A1, $20, $15; Green Piranha Plant (downward)
	.byte $A6, $25, $15; Red Venus Fire Trap (upward)
	.byte $6F, $34, $11; Red Koopa Paratroopa
	.byte $FF
; Pipe_1_End_1_W8
; Object Set 14
Pipe_1_End_1_W8_generators:
Pipe_1_End_1_W8_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_0F0; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $1A, $00, $50, $0F; Hilly Fill
	.byte $80 | $15, $00, $54, $00; Hilly Fill
	.byte $60 | $0F, $00, $E5; Hilly Wall - Right Side
	.byte $80 | $15, $01, $84, $04; Flat Land - Hilly
	.byte $00 | $15, $06, $54; 45 Degree Hill - Down/Right
	.byte $80 | $1A, $0B, $80, $03; Flat Land - Hilly
	.byte $80 | $0F, $0F, $5B, $00; Hilly Fill
	.byte $00 | $14, $0F, $E5; Hilly Wall - Left Side
	.byte $80 | $0F, $0B, $B4, $03; Ceiling - Hilly
	.byte $00 | $0F, $06, $74; 45 Degree Hill - Up/Left
	.byte $80 | $0F, $03, $B0, $03; Ceiling - Hilly
	.byte $00 | $0F, $03, $07; Lower Left Corner - Hilly
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $18, $0D, $91; Downward Pipe (CAN go down)
	.byte $80 | $1A, $0D, $50, $01; Hilly Fill
	.byte $FF
Pipe_1_End_1_W8_objects:
	.byte $25, $02, $0C; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Hidden_Level_W8
; Object Set 1
Hidden_Level_W8_generators:
Hidden_Level_W8_header:
	.byte $4F; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_04; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $80 | $08; Time | Music
	.byte $40 | $00, $00, $B0, $15; Blue X-Blocks
	.byte $40 | $01, $00, $BF, $00; Blue X-Blocks
	.byte $40 | $11, $00, $B8, $00; Blue X-Blocks
	.byte $40 | $01, $0F, $BF, $06; Blue X-Blocks
	.byte $40 | $11, $0F, $B8, $06; Blue X-Blocks
	.byte $00 | $1A, $00, $C0, $3F; Flat Ground
	.byte $00 | $0E, $08, $E2; Background Clouds
	.byte $00 | $0F, $03, $E2; Background Clouds
	.byte $00 | $19, $06, $92; Background Bushes
	.byte $20 | $18, $0C, $E2; Rightward Pipe (CAN go in)
	.byte $40 | $18, $16, $22; Leftward Pipe (CAN'T go in)
	.byte $40 | $00, $28, $09; Level Ending
	; Pointer on screen $00
	.byte $E0 | $00, $70 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Hidden_Level_W8_objects:
	.byte $70, $0A, $17; Buzzy Beetle
	.byte $2A, $10, $16; Ptooie
	.byte $A0, $2C, $12; Green Piranha Plant (upward)
	.byte $73, $3E, $10; Para-Goomba
	.byte $74, $40, $10; Para-Goomba with Micro-Goombas
	.byte $73, $42, $10; Para-Goomba
	.byte $74, $44, $10; Para-Goomba with Micro-Goombas
	.byte $73, $46, $10; Para-Goomba
	.byte $74, $50, $10; Para-Goomba with Micro-Goombas
	.byte $73, $55, $16; Para-Goomba
	.byte $74, $5C, $16; Para-Goomba with Micro-Goombas
	.byte $73, $5D, $16; Para-Goomba
	.byte $74, $5E, $16; Para-Goomba with Micro-Goombas
	.byte $73, $5F, $16; Para-Goomba
	.byte $74, $60, $16; Para-Goomba with Micro-Goombas
	.byte $41, $68, $15; Goal Card
	.byte $FF
; Pipe_2_End_1_W8
; Object Set 14
Pipe_2_End_1_W8_generators:
Pipe_2_End_1_W8_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_0F0; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $1A, $00, $50, $0F; Hilly Fill
	.byte $80 | $15, $00, $54, $00; Hilly Fill
	.byte $60 | $0F, $00, $E5; Hilly Wall - Right Side
	.byte $80 | $15, $01, $84, $04; Flat Land - Hilly
	.byte $00 | $15, $06, $54; 45 Degree Hill - Down/Right
	.byte $80 | $1A, $0B, $80, $03; Flat Land - Hilly
	.byte $80 | $0F, $0F, $5B, $00; Hilly Fill
	.byte $00 | $14, $0F, $E5; Hilly Wall - Left Side
	.byte $80 | $0F, $0B, $B4, $03; Ceiling - Hilly
	.byte $00 | $0F, $06, $74; 45 Degree Hill - Up/Left
	.byte $80 | $0F, $03, $B0, $03; Ceiling - Hilly
	.byte $00 | $0F, $03, $07; Lower Left Corner - Hilly
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $18, $0D, $91; Downward Pipe (CAN go down)
	.byte $80 | $1A, $0D, $50, $01; Hilly Fill
	.byte $FF
Pipe_2_End_1_W8_objects:
	.byte $25, $02, $0F; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Tank__1_W8
; Object Set 10
Tank__1_W8_generators:
Tank__1_W8_header:
	.byte $55; Next Level
	.byte LEVEL1_SIZE_13 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_06; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $15; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $60 | $19, $00, $3F; Ground (like on tank levels)
	.byte $60 | $19, $10, $3F; Ground (like on tank levels)
	.byte $60 | $19, $20, $3F; Ground (like on tank levels)
	.byte $60 | $19, $30, $3F; Ground (like on tank levels)
	.byte $60 | $19, $40, $3F; Ground (like on tank levels)
	.byte $60 | $19, $50, $3F; Ground (like on tank levels)
	.byte $60 | $19, $60, $3F; Ground (like on tank levels)
	.byte $60 | $19, $70, $3F; Ground (like on tank levels)
	.byte $60 | $19, $80, $3F; Ground (like on tank levels)
	.byte $60 | $19, $90, $3F; Ground (like on tank levels)
	.byte $60 | $19, $A0, $3F; Ground (like on tank levels)
	.byte $60 | $19, $B0, $3F; Ground (like on tank levels)
	.byte $60 | $19, $C0, $3F; Ground (like on tank levels)
	.byte $00 | $17, $0C, $13; Wooden Ship Beam
	.byte $60 | $18, $0C, $B3; Tank Wheels
	.byte $40 | $17, $0C, $0F; Left terminus of wooden tank beam
	.byte $60 | $16, $0D, $00; Rocky Wrench hole
	.byte $60 | $17, $12, $70, $1D; Wooden Tank Beam
	.byte $00 | $16, $17, $11; Wooden Ship Beam
	.byte $40 | $17, $12, $0F; Left terminus of wooden tank beam
	.byte $00 | $15, $17, $06; Bullet Shooter - Up/Left
	.byte $00 | $16, $1A, $07; Bullet Shooter - Up/Right
	.byte $60 | $16, $15, $A1; Leftward Bullet Shooter
	.byte $60 | $18, $12, $B4; Tank Wheels
	.byte $00 | $16, $22, $11; Wooden Ship Beam
	.byte $00 | $16, $2C, $11; Wooden Ship Beam
	.byte $60 | $16, $20, $A1; Leftward Bullet Shooter
	.byte $60 | $16, $2A, $A1; Leftward Bullet Shooter
	.byte $00 | $16, $26, $06; Bullet Shooter - Up/Left
	.byte $00 | $15, $2D, $06; Bullet Shooter - Up/Left
	.byte $00 | $15, $23, $06; Bullet Shooter - Up/Left
	.byte $60 | $18, $2A, $B4; Tank Wheels
	.byte $60 | $17, $37, $A1; Leftward Bullet Shooter
	.byte $00 | $17, $38, $13; Wooden Ship Beam
	.byte $60 | $18, $38, $B3; Tank Wheels
	.byte $60 | $16, $39, $00; Rocky Wrench hole
	.byte $00 | $16, $3B, $07; Bullet Shooter - Up/Right
	.byte $60 | $18, $37, $C0; Invisible Platform
	.byte $40 | $14, $41, $0C; Tank A
	.byte $40 | $14, $4E, $0C; Tank A
	.byte $60 | $17, $41, $C1; Invisible Platform
	.byte $60 | $17, $4E, $C1; Invisible Platform
	.byte $40 | $14, $5B, $0C; Tank A
	.byte $00 | $17, $5B, $15; Wooden Ship Beam
	.byte $40 | $17, $5B, $0F; Left terminus of wooden tank beam
	.byte $60 | $18, $59, $70, $02; Wooden Tank Beam
	.byte $60 | $18, $59, $A0; Leftward Bullet Shooter
	.byte $00 | $16, $60, $07; Bullet Shooter - Up/Right
	.byte $40 | $14, $66, $0D; Tank B
	.byte $60 | $17, $66, $C1; Invisible Platform
	.byte $20 | $15, $6E, $01; '?' with leaf
	.byte $40 | $14, $76, $0D; Tank B
	.byte $00 | $16, $7F, $07; Bullet Shooter - Up/Right
	.byte $60 | $17, $76, $C1; Invisible Platform
	.byte $00 | $16, $80, $07; Bullet Shooter - Up/Right
	.byte $40 | $14, $86, $0D; Tank B
	.byte $00 | $16, $8F, $07; Bullet Shooter - Up/Right
	.byte $60 | $17, $86, $C1; Invisible Platform
	.byte $00 | $15, $97, $13; Wooden Ship Beam
	.byte $00 | $16, $97, $13; Wooden Ship Beam
	.byte $00 | $17, $95, $16; Wooden Ship Beam
	.byte $60 | $18, $95, $B5; Tank Wheels
	.byte $60 | $14, $98, $00; Rocky Wrench hole
	.byte $00 | $14, $9A, $07; Bullet Shooter - Up/Right
	.byte $40 | $15, $97, $0F; Left terminus of wooden tank beam
	.byte $00 | $16, $96, $06; Bullet Shooter - Up/Left
	.byte $40 | $17, $95, $0F; Left terminus of wooden tank beam
	.byte $00 | $16, $9B, $07; Bullet Shooter - Up/Right
	.byte $00 | $17, $AB, $14; Wooden Ship Beam
	.byte $60 | $16, $AE, $00; Rocky Wrench hole
	.byte $40 | $17, $AB, $0F; Left terminus of wooden tank beam
	.byte $60 | $18, $AC, $B3; Tank Wheels
	.byte $60 | $18, $A9, $70, $02; Wooden Tank Beam
	.byte $60 | $18, $A9, $A0; Leftward Bullet Shooter
	.byte $00 | $13, $B4, $14; Wooden Ship Beam
	.byte $40 | $13, $B4, $0F; Left terminus of wooden tank beam
	.byte $00 | $14, $B4, $14; Wooden Ship Beam
	.byte $60 | $15, $B3, $70, $05; Wooden Tank Beam
	.byte $00 | $16, $B2, $19; Wooden Ship Beam
	.byte $40 | $16, $B2, $0F; Left terminus of wooden tank beam
	.byte $60 | $17, $B2, $70, $09; Wooden Tank Beam
	.byte $00 | $17, $B2, $14; Wooden Ship Beam
	.byte $60 | $18, $B2, $B8; Tank Wheels
	.byte $60 | $12, $B5, $00; Rocky Wrench hole
	.byte $00 | $12, $B7, $06; Bullet Shooter - Up/Left
	.byte $00 | $12, $B8, $07; Bullet Shooter - Up/Right
	.byte $00 | $15, $B9, $07; Bullet Shooter - Up/Right
	.byte $60 | $14, $B1, $82; Leftward Giant Bullet Shooter
	.byte $00 | $14, $C0, $16; Wooden Ship Beam
	.byte $00 | $15, $C0, $17; Wooden Ship Beam
	.byte $00 | $16, $C0, $17; Wooden Ship Beam
	.byte $00 | $17, $C0, $17; Wooden Ship Beam
	.byte $40 | $14, $C0, $0F; Left terminus of wooden tank beam
	.byte $60 | $18, $C0, $B7; Tank Wheels
	.byte $20 | $12, $C3, $91; Downward Pipe (CAN go down)
	; Pointer on screen $0C
	.byte $E0 | $0C, $40 | $02, 16; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Tank__1_W8_objects:
	.byte $D3, $00, $13; Autoscrolling
	.byte $C2, $15, $16; Bullet Shots (leftward)
	.byte $C4, $17, $15; Bullet Shots (up/left)
	.byte $CF, $1A, $16; Infinite Bob-Ombs (rightward) (use with bullet shooters)
	.byte $C2, $20, $16; Bullet Shots (leftward)
	.byte $CE, $23, $15; Infinite Bob-Ombs (leftward) (use with bullet shooters)
	.byte $C4, $26, $16; Bullet Shots (up/left)
	.byte $C2, $2A, $16; Bullet Shots (leftward)
	.byte $C4, $2D, $15; Bullet Shots (up/left)
	.byte $AC, $34, $17; Leftward Rocket Engine
	.byte $AD, $39, $17; Brown Rocky Wrench
	.byte $CF, $3B, $16; Infinite Bob-Ombs (rightward) (use with bullet shooters)
	.byte $C2, $41, $16; Bullet Shots (leftward)
	.byte $AD, $44, $15; Brown Rocky Wrench
	.byte $C2, $4E, $16; Bullet Shots (leftward)
	.byte $AD, $51, $15; Brown Rocky Wrench
	.byte $C2, $59, $18; Bullet Shots (leftward)
	.byte $C2, $5B, $16; Bullet Shots (leftward)
	.byte $AD, $5E, $15; Brown Rocky Wrench
	.byte $CF, $60, $16; Infinite Bob-Ombs (rightward) (use with bullet shooters)
	.byte $C2, $66, $16; Bullet Shots (leftward)
	.byte $AD, $6B, $15; Brown Rocky Wrench
	.byte $C2, $76, $16; Bullet Shots (leftward)
	.byte $AD, $7B, $15; Brown Rocky Wrench
	.byte $C5, $7F, $16; Bullet Shots (up/right)
	.byte $CF, $80, $16; Infinite Bob-Ombs (rightward) (use with bullet shooters)
	.byte $C2, $86, $16; Bullet Shots (leftward)
	.byte $AD, $8B, $15; Brown Rocky Wrench
	.byte $CF, $8F, $16; Infinite Bob-Ombs (rightward) (use with bullet shooters)
	.byte $CE, $96, $16; Infinite Bob-Ombs (leftward) (use with bullet shooters)
	.byte $AD, $98, $15; Brown Rocky Wrench
	.byte $C5, $9A, $14; Bullet Shots (up/right)
	.byte $CF, $9B, $16; Infinite Bob-Ombs (rightward) (use with bullet shooters)
	.byte $C2, $A9, $18; Bullet Shots (leftward)
	.byte $C3, $B1, $14; Big Bullet Shots (leftward)
	.byte $AD, $B5, $13; Brown Rocky Wrench
	.byte $C4, $B7, $12; Bullet Shots (up/left)
	.byte $C5, $B8, $12; Bullet Shots (up/right)
	.byte $C5, $B9, $15; Bullet Shots (up/right)
	.byte $FF
; Battleship_W8
; Object Set 10
Battleship_W8_generators:
Battleship_W8_header:
	.byte $56; Next Level
	.byte LEVEL1_SIZE_10 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_07; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $E0 | $15; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $40 | $19, $00, $81, $9F; Water (still)
	.byte $20 | $15, $0B, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $15, $1F, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $14, $2A, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $45, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $14, $4A, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $14, $5B, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $15, $76, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $15, $83, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $15, $8A, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $16, $03, $20, $2E; Wooden Ship Beam
	.byte $60 | $17, $04, $70, $2D; Wooden Tank Beam
	.byte $60 | $18, $05, $70, $2B; Wooden Tank Beam
	.byte $00 | $16, $03, $03; Wooden ship beam terminus A
	.byte $40 | $18, $05, $0A; Wooden ship beam terminus B
	.byte $00 | $13, $0B, $13; Wooden Ship Beam
	.byte $40 | $13, $0B, $0F; Left terminus of wooden tank beam
	.byte $60 | $14, $0A, $70, $04; Wooden Tank Beam
	.byte $60 | $14, $08, $A2; Leftward Bullet Shooter
	.byte $60 | $15, $08, $C0; Invisible Platform
	.byte $00 | $11, $10, $64; Thick Wooden Ship Beam
	.byte $00 | $11, $12, $17; Wooden Ship Beam
	.byte $00 | $12, $15, $08; Bullet Shooter - Down/Left
	.byte $00 | $12, $19, $08; Bullet Shooter - Down/Left
	.byte $00 | $13, $1F, $13; Wooden Ship Beam
	.byte $60 | $14, $1E, $70, $04; Wooden Tank Beam
	.byte $40 | $13, $1F, $0F; Left terminus of wooden tank beam
	.byte $60 | $14, $1C, $A2; Leftward Bullet Shooter
	.byte $20 | $13, $12, $00; '?' with flower
	.byte $60 | $15, $1C, $C0; Invisible Platform
	.byte $00 | $12, $28, $14; Wooden Ship Beam
	.byte $00 | $13, $28, $14; Wooden Ship Beam
	.byte $00 | $13, $28, $03; Wooden ship beam terminus A
	.byte $00 | $15, $28, $19; Wooden Ship Beam
	.byte $60 | $12, $2D, $92; Rightward Giant Bullet Shooter
	.byte $00 | $12, $22, $07; Bullet Shooter - Up/Right
	.byte $60 | $14, $28, $C0; Invisible Platform
	.byte $00 | $16, $3B, $16; Wooden Ship Beam
	.byte $00 | $16, $3B, $03; Wooden ship beam terminus A
	.byte $60 | $17, $3C, $70, $2A; Wooden Tank Beam
	.byte $60 | $18, $3D, $70, $28; Wooden Tank Beam
	.byte $40 | $18, $3D, $0A; Wooden ship beam terminus B
	.byte $00 | $15, $49, $20, $1D; Wooden Ship Beam
	.byte $00 | $16, $49, $20, $1D; Wooden Ship Beam
	.byte $00 | $12, $4A, $13; Wooden Ship Beam
	.byte $60 | $13, $49, $70, $04; Wooden Tank Beam
	.byte $60 | $13, $47, $A2; Leftward Bullet Shooter
	.byte $40 | $12, $4A, $0F; Left terminus of wooden tank beam
	.byte $00 | $14, $45, $13; Wooden Ship Beam
	.byte $60 | $15, $44, $70, $04; Wooden Tank Beam
	.byte $40 | $14, $45, $0F; Left terminus of wooden tank beam
	.byte $60 | $15, $42, $A2; Leftward Bullet Shooter
	.byte $00 | $11, $50, $63; Thick Wooden Ship Beam
	.byte $00 | $11, $52, $63; Thick Wooden Ship Beam
	.byte $00 | $13, $54, $14; Wooden Ship Beam
	.byte $00 | $14, $54, $14; Wooden Ship Beam
	.byte $00 | $12, $59, $13; Wooden Ship Beam
	.byte $00 | $13, $59, $13; Wooden Ship Beam
	.byte $00 | $13, $59, $03; Wooden ship beam terminus A
	.byte $60 | $12, $5D, $92; Rightward Giant Bullet Shooter
	.byte $00 | $14, $61, $15; Wooden Ship Beam
	.byte $00 | $15, $6B, $17; Wooden Ship Beam
	.byte $00 | $15, $6B, $03; Wooden ship beam terminus A
	.byte $00 | $16, $6C, $20, $2F; Wooden Ship Beam
	.byte $00 | $16, $6C, $03; Wooden ship beam terminus A
	.byte $60 | $17, $6D, $70, $2E; Wooden Tank Beam
	.byte $60 | $18, $6F, $70, $2B; Wooden Tank Beam
	.byte $40 | $17, $6D, $0A; Wooden ship beam terminus B
	.byte $40 | $18, $6F, $0A; Wooden ship beam terminus B
	.byte $00 | $12, $76, $13; Wooden Ship Beam
	.byte $00 | $13, $76, $13; Wooden Ship Beam
	.byte $60 | $14, $75, $70, $04; Wooden Tank Beam
	.byte $40 | $12, $76, $0F; Left terminus of wooden tank beam
	.byte $60 | $13, $73, $82; Leftward Giant Bullet Shooter
	.byte $00 | $15, $7F, $06; Bullet Shooter - Up/Left
	.byte $00 | $12, $84, $12; Wooden Ship Beam
	.byte $00 | $13, $83, $13; Wooden Ship Beam
	.byte $60 | $14, $81, $70, $05; Wooden Tank Beam
	.byte $60 | $12, $82, $A1; Leftward Bullet Shooter
	.byte $60 | $13, $81, $A1; Leftward Bullet Shooter
	.byte $60 | $14, $80, $A1; Leftward Bullet Shooter
	.byte $00 | $12, $89, $13; Wooden Ship Beam
	.byte $00 | $13, $89, $13; Wooden Ship Beam
	.byte $60 | $14, $89, $70, $03; Wooden Tank Beam
	.byte $60 | $12, $8D, $92; Rightward Giant Bullet Shooter
	.byte $60 | $15, $80, $C0; Invisible Platform
	.byte $60 | $15, $89, $C0; Invisible Platform
	.byte $00 | $14, $94, $16; Wooden Ship Beam
	.byte $00 | $15, $91, $1A; Wooden Ship Beam
	.byte $20 | $12, $97, $91; Downward Pipe (CAN go down)
	; Pointer on screen $09
	.byte $E0 | $09, $40 | $02, 16; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Battleship_W8_objects:
	.byte $D3, $00, $0E; Autoscrolling
	.byte $BE, $0D, $13; Rocky Wrench
	.byte $C2, $08, $14; Bullet Shots (leftward)
	.byte $C6, $15, $12; Bullet Shots (down/left)
	.byte $C6, $19, $12; Bullet Shots (down/left)
	.byte $C2, $1C, $14; Bullet Shots (leftward)
	.byte $BE, $20, $13; Rocky Wrench
	.byte $CF, $22, $12; Infinite Bob-Ombs (rightward) (use with bullet shooters)
	.byte $BE, $2A, $12; Rocky Wrench
	.byte $CD, $2F, $12; Big Bullet Shots (rightward)
	.byte $C2, $42, $15; Bullet Shots (leftward)
	.byte $C2, $47, $13; Bullet Shots (leftward)
	.byte $BE, $4C, $12; Rocky Wrench
	.byte $BE, $52, $11; Rocky Wrench
	.byte $BE, $57, $13; Rocky Wrench
	.byte $BE, $5C, $12; Rocky Wrench
	.byte $CD, $5F, $12; Big Bullet Shots (rightward)
	.byte $C3, $73, $13; Big Bullet Shots (leftward)
	.byte $BE, $78, $12; Rocky Wrench
	.byte $CE, $7F, $15; Infinite Bob-Ombs (leftward) (use with bullet shooters)
	.byte $C2, $80, $14; Bullet Shots (leftward)
	.byte $C2, $81, $13; Bullet Shots (leftward)
	.byte $C2, $82, $12; Bullet Shots (leftward)
	.byte $CD, $8F, $12; Big Bullet Shots (rightward)
	.byte $50, $95, $13; Bob-Omb (about to blow up)
	.byte $50, $97, $11; Bob-Omb (about to blow up)
	.byte $FF
; Pipe_2_End_2_W8
; Object Set 14
Pipe_2_End_2_W8_generators:
Pipe_2_End_2_W8_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_D8 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $40 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $1A, $00, $50, $0F; Hilly Fill
	.byte $80 | $15, $00, $54, $00; Hilly Fill
	.byte $60 | $0F, $00, $E5; Hilly Wall - Right Side
	.byte $80 | $15, $01, $84, $04; Flat Land - Hilly
	.byte $00 | $15, $06, $54; 45 Degree Hill - Down/Right
	.byte $80 | $1A, $0B, $80, $03; Flat Land - Hilly
	.byte $80 | $0F, $0F, $5B, $00; Hilly Fill
	.byte $00 | $14, $0F, $E5; Hilly Wall - Left Side
	.byte $80 | $0F, $0B, $B4, $03; Ceiling - Hilly
	.byte $00 | $0F, $06, $74; 45 Degree Hill - Up/Left
	.byte $80 | $0F, $03, $B0, $03; Ceiling - Hilly
	.byte $00 | $0F, $03, $07; Lower Left Corner - Hilly
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $18, $0D, $91; Downward Pipe (CAN go down)
	.byte $80 | $1A, $0D, $50, $01; Hilly Fill
	.byte $FF
Pipe_2_End_2_W8_objects:
	.byte $25, $02, $0F; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Pipe_4_End_1_W8
; Object Set 14
Pipe_4_End_1_W8_generators:
Pipe_4_End_1_W8_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_0F0; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $1A, $00, $50, $0F; Hilly Fill
	.byte $80 | $15, $00, $54, $00; Hilly Fill
	.byte $60 | $0F, $00, $E5; Hilly Wall - Right Side
	.byte $80 | $15, $01, $84, $04; Flat Land - Hilly
	.byte $00 | $15, $06, $54; 45 Degree Hill - Down/Right
	.byte $80 | $1A, $0B, $80, $03; Flat Land - Hilly
	.byte $80 | $0F, $0F, $5B, $00; Hilly Fill
	.byte $00 | $14, $0F, $E5; Hilly Wall - Left Side
	.byte $80 | $0F, $0B, $B4, $03; Ceiling - Hilly
	.byte $00 | $0F, $06, $74; 45 Degree Hill - Up/Left
	.byte $80 | $0F, $03, $B0, $03; Ceiling - Hilly
	.byte $00 | $0F, $03, $07; Lower Left Corner - Hilly
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $18, $0D, $91; Downward Pipe (CAN go down)
	.byte $80 | $1A, $0D, $50, $01; Hilly Fill
	.byte $FF
Pipe_4_End_1_W8_objects:
	.byte $25, $02, $0D; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Crappy_Ship_W8
; Object Set 10
Crappy_Ship_W8_generators:
Crappy_Ship_W8_header:
	.byte $07; Next Level
	.byte LEVEL1_SIZE_12 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_06; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $E0 | $0A; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $60 | $15, $06, $01; Ship Platform A
	.byte $60 | $16, $0C, $01; Ship Platform A
	.byte $00 | $19, $12, $15; Wooden Ship Beam
	.byte $00 | $19, $12, $03; Wooden ship beam terminus A
	.byte $00 | $18, $17, $01; 2-Way Bullet Shooter
	.byte $60 | $18, $14, $00; Rocky Wrench hole
	.byte $00 | $17, $16, $41; Wooden Ship Pillar
	.byte $60 | $18, $1E, $70, $07; Wooden Tank Beam
	.byte $00 | $17, $20, $15; Wooden Ship Beam
	.byte $40 | $17, $20, $0F; Left terminus of wooden tank beam
	.byte $00 | $14, $24, $42; Wooden Ship Pillar
	.byte $00 | $16, $25, $01; 2-Way Bullet Shooter
	.byte $60 | $16, $2C, $01; Ship Platform A
	.byte $60 | $16, $22, $00; Rocky Wrench hole
	.byte $00 | $14, $34, $15; Wooden Ship Beam
	.byte $00 | $14, $34, $03; Wooden ship beam terminus A
	.byte $60 | $13, $35, $00; Rocky Wrench hole
	.byte $00 | $12, $37, $41; Wooden Ship Pillar
	.byte $00 | $13, $39, $01; 2-Way Bullet Shooter
	.byte $60 | $14, $40, $02; Ship Platform B
	.byte $60 | $15, $47, $02; Ship Platform B
	.byte $60 | $16, $4E, $02; Ship Platform B
	.byte $00 | $18, $56, $12; Wooden Ship Beam
	.byte $00 | $18, $56, $03; Wooden ship beam terminus A
	.byte $60 | $19, $57, $70, $0C; Wooden Tank Beam
	.byte $60 | $15, $5C, $53; Crate
	.byte $00 | $18, $61, $12; Wooden Ship Beam
	.byte $00 | $16, $63, $01; 2-Way Bullet Shooter
	.byte $00 | $17, $63, $01; 2-Way Bullet Shooter
	.byte $60 | $11, $65, $02; Ship Platform B
	.byte $60 | $18, $6F, $01; Ship Platform A
	.byte $60 | $16, $7A, $01; Ship Platform A
	.byte $60 | $11, $82, $01; Ship Platform A
	.byte $60 | $18, $8D, $01; Ship Platform A
	.byte $60 | $13, $94, $01; Ship Platform A
	.byte $60 | $15, $A1, $01; Ship Platform A
	.byte $00 | $17, $AD, $13; Wooden Ship Beam
	.byte $00 | $17, $AD, $03; Wooden ship beam terminus A
	.byte $60 | $18, $AE, $70, $0E; Wooden Tank Beam
	.byte $00 | $17, $BC, $72; Corkscrew - Left terminus
	.byte $00 | $17, $BA, $12; Wooden Ship Beam
	.byte $00 | $14, $B3, $14; Wooden Ship Beam
	.byte $00 | $15, $B3, $14; Wooden Ship Beam
	.byte $00 | $16, $B3, $14; Wooden Ship Beam
	.byte $00 | $17, $B3, $14; Wooden Ship Beam
	.byte $20 | $12, $B4, $91; Downward Pipe (CAN go down)
	; Pointer on screen $0B
	.byte $E0 | $0B, $40 | $02, 16; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Crappy_Ship_W8_objects:
	.byte $D3, $00, $0D; Autoscrolling
	.byte $B8, $01, $03; Moving Background Clouds
	.byte $B1, $0B, $15; Rightward Rocket Engine
	.byte $AD, $0E, $17; Brown Rocky Wrench
	.byte $B1, $11, $16; Rightward Rocket Engine
	.byte $AD, $14, $19; Brown Rocky Wrench
	.byte $B1, $18, $18; Rightward Rocket Engine
	.byte $AD, $22, $17; Brown Rocky Wrench
	.byte $B1, $26, $16; Rightward Rocket Engine
	.byte $AD, $2E, $17; Brown Rocky Wrench
	.byte $B1, $31, $16; Rightward Rocket Engine
	.byte $B1, $3A, $13; Rightward Rocket Engine
	.byte $AD, $43, $14; Brown Rocky Wrench
	.byte $B1, $45, $15; Rightward Rocket Engine
	.byte $B1, $4C, $16; Rightward Rocket Engine
	.byte $AD, $51, $16; Brown Rocky Wrench
	.byte $B1, $53, $17; Rightward Rocket Engine
	.byte $B1, $64, $16; Rightward Rocket Engine
	.byte $B1, $64, $17; Rightward Rocket Engine
	.byte $AD, $68, $11; Brown Rocky Wrench
	.byte $B1, $6A, $12; Rightward Rocket Engine
	.byte $B1, $74, $18; Rightward Rocket Engine
	.byte $AD, $7C, $17; Brown Rocky Wrench
	.byte $B1, $7F, $16; Rightward Rocket Engine
	.byte $AD, $84, $12; Brown Rocky Wrench
	.byte $B1, $87, $11; Rightward Rocket Engine
	.byte $AD, $8F, $19; Brown Rocky Wrench
	.byte $B1, $92, $18; Rightward Rocket Engine
	.byte $AD, $96, $14; Brown Rocky Wrench
	.byte $B1, $99, $13; Rightward Rocket Engine
	.byte $AD, $A3, $16; Brown Rocky Wrench
	.byte $B1, $A6, $15; Rightward Rocket Engine
	.byte $AA, $BE, $17; Propeller
	.byte $FF
; Pipe_3_End_1_W8
; Object Set 14
Pipe_3_End_1_W8_generators:
Pipe_3_End_1_W8_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_0F0; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $1A, $00, $50, $0F; Hilly Fill
	.byte $80 | $15, $00, $54, $00; Hilly Fill
	.byte $60 | $0F, $00, $E5; Hilly Wall - Right Side
	.byte $80 | $15, $01, $84, $04; Flat Land - Hilly
	.byte $00 | $15, $06, $54; 45 Degree Hill - Down/Right
	.byte $80 | $1A, $0B, $80, $03; Flat Land - Hilly
	.byte $80 | $0F, $0F, $5B, $00; Hilly Fill
	.byte $00 | $14, $0F, $E5; Hilly Wall - Left Side
	.byte $80 | $0F, $0B, $B4, $03; Ceiling - Hilly
	.byte $00 | $0F, $06, $74; 45 Degree Hill - Up/Left
	.byte $80 | $0F, $03, $B0, $03; Ceiling - Hilly
	.byte $00 | $0F, $03, $07; Lower Left Corner - Hilly
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $18, $0D, $91; Downward Pipe (CAN go down)
	.byte $80 | $1A, $0D, $50, $01; Hilly Fill
	.byte $FF
Pipe_3_End_1_W8_objects:
	.byte $25, $02, $10; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Hand_Trap__3_W8
; Object Set 11
Hand_Trap__3_W8_generators:
Hand_Trap__3_W8_header:
	.byte $57; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_03; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_11; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0B; Start action | Graphic set
	.byte $80 | $01; Time | Music
	.byte $60 | $19, $0E, $71, $63; Lava
	.byte $40 | $16, $00, $B4, $06; Blue X-Blocks
	.byte $40 | $14, $07, $B6, $06; Blue X-Blocks
	.byte $40 | $14, $0E, $4E; Bridge
	.byte $20 | $11, $18, $21; '?' blocks with single coins
	.byte $40 | $14, $20, $42; Bridge
	.byte $40 | $14, $25, $41; Bridge
	.byte $40 | $14, $2A, $43; Bridge
	.byte $40 | $14, $31, $49; Bridge
	.byte $40 | $14, $3D, $45; Bridge
	.byte $20 | $11, $3F, $00; '?' with flower
	.byte $20 | $12, $37, $40; Wooden blocks
	.byte $20 | $13, $37, $40; Wooden blocks
	.byte $40 | $14, $43, $49; Bridge
	.byte $40 | $14, $4F, $45; Bridge
	.byte $20 | $0E, $44, $40; Wooden blocks
	.byte $20 | $0F, $44, $40; Wooden blocks
	.byte $20 | $10, $44, $40; Wooden blocks
	.byte $20 | $11, $44, $40; Wooden blocks
	.byte $20 | $12, $44, $40; Wooden blocks
	.byte $20 | $13, $44, $40; Wooden blocks
	.byte $20 | $12, $48, $40; Wooden blocks
	.byte $20 | $13, $48, $40; Wooden blocks
	.byte $20 | $14, $48, $40; Wooden blocks
	.byte $20 | $15, $48, $40; Wooden blocks
	.byte $20 | $16, $48, $40; Wooden blocks
	.byte $40 | $14, $57, $44; Bridge
	.byte $40 | $14, $5F, $4A; Bridge
	.byte $40 | $14, $60, $49; Bridge
	.byte $40 | $14, $6D, $44; Bridge
	.byte $40 | $14, $72, $B6, $0D; Blue X-Blocks
	.byte $40 | $00, $7C, $B7, $03; Blue X-Blocks
	.byte $40 | $08, $7F, $BB, $00; Blue X-Blocks
	.byte $20 | $11, $74, $80; Coins
	.byte $20 | $10, $75, $81; Coins
	.byte $20 | $11, $77, $81; Coins
	.byte $20 | $10, $79, $81; Coins
	.byte $20 | $11, $7B, $80; Coins
	.byte $20 | $08, $7D, $C8; Upward Pipe (CAN go up)
	; Pointer on screen $07
	.byte $E0 | $07, $50 | $01, 16; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Hand_Trap__3_W8_objects:
	.byte $BB, $04, $19; Stops infinite flying or spiny Cheep-Cheeps
	.byte $B4, $17, $19; Infinite flying Cheep-Cheeps
	.byte $B4, $5C, $19; Infinite flying Cheep-Cheeps
	.byte $BB, $70, $19; Stops infinite flying or spiny Cheep-Cheeps
	.byte $FF
; Hand_Trap__2_W8
; Object Set 11
Hand_Trap__2_W8_generators:
Hand_Trap__2_W8_header:
	.byte $57; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_03; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_11; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0B; Start action | Graphic set
	.byte $80 | $01; Time | Music
	.byte $60 | $19, $00, $71, $3F; Lava
	.byte $40 | $19, $00, $B1, $09; Blue X-Blocks
	.byte $40 | $17, $04, $B1, $05; Blue X-Blocks
	.byte $40 | $15, $06, $B1, $03; Blue X-Blocks
	.byte $40 | $14, $0A, $42; Bridge
	.byte $20 | $11, $0D, $81; Coins
	.byte $20 | $12, $0F, $80; Coins
	.byte $40 | $16, $10, $41; Bridge
	.byte $40 | $14, $14, $42; Bridge
	.byte $40 | $16, $1B, $42; Bridge
	.byte $20 | $13, $10, $81; Coins
	.byte $20 | $11, $14, $82; Coins
	.byte $20 | $11, $18, $81; Coins
	.byte $20 | $12, $1A, $80; Coins
	.byte $40 | $16, $20, $41; Bridge
	.byte $40 | $14, $27, $42; Bridge
	.byte $40 | $13, $2E, $42; Bridge
	.byte $20 | $13, $20, $80; Coins
	.byte $20 | $11, $27, $82; Coins
	.byte $20 | $10, $2D, $84; Coins
	.byte $40 | $00, $3C, $B9, $03; Blue X-Blocks
	.byte $40 | $0A, $3F, $BC, $00; Blue X-Blocks
	.byte $40 | $17, $36, $B3, $09; Blue X-Blocks
	.byte $20 | $12, $33, $80; Coins
	.byte $20 | $13, $34, $80; Coins
	.byte $20 | $0A, $3D, $C8; Upward Pipe (CAN go up)
	; Pointer on screen $03
	.byte $E0 | $03, $50 | $01, 16; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Hand_Trap__2_W8_objects:
	.byte $9E, $0E, $0D; Podoboo (comes out of lava)
	.byte $9E, $12, $0F; Podoboo (comes out of lava)
	.byte $9E, $19, $10; Podoboo (comes out of lava)
	.byte $9E, $17, $0D; Podoboo (comes out of lava)
	.byte $9E, $1E, $11; Podoboo (comes out of lava)
	.byte $9E, $23, $10; Podoboo (comes out of lava)
	.byte $9E, $2B, $0F; Podoboo (comes out of lava)
	.byte $9E, $25, $0B; Podoboo (comes out of lava)
	.byte $9E, $33, $0F; Podoboo (comes out of lava)
	.byte $FF
; Hand_Trap__1_W8
; Object Set 11
Hand_Trap__1_W8_generators:
Hand_Trap__1_W8_header:
	.byte $57; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_03; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_11; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0B; Start action | Graphic set
	.byte $80 | $01; Time | Music
	.byte $60 | $19, $00, $71, $0D; Lava
	.byte $60 | $19, $26, $71, $19; Lava
	.byte $40 | $15, $00, $4D; Bridge
	.byte $40 | $16, $0E, $B4, $01; Blue X-Blocks
	.byte $40 | $15, $0F, $B0, $00; Blue X-Blocks
	.byte $40 | $19, $10, $4F; Bridge
	.byte $20 | $12, $19, $16; Bricks
	.byte $20 | $16, $19, $16; Bricks
	.byte $20 | $12, $1F, $30; Bricks with single coins
	.byte $20 | $16, $1E, $31; Bricks with single coins
	.byte $20 | $16, $1D, $07; Brick with Leaf
	.byte $40 | $12, $20, $B8, $02; Blue X-Blocks
	.byte $40 | $15, $23, $B5, $02; Blue X-Blocks
	.byte $40 | $14, $26, $4F; Bridge
	.byte $40 | $14, $36, $48; Bridge
	.byte $40 | $00, $3D, $B9, $02; Blue X-Blocks
	.byte $40 | $0A, $3F, $BF, $00; Blue X-Blocks
	.byte $40 | $1A, $3F, $B0, $00; Blue X-Blocks
	.byte $20 | $0A, $3D, $C7; Upward Pipe (CAN go up)
	; Pointer on screen $03
	.byte $E0 | $03, $50 | $01, 16; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Hand_Trap__1_W8_objects:
	.byte $87, $0D, $14; Fire Brother
	.byte $81, $1B, $18; Hammer Brother
	.byte $81, $1D, $14; Hammer Brother
	.byte $82, $2D, $13; Boomerang Brother
	.byte $86, $37, $13; Sledge Brother
	.byte $FF
; Pipe_1_End_2_W8
; Object Set 14
Pipe_1_End_2_W8_generators:
Pipe_1_End_2_W8_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_D8 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $40 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $1A, $00, $50, $0F; Hilly Fill
	.byte $80 | $15, $00, $54, $00; Hilly Fill
	.byte $60 | $0F, $00, $E5; Hilly Wall - Right Side
	.byte $80 | $15, $01, $84, $04; Flat Land - Hilly
	.byte $00 | $15, $06, $54; 45 Degree Hill - Down/Right
	.byte $80 | $1A, $0B, $80, $03; Flat Land - Hilly
	.byte $80 | $0F, $0F, $5B, $00; Hilly Fill
	.byte $00 | $14, $0F, $E5; Hilly Wall - Left Side
	.byte $80 | $0F, $0B, $B4, $03; Ceiling - Hilly
	.byte $00 | $0F, $06, $74; 45 Degree Hill - Up/Left
	.byte $80 | $0F, $03, $B0, $03; Ceiling - Hilly
	.byte $00 | $0F, $03, $07; Lower Left Corner - Hilly
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $18, $0D, $91; Downward Pipe (CAN go down)
	.byte $80 | $1A, $0D, $50, $01; Hilly Fill
	.byte $FF
Pipe_1_End_2_W8_objects:
	.byte $25, $02, $0C; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Pipe_4_End_2_W8
; Object Set 14
Pipe_4_End_2_W8_generators:
Pipe_4_End_2_W8_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_D8 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $40 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $1A, $00, $50, $0F; Hilly Fill
	.byte $80 | $15, $00, $54, $00; Hilly Fill
	.byte $60 | $0F, $00, $E5; Hilly Wall - Right Side
	.byte $80 | $15, $01, $84, $04; Flat Land - Hilly
	.byte $00 | $15, $06, $54; 45 Degree Hill - Down/Right
	.byte $80 | $1A, $0B, $80, $03; Flat Land - Hilly
	.byte $80 | $0F, $0F, $5B, $00; Hilly Fill
	.byte $00 | $14, $0F, $E5; Hilly Wall - Left Side
	.byte $80 | $0F, $0B, $B4, $03; Ceiling - Hilly
	.byte $00 | $0F, $06, $74; 45 Degree Hill - Up/Left
	.byte $80 | $0F, $03, $B0, $03; Ceiling - Hilly
	.byte $00 | $0F, $03, $07; Lower Left Corner - Hilly
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $18, $0D, $91; Downward Pipe (CAN go down)
	.byte $80 | $1A, $0D, $50, $01; Hilly Fill
	.byte $FF
Pipe_4_End_2_W8_objects:
	.byte $25, $02, $0D; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Pipe_6_End_1_W8
; Object Set 14
Pipe_6_End_1_W8_generators:
Pipe_6_End_1_W8_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_0F0; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $1A, $00, $50, $0F; Hilly Fill
	.byte $80 | $15, $00, $54, $00; Hilly Fill
	.byte $60 | $0F, $00, $E5; Hilly Wall - Right Side
	.byte $80 | $15, $01, $84, $04; Flat Land - Hilly
	.byte $00 | $15, $06, $54; 45 Degree Hill - Down/Right
	.byte $80 | $1A, $0B, $80, $03; Flat Land - Hilly
	.byte $80 | $0F, $0F, $5B, $00; Hilly Fill
	.byte $00 | $14, $0F, $E5; Hilly Wall - Left Side
	.byte $80 | $0F, $0B, $B4, $03; Ceiling - Hilly
	.byte $00 | $0F, $06, $74; 45 Degree Hill - Up/Left
	.byte $80 | $0F, $03, $B0, $03; Ceiling - Hilly
	.byte $00 | $0F, $03, $07; Lower Left Corner - Hilly
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $18, $0D, $91; Downward Pipe (CAN go down)
	.byte $80 | $1A, $0D, $50, $01; Hilly Fill
	.byte $FF
Pipe_6_End_1_W8_objects:
	.byte $25, $02, $0E; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_1_W8
; Object Set 1
Level_1_W8_generators:
Level_1_W8_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_11 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $00 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	.byte $00 | $1A, $00, $C0, $0B; Flat Ground
	.byte $20 | $19, $0B, $40; Wooden Blocks
	.byte $00 | $13, $0A, $E2; Background Clouds
	.byte $40 | $0F, $00, $5F; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $10, $00, $5F; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $11, $00, $5F; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $12, $00, $5F; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $13, $00, $5F; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $14, $00, $5F; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $15, $00, $5F; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $16, $00, $5F; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $17, $00, $5F; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $18, $00, $5F; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $19, $00, $5A; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $19, $0C, $53; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $1A, $0C, $53; Silver Coins (appear when you hit a P-Switch)
	.byte $00 | $19, $10, $C1, $08; Flat Ground
	.byte $20 | $13, $16, $A5; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $1C, $A4; Downward Pipe (CAN'T go down)
	.byte $00 | $16, $11, $01; Background Hills B
	.byte $20 | $15, $14, $20; '?' Blocks with single coins
	.byte $20 | $15, $18, $00; '?' with Flower
	.byte $00 | $11, $1D, $E2; Background Clouds
	.byte $00 | $12, $11, $E2; Background Clouds
	.byte $00 | $1A, $27, $C0, $88; Flat Ground
	.byte $20 | $0A, $28, $B8; Downward Pipe (CAN go down, ignores pointers)
	.byte $20 | $12, $24, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $14, $28, $D2; Upward Pipe (CAN'T go up)
	.byte $00 | $17, $2A, $01; Background Hills B
	.byte $00 | $19, $2E, $94; Background Bushes
	.byte $20 | $16, $24, $40; Wooden Blocks
	.byte $20 | $16, $25, $70; Wooden Blocks - movable
	.byte $20 | $13, $28, $70; Wooden Blocks - movable
	.byte $20 | $13, $29, $40; Wooden Blocks
	.byte $20 | $12, $2E, $13; Bricks
	.byte $20 | $15, $2E, $13; Bricks
	.byte $20 | $12, $2F, $0A; Multi-Coin Brick
	.byte $20 | $15, $2F, $30; Bricks with single coins
	.byte $20 | $13, $20, $A7; Downward Pipe (CAN'T go down)
	.byte $20 | $06, $05, $40; Wooden Blocks
	.byte $40 | $05, $05, $08; P-Switch
	.byte $00 | $1A, $34, $A6; Gap
	.byte $00 | $1A, $3C, $A3; Gap
	.byte $40 | $14, $3C, $34; Bullet Bill Machine
	.byte $40 | $19, $3C, $30; Bullet Bill Machine
	.byte $40 | $16, $37, $31; Bullet Bill Machine
	.byte $40 | $18, $37, $32; Bullet Bill Machine
	.byte $40 | $19, $34, $30; Bullet Bill Machine
	.byte $20 | $17, $3A, $02; '?' with Star
	.byte $00 | $11, $38, $E2; Background Clouds
	.byte $00 | $12, $35, $E2; Background Clouds
	.byte $40 | $08, $40, $BC, $0C; Blue X-Blocks
	.byte $40 | $15, $40, $B1, $03; Blue X-Blocks
	.byte $40 | $08, $4E, $BE, $01; Blue X-Blocks
	.byte $40 | $17, $4F, $B0, $00; Blue X-Blocks
	.byte $20 | $16, $44, $28; '?' Blocks with single coins
	.byte $20 | $16, $45, $0B; Brick with 1-up
	.byte $40 | $18, $4F, $30; Bullet Bill Machine
	.byte $40 | $19, $45, $30; Bullet Bill Machine
	.byte $00 | $19, $40, $92; Background Bushes
	.byte $00 | $19, $47, $96; Background Bushes
	.byte $00 | $1A, $51, $A4; Gap
	.byte $00 | $1A, $5A, $A3; Gap
	.byte $20 | $16, $50, $07; Brick with Leaf
	.byte $40 | $13, $50, $30; Bullet Bill Machine
	.byte $40 | $14, $50, $B0, $00; Blue X-Blocks
	.byte $20 | $11, $56, $21; '?' Blocks with single coins
	.byte $20 | $16, $5D, $20; '?' Blocks with single coins
	.byte $20 | $14, $5F, $A5; Downward Pipe (CAN'T go down)
	.byte $00 | $15, $56, $31; Green Block Platform (Extends to ground)
	.byte $00 | $17, $57, $32; Green Block Platform (Extends to ground)
	.byte $00 | $12, $5A, $E2; Background Clouds
	.byte $00 | $1A, $6B, $A7; Gap
	.byte $00 | $12, $62, $02; Background Hills C
	.byte $40 | $18, $6B, $31; Bullet Bill Machine
	.byte $00 | $11, $67, $E2; Background Clouds
	.byte $00 | $14, $6D, $E2; Background Clouds
	.byte $40 | $13, $72, $32; Bullet Bill Machine
	.byte $40 | $16, $72, $33; Bullet Bill Machine
	.byte $40 | $15, $7A, $32; Bullet Bill Machine
	.byte $40 | $18, $7A, $31; Bullet Bill Machine
	.byte $20 | $17, $77, $0E; Invisible Coin
	.byte $20 | $18, $73, $83; Coins
	.byte $00 | $19, $73, $96; Background Bushes
	.byte $00 | $14, $75, $E2; Background Clouds
	.byte $00 | $11, $7C, $E2; Background Clouds
	.byte $00 | $12, $7D, $02; Background Hills C
	.byte $00 | $1A, $84, $AD; Gap
	.byte $20 | $15, $8A, $A5; Downward Pipe (CAN'T go down)
	.byte $20 | $19, $84, $60; Note Blocks - movable two directions
	.byte $00 | $12, $8E, $E2; Background Clouds
	.byte $00 | $14, $85, $E2; Background Clouds
	.byte $20 | $15, $91, $A4; Downward Pipe (CAN'T go down)
	.byte $00 | $19, $93, $93; Background Bushes
	.byte $40 | $00, $98, $09; Level Ending
	; Pointer on screen $02
	.byte $E0 | $02, $00 | $02, 212; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_1_W8_objects:
	.byte $A4, $16, $13; Green Venus Fire Trap (upward)
	.byte $A0, $1C, $16; Green Piranha Plant (upward)
	.byte $A4, $20, $13; Green Venus Fire Trap (upward)
	.byte $A0, $24, $12; Green Piranha Plant (upward)
	.byte $6E, $33, $19; Green Koopa Paratroopa (bounces)
	.byte $BC, $37, $16; Bullet Bills
	.byte $BC, $37, $18; Bullet Bills
	.byte $BC, $3C, $14; Bullet Bills
	.byte $BC, $3C, $19; Bullet Bills
	.byte $BC, $4F, $18; Bullet Bills
	.byte $BC, $50, $13; Bullet Bills
	.byte $2F, $51, $12; Boo Buddy
	.byte $6D, $59, $16; Red Koopa Troopa
	.byte $A4, $5F, $14; Green Venus Fire Trap (upward)
	.byte $6E, $6A, $17; Green Koopa Paratroopa (bounces)
	.byte $BC, $6B, $18; Bullet Bills
	.byte $6F, $6E, $14; Red Koopa Paratroopa
	.byte $BC, $72, $13; Bullet Bills
	.byte $BC, $72, $16; Bullet Bills
	.byte $BC, $7A, $15; Bullet Bills
	.byte $BC, $7A, $18; Bullet Bills
	.byte $6C, $7F, $19; Green Koopa Troopa
	.byte $A2, $91, $15; Red Piranha Plant (upward)
	.byte $41, $A8, $15; Goal Card
	.byte $FF
; Dungeon_W8
; Object Set 2
Dungeon_W8_generators:
Dungeon_W8_header:
	.byte $58; Next Level
	.byte LEVEL1_SIZE_15 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $40 | $03; Time | Music
	.byte $60 | $0F, $00, $3B, $EF; Blank Background (used to block out stuff)
	.byte $00 | $0F, $00, $E5, $05; Horizontally oriented X-blocks
	.byte $00 | $15, $00, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $19, $00, $E1, $07; Horizontally oriented X-blocks
	.byte $00 | $0F, $06, $E1, $07; Horizontally oriented X-blocks
	.byte $00 | $15, $08, $E5, $03; Horizontally oriented X-blocks
	.byte $00 | $0F, $0E, $E2, $03; Horizontally oriented X-blocks
	.byte $00 | $1A, $0D, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $0F, $10, $E0, $DF; Horizontally oriented X-blocks
	.byte $00 | $1A, $10, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $12, $11, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $17, $15, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $10, $1D, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $13, $1C, $E0, $00; Horizontally oriented X-blocks
	.byte $20 | $15, $18, $30; Bricks with single coins
	.byte $00 | $16, $11, $02; Rotodisc block
	.byte $00 | $16, $15, $02; Rotodisc block
	.byte $00 | $16, $1C, $02; Rotodisc block
	.byte $00 | $11, $1C, $00; Door
	.byte $00 | $1A, $20, $E0, $03; Horizontally oriented X-blocks
	.byte $00 | $1A, $25, $E0, $0A; Horizontally oriented X-blocks
	.byte $00 | $13, $29, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $13, $2D, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $17, $22, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $10, $28, $E5, $00; Horizontally oriented X-blocks
	.byte $00 | $17, $20, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $17, $23, $E2, $01; Horizontally oriented X-blocks
	.byte $00 | $17, $2C, $E2, $00; Horizontally oriented X-blocks
	.byte $20 | $13, $22, $06; Brick with Flower
	.byte $00 | $16, $28, $02; Rotodisc block
	.byte $00 | $18, $22, $00; Door
	.byte $00 | $11, $29, $00; Door
	.byte $20 | $17, $21, $10; Bricks
	.byte $00 | $1A, $24, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $1A, $30, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $17, $39, $E2, $05; Horizontally oriented X-blocks
	.byte $00 | $10, $39, $E6, $00; Horizontally oriented X-blocks
	.byte $00 | $12, $3C, $E4, $00; Horizontally oriented X-blocks
	.byte $00 | $10, $3D, $E6, $00; Horizontally oriented X-blocks
	.byte $20 | $13, $34, $30; Bricks with single coins
	.byte $20 | $13, $36, $0D; Brick with P-Switch
	.byte $20 | $14, $34, $12; Bricks
	.byte $20 | $14, $35, $30; Bricks with single coins
	.byte $20 | $15, $34, $12; Bricks
	.byte $20 | $16, $34, $12; Bricks
	.byte $20 | $16, $38, $0E; Invisible Coin
	.byte $20 | $12, $3A, $10; Bricks
	.byte $20 | $12, $3B, $0B; Brick with 1-up
	.byte $00 | $15, $35, $00; Door
	.byte $00 | $15, $3B, $00; Door
	.byte $00 | $15, $3E, $00; Door
	.byte $00 | $17, $35, $02; Rotodisc block
	.byte $00 | $1A, $40, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $10, $42, $E4, $00; Horizontally oriented X-blocks
	.byte $00 | $10, $43, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $14, $43, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $10, $4E, $E2, $03; Horizontally oriented X-blocks
	.byte $00 | $18, $42, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $48, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $12, $43, $00; Door
	.byte $00 | $10, $5E, $E0, $61; Horizontally oriented X-blocks
	.byte $00 | $1A, $50, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $10, $54, $E0, $06; Horizontally oriented X-blocks
	.byte $00 | $11, $54, $E0, $05; Horizontally oriented X-blocks
	.byte $00 | $12, $54, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $14, $5D, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $15, $5B, $E1, $04; Horizontally oriented X-blocks
	.byte $00 | $17, $59, $E1, $06; Horizontally oriented X-blocks
	.byte $00 | $19, $57, $E0, $08; Horizontally oriented X-blocks
	.byte $00 | $17, $50, $E0, $03; Horizontally oriented X-blocks
	.byte $00 | $18, $53, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $52, $00; Door
	.byte $20 | $17, $51, $0B; Brick with 1-up
	.byte $00 | $14, $60, $E6, $02; Horizontally oriented X-blocks
	.byte $00 | $11, $63, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $12, $65, $E8, $00; Horizontally oriented X-blocks
	.byte $00 | $14, $63, $E6, $02; Horizontally oriented X-blocks
	.byte $00 | $15, $65, $E5, $01; Horizontally oriented X-blocks
	.byte $00 | $14, $6B, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $15, $67, $E0, $24; Horizontally oriented X-blocks
	.byte $00 | $1A, $69, $E0, $06; Horizontally oriented X-blocks
	.byte $00 | $12, $63, $00; Door
	.byte $00 | $12, $6C, $00; Door
	.byte $20 | $17, $69, $0B; Brick with 1-up
	.byte $20 | $17, $6A, $11; Bricks
	.byte $00 | $1A, $70, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $18, $74, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $75, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $74, $00; Door
	.byte $00 | $18, $7D, $00; Door
	.byte $00 | $12, $70, $62; Dungeon windows
	.byte $20 | $11, $7C, $11; Bricks
	.byte $20 | $12, $7C, $11; Bricks
	.byte $20 | $13, $7C, $11; Bricks
	.byte $20 | $14, $7C, $11; Bricks
	.byte $40 | $14, $76, $08; P-Switch
	.byte $20 | $17, $78, $82; Coins
	.byte $00 | $1A, $80, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $11, $8C, $E0, $0D; Horizontally oriented X-blocks
	.byte $00 | $12, $8C, $E0, $0B; Horizontally oriented X-blocks
	.byte $20 | $11, $82, $11; Bricks
	.byte $20 | $12, $82, $11; Bricks
	.byte $20 | $13, $82, $11; Bricks
	.byte $20 | $14, $82, $11; Bricks
	.byte $20 | $11, $8A, $11; Bricks
	.byte $20 | $12, $8A, $11; Bricks
	.byte $20 | $13, $8A, $11; Bricks
	.byte $20 | $14, $8A, $11; Bricks
	.byte $60 | $15, $8C, $5F; Conveyor Belt - moves left
	.byte $00 | $18, $86, $00; Door
	.byte $20 | $17, $8A, $82; Coins
	.byte $60 | $10, $9A, $30, $01; Blank Background (used to block out stuff)
	.byte $00 | $1A, $9A, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $16, $90, $E3, $05; Horizontally oriented X-blocks
	.byte $00 | $1A, $90, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $11, $9C, $E0, $01; Horizontally oriented X-blocks
	.byte $20 | $13, $90, $11; Bricks
	.byte $20 | $14, $90, $11; Bricks
	.byte $00 | $18, $97, $00; Door
	.byte $20 | $15, $9C, $87; Coins
	.byte $00 | $17, $9E, $62; Dungeon windows
	.byte $00 | $1A, $A0, $E0, $0F; Horizontally oriented X-blocks
	.byte $60 | $15, $A4, $67; Conveyor Belt - moves right
	.byte $00 | $18, $AC, $00; Door
	.byte $20 | $11, $A4, $11; Bricks
	.byte $20 | $12, $A4, $11; Bricks
	.byte $20 | $13, $A4, $11; Bricks
	.byte $20 | $14, $A4, $11; Bricks
	.byte $00 | $11, $AC, $E4, $03; Horizontally oriented X-blocks
	.byte $00 | $15, $A0, $02; Rotodisc block
	.byte $00 | $1A, $B0, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $19, $B0, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $15, $B0, $E0, $0D; Horizontally oriented X-blocks
	.byte $00 | $16, $BA, $E3, $03; Horizontally oriented X-blocks
	.byte $00 | $12, $B7, $61; Dungeon windows
	.byte $00 | $17, $B4, $02; Rotodisc block
	.byte $20 | $15, $B6, $11; Bricks
	.byte $20 | $12, $B1, $07; Brick with Leaf
	.byte $20 | $11, $B3, $10; Bricks
	.byte $20 | $12, $B3, $10; Bricks
	.byte $20 | $13, $B3, $10; Bricks
	.byte $20 | $14, $B3, $10; Bricks
	.byte $60 | $10, $CD, $3A, $22; Blank Background (used to block out stuff)
	.byte $00 | $1A, $C0, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $10, $C5, $E9, $07; Horizontally oriented X-blocks
	.byte $00 | $10, $C0, $E4, $00; Horizontally oriented X-blocks
	.byte $00 | $15, $C0, $E0, $05; Horizontally oriented X-blocks
	.byte $00 | $13, $C4, $00; Door
	.byte $00 | $18, $C3, $00; Door
	.byte $00 | $13, $CE, $00; Door
	.byte $60 | $1A, $CD, $63; Conveyor Belt - moves right
	.byte $20 | $12, $C2, $00; '?' with flower
	.byte $00 | $10, $D1, $E7, $0E; Horizontally oriented X-blocks
	.byte $00 | $18, $D1, $DE; Ceiling Spikes
	.byte $60 | $1A, $D1, $6F; Conveyor Belt - moves right
	.byte $60 | $1A, $E0, $6F; Conveyor Belt - moves right
	.byte $00 | $11, $E1, $63; Dungeon windows
	.byte $00 | $10, $EF, $EA, $00; Horizontally oriented X-blocks
	.byte $FF
Dungeon_W8_objects:
	.byte $5A, $11, $16; Single Rotodisc (rotates clockwise)
	.byte $5F, $1C, $16; Double Rotodisc (rotates both ways, starting at top)
	.byte $60, $28, $16; Double Rotodisc (rotates clockwise)
	.byte $3F, $31, $18; Dry Bones
	.byte $5A, $35, $17; Single Rotodisc (rotates clockwise)
	.byte $8F, $4C, $10; Thwomp (moves diagonally down and left)
	.byte $8B, $50, $18; Thwomp (moves left)
	.byte $8A, $52, $10; Thwomp (normal)
	.byte $8F, $5C, $10; Thwomp (moves diagonally down and left)
	.byte $2F, $83, $17; Boo Buddy
	.byte $3F, $87, $13; Dry Bones
	.byte $8A, $9A, $10; Thwomp (normal)
	.byte $5F, $A0, $15; Double Rotodisc (rotates both ways, starting at top)
	.byte $3F, $A8, $13; Dry Bones
	.byte $08, $AA, $13; Invisible door (appears when you hit a P-switch)
	.byte $5B, $B4, $17; Single Rotodisc (rotates counterclockwise)
	.byte $3F, $B9, $14; Dry Bones
	.byte $4B, $EC, $38; Boom Boom
	.byte $FF
; Pipe_3_End_2_W8
; Object Set 14
Pipe_3_End_2_W8_generators:
Pipe_3_End_2_W8_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_D8 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $40 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $1A, $00, $50, $0F; Hilly Fill
	.byte $80 | $15, $00, $54, $00; Hilly Fill
	.byte $60 | $0F, $00, $E5; Hilly Wall - Right Side
	.byte $80 | $15, $01, $84, $04; Flat Land - Hilly
	.byte $00 | $15, $06, $54; 45 Degree Hill - Down/Right
	.byte $80 | $1A, $0B, $80, $03; Flat Land - Hilly
	.byte $80 | $0F, $0F, $5B, $00; Hilly Fill
	.byte $00 | $14, $0F, $E5; Hilly Wall - Left Side
	.byte $80 | $0F, $0B, $B4, $03; Ceiling - Hilly
	.byte $00 | $0F, $06, $74; 45 Degree Hill - Up/Left
	.byte $80 | $0F, $03, $B0, $03; Ceiling - Hilly
	.byte $00 | $0F, $03, $07; Lower Left Corner - Hilly
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $18, $0D, $91; Downward Pipe (CAN go down)
	.byte $80 | $1A, $0D, $50, $01; Hilly Fill
	.byte $FF
Pipe_3_End_2_W8_objects:
	.byte $25, $02, $10; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_2_W8
; Object Set 14
Level_2_W8_generators:
Level_2_W8_header:
	.byte $59; Next Level
	.byte LEVEL1_SIZE_15 | LEVEL1_YSTART_070; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_03; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $13; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $A0 | $1A, $00, $1F; Background like at bottom of hilly level
	.byte $A0 | $1A, $10, $1F; Background like at bottom of hilly level
	.byte $A0 | $1A, $20, $1F; Background like at bottom of hilly level
	.byte $80 | $09, $00, $8F, $07; Flat Land - Hilly
	.byte $80 | $19, $00, $50, $07; Hilly Fill
	.byte $80 | $0B, $08, $57, $1F; Hilly Fill
	.byte $00 | $09, $08, $51; 45 Degree Hill - Down/Right
	.byte $80 | $0B, $0A, $80, $05; Flat Land - Hilly
	.byte $60 | $13, $07, $E6; Hilly Wall - Right Side
	.byte $40 | $08, $0B, $0B; Background Hills B
	.byte $20 | $13, $08, $4F; Wooden blocks
	.byte $20 | $14, $08, $40; Wooden blocks
	.byte $20 | $15, $08, $40; Wooden blocks
	.byte $20 | $16, $08, $40; Wooden blocks
	.byte $20 | $17, $08, $40; Wooden blocks
	.byte $20 | $18, $08, $40; Wooden blocks
	.byte $20 | $19, $08, $40; Wooden blocks
	.byte $20 | $1A, $08, $4F; Wooden blocks
	.byte $20 | $18, $0B, $91; Downward Pipe (CAN go down)
	.byte $A0 | $04, $06, $32; Background Clouds
	.byte $A0 | $07, $0E, $32; Background Clouds
	.byte $80 | $08, $13, $82, $02; Flat Land - Hilly
	.byte $00 | $08, $12, $62; 45 Degree Hill - Down/Left
	.byte $00 | $08, $16, $52; 45 Degree Hill - Down/Right
	.byte $60 | $0A, $17, $E7; Hilly Wall - Right Side
	.byte $00 | $12, $17, $0A; Lower Right Hill Corner
	.byte $00 | $08, $1B, $62; 45 Degree Hill - Down/Left
	.byte $80 | $08, $1C, $82, $09; Flat Land - Hilly
	.byte $00 | $0A, $1A, $E7; Hilly Wall - Left Side
	.byte $00 | $12, $1A, $07; Lower Left Corner - Hilly
	.byte $80 | $07, $1D, $D2; Small Background Hills
	.byte $20 | $13, $1A, $4D; Wooden blocks
	.byte $40 | $0A, $18, $D9, $01; Normal Quicksand
	.byte $20 | $1A, $18, $4F; Wooden blocks
	.byte $A0 | $03, $18, $32; Background Clouds
	.byte $00 | $08, $25, $51; 45 Degree Hill - Down/Right
	.byte $80 | $09, $26, $81, $01; Flat Land - Hilly
	.byte $00 | $09, $27, $50; 45 Degree Hill - Down/Right
	.byte $80 | $0A, $28, $8F, $01; Flat Land - Hilly
	.byte $00 | $0A, $29, $50; 45 Degree Hill - Down/Right
	.byte $80 | $0B, $2A, $8E, $08; Flat Land - Hilly
	.byte $00 | $13, $28, $E6; Hilly Wall - Left Side
	.byte $40 | $05, $20, $0B; Background Hills B
	.byte $40 | $07, $2B, $0A; Background Hills A
	.byte $20 | $18, $24, $91; Downward Pipe (CAN go down)
	.byte $20 | $14, $27, $40; Wooden blocks
	.byte $20 | $15, $27, $40; Wooden blocks
	.byte $20 | $16, $27, $40; Wooden blocks
	.byte $20 | $17, $27, $40; Wooden blocks
	.byte $20 | $18, $27, $40; Wooden blocks
	.byte $20 | $19, $27, $40; Wooden blocks
	.byte $40 | $08, $2F, $0B; Background Hills B
	.byte $A0 | $07, $28, $32; Background Clouds
	.byte $A0 | $1A, $30, $1F; Background like at bottom of hilly level
	.byte $80 | $0B, $33, $5E, $06; Hilly Fill
	.byte $00 | $07, $36, $63; 45 Degree Hill - Down/Left
	.byte $80 | $07, $37, $83, $00; Flat Land - Hilly
	.byte $00 | $07, $38, $51; 45 Degree Hill - Down/Right
	.byte $80 | $09, $38, $51, $01; Hilly Fill
	.byte $60 | $09, $39, $E4; Hilly Wall - Right Side
	.byte $80 | $0E, $3A, $8B, $0D; Flat Land - Hilly
	.byte $80 | $08, $3C, $8F, $03; Flat Land - Hilly
	.byte $00 | $08, $3F, $50; 45 Degree Hill - Down/Right
	.byte $80 | $18, $3C, $51, $03; Hilly Fill
	.byte $00 | $08, $3C, $60; 45 Degree Hill - Down/Left
	.byte $00 | $09, $3C, $E4; Hilly Wall - Left Side
	.byte $60 | $09, $3F, $E4; Hilly Wall - Right Side
	.byte $00 | $19, $65, $04; Upper Right Hill Corner - Hilly
	.byte $40 | $0A, $3A, $D1, $01; Normal Quicksand
	.byte $20 | $0C, $3A, $A1; Downward Pipe (CAN'T go down)
	.byte $A0 | $03, $32, $32; Background Clouds
	.byte $A0 | $04, $3A, $32; Background Clouds
	.byte $A0 | $1A, $40, $1F; Background like at bottom of hilly level
	.byte $80 | $08, $42, $8F, $03; Flat Land - Hilly
	.byte $00 | $08, $42, $60; 45 Degree Hill - Down/Left
	.byte $00 | $08, $45, $50; 45 Degree Hill - Down/Right
	.byte $00 | $09, $42, $E4; Hilly Wall - Left Side
	.byte $60 | $09, $45, $E4; Hilly Wall - Right Side
	.byte $80 | $09, $48, $5F, $06; Hilly Fill
	.byte $80 | $19, $48, $51, $06; Hilly Fill
	.byte $80 | $0B, $4F, $5E, $03; Hilly Fill
	.byte $80 | $07, $4A, $82, $01; Flat Land - Hilly
	.byte $00 | $07, $49, $61; 45 Degree Hill - Down/Left
	.byte $00 | $07, $4C, $53; 45 Degree Hill - Down/Right
	.byte $40 | $0A, $40, $D1, $01; Normal Quicksand
	.byte $40 | $0A, $46, $D1, $01; Normal Quicksand
	.byte $00 | $09, $48, $E4; Hilly Wall - Left Side
	.byte $20 | $0C, $40, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $0C, $46, $A1; Downward Pipe (CAN'T go down)
	.byte $80 | $06, $4A, $D1; Small Background Hills
	.byte $A0 | $03, $42, $32; Background Clouds
	.byte $A0 | $1A, $50, $1F; Background like at bottom of hilly level
	.byte $00 | $0B, $52, $53; 45 Degree Hill - Down/Right
	.byte $80 | $0F, $52, $5A, $05; Hilly Fill
	.byte $80 | $13, $58, $56, $05; Hilly Fill
	.byte $00 | $0F, $58, $53; 45 Degree Hill - Down/Right
	.byte $00 | $13, $5E, $56; 45 Degree Hill - Down/Right
	.byte $20 | $0B, $50, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $0F, $56, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $13, $5C, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $09, $54, $0D; Brick with P-Switch
	.byte $A0 | $0A, $58, $32; Background Clouds
	.byte $A0 | $07, $5C, $32; Background Clouds
	.byte $A0 | $1A, $60, $1E; Background like at bottom of hilly level
	.byte $60 | $18, $63, $50; 30 Degree Hill - Down/Right
	.byte $80 | $19, $64, $50, $01; Hilly Fill
	.byte $80 | $19, $65, $80, $08; Flat Land - Hilly
	.byte $00 | $19, $6E, $04; Upper Right Hill Corner - Hilly
	.byte $A0 | $0B, $66, $32; Background Clouds
	.byte $A0 | $0F, $6C, $32; Background Clouds
	.byte $A0 | $11, $62, $32; Background Clouds
	.byte $20 | $16, $68, $80; Coins
	.byte $20 | $14, $6B, $80; Coins
	.byte $20 | $13, $6E, $80; Coins
	.byte $20 | $15, $71, $60; Note Blocks - movable two directions
	.byte $20 | $17, $74, $60; Note Blocks - movable two directions
	.byte $20 | $15, $77, $60; Note Blocks - movable two directions
	.byte $20 | $13, $7A, $60; Note Blocks - movable two directions
	.byte $20 | $17, $7A, $60; Note Blocks - movable two directions
	.byte $20 | $15, $7D, $60; Note Blocks - movable two directions
	.byte $20 | $11, $71, $80; Coins
	.byte $20 | $13, $74, $80; Coins
	.byte $20 | $11, $77, $80; Coins
	.byte $20 | $0F, $7A, $80; Coins
	.byte $20 | $11, $7D, $80; Coins
	.byte $A0 | $07, $7C, $32; Background Clouds
	.byte $A0 | $0C, $74, $32; Background Clouds
	.byte $A0 | $0D, $7C, $32; Background Clouds
	.byte $A0 | $18, $72, $32; Background Clouds
	.byte $A0 | $1A, $84, $1B; Background like at bottom of hilly level
	.byte $80 | $19, $84, $80, $3B; Flat Land - Hilly
	.byte $00 | $19, $84, $01; Upper Left Hill Corner - Hilly
	.byte $80 | $19, $87, $50, $30; Hilly Fill
	.byte $00 | $13, $8C, $65; 45 Degree Hill - Down/Left
	.byte $80 | $13, $8D, $55, $22; Hilly Fill
	.byte $20 | $13, $8D, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $12, $80, $60; Note Blocks - movable two directions
	.byte $20 | $0F, $80, $80; Coins
	.byte $A0 | $0C, $84, $32; Background Clouds
	.byte $A0 | $0D, $8A, $32; Background Clouds
	.byte $A0 | $12, $86, $32; Background Clouds
	.byte $A0 | $16, $82, $32; Background Clouds
	.byte $A0 | $1A, $90, $1F; Background like at bottom of hilly level
	.byte $00 | $0F, $92, $63; 45 Degree Hill - Down/Left
	.byte $80 | $0F, $93, $53, $1A; Hilly Fill
	.byte $00 | $0B, $98, $63; 45 Degree Hill - Down/Left
	.byte $80 | $0B, $99, $53, $10; Hilly Fill
	.byte $00 | $07, $9E, $63; 45 Degree Hill - Down/Left
	.byte $80 | $06, $9F, $84, $06; Flat Land - Hilly
	.byte $60 | $06, $9F, $60; 30 Degree Hill - Down/Left
	.byte $20 | $0B, $99, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $0F, $93, $A1; Downward Pipe (CAN'T go down)
	.byte $A0 | $05, $9A, $32; Background Clouds
	.byte $A0 | $0A, $92, $32; Background Clouds
	.byte $A0 | $1A, $A0, $1F; Background like at bottom of hilly level
	.byte $60 | $06, $A4, $50; 30 Degree Hill - Down/Right
	.byte $00 | $07, $A6, $5F; 45 Degree Hill - Down/Right
	.byte $20 | $03, $A1, $82; Coins
	.byte $A0 | $08, $AC, $32; Background Clouds
	.byte $A0 | $1A, $B0, $1F; Background like at bottom of hilly level
	.byte $00 | $11, $B0, $57; 45 Degree Hill - Down/Right
	.byte $40 | $11, $B8, $0C; Background Hills C
	.byte $00 | $19, $BF, $04; Upper Right Hill Corner - Hilly
	.byte $A0 | $0C, $B8, $32; Background Clouds
	.byte $A0 | $0D, $B2, $32; Background Clouds
	.byte $A0 | $13, $B4, $32; Background Clouds
	.byte $A0 | $13, $C6, $32; Background Clouds
	.byte $A0 | $16, $CC, $32; Background Clouds
	.byte $20 | $19, $C6, $60; Note Blocks - movable two directions
	.byte $20 | $19, $CB, $60; Note Blocks - movable two directions
	.byte $80 | $1A, $D0, $80, $1F; Flat Land - Hilly
	.byte $00 | $1A, $D0, $01; Upper Left Hill Corner - Hilly
	.byte $40 | $17, $D4, $0B; Background Hills B
	.byte $80 | $19, $D8, $D1; Small Background Hills
	.byte $A0 | $12, $D7, $32; Background Clouds
	.byte $40 | $00, $DB, $09; Level Ending
	; Pointer on screen $00
	.byte $E0 | $00, $00 | $02, 32; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $02
	.byte $E0 | $02, $00 | $02, 18; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_2_W8_objects:
	.byte $AF, $02, $11; The Angry Sun
	.byte $74, $2E, $05; Para-Goomba with Micro-Goombas
	.byte $A6, $3A, $0A; Red Venus Fire Trap (upward)
	.byte $A6, $40, $0A; Red Venus Fire Trap (upward)
	.byte $A6, $46, $0A; Red Venus Fire Trap (upward)
	.byte $A6, $50, $0B; Red Venus Fire Trap (upward)
	.byte $A6, $56, $0F; Red Venus Fire Trap (upward)
	.byte $A6, $5C, $13; Red Venus Fire Trap (upward)
	.byte $A6, $8D, $13; Red Venus Fire Trap (upward)
	.byte $BB, $92, $01; Stops infinite flying or spiny Cheep-Cheeps
	.byte $A6, $93, $0F; Red Venus Fire Trap (upward)
	.byte $A6, $99, $0B; Red Venus Fire Trap (upward)
	.byte $80, $C1, $19; Green Koopa Paratroopa (doesn't bounce)
	.byte $41, $E8, $15; Goal Card
	.byte $FF
; Default_Level_298
; Object Set 14
Default_Level_298_generators:
Default_Level_298_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_0F0; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $60 | $0F, $00, $E4; Hilly Wall - Right Side
	.byte $80 | $14, $00, $56, $00; Hilly Fill
	.byte $80 | $14, $01, $86, $01; Flat Land - Hilly
	.byte $00 | $14, $02, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $15, $02, $E0; Hilly Wall - Right Side
	.byte $00 | $16, $03, $54; 45 Degree Hill - Down/Right
	.byte $00 | $16, $0C, $64; 45 Degree Hill - Down/Left
	.byte $80 | $19, $06, $81, $03; Flat Land - Hilly
	.byte $80 | $14, $0D, $86, $01; Flat Land - Hilly
	.byte $00 | $14, $0D, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $15, $0D, $E0; Hilly Wall - Left Side
	.byte $80 | $14, $0F, $56, $00; Hilly Fill
	.byte $00 | $0F, $0F, $E4; Hilly Wall - Left Side
	.byte $80 | $0F, $03, $B1, $09; Ceiling - Hilly
	.byte $00 | $0F, $03, $E0; Hilly Wall - Left Side
	.byte $60 | $0F, $0C, $E0; Hilly Wall - Right Side
	.byte $00 | $10, $03, $07; Lower Left Corner - Hilly
	.byte $00 | $10, $0C, $0A; Lower Right Hill Corner
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $0F, $0D, $C1; Upward Pipe (CAN go up)
	.byte $FF
Default_Level_298_objects:
	.byte $25, $02, $11; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Default_Level_299
; Object Set 14
Default_Level_299_generators:
Default_Level_299_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_0F0; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_D8 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $60 | $0F, $00, $E4; Hilly Wall - Right Side
	.byte $80 | $14, $00, $56, $00; Hilly Fill
	.byte $80 | $14, $01, $86, $01; Flat Land - Hilly
	.byte $00 | $14, $02, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $15, $02, $E0; Hilly Wall - Right Side
	.byte $00 | $16, $03, $54; 45 Degree Hill - Down/Right
	.byte $00 | $16, $0C, $64; 45 Degree Hill - Down/Left
	.byte $80 | $19, $06, $81, $03; Flat Land - Hilly
	.byte $80 | $14, $0D, $86, $01; Flat Land - Hilly
	.byte $00 | $14, $0D, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $15, $0D, $E0; Hilly Wall - Left Side
	.byte $80 | $14, $0F, $56, $00; Hilly Fill
	.byte $00 | $0F, $0F, $E4; Hilly Wall - Left Side
	.byte $80 | $0F, $03, $B1, $09; Ceiling - Hilly
	.byte $00 | $0F, $03, $E0; Hilly Wall - Left Side
	.byte $60 | $0F, $0C, $E0; Hilly Wall - Right Side
	.byte $00 | $10, $03, $07; Lower Left Corner - Hilly
	.byte $00 | $10, $0C, $0A; Lower Right Hill Corner
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $0F, $0D, $C1; Upward Pipe (CAN go up)
	.byte $FF
Default_Level_299_objects:
	.byte $25, $02, $11; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Pipe_6_End_2_W8
; Object Set 14
Pipe_6_End_2_W8_generators:
Pipe_6_End_2_W8_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_D8 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $40 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $1A, $00, $50, $0F; Hilly Fill
	.byte $80 | $15, $00, $54, $00; Hilly Fill
	.byte $60 | $0F, $00, $E5; Hilly Wall - Right Side
	.byte $80 | $15, $01, $84, $04; Flat Land - Hilly
	.byte $00 | $15, $06, $54; 45 Degree Hill - Down/Right
	.byte $80 | $1A, $0B, $80, $03; Flat Land - Hilly
	.byte $80 | $0F, $0F, $5B, $00; Hilly Fill
	.byte $00 | $14, $0F, $E5; Hilly Wall - Left Side
	.byte $80 | $0F, $0B, $B4, $03; Ceiling - Hilly
	.byte $00 | $0F, $06, $74; 45 Degree Hill - Up/Left
	.byte $80 | $0F, $03, $B0, $03; Ceiling - Hilly
	.byte $00 | $0F, $03, $07; Lower Left Corner - Hilly
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $18, $0D, $91; Downward Pipe (CAN go down)
	.byte $80 | $1A, $0D, $50, $01; Hilly Fill
	.byte $FF
Pipe_6_End_2_W8_objects:
	.byte $25, $02, $0E; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Tank__2_W8
; Object Set 10
Tank__2_W8_generators:
Tank__2_W8_header:
	.byte $5A; Next Level
	.byte LEVEL1_SIZE_09 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_06; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $15; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $60 | $19, $00, $3F; Ground (like on tank levels)
	.byte $60 | $19, $10, $3F; Ground (like on tank levels)
	.byte $60 | $19, $20, $3F; Ground (like on tank levels)
	.byte $60 | $19, $30, $3F; Ground (like on tank levels)
	.byte $60 | $19, $40, $3F; Ground (like on tank levels)
	.byte $60 | $19, $50, $3F; Ground (like on tank levels)
	.byte $60 | $19, $60, $3F; Ground (like on tank levels)
	.byte $60 | $19, $70, $3F; Ground (like on tank levels)
	.byte $60 | $19, $80, $3F; Ground (like on tank levels)
	.byte $40 | $14, $0D, $0C; Tank A
	.byte $60 | $17, $0D, $C1; Invisible Platform
	.byte $60 | $0F, $14, $70, $10; Wooden Tank Beam
	.byte $60 | $10, $16, $70, $0D; Wooden Tank Beam
	.byte $40 | $10, $16, $0A; Wooden ship beam terminus B
	.byte $60 | $17, $16, $70, $19; Wooden Tank Beam
	.byte $60 | $18, $18, $B2; Tank Wheels
	.byte $60 | $18, $1E, $BF; Tank Wheels
	.byte $00 | $16, $1C, $06; Bullet Shooter - Up/Left
	.byte $00 | $10, $15, $08; Bullet Shooter - Down/Left
	.byte $00 | $16, $1A, $06; Bullet Shooter - Up/Left
	.byte $00 | $16, $1B, $06; Bullet Shooter - Up/Left
	.byte $60 | $18, $16, $C0; Invisible Platform
	.byte $60 | $0F, $2E, $70, $0C; Wooden Tank Beam
	.byte $60 | $15, $2C, $A1; Leftward Bullet Shooter
	.byte $60 | $16, $2B, $A1; Leftward Bullet Shooter
	.byte $00 | $15, $2D, $11; Wooden Ship Beam
	.byte $00 | $16, $2C, $12; Wooden Ship Beam
	.byte $00 | $11, $21, $09; Bullet Shooter - Down/Right
	.byte $00 | $16, $23, $07; Bullet Shooter - Up/Right
	.byte $60 | $17, $33, $70, $1C; Wooden Tank Beam
	.byte $60 | $18, $34, $B5; Tank Wheels
	.byte $60 | $18, $3B, $B4; Tank Wheels
	.byte $00 | $10, $34, $09; Bullet Shooter - Down/Right
	.byte $60 | $16, $35, $00; Rocky Wrench hole
	.byte $60 | $16, $39, $00; Rocky Wrench hole
	.byte $60 | $16, $3D, $00; Rocky Wrench hole
	.byte $60 | $18, $33, $C0; Invisible Platform
	.byte $60 | $0F, $4F, $70, $0F; Wooden Tank Beam
	.byte $60 | $16, $41, $00; Rocky Wrench hole
	.byte $60 | $16, $45, $00; Rocky Wrench hole
	.byte $60 | $16, $49, $00; Rocky Wrench hole
	.byte $60 | $16, $4D, $00; Rocky Wrench hole
	.byte $60 | $18, $46, $B8; Tank Wheels
	.byte $60 | $10, $50, $70, $0D; Wooden Tank Beam
	.byte $40 | $10, $50, $0A; Wooden ship beam terminus B
	.byte $00 | $11, $53, $09; Bullet Shooter - Down/Right
	.byte $00 | $11, $58, $08; Bullet Shooter - Down/Left
	.byte $00 | $11, $5A, $09; Bullet Shooter - Down/Right
	.byte $60 | $17, $5C, $70, $25; Wooden Tank Beam
	.byte $60 | $18, $5E, $B5; Tank Wheels
	.byte $60 | $18, $5C, $C0; Invisible Platform
	.byte $00 | $16, $61, $06; Bullet Shooter - Up/Left
	.byte $00 | $16, $67, $06; Bullet Shooter - Up/Left
	.byte $00 | $16, $68, $07; Bullet Shooter - Up/Right
	.byte $00 | $16, $6D, $07; Bullet Shooter - Up/Right
	.byte $60 | $18, $66, $BF; Tank Wheels
	.byte $00 | $13, $7B, $13; Wooden Ship Beam
	.byte $60 | $14, $7B, $70, $03; Wooden Tank Beam
	.byte $00 | $15, $7A, $14; Wooden Ship Beam
	.byte $60 | $16, $7A, $70, $04; Wooden Tank Beam
	.byte $60 | $18, $77, $B9; Tank Wheels
	.byte $60 | $12, $7D, $00; Rocky Wrench hole
	.byte $60 | $13, $79, $A1; Leftward Bullet Shooter
	.byte $60 | $15, $76, $A3; Leftward Bullet Shooter
	.byte $00 | $16, $73, $06; Bullet Shooter - Up/Left
	.byte $60 | $14, $79, $C0; Invisible Platform
	.byte $60 | $16, $76, $C0; Invisible Platform
	.byte $00 | $14, $83, $16; Wooden Ship Beam
	.byte $00 | $15, $83, $17; Wooden Ship Beam
	.byte $00 | $16, $83, $17; Wooden Ship Beam
	.byte $00 | $17, $83, $17; Wooden Ship Beam
	.byte $60 | $18, $83, $B7; Tank Wheels
	.byte $40 | $14, $83, $0F; Left terminus of wooden tank beam
	.byte $20 | $12, $86, $91; Downward Pipe (CAN go down)
	; Pointer on screen $08
	.byte $E0 | $08, $40 | $02, 16; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Tank__2_W8_objects:
	.byte $D3, $00, $14; Autoscrolling
	.byte $C2, $0D, $16; Bullet Shots (leftward)
	.byte $C6, $15, $10; Bullet Shots (down/left)
	.byte $C4, $1A, $16; Bullet Shots (up/left)
	.byte $C4, $1B, $16; Bullet Shots (up/left)
	.byte $C4, $1C, $16; Bullet Shots (up/left)
	.byte $C7, $21, $11; Bullet Shots (down/right)
	.byte $CF, $23, $16; Infinite Bob-Ombs (rightward) (use with bullet shooters)
	.byte $C2, $2B, $16; Bullet Shots (leftward)
	.byte $C2, $2C, $15; Bullet Shots (leftward)
	.byte $C7, $34, $10; Bullet Shots (down/right)
	.byte $AD, $35, $17; Brown Rocky Wrench
	.byte $AD, $3D, $17; Brown Rocky Wrench
	.byte $AD, $41, $17; Brown Rocky Wrench
	.byte $AD, $49, $17; Brown Rocky Wrench
	.byte $AD, $4D, $17; Brown Rocky Wrench
	.byte $C7, $53, $11; Bullet Shots (down/right)
	.byte $C6, $58, $11; Bullet Shots (down/left)
	.byte $C7, $5A, $11; Bullet Shots (down/right)
	.byte $C4, $61, $16; Bullet Shots (up/left)
	.byte $C4, $67, $16; Bullet Shots (up/left)
	.byte $C5, $68, $16; Bullet Shots (up/right)
	.byte $CF, $6D, $16; Infinite Bob-Ombs (rightward) (use with bullet shooters)
	.byte $C4, $73, $16; Bullet Shots (up/left)
	.byte $C2, $76, $15; Bullet Shots (leftward)
	.byte $C2, $79, $13; Bullet Shots (leftward)
	.byte $AD, $7D, $13; Brown Rocky Wrench
	.byte $FF
; Bowser's_Castle_W8
; Object Set 2
Bowser's_Castle_W8_generators:
Bowser's_Castle_W8_header:
	.byte $5B; Next Level
	.byte LEVEL1_SIZE_15 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $40 | $03; Time | Music
	.byte $60 | $00, $00, $3F, $EF; Blank Background (used to block out stuff)
	.byte $60 | $10, $00, $38, $41; Blank Background (used to block out stuff)
	.byte $60 | $10, $42, $3A, $7D; Blank Background (used to block out stuff)
	.byte $60 | $10, $C0, $38, $2F; Blank Background (used to block out stuff)
	.byte $60 | $00, $00, $DC, $2F; Red Bricks - found in Bowser's Castle
	.byte $60 | $0D, $00, $D7, $11; Red Bricks - found in Bowser's Castle
	.byte $00 | $16, $04, $63; Dungeon windows
	.byte $00 | $10, $16, $64; Dungeon windows
	.byte $00 | $16, $18, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $1D, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $14, $18, $05; Bowser Statue
	.byte $00 | $14, $1D, $05; Bowser Statue
	.byte $60 | $11, $2B, $D7, $0C; Red Bricks - found in Bowser's Castle
	.byte $60 | $12, $2A, $D6, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $13, $29, $D5, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $14, $28, $D4, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $15, $27, $D3, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $16, $26, $D2, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $17, $25, $D1, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $18, $24, $D0, $00; Red Bricks - found in Bowser's Castle
	.byte $00 | $0E, $2B, $61; Dungeon windows
	.byte $00 | $16, $22, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $14, $22, $05; Bowser Statue
	.byte $60 | $00, $30, $D0, $04; Red Bricks - found in Bowser's Castle
	.byte $60 | $00, $35, $D1, $0D; Red Bricks - found in Bowser's Castle
	.byte $60 | $04, $34, $D9, $0D; Red Bricks - found in Bowser's Castle
	.byte $60 | $0E, $3A, $D2, $07; Red Bricks - found in Bowser's Castle
	.byte $60 | $11, $38, $D9, $09; Red Bricks - found in Bowser's Castle
	.byte $00 | $0F, $38, $00; Door
	.byte $60 | $00, $43, $DF, $0D; Red Bricks - found in Bowser's Castle
	.byte $60 | $10, $43, $D4, $0D; Red Bricks - found in Bowser's Castle
	.byte $60 | $19, $43, $D1, $21; Red Bricks - found in Bowser's Castle
	.byte $60 | $04, $42, $E0; Donut Blocks
	.byte $00 | $16, $4E, $04; Hot Foot Candle
	.byte $60 | $00, $51, $D2, $08; Red Bricks - found in Bowser's Castle
	.byte $60 | $03, $51, $D1, $07; Red Bricks - found in Bowser's Castle
	.byte $60 | $05, $51, $D1, $06; Red Bricks - found in Bowser's Castle
	.byte $60 | $07, $51, $D1, $05; Red Bricks - found in Bowser's Castle
	.byte $60 | $09, $51, $D1, $04; Red Bricks - found in Bowser's Castle
	.byte $60 | $0B, $51, $D1, $03; Red Bricks - found in Bowser's Castle
	.byte $60 | $0D, $51, $D1, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $0F, $51, $D1, $01; Red Bricks - found in Bowser's Castle
	.byte $60 | $11, $51, $D1, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $03, $5C, $D1, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $05, $5B, $D1, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $07, $5A, $D1, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $09, $59, $D1, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $0B, $58, $D1, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $0D, $57, $D1, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $0F, $56, $D1, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $11, $55, $D1, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $13, $54, $D1, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $15, $53, $D1, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $17, $52, $D1, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $09, $5F, $D1, $04; Red Bricks - found in Bowser's Castle
	.byte $60 | $0B, $5E, $D1, $05; Red Bricks - found in Bowser's Castle
	.byte $60 | $0D, $5D, $D1, $06; Red Bricks - found in Bowser's Castle
	.byte $60 | $0F, $5C, $D1, $07; Red Bricks - found in Bowser's Castle
	.byte $60 | $11, $5B, $D1, $08; Red Bricks - found in Bowser's Castle
	.byte $60 | $13, $5A, $D1, $09; Red Bricks - found in Bowser's Castle
	.byte $60 | $15, $59, $D1, $0A; Red Bricks - found in Bowser's Castle
	.byte $60 | $00, $5A, $D0, $35; Red Bricks - found in Bowser's Castle
	.byte $00 | $07, $5B, $02; Rotodisc block
	.byte $00 | $0D, $58, $02; Rotodisc block
	.byte $00 | $13, $55, $02; Rotodisc block
	.byte $60 | $01, $62, $D3, $01; Red Bricks - found in Bowser's Castle
	.byte $60 | $05, $61, $D1, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $07, $60, $D1, $03; Red Bricks - found in Bowser's Castle
	.byte $60 | $1A, $65, $40, $2A; Lava
	.byte $00 | $04, $6B, $60; Dungeon windows
	.byte $00 | $0B, $69, $61; Dungeon windows
	.byte $00 | $10, $66, $70; Long dungeon windows
	.byte $60 | $08, $6C, $E1; Donut Blocks
	.byte $60 | $0C, $65, $E2; Donut Blocks
	.byte $60 | $0F, $69, $E0; Donut Blocks
	.byte $60 | $13, $6C, $E1; Donut Blocks
	.byte $60 | $17, $67, $E2; Donut Blocks
	.byte $20 | $02, $61, $0F; Invisible 1-up
	.byte $00 | $04, $76, $60; Dungeon windows
	.byte $00 | $0B, $74, $61; Dungeon windows
	.byte $00 | $10, $70, $70; Long dungeon windows
	.byte $00 | $10, $7B, $70; Long dungeon windows
	.byte $60 | $05, $70, $E1; Donut Blocks
	.byte $60 | $07, $78, $E0; Donut Blocks
	.byte $60 | $07, $7C, $E0; Donut Blocks
	.byte $60 | $08, $74, $E0; Donut Blocks
	.byte $60 | $0C, $72, $E0; Donut Blocks
	.byte $60 | $0C, $7D, $E1; Donut Blocks
	.byte $60 | $11, $76, $E3; Donut Blocks
	.byte $60 | $15, $72, $E1; Donut Blocks
	.byte $60 | $15, $7C, $E1; Donut Blocks
	.byte $60 | $04, $84, $D1, $0B; Red Bricks - found in Bowser's Castle
	.byte $60 | $0A, $84, $D2, $08; Red Bricks - found in Bowser's Castle
	.byte $60 | $0A, $8E, $D2, $05; Red Bricks - found in Bowser's Castle
	.byte $60 | $11, $84, $D2, $13; Red Bricks - found in Bowser's Castle
	.byte $60 | $17, $85, $D1, $0A; Red Bricks - found in Bowser's Castle
	.byte $60 | $18, $84, $D0, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $04, $80, $E0; Donut Blocks
	.byte $60 | $0D, $81, $E0; Donut Blocks
	.byte $60 | $15, $82, $E0; Donut Blocks
	.byte $60 | $0A, $8D, $E0; Donut Blocks
	.byte $00 | $12, $89, $02; Rotodisc block
	.byte $00 | $02, $8E, $00; Door
	.byte $60 | $00, $90, $D5, $2F; Red Bricks - found in Bowser's Castle
	.byte $60 | $06, $94, $D6, $2B; Red Bricks - found in Bowser's Castle
	.byte $60 | $0D, $9A, $D1, $25; Red Bricks - found in Bowser's Castle
	.byte $60 | $0F, $9C, $D2, $03; Red Bricks - found in Bowser's Castle
	.byte $60 | $11, $99, $D3, $06; Red Bricks - found in Bowser's Castle
	.byte $60 | $19, $99, $D1, $07; Red Bricks - found in Bowser's Castle
	.byte $60 | $10, $93, $D0, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $14, $93, $D2, $04; Red Bricks - found in Bowser's Castle
	.byte $60 | $17, $90, $D3, $07; Red Bricks - found in Bowser's Castle
	.byte $60 | $11, $98, $E0; Donut Blocks
	.byte $20 | $07, $92, $01; '?' with leaf
	.byte $00 | $15, $91, $00; Door
	.byte $60 | $1A, $A1, $40, $0F; Lava
	.byte $60 | $00, $A0, $DF, $1F; Red Bricks - found in Bowser's Castle
	.byte $60 | $19, $A3, $D1, $01; Red Bricks - found in Bowser's Castle
	.byte $60 | $19, $A8, $D1, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $18, $AC, $D2, $01; Red Bricks - found in Bowser's Castle
	.byte $00 | $18, $A8, $02; Rotodisc block
	.byte $60 | $10, $B2, $D2, $0D; Red Bricks - found in Bowser's Castle
	.byte $60 | $13, $B6, $D3, $09; Red Bricks - found in Bowser's Castle
	.byte $60 | $17, $B1, $D3, $0E; Red Bricks - found in Bowser's Castle
	.byte $00 | $15, $B4, $00; Door
	.byte $00 | $17, $C0, $E3, $01; Horizontally oriented X-blocks
	.byte $00 | $18, $C2, $E2, $2D; Horizontally oriented X-blocks
	.byte $00 | $17, $CD, $E3, $14; Horizontally oriented X-blocks
	.byte $00 | $14, $CE, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $15, $CE, $07; The Princess's Door
	.byte $60 | $18, $C2, $D0, $0A; Red Bricks - found in Bowser's Castle
	.byte $60 | $19, $C4, $D0, $07; Red Bricks - found in Bowser's Castle
	.byte $60 | $1A, $C6, $D0, $03; Red Bricks - found in Bowser's Castle
	.byte $60 | $00, $D0, $DF, $0F; Red Bricks - found in Bowser's Castle
	.byte $60 | $10, $D0, $D6, $0F; Red Bricks - found in Bowser's Castle
	.byte $00 | $14, $EE, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $17, $ED, $E3, $02; Horizontally oriented X-blocks
	.byte $60 | $17, $E2, $D1, $0A; Red Bricks - found in Bowser's Castle
	.byte $60 | $19, $E4, $D0, $06; Red Bricks - found in Bowser's Castle
	.byte $40 | $1A, $E4, $56; Silver Coins (appear when you hit a P-Switch)
	.byte $00 | $15, $EE, $07; The Princess's Door
	; Pointer on screen $03
	.byte $E0 | $03, $40 | $08, 33; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $08
	.byte $E0 | $08, $60 | $08, 99; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $09
	.byte $E0 | $09, $60 | $08, 50; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $0B
	.byte $E0 | $0B, $60 | $08, 105; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Bowser's_Castle_W8_objects:
	.byte $D0, $18, $14; Lasers (use with Bowser statues)
	.byte $D0, $1D, $14; Lasers (use with Bowser statues)
	.byte $D0, $22, $14; Lasers (use with Bowser statues)
	.byte $2E, $31, $10; Upward-moving Circle Block platform
	.byte $30, $4E, $15; Hot Foot
	.byte $5A, $55, $13; Single Rotodisc (rotates clockwise)
	.byte $5A, $58, $0D; Single Rotodisc (rotates clockwise)
	.byte $5A, $5B, $07; Single Rotodisc (rotates clockwise)
	.byte $9E, $6A, $09; Podoboo (comes out of lava)
	.byte $9E, $6E, $09; Podoboo (comes out of lava)
	.byte $9E, $74, $09; Podoboo (comes out of lava)
	.byte $9E, $7A, $09; Podoboo (comes out of lava)
	.byte $51, $89, $12; Double Rotodisc (rotates counterclockwise)
	.byte $8B, $9A, $0F; Thwomp (moves left)
	.byte $9E, $A1, $13; Podoboo (comes out of lava)
	.byte $5A, $A8, $18; Single Rotodisc (rotates clockwise)
	.byte $9E, $AA, $13; Podoboo (comes out of lava)
	.byte $9E, $AF, $13; Podoboo (comes out of lava)
	.byte $18, $CC, $0B; Bowser
	.byte $18, $EC, $0B; Bowser
	.byte $FF
; Default_Level_305_213
; Object Set 1
Default_Level_305_213_generators:
Default_Level_305_213_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_305_213_objects:
	.byte $FF
; Default_Level_306_214
; Object Set 1
Default_Level_306_214_generators:
Default_Level_306_214_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_306_214_objects:
	.byte $FF
; Default_Level_307_215
; Object Set 1
Default_Level_307_215_generators:
Default_Level_307_215_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_307_215_objects:
	.byte $FF
; Default_Level_308_216
; Object Set 1
Default_Level_308_216_generators:
Default_Level_308_216_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_308_216_objects:
	.byte $FF
; Default_Level_309_217
; Object Set 1
Default_Level_309_217_generators:
Default_Level_309_217_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_309_217_objects:
	.byte $FF
; Default_Level_310_218
; Object Set 1
Default_Level_310_218_generators:
Default_Level_310_218_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_310_218_objects:
	.byte $FF
; Default_Level_311_219
; Object Set 1
Default_Level_311_219_generators:
Default_Level_311_219_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_311_219_objects:
	.byte $FF
; Default_Level_312_220
; Object Set 1
Default_Level_312_220_generators:
Default_Level_312_220_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_312_220_objects:
	.byte $FF
; Default_Level_313_221
; Object Set 1
Default_Level_313_221_generators:
Default_Level_313_221_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_313_221_objects:
	.byte $FF
; Default_Level_314_222
; Object Set 1
Default_Level_314_222_generators:
Default_Level_314_222_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_314_222_objects:
	.byte $FF
; Default_Level_315_223
; Object Set 1
Default_Level_315_223_generators:
Default_Level_315_223_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_315_223_objects:
	.byte $FF
; Default_Level_316_224
; Object Set 1
Default_Level_316_224_generators:
Default_Level_316_224_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_316_224_objects:
	.byte $FF
; Default_Level_317_225
; Object Set 1
Default_Level_317_225_generators:
Default_Level_317_225_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_317_225_objects:
	.byte $FF
; Default_Level_318_226
; Object Set 1
Default_Level_318_226_generators:
Default_Level_318_226_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_318_226_objects:
	.byte $FF
; Default_Level_319_227
; Object Set 1
Default_Level_319_227_generators:
Default_Level_319_227_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_319_227_objects:
	.byte $FF
; Default_Level_320_228
; Object Set 1
Default_Level_320_228_generators:
Default_Level_320_228_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_320_228_objects:
	.byte $FF
; Default_Level_321_229
; Object Set 1
Default_Level_321_229_generators:
Default_Level_321_229_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_321_229_objects:
	.byte $FF
; Default_Level_322_230
; Object Set 1
Default_Level_322_230_generators:
Default_Level_322_230_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_322_230_objects:
	.byte $FF
; Default_Level_323_231
; Object Set 1
Default_Level_323_231_generators:
Default_Level_323_231_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_323_231_objects:
	.byte $FF
; Default_Level_324_232
; Object Set 1
Default_Level_324_232_generators:
Default_Level_324_232_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_324_232_objects:
	.byte $FF
; Default_Level_325_233
; Object Set 1
Default_Level_325_233_generators:
Default_Level_325_233_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_325_233_objects:
	.byte $FF
; Default_Level_326_234
; Object Set 1
Default_Level_326_234_generators:
Default_Level_326_234_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_326_234_objects:
	.byte $FF
; Default_Level_327_235
; Object Set 1
Default_Level_327_235_generators:
Default_Level_327_235_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_327_235_objects:
	.byte $FF
; Default_Level_328_236
; Object Set 1
Default_Level_328_236_generators:
Default_Level_328_236_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_328_236_objects:
	.byte $FF
; Default_Level_329_237
; Object Set 1
Default_Level_329_237_generators:
Default_Level_329_237_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_329_237_objects:
	.byte $FF
; Default_Level_330_238
; Object Set 1
Default_Level_330_238_generators:
Default_Level_330_238_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_330_238_objects:
	.byte $FF
; Default_Level_331_239
; Object Set 1
Default_Level_331_239_generators:
Default_Level_331_239_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_331_239_objects:
	.byte $FF
; Default_Level_332_240
; Object Set 1
Default_Level_332_240_generators:
Default_Level_332_240_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_332_240_objects:
	.byte $FF
; Default_Level_333_241
; Object Set 1
Default_Level_333_241_generators:
Default_Level_333_241_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_333_241_objects:
	.byte $FF
; Default_Level_334_242
; Object Set 1
Default_Level_334_242_generators:
Default_Level_334_242_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_334_242_objects:
	.byte $FF
; Default_Level_335_243
; Object Set 1
Default_Level_335_243_generators:
Default_Level_335_243_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_335_243_objects:
	.byte $FF
; Default_Level_336_244
; Object Set 1
Default_Level_336_244_generators:
Default_Level_336_244_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_336_244_objects:
	.byte $FF
; Default_Level_337_245
; Object Set 1
Default_Level_337_245_generators:
Default_Level_337_245_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_337_245_objects:
	.byte $FF
; Default_Level_338_246
; Object Set 1
Default_Level_338_246_generators:
Default_Level_338_246_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_338_246_objects:
	.byte $FF
; Default_Level_339_247
; Object Set 1
Default_Level_339_247_generators:
Default_Level_339_247_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_339_247_objects:
	.byte $FF
; Default_Level_340_248
; Object Set 1
Default_Level_340_248_generators:
Default_Level_340_248_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_340_248_objects:
	.byte $FF
; Default_Level_341_249
; Object Set 1
Default_Level_341_249_generators:
Default_Level_341_249_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_341_249_objects:
	.byte $FF
; Default_Level_342_250
; Object Set 1
Default_Level_342_250_generators:
Default_Level_342_250_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_342_250_objects:
	.byte $FF
; Default_Level_343_251
; Object Set 1
Default_Level_343_251_generators:
Default_Level_343_251_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_343_251_objects:
	.byte $FF
; Default_Level_344_252
; Object Set 1
Default_Level_344_252_generators:
Default_Level_344_252_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_344_252_objects:
	.byte $FF
; Default_Level_345_253
; Object Set 1
Default_Level_345_253_generators:
Default_Level_345_253_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_345_253_objects:
	.byte $FF
; Default_Level_346_254
; Object Set 1
Default_Level_346_254_generators:
Default_Level_346_254_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_346_254_objects:
	.byte $FF
; Default_Level_347_255
; Object Set 1
Default_Level_347_255_generators:
Default_Level_347_255_header:
	.byte $08; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_347_255_objects:
	.byte $FF
; Ship_Boss_Room_W1
; Object Set 10
Ship_Boss_Room_W1_generators:
Ship_Boss_Room_W1_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_070; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0A; Start action | Graphic set
	.byte $00 | $04; Time | Music
	.byte $00 | $00, $00, $0F; Black boss room background
	.byte $00 | $03, $01, $E4; Thick Vertical Background Pillar
	.byte $00 | $06, $03, $E0; Thick Vertical Background Pillar
	.byte $00 | $04, $04, $E1; Thick Vertical Background Pillar
	.byte $00 | $06, $06, $F0; 1 Background Pillar
	.byte $00 | $05, $07, $F1; 1 Background Pillar
	.byte $00 | $06, $0A, $E1; Thick Vertical Background Pillar
	.byte $00 | $05, $0C, $E1; Thick Vertical Background Pillar
	.byte $00 | $02, $0D, $E5; Thick Vertical Background Pillar
	.byte $60 | $03, $02, $10; Wooden Ship Background Line
	.byte $60 | $06, $04, $10; Wooden Ship Background Line
	.byte $60 | $04, $05, $10; Wooden Ship Background Line
	.byte $60 | $06, $0B, $10; Wooden Ship Background Line
	.byte $60 | $05, $0D, $10; Wooden Ship Background Line
	.byte $60 | $02, $0E, $10; Wooden Ship Background Line
	.byte $60 | $06, $0E, $10; Wooden Ship Background Line
	.byte $00 | $00, $00, $4B; Wooden Ship Pillar
	.byte $00 | $00, $0F, $4B; Wooden Ship Pillar
	.byte $00 | $0A, $01, $5D; Row of Wooden Ship Pillars
	.byte $00 | $09, $04, $62; Thick Wooden Ship Beam
	.byte $00 | $09, $06, $42; Wooden Ship Pillar
	.byte $FF
Ship_Boss_Room_W1_objects:
	.byte $0E, $0D, $08; World x Boss (where x = world)
	.byte $FF
; Ship_Boss_Room_W2
; Object Set 10
Ship_Boss_Room_W2_generators:
Ship_Boss_Room_W2_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_070; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0A; Start action | Graphic set
	.byte $00 | $04; Time | Music
	.byte $00 | $00, $00, $0F; Black boss room background
	.byte $00 | $06, $01, $E1; Thick Vertical Background Pillar
	.byte $00 | $04, $02, $E1; Thick Vertical Background Pillar
	.byte $00 | $03, $04, $E3; Thick Vertical Background Pillar
	.byte $00 | $05, $05, $F2; 1 Background Pillar
	.byte $00 | $06, $06, $F0; 1 Background Pillar
	.byte $00 | $04, $07, $E1; Thick Vertical Background Pillar
	.byte $00 | $05, $08, $E1; Thick Vertical Background Pillar
	.byte $00 | $04, $0B, $E1; Thick Vertical Background Pillar
	.byte $00 | $03, $0D, $E1; Thick Vertical Background Pillar
	.byte $60 | $06, $02, $10; Wooden Ship Background Line
	.byte $60 | $04, $03, $10; Wooden Ship Background Line
	.byte $60 | $03, $05, $10; Wooden Ship Background Line
	.byte $60 | $04, $08, $10; Wooden Ship Background Line
	.byte $60 | $05, $09, $10; Wooden Ship Background Line
	.byte $60 | $04, $0C, $10; Wooden Ship Background Line
	.byte $60 | $03, $0E, $10; Wooden Ship Background Line
	.byte $00 | $00, $00, $4B; Wooden Ship Pillar
	.byte $00 | $00, $0F, $4B; Wooden Ship Pillar
	.byte $00 | $0A, $01, $59; Row of Wooden Ship Pillars
	.byte $00 | $09, $08, $42; Wooden Ship Pillar
	.byte $00 | $09, $04, $62; Thick Wooden Ship Beam
	.byte $00 | $09, $06, $62; Thick Wooden Ship Beam
	.byte $00 | $08, $0B, $63; Thick Wooden Ship Beam
	.byte $00 | $08, $0D, $63; Thick Wooden Ship Beam
	.byte $FF
Ship_Boss_Room_W2_objects:
	.byte $0E, $0D, $06; World x Boss (where x = world)
	.byte $FF
; Ship_Boss_Room_W3
; Object Set 10
Ship_Boss_Room_W3_generators:
Ship_Boss_Room_W3_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_070; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0A; Start action | Graphic set
	.byte $00 | $04; Time | Music
	.byte $00 | $00, $00, $0F; Black boss room background
	.byte $00 | $03, $01, $E4; Thick Vertical Background Pillar
	.byte $00 | $05, $02, $F2; 1 Background Pillar
	.byte $00 | $06, $03, $F1; 1 Background Pillar
	.byte $00 | $05, $04, $E3; Thick Vertical Background Pillar
	.byte $00 | $06, $06, $F1; 1 Background Pillar
	.byte $00 | $07, $07, $F0; 1 Background Pillar
	.byte $00 | $07, $08, $F1; 1 Background Pillar
	.byte $00 | $07, $09, $E0; Thick Vertical Background Pillar
	.byte $00 | $04, $0A, $E2; Thick Vertical Background Pillar
	.byte $00 | $05, $0C, $E2; Thick Vertical Background Pillar
	.byte $00 | $03, $0E, $E5; Thick Vertical Background Pillar
	.byte $60 | $03, $02, $10; Wooden Ship Background Line
	.byte $60 | $05, $05, $10; Wooden Ship Background Line
	.byte $60 | $07, $0A, $10; Wooden Ship Background Line
	.byte $60 | $04, $0B, $10; Wooden Ship Background Line
	.byte $60 | $05, $0D, $10; Wooden Ship Background Line
	.byte $00 | $00, $00, $4B; Wooden Ship Pillar
	.byte $00 | $00, $0F, $4B; Wooden Ship Pillar
	.byte $00 | $0A, $03, $59; Row of Wooden Ship Pillars
	.byte $00 | $0A, $01, $61; Thick Wooden Ship Beam
	.byte $00 | $0A, $04, $61; Thick Wooden Ship Beam
	.byte $00 | $0A, $07, $61; Thick Wooden Ship Beam
	.byte $00 | $0A, $0A, $61; Thick Wooden Ship Beam
	.byte $00 | $0A, $0D, $61; Thick Wooden Ship Beam
	.byte $FF
Ship_Boss_Room_W3_objects:
	.byte $0E, $0D, $08; World x Boss (where x = world)
	.byte $FF
; Ship_Boss_Room_W4
; Object Set 10
Ship_Boss_Room_W4_generators:
Ship_Boss_Room_W4_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_070; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0A; Start action | Graphic set
	.byte $00 | $04; Time | Music
	.byte $00 | $00, $00, $0F; Black boss room background
	.byte $00 | $00, $00, $4B; Wooden Ship Pillar
	.byte $00 | $06, $04, $F2; 1 Background Pillar
	.byte $00 | $06, $0B, $E3; Thick Vertical Background Pillar
	.byte $60 | $06, $05, $11; Wooden Ship Background Line
	.byte $60 | $06, $0C, $11; Wooden Ship Background Line
	.byte $00 | $07, $02, $E0; Thick Vertical Background Pillar
	.byte $60 | $07, $03, $10; Wooden Ship Background Line
	.byte $00 | $07, $09, $F1; 1 Background Pillar
	.byte $00 | $08, $01, $43; Wooden Ship Pillar
	.byte $00 | $08, $02, $43; Wooden Ship Pillar
	.byte $00 | $08, $06, $43; Wooden Ship Pillar
	.byte $00 | $08, $07, $63; Thick Wooden Ship Beam
	.byte $00 | $08, $0E, $E1; Thick Vertical Background Pillar
	.byte $60 | $08, $0F, $10; Wooden Ship Background Line
	.byte $00 | $09, $03, $62; Thick Wooden Ship Beam
	.byte $00 | $09, $05, $42; Wooden Ship Pillar
	.byte $00 | $09, $09, $42; Wooden Ship Pillar
	.byte $00 | $09, $0D, $F0; 1 Background Pillar
	.byte $00 | $0A, $0A, $61; Thick Wooden Ship Beam
	.byte $00 | $0A, $0B, $61; Thick Wooden Ship Beam
	.byte $00 | $0A, $0E, $61; Thick Wooden Ship Beam
	.byte $00 | $0A, $0F, $61; Thick Wooden Ship Beam
	.byte $00 | $0A, $0C, $61; Thick Wooden Ship Beam
	.byte $00 | $00, $0F, $4B; Wooden Ship Pillar
	.byte $FF
Ship_Boss_Room_W4_objects:
	.byte $0E, $0D, $08; World x Boss (where x = world)
	.byte $FF
; Ship_Boss_Room_W5
; Object Set 10
Ship_Boss_Room_W5_generators:
Ship_Boss_Room_W5_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_070; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0A; Start action | Graphic set
	.byte $00 | $04; Time | Music
	.byte $00 | $00, $00, $0F; Black boss room background
	.byte $00 | $03, $01, $F2; 1 Background Pillar
	.byte $00 | $05, $02, $E2; Thick Vertical Background Pillar
	.byte $00 | $04, $04, $E2; Thick Vertical Background Pillar
	.byte $00 | $03, $05, $E0; Thick Vertical Background Pillar
	.byte $00 | $06, $05, $E1; Thick Vertical Background Pillar
	.byte $00 | $06, $07, $E0; Thick Vertical Background Pillar
	.byte $00 | $03, $08, $E2; Thick Vertical Background Pillar
	.byte $00 | $05, $0A, $E1; Thick Vertical Background Pillar
	.byte $00 | $04, $0C, $E2; Thick Vertical Background Pillar
	.byte $00 | $03, $0E, $E4; Thick Vertical Background Pillar
	.byte $60 | $05, $03, $10; Wooden Ship Background Line
	.byte $60 | $04, $05, $10; Wooden Ship Background Line
	.byte $60 | $03, $06, $10; Wooden Ship Background Line
	.byte $60 | $06, $06, $10; Wooden Ship Background Line
	.byte $60 | $06, $08, $10; Wooden Ship Background Line
	.byte $60 | $03, $09, $10; Wooden Ship Background Line
	.byte $60 | $05, $0B, $10; Wooden Ship Background Line
	.byte $60 | $04, $0D, $10; Wooden Ship Background Line
	.byte $00 | $00, $00, $4B; Wooden Ship Pillar
	.byte $00 | $00, $0F, $4B; Wooden Ship Pillar
	.byte $00 | $0A, $01, $5D; Row of Wooden Ship Pillars
	.byte $00 | $09, $03, $62; Thick Wooden Ship Beam
	.byte $00 | $09, $07, $62; Thick Wooden Ship Beam
	.byte $00 | $09, $09, $62; Thick Wooden Ship Beam
	.byte $FF
Ship_Boss_Room_W5_objects:
	.byte $0E, $0D, $08; World x Boss (where x = world)
	.byte $FF
; Ship_Boss_Room_W6
; Object Set 10
Ship_Boss_Room_W6_generators:
Ship_Boss_Room_W6_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_070; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0A; Start action | Graphic set
	.byte $00 | $04; Time | Music
	.byte $00 | $00, $00, $0F; Black boss room background
	.byte $00 | $06, $01, $E0; Thick Vertical Background Pillar
	.byte $00 | $05, $02, $E2; Thick Vertical Background Pillar
	.byte $00 | $03, $03, $E4; Thick Vertical Background Pillar
	.byte $00 | $05, $04, $E3; Thick Vertical Background Pillar
	.byte $00 | $06, $05, $E2; Thick Vertical Background Pillar
	.byte $00 | $03, $06, $E2; Thick Vertical Background Pillar
	.byte $00 | $07, $07, $E0; Thick Vertical Background Pillar
	.byte $00 | $05, $09, $E2; Thick Vertical Background Pillar
	.byte $00 | $07, $0B, $E1; Thick Vertical Background Pillar
	.byte $00 | $06, $0C, $E0; Thick Vertical Background Pillar
	.byte $00 | $05, $0D, $E0; Thick Vertical Background Pillar
	.byte $00 | $06, $0E, $E1; Thick Vertical Background Pillar
	.byte $60 | $05, $03, $10; Wooden Ship Background Line
	.byte $60 | $03, $04, $10; Wooden Ship Background Line
	.byte $60 | $06, $04, $10; Wooden Ship Background Line
	.byte $60 | $05, $05, $10; Wooden Ship Background Line
	.byte $60 | $07, $05, $10; Wooden Ship Background Line
	.byte $60 | $06, $06, $10; Wooden Ship Background Line
	.byte $60 | $03, $07, $10; Wooden Ship Background Line
	.byte $60 | $07, $08, $10; Wooden Ship Background Line
	.byte $60 | $05, $0A, $10; Wooden Ship Background Line
	.byte $60 | $07, $0C, $10; Wooden Ship Background Line
	.byte $60 | $06, $0D, $10; Wooden Ship Background Line
	.byte $60 | $05, $0E, $10; Wooden Ship Background Line
	.byte $00 | $00, $00, $4B; Wooden Ship Pillar
	.byte $00 | $00, $0F, $4B; Wooden Ship Pillar
	.byte $00 | $0A, $01, $61; Thick Wooden Ship Beam
	.byte $00 | $0A, $03, $61; Thick Wooden Ship Beam
	.byte $00 | $0A, $05, $61; Thick Wooden Ship Beam
	.byte $00 | $0A, $07, $61; Thick Wooden Ship Beam
	.byte $00 | $0A, $09, $61; Thick Wooden Ship Beam
	.byte $00 | $0A, $0B, $61; Thick Wooden Ship Beam
	.byte $00 | $0A, $0D, $61; Thick Wooden Ship Beam
	.byte $FF
Ship_Boss_Room_W6_objects:
	.byte $0E, $0D, $07; World x Boss (where x = world)
	.byte $FF
; Ship_Boss_Room_W7
; Object Set 10
Ship_Boss_Room_W7_generators:
Ship_Boss_Room_W7_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_070; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0A; Start action | Graphic set
	.byte $00 | $04; Time | Music
	.byte $00 | $00, $00, $0F; Black boss room background
	.byte $00 | $05, $01, $F1; 1 Background Pillar
	.byte $00 | $07, $01, $E0; Thick Vertical Background Pillar
	.byte $00 | $06, $02, $E0; Thick Vertical Background Pillar
	.byte $00 | $04, $03, $F1; 1 Background Pillar
	.byte $00 | $03, $04, $E1; Thick Vertical Background Pillar
	.byte $00 | $03, $07, $F2; 1 Background Pillar
	.byte $00 | $06, $08, $E0; Thick Vertical Background Pillar
	.byte $00 | $04, $09, $F1; 1 Background Pillar
	.byte $00 | $03, $0A, $F2; 1 Background Pillar
	.byte $00 | $04, $0C, $E1; Thick Vertical Background Pillar
	.byte $60 | $07, $02, $10; Wooden Ship Background Line
	.byte $60 | $06, $03, $10; Wooden Ship Background Line
	.byte $60 | $03, $05, $10; Wooden Ship Background Line
	.byte $60 | $06, $09, $10; Wooden Ship Background Line
	.byte $60 | $04, $0D, $10; Wooden Ship Background Line
	.byte $00 | $00, $00, $4B; Wooden Ship Pillar
	.byte $00 | $00, $0F, $4B; Wooden Ship Pillar
	.byte $00 | $0A, $01, $52; Row of Wooden Ship Pillars
	.byte $00 | $09, $07, $52; Row of Wooden Ship Pillars
	.byte $00 | $09, $0D, $51; Row of Wooden Ship Pillars
	.byte $00 | $08, $04, $43; Wooden Ship Pillar
	.byte $00 | $08, $05, $43; Wooden Ship Pillar
	.byte $00 | $08, $06, $43; Wooden Ship Pillar
	.byte $00 | $08, $0A, $43; Wooden Ship Pillar
	.byte $00 | $08, $0B, $43; Wooden Ship Pillar
	.byte $00 | $08, $0C, $43; Wooden Ship Pillar
	.byte $FF
Ship_Boss_Room_W7_objects:
	.byte $0E, $0D, $07; World x Boss (where x = world)
	.byte $FF
; Anchors_Away_W1
; Object Set 10
Anchors_Away_W1_generators:
Anchors_Away_W1_header:
	.byte $09; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $C0 | $0A; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $60 | $19, $00, $3F; Ground (like on tank levels)
	.byte $60 | $19, $10, $3F; Ground (like on tank levels)
	.byte $40 | $00, $10, $0E; Corner of Airship - Lasts 32 Blocks
	.byte $60 | $19, $20, $3F; Ground (like on tank levels)
	; Pointer on screen $01
	.byte $E0 | $01, $30 | $01, 112; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Anchors_Away_W1_objects:
	.byte $09, $16, $14; Ship Anchor
	.byte $FF