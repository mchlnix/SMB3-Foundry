; Bank 6

; Level_3_W5
; Object Set 1
Level_3_W5_generators:
Level_3_W5_header:
	.byte $38; Next Level
	.byte LEVEL1_SIZE_09 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $0B, $00, $C1, $7F; Flat Ground
	.byte $00 | $19, $00, $C1, $11; Flat Ground
	.byte $40 | $00, $00, $BA, $01; Blue X-Blocks
	.byte $40 | $0D, $00, $BB, $01; Blue X-Blocks
	.byte $40 | $08, $02, $FC; Double-Ended Vertical Pipe
	.byte $00 | $07, $05, $00; Background Hills A
	.byte $00 | $18, $06, $91; Background Bushes
	.byte $20 | $16, $06, $13; Bricks
	.byte $40 | $17, $0A, $E0; White Turtle Bricks
	.byte $40 | $18, $0A, $E0; White Turtle Bricks
	.byte $00 | $04, $0A, $E2; Background Clouds
	.byte $20 | $16, $0C, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $09, $0D, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $0E, $11; Bricks
	.byte $20 | $13, $07, $82; Coins
	.byte $20 | $17, $05, $10; Bricks
	.byte $20 | $18, $05, $10; Bricks
	.byte $00 | $18, $10, $91; Background Bushes
	.byte $40 | $19, $13, $B1, $00; Blue X-Blocks
	.byte $00 | $19, $15, $C1, $01; Flat Ground
	.byte $40 | $19, $18, $B1, $00; Blue X-Blocks
	.byte $20 | $08, $12, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $09, $17, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $08, $1A, $82; Coins
	.byte $20 | $08, $1E, $82; Coins
	.byte $00 | $0A, $1A, $92; Background Bushes
	.byte $00 | $04, $1D, $E2; Background Clouds
	.byte $00 | $02, $12, $E3; Background Clouds
	.byte $20 | $16, $14, $82; Coins
	.byte $00 | $18, $1B, $96; Background Bushes
	.byte $20 | $06, $1C, $14; Bricks
	.byte $20 | $06, $1D, $0B; Brick with 1-up
	.byte $20 | $0A, $19, $05; Muncher
	.byte $20 | $0A, $1A, $05; Muncher
	.byte $20 | $0A, $1B, $05; Muncher
	.byte $20 | $0A, $1C, $05; Muncher
	.byte $20 | $0A, $1D, $05; Muncher
	.byte $20 | $0A, $1E, $05; Muncher
	.byte $20 | $0A, $1F, $05; Muncher
	.byte $20 | $1A, $12, $05; Muncher
	.byte $20 | $1A, $14, $05; Muncher
	.byte $20 | $1A, $17, $05; Muncher
	.byte $00 | $19, $1A, $C1, $0C; Flat Ground
	.byte $20 | $09, $22, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $22, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $18, $24, $92; Background Bushes
	.byte $00 | $03, $27, $02; Background Hills C
	.byte $40 | $19, $28, $B1, $00; Blue X-Blocks
	.byte $00 | $19, $2A, $C1, $01; Flat Ground
	.byte $40 | $19, $2D, $B1, $00; Blue X-Blocks
	.byte $00 | $08, $2C, $01; Background Hills B
	.byte $20 | $15, $2F, $82; Coins
	.byte $00 | $04, $2D, $E3; Background Clouds
	.byte $00 | $10, $21, $E3; Background Clouds
	.byte $20 | $0A, $20, $05; Muncher
	.byte $20 | $0A, $21, $05; Muncher
	.byte $20 | $1A, $27, $05; Muncher
	.byte $20 | $1A, $29, $05; Muncher
	.byte $20 | $1A, $2C, $05; Muncher
	.byte $20 | $1A, $2E, $05; Muncher
	.byte $20 | $1A, $2F, $05; Muncher
	.byte $20 | $0A, $30, $40; Wooden Blocks
	.byte $00 | $18, $30, $94; Background Bushes
	.byte $00 | $0A, $34, $92; Background Bushes
	.byte $00 | $19, $30, $C1, $04; Flat Ground
	.byte $20 | $15, $36, $A3; Downward Pipe (CAN'T go down)
	.byte $00 | $03, $37, $E2; Background Clouds
	.byte $20 | $08, $38, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $18, $39, $95; Background Bushes
	.byte $00 | $11, $3A, $E2; Background Clouds
	.byte $00 | $07, $3B, $00; Background Hills A
	.byte $20 | $15, $3B, $22; '?' Blocks with single coins
	.byte $20 | $15, $3C, $00; '?' with Flower
	.byte $00 | $19, $36, $C1, $09; Flat Ground
	.byte $20 | $1A, $35, $05; Muncher
	.byte $20 | $18, $3F, $40; Wooden Blocks
	.byte $20 | $08, $40, $16; Bricks
	.byte $20 | $08, $40, $30; Bricks with single coins
	.byte $20 | $08, $42, $30; Bricks with single coins
	.byte $20 | $08, $44, $30; Bricks with single coins
	.byte $20 | $08, $46, $30; Bricks with single coins
	.byte $20 | $14, $42, $A4; Downward Pipe (CAN'T go down)
	.byte $00 | $19, $42, $C1, $03; Flat Ground
	.byte $00 | $0A, $44, $93; Background Bushes
	.byte $20 | $0A, $48, $11; Bricks
	.byte $00 | $12, $45, $E2; Background Clouds
	.byte $40 | $19, $48, $B1, $00; Blue X-Blocks
	.byte $20 | $09, $4A, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $4A, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $19, $4A, $C1, $01; Flat Ground
	.byte $00 | $19, $4D, $C1, $01; Flat Ground
	.byte $00 | $18, $4D, $91; Background Bushes
	.byte $00 | $0A, $4F, $94; Background Bushes
	.byte $00 | $02, $49, $E2; Background Clouds
	.byte $00 | $10, $4C, $E2; Background Clouds
	.byte $20 | $1A, $40, $05; Muncher
	.byte $20 | $1A, $41, $05; Muncher
	.byte $20 | $1A, $46, $05; Muncher
	.byte $20 | $1A, $47, $05; Muncher
	.byte $20 | $1A, $49, $05; Muncher
	.byte $20 | $1A, $4C, $05; Muncher
	.byte $20 | $1A, $4F, $05; Muncher
	.byte $00 | $04, $50, $E2; Background Clouds
	.byte $40 | $19, $50, $B1, $00; Blue X-Blocks
	.byte $20 | $16, $51, $82; Coins
	.byte $00 | $13, $51, $E2; Background Clouds
	.byte $00 | $19, $52, $C1, $01; Flat Ground
	.byte $00 | $18, $52, $91; Background Bushes
	.byte $40 | $19, $55, $B1, $00; Blue X-Blocks
	.byte $00 | $19, $58, $C1, $02; Flat Ground
	.byte $00 | $19, $5C, $C1, $26; Flat Ground
	.byte $00 | $03, $58, $02; Background Hills C
	.byte $20 | $17, $59, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $09, $5E, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $16, $5E, $01; Background Hills B
	.byte $00 | $10, $5C, $E3; Background Clouds
	.byte $00 | $11, $55, $E2; Background Clouds
	.byte $20 | $1A, $51, $05; Muncher
	.byte $20 | $1A, $54, $05; Muncher
	.byte $20 | $1A, $56, $05; Muncher
	.byte $20 | $1A, $57, $05; Muncher
	.byte $00 | $04, $61, $E2; Background Clouds
	.byte $00 | $0A, $61, $93; Background Bushes
	.byte $00 | $18, $63, $94; Background Bushes
	.byte $20 | $12, $61, $82; Coins
	.byte $20 | $07, $66, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $06, $6A, $14; Bricks
	.byte $20 | $17, $69, $E4; Rightward Pipe (CAN go in)
	.byte $20 | $06, $6C, $01; '?' with Leaf
	.byte $00 | $0A, $6C, $92; Background Bushes
	.byte $40 | $0D, $6E, $BB, $11; Blue X-Blocks
	.byte $20 | $08, $61, $13; Bricks
	.byte $00 | $02, $69, $E2; Background Clouds
	.byte $20 | $08, $70, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $03, $73, $E2; Background Clouds
	.byte $00 | $08, $76, $01; Background Hills B
	.byte $20 | $00, $76, $D1; Upward Pipe (CAN'T go up)
	.byte $40 | $00, $7B, $BC, $04; Blue X-Blocks
	.byte $40 | $00, $80, $BF, $0A; Blue X-Blocks
	.byte $40 | $10, $80, $BA, $0A; Blue X-Blocks
	; Pointer on screen $06
	.byte $E0 | $06, $70 | $01, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_3_W5_objects:
	.byte $A2, $0C, $16; Red Piranha Plant (upward)
	.byte $2B, $08, $18; Kuribo's Goomba
	.byte $A2, $0D, $09; Red Piranha Plant (upward)
	.byte $A6, $12, $08; Red Venus Fire Trap (upward)
	.byte $A2, $17, $09; Red Piranha Plant (upward)
	.byte $71, $1C, $18; Spiny
	.byte $71, $1E, $18; Spiny
	.byte $71, $20, $18; Spiny
	.byte $A2, $22, $16; Red Piranha Plant (upward)
	.byte $71, $26, $0A; Spiny
	.byte $71, $28, $0A; Spiny
	.byte $71, $2A, $0A; Spiny
	.byte $55, $32, $09; Bob-Omb
	.byte $A2, $36, $15; Red Piranha Plant (upward)
	.byte $55, $3C, $17; Bob-Omb
	.byte $2B, $3D, $0A; Kuribo's Goomba
	.byte $A6, $42, $14; Red Venus Fire Trap (upward)
	.byte $A0, $4A, $16; Green Piranha Plant (upward)
	.byte $71, $4D, $0A; Spiny
	.byte $71, $51, $0A; Spiny
	.byte $71, $55, $0A; Spiny
	.byte $A2, $59, $17; Red Piranha Plant (upward)
	.byte $2B, $5C, $0A; Kuribo's Goomba
	.byte $71, $64, $18; Spiny
	.byte $A6, $66, $07; Red Venus Fire Trap (upward)
	.byte $71, $6A, $0A; Spiny
	.byte $FF
; Tower__Part_2__W5
; Object Set 2
Tower__Part_2__W5_generators:
Tower__Part_2__W5_header:
	.byte $3C; Next Level
	.byte LEVEL1_SIZE_02 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_13; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $00 | $12, $02, $42; Dungeon background
	.byte $00 | $10, $05, $4F; Dungeon background
	.byte $00 | $10, $15, $46; Dungeon background
	.byte $00 | $02, $10, $5D; Dark dungeon background
	.byte $00 | $11, $0A, $41; Dungeon background
	.byte $60 | $19, $06, $18; Dark Dungeon Background
	.byte $60 | $19, $0F, $1A; Dark Dungeon Background
	.byte $00 | $00, $00, $01; MSG_NOTHING
	.byte $00 | $00, $00, $EF, $0F; Horizontally oriented X-blocks
	.byte $00 | $10, $00, $EA, $01; Horizontally oriented X-blocks
	.byte $00 | $10, $02, $E1, $02; Horizontally oriented X-blocks
	.byte $00 | $18, $02, $E2, $09; Horizontally oriented X-blocks
	.byte $00 | $19, $0F, $E1, $06; Horizontally oriented X-blocks
	.byte $00 | $14, $0F, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $10, $09, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $10, $0A, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $10, $0C, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $1A, $0C, $C2; Floor Spikes
	.byte $20 | $14, $02, $A3; Downward Pipe (CAN'T go down)
	.byte $60 | $00, $10, $29, $0F; Dark Dungeon Background
	.byte $00 | $00, $10, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $07, $10, $E8, $07; Horizontally oriented X-blocks
	.byte $00 | $08, $18, $E7, $01; Horizontally oriented X-blocks
	.byte $00 | $09, $1A, $E6, $01; Horizontally oriented X-blocks
	.byte $00 | $10, $10, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $14, $11, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $15, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $1C, $E4, $01; Horizontally oriented X-blocks
	.byte $00 | $17, $1B, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $1A, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $00, $1E, $F1, $1A; Vertically oriented X-blocks
	.byte $00 | $1A, $16, $C3; Floor Spikes
	.byte $00 | $14, $10, $02; Rotodisc block
	.byte $20 | $00, $13, $C2; Upward Pipe (CAN go up)
	.byte $40 | $0A, $1C, $F8; Double-Ended Vertical Pipe
	.byte $00 | $01, $11, $10; Bottom of background with pillars A
	.byte $00 | $01, $16, $11; Bottom of background with pillars A
	.byte $00 | $01, $10, $50; Dark dungeon background
	.byte $00 | $01, $15, $50; Dark dungeon background
	.byte $00 | $01, $18, $51; Dark dungeon background
	.byte $00 | $01, $1C, $51; Dark dungeon background
	.byte $00 | $04, $18, $91; Dungeon Lamps (Note: extends to ceiling)
	; Pointer on screen $01
	.byte $E0 | $01, $50 | $01, 113; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Tower__Part_2__W5_objects:
	.byte $8A, $0A, $11; Thwomp (normal)
	.byte $5B, $10, $14; Single Rotodisc (rotates counterclockwise)
	.byte $FF
; Tower_Outside_Area__Part_2__W5
; Object Set 13
Tower_Outside_Area__Part_2__W5_generators:
Tower_Outside_Area__Part_2__W5_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $00 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0D; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $00 | $0C, $37, $02; Cloud Background A
	.byte $00 | $11, $36, $02; Cloud Background A
	.byte $00 | $13, $30, $02; Cloud Background A
	.byte $00 | $14, $2D, $02; Cloud Background A
	.byte $00 | $14, $20, $02; Cloud Background A
	.byte $00 | $0F, $21, $02; Cloud Background A
	.byte $00 | $07, $21, $02; Cloud Background A
	.byte $00 | $03, $21, $02; Cloud Background A
	.byte $00 | $00, $22, $02; Cloud Background A
	.byte $00 | $14, $14, $02; Cloud Background A
	.byte $00 | $11, $1F, $02; Cloud Background A
	.byte $00 | $10, $12, $02; Cloud Background A
	.byte $00 | $0F, $1D, $02; Cloud Background A
	.byte $00 | $0B, $1D, $02; Cloud Background A
	.byte $00 | $09, $1F, $02; Cloud Background A
	.byte $00 | $07, $1D, $02; Cloud Background A
	.byte $00 | $05, $1B, $02; Cloud Background A
	.byte $00 | $03, $19, $02; Cloud Background A
	.byte $00 | $00, $1A, $02; Cloud Background A
	.byte $00 | $14, $0A, $02; Cloud Background A
	.byte $00 | $11, $0F, $02; Cloud Background A
	.byte $00 | $14, $18, $02; Cloud Background A
	.byte $20 | $14, $17, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $17, $31; Bricks with single coins
	.byte $20 | $17, $17, $31; Bricks with single coins
	.byte $20 | $18, $15, $19; Bricks
	.byte $20 | $19, $15, $19; Bricks
	.byte $20 | $1A, $15, $19; Bricks
	.byte $60 | $18, $12, $42, $02; White Background
	.byte $60 | $00, $1F, $46, $07; White Background
	.byte $20 | $00, $22, $C5; Upward Pipe (CAN go up)
	.byte $00 | $09, $21, $F5; World 6-style Cloud Platform
	.byte $00 | $0D, $24, $F2; World 6-style Cloud Platform
	.byte $20 | $11, $21, $81; Coins
	.byte $20 | $11, $24, $81; Coins
	.byte $20 | $14, $22, $23; '?' blocks with single coins
	.byte $20 | $14, $23, $0C; Brick with Vine
	.byte $00 | $18, $21, $F2; World 6-style Cloud Platform
	.byte $00 | $18, $24, $F2; World 6-style Cloud Platform
	.byte $60 | $11, $39, $49, $06; White Background
	.byte $60 | $19, $35, $41, $03; White Background
	.byte $FF
Tower_Outside_Area__Part_2__W5_objects:
	.byte $6D, $24, $17; Red Koopa Troopa
	.byte $25, $20, $80; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_9_Ending_W5
; Object Set 13
Level_9_Ending_W5_generators:
Level_9_Ending_W5_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_02 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0D; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $00, $00, $03; Sets background color to white
	.byte $40 | $00, $09, $09; Level Ending
	.byte $60 | $19, $00, $11, $1F; Clouds A
	.byte $40 | $17, $00, $22; Leftward Pipe (CAN'T go in)
	.byte $FF
Level_9_Ending_W5_objects:
	.byte $83, $0F, $12; Lakitu
	.byte $41, $18, $15; Goal Card
	.byte $FF
; Dungeon__2_W5
; Object Set 2
Dungeon__2_W5_generators:
Dungeon__2_W5_header:
	.byte $84; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $19, $00, $1F; Dark Dungeon Background
	.byte $60 | $19, $10, $1F; Dark Dungeon Background
	.byte $60 | $19, $20, $1F; Dark Dungeon Background
	.byte $60 | $19, $30, $1F; Dark Dungeon Background
	.byte $60 | $19, $40, $1F; Dark Dungeon Background
	.byte $60 | $19, $50, $1F; Dark Dungeon Background
	.byte $60 | $19, $60, $1F; Dark Dungeon Background
	.byte $60 | $19, $70, $1F; Dark Dungeon Background
	.byte $00 | $0C, $00, $E1, $7F; Horizontally oriented X-blocks
	.byte $60 | $0E, $00, $41, $7F; Lava
	.byte $60 | $1A, $00, $40, $7F; Lava
	.byte $00 | $0E, $02, $E4, $01; Horizontally oriented X-blocks
	.byte $40 | $17, $01, $44; Bridge
	.byte $40 | $17, $08, $42; Bridge
	.byte $40 | $16, $0F, $41; Bridge
	.byte $20 | $13, $02, $D2; Upward Pipe (CAN'T go up)
	.byte $40 | $15, $14, $42; Bridge
	.byte $40 | $17, $1B, $44; Bridge
	.byte $40 | $17, $20, $4B; Bridge
	.byte $20 | $15, $20, $24; '?' blocks with single coins
	.byte $20 | $15, $25, $02; '?' with star
	.byte $40 | $15, $30, $41; Bridge
	.byte $40 | $15, $34, $41; Bridge
	.byte $40 | $17, $3B, $44; Bridge
	.byte $40 | $16, $42, $41; Bridge
	.byte $40 | $18, $49, $41; Bridge
	.byte $40 | $18, $4D, $40; Bridge
	.byte $40 | $18, $50, $40; Bridge
	.byte $40 | $18, $53, $41; Bridge
	.byte $40 | $17, $59, $46; Bridge
	.byte $20 | $15, $5B, $01; '?' with leaf
	.byte $20 | $15, $5C, $20; '?' blocks with single coins
	.byte $40 | $17, $66, $4F; Bridge
	.byte $40 | $17, $76, $49; Bridge
	.byte $00 | $0E, $7D, $E4, $01; Horizontally oriented X-blocks
	.byte $20 | $13, $7D, $C1; Upward Pipe (CAN go up)
	; Pointer on screen $07
	.byte $E0 | $07, $60 | $01, 114; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__2_W5_objects:
	.byte $9E, $06, $17; Podoboo (comes out of lava)
	.byte $9E, $0B, $15; Podoboo (comes out of lava)
	.byte $9E, $0D, $11; Podoboo (comes out of lava)
	.byte $53, $12, $0F; Stray Podoboo
	.byte $53, $18, $0F; Stray Podoboo
	.byte $9E, $1E, $12; Podoboo (comes out of lava)
	.byte $9E, $24, $16; Podoboo (comes out of lava)
	.byte $9E, $2C, $15; Podoboo (comes out of lava)
	.byte $9E, $2E, $11; Podoboo (comes out of lava)
	.byte $3F, $28, $17; Dry Bones
	.byte $9E, $32, $11; Podoboo (comes out of lava)
	.byte $9E, $36, $12; Podoboo (comes out of lava)
	.byte $53, $3A, $0F; Stray Podoboo
	.byte $2F, $47, $17; Boo Buddy
	.byte $9E, $4B, $14; Podoboo (comes out of lava)
	.byte $9E, $4E, $17; Podoboo (comes out of lava)
	.byte $9E, $51, $14; Podoboo (comes out of lava)
	.byte $53, $56, $0F; Stray Podoboo
	.byte $53, $5E, $0F; Stray Podoboo
	.byte $9E, $63, $11; Podoboo (comes out of lava)
	.byte $2F, $6F, $15; Boo Buddy
	.byte $9E, $6A, $10; Podoboo (comes out of lava)
	.byte $9E, $71, $12; Podoboo (comes out of lava)
	.byte $9E, $78, $13; Podoboo (comes out of lava)
	.byte $53, $79, $0F; Stray Podoboo
	.byte $3F, $7E, $17; Dry Bones
	.byte $FF
; Level_7_Bonus_Area_W5
; Object Set 1
Level_7_Bonus_Area_W5_generators:
Level_7_Bonus_Area_W5_header:
	.byte $85; Next Level
	.byte LEVEL1_SIZE_07 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_13; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	.byte $60 | $00, $00, $19; Cloud Platform
	.byte $20 | $00, $02, $D5; Upward Pipe (CAN'T go up)
	.byte $00 | $1A, $00, $C0, $2A; Flat Ground
	.byte $00 | $19, $03, $92; Background Bushes
	.byte $00 | $09, $05, $E2; Background Clouds
	.byte $00 | $0F, $07, $E3; Background Clouds
	.byte $60 | $01, $08, $16; Cloud Platform
	.byte $00 | $19, $08, $90; Background Bushes
	.byte $00 | $14, $0A, $43; Blue Block Platform (Extends to ground)
	.byte $00 | $17, $0C, $22; Orange Block Platform (Extends to ground)
	.byte $00 | $0C, $0B, $E2; Background Clouds
	.byte $60 | $02, $0D, $15; Cloud Platform
	.byte $00 | $12, $10, $02; Background Hills C
	.byte $20 | $00, $13, $14; Bricks
	.byte $20 | $00, $19, $16; Bricks
	.byte $20 | $01, $13, $14; Bricks
	.byte $20 | $01, $19, $16; Bricks
	.byte $20 | $02, $13, $14; Bricks
	.byte $20 | $02, $19, $16; Bricks
	.byte $20 | $03, $15, $18; Bricks
	.byte $20 | $04, $17, $14; Bricks
	.byte $20 | $05, $19, $10; Bricks
	.byte $20 | $03, $18, $0D; Brick with P-Switch
	.byte $00 | $0A, $13, $E2; Background Clouds
	.byte $20 | $14, $15, $84; Coins
	.byte $20 | $17, $16, $09; Brick with Continuous Star
	.byte $20 | $18, $16, $40; Wooden Blocks
	.byte $20 | $19, $16, $40; Wooden Blocks
	.byte $00 | $19, $1B, $92; Background Bushes
	.byte $00 | $08, $1D, $E3; Background Clouds
	.byte $20 | $14, $1D, $84; Coins
	.byte $20 | $16, $1F, $40; Wooden Blocks
	.byte $20 | $17, $1F, $40; Wooden Blocks
	.byte $20 | $18, $1F, $40; Wooden Blocks
	.byte $20 | $19, $1F, $40; Wooden Blocks
	.byte $00 | $12, $21, $02; Background Hills C
	.byte $60 | $00, $20, $1E; Cloud Platform
	.byte $00 | $02, $22, $E2; Background Clouds
	.byte $00 | $04, $26, $E3; Background Clouds
	.byte $20 | $14, $26, $84; Coins
	.byte $40 | $17, $28, $05; Wooden Block with Leaf
	.byte $20 | $18, $28, $40; Wooden Blocks
	.byte $20 | $19, $28, $40; Wooden Blocks
	.byte $00 | $1A, $2D, $C0, $11; Flat Ground
	.byte $00 | $14, $2E, $33; Green Block Platform (Extends to ground)
	.byte $20 | $00, $2F, $18; Bricks
	.byte $20 | $16, $2D, $09; Brick with Continuous Star
	.byte $20 | $01, $31, $14; Bricks
	.byte $20 | $02, $33, $10; Bricks
	.byte $00 | $18, $31, $13; White Block Platform (Extends to ground)
	.byte $20 | $12, $35, $41; Wooden Blocks
	.byte $20 | $16, $37, $61; Note Blocks - movable two directions
	.byte $20 | $0E, $39, $41; Wooden Blocks
	.byte $20 | $0A, $3B, $41; Wooden Blocks
	.byte $00 | $19, $3A, $92; Background Bushes
	.byte $40 | $16, $37, $03; Note Block with Star
	.byte $20 | $0A, $39, $09; Brick with Continuous Star
	.byte $20 | $00, $3B, $C4; Upward Pipe (CAN go up)
	.byte $40 | $00, $40, $BF, $0F; Blue X-Blocks
	.byte $40 | $10, $40, $BA, $0F; Blue X-Blocks
	.byte $40 | $18, $50, $22; Leftward Pipe (CAN'T go in)
	.byte $00 | $1A, $50, $BF; Cloud Platform
	.byte $00 | $1A, $60, $BF; Cloud Platform
	.byte $40 | $00, $5A, $09; Level Ending
	; Pointer on screen $03
	.byte $E0 | $03, $60 | $01, 5; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_7_Bonus_Area_W5_objects:
	.byte $6D, $12, $19; Red Koopa Troopa
	.byte $83, $56, $12; Lakitu
	.byte $41, $68, $15; Goal Card
	.byte $FF
; Level_1_Bonus_Area_W6
; Object Set 12
Level_1_Bonus_Area_W6_generators:
Level_1_Bonus_Area_W6_header:
	.byte $8E; Next Level
	.byte LEVEL1_SIZE_02 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_12; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $60 | $0F, $00, $8F; Large Ice Blocks
	.byte $60 | $11, $00, $80; Large Ice Blocks
	.byte $60 | $13, $00, $80; Large Ice Blocks
	.byte $60 | $15, $00, $80; Large Ice Blocks
	.byte $60 | $17, $00, $80; Large Ice Blocks
	.byte $60 | $19, $00, $8F; Large Ice Blocks
	.byte $60 | $17, $04, $80; Large Ice Blocks
	.byte $60 | $11, $0C, $80; Large Ice Blocks
	.byte $60 | $14, $06, $1F; Ice Blocks
	.byte $20 | $15, $09, $1A; Bricks
	.byte $20 | $16, $09, $1A; Bricks
	.byte $20 | $17, $09, $1A; Bricks
	.byte $20 | $18, $09, $1A; Bricks
	.byte $60 | $11, $10, $80; Large Ice Blocks
	.byte $60 | $11, $18, $80; Large Ice Blocks
	.byte $60 | $14, $16, $17; Ice Blocks
	.byte $60 | $17, $16, $80; Large Ice Blocks
	.byte $60 | $17, $1A, $81; Large Ice Blocks
	.byte $60 | $11, $1E, $80; Large Ice Blocks
	.byte $60 | $13, $1E, $80; Large Ice Blocks
	.byte $60 | $15, $1E, $80; Large Ice Blocks
	.byte $60 | $17, $1E, $80; Large Ice Blocks
	.byte $40 | $13, $1C, $08; P-Switch
	.byte $00 | $17, $19, $05; Door
	; Pointer on screen $01
	.byte $E0 | $01, $10 | $08, 195; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_1_Bonus_Area_W6_objects:
	.byte $FF
; Dungeon__1_Spike_Room_W6
; Object Set 2
Dungeon__1_Spike_Room_W6_generators:
Dungeon__1_Spike_Room_W6_header:
	.byte $8F; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $00 | $10, $00, $4F; Dungeon background
	.byte $00 | $10, $10, $42; Dungeon background
	.byte $00 | $02, $13, $4C; Dungeon background
	.byte $00 | $02, $20, $47; Dungeon background
	.byte $00 | $10, $18, $49; Dungeon background
	.byte $00 | $10, $28, $4F; Dungeon background
	.byte $00 | $10, $38, $46; Dungeon background
	.byte $00 | $00, $00, $EF, $12; Horizontally oriented X-blocks
	.byte $00 | $17, $08, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $13, $07, $62; Dungeon windows
	.byte $00 | $16, $08, $02; Rotodisc block
	.byte $00 | $17, $02, $00; Door
	.byte $00 | $10, $04, $20; Bottom of background with pillars B
	.byte $20 | $16, $0A, $01; '?' with leaf
	.byte $00 | $00, $13, $E1, $14; Horizontally oriented X-blocks
	.byte $00 | $10, $11, $20; Bottom of background with pillars B
	.byte $00 | $04, $15, $74; Long dungeon windows
	.byte $00 | $0A, $17, $E5, $0A; Horizontally oriented X-blocks
	.byte $00 | $10, $17, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $17, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $10, $1E, $E7, $00; Horizontally oriented X-blocks
	.byte $00 | $14, $17, $02; Rotodisc block
	.byte $00 | $15, $1E, $02; Rotodisc block
	.byte $20 | $14, $19, $21; '?' blocks with single coins
	.byte $20 | $15, $1C, $21; '?' blocks with single coins
	.byte $20 | $14, $18, $02; '?' with star
	.byte $00 | $00, $28, $EF, $17; Horizontally oriented X-blocks
	.byte $00 | $17, $26, $E1, $05; Horizontally oriented X-blocks
	.byte $00 | $18, $25, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $2F, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $18, $2C, $CA; Floor Spikes
	.byte $00 | $10, $29, $20; Bottom of background with pillars B
	.byte $20 | $09, $21, $0B; Brick with 1-up
	.byte $00 | $10, $3F, $E4, $00; Horizontally oriented X-blocks
	.byte $00 | $15, $37, $E3, $08; Horizontally oriented X-blocks
	.byte $20 | $12, $30, $01; '?' with leaf
	.byte $00 | $13, $3D, $00; Door
	.byte $00 | $10, $38, $20; Bottom of background with pillars B
	; Pointer on screen $03
	.byte $E0 | $03, $60 | $08, 22; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $00
	.byte $E0 | $00, $50 | $08, 212; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__1_Spike_Room_W6_objects:
	.byte $51, $08, $16; Double Rotodisc (rotates counterclockwise)
	.byte $5B, $17, $14; Single Rotodisc (rotates counterclockwise)
	.byte $5B, $1E, $15; Single Rotodisc (rotates counterclockwise)
	.byte $5F, $25, $0A; Double Rotodisc (rotates both ways, starting at top)
	.byte $5B, $30, $12; Single Rotodisc (rotates counterclockwise)
	.byte $FF
; Level_6_W6
; Object Set 3
Level_6_W6_generators:
Level_6_W6_header:
	.byte $94; Next Level
	.byte LEVEL1_SIZE_12 | LEVEL1_YSTART_040; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_07; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_12; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $00, $00, $5F, $01; Hilly Wall
	.byte $80 | $10, $00, $5A, $01; Hilly Wall
	.byte $80 | $12, $02, $88, $0D; Flat Land - Hilly
	.byte $60 | $00, $01, $EF; Hilly Wall - Right Side
	.byte $60 | $10, $01, $E1; Hilly Wall - Right Side
	.byte $80 | $00, $04, $B0, $2C; Ceiling
	.byte $00 | $00, $04, $07; Lower Left Hill Corner
	.byte $60 | $12, $08, $0B; Steps B
	.byte $60 | $0D, $0D, $0C; Square Hill Object
	.byte $60 | $15, $0F, $0D; Flat Land & Water Pits
	.byte $20 | $00, $02, $D5; Upward Pipe (CAN'T go up)
	.byte $20 | $11, $0F, $70; Wooden Blocks - movable
	.byte $20 | $12, $0F, $70; Wooden Blocks - movable
	.byte $80 | $0E, $19, $B2, $0F; Ceiling
	.byte $00 | $0B, $1C, $63; 45 Degree Hill - Down/Left
	.byte $60 | $08, $1D, $0D; Flat Land & Water Pits
	.byte $60 | $0D, $11, $04; Horizontal Hill Strip
	.byte $60 | $15, $16, $0D; Flat Land & Water Pits
	.byte $80 | $18, $1E, $82, $06; Flat Land - Hilly
	.byte $20 | $07, $1F, $82; Coins
	.byte $20 | $08, $1A, $81; Coins
	.byte $20 | $0B, $12, $82; Coins
	.byte $20 | $11, $18, $D3; Upward Pipe (CAN'T go up)
	.byte $40 | $13, $10, $06; Wooden Block with Star
	.byte $20 | $14, $10, $70; Wooden Blocks - movable
	.byte $20 | $11, $18, $D3; Upward Pipe (CAN'T go up)
	.byte $80 | $0C, $25, $51, $06; Hilly Wall
	.byte $80 | $0C, $2C, $B0, $0A; Ceiling
	.byte $80 | $0A, $2D, $81, $03; Flat Land - Hilly
	.byte $00 | $0D, $28, $83; 45 Degree Hill - Up/Right
	.byte $80 | $14, $25, $86, $02; Flat Land - Hilly
	.byte $00 | $14, $25, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $15, $25, $E2; Hilly Wall - Left Side
	.byte $00 | $14, $28, $53; 45 Degree Hill - Down/Right
	.byte $80 | $18, $28, $52, $03; Hilly Wall
	.byte $60 | $18, $2B, $E2; Hilly Wall - Right Side
	.byte $80 | $18, $2E, $52, $05; Hilly Wall
	.byte $00 | $18, $2E, $E2; Hilly Wall - Left Side
	.byte $60 | $06, $25, $0E; 30-Degree Hill & Water Pits A
	.byte $80 | $0A, $23, $51, $01; Hilly Wall
	.byte $00 | $0A, $23, $E0; Hilly Wall - Left Side
	.byte $00 | $0B, $23, $F0; Dark Underground Wall - Left Side
	.byte $60 | $09, $23, $60; 30 Degree Hill - Down/Left
	.byte $60 | $06, $2C, $E3; Hilly Wall - Right Side
	.byte $00 | $06, $2C, $04; Upper Right Hill Corner - Hilly
	.byte $20 | $03, $27, $82; Coins
	.byte $20 | $06, $2F, $00; '?' with flower
	.byte $20 | $18, $2C, $A2; Downward Pipe (CAN'T go down)
	.byte $80 | $0A, $40, $3F, $3F; Water
	.byte $80 | $1A, $40, $30, $3F; Water
	.byte $80 | $0D, $80, $36, $15; Water
	.byte $80 | $13, $38, $33, $07; Water
	.byte $80 | $00, $31, $5B, $05; Hilly Wall
	.byte $80 | $00, $37, $5C, $0C; Hilly Wall
	.byte $00 | $0D, $37, $76; 45 Degree Hill - Up/Left
	.byte $00 | $13, $3D, $B0; 45 Degree Underwater Hill - Up/Left
	.byte $80 | $0D, $3E, $C6, $05; Underwater Ceiling
	.byte $00 | $12, $33, $65; 45 Degree Hill - Down/Left
	.byte $80 | $12, $34, $88, $02; Flat Land - Hilly
	.byte $80 | $17, $37, $53, $04; Hilly Wall
	.byte $00 | $12, $37, $54; 45 Degree Hill - Down/Right
	.byte $00 | $13, $38, $93; 45 Degree Underwater Hill - Down/Right
	.byte $80 | $17, $3C, $93, $13; Flat Land - Underwater
	.byte $00 | $01, $31, $E8; Hilly Wall - Left Side
	.byte $20 | $0D, $34, $D1; Upward Pipe (CAN'T go up)
	.byte $80 | $00, $44, $57, $0B; Hilly Wall
	.byte $00 | $08, $44, $CB; 45 Degree Underwater Hill - Up/Right
	.byte $00 | $08, $4E, $81; 45 Degree Hill - Up/Right
	.byte $80 | $00, $50, $B7, $20; Ceiling
	.byte $80 | $07, $58, $50, $01; Hilly Wall
	.byte $00 | $08, $58, $F3; Dark Underground Wall - Left Side
	.byte $60 | $08, $59, $F5; Dark Underground Wall - Right Side
	.byte $00 | $08, $58, $E1; Hilly Wall - Left Side
	.byte $60 | $08, $59, $E1; Hilly Wall - Right Side
	.byte $00 | $0C, $51, $A1; 45 Degree Underwater Hill - Down/Left
	.byte $00 | $0E, $50, $08; Lower Left Hill Corner - UnderWater
	.byte $80 | $0C, $52, $91, $05; Flat Land - Underwater
	.byte $80 | $0E, $51, $C0, $07; Underwater Ceiling
	.byte $00 | $0E, $59, $0B; Lower Right Hill Corner - UnderWater
	.byte $80 | $13, $54, $90, $07; Flat Land - Underwater
	.byte $80 | $14, $54, $C0, $07; Underwater Ceiling
	.byte $00 | $13, $54, $02; Upper Left Hill Corner - UnderWater
	.byte $00 | $14, $54, $08; Lower Left Hill Corner - UnderWater
	.byte $00 | $13, $5B, $05; Upper Right Hill Corner - UnderWater
	.byte $00 | $14, $5B, $0B; Lower Right Hill Corner - UnderWater
	.byte $00 | $17, $50, $91; 45 Degree Underwater Hill - Down/Right
	.byte $80 | $19, $52, $91, $01; Flat Land - Underwater
	.byte $00 | $19, $53, $05; Upper Right Hill Corner - UnderWater
	.byte $60 | $1A, $53, $F0; Dark Underground Wall - Right Side
	.byte $80 | $19, $58, $91, $17; Flat Land - Underwater
	.byte $00 | $19, $58, $02; Upper Left Hill Corner - UnderWater
	.byte $00 | $1A, $58, $F0; Dark Underground Wall - Left Side
	.byte $80 | $0C, $58, $51, $00; Hilly Wall
	.byte $80 | $19, $50, $51, $01; Hilly Wall
	.byte $20 | $09, $56, $0F; Invisible 1-up
	.byte $00 | $0B, $6B, $02; Upper Left Hill Corner - UnderWater
	.byte $00 | $0B, $6C, $05; Upper Right Hill Corner - UnderWater
	.byte $00 | $11, $6B, $08; Lower Left Hill Corner - UnderWater
	.byte $00 | $11, $6C, $0B; Lower Right Hill Corner - UnderWater
	.byte $00 | $0C, $6B, $F4; Dark Underground Wall - Left Side
	.byte $60 | $0C, $6C, $F4; Dark Underground Wall - Right Side
	.byte $80 | $10, $62, $9A, $01; Flat Land - Underwater
	.byte $00 | $10, $62, $02; Upper Left Hill Corner - UnderWater
	.byte $00 | $10, $63, $05; Upper Right Hill Corner - UnderWater
	.byte $00 | $11, $62, $F7; Dark Underground Wall - Left Side
	.byte $60 | $11, $63, $F7; Dark Underground Wall - Right Side
	.byte $00 | $19, $6F, $05; Upper Right Hill Corner - UnderWater
	.byte $60 | $1A, $6F, $F0; Dark Underground Wall - Right Side
	.byte $20 | $0B, $62, $45; Wooden blocks
	.byte $20 | $0B, $63, $20; '?' blocks with single coins
	.byte $20 | $0B, $64, $00; '?' with flower
	.byte $20 | $0C, $67, $40; Wooden blocks
	.byte $20 | $0F, $67, $40; Wooden blocks
	.byte $20 | $10, $67, $40; Wooden blocks
	.byte $20 | $11, $67, $40; Wooden blocks
	.byte $20 | $12, $67, $40; Wooden blocks
	.byte $20 | $13, $67, $40; Wooden blocks
	.byte $20 | $14, $67, $44; Wooden blocks
	.byte $80 | $00, $71, $CD, $1D; Underwater Ceiling
	.byte $00 | $08, $71, $F4; Dark Underground Wall - Left Side
	.byte $00 | $08, $71, $E1; Hilly Wall - Left Side
	.byte $00 | $0D, $71, $08; Lower Left Hill Corner - UnderWater
	.byte $80 | $19, $74, $91, $08; Flat Land - Underwater
	.byte $00 | $19, $74, $02; Upper Left Hill Corner - UnderWater
	.byte $00 | $1A, $74, $F0; Dark Underground Wall - Left Side
	.byte $80 | $14, $7D, $96, $11; Flat Land - Underwater
	.byte $00 | $14, $7D, $02; Upper Left Hill Corner - UnderWater
	.byte $00 | $15, $7D, $F3; Dark Underground Wall - Left Side
	.byte $20 | $0C, $6D, $43; Wooden blocks
	.byte $20 | $14, $74, $42; Wooden blocks
	.byte $20 | $14, $79, $43; Wooden blocks
	.byte $80 | $00, $8F, $59, $03; Hilly Wall
	.byte $80 | $14, $8F, $56, $07; Hilly Wall
	.byte $00 | $0A, $8F, $83; 45 Degree Hill - Up/Right
	.byte $00 | $0D, $8F, $C0; 45 Degree Underwater Hill - Up/Right
	.byte $20 | $0E, $80, $D2; Upward Pipe (CAN'T go up)
	.byte $20 | $0E, $88, $D2; Upward Pipe (CAN'T go up)
	.byte $20 | $11, $84, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $12, $8C, $A1; Downward Pipe (CAN'T go down)
	.byte $80 | $00, $93, $B9, $08; Ceiling
	.byte $80 | $00, $9C, $BC, $06; Ceiling
	.byte $00 | $0A, $9C, $E1; Hilly Wall - Left Side
	.byte $00 | $0C, $9C, $07; Lower Left Hill Corner
	.byte $00 | $0C, $96, $67; 45 Degree Hill - Down/Left
	.byte $00 | $0D, $95, $A6; 45 Degree Underwater Hill - Down/Left
	.byte $80 | $0C, $97, $8E, $02; Flat Land - Hilly
	.byte $00 | $0C, $99, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $0D, $99, $E2; Hilly Wall - Right Side
	.byte $80 | $10, $9A, $8A, $0D; Flat Land - Hilly
	.byte $80 | $00, $A3, $59, $02; Hilly Wall
	.byte $00 | $0A, $A3, $82; 45 Degree Hill - Up/Right
	.byte $80 | $00, $A6, $53, $0B; Hilly Wall
	.byte $60 | $04, $A6, $85; 30 Degree Hill - Up/Right
	.byte $00 | $10, $A7, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $11, $A7, $E9; Hilly Wall - Right Side
	.byte $80 | $10, $AA, $5A, $15; Hilly Wall
	.byte $00 | $10, $AA, $EA; Hilly Wall - Left Side
	.byte $60 | $0F, $AA, $60; 30 Degree Hill - Down/Left
	.byte $60 | $0C, $AC, $0E; 30-Degree Hill & Water Pits A
	.byte $20 | $10, $A8, $AA; Downward Pipe (CAN'T go down)
	.byte $80 | $00, $B2, $B3, $0A; Ceiling
	.byte $60 | $00, $BC, $E2; Hilly Wall - Right Side
	.byte $00 | $03, $BC, $0A; Lower Right Hill Corner
	.byte $80 | $0A, $B8, $85, $06; Flat Land - Hilly
	.byte $80 | $00, $BF, $5F, $09; Hilly Wall
	.byte $00 | $00, $BF, $E9; Hilly Wall - Left Side
	.byte $60 | $0A, $B0, $0E; 30-Degree Hill & Water Pits A
	.byte $20 | $00, $BD, $C6; Upward Pipe (CAN go up)
	.byte $80 | $0D, $80, $50, $01; Hilly Wall
	.byte $80 | $0D, $88, $50, $01; Hilly Wall
	.byte $80 | $14, $84, $50, $01; Hilly Wall
	.byte $80 | $14, $8C, $50, $01; Hilly Wall
	.byte $80 | $0C, $34, $50, $01; Hilly Wall
	; Pointer on screen $0B
	.byte $E0 | $0B, $70 | $01, 50; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_6_W6_objects:
	.byte $43, $10, $18; Jumping Cheep-Cheep (2 jumps, down and right)
	.byte $43, $17, $18; Jumping Cheep-Cheep (2 jumps, down and right)
	.byte $A3, $18, $14; Red Piranha Plant (downward)
	.byte $29, $18, $0E; Spike
	.byte $42, $22, $0B; Jumping Cheep-Cheep (3 jumps, up and right)
	.byte $29, $23, $17; Spike
	.byte $A4, $2C, $18; Green Venus Fire Trap (upward)
	.byte $29, $2F, $09; Spike
	.byte $A7, $34, $0E; Red Venus Fire Trap (downward)
	.byte $77, $4D, $0F; Cheep-Cheep
	.byte $77, $47, $15; Cheep-Cheep
	.byte $77, $53, $11; Cheep-Cheep
	.byte $77, $51, $15; Cheep-Cheep
	.byte $77, $5E, $0F; Cheep-Cheep
	.byte $77, $63, $0D; Cheep-Cheep
	.byte $77, $6B, $12; Cheep-Cheep
	.byte $77, $70, $14; Cheep-Cheep
	.byte $77, $76, $0F; Cheep-Cheep
	.byte $77, $78, $16; Cheep-Cheep
	.byte $77, $7E, $12; Cheep-Cheep
	.byte $77, $8D, $0F; Cheep-Cheep
	.byte $A3, $80, $10; Red Piranha Plant (downward)
	.byte $A2, $84, $11; Red Piranha Plant (upward)
	.byte $A3, $88, $10; Red Piranha Plant (downward)
	.byte $A2, $8C, $12; Red Piranha Plant (upward)
	.byte $29, $A0, $0F; Spike
	.byte $29, $A6, $0F; Spike
	.byte $29, $A4, $0F; Spike
	.byte $A4, $A8, $10; Green Venus Fire Trap (upward)
	.byte $42, $AD, $0F; Jumping Cheep-Cheep (3 jumps, up and right)
	.byte $29, $BC, $09; Spike
	.byte $FF
; Dungeon__2_Boss_Room_W6
; Object Set 12
Dungeon__2_Boss_Room_W6_generators:
Dungeon__2_Boss_Room_W6_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_02 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $0F, $00, $82; Large Ice Blocks
	.byte $60 | $11, $00, $82; Large Ice Blocks
	.byte $60 | $13, $00, $82; Large Ice Blocks
	.byte $60 | $15, $00, $82; Large Ice Blocks
	.byte $60 | $17, $00, $82; Large Ice Blocks
	.byte $60 | $19, $00, $8F; Large Ice Blocks
	.byte $60 | $0F, $06, $1F; Ice Blocks
	.byte $60 | $0F, $16, $19; Ice Blocks
	.byte $60 | $10, $06, $84; Large Ice Blocks
	.byte $60 | $12, $06, $84; Large Ice Blocks
	.byte $60 | $14, $06, $84; Large Ice Blocks
	.byte $60 | $0F, $1F, $10; Ice Blocks
	.byte $60 | $10, $1F, $10; Ice Blocks
	.byte $60 | $11, $1F, $10; Ice Blocks
	.byte $60 | $12, $1F, $10; Ice Blocks
	.byte $60 | $13, $1F, $10; Ice Blocks
	.byte $60 | $14, $1F, $10; Ice Blocks
	.byte $60 | $15, $1F, $10; Ice Blocks
	.byte $60 | $16, $1F, $10; Ice Blocks
	.byte $60 | $17, $1F, $10; Ice Blocks
	.byte $60 | $18, $1F, $10; Ice Blocks
	.byte $60 | $15, $14, $10; Ice Blocks
	.byte $60 | $13, $18, $10; Ice Blocks
	.byte $60 | $16, $1B, $13; Ice Blocks
	.byte $FF
Dungeon__2_Boss_Room_W6_objects:
	.byte $4B, $1D, $24; Boom Boom
	.byte $FF
; Level_4_Bonus_Area_W6
; Object Set 13
Level_4_Bonus_Area_W6_generators:
Level_4_Bonus_Area_W6_header:
	.byte $97; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_12; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0D; Start action | Graphic set
	.byte $00 | $0A; Time | Music
	.byte $60 | $0E, $00, $4C, $2F; White Background
	.byte $60 | $19, $00, $21, $2F; Clouds B
	.byte $00 | $0E, $00, $07; Cloud Background C
	.byte $00 | $13, $06, $06; Cloud Background B
	.byte $20 | $16, $0C, $87; Coins
	.byte $20 | $18, $0C, $87; Coins
	.byte $00 | $0E, $12, $07; Cloud Background C
	.byte $20 | $14, $19, $83; Coins
	.byte $20 | $16, $16, $89; Coins
	.byte $20 | $18, $16, $89; Coins
	.byte $00 | $0F, $26, $07; Cloud Background C
	.byte $00 | $10, $2B, $07; Cloud Background C
	.byte $20 | $16, $21, $87; Coins
	.byte $20 | $18, $21, $87; Coins
	.byte $20 | $17, $2C, $93; Downward Pipe (CAN go down)
	; Pointer on screen $02
	.byte $E0 | $02, $00 | $02, 22; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_4_Bonus_Area_W6_objects:
	.byte $D3, $00, $12; Autoscrolling
	.byte $FF
; Level_7_Ending_W6
; Object Set 12
Level_7_Ending_W6_generators:
Level_7_Ending_W6_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $20 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $60 | $14, $03, $36; Frozen Coins
	.byte $60 | $15, $03, $36; Frozen Coins
	.byte $60 | $16, $03, $31; Frozen Coins
	.byte $60 | $17, $03, $31; Frozen Coins
	.byte $60 | $18, $03, $31; Frozen Coins
	.byte $60 | $19, $03, $36; Frozen Coins
	.byte $60 | $16, $08, $31; Frozen Coins
	.byte $60 | $17, $08, $31; Frozen Coins
	.byte $60 | $18, $08, $31; Frozen Coins
	.byte $00 | $1A, $00, $10, $30; Icy flat ground
	.byte $00 | $09, $03, $C2; Background Clouds
	.byte $20 | $00, $08, $D5; Upward Pipe (CAN'T go up)
	.byte $00 | $0D, $0B, $C2; Background Clouds
	.byte $00 | $15, $0C, $73; Snowy Platform
	.byte $00 | $18, $0B, $72; Snowy Platform
	.byte $20 | $16, $02, $0E; Invisible Coin
	.byte $40 | $00, $18, $09; Level Ending
	.byte $FF
Level_7_Ending_W6_objects:
	.byte $6E, $06, $17; Green Koopa Paratroopa (bounces)
	.byte $41, $28, $15; Goal Card
	.byte $FF
; Level_5_W6
; Object Set 3
Level_5_W6_generators:
Level_5_W6_header:
	.byte $99; Next Level
	.byte LEVEL1_SIZE_07 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_07; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_12; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $00, $00, $5F, $01; Hilly Wall
	.byte $60 | $00, $01, $EF; Hilly Wall - Right Side
	.byte $80 | $10, $00, $5A, $01; Hilly Wall
	.byte $60 | $10, $01, $E8; Hilly Wall - Right Side
	.byte $80 | $19, $02, $81, $28; Flat Land - Hilly
	.byte $80 | $00, $04, $5F, $07; Hilly Wall
	.byte $80 | $10, $04, $B0, $07; Ceiling
	.byte $00 | $00, $04, $EF; Hilly Wall - Left Side
	.byte $00 | $10, $04, $07; Lower Left Hill Corner
	.byte $60 | $03, $0B, $EC; Hilly Wall - Right Side
	.byte $00 | $10, $0B, $0A; Lower Right Hill Corner
	.byte $80 | $00, $0C, $B2, $02; Ceiling
	.byte $80 | $00, $0F, $5F, $08; Hilly Wall
	.byte $80 | $10, $0F, $B0, $08; Ceiling
	.byte $00 | $03, $0F, $EC; Hilly Wall - Left Side
	.byte $00 | $10, $0F, $07; Lower Left Hill Corner
	.byte $20 | $06, $02, $DF; Upward Pipe (CAN'T go up)
	.byte $80 | $00, $18, $B1, $1E; Ceiling
	.byte $60 | $02, $17, $ED; Hilly Wall - Right Side
	.byte $00 | $10, $17, $0A; Lower Right Hill Corner
	.byte $80 | $05, $1B, $89, $04; Flat Land - Hilly
	.byte $80 | $0F, $1B, $B1, $09; Ceiling
	.byte $00 | $06, $1B, $E9; Hilly Wall - Left Side
	.byte $60 | $07, $1F, $E5; Hilly Wall - Right Side
	.byte $00 | $05, $1B, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $10, $1B, $07; Lower Left Hill Corner
	.byte $60 | $00, $13, $EF; Hilly Wall - Right Side
	.byte $00 | $00, $16, $EF; Hilly Wall - Left Side
	.byte $00 | $10, $13, $0A; Lower Right Hill Corner
	.byte $00 | $10, $16, $07; Lower Left Hill Corner
	.byte $20 | $02, $1E, $10; Bricks
	.byte $20 | $03, $1E, $10; Bricks
	.byte $20 | $04, $1E, $10; Bricks
	.byte $20 | $00, $14, $DB; Upward Pipe (CAN'T go up)
	.byte $20 | $0B, $14, $CA; Upward Pipe (CAN go up)
	.byte $80 | $05, $2C, $89, $07; Flat Land - Hilly
	.byte $80 | $0D, $20, $81, $03; Flat Land - Hilly
	.byte $80 | $0D, $28, $81, $03; Flat Land - Hilly
	.byte $80 | $0F, $28, $B1, $0B; Ceiling
	.byte $00 | $07, $2C, $E5; Hilly Wall - Left Side
	.byte $00 | $0D, $24, $04; Upper Right Hill Corner - Hilly
	.byte $00 | $0D, $28, $01; Upper Left Hill Corner - Hilly
	.byte $60 | $0E, $24, $E1; Hilly Wall - Right Side
	.byte $00 | $0E, $28, $E1; Hilly Wall - Left Side
	.byte $00 | $10, $24, $0A; Lower Right Hill Corner
	.byte $00 | $10, $28, $07; Lower Left Hill Corner
	.byte $60 | $03, $20, $04; Horizontal Hill Strip
	.byte $60 | $03, $24, $04; Horizontal Hill Strip
	.byte $80 | $19, $2B, $51, $07; Hilly Wall
	.byte $20 | $03, $20, $82; Coins
	.byte $20 | $03, $24, $84; Coins
	.byte $20 | $03, $2A, $82; Coins
	.byte $20 | $02, $2E, $10; Bricks
	.byte $20 | $03, $2E, $10; Bricks
	.byte $20 | $04, $2E, $10; Bricks
	.byte $20 | $09, $26, $13; Bricks
	.byte $20 | $0B, $22, $13; Bricks
	.byte $20 | $16, $23, $01; '?' with leaf
	.byte $40 | $18, $20, $E4; White Turtle Bricks
	.byte $20 | $09, $26, $0B; Brick with 1-up
	.byte $80 | $00, $37, $BB, $0A; Ceiling
	.byte $00 | $02, $37, $E8; Hilly Wall - Left Side
	.byte $00 | $0B, $37, $07; Lower Left Hill Corner
	.byte $00 | $05, $33, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $06, $33, $E9; Hilly Wall - Right Side
	.byte $00 | $10, $33, $0A; Lower Right Hill Corner
	.byte $60 | $15, $31, $63; 30 Degree Hill - Down/Left
	.byte $80 | $15, $33, $85, $0B; Flat Land - Hilly
	.byte $00 | $15, $3F, $53; 45 Degree Hill - Down/Right
	.byte $80 | $19, $3F, $51, $03; Hilly Wall
	.byte $40 | $14, $39, $E0; White Turtle Bricks
	.byte $40 | $14, $3D, $E0; White Turtle Bricks
	.byte $80 | $00, $42, $5F, $07; Hilly Wall
	.byte $80 | $00, $4A, $B1, $08; Ceiling
	.byte $80 | $10, $42, $B0, $07; Ceiling
	.byte $60 | $02, $49, $ED; Hilly Wall - Right Side
	.byte $00 | $0C, $42, $E3; Hilly Wall - Left Side
	.byte $00 | $10, $42, $07; Lower Left Hill Corner
	.byte $00 | $10, $49, $0A; Lower Right Hill Corner
	.byte $80 | $09, $4D, $85, $04; Flat Land - Hilly
	.byte $80 | $0F, $4D, $B1, $04; Ceiling
	.byte $00 | $0A, $4D, $E5; Hilly Wall - Left Side
	.byte $00 | $09, $4D, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $10, $4D, $07; Lower Left Hill Corner
	.byte $80 | $19, $43, $81, $11; Flat Land - Hilly
	.byte $20 | $06, $4E, $11; Bricks
	.byte $20 | $07, $4E, $11; Bricks
	.byte $20 | $08, $4D, $12; Bricks
	.byte $40 | $16, $46, $E0; White Turtle Bricks
	.byte $40 | $17, $46, $E0; White Turtle Bricks
	.byte $40 | $18, $46, $E0; White Turtle Bricks
	.byte $40 | $18, $4C, $E0; White Turtle Bricks
	.byte $20 | $06, $4D, $40; Wooden blocks
	.byte $20 | $07, $4D, $40; Wooden blocks
	.byte $60 | $00, $52, $E0; Hilly Wall - Right Side
	.byte $00 | $01, $52, $0A; Lower Right Hill Corner
	.byte $80 | $00, $55, $5F, $1A; Hilly Wall
	.byte $80 | $10, $55, $B0, $15; Ceiling
	.byte $00 | $00, $55, $EF; Hilly Wall - Left Side
	.byte $60 | $0A, $51, $E5; Hilly Wall - Right Side
	.byte $00 | $09, $51, $04; Upper Right Hill Corner - Hilly
	.byte $00 | $10, $51, $0A; Lower Right Hill Corner
	.byte $00 | $10, $55, $07; Lower Left Hill Corner
	.byte $80 | $19, $55, $51, $06; Hilly Wall
	.byte $80 | $13, $5C, $87, $03; Flat Land - Hilly
	.byte $60 | $13, $54, $0A; Steps A
	.byte $20 | $00, $53, $C5; Upward Pipe (CAN go up)
	.byte $20 | $05, $52, $40; Wooden blocks
	.byte $20 | $06, $52, $40; Wooden blocks
	.byte $20 | $07, $52, $10; Bricks
	.byte $20 | $08, $52, $10; Bricks
	.byte $20 | $09, $52, $42; Wooden blocks
	.byte $20 | $15, $52, $10; Bricks
	.byte $20 | $16, $52, $10; Bricks
	.byte $20 | $17, $52, $10; Bricks
	.byte $20 | $18, $52, $10; Bricks
	.byte $80 | $18, $60, $52, $04; Hilly Wall
	.byte $00 | $13, $60, $54; 45 Degree Hill - Down/Right
	.byte $60 | $18, $64, $E2; Hilly Wall - Right Side
	.byte $00 | $19, $67, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $1A, $67, $E0; Hilly Wall - Left Side
	.byte $80 | $19, $68, $81, $02; Flat Land - Hilly
	.byte $80 | $10, $6B, $5A, $04; Hilly Wall
	.byte $00 | $11, $6B, $E7; Hilly Wall - Left Side
	.byte $20 | $18, $65, $A2; Downward Pipe (CAN'T go down)
	.byte $60 | $06, $6F, $E5; Hilly Wall - Right Side
	.byte $20 | $17, $69, $E1; Rightward Pipe (CAN go in)
	.byte $80 | $17, $6B, $51, $00; Hilly Wall
	; Pointer on screen $01
	.byte $E0 | $01, $60 | $01, 66; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $05
	.byte $E0 | $05, $60 | $01, 20; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $06
	.byte $E0 | $06, $60 | $03, 209; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_5_W6_objects:
	.byte $40, $0C, $18; Buster Beetle
	.byte $40, $0F, $18; Buster Beetle
	.byte $40, $1E, $18; Buster Beetle
	.byte $40, $26, $18; Buster Beetle
	.byte $40, $37, $14; Buster Beetle
	.byte $40, $3B, $14; Buster Beetle
	.byte $6C, $4A, $18; Green Koopa Troopa
	.byte $40, $50, $18; Buster Beetle
	.byte $33, $50, $08; Nipper Plant
	.byte $33, $51, $08; Nipper Plant
	.byte $A6, $65, $18; Red Venus Fire Trap (upward)
	.byte $FF
; Level_9_W6
; Object Set 3
Level_9_W6_generators:
Level_9_W6_header:
	.byte $9A; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_07; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_12; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $03; Start action | Graphic set
	.byte $00 | $02; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $10, $02, $3A, $73; Water
	.byte $80 | $00, $00, $5F, $01; Hilly Wall
	.byte $80 | $10, $00, $5A, $01; Hilly Wall
	.byte $80 | $1A, $02, $50, $06; Hilly Wall
	.byte $60 | $00, $01, $EF; Hilly Wall - Right Side
	.byte $60 | $10, $01, $F2; Dark Underground Wall - Right Side
	.byte $00 | $13, $02, $96; 45 Degree Underwater Hill - Down/Right
	.byte $80 | $1A, $09, $90, $0D; Flat Land - Underwater
	.byte $80 | $00, $08, $5D, $0B; Hilly Wall
	.byte $00 | $00, $08, $ED; Hilly Wall - Left Side
	.byte $00 | $0E, $08, $74; 45 Degree Hill - Up/Left
	.byte $00 | $10, $0A, $B2; 45 Degree Underwater Hill - Up/Left
	.byte $80 | $0E, $0D, $C4, $06; Underwater Ceiling
	.byte $20 | $00, $04, $D1; Upward Pipe (CAN'T go up)
	.byte $80 | $00, $14, $B1, $27; Ceiling
	.byte $60 | $02, $13, $ED; Hilly Wall - Right Side
	.byte $60 | $10, $13, $F1; Dark Underground Wall - Right Side
	.byte $00 | $12, $13, $0B; Lower Right Hill Corner - UnderWater
	.byte $00 | $1A, $16, $05; Upper Right Hill Corner - UnderWater
	.byte $80 | $0B, $18, $85, $09; Flat Land - Hilly
	.byte $80 | $10, $18, $C0, $05; Underwater Ceiling
	.byte $80 | $11, $1E, $C3, $03; Underwater Ceiling
	.byte $00 | $11, $1E, $F2; Dark Underground Wall - Left Side
	.byte $00 | $14, $1E, $08; Lower Left Hill Corner - UnderWater
	.byte $00 | $0B, $18, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $10, $18, $08; Lower Left Hill Corner - UnderWater
	.byte $00 | $0C, $18, $E3; Hilly Wall - Left Side
	.byte $20 | $11, $1C, $D3; Upward Pipe (CAN'T go up)
	.byte $20 | $09, $1B, $40; Wooden blocks
	.byte $20 | $0A, $1B, $40; Wooden blocks
	.byte $20 | $0F, $17, $40; Wooden blocks
	.byte $20 | $0A, $1C, $05; Muncher
	.byte $20 | $0A, $1D, $05; Muncher
	.byte $20 | $0A, $1E, $05; Muncher
	.byte $20 | $0A, $1F, $05; Muncher
	.byte $60 | $0C, $21, $E3; Hilly Wall - Right Side
	.byte $00 | $0B, $21, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $10, $21, $F3; Dark Underground Wall - Right Side
	.byte $00 | $14, $21, $0A; Lower Right Hill Corner
	.byte $80 | $0D, $26, $83, $06; Flat Land - Hilly
	.byte $00 | $0D, $26, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $0E, $26, $E1; Hilly Wall - Left Side
	.byte $00 | $10, $26, $F3; Dark Underground Wall - Left Side
	.byte $00 | $14, $26, $08; Lower Left Hill Corner - UnderWater
	.byte $00 | $14, $27, $0B; Lower Right Hill Corner - UnderWater
	.byte $60 | $11, $27, $F2; Dark Underground Wall - Right Side
	.byte $80 | $10, $28, $C0, $0F; Underwater Ceiling
	.byte $80 | $0B, $2D, $84, $04; Flat Land - Hilly
	.byte $00 | $0B, $2D, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $0C, $2D, $E0; Hilly Wall - Left Side
	.byte $80 | $13, $2A, $90, $0E; Flat Land - Underwater
	.byte $80 | $14, $2A, $C0, $0E; Underwater Ceiling
	.byte $00 | $13, $2A, $02; Upper Left Hill Corner - UnderWater
	.byte $00 | $14, $2A, $08; Lower Left Hill Corner - UnderWater
	.byte $80 | $1A, $24, $90, $05; Flat Land - Underwater
	.byte $00 | $1A, $24, $01; Upper Left Hill Corner - Hilly
	.byte $20 | $02, $23, $D2; Upward Pipe (CAN'T go up)
	.byte $20 | $09, $20, $40; Wooden blocks
	.byte $20 | $0A, $20, $40; Wooden blocks
	.byte $20 | $0B, $26, $40; Wooden blocks
	.byte $20 | $0C, $26, $40; Wooden blocks
	.byte $20 | $0C, $27, $05; Muncher
	.byte $20 | $0C, $28, $05; Muncher
	.byte $20 | $0C, $29, $05; Muncher
	.byte $20 | $0C, $2A, $05; Muncher
	.byte $20 | $0C, $2B, $05; Muncher
	.byte $20 | $0C, $2C, $05; Muncher
	.byte $20 | $17, $28, $A2; Downward Pipe (CAN'T go down)
	.byte $40 | $07, $2F, $01; Note Block with Flower
	.byte $80 | $00, $3C, $BD, $09; Ceiling
	.byte $00 | $02, $3C, $EB; Hilly Wall - Left Side
	.byte $00 | $0D, $3C, $07; Lower Left Hill Corner
	.byte $80 | $13, $39, $97, $02; Flat Land - Underwater
	.byte $80 | $0D, $32, $82, $00; Flat Land - Hilly
	.byte $80 | $0B, $33, $84, $01; Flat Land - Hilly
	.byte $80 | $0D, $35, $82, $00; Flat Land - Hilly
	.byte $80 | $0B, $36, $84, $01; Flat Land - Hilly
	.byte $00 | $0B, $31, $04; Upper Right Hill Corner - Hilly
	.byte $00 | $0B, $33, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $0B, $34, $04; Upper Right Hill Corner - Hilly
	.byte $00 | $0B, $36, $01; Upper Left Hill Corner - Hilly
	.byte $60 | $0C, $31, $E0; Hilly Wall - Right Side
	.byte $00 | $0C, $33, $E0; Hilly Wall - Left Side
	.byte $60 | $0C, $34, $E0; Hilly Wall - Right Side
	.byte $00 | $0C, $36, $E0; Hilly Wall - Left Side
	.byte $00 | $0B, $37, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $0C, $37, $E3; Hilly Wall - Right Side
	.byte $00 | $10, $37, $0B; Lower Right Hill Corner - UnderWater
	.byte $00 | $13, $3C, $96; 45 Degree Underwater Hill - Down/Right
	.byte $80 | $1A, $3C, $50, $06; Hilly Wall
	.byte $00 | $15, $39, $F4; Dark Underground Wall - Left Side
	.byte $80 | $1A, $36, $90, $02; Flat Land - Underwater
	.byte $20 | $0C, $32, $05; Muncher
	.byte $20 | $0C, $35, $05; Muncher
	.byte $20 | $02, $33, $D6; Upward Pipe (CAN'T go up)
	.byte $20 | $15, $31, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $18, $36, $B1; Downward Pipe (CAN go down, ignores pointers)
	.byte $80 | $00, $46, $B7, $09; Ceiling
	.byte $60 | $02, $4F, $E4; Hilly Wall - Right Side
	.byte $00 | $07, $4F, $0A; Lower Right Hill Corner
	.byte $60 | $08, $45, $E4; Hilly Wall - Right Side
	.byte $00 | $0D, $45, $0A; Lower Right Hill Corner
	.byte $80 | $0E, $4A, $81, $02; Flat Land - Hilly
	.byte $80 | $10, $4A, $C0, $13; Underwater Ceiling
	.byte $00 | $0E, $4A, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $0E, $4C, $04; Upper Right Hill Corner - Hilly
	.byte $00 | $0F, $4A, $F0; Dark Underground Wall - Left Side
	.byte $00 | $10, $4A, $08; Lower Left Hill Corner - UnderWater
	.byte $80 | $0F, $4D, $80, $04; Flat Land - Hilly
	.byte $80 | $1A, $43, $90, $16; Flat Land - Underwater
	.byte $20 | $0D, $4C, $40; Wooden blocks
	.byte $20 | $10, $49, $40; Wooden blocks
	.byte $20 | $0E, $4D, $05; Muncher
	.byte $20 | $0E, $4E, $05; Muncher
	.byte $20 | $0E, $4F, $05; Muncher
	.byte $20 | $17, $46, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $11, $4C, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $18, $4C, $A1; Downward Pipe (CAN'T go down)
	.byte $80 | $00, $50, $B1, $1F; Ceiling
	.byte $80 | $0B, $52, $84, $01; Flat Land - Hilly
	.byte $00 | $0B, $52, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $0B, $53, $04; Upper Right Hill Corner - Hilly
	.byte $00 | $0C, $52, $E2; Hilly Wall - Left Side
	.byte $60 | $0C, $53, $E0; Hilly Wall - Right Side
	.byte $80 | $0D, $54, $82, $07; Flat Land - Hilly
	.byte $80 | $0B, $5C, $84, $01; Flat Land - Hilly
	.byte $00 | $0B, $5C, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $0B, $5D, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $0C, $5D, $E3; Hilly Wall - Right Side
	.byte $00 | $10, $5D, $0B; Lower Right Hill Corner - UnderWater
	.byte $00 | $1A, $59, $05; Upper Right Hill Corner - UnderWater
	.byte $80 | $19, $5C, $91, $06; Flat Land - Underwater
	.byte $00 | $19, $5C, $02; Upper Left Hill Corner - UnderWater
	.byte $00 | $1A, $5C, $F0; Dark Underground Wall - Left Side
	.byte $20 | $02, $53, $D2; Upward Pipe (CAN'T go up)
	.byte $20 | $11, $50, $D2; Upward Pipe (CAN'T go up)
	.byte $20 | $16, $50, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $57, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $02, $5B, $D2; Upward Pipe (CAN'T go up)
	.byte $20 | $05, $52, $0D; Brick with P-Switch
	.byte $20 | $07, $50, $0E; Invisible Coin
	.byte $40 | $09, $5F, $01; Note Block with Flower
	.byte $20 | $0C, $54, $05; Muncher
	.byte $20 | $0C, $55, $05; Muncher
	.byte $20 | $0E, $50, $05; Muncher
	.byte $20 | $0C, $56, $05; Muncher
	.byte $20 | $0C, $57, $05; Muncher
	.byte $20 | $0C, $58, $05; Muncher
	.byte $20 | $0C, $59, $05; Muncher
	.byte $20 | $0C, $5A, $05; Muncher
	.byte $20 | $0C, $5B, $05; Muncher
	.byte $20 | $0F, $5E, $40; Wooden blocks
	.byte $20 | $09, $59, $40; Wooden blocks
	.byte $20 | $0D, $51, $40; Wooden blocks
	.byte $20 | $0E, $51, $40; Wooden blocks
	.byte $80 | $0B, $60, $84, $01; Flat Land - Hilly
	.byte $00 | $0B, $60, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $0B, $61, $04; Upper Right Hill Corner - Hilly
	.byte $00 | $0C, $60, $E3; Hilly Wall - Left Side
	.byte $60 | $0C, $61, $E0; Hilly Wall - Right Side
	.byte $80 | $0D, $62, $82, $01; Flat Land - Hilly
	.byte $80 | $0B, $64, $84, $06; Flat Land - Hilly
	.byte $80 | $0B, $6C, $84, $03; Flat Land - Hilly
	.byte $80 | $10, $6C, $B0, $03; Ceiling
	.byte $00 | $0B, $64, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $0B, $6F, $04; Upper Right Hill Corner - Hilly
	.byte $00 | $0C, $64, $E0; Hilly Wall - Left Side
	.byte $80 | $10, $60, $C0, $0A; Underwater Ceiling
	.byte $00 | $10, $60, $08; Lower Left Hill Corner - UnderWater
	.byte $00 | $10, $6F, $0B; Lower Right Hill Corner - UnderWater
	.byte $00 | $19, $62, $05; Upper Right Hill Corner - UnderWater
	.byte $60 | $1A, $62, $F0; Dark Underground Wall - Right Side
	.byte $00 | $1A, $68, $02; Upper Left Hill Corner - UnderWater
	.byte $80 | $1A, $69, $90, $00; Flat Land - Underwater
	.byte $80 | $1A, $6A, $50, $12; Hilly Wall
	.byte $00 | $0B, $6A, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $0C, $6A, $E3; Hilly Wall - Right Side
	.byte $00 | $10, $6A, $0B; Lower Right Hill Corner - UnderWater
	.byte $00 | $0B, $6C, $01; Upper Left Hill Corner - Hilly
	.byte $60 | $0C, $6F, $E3; Hilly Wall - Right Side
	.byte $20 | $02, $6C, $C1; Upward Pipe (CAN go up)
	.byte $20 | $09, $65, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $08, $6C, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $11, $65, $D5; Upward Pipe (CAN'T go up)
	.byte $20 | $06, $61, $42; Wooden blocks
	.byte $20 | $0C, $62, $05; Muncher
	.byte $20 | $0C, $63, $05; Muncher
	.byte $00 | $10, $6C, $08; Lower Left Hill Corner - UnderWater
	.byte $80 | $00, $70, $B6, $07; Ceiling
	.byte $00 | $02, $70, $E3; Hilly Wall - Left Side
	.byte $00 | $06, $70, $07; Lower Left Hill Corner
	.byte $80 | $00, $78, $5F, $07; Hilly Wall
	.byte $80 | $10, $78, $5A, $07; Hilly Wall
	.byte $00 | $0C, $77, $6D; 45 Degree Hill - Down/Left
	.byte $00 | $10, $73, $A9; 45 Degree Underwater Hill - Down/Left
	.byte $00 | $07, $78, $E4; Hilly Wall - Left Side
	.byte $80 | $10, $1C, $50, $01; Hilly Wall
	.byte $80 | $01, $23, $50, $01; Hilly Wall
	.byte $80 | $1A, $28, $50, $01; Hilly Wall
	.byte $60 | $1A, $29, $E0; Hilly Wall - Right Side
	.byte $80 | $01, $33, $50, $01; Hilly Wall
	.byte $80 | $14, $31, $50, $01; Hilly Wall
	.byte $80 | $1A, $36, $50, $01; Hilly Wall
	.byte $00 | $1A, $36, $E0; Hilly Wall - Left Side
	.byte $80 | $10, $4C, $50, $01; Hilly Wall
	.byte $80 | $1A, $4C, $50, $01; Hilly Wall
	.byte $80 | $1A, $46, $50, $01; Hilly Wall
	.byte $80 | $01, $5B, $50, $01; Hilly Wall
	.byte $80 | $01, $53, $50, $01; Hilly Wall
	.byte $80 | $10, $50, $50, $01; Hilly Wall
	.byte $80 | $1A, $50, $50, $01; Hilly Wall
	.byte $80 | $1A, $57, $50, $01; Hilly Wall
	.byte $80 | $0B, $65, $50, $01; Hilly Wall
	.byte $80 | $0B, $6C, $50, $01; Hilly Wall
	.byte $80 | $10, $65, $50, $01; Hilly Wall
	.byte $80 | $01, $6C, $50, $01; Hilly Wall
	.byte $00 | $0B, $6C, $E4; Hilly Wall - Left Side
	; Pointer on screen $03
	.byte $E0 | $03, $00 | $02, 131; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $06
	.byte $E0 | $06, $60 | $01, 67; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_9_W6_objects:
	.byte $77, $0D, $16; Cheep-Cheep
	.byte $6A, $17, $14; Bloober Nanny
	.byte $66, $1C, $14; Downward Current
	.byte $A1, $23, $04; Green Piranha Plant (downward)
	.byte $63, $24, $16; Big Bertha (underwater)
	.byte $65, $28, $17; Upward Current
	.byte $66, $31, $16; Downward Current
	.byte $A3, $33, $08; Red Piranha Plant (downward)
	.byte $77, $44, $14; Cheep-Cheep
	.byte $6A, $4E, $14; Bloober Nanny
	.byte $65, $57, $18; Upward Current
	.byte $77, $58, $14; Cheep-Cheep
	.byte $A0, $65, $09; Green Piranha Plant (upward)
	.byte $66, $65, $16; Downward Current
	.byte $A4, $6C, $08; Green Venus Fire Trap (upward)
	.byte $63, $6C, $13; Big Bertha (underwater)
	.byte $FF
; Dungeon__3_Falling_Room_W6
; Object Set 2
Dungeon__3_Falling_Room_W6_generators:
Dungeon__3_Falling_Room_W6_header:
	.byte $9B; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $01, $00, $2F, $0F; Dark Dungeon Background
	.byte $60 | $11, $00, $27, $0F; Dark Dungeon Background
	.byte $00 | $01, $00, $5F; Dark dungeon background
	.byte $00 | $00, $00, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $07, $01, $93; Dungeon Lamps (Note: extends to ceiling)
	.byte $00 | $0D, $06, $61; Dungeon windows
	.byte $00 | $11, $04, $62; Dungeon windows
	.byte $00 | $14, $02, $73; Long dungeon windows
	.byte $00 | $09, $0E, $00; Door
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $08, 153; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__3_Falling_Room_W6_objects:
	.byte $D3, $08, $40; Autoscrolling
	.byte $2F, $04, $14; Boo Buddy
	.byte $2F, $0C, $14; Boo Buddy
	.byte $2F, $0D, $17; Boo Buddy
	.byte $FF
; Dungeon__1_Lonely_Room_W7
; Object Set 2
Dungeon__1_Lonely_Room_W7_generators:
Dungeon__1_Lonely_Room_W7_header:
	.byte $A1; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $02, $00, $2F, $4F; Dark Dungeon Background
	.byte $60 | $12, $00, $26, $4F; Dark Dungeon Background
	.byte $00 | $02, $00, $5F; Dark dungeon background
	.byte $00 | $02, $10, $5F; Dark dungeon background
	.byte $00 | $02, $20, $5F; Dark dungeon background
	.byte $00 | $02, $30, $5F; Dark dungeon background
	.byte $00 | $02, $40, $5F; Dark dungeon background
	.byte $00 | $00, $00, $E1, $4F; Horizontally oriented X-blocks
	.byte $00 | $02, $00, $F0, $16; Vertically oriented X-blocks
	.byte $00 | $09, $04, $72; Long dungeon windows
	.byte $00 | $14, $0B, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $15, $0B, $02; Rotodisc block
	.byte $00 | $14, $06, $04; Hot Foot Candle
	.byte $00 | $02, $0F, $10; Bottom of background with pillars A
	.byte $20 | $02, $12, $C2; Upward Pipe (CAN go up)
	.byte $00 | $05, $17, $62; Dungeon windows
	.byte $00 | $0B, $15, $73; Long dungeon windows
	.byte $00 | $14, $11, $04; Hot Foot Candle
	.byte $00 | $13, $14, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $12, $15, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $13, $15, $02; Rotodisc block
	.byte $00 | $16, $1A, $B5; Stretch platform
	.byte $00 | $02, $23, $10; Bottom of background with pillars A
	.byte $00 | $09, $27, $72; Long dungeon windows
	.byte $00 | $14, $25, $04; Hot Foot Candle
	.byte $00 | $14, $2B, $04; Hot Foot Candle
	.byte $00 | $17, $28, $00; Door
	.byte $00 | $15, $2F, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $13, $30, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $15, $30, $02; Rotodisc block
	.byte $00 | $02, $33, $10; Bottom of background with pillars A
	.byte $00 | $14, $35, $04; Hot Foot Candle
	.byte $00 | $14, $3E, $04; Hot Foot Candle
	.byte $00 | $16, $37, $B5; Stretch platform
	.byte $00 | $06, $3B, $63; Dungeon windows
	.byte $00 | $13, $45, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $14, $45, $02; Rotodisc block
	.byte $00 | $14, $4A, $04; Hot Foot Candle
	.byte $00 | $17, $4D, $00; Door
	.byte $00 | $00, $4F, $EF, $30; Horizontally oriented X-blocks
	.byte $00 | $10, $4F, $E8, $30; Horizontally oriented X-blocks
	.byte $60 | $11, $5D, $37, $15; Blank Background (used to block out stuff)
	.byte $20 | $17, $6C, $B1; Downward Pipe (CAN go down, ignores pointers)
	.byte $20 | $17, $71, $E2; Rightward Pipe (CAN go in)
	; Pointer on screen $01
	.byte $E0 | $01, $60 | $01, 149; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $02
	.byte $E0 | $02, $30 | $08, 225; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $04
	.byte $E0 | $04, $60 | $08, 83; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $06
	.byte $E0 | $06, $00 | $02, 22; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $07
	.byte $E0 | $07, $30 | $04, 100; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__1_Lonely_Room_W7_objects:
	.byte $FF
; Level_1_W7
; Object Set 8
Level_1_W7_generators:
Level_1_W7_header:
	.byte $A2; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_VERTICAL | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $08; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $00 | $00, $00, $0C; Background for pipe levels
	.byte $20 | $00, $00, $4F; Wooden blocks
	.byte $20 | $01, $00, $40; Wooden blocks
	.byte $20 | $02, $00, $40; Wooden blocks
	.byte $20 | $03, $00, $40; Wooden blocks
	.byte $20 | $04, $00, $40; Wooden blocks
	.byte $20 | $05, $00, $40; Wooden blocks
	.byte $20 | $06, $00, $40; Wooden blocks
	.byte $20 | $07, $00, $40; Wooden blocks
	.byte $20 | $08, $00, $40; Wooden blocks
	.byte $20 | $09, $00, $40; Wooden blocks
	.byte $20 | $0A, $00, $40; Wooden blocks
	.byte $20 | $0B, $00, $40; Wooden blocks
	.byte $20 | $0C, $00, $40; Wooden blocks
	.byte $20 | $0D, $00, $40; Wooden blocks
	.byte $20 | $0E, $00, $42; Wooden blocks
	.byte $20 | $01, $0F, $40; Wooden blocks
	.byte $20 | $02, $0F, $40; Wooden blocks
	.byte $20 | $03, $0F, $40; Wooden blocks
	.byte $20 | $04, $0F, $40; Wooden blocks
	.byte $20 | $05, $0F, $40; Wooden blocks
	.byte $20 | $06, $0F, $40; Wooden blocks
	.byte $20 | $07, $0F, $40; Wooden blocks
	.byte $20 | $08, $0F, $40; Wooden blocks
	.byte $20 | $09, $0F, $40; Wooden blocks
	.byte $20 | $0A, $0D, $42; Wooden blocks
	.byte $20 | $0B, $0D, $42; Wooden blocks
	.byte $20 | $0C, $0D, $42; Wooden blocks
	.byte $20 | $0D, $0D, $42; Wooden blocks
	.byte $20 | $0E, $0F, $40; Wooden blocks
	.byte $20 | $00, $10, $40; Wooden blocks
	.byte $20 | $01, $10, $40; Wooden blocks
	.byte $20 | $02, $10, $4F; Wooden blocks
	.byte $20 | $03, $10, $4F; Wooden blocks
	.byte $20 | $00, $1F, $40; Wooden blocks
	.byte $20 | $01, $1F, $40; Wooden blocks
	.byte $20 | $0A, $04, $41; Wooden blocks
	.byte $20 | $0B, $04, $41; Wooden blocks
	.byte $20 | $0C, $04, $41; Wooden blocks
	.byte $20 | $0D, $04, $41; Wooden blocks
	.byte $20 | $0E, $04, $41; Wooden blocks
	.byte $20 | $0A, $07, $41; Wooden blocks
	.byte $20 | $0B, $07, $41; Wooden blocks
	.byte $20 | $0C, $07, $41; Wooden blocks
	.byte $20 | $0D, $07, $41; Wooden blocks
	.byte $20 | $0E, $07, $41; Wooden blocks
	.byte $20 | $0A, $0A, $41; Wooden blocks
	.byte $20 | $0B, $0A, $41; Wooden blocks
	.byte $20 | $0C, $0A, $41; Wooden blocks
	.byte $20 | $0D, $0A, $41; Wooden blocks
	.byte $20 | $0E, $0A, $41; Wooden blocks
	.byte $20 | $0C, $14, $83; Coins
	.byte $20 | $0D, $14, $83; Coins
	.byte $20 | $0E, $12, $85; Coins
	.byte $20 | $00, $22, $85; Coins
	.byte $20 | $01, $22, $85; Coins
	.byte $20 | $02, $22, $85; Coins
	.byte $20 | $00, $0D, $C5; Upward Pipe (CAN go up)
	.byte $20 | $05, $06, $80; Coins
	.byte $20 | $05, $09, $80; Coins
	.byte $20 | $06, $05, $80; Coins
	.byte $20 | $06, $07, $81; Coins
	.byte $20 | $06, $0A, $80; Coins
	.byte $20 | $02, $09, $0F; Invisible 1-up
	.byte $00 | $02, $1D, $14; Double-ended pipe
	.byte $00 | $04, $14, $32; Leftward pipe
	.byte $00 | $09, $11, $27; Rightward pipe
	.byte $00 | $05, $12, $18; Double-ended pipe
	.byte $00 | $0A, $10, $18; Double-ended pipe
	.byte $00 | $0A, $18, $18; Double-ended pipe
	.byte $00 | $03, $21, $27; Rightward pipe
	.byte $20 | $0B, $14, $83; Coins
	.byte $20 | $0B, $1D, $41; Wooden blocks
	.byte $20 | $00, $2A, $41; Wooden blocks
	.byte $00 | $01, $24, $15; Double-ended pipe
	.byte $00 | $05, $26, $18; Double-ended pipe
	.byte $00 | $06, $29, $55; Small Vertical background pipe
	.byte $20 | $05, $2C, $60; Note Blocks - movable two directions
	.byte $40 | $09, $20, $22; Leftward Pipe (CAN'T go in)
	.byte $20 | $09, $2E, $A7; Downward Pipe (CAN'T go down)
	.byte $20 | $0C, $2B, $61; Note Blocks - movable two directions
	.byte $00 | $0E, $23, $22; Rightward pipe
	.byte $00 | $0E, $26, $31; Leftward pipe
	.byte $00 | $01, $35, $22; Rightward pipe
	.byte $00 | $01, $38, $31; Leftward pipe
	.byte $20 | $02, $3E, $F1; Rightward Pipe (CAN'T go in)
	.byte $20 | $04, $3C, $F3; Rightward Pipe (CAN'T go in)
	.byte $20 | $06, $3A, $F5; Rightward Pipe (CAN'T go in)
	.byte $00 | $04, $32, $46; Downward background pipe
	.byte $00 | $06, $34, $44; Downward background pipe
	.byte $60 | $0A, $30, $96; Double Ended Small Horizontal Pipe
	.byte $60 | $0A, $38, $97; Double Ended Small Horizontal Pipe
	.byte $60 | $00, $45, $94; Double Ended Small Horizontal Pipe
	.byte $00 | $01, $45, $62; Rightward background pipe
	.byte $00 | $01, $48, $72; Leftward background pipe
	.byte $20 | $02, $4C, $31; Bricks with single coins
	.byte $20 | $02, $4E, $0F; Invisible 1-up
	.byte $00 | $05, $41, $85; Small Horizontal background pipe
	.byte $00 | $07, $41, $83; Small Horizontal background pipe
	.byte $00 | $06, $4A, $21; Rightward pipe
	.byte $00 | $06, $4C, $31; Leftward pipe
	.byte $20 | $09, $4A, $13; Bricks
	.byte $20 | $0A, $47, $60; Note Blocks - movable two directions
	.byte $20 | $09, $4C, $04; '?' with Single coin
	.byte $20 | $0C, $49, $01; '?' with Leaf
	.byte $20 | $0C, $4E, $20; '?' blocks with single coins
	.byte $20 | $0E, $37, $40; Wooden blocks
	.byte $00 | $0D, $42, $14; Double-ended pipe
	.byte $00 | $0D, $49, $25; Rightward pipe
	.byte $00 | $0E, $48, $1A; Double-ended pipe
	.byte $00 | $0E, $4E, $1A; Double-ended pipe
	.byte $00 | $02, $56, $17; Double-ended pipe
	.byte $20 | $05, $5B, $22; '?' blocks with single coins
	.byte $00 | $04, $53, $46; Downward background pipe
	.byte $00 | $09, $5C, $14; Double-ended pipe
	.byte $00 | $0D, $54, $28; Rightward pipe
	.byte $20 | $01, $5D, $0F; Invisible 1-up
	.byte $00 | $01, $6A, $61; Rightward background pipe
	.byte $00 | $01, $6C, $71; Leftward background pipe
	.byte $00 | $0E, $53, $16; Double-ended pipe
	.byte $00 | $04, $68, $17; Double-ended pipe
	.byte $00 | $05, $6C, $17; Double-ended pipe
	.byte $40 | $06, $60, $22; Leftward Pipe (CAN'T go in)
	.byte $20 | $06, $68, $F7; Rightward Pipe (CAN'T go in)
	.byte $00 | $08, $60, $2F; Rightward pipe
	.byte $00 | $0C, $62, $63; Rightward background pipe
	.byte $00 | $0B, $66, $46; Downward background pipe
	.byte $00 | $0C, $68, $72; Leftward background pipe
	.byte $20 | $01, $72, $22; '?' blocks with single coins
	.byte $60 | $01, $79, $95; Double Ended Small Horizontal Pipe
	.byte $60 | $05, $72, $93; Double Ended Small Horizontal Pipe
	.byte $00 | $04, $78, $62; Rightward background pipe
	.byte $00 | $04, $7B, $72; Leftward background pipe
	.byte $60 | $09, $78, $93; Double Ended Small Horizontal Pipe
	.byte $20 | $0A, $70, $4F; Wooden blocks
	.byte $20 | $0B, $70, $4F; Wooden blocks
	.byte $20 | $0C, $70, $4F; Wooden blocks
	.byte $20 | $0D, $70, $4F; Wooden blocks
	.byte $20 | $0E, $70, $4F; Wooden blocks
	.byte $00 | $04, $12, $00; Upper-left corner of curved pipe
	.byte $00 | $09, $10, $00; Upper-left corner of curved pipe
	.byte $00 | $09, $18, $01; Upper-right corner of curved pipe
	.byte $00 | $03, $20, $02; Lower-left corner of curved pipe
	.byte $00 | $03, $28, $03; Lower-right corner of curved pipe
	.byte $00 | $0D, $48, $00; Upper-left corner of curved pipe
	.byte $00 | $0D, $4E, $01; Upper-right corner of curved pipe
	.byte $00 | $0D, $53, $00; Upper-left corner of curved pipe
	.byte $00 | $0D, $5C, $03; Lower-right corner of curved pipe
	; Pointer on screen $00
	.byte $E0 | $00, $70 | $03, 18; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_1_W7_objects:
	.byte $6F, $09, $07; Red Koopa Paratroopa
	.byte $6C, $02, $10; Green Koopa Troopa
	.byte $6C, $04, $10; Green Koopa Troopa
	.byte $A2, $0E, $27; Red Piranha Plant (upward)
	.byte $57, $07, $2C; Rightward Piranha Plant
	.byte $56, $0E, $2F; Leftward Piranha Plant
	.byte $56, $0A, $33; Leftward Piranha Plant
	.byte $6D, $01, $36; Red Koopa Troopa
	.byte $6F, $04, $43; Red Koopa Paratroopa
	.byte $6D, $0C, $48; Red Koopa Troopa
	.byte $6D, $07, $57; Red Koopa Troopa
	.byte $A2, $08, $5E; Red Piranha Plant (upward)
	.byte $57, $02, $60; Rightward Piranha Plant
	.byte $56, $08, $60; Leftward Piranha Plant
	.byte $6D, $03, $6D; Red Koopa Troopa
	.byte $FF
; Piranha_Plant__1_Ending_W7
; Object Set 5
Piranha_Plant__1_Ending_W7_generators:
Piranha_Plant__1_Ending_W7_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $00 | LEVEL3_TILESET_05; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $05; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $FD; Double-Ended Vertical Pipe
	.byte $40 | $0E, $00, $F7; Double-Ended Vertical Pipe
	.byte $40 | $00, $04, $FC; Double-Ended Vertical Pipe
	.byte $40 | $0D, $0E, $F8; Double-Ended Vertical Pipe
	.byte $20 | $0D, $04, $F9; Rightward Pipe (CAN'T go in)
	.byte $40 | $0D, $09, $24; Leftward Pipe (CAN'T go in)
	.byte $20 | $14, $09, $F2; Rightward Pipe (CAN'T go in)
	.byte $40 | $14, $0B, $22; Leftward Pipe (CAN'T go in)
	.byte $20 | $16, $00, $F8; Rightward Pipe (CAN'T go in)
	.byte $40 | $16, $08, $27; Leftward Pipe (CAN'T go in)
	.byte $20 | $00, $02, $D1; Upward Pipe (CAN'T go up)
	.byte $00 | $19, $00, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $01, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $02, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $03, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $04, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $05, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $06, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $07, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $08, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $09, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $0A, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $0B, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $0C, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $0D, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $0E, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $0F, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $18, $00, $01; Piranha Plant Muncher B
	.byte $00 | $18, $01, $00; Piranha Plant Muncher A
	.byte $00 | $18, $02, $01; Piranha Plant Muncher B
	.byte $00 | $18, $03, $00; Piranha Plant Muncher A
	.byte $00 | $18, $04, $01; Piranha Plant Muncher B
	.byte $00 | $18, $05, $00; Piranha Plant Muncher A
	.byte $00 | $18, $06, $01; Piranha Plant Muncher B
	.byte $00 | $18, $07, $00; Piranha Plant Muncher A
	.byte $00 | $18, $08, $01; Piranha Plant Muncher B
	.byte $00 | $18, $09, $00; Piranha Plant Muncher A
	.byte $00 | $18, $0A, $01; Piranha Plant Muncher B
	.byte $00 | $18, $0B, $00; Piranha Plant Muncher A
	.byte $00 | $18, $0C, $01; Piranha Plant Muncher B
	.byte $00 | $18, $0D, $00; Piranha Plant Muncher A
	.byte $00 | $18, $0E, $01; Piranha Plant Muncher B
	.byte $00 | $18, $0F, $00; Piranha Plant Muncher A
	.byte $FF
Piranha_Plant__1_Ending_W7_objects:
	.byte $52, $0B, $13; Treasure Chest
	.byte $BA, $0C, $13; Exit on get treasure chest
	.byte $FF
; Level_4_W7
; Object Set 6
Level_4_W7_generators:
Level_4_W7_header:
	.byte $A9; Next Level
	.byte LEVEL1_SIZE_10 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $06; Start action | Graphic set
	.byte $00 | $02; Time | Music
	.byte $00 | $00, $00, $0D; Water - lasts whole level
	.byte $60 | $00, $00, $8F; Jelectros
	.byte $60 | $00, $10, $8F; Jelectros
	.byte $60 | $00, $20, $8F; Jelectros
	.byte $60 | $00, $30, $8F; Jelectros
	.byte $60 | $00, $40, $8F; Jelectros
	.byte $60 | $00, $50, $8F; Jelectros
	.byte $60 | $00, $60, $8F; Jelectros
	.byte $60 | $00, $70, $8F; Jelectros
	.byte $60 | $00, $80, $8F; Jelectros
	.byte $60 | $00, $90, $8F; Jelectros
	.byte $60 | $06, $30, $DA, $3C; Water
	.byte $60 | $1A, $00, $50, $1F; Orange Block Platform
	.byte $60 | $1A, $22, $50, $7F; Orange Block Platform
	.byte $60 | $16, $00, $46; Gray platform
	.byte $00 | $16, $0A, $D3; Background Aquatic Plants
	.byte $00 | $15, $0C, $D4; Background Aquatic Plants
	.byte $20 | $12, $09, $84; Coins
	.byte $40 | $14, $00, $22; Leftward Pipe (CAN'T go in)
	.byte $60 | $16, $17, $42; Gray platform
	.byte $00 | $0B, $10, $E7; Vertically Oriented Donut Blocks
	.byte $00 | $12, $11, $E0; Vertically Oriented Donut Blocks
	.byte $00 | $11, $12, $E2; Vertically Oriented Donut Blocks
	.byte $60 | $11, $13, $A2; Horizontally Oriented Donut Blocks
	.byte $60 | $10, $14, $A0; Horizontally Oriented Donut Blocks
	.byte $60 | $12, $1A, $A0; Horizontally Oriented Donut Blocks
	.byte $60 | $13, $1A, $A2; Horizontally Oriented Donut Blocks
	.byte $60 | $14, $1C, $A3; Horizontally Oriented Donut Blocks
	.byte $60 | $15, $1F, $A2; Horizontally Oriented Donut Blocks
	.byte $60 | $16, $1F, $A0; Horizontally Oriented Donut Blocks
	.byte $20 | $14, $11, $42; Wooden blocks
	.byte $20 | $17, $1F, $41; Wooden blocks
	.byte $00 | $17, $1B, $D2; Background Aquatic Plants
	.byte $20 | $12, $19, $00; '?' with Flower
	.byte $60 | $14, $24, $41; Gray platform
	.byte $00 | $0B, $2A, $E4; Vertically Oriented Donut Blocks
	.byte $00 | $0F, $2B, $E3; Vertically Oriented Donut Blocks
	.byte $60 | $10, $2C, $A1; Horizontally Oriented Donut Blocks
	.byte $60 | $15, $27, $A0; Horizontally Oriented Donut Blocks
	.byte $60 | $16, $27, $A2; Horizontally Oriented Donut Blocks
	.byte $60 | $17, $29, $A2; Horizontally Oriented Donut Blocks
	.byte $60 | $18, $2B, $A4; Horizontally Oriented Donut Blocks
	.byte $60 | $19, $2B, $A0; Horizontally Oriented Donut Blocks
	.byte $00 | $16, $2D, $E1; Vertically Oriented Donut Blocks
	.byte $00 | $17, $2F, $E0; Vertically Oriented Donut Blocks
	.byte $20 | $11, $21, $84; Coins
	.byte $60 | $06, $4D, $80; Jelectros
	.byte $60 | $07, $46, $80; Jelectros
	.byte $60 | $08, $49, $80; Jelectros
	.byte $60 | $08, $4F, $80; Jelectros
	.byte $60 | $09, $41, $80; Jelectros
	.byte $60 | $09, $4C, $80; Jelectros
	.byte $60 | $0A, $4E, $80; Jelectros
	.byte $60 | $0B, $4A, $80; Jelectros
	.byte $60 | $0C, $44, $80; Jelectros
	.byte $60 | $0F, $48, $80; Jelectros
	.byte $60 | $10, $4C, $80; Jelectros
	.byte $60 | $11, $4A, $80; Jelectros
	.byte $60 | $11, $4E, $80; Jelectros
	.byte $60 | $12, $45, $80; Jelectros
	.byte $60 | $12, $4D, $80; Jelectros
	.byte $60 | $13, $42, $80; Jelectros
	.byte $60 | $13, $48, $80; Jelectros
	.byte $60 | $07, $51, $80; Jelectros
	.byte $60 | $07, $5A, $80; Jelectros
	.byte $60 | $09, $51, $80; Jelectros
	.byte $60 | $09, $56, $80; Jelectros
	.byte $60 | $0A, $53, $80; Jelectros
	.byte $60 | $0D, $59, $80; Jelectros
	.byte $60 | $0F, $50, $80; Jelectros
	.byte $60 | $10, $53, $80; Jelectros
	.byte $60 | $11, $51, $80; Jelectros
	.byte $60 | $11, $56, $80; Jelectros
	.byte $60 | $11, $5C, $80; Jelectros
	.byte $60 | $13, $50, $80; Jelectros
	.byte $00 | $15, $70, $E4; Vertically Oriented Donut Blocks
	.byte $00 | $16, $71, $E0; Vertically Oriented Donut Blocks
	.byte $00 | $14, $73, $E2; Vertically Oriented Donut Blocks
	.byte $00 | $0B, $7B, $E6; Vertically Oriented Donut Blocks
	.byte $00 | $11, $7C, $E3; Vertically Oriented Donut Blocks
	.byte $60 | $12, $7D, $A2; Horizontally Oriented Donut Blocks
	.byte $60 | $11, $7F, $A0; Horizontally Oriented Donut Blocks
	.byte $60 | $14, $79, $A3; Horizontally Oriented Donut Blocks
	.byte $60 | $15, $7B, $A0; Horizontally Oriented Donut Blocks
	.byte $00 | $16, $75, $D3; Background Aquatic Plants
	.byte $00 | $14, $77, $D5; Background Aquatic Plants
	.byte $20 | $11, $72, $00; '?' with Flower
	.byte $20 | $12, $76, $83; Coins
	.byte $20 | $16, $7B, $40; Wooden blocks
	.byte $60 | $15, $81, $42; Gray platform
	.byte $60 | $18, $8B, $43; Gray platform
	.byte $00 | $0D, $8E, $E3; Vertically Oriented Donut Blocks
	.byte $60 | $10, $8A, $A2; Horizontally Oriented Donut Blocks
	.byte $60 | $11, $8C, $A3; Horizontally Oriented Donut Blocks
	.byte $60 | $16, $8B, $A7; Horizontally Oriented Donut Blocks
	.byte $00 | $15, $8D, $E2; Vertically Oriented Donut Blocks
	.byte $00 | $15, $88, $D4; Background Aquatic Plants
	.byte $00 | $17, $86, $D2; Background Aquatic Plants
	.byte $20 | $12, $84, $83; Coins
	.byte $00 | $0B, $9A, $E5; Vertically Oriented Donut Blocks
	.byte $00 | $0F, $99, $E0; Vertically Oriented Donut Blocks
	.byte $00 | $11, $92, $E5; Vertically Oriented Donut Blocks
	.byte $00 | $15, $93, $E0; Vertically Oriented Donut Blocks
	.byte $20 | $12, $95, $83; Coins
	.byte $60 | $17, $97, $42; Gray platform
	.byte $60 | $16, $9A, $45; Gray platform
	.byte $20 | $14, $9C, $E3; Rightward Pipe (CAN go in)
	.byte $20 | $11, $9A, $41; Wooden blocks
	; Pointer on screen $09
	.byte $E0 | $09, $70 | $03, 35; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_4_W7_objects:
	.byte $D3, $00, $0F; Autoscrolling
	.byte $B5, $0F, $0F; Infinite Spiny Cheep-Cheeps
	.byte $67, $14, $18; Lava Lotus
	.byte $63, $2E, $13; Big Bertha (underwater)
	.byte $6A, $36, $13; Bloober Nanny
	.byte $BB, $3F, $0F; Stops infinite flying or spiny Cheep-Cheeps
	.byte $63, $56, $0D; Big Bertha (underwater)
	.byte $6A, $63, $0C; Bloober Nanny
	.byte $6A, $69, $10; Bloober Nanny
	.byte $B5, $6F, $0F; Infinite Spiny Cheep-Cheeps
	.byte $67, $7E, $18; Lava Lotus
	.byte $63, $8A, $13; Big Bertha (underwater)
	.byte $67, $97, $15; Lava Lotus
	.byte $FF
; Level_6_W7
; Object Set 8
Level_6_W7_generators:
Level_6_W7_header:
	.byte $AE; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_VERTICAL | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $08; Start action | Graphic set
	.byte $80 | $01; Time | Music
	.byte $00 | $00, $00, $0C; Background for pipe levels
	.byte $20 | $0D, $00, $41; Wooden blocks
	.byte $20 | $0E, $00, $41; Wooden blocks
	.byte $20 | $00, $10, $41; Wooden blocks
	.byte $20 | $01, $10, $41; Wooden blocks
	.byte $20 | $0D, $0F, $40; Wooden blocks
	.byte $20 | $0E, $0F, $40; Wooden blocks
	.byte $20 | $00, $1F, $40; Wooden blocks
	.byte $20 | $01, $1F, $40; Wooden blocks
	.byte $20 | $00, $07, $C6; Upward Pipe (CAN go up)
	.byte $20 | $09, $01, $0F; Invisible 1-up
	.byte $60 | $0C, $05, $C6; Floor Spikes
	.byte $20 | $0D, $05, $F3; Rightward Pipe (CAN'T go in)
	.byte $20 | $00, $15, $F3; Rightward Pipe (CAN'T go in)
	.byte $40 | $0D, $09, $22; Leftward Pipe (CAN'T go in)
	.byte $40 | $00, $19, $22; Leftward Pipe (CAN'T go in)
	.byte $00 | $08, $18, $07; Multi-directional directional platform
	.byte $20 | $0A, $1D, $20; '?' blocks with single coins
	.byte $20 | $0B, $14, $21; '?' blocks with single coins
	.byte $20 | $0C, $1B, $40; Wooden blocks
	.byte $20 | $0D, $1B, $40; Wooden blocks
	.byte $20 | $0E, $1B, $42; Wooden blocks
	.byte $20 | $0B, $20, $49; Wooden blocks
	.byte $20 | $0C, $20, $49; Wooden blocks
	.byte $20 | $0D, $20, $49; Wooden blocks
	.byte $20 | $0B, $2D, $42; Wooden blocks
	.byte $20 | $0C, $2D, $42; Wooden blocks
	.byte $20 | $0D, $2D, $42; Wooden blocks
	.byte $20 | $00, $2B, $42; Wooden blocks
	.byte $20 | $00, $24, $21; '?' blocks with single coins
	.byte $20 | $01, $2B, $22; '?' blocks with single coins
	.byte $00 | $03, $28, $05; Rightward directional platform
	.byte $20 | $04, $28, $21; '?' blocks with single coins
	.byte $00 | $07, $24, $04; Upward directional platform
	.byte $00 | $09, $2D, $06; Leftward directional platform
	.byte $00 | $0E, $20, $F8; Ceiling Spikes
	.byte $00 | $0E, $2E, $F1; Ceiling Spikes
	.byte $60 | $0A, $20, $C9; Floor Spikes
	.byte $60 | $0A, $2D, $C2; Floor Spikes
	.byte $20 | $05, $37, $25; '?' blocks with single coins
	.byte $20 | $05, $39, $01; '?' with Leaf
	.byte $00 | $06, $32, $05; Rightward directional platform
	.byte $00 | $09, $3D, $06; Leftward directional platform
	.byte $00 | $0D, $3D, $18; Double-ended pipe
	.byte $00 | $0C, $38, $07; Multi-directional directional platform
	.byte $20 | $0C, $35, $40; Wooden blocks
	.byte $20 | $0D, $30, $45; Wooden blocks
	.byte $20 | $0E, $30, $45; Wooden blocks
	.byte $20 | $0D, $3F, $40; Wooden blocks
	.byte $20 | $0E, $3F, $40; Wooden blocks
	.byte $20 | $0A, $3C, $40; Wooden blocks
	.byte $20 | $0B, $3C, $40; Wooden blocks
	.byte $20 | $0C, $3C, $40; Wooden blocks
	.byte $20 | $0D, $3C, $40; Wooden blocks
	.byte $20 | $0E, $3C, $40; Wooden blocks
	.byte $20 | $00, $40, $45; Wooden blocks
	.byte $20 | $01, $40, $45; Wooden blocks
	.byte $20 | $02, $40, $42; Wooden blocks
	.byte $20 | $03, $40, $42; Wooden blocks
	.byte $20 | $04, $40, $42; Wooden blocks
	.byte $20 | $05, $40, $42; Wooden blocks
	.byte $20 | $06, $40, $42; Wooden blocks
	.byte $20 | $07, $40, $42; Wooden blocks
	.byte $20 | $00, $4C, $40; Wooden blocks
	.byte $20 | $01, $4C, $40; Wooden blocks
	.byte $20 | $02, $4C, $40; Wooden blocks
	.byte $20 | $03, $4C, $40; Wooden blocks
	.byte $20 | $04, $4C, $40; Wooden blocks
	.byte $20 | $05, $4C, $40; Wooden blocks
	.byte $20 | $06, $4C, $40; Wooden blocks
	.byte $20 | $07, $4C, $40; Wooden blocks
	.byte $20 | $08, $4C, $40; Wooden blocks
	.byte $20 | $00, $4F, $40; Wooden blocks
	.byte $20 | $01, $4F, $40; Wooden blocks
	.byte $20 | $02, $4F, $40; Wooden blocks
	.byte $20 | $03, $4F, $40; Wooden blocks
	.byte $20 | $04, $4F, $40; Wooden blocks
	.byte $20 | $05, $4F, $40; Wooden blocks
	.byte $20 | $06, $4F, $40; Wooden blocks
	.byte $20 | $04, $4B, $20; '?' blocks with single coins
	.byte $20 | $05, $48, $21; '?' blocks with single coins
	.byte $00 | $06, $44, $14; Double-ended pipe
	.byte $00 | $09, $48, $06; Leftward directional platform
	.byte $20 | $09, $4C, $20; '?' blocks with single coins
	.byte $60 | $0D, $4B, $C0; Floor Spikes
	.byte $20 | $0E, $4B, $20; '?' blocks with single coins
	.byte $20 | $00, $54, $82; Coins
	.byte $20 | $01, $53, $80; Coins
	.byte $20 | $01, $57, $80; Coins
	.byte $60 | $03, $5C, $C0; Floor Spikes
	.byte $20 | $04, $5C, $20; '?' blocks with single coins
	.byte $20 | $04, $55, $60; Note Blocks - movable two directions
	.byte $20 | $08, $54, $13; Bricks
	.byte $20 | $08, $56, $0A; Multi-Coin Brick
	.byte $00 | $09, $5B, $04; Upward directional platform
	.byte $60 | $0C, $54, $B4; Donut Blocks
	.byte $20 | $0C, $5E, $20; '?' blocks with single coins
	.byte $20 | $0E, $51, $60; Note Blocks - movable two directions
	.byte $20 | $01, $6B, $F1; Rightward Pipe (CAN'T go in)
	.byte $40 | $01, $6D, $21; Leftward Pipe (CAN'T go in)
	.byte $20 | $03, $62, $20; '?' blocks with single coins
	.byte $60 | $03, $68, $B1; Donut Blocks
	.byte $20 | $07, $64, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $07, $68, $82; Coins
	.byte $00 | $08, $6D, $07; Multi-directional directional platform
	.byte $20 | $0A, $64, $21; '?' blocks with single coins
	.byte $60 | $0B, $67, $B2; Donut Blocks
	.byte $20 | $0B, $68, $60; Note Blocks - movable two directions
	.byte $20 | $0D, $65, $81; Coins
	.byte $20 | $0E, $67, $80; Coins
	.byte $20 | $01, $79, $81; Coins
	.byte $20 | $02, $7B, $80; Coins
	.byte $20 | $0D, $6C, $40; Wooden blocks
	.byte $20 | $0E, $6C, $43; Wooden blocks
	.byte $20 | $0E, $60, $41; Wooden blocks
	.byte $20 | $00, $70, $42; Wooden blocks
	.byte $20 | $01, $70, $43; Wooden blocks
	.byte $20 | $02, $70, $44; Wooden blocks
	.byte $20 | $03, $70, $45; Wooden blocks
	.byte $20 | $04, $70, $46; Wooden blocks
	.byte $20 | $05, $70, $47; Wooden blocks
	.byte $20 | $06, $75, $43; Wooden blocks
	.byte $20 | $07, $75, $44; Wooden blocks
	.byte $20 | $08, $75, $45; Wooden blocks
	.byte $20 | $09, $75, $46; Wooden blocks
	.byte $20 | $0A, $70, $4F; Wooden blocks
	.byte $20 | $0B, $70, $4F; Wooden blocks
	.byte $20 | $00, $7D, $42; Wooden blocks
	.byte $20 | $01, $7D, $42; Wooden blocks
	.byte $20 | $02, $7E, $41; Wooden blocks
	.byte $20 | $03, $7E, $41; Wooden blocks
	; Pointer on screen $00
	.byte $E0 | $00, $50 | $03, 50; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_6_W7_objects:
	.byte $57, $0B, $0D; Rightward Piranha Plant
	.byte $56, $05, $0F; Leftward Piranha Plant
	.byte $A0, $04, $42; Green Piranha Plant (upward)
	.byte $6D, $05, $52; Red Koopa Troopa
	.byte $56, $0B, $5B; Leftward Piranha Plant
	.byte $A0, $04, $61; Green Piranha Plant (upward)
	.byte $6C, $0D, $67; Green Koopa Troopa
	.byte $6C, $0F, $67; Green Koopa Troopa
	.byte $FF
; Level_7_W7
; Object Set 4
Level_7_W7_generators:
Level_7_W7_header:
	.byte $AF; Next Level
	.byte LEVEL1_SIZE_12 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $04; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $40 | $00, $00, $B0, $BF; Blue Wooden Blocks
	.byte $00 | $0F, $02, $00; Small Swirly Background Cloud
	.byte $00 | $11, $05, $01; Large Swirly Background Cloud
	.byte $00 | $0E, $0C, $01; Large Swirly Background Cloud
	.byte $00 | $11, $0E, $00; Small Swirly Background Cloud
	.byte $00 | $19, $06, $40; Background Bushes
	.byte $00 | $19, $08, $41; Background Bushes
	.byte $00 | $19, $0D, $42; Background Bushes
	.byte $00 | $1A, $00, $10, $BF; Wooden platform
	.byte $40 | $18, $00, $22; Leftward Pipe (CAN'T go in)
	.byte $20 | $16, $0A, $A3; Downward Pipe (CAN'T go down)
	.byte $00 | $0F, $12, $00; Small Swirly Background Cloud
	.byte $00 | $11, $15, $01; Large Swirly Background Cloud
	.byte $00 | $0E, $1C, $01; Large Swirly Background Cloud
	.byte $00 | $11, $1E, $00; Small Swirly Background Cloud
	.byte $20 | $17, $12, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $1E, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $18, $02; '?' with star
	.byte $60 | $17, $1F, $A0, $9A; Munchers
	.byte $00 | $19, $1A, $40; Background Bushes
	.byte $00 | $19, $1C, $40; Background Bushes
	.byte $00 | $0F, $22, $00; Small Swirly Background Cloud
	.byte $00 | $11, $25, $01; Large Swirly Background Cloud
	.byte $00 | $0E, $2C, $01; Large Swirly Background Cloud
	.byte $00 | $11, $2E, $00; Small Swirly Background Cloud
	.byte $20 | $18, $20, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $22, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $24, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $26, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $28, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $2A, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $2C, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $2E, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $15, $2A, $02; '?' with star
	.byte $00 | $0F, $32, $00; Small Swirly Background Cloud
	.byte $00 | $11, $35, $01; Large Swirly Background Cloud
	.byte $00 | $0E, $3C, $01; Large Swirly Background Cloud
	.byte $00 | $11, $3E, $00; Small Swirly Background Cloud
	.byte $20 | $18, $30, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $32, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $34, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $36, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $38, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $3A, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $3C, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $3E, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $0F, $42, $00; Small Swirly Background Cloud
	.byte $00 | $11, $45, $01; Large Swirly Background Cloud
	.byte $00 | $0E, $4C, $01; Large Swirly Background Cloud
	.byte $00 | $11, $4E, $00; Small Swirly Background Cloud
	.byte $20 | $18, $40, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $42, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $44, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $46, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $48, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $4A, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $4C, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $4E, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $0F, $52, $00; Small Swirly Background Cloud
	.byte $00 | $11, $55, $01; Large Swirly Background Cloud
	.byte $00 | $0E, $5C, $01; Large Swirly Background Cloud
	.byte $00 | $11, $5E, $00; Small Swirly Background Cloud
	.byte $20 | $18, $50, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $52, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $54, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $56, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $58, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $5A, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $5C, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $5E, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $14, $56, $02; '?' with star
	.byte $00 | $0F, $62, $00; Small Swirly Background Cloud
	.byte $00 | $11, $65, $01; Large Swirly Background Cloud
	.byte $00 | $0E, $6C, $01; Large Swirly Background Cloud
	.byte $00 | $11, $6E, $00; Small Swirly Background Cloud
	.byte $20 | $18, $60, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $62, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $64, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $66, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $68, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $6C, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $6E, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $0C, $6A, $D4; Upward Pipe (CAN'T go up)
	.byte $20 | $14, $6A, $A5; Downward Pipe (CAN'T go down)
	.byte $00 | $0F, $72, $00; Small Swirly Background Cloud
	.byte $00 | $11, $75, $01; Large Swirly Background Cloud
	.byte $00 | $0E, $7C, $01; Large Swirly Background Cloud
	.byte $00 | $11, $7E, $00; Small Swirly Background Cloud
	.byte $20 | $18, $70, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $74, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $76, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $78, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $7A, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $7C, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $7E, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $72, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $0C, $72, $D6; Upward Pipe (CAN'T go up)
	.byte $00 | $0F, $82, $00; Small Swirly Background Cloud
	.byte $00 | $11, $85, $01; Large Swirly Background Cloud
	.byte $00 | $0E, $8C, $01; Large Swirly Background Cloud
	.byte $00 | $11, $8E, $00; Small Swirly Background Cloud
	.byte $20 | $18, $80, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $82, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $86, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $88, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $8A, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $8C, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $8E, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $14, $84, $A5; Downward Pipe (CAN'T go down)
	.byte $20 | $0C, $84, $D4; Upward Pipe (CAN'T go up)
	.byte $20 | $14, $8C, $40; Wooden blocks
	.byte $20 | $15, $8C, $40; Wooden blocks
	.byte $20 | $16, $8C, $40; Wooden blocks
	.byte $20 | $14, $8D, $02; '?' with star
	.byte $00 | $0F, $92, $00; Small Swirly Background Cloud
	.byte $00 | $11, $95, $01; Large Swirly Background Cloud
	.byte $00 | $0E, $9C, $01; Large Swirly Background Cloud
	.byte $00 | $11, $9E, $00; Small Swirly Background Cloud
	.byte $20 | $18, $90, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $92, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $94, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $96, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $98, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $9A, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $9C, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $9E, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $0F, $A2, $00; Small Swirly Background Cloud
	.byte $00 | $11, $A5, $01; Large Swirly Background Cloud
	.byte $00 | $0E, $AC, $01; Large Swirly Background Cloud
	.byte $00 | $11, $AE, $00; Small Swirly Background Cloud
	.byte $20 | $18, $A0, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $A2, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $A4, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $A6, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $A8, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $AA, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $AC, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $AE, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $00, $A3, $AF; Downward Pipe (CAN'T go down)
	.byte $20 | $0C, $A3, $D9; Upward Pipe (CAN'T go up)
	.byte $00 | $0F, $B2, $00; Small Swirly Background Cloud
	.byte $00 | $11, $B5, $01; Large Swirly Background Cloud
	.byte $00 | $0E, $BC, $01; Large Swirly Background Cloud
	.byte $00 | $11, $BE, $00; Small Swirly Background Cloud
	.byte $20 | $18, $B0, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $B2, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $B6, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $B8, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $BA, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $BC, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $BE, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $14, $B4, $A5; Downward Pipe (CAN'T go down)
	.byte $20 | $00, $B4, $D4; Upward Pipe (CAN'T go up)
	.byte $20 | $15, $BD, $E2; Rightward Pipe (CAN go in)
	.byte $20 | $17, $BA, $45; Wooden blocks
	; Pointer on screen $0B
	.byte $E0 | $0B, $70 | $03, 129; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_7_W7_objects:
	.byte $A0, $0A, $16; Green Piranha Plant (upward)
	.byte $A0, $12, $17; Green Piranha Plant (upward)
	.byte $A0, $22, $18; Green Piranha Plant (upward)
	.byte $A0, $34, $18; Green Piranha Plant (upward)
	.byte $A0, $48, $18; Green Piranha Plant (upward)
	.byte $A0, $4C, $18; Green Piranha Plant (upward)
	.byte $A0, $5C, $18; Green Piranha Plant (upward)
	.byte $A0, $6E, $18; Green Piranha Plant (upward)
	.byte $A0, $96, $18; Green Piranha Plant (upward)
	.byte $A0, $B8, $18; Green Piranha Plant (upward)
	.byte $FF
; Level_8_Bonus_Area__1_W7
; Object Set 13
Level_8_Bonus_Area__1_W7_generators:
Level_8_Bonus_Area__1_W7_header:
	.byte $B4; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0D; Start action | Graphic set
	.byte $00 | $0A; Time | Music
	.byte $60 | $0E, $00, $4C, $2F; White Background
	.byte $60 | $19, $00, $21, $2F; Clouds B
	.byte $00 | $0E, $00, $07; Cloud Background C
	.byte $00 | $13, $06, $06; Cloud Background B
	.byte $20 | $16, $0C, $87; Coins
	.byte $20 | $18, $0C, $87; Coins
	.byte $00 | $0E, $12, $07; Cloud Background C
	.byte $20 | $14, $19, $83; Coins
	.byte $20 | $16, $16, $89; Coins
	.byte $20 | $18, $16, $89; Coins
	.byte $00 | $0F, $26, $07; Cloud Background C
	.byte $00 | $10, $2B, $07; Cloud Background C
	.byte $20 | $16, $21, $87; Coins
	.byte $20 | $18, $21, $87; Coins
	.byte $20 | $17, $2C, $93; Downward Pipe (CAN go down)
	; Pointer on screen $02
	.byte $E0 | $02, $00 | $02, 38; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_8_Bonus_Area__1_W7_objects:
	.byte $D3, $00, $12; Autoscrolling
	.byte $FF
; Level_5_W7
; Object Set 1
Level_5_W7_generators:
Level_5_W7_header:
	.byte $B5; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_07; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $0B, $00, $B4, $7F; Blue X-Blocks
	.byte $40 | $00, $00, $B0, $7F; Blue X-Blocks
	.byte $40 | $1A, $00, $B0, $7F; Blue X-Blocks
	.byte $40 | $01, $00, $BE, $0F; Blue X-Blocks
	.byte $40 | $10, $00, $B9, $01; Blue X-Blocks
	.byte $20 | $10, $02, $D5; Upward Pipe (CAN'T go up)
	.byte $40 | $0B, $14, $BE, $08; Blue X-Blocks
	.byte $40 | $01, $1F, $BE, $02; Blue X-Blocks
	.byte $20 | $04, $19, $13; Bricks
	.byte $20 | $07, $16, $13; Bricks
	.byte $40 | $09, $12, $FD; Double-Ended Vertical Pipe
	.byte $40 | $07, $1D, $FB; Double-Ended Vertical Pipe
	.byte $40 | $13, $20, $B3, $00; Blue X-Blocks
	.byte $40 | $16, $20, $B0, $1A; Blue X-Blocks
	.byte $40 | $04, $23, $B0, $06; Blue X-Blocks
	.byte $40 | $05, $24, $BA, $04; Blue X-Blocks
	.byte $40 | $10, $27, $B5, $01; Blue X-Blocks
	.byte $40 | $04, $2B, $BB, $02; Blue X-Blocks
	.byte $40 | $05, $2F, $B0, $11; Blue X-Blocks
	.byte $40 | $08, $22, $FB; Double-Ended Vertical Pipe
	.byte $40 | $08, $29, $FB; Double-Ended Vertical Pipe
	.byte $40 | $08, $2E, $FB; Double-Ended Vertical Pipe
	.byte $20 | $12, $25, $00; '?' with Flower
	.byte $20 | $04, $22, $0E; Invisible Coin
	.byte $20 | $04, $2A, $0E; Invisible Coin
	.byte $20 | $16, $2B, $0E; Invisible Coin
	.byte $20 | $16, $2C, $0E; Invisible Coin
	.byte $20 | $17, $25, $10; Bricks
	.byte $20 | $18, $25, $10; Bricks
	.byte $40 | $05, $30, $BA, $00; Blue X-Blocks
	.byte $40 | $05, $33, $B3, $00; Blue X-Blocks
	.byte $40 | $09, $33, $B1, $05; Blue X-Blocks
	.byte $40 | $05, $3F, $BF, $02; Blue X-Blocks
	.byte $40 | $14, $3F, $B5, $02; Blue X-Blocks
	.byte $20 | $05, $35, $0E; Invisible Coin
	.byte $20 | $16, $34, $0E; Invisible Coin
	.byte $20 | $16, $35, $0E; Invisible Coin
	.byte $20 | $05, $32, $0F; Invisible 1-up
	.byte $20 | $08, $3B, $01; '?' with Leaf
	.byte $20 | $12, $36, $24; '?' Blocks with single coins
	.byte $40 | $08, $31, $FB; Double-Ended Vertical Pipe
	.byte $40 | $08, $3D, $FF; Double-Ended Vertical Pipe
	.byte $40 | $17, $30, $E0; White Turtle Bricks
	.byte $40 | $18, $30, $E0; White Turtle Bricks
	.byte $40 | $19, $30, $E0; White Turtle Bricks
	.byte $40 | $01, $44, $B2, $00; Blue X-Blocks
	.byte $40 | $05, $43, $B0, $00; Blue X-Blocks
	.byte $40 | $05, $44, $BA, $01; Blue X-Blocks
	.byte $40 | $07, $48, $B0, $04; Blue X-Blocks
	.byte $40 | $03, $4E, $B0, $07; Blue X-Blocks
	.byte $20 | $04, $44, $10; Bricks
	.byte $20 | $12, $4D, $10; Bricks
	.byte $20 | $13, $4D, $10; Bricks
	.byte $20 | $14, $4D, $10; Bricks
	.byte $20 | $15, $4D, $13; Bricks
	.byte $20 | $15, $45, $82; Coins
	.byte $20 | $15, $4E, $21; '?' Blocks with single coins
	.byte $40 | $09, $42, $F8; Double-Ended Vertical Pipe
	.byte $40 | $09, $4E, $F9; Double-Ended Vertical Pipe
	.byte $40 | $10, $56, $B9, $08; Blue X-Blocks
	.byte $40 | $04, $5A, $B0, $06; Blue X-Blocks
	.byte $40 | $08, $53, $B0, $08; Blue X-Blocks
	.byte $20 | $03, $56, $0E; Invisible Coin
	.byte $20 | $03, $57, $0E; Invisible Coin
	.byte $20 | $03, $58, $0E; Invisible Coin
	.byte $20 | $03, $59, $0E; Invisible Coin
	.byte $40 | $09, $5F, $FD; Double-Ended Vertical Pipe
	.byte $20 | $08, $50, $0E; Invisible Coin
	.byte $20 | $08, $51, $0E; Invisible Coin
	.byte $20 | $08, $52, $0E; Invisible Coin
	.byte $40 | $10, $64, $B7, $00; Blue X-Blocks
	.byte $40 | $18, $62, $B1, $00; Blue X-Blocks
	.byte $40 | $18, $66, $B1, $00; Blue X-Blocks
	.byte $40 | $04, $61, $B0, $08; Blue X-Blocks
	.byte $40 | $04, $6A, $B6, $02; Blue X-Blocks
	.byte $40 | $14, $6C, $B2, $00; Blue X-Blocks
	.byte $40 | $16, $6C, $B0, $02; Blue X-Blocks
	.byte $20 | $16, $6F, $0E; Invisible Coin
	.byte $20 | $16, $70, $0E; Invisible Coin
	.byte $20 | $16, $71, $0E; Invisible Coin
	.byte $20 | $16, $72, $0E; Invisible Coin
	.byte $20 | $16, $73, $0E; Invisible Coin
	.byte $20 | $16, $74, $0E; Invisible Coin
	.byte $20 | $06, $6F, $0F; Invisible 1-up
	.byte $40 | $08, $68, $FE; Double-Ended Vertical Pipe
	.byte $40 | $09, $6D, $FA; Double-Ended Vertical Pipe
	.byte $40 | $05, $61, $E4; White Turtle Bricks
	.byte $40 | $06, $61, $E0; White Turtle Bricks
	.byte $40 | $07, $61, $E0; White Turtle Bricks
	.byte $40 | $06, $65, $E0; White Turtle Bricks
	.byte $40 | $07, $65, $E0; White Turtle Bricks
	.byte $40 | $08, $61, $E4; White Turtle Bricks
	.byte $40 | $09, $61, $E4; White Turtle Bricks
	.byte $40 | $0A, $61, $E4; White Turtle Bricks
	.byte $40 | $01, $70, $B9, $0F; Blue X-Blocks
	.byte $40 | $10, $73, $B2, $00; Blue X-Blocks
	.byte $40 | $16, $75, $B3, $00; Blue X-Blocks
	.byte $20 | $10, $78, $C6; Upward Pipe (CAN go up)
	.byte $40 | $10, $7B, $B9, $04; Blue X-Blocks
	; Pointer on screen $07
	.byte $E0 | $07, $60 | $01, 66; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_5_W7_objects:
	.byte $6E, $0C, $19; Green Koopa Paratroopa (bounces)
	.byte $6E, $12, $19; Green Koopa Paratroopa (bounces)
	.byte $6D, $19, $06; Red Koopa Troopa
	.byte $6D, $1C, $03; Red Koopa Troopa
	.byte $55, $25, $19; Bob-Omb
	.byte $55, $27, $19; Bob-Omb
	.byte $55, $29, $19; Bob-Omb
	.byte $6C, $38, $19; Green Koopa Troopa
	.byte $6C, $3A, $19; Green Koopa Troopa
	.byte $6D, $4C, $06; Red Koopa Troopa
	.byte $6E, $4E, $19; Green Koopa Paratroopa (bounces)
	.byte $6E, $51, $19; Green Koopa Paratroopa (bounces)
	.byte $6E, $54, $19; Green Koopa Paratroopa (bounces)
	.byte $6D, $56, $06; Red Koopa Troopa
	.byte $55, $5D, $0A; Bob-Omb
	.byte $6C, $63, $07; Green Koopa Troopa
	.byte $71, $64, $19; Spiny
	.byte $FF
; Level_9_Ending_W7
; Object Set 9
Level_9_Ending_W7_generators:
Level_9_Ending_W7_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_02 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_09; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $09; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $20 | $18, $06, $A1; Downward Pipe (CAN'T go down)
	.byte $40 | $00, $0A, $09; Level Ending
	.byte $FF
Level_9_Ending_W7_objects:
	.byte $41, $18, $15; Goal Card
	.byte $FF
; Dungeon__2_Boss_Room_W7
; Object Set 2
Dungeon__2_Boss_Room_W7_generators:
Dungeon__2_Boss_Room_W7_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $0E, $00, $3A, $3F; Blank Background (used to block out stuff)
	.byte $00 | $00, $00, $EF, $19; Horizontally oriented X-blocks
	.byte $20 | $10, $01, $D5; Upward Pipe (CAN'T go up)
	.byte $00 | $00, $1A, $EE, $01; Horizontally oriented X-blocks
	.byte $00 | $00, $1C, $EF, $23; Horizontally oriented X-blocks
	.byte $00 | $10, $10, $E7, $00; Horizontally oriented X-blocks
	.byte $00 | $10, $19, $E7, $00; Horizontally oriented X-blocks
	.byte $00 | $10, $1C, $E5, $00; Horizontally oriented X-blocks
	.byte $00 | $15, $10, $02; Rotodisc block
	.byte $00 | $15, $19, $02; Rotodisc block
	.byte $00 | $13, $25, $E0, $08; Horizontally oriented X-blocks
	.byte $00 | $14, $24, $E0, $09; Horizontally oriented X-blocks
	.byte $00 | $15, $23, $E0, $0A; Horizontally oriented X-blocks
	.byte $00 | $16, $22, $E0, $0B; Horizontally oriented X-blocks
	.byte $00 | $17, $21, $E0, $0C; Horizontally oriented X-blocks
	.byte $00 | $18, $20, $E0, $0D; Horizontally oriented X-blocks
	.byte $00 | $11, $35, $71; Long dungeon windows
	.byte $00 | $16, $33, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $37, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $3B, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $10, $3F, $E8, $00; Horizontally oriented X-blocks
	.byte $FF
Dungeon__2_Boss_Room_W7_objects:
	.byte $5A, $10, $15; Single Rotodisc (rotates clockwise)
	.byte $3F, $11, $18; Dry Bones
	.byte $3F, $13, $18; Dry Bones
	.byte $5A, $19, $15; Single Rotodisc (rotates clockwise)
	.byte $8A, $1A, $0F; Thwomp (normal)
	.byte $4B, $3C, $27; Boom Boom
	.byte $FF
; Piranha_Plant__2_Ending_W7
; Object Set 5
Piranha_Plant__2_Ending_W7_generators:
Piranha_Plant__2_Ending_W7_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $00 | LEVEL3_TILESET_05; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $05; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $FD; Double-Ended Vertical Pipe
	.byte $40 | $0E, $00, $F7; Double-Ended Vertical Pipe
	.byte $40 | $00, $04, $FC; Double-Ended Vertical Pipe
	.byte $40 | $0D, $0E, $F8; Double-Ended Vertical Pipe
	.byte $20 | $0D, $04, $F9; Rightward Pipe (CAN'T go in)
	.byte $40 | $0D, $09, $24; Leftward Pipe (CAN'T go in)
	.byte $20 | $14, $09, $F2; Rightward Pipe (CAN'T go in)
	.byte $40 | $14, $0B, $22; Leftward Pipe (CAN'T go in)
	.byte $20 | $16, $00, $F8; Rightward Pipe (CAN'T go in)
	.byte $40 | $16, $08, $27; Leftward Pipe (CAN'T go in)
	.byte $20 | $00, $02, $D1; Upward Pipe (CAN'T go up)
	.byte $00 | $19, $00, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $01, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $02, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $03, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $04, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $05, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $06, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $07, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $08, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $09, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $0A, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $0B, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $0C, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $0D, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $19, $0E, $B1; Piranha Plant Small Downward Pipe B
	.byte $00 | $19, $0F, $A1; Piranha Plant Small Downward Pipe A
	.byte $00 | $18, $00, $01; Piranha Plant Muncher B
	.byte $00 | $18, $01, $00; Piranha Plant Muncher A
	.byte $00 | $18, $02, $01; Piranha Plant Muncher B
	.byte $00 | $18, $03, $00; Piranha Plant Muncher A
	.byte $00 | $18, $04, $01; Piranha Plant Muncher B
	.byte $00 | $18, $05, $00; Piranha Plant Muncher A
	.byte $00 | $18, $06, $01; Piranha Plant Muncher B
	.byte $00 | $18, $07, $00; Piranha Plant Muncher A
	.byte $00 | $18, $08, $01; Piranha Plant Muncher B
	.byte $00 | $18, $09, $00; Piranha Plant Muncher A
	.byte $00 | $18, $0A, $01; Piranha Plant Muncher B
	.byte $00 | $18, $0B, $00; Piranha Plant Muncher A
	.byte $00 | $18, $0C, $01; Piranha Plant Muncher B
	.byte $00 | $18, $0D, $00; Piranha Plant Muncher A
	.byte $00 | $18, $0E, $01; Piranha Plant Muncher B
	.byte $00 | $18, $0F, $00; Piranha Plant Muncher A
	.byte $FF
Piranha_Plant__2_Ending_W7_objects:
	.byte $52, $0B, $13; Treasure Chest
	.byte $BA, $0C, $13; Exit on get treasure chest
	.byte $FF
; Tank__1_Boss_Room_W8
; Object Set 10
Tank__1_Boss_Room_W8_generators:
Tank__1_Boss_Room_W8_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_000; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0A; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $00 | $00, $00, $0F; Black boss room background
	.byte $00 | $0F, $00, $1F; Wooden Ship Beam
	.byte $00 | $10, $00, $4A; Wooden Ship Pillar
	.byte $00 | $10, $0F, $4A; Wooden Ship Pillar
	.byte $00 | $19, $01, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $03, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $05, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $07, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $09, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $0B, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $0D, $61; Thick Wooden Ship Beam
	.byte $00 | $0F, $01, $41; Wooden Ship Pillar
	.byte $00 | $0F, $02, $41; Wooden Ship Pillar
	.byte $FF
Tank__1_Boss_Room_W8_objects:
	.byte $82, $0C, $17; Boomerang Brother
	.byte $D6, $0D, $09; Puts item in treasure chest (Y pos. determines item; see docs/items.txt)
	.byte $BA, $0E, $17; Exit on get treasure chest
	.byte $FF
; Battleship_Boss_Room_W8
; Object Set 10
Battleship_Boss_Room_W8_generators:
Battleship_Boss_Room_W8_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_000; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0A; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $00 | $00, $00, $0F; Black boss room background
	.byte $00 | $0F, $00, $1F; Wooden Ship Beam
	.byte $00 | $10, $00, $4A; Wooden Ship Pillar
	.byte $00 | $10, $0F, $4A; Wooden Ship Pillar
	.byte $00 | $19, $01, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $03, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $05, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $07, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $09, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $0B, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $0D, $61; Thick Wooden Ship Beam
	.byte $00 | $0F, $01, $41; Wooden Ship Pillar
	.byte $00 | $0F, $02, $41; Wooden Ship Pillar
	.byte $FF
Battleship_Boss_Room_W8_objects:
	.byte $4B, $0C, $17; Boom Boom
	.byte $FF
; Hand_Trap__3_Ending_W8
; Object Set 11
Hand_Trap__3_Ending_W8_generators:
Hand_Trap__3_Ending_W8_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_03; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_11; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0B; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $0F, $00, $B0, $0F; Blue X-Blocks
	.byte $40 | $10, $00, $B8, $00; Blue X-Blocks
	.byte $40 | $19, $00, $B1, $0F; Blue X-Blocks
	.byte $40 | $0F, $0F, $BB, $0A; Blue X-Blocks
	.byte $40 | $17, $03, $B0, $00; Blue X-Blocks
	.byte $40 | $18, $03, $B0, $01; Blue X-Blocks
	.byte $40 | $16, $0B, $B2, $03; Blue X-Blocks
	.byte $40 | $17, $0A, $B1, $00; Blue X-Blocks
	.byte $40 | $18, $09, $B0, $00; Blue X-Blocks
	.byte $20 | $14, $01, $A4; Downward Pipe (CAN'T go down)
	.byte $FF
Hand_Trap__3_Ending_W8_objects:
	.byte $D6, $0C, $03; Puts item in treasure chest (Y pos. determines item; see docs/items.txt)
	.byte $52, $0D, $15; Treasure Chest
	.byte $BA, $0E, $15; Exit on get treasure chest
	.byte $FF
; Dungeon__White_Side__W8
; Object Set 2
Dungeon__White_Side__W8_generators:
Dungeon__White_Side__W8_header:
	.byte $CD; Next Level
	.byte LEVEL1_SIZE_14 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $0F, $00, $3B, $DF; Blank Background (used to block out stuff)
	.byte $00 | $0F, $00, $E0, $DF; Horizontally oriented X-blocks
	.byte $00 | $10, $00, $E6, $0D; Horizontally oriented X-blocks
	.byte $00 | $17, $00, $E3, $10; Horizontally oriented X-blocks
	.byte $20 | $13, $0F, $01; '?' with leaf
	.byte $60 | $18, $11, $42, $0F; Lava
	.byte $00 | $17, $12, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $10, $18, $E1, $01; Horizontally oriented X-blocks
	.byte $60 | $13, $1B, $63; Conveyor Belt - moves right
	.byte $60 | $17, $18, $52; Conveyor Belt - moves left
	.byte $00 | $11, $1C, $00; Door
	.byte $00 | $10, $21, $EA, $00; Horizontally oriented X-blocks
	.byte $00 | $17, $22, $E0, $05; Horizontally oriented X-blocks
	.byte $00 | $13, $27, $E4, $00; Horizontally oriented X-blocks
	.byte $00 | $13, $2B, $E5, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $2B, $E0, $03; Horizontally oriented X-blocks
	.byte $00 | $10, $2D, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $1A, $21, $E0, $0A; Horizontally oriented X-blocks
	.byte $00 | $1A, $2D, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $1A, $2F, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $17, $20, $E3, $00; Horizontally oriented X-blocks
	.byte $20 | $13, $24, $00; '?' with flower
	.byte $00 | $11, $29, $00; Door
	.byte $00 | $18, $22, $00; Door
	.byte $20 | $14, $21, $10; Bricks
	.byte $20 | $15, $21, $10; Bricks
	.byte $20 | $16, $21, $10; Bricks
	.byte $20 | $17, $23, $12; Bricks
	.byte $20 | $13, $28, $0E; Invisible Coin
	.byte $20 | $13, $29, $0E; Invisible Coin
	.byte $20 | $13, $2A, $0E; Invisible Coin
	.byte $20 | $17, $29, $0E; Invisible Coin
	.byte $60 | $18, $30, $42, $3F; Lava
	.byte $00 | $10, $30, $EA, $00; Horizontally oriented X-blocks
	.byte $00 | $17, $3A, $E3, $01; Horizontally oriented X-blocks
	.byte $00 | $17, $3E, $E3, $01; Horizontally oriented X-blocks
	.byte $00 | $17, $31, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $15, $35, $00; Door
	.byte $00 | $15, $3E, $00; Door
	.byte $20 | $14, $30, $10; Bricks
	.byte $20 | $15, $30, $10; Bricks
	.byte $20 | $16, $30, $10; Bricks
	.byte $60 | $17, $34, $52; Conveyor Belt - moves left
	.byte $60 | $14, $41, $53; Conveyor Belt - moves left
	.byte $60 | $16, $46, $62; Conveyor Belt - moves right
	.byte $60 | $17, $4B, $62; Conveyor Belt - moves right
	.byte $00 | $12, $43, $00; Door
	.byte $00 | $17, $51, $E0, $05; Horizontally oriented X-blocks
	.byte $00 | $18, $51, $E2, $03; Horizontally oriented X-blocks
	.byte $60 | $17, $53, $32, $00; Blank Background (used to block out stuff)
	.byte $00 | $10, $51, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $10, $54, $E0, $00; Horizontally oriented X-blocks
	.byte $20 | $13, $55, $01; '?' with leaf
	.byte $60 | $17, $59, $62; Conveyor Belt - moves right
	.byte $00 | $18, $52, $00; Door
	.byte $00 | $14, $6B, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $12, $63, $00; Door
	.byte $00 | $12, $6C, $00; Door
	.byte $60 | $14, $62, $52; Conveyor Belt - moves left
	.byte $60 | $17, $61, $64; Conveyor Belt - moves right
	.byte $00 | $0F, $74, $E1, $61; Horizontally oriented X-blocks
	.byte $00 | $15, $70, $E0, $25; Horizontally oriented X-blocks
	.byte $00 | $1A, $70, $E0, $15; Horizontally oriented X-blocks
	.byte $00 | $16, $70, $E3, $03; Horizontally oriented X-blocks
	.byte $00 | $18, $74, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $7E, $E3, $07; Horizontally oriented X-blocks
	.byte $20 | $12, $7E, $02; '?' with star
	.byte $20 | $15, $79, $0E; Invisible Coin
	.byte $20 | $15, $7A, $0E; Invisible Coin
	.byte $20 | $15, $7B, $0F; Invisible 1-up
	.byte $00 | $18, $7D, $00; Door
	.byte $00 | $12, $72, $62; Dungeon windows
	.byte $00 | $16, $86, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $17, $88, $E1, $0D; Horizontally oriented X-blocks
	.byte $60 | $1A, $86, $69; Conveyor Belt - moves right
	.byte $00 | $18, $89, $DB; Ceiling Spikes
	.byte $20 | $11, $81, $11; Bricks
	.byte $20 | $12, $81, $11; Bricks
	.byte $20 | $13, $81, $11; Bricks
	.byte $20 | $14, $81, $11; Bricks
	.byte $00 | $12, $87, $63; Dungeon windows
	.byte $00 | $18, $86, $00; Door
	.byte $60 | $1A, $90, $68; Conveyor Belt - moves right
	.byte $60 | $15, $96, $68; Conveyor Belt - moves right
	.byte $20 | $13, $9C, $03; '?' with continuous star
	.byte $00 | $18, $97, $00; Door
	.byte $00 | $1A, $9C, $E0, $16; Horizontally oriented X-blocks
	.byte $00 | $16, $A4, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $17, $A3, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $A2, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $19, $A1, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $15, $A5, $E0, $18; Horizontally oriented X-blocks
	.byte $00 | $18, $AC, $00; Door
	.byte $00 | $14, $A2, $02; Rotodisc block
	.byte $00 | $1A, $B4, $E0, $1B; Horizontally oriented X-blocks
	.byte $00 | $16, $BC, $E3, $01; Horizontally oriented X-blocks
	.byte $00 | $11, $B4, $E1, $07; Horizontally oriented X-blocks
	.byte $00 | $16, $B7, $02; Rotodisc block
	.byte $20 | $17, $BB, $0B; Brick with 1-up
	.byte $20 | $15, $BE, $10; Bricks
	.byte $00 | $19, $BE, $E0, $00; Horizontally oriented X-blocks
	.byte $20 | $15, $BF, $0D; Brick with P-Switch
	.byte $60 | $15, $C0, $5A; Conveyor Belt - moves left
	.byte $00 | $18, $C3, $00; Door
	.byte $00 | $15, $CE, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $11, $CF, $E9, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $C4, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $0F, $D0, $FF, $0B; Vertically oriented X-blocks
	.byte $FF
Dungeon__White_Side__W8_objects:
	.byte $9E, $14, $13; Podoboo (comes out of lava)
	.byte $9E, $1E, $11; Podoboo (comes out of lava)
	.byte $8A, $2E, $10; Thwomp (normal)
	.byte $9E, $32, $12; Podoboo (comes out of lava)
	.byte $9E, $38, $13; Podoboo (comes out of lava)
	.byte $08, $3B, $15; Invisible door (appears when you hit a P-switch)
	.byte $9E, $3C, $12; Podoboo (comes out of lava)
	.byte $9E, $49, $13; Podoboo (comes out of lava)
	.byte $9E, $4E, $12; Podoboo (comes out of lava)
	.byte $8A, $52, $10; Thwomp (normal)
	.byte $9E, $57, $13; Podoboo (comes out of lava)
	.byte $9E, $5C, $10; Podoboo (comes out of lava)
	.byte $9E, $5E, $13; Podoboo (comes out of lava)
	.byte $9E, $69, $12; Podoboo (comes out of lava)
	.byte $08, $74, $16; Invisible door (appears when you hit a P-switch)
	.byte $5E, $A2, $14; Double Rotodisc (rotates both ways, starting at sides)
	.byte $08, $AA, $13; Invisible door (appears when you hit a P-switch)
	.byte $2F, $B2, $12; Boo Buddy
	.byte $60, $B7, $16; Double Rotodisc (rotates clockwise)
	.byte $08, $C4, $13; Invisible door (appears when you hit a P-switch)
	.byte $8B, $CD, $18; Thwomp (moves left)
	.byte $08, $CE, $13; Invisible door (appears when you hit a P-switch)
	.byte $FF
; Default_Level_297
; Object Set 1
Default_Level_297_generators:
Default_Level_297_header:
	.byte $CF; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_14; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $BF, $01; Blue X-Blocks
	.byte $40 | $10, $00, $B9, $01; Blue X-Blocks
	.byte $00 | $1A, $00, $D0, $2F; Underwater Flat Ground
	.byte $40 | $00, $04, $BF, $01; Blue X-Blocks
	.byte $40 | $0A, $06, $B0, $00; Blue X-Blocks
	.byte $40 | $0B, $06, $B4, $01; Blue X-Blocks
	.byte $40 | $0C, $08, $B0, $00; Blue X-Blocks
	.byte $40 | $0D, $08, $B2, $01; Blue X-Blocks
	.byte $40 | $0E, $0A, $B0, $00; Blue X-Blocks
	.byte $40 | $0F, $0A, $B0, $01; Blue X-Blocks
	.byte $40 | $00, $06, $B0, $29; Blue X-Blocks
	.byte $40 | $01, $0F, $BF, $01; Blue X-Blocks
	.byte $40 | $05, $0C, $B3, $03; Blue X-Blocks
	.byte $40 | $06, $0B, $B2, $00; Blue X-Blocks
	.byte $40 | $07, $0A, $B1, $00; Blue X-Blocks
	.byte $20 | $08, $09, $07; Brick with Leaf
	.byte $40 | $11, $0E, $B8, $02; Blue X-Blocks
	.byte $40 | $12, $0D, $B7, $00; Blue X-Blocks
	.byte $40 | $13, $0C, $B6, $00; Blue X-Blocks
	.byte $40 | $14, $0B, $B5, $00; Blue X-Blocks
	.byte $40 | $15, $0A, $B4, $00; Blue X-Blocks
	.byte $40 | $16, $09, $B3, $00; Blue X-Blocks
	.byte $40 | $17, $08, $B2, $00; Blue X-Blocks
	.byte $40 | $18, $07, $B1, $00; Blue X-Blocks
	.byte $40 | $19, $06, $B0, $00; Blue X-Blocks
	.byte $20 | $00, $02, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $00, $0D, $C2; Upward Pipe (CAN go up)
	.byte $40 | $00, $10, $BF, $0F; Blue X-Blocks
	.byte $40 | $10, $10, $B9, $0F; Blue X-Blocks
	.byte $40 | $00, $20, $BF, $00; Blue X-Blocks
	.byte $40 | $10, $20, $B9, $00; Blue X-Blocks
	.byte $40 | $00, $2E, $BF, $01; Blue X-Blocks
	.byte $40 | $10, $2E, $B9, $01; Blue X-Blocks
	.byte $40 | $05, $21, $B0, $02; Blue X-Blocks
	.byte $20 | $08, $23, $89; Coins
	.byte $20 | $09, $23, $89; Coins
	.byte $20 | $0A, $23, $89; Coins
	.byte $20 | $0B, $23, $89; Coins
	.byte $20 | $0C, $23, $89; Coins
	.byte $20 | $0D, $23, $89; Coins
	.byte $20 | $0E, $23, $89; Coins
	.byte $20 | $0F, $23, $89; Coins
	.byte $20 | $10, $23, $89; Coins
	.byte $20 | $11, $23, $89; Coins
	.byte $20 | $00, $21, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $18, $2D, $E1; Rightward Pipe (CAN go in)
	; Pointer on screen $00
	.byte $E0 | $00, $40 | $01, 57; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $02
	.byte $E0 | $02, $40 | $01, 57; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_297_objects:
	.byte $FF
; Tank__2_Boss_Room_W8
; Object Set 10
Tank__2_Boss_Room_W8_generators:
Tank__2_Boss_Room_W8_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_000; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0A; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $00 | $00, $00, $0F; Black boss room background
	.byte $00 | $0F, $00, $1F; Wooden Ship Beam
	.byte $00 | $10, $00, $4A; Wooden Ship Pillar
	.byte $00 | $10, $0F, $4A; Wooden Ship Pillar
	.byte $00 | $19, $01, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $03, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $05, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $07, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $09, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $0B, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $0D, $61; Thick Wooden Ship Beam
	.byte $00 | $0F, $01, $41; Wooden Ship Pillar
	.byte $00 | $0F, $02, $41; Wooden Ship Pillar
	.byte $FF
Tank__2_Boss_Room_W8_objects:
	.byte $4C, $0C, $47; Flying Boom Boom
	.byte $FF
; Bowser's_Lair_W8
; Object Set 2
Bowser's_Lair_W8_generators:
Bowser's_Lair_W8_header:
	.byte $D4; Next Level
	.byte LEVEL1_SIZE_15 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $40 | $0E, $00, $AA, $24; Background used in Bowser's Castle
	.byte $60 | $0E, $2D, $3A, $C2; Blank Background (used to block out stuff)
	.byte $60 | $19, $60, $31, $1F; Blank Background (used to block out stuff)
	.byte $60 | $19, $C0, $31, $2F; Blank Background (used to block out stuff)
	.byte $60 | $0E, $00, $D6, $10; Red Bricks - found in Bowser's Castle
	.byte $60 | $15, $00, $D3, $01; Red Bricks - found in Bowser's Castle
	.byte $60 | $19, $00, $D1, $2C; Red Bricks - found in Bowser's Castle
	.byte $00 | $17, $03, $00; Door
	.byte $60 | $0E, $11, $D0, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $0E, $14, $D1, $CF; Red Bricks - found in Bowser's Castle
	.byte $60 | $10, $1E, $D0, $20; Red Bricks - found in Bowser's Castle
	.byte $60 | $11, $1F, $D0, $1D; Red Bricks - found in Bowser's Castle
	.byte $60 | $12, $14, $D6, $05; Red Bricks - found in Bowser's Castle
	.byte $60 | $13, $1A, $D5, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $14, $1B, $D4, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $15, $1C, $D3, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $16, $1D, $D2, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $17, $1E, $D1, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $18, $1F, $D0, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $12, $20, $D0, $1B; Red Bricks - found in Bowser's Castle
	.byte $60 | $13, $21, $D0, $19; Red Bricks - found in Bowser's Castle
	.byte $60 | $14, $22, $D0, $18; Red Bricks - found in Bowser's Castle
	.byte $60 | $15, $25, $D3, $0F; Red Bricks - found in Bowser's Castle
	.byte $00 | $17, $40, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $45, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $4C, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $15, $40, $05; Bowser Statue
	.byte $00 | $16, $45, $05; Bowser Statue
	.byte $00 | $14, $4C, $05; Bowser Statue
	.byte $00 | $11, $42, $63; Dungeon windows
	.byte $60 | $10, $51, $D0, $0E; Red Bricks - found in Bowser's Castle
	.byte $60 | $11, $53, $D0, $0A; Red Bricks - found in Bowser's Castle
	.byte $60 | $12, $54, $D0, $08; Red Bricks - found in Bowser's Castle
	.byte $60 | $13, $55, $D1, $06; Red Bricks - found in Bowser's Castle
	.byte $60 | $18, $5E, $D0, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $17, $5F, $D3, $01; Red Bricks - found in Bowser's Castle
	.byte $00 | $17, $52, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $15, $52, $05; Bowser Statue
	.byte $00 | $16, $56, $61; Dungeon windows
	.byte $60 | $1A, $61, $40, $1A; Lava
	.byte $00 | $11, $64, $65; Dungeon windows
	.byte $00 | $11, $6C, $71; Long dungeon windows
	.byte $60 | $17, $65, $E1; Donut Blocks
	.byte $60 | $18, $6C, $E1; Donut Blocks
	.byte $60 | $10, $7D, $D3, $07; Red Bricks - found in Bowser's Castle
	.byte $60 | $13, $7C, $D0, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $19, $7B, $D1, $04; Red Bricks - found in Bowser's Castle
	.byte $00 | $11, $7C, $05; Bowser Statue
	.byte $60 | $14, $72, $E1; Donut Blocks
	.byte $60 | $17, $77, $E0; Donut Blocks
	.byte $60 | $0F, $85, $DB, $07; Red Bricks - found in Bowser's Castle
	.byte $60 | $0F, $8D, $D9, $07; Red Bricks - found in Bowser's Castle
	.byte $60 | $17, $81, $D3, $03; Red Bricks - found in Bowser's Castle
	.byte $60 | $18, $80, $D2, $00; Red Bricks - found in Bowser's Castle
	.byte $00 | $15, $83, $00; Door
	.byte $60 | $0F, $95, $D6, $09; Red Bricks - found in Bowser's Castle
	.byte $60 | $10, $9F, $D0, $05; Red Bricks - found in Bowser's Castle
	.byte $60 | $11, $9F, $D0, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $12, $9F, $D0, $01; Red Bricks - found in Bowser's Castle
	.byte $60 | $13, $9F, $D0, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $10, $AD, $D0, $08; Red Bricks - found in Bowser's Castle
	.byte $60 | $11, $AF, $D0, $05; Red Bricks - found in Bowser's Castle
	.byte $60 | $15, $A9, $D0, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $16, $A8, $D0, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $17, $A7, $D0, $04; Red Bricks - found in Bowser's Castle
	.byte $60 | $18, $A3, $D0, $09; Red Bricks - found in Bowser's Castle
	.byte $00 | $11, $A7, $61; Dungeon windows
	.byte $00 | $13, $A9, $05; Bowser Statue
	.byte $00 | $16, $A3, $05; Bowser Statue
	.byte $20 | $14, $AC, $01; '?' with leaf
	.byte $60 | $12, $B1, $D0, $01; Red Bricks - found in Bowser's Castle
	.byte $60 | $13, $B1, $D1, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $15, $B0, $D0, $01; Red Bricks - found in Bowser's Castle
	.byte $60 | $17, $B4, $D1, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $14, $BD, $D0, $06; Red Bricks - found in Bowser's Castle
	.byte $60 | $15, $BC, $D0, $07; Red Bricks - found in Bowser's Castle
	.byte $60 | $16, $BB, $D0, $08; Red Bricks - found in Bowser's Castle
	.byte $60 | $17, $BA, $D0, $09; Red Bricks - found in Bowser's Castle
	.byte $60 | $18, $B9, $D0, $0A; Red Bricks - found in Bowser's Castle
	.byte $60 | $19, $B9, $D1, $0E; Red Bricks - found in Bowser's Castle
	.byte $00 | $11, $BA, $62; Dungeon windows
	.byte $00 | $13, $B0, $05; Bowser Statue
	.byte $00 | $13, $BC, $05; Bowser Statue
	.byte $00 | $15, $B4, $05; Bowser Statue
	.byte $60 | $10, $C5, $D0, $02; Red Bricks - found in Bowser's Castle
	.byte $60 | $11, $C6, $D5, $00; Red Bricks - found in Bowser's Castle
	.byte $00 | $11, $CA, $71; Long dungeon windows
	.byte $60 | $18, $CC, $D0, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $1A, $C8, $40, $1C; Lava
	.byte $60 | $15, $DC, $D0, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $17, $D2, $D0, $01; Red Bricks - found in Bowser's Castle
	.byte $60 | $18, $D9, $D0, $00; Red Bricks - found in Bowser's Castle
	.byte $00 | $12, $D2, $61; Dungeon windows
	.byte $00 | $11, $DA, $71; Long dungeon windows
	.byte $60 | $0F, $E4, $D1, $0B; Red Bricks - found in Bowser's Castle
	.byte $60 | $11, $E6, $D1, $09; Red Bricks - found in Bowser's Castle
	.byte $60 | $13, $E6, $D0, $01; Red Bricks - found in Bowser's Castle
	.byte $60 | $14, $E5, $D0, $01; Red Bricks - found in Bowser's Castle
	.byte $60 | $13, $EF, $D2, $00; Red Bricks - found in Bowser's Castle
	.byte $60 | $16, $EC, $D0, $03; Red Bricks - found in Bowser's Castle
	.byte $60 | $17, $EB, $D0, $04; Red Bricks - found in Bowser's Castle
	.byte $60 | $18, $EA, $D0, $05; Red Bricks - found in Bowser's Castle
	.byte $60 | $19, $E4, $D1, $0B; Red Bricks - found in Bowser's Castle
	.byte $60 | $18, $E0, $D0, $00; Red Bricks - found in Bowser's Castle
	.byte $00 | $12, $E5, $05; Bowser Statue
	.byte $00 | $14, $ED, $00; Door
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $08, 32; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $08
	.byte $E0 | $08, $50 | $08, 28; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $0E
	.byte $E0 | $0E, $50 | $08, 30; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Bowser's_Lair_W8_objects:
	.byte $3F, $04, $18; Dry Bones
	.byte $3F, $0A, $18; Dry Bones
	.byte $8C, $16, $10; Thwomp (moves right)
	.byte $D0, $40, $15; Lasers (use with Bowser statues)
	.byte $75, $62, $16; Bowser's Fireballs
	.byte $75, $6C, $16; Bowser's Fireballs
	.byte $75, $73, $17; Bowser's Fireballs
	.byte $75, $7E, $15; Bowser's Fireballs
	.byte $D0, $A3, $16; Lasers (use with Bowser statues)
	.byte $75, $D1, $17; Bowser's Fireballs
	.byte $75, $D6, $16; Bowser's Fireballs
	.byte $75, $D9, $16; Bowser's Fireballs
	.byte $75, $E1, $14; Bowser's Fireballs
	.byte $75, $E5, $17; Bowser's Fireballs
	.byte $FF
; Default_Level_348_348
; Object Set 1
Default_Level_348_348_generators:
Default_Level_348_348_header:
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
Default_Level_348_348_objects:
	.byte $FF
; Default_Level_349_349
; Object Set 1
Default_Level_349_349_generators:
Default_Level_349_349_header:
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
Default_Level_349_349_objects:
	.byte $FF
; Default_Level_350_350
; Object Set 1
Default_Level_350_350_generators:
Default_Level_350_350_header:
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
Default_Level_350_350_objects:
	.byte $FF
; Default_Level_351_351
; Object Set 1
Default_Level_351_351_generators:
Default_Level_351_351_header:
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
Default_Level_351_351_objects:
	.byte $FF
; Default_Level_352_352
; Object Set 1
Default_Level_352_352_generators:
Default_Level_352_352_header:
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
Default_Level_352_352_objects:
	.byte $FF
; Default_Level_353_353
; Object Set 1
Default_Level_353_353_generators:
Default_Level_353_353_header:
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
Default_Level_353_353_objects:
	.byte $FF
; Default_Level_354_354
; Object Set 1
Default_Level_354_354_generators:
Default_Level_354_354_header:
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
Default_Level_354_354_objects:
	.byte $FF
; Default_Level_355_355
; Object Set 1
Default_Level_355_355_generators:
Default_Level_355_355_header:
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
Default_Level_355_355_objects:
	.byte $FF
; Default_Level_356_356
; Object Set 1
Default_Level_356_356_generators:
Default_Level_356_356_header:
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
Default_Level_356_356_objects:
	.byte $FF
; Default_Level_357_357
; Object Set 1
Default_Level_357_357_generators:
Default_Level_357_357_header:
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
Default_Level_357_357_objects:
	.byte $FF
; Default_Level_358_358
; Object Set 1
Default_Level_358_358_generators:
Default_Level_358_358_header:
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
Default_Level_358_358_objects:
	.byte $FF
; Default_Level_359_359
; Object Set 1
Default_Level_359_359_generators:
Default_Level_359_359_header:
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
Default_Level_359_359_objects:
	.byte $FF
; Default_Level_360_360
; Object Set 1
Default_Level_360_360_generators:
Default_Level_360_360_header:
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
Default_Level_360_360_objects:
	.byte $FF