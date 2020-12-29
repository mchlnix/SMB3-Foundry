; Bank 1

; Level_3_W1
; Object Set 1
Level_3_W1_generators:
Level_3_W1_header:
	.byte $19; Next Level
	.byte LEVEL1_SIZE_10 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_13; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	.byte $00 | $18, $0B, $64; Orange Block Platform (Floating)
	.byte $00 | $1A, $00, $C0, $4F; Flat Ground
	.byte $00 | $14, $07, $E3; Background Clouds
	.byte $00 | $15, $0E, $84; Blue Block Platform (Floating)
	.byte $00 | $19, $04, $93; Background Bushes
	.byte $00 | $10, $1B, $E2; Background Clouds
	.byte $00 | $12, $15, $02; Background Hills C
	.byte $00 | $19, $1D, $91; Background Bushes
	.byte $20 | $17, $1E, $60; Note Blocks - movable two directions
	.byte $00 | $12, $29, $02; Background Hills C
	.byte $20 | $15, $20, $60; Note Blocks - movable two directions
	.byte $20 | $15, $25, $13; Bricks
	.byte $20 | $16, $20, $12; Bricks
	.byte $20 | $16, $25, $11; Bricks
	.byte $20 | $16, $28, $10; Bricks
	.byte $20 | $17, $20, $14; Bricks
	.byte $40 | $17, $22, $07; Red Invisible Note Block
	.byte $20 | $17, $28, $20; '?' Blocks with single coins
	.byte $20 | $18, $20, $11; Bricks
	.byte $20 | $18, $24, $14; Bricks
	.byte $20 | $19, $20, $12; Bricks
	.byte $20 | $19, $26, $12; Bricks
	.byte $20 | $16, $2D, $43; Wooden Blocks
	.byte $20 | $18, $21, $20; '?' Blocks with single coins
	.byte $20 | $15, $26, $0A; Multi-Coin Brick
	.byte $20 | $15, $27, $10; Bricks
	.byte $20 | $18, $25, $07; Brick with Leaf
	.byte $00 | $11, $34, $E2; Background Clouds
	.byte $00 | $14, $38, $E3; Background Clouds
	.byte $20 | $14, $3F, $82; Coins
	.byte $00 | $17, $36, $01; Background Hills B
	.byte $00 | $19, $3A, $90; Background Bushes
	.byte $20 | $16, $34, $40; Wooden Blocks
	.byte $20 | $17, $34, $40; Wooden Blocks
	.byte $20 | $18, $34, $40; Wooden Blocks
	.byte $20 | $19, $34, $40; Wooden Blocks
	.byte $40 | $17, $3C, $05; Wooden Block with Leaf
	.byte $20 | $18, $3C, $40; Wooden Blocks
	.byte $20 | $19, $3C, $40; Wooden Blocks
	.byte $00 | $11, $43, $E4; Background Clouds
	.byte $20 | $14, $47, $82; Coins
	.byte $00 | $16, $46, $00; Background Hills A
	.byte $00 | $17, $4B, $01; Background Hills B
	.byte $00 | $19, $40, $92; Background Bushes
	.byte $20 | $16, $44, $40; Wooden Blocks
	.byte $20 | $17, $44, $40; Wooden Blocks
	.byte $20 | $18, $44, $40; Wooden Blocks
	.byte $20 | $19, $44, $40; Wooden Blocks
	.byte $20 | $16, $4C, $40; Wooden Blocks
	.byte $20 | $17, $4C, $40; Wooden Blocks
	.byte $20 | $18, $4C, $40; Wooden Blocks
	.byte $20 | $19, $4C, $40; Wooden Blocks
	.byte $00 | $1A, $51, $C0, $0A; Flat Ground
	.byte $00 | $1A, $5D, $C0, $42; Flat Ground
	.byte $00 | $12, $55, $02; Background Hills C
	.byte $00 | $13, $5B, $E3; Background Clouds
	.byte $00 | $11, $62, $74; Green Block Platform (Floating)
	.byte $00 | $13, $6C, $84; Blue Block Platform (Floating)
	.byte $00 | $15, $67, $54; White Block Platform (Floating)
	.byte $00 | $16, $6E, $75; Green Block Platform (Floating)
	.byte $00 | $17, $61, $65; Orange Block Platform (Floating)
	.byte $20 | $11, $6C, $82; Coins
	.byte $20 | $13, $68, $80; Coins
	.byte $20 | $15, $63, $80; Coins
	.byte $00 | $19, $67, $95; Background Bushes
	.byte $00 | $12, $79, $43; Blue Block Platform (Extends to ground)
	.byte $00 | $14, $74, $64; Orange Block Platform (Floating)
	.byte $00 | $19, $74, $91; Background Bushes
	.byte $00 | $12, $83, $02; Background Hills C
	.byte $00 | $17, $80, $01; Background Hills B
	.byte $00 | $00, $81, $B5; Cloud Platform
	.byte $20 | $01, $83, $D4; Upward Pipe (CAN'T go up)
	.byte $40 | $00, $8B, $09; Level Ending
	; Pointer on screen $02
	.byte $E0 | $02, $70 | $07, 128; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $09
	.byte $E0 | $09, $70 | $07, 128; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_3_W1_objects:
	.byte $6C, $0D, $19; Green Koopa Troopa
	.byte $82, $15, $18; Boomerang Brother
	.byte $6D, $27, $14; Red Koopa Troopa
	.byte $6C, $32, $18; Green Koopa Troopa
	.byte $72, $3A, $19; Goomba
	.byte $73, $42, $19; Para-Goomba
	.byte $73, $4A, $19; Para-Goomba
	.byte $82, $57, $17; Boomerang Brother
	.byte $72, $65, $19; Goomba
	.byte $72, $67, $19; Goomba
	.byte $6D, $68, $13; Red Koopa Troopa
	.byte $74, $79, $19; Para-Goomba with Micro-Goombas
	.byte $6C, $78, $18; Green Koopa Troopa
	.byte $07, $96, $18; Mushroom House with Warp Whistle entrance
	.byte $41, $98, $15; Goal Card
	.byte $FF
; Default_Level_86
; Object Set 4
Default_Level_86_generators:
Default_Level_86_header:
	.byte $1A; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_12; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $40 | $19, $00, $81, $7F; Water (still)
	.byte $60 | $16, $00, $85; Weird
	.byte $00 | $12, $05, $C2; Weird
	.byte $60 | $13, $0C, $12; Weird
	.byte $20 | $10, $0C, $82; Coins
	.byte $00 | $11, $13, $C2; Weird
	.byte $20 | $13, $16, $82; Coins
	.byte $60 | $16, $12, $1C; Weird
	.byte $20 | $13, $1D, $82; Coins
	.byte $20 | $15, $25, $40; Wooden blocks
	.byte $00 | $12, $26, $C2; Weird
	.byte $60 | $15, $24, $10; Weird
	.byte $60 | $16, $28, $14; Weird
	.byte $20 | $13, $2A, $00; '?' with flower
	.byte $60 | $14, $31, $11; Weird
	.byte $60 | $16, $37, $82; Weird
	.byte $20 | $14, $38, $81; Coins
	.byte $20 | $14, $3B, $80; Coins
	.byte $60 | $16, $42, $82; Weird
	.byte $00 | $10, $42, $C2; Weird
	.byte $20 | $13, $46, $81; Coins
	.byte $20 | $13, $4B, $82; Coins
	.byte $20 | $14, $4F, $30; Bricks with single coins
	.byte $60 | $12, $50, $13; Weird
	.byte $60 | $13, $54, $10; Weird
	.byte $60 | $14, $55, $10; Weird
	.byte $60 | $15, $56, $10; Weird
	.byte $60 | $16, $57, $11; Weird
	.byte $00 | $17, $5F, $07; Blue gear
	.byte $00 | $11, $5E, $95; 1 platform wire
	.byte $00 | $10, $5F, $80; Horizontal platform wire
	.byte $00 | $11, $60, $A5; 45 Degree Platform Wire - Down/Right
	.byte $00 | $16, $66, $83; Horizontal platform wire
	.byte $00 | $15, $6A, $E0; 60 Degree Platform Wire - Down/Left
	.byte $00 | $14, $6B, $B0; 45 Degree Platform Wire - Up/Right
	.byte $00 | $13, $6C, $82; Horizontal platform wire
	.byte $00 | $14, $6F, $D1; 60 Degree Platform Wire - Down/Right
	.byte $00 | $14, $72, $E1; 60 Degree Platform Wire - Down/Left
	.byte $00 | $13, $73, $83; Horizontal platform wire
	.byte $20 | $14, $67, $40; Wooden blocks
	.byte $00 | $12, $63, $C2; Weird
	.byte $20 | $0F, $70, $82; Coins
	.byte $20 | $12, $71, $60; Note Blocks - movable two directions
	.byte $00 | $10, $75, $C2; Weird
	.byte $20 | $14, $7C, $92; Downward Pipe (CAN go down)
	.byte $60 | $17, $7C, $80; Weird
	.byte $60 | $00, $7E, $11; Weird
	.byte $60 | $01, $7E, $80; Weird
	.byte $60 | $03, $7E, $80; Weird
	.byte $60 | $05, $7E, $80; Weird
	.byte $60 | $07, $7E, $80; Weird
	.byte $60 | $09, $7E, $80; Weird
	.byte $60 | $0B, $7E, $80; Weird
	.byte $60 | $0D, $7E, $80; Weird
	.byte $60 | $0F, $7E, $80; Weird
	.byte $60 | $11, $7E, $80; Weird
	.byte $60 | $13, $7E, $80; Weird
	.byte $60 | $15, $7E, $80; Weird
	.byte $60 | $17, $7E, $80; Weird
	.byte $60 | $16, $7B, $10; Weird
	; Pointer on screen $07
	.byte $E0 | $07, $40 | $02, 128; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_86_objects:
	.byte $D3, $00, $53; Autoscrolling
	.byte $64, $11, $19; Surface Cheep-Cheep (jumps out of water)
	.byte $64, $19, $19; Surface Cheep-Cheep (jumps out of water)
	.byte $64, $23, $19; Surface Cheep-Cheep (jumps out of water)
	.byte $58, $40, $13; Fire Chomp
	.byte $6F, $4B, $12; Red Koopa Paratroopa
	.byte $59, $57, $10; Fire Snake
	.byte $44, $5D, $15; Falling Platform (falls when stepped on)
	.byte $58, $6B, $11; Fire Chomp
	.byte $64, $6B, $19; Surface Cheep-Cheep (jumps out of water)
	.byte $43, $76, $19; Jumping Cheep-Cheep (2 jumps, down and right)
	.byte $FF
; Level_4_W1
; Object Set 4
Level_4_W1_generators:
Level_4_W1_header:
	.byte $1B; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $04; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $16, $00, $69; Green platform
	.byte $00 | $15, $04, $44; Background Bushes
	.byte $20 | $16, $0E, $13; Bricks
	.byte $00 | $10, $0A, $01; Large Swirly Background Cloud
	.byte $00 | $12, $01, $01; Large Swirly Background Cloud
	.byte $00 | $13, $06, $00; Small Swirly Background Cloud
	.byte $00 | $19, $0E, $01; Large Swirly Background Cloud
	.byte $20 | $11, $1A, $82; Coins
	.byte $20 | $13, $15, $82; Coins
	.byte $20 | $15, $18, $14; Bricks
	.byte $00 | $12, $11, $00; Small Swirly Background Cloud
	.byte $00 | $13, $1A, $01; Large Swirly Background Cloud
	.byte $00 | $17, $1F, $00; Small Swirly Background Cloud
	.byte $00 | $18, $18, $00; Small Swirly Background Cloud
	.byte $20 | $12, $26, $13; Bricks
	.byte $20 | $17, $28, $11; Bricks
	.byte $20 | $12, $28, $0B; Brick with 1-up
	.byte $00 | $11, $22, $01; Large Swirly Background Cloud
	.byte $00 | $11, $2C, $01; Large Swirly Background Cloud
	.byte $00 | $15, $2A, $00; Small Swirly Background Cloud
	.byte $20 | $14, $2F, $10; Bricks
	.byte $20 | $15, $2F, $10; Bricks
	.byte $20 | $16, $2F, $10; Bricks
	.byte $20 | $17, $2F, $13; Bricks
	.byte $20 | $15, $36, $10; Bricks
	.byte $20 | $16, $36, $10; Bricks
	.byte $20 | $17, $36, $10; Bricks
	.byte $20 | $18, $36, $12; Bricks
	.byte $20 | $15, $3B, $10; Bricks
	.byte $20 | $16, $3B, $11; Bricks
	.byte $20 | $16, $3F, $14; Bricks
	.byte $20 | $19, $3C, $13; Bricks
	.byte $20 | $11, $35, $82; Coins
	.byte $20 | $13, $30, $82; Coins
	.byte $20 | $16, $3F, $0A; Multi-Coin Brick
	.byte $00 | $13, $38, $01; Large Swirly Background Cloud
	.byte $00 | $19, $32, $01; Large Swirly Background Cloud
	.byte $00 | $14, $32, $00; Small Swirly Background Cloud
	.byte $00 | $18, $3A, $00; Small Swirly Background Cloud
	.byte $20 | $16, $3C, $07; Brick with Leaf
	.byte $20 | $13, $4A, $13; Bricks
	.byte $20 | $12, $4D, $0B; Brick with 1-up
	.byte $20 | $18, $48, $14; Bricks
	.byte $20 | $17, $4F, $11; Bricks
	.byte $00 | $11, $42, $01; Large Swirly Background Cloud
	.byte $00 | $15, $48, $01; Large Swirly Background Cloud
	.byte $00 | $10, $4F, $00; Small Swirly Background Cloud
	.byte $00 | $19, $49, $00; Small Swirly Background Cloud
	.byte $20 | $13, $57, $12; Bricks
	.byte $20 | $12, $53, $82; Coins
	.byte $20 | $11, $5E, $80; Coins
	.byte $20 | $12, $5E, $80; Coins
	.byte $20 | $13, $5E, $80; Coins
	.byte $20 | $14, $5E, $80; Coins
	.byte $20 | $15, $5E, $80; Coins
	.byte $20 | $16, $5E, $80; Coins
	.byte $20 | $17, $5E, $80; Coins
	.byte $20 | $18, $5E, $80; Coins
	.byte $00 | $12, $5B, $01; Large Swirly Background Cloud
	.byte $00 | $18, $53, $01; Large Swirly Background Cloud
	.byte $00 | $14, $56, $00; Small Swirly Background Cloud
	.byte $00 | $18, $5A, $00; Small Swirly Background Cloud
	.byte $20 | $12, $60, $0A; Multi-Coin Brick
	.byte $20 | $13, $60, $10; Bricks
	.byte $20 | $17, $60, $10; Bricks
	.byte $20 | $18, $60, $10; Bricks
	.byte $20 | $19, $60, $13; Bricks
	.byte $20 | $12, $6C, $10; Bricks
	.byte $20 | $13, $6C, $10; Bricks
	.byte $20 | $14, $6C, $10; Bricks
	.byte $20 | $17, $6F, $12; Bricks
	.byte $00 | $11, $6F, $00; Small Swirly Background Cloud
	.byte $00 | $13, $68, $00; Small Swirly Background Cloud
	.byte $00 | $19, $6C, $00; Small Swirly Background Cloud
	.byte $00 | $12, $62, $01; Large Swirly Background Cloud
	.byte $00 | $16, $66, $01; Large Swirly Background Cloud
	.byte $20 | $13, $76, $82; Coins
	.byte $00 | $19, $78, $27; Wooden block platform
	.byte $20 | $15, $79, $93; Downward Pipe (CAN go down)
	.byte $00 | $17, $7B, $62; Green platform
	.byte $00 | $11, $78, $01; Large Swirly Background Cloud
	.byte $00 | $16, $74, $01; Large Swirly Background Cloud
	.byte $00 | $13, $7D, $00; Small Swirly Background Cloud
	.byte $20 | $0F, $7F, $40; Wooden blocks
	.byte $20 | $10, $7F, $40; Wooden blocks
	.byte $20 | $11, $7F, $40; Wooden blocks
	.byte $20 | $12, $7F, $40; Wooden blocks
	.byte $20 | $13, $7F, $40; Wooden blocks
	.byte $20 | $14, $7F, $40; Wooden blocks
	.byte $20 | $15, $7F, $40; Wooden blocks
	.byte $20 | $16, $7F, $40; Wooden blocks
	.byte $20 | $17, $7F, $40; Wooden blocks
	.byte $20 | $18, $7F, $40; Wooden blocks
	; Pointer on screen $07
	.byte $E0 | $07, $70 | $01, 128; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_4_W1_objects:
	.byte $D3, $00, $00; Autoscrolling
	.byte $D4, $01, $2C; White Mushroom House (X pos must be uneven, Y pos=amount of coins required)
	.byte $36, $17, $14; Wooden platform - moves left,falls when stepped on
	.byte $36, $23, $16; Wooden platform - moves left,falls when stepped on
	.byte $36, $25, $13; Wooden platform - moves left,falls when stepped on
	.byte $36, $27, $19; Wooden platform - moves left,falls when stepped on
	.byte $36, $2F, $15; Wooden platform - moves left,falls when stepped on
	.byte $6D, $43, $15; Red Koopa Troopa
	.byte $36, $44, $18; Wooden platform - moves left,falls when stepped on
	.byte $36, $4B, $14; Wooden platform - moves left,falls when stepped on
	.byte $36, $56, $16; Wooden platform - moves left,falls when stepped on
	.byte $36, $58, $15; Wooden platform - moves left,falls when stepped on
	.byte $36, $61, $13; Wooden platform - moves left,falls when stepped on
	.byte $36, $6D, $18; Wooden platform - moves left,falls when stepped on
	.byte $36, $6F, $15; Wooden platform - moves left,falls when stepped on
	.byte $36, $70, $1A; Wooden platform - moves left,falls when stepped on
	.byte $6F, $75, $13; Red Koopa Paratroopa
	.byte $6D, $7C, $16; Red Koopa Troopa
	.byte $FF
; Dungeon_W1
; Object Set 2
Dungeon_W1_generators:
Dungeon_W1_header:
	.byte $1C; Next Level
	.byte LEVEL1_SIZE_10 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $0E, $00, $3C, $9F; Blank Background (used to block out stuff)
	.byte $00 | $00, $00, $EF, $9F; Horizontally oriented X-blocks
	.byte $00 | $10, $00, $E5, $09; Horizontally oriented X-blocks
	.byte $00 | $10, $0A, $E4, $00; Horizontally oriented X-blocks
	.byte $00 | $10, $0B, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $10, $0C, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $0E, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $17, $0D, $E0, $03; Horizontally oriented X-blocks
	.byte $00 | $18, $0C, $E0, $04; Horizontally oriented X-blocks
	.byte $00 | $19, $00, $E1, $10; Horizontally oriented X-blocks
	.byte $60 | $19, $11, $31, $18; Blank Background (used to block out stuff)
	.byte $60 | $1A, $11, $40, $18; Lava
	.byte $00 | $15, $14, $E5, $03; Horizontally oriented X-blocks
	.byte $00 | $19, $1A, $E1, $03; Horizontally oriented X-blocks
	.byte $00 | $18, $1C, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $1D, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $21, $E0, $04; Horizontally oriented X-blocks
	.byte $00 | $16, $2A, $E2, $02; Horizontally oriented X-blocks
	.byte $00 | $17, $2D, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $2E, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $19, $2A, $E1, $26; Horizontally oriented X-blocks
	.byte $20 | $14, $24, $00; '?' with flower
	.byte $00 | $10, $2F, $E5, $0F; Horizontally oriented X-blocks
	.byte $00 | $15, $38, $02; Rotodisc block
	.byte $00 | $16, $43, $E0, $0A; Horizontally oriented X-blocks
	.byte $00 | $17, $42, $E0, $0C; Horizontally oriented X-blocks
	.byte $00 | $18, $41, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $16, $47, $02; Rotodisc block
	.byte $00 | $12, $4A, $61; Dungeon windows
	.byte $60 | $1A, $51, $40, $0E; Lava
	.byte $00 | $18, $55, $E2, $01; Horizontally oriented X-blocks
	.byte $00 | $17, $5A, $E3, $02; Horizontally oriented X-blocks
	.byte $00 | $17, $5B, $02; Rotodisc block
	.byte $60 | $04, $51, $3B, $11; Blank Background (used to block out stuff)
	.byte $00 | $18, $60, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $19, $60, $E1, $3F; Horizontally oriented X-blocks
	.byte $00 | $10, $63, $E0, $2C; Horizontally oriented X-blocks
	.byte $20 | $16, $62, $01; '?' with leaf
	.byte $00 | $11, $64, $E0, $2B; Horizontally oriented X-blocks
	.byte $00 | $12, $66, $E0, $29; Horizontally oriented X-blocks
	.byte $00 | $13, $68, $E0, $27; Horizontally oriented X-blocks
	.byte $00 | $14, $6B, $E0, $24; Horizontally oriented X-blocks
	.byte $00 | $15, $6F, $E3, $0A; Horizontally oriented X-blocks
	.byte $00 | $15, $61, $62; Dungeon windows
	.byte $00 | $17, $6D, $00; Door
	.byte $60 | $04, $63, $32, $0F; Blank Background (used to block out stuff)
	.byte $00 | $16, $7E, $64; Dungeon windows
	.byte $00 | $05, $72, $00; Door
	.byte $00 | $12, $93, $62; Dungeon windows
	.byte $00 | $10, $9F, $E8, $00; Horizontally oriented X-blocks
	; Pointer on screen $07
	.byte $E0 | $07, $40 | $08, 84; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $06
	.byte $E0 | $06, $60 | $08, 16; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon_W1_objects:
	.byte $9E, $12, $12; Podoboo (comes out of lava)
	.byte $9E, $18, $12; Podoboo (comes out of lava)
	.byte $9E, $1F, $12; Podoboo (comes out of lava)
	.byte $9E, $27, $11; Podoboo (comes out of lava)
	.byte $5B, $38, $15; Single Rotodisc (rotates counterclockwise)
	.byte $5A, $47, $16; Single Rotodisc (rotates clockwise)
	.byte $9E, $51, $11; Podoboo (comes out of lava)
	.byte $9E, $53, $14; Podoboo (comes out of lava)
	.byte $9E, $5E, $11; Podoboo (comes out of lava)
	.byte $5A, $5B, $17; Single Rotodisc (rotates clockwise)
	.byte $3F, $6B, $18; Dry Bones
	.byte $4B, $9D, $17; Boom Boom
	.byte $FF
; Level_5_W1
; Object Set 14
Level_5_W1_generators:
Level_5_W1_header:
	.byte $1D; Next Level
	.byte LEVEL1_SIZE_09 | LEVEL1_YSTART_040; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_13; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $20 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $00, $00, $1B, $77; Sky Fill
	.byte $80 | $18, $17, $31, $08; Water
	.byte $80 | $17, $3C, $32, $18; Water
	.byte $60 | $05, $00, $12; 30 Degree Aboveground Hill - Down/Right
	.byte $80 | $08, $00, $43, $05; Aboveground Fill
	.byte $00 | $08, $06, $13; 45 Degree Aboveground Hill - Down/Right
	.byte $80 | $0C, $00, $5E, $09; Hilly Fill
	.byte $00 | $0C, $0A, $5A; 45 Degree Hill - Down/Right
	.byte $80 | $17, $0A, $53, $0A; Hilly Fill
	.byte $00 | $00, $0F, $DB; Aboveground Wall - Left Side
	.byte $00 | $0C, $0F, $74; 45 Degree Hill - Up/Left
	.byte $80 | $01, $06, $00; Small Background Cloud
	.byte $80 | $04, $04, $00; Small Background Cloud
	.byte $80 | $05, $0D, $00; Small Background Cloud
	.byte $80 | $06, $08, $00; Small Background Cloud
	.byte $80 | $00, $10, $4B, $23; Aboveground Fill
	.byte $80 | $0C, $14, $B4, $0E; Ceiling - Hilly
	.byte $80 | $17, $15, $83, $01; Flat Land - Hilly
	.byte $00 | $17, $16, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $18, $16, $F1; Underground Wall - Right Side
	.byte $80 | $1A, $17, $90, $06; Flat Land - Underwater
	.byte $80 | $1A, $1E, $50, $06; Hilly Fill
	.byte $00 | $13, $24, $66; 45 Degree Hill - Down/Left
	.byte $00 | $18, $1F, $A1; 45 Degree Underwater Hill - Down/Left
	.byte $20 | $16, $19, $84; Coins
	.byte $60 | $00, $26, $DB; Aboveground Wall - Right Side
	.byte $80 | $0C, $23, $50, $03; Hilly Fill
	.byte $60 | $0C, $26, $E0; Hilly Wall - Right Side
	.byte $00 | $0D, $23, $83; 45 Degree Hill - Up/Right
	.byte $00 | $00, $29, $DB; Aboveground Wall - Left Side
	.byte $00 | $0C, $29, $07; Lower Left Corner - Hilly
	.byte $80 | $0C, $2A, $B0, $03; Ceiling - Hilly
	.byte $80 | $0C, $2E, $50, $02; Hilly Fill
	.byte $00 | $0D, $2E, $72; 45 Degree Hill - Up/Left
	.byte $60 | $10, $2C, $0C; Square Hill Object
	.byte $80 | $13, $25, $87, $07; Flat Land - Hilly
	.byte $00 | $13, $2C, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $14, $2C, $E6; Hilly Wall - Right Side
	.byte $80 | $19, $2F, $81, $06; Flat Land - Hilly
	.byte $20 | $00, $27, $D4; Upward Pipe (CAN'T go up)
	.byte $20 | $04, $27, $DC; Upward Pipe (CAN'T go up)
	.byte $00 | $19, $2F, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $1A, $2F, $E0; Hilly Wall - Left Side
	.byte $20 | $16, $2D, $A4; Downward Pipe (CAN'T go down)
	.byte $60 | $00, $34, $D9; Aboveground Wall - Right Side
	.byte $80 | $0B, $34, $50, $00; Hilly Fill
	.byte $80 | $0A, $34, $40, $00; Aboveground Fill
	.byte $60 | $0A, $35, $01; Underground Tunnel B
	.byte $00 | $0B, $3C, $D0; Aboveground Wall - Left Side
	.byte $80 | $0A, $3D, $71, $04; Flat Land - Aboveground
	.byte $80 | $0C, $31, $B3, $04; Ceiling - Hilly
	.byte $00 | $0E, $3B, $63; 45 Degree Hill - Down/Left
	.byte $80 | $12, $38, $B1, $03; Ceiling - Hilly
	.byte $80 | $10, $3C, $B3, $00; Ceiling - Hilly
	.byte $80 | $0C, $3D, $B7, $06; Ceiling - Hilly
	.byte $60 | $10, $30, $04; Horizontal Hill Strip
	.byte $80 | $19, $36, $51, $02; Hilly Fill
	.byte $80 | $16, $39, $84, $01; Flat Land - Hilly
	.byte $00 | $16, $38, $62; 45 Degree Hill - Down/Left
	.byte $00 | $16, $3B, $54; 45 Degree Hill - Down/Right
	.byte $00 | $17, $3C, $92; 45 Degree Underwater Hill - Down/Right
	.byte $80 | $1A, $3F, $90, $02; Flat Land - Underwater
	.byte $20 | $15, $3E, $84; Coins
	.byte $40 | $0C, $39, $07; Red Invisible Note Block
	.byte $80 | $06, $3E, $00; Small Background Cloud
	.byte $80 | $0B, $34, $40, $03; Aboveground Fill
	.byte $60 | $0B, $38, $D0; Aboveground Wall - Right Side
	.byte $80 | $06, $42, $75, $01; Flat Land - Aboveground
	.byte $00 | $06, $42, $00; Upper Left Hill Corner - Aboveground
	.byte $00 | $07, $42, $D2; Aboveground Wall - Left Side
	.byte $00 | $06, $44, $15; 45 Degree Aboveground Hill - Down/Right
	.byte $00 | $08, $4E, $23; 45 Degree Aboveground Hill - Down/Left
	.byte $80 | $0B, $49, $70, $02; Flat Land - Aboveground
	.byte $80 | $06, $4F, $75, $00; Flat Land - Aboveground
	.byte $00 | $06, $4F, $00; Upper Left Hill Corner - Aboveground
	.byte $00 | $07, $4F, $D0; Aboveground Wall - Left Side
	.byte $80 | $0C, $44, $55, $03; Hilly Fill
	.byte $60 | $12, $44, $81; 30 Degree Hill - Up/Right
	.byte $80 | $0C, $48, $B5, $0C; Ceiling - Hilly
	.byte $00 | $16, $45, $63; 45 Degree Hill - Down/Left
	.byte $00 | $17, $44, $A2; 45 Degree Underwater Hill - Down/Left
	.byte $80 | $1A, $42, $50, $03; Hilly Fill
	.byte $80 | $16, $46, $84, $0B; Flat Land - Hilly
	.byte $60 | $13, $48, $0D; Flat Land & Water Pits
	.byte $80 | $05, $44, $00; Small Background Cloud
	.byte $80 | $06, $47, $00; Small Background Cloud
	.byte $80 | $08, $4B, $00; Small Background Cloud
	.byte $80 | $05, $4E, $00; Small Background Cloud
	.byte $00 | $06, $50, $15; 45 Degree Aboveground Hill - Down/Right
	.byte $80 | $0B, $5D, $70, $04; Flat Land - Aboveground
	.byte $00 | $11, $55, $80; 45 Degree Hill - Up/Right
	.byte $00 | $0F, $5B, $66; 45 Degree Hill - Down/Left
	.byte $80 | $16, $55, $54, $06; Hilly Fill
	.byte $00 | $16, $51, $04; Upper Right Hill Corner - Hilly
	.byte $00 | $16, $55, $E0; Hilly Wall - Left Side
	.byte $60 | $17, $51, $F2; Underground Wall - Right Side
	.byte $00 | $17, $55, $F2; Underground Wall - Left Side
	.byte $80 | $1A, $52, $90, $02; Flat Land - Underwater
	.byte $80 | $0C, $5C, $5E, $13; Hilly Fill
	.byte $60 | $0B, $55, $01; Underground Tunnel B
	.byte $20 | $00, $5C, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $16, $53, $00; '?' with flower
	.byte $80 | $06, $52, $00; Small Background Cloud
	.byte $80 | $07, $5E, $00; Small Background Cloud
	.byte $80 | $05, $63, $76, $02; Flat Land - Aboveground
	.byte $00 | $05, $63, $00; Upper Left Hill Corner - Aboveground
	.byte $00 | $06, $63, $D1; Aboveground Wall - Left Side
	.byte $00 | $08, $62, $00; Upper Left Hill Corner - Aboveground
	.byte $00 | $09, $62, $D1; Aboveground Wall - Left Side
	.byte $00 | $05, $66, $16; 45 Degree Aboveground Hill - Down/Right
	.byte $80 | $0B, $6C, $70, $02; Flat Land - Aboveground
	.byte $60 | $0B, $6F, $00; Underground Tunnel A
	.byte $80 | $0B, $62, $40, $00; Aboveground Fill
	.byte $80 | $02, $65, $00; Small Background Cloud
	.byte $80 | $06, $6D, $00; Small Background Cloud
	.byte $00 | $00, $77, $DA; Aboveground Wall - Left Side
	.byte $80 | $0B, $77, $40, $00; Aboveground Fill
	.byte $80 | $00, $78, $5B, $17; Hilly Fill
	.byte $80 | $0C, $76, $B4, $02; Ceiling - Hilly
	.byte $80 | $0C, $79, $53, $01; Hilly Fill
	.byte $00 | $11, $7A, $70; 45 Degree Hill - Up/Left
	.byte $80 | $0C, $7B, $B5, $07; Ceiling - Hilly
	.byte $60 | $00, $7C, $EF; Hilly Wall - Right Side
	.byte $60 | $10, $7C, $E0; Hilly Wall - Right Side
	.byte $00 | $11, $7C, $0A; Lower Right Hill Corner
	.byte $00 | $00, $7F, $EF; Hilly Wall - Left Side
	.byte $00 | $10, $7F, $E0; Hilly Wall - Left Side
	.byte $00 | $11, $7F, $07; Lower Left Corner - Hilly
	.byte $00 | $0F, $70, $54; 45 Degree Hill - Down/Right
	.byte $80 | $14, $70, $56, $04; Hilly Fill
	.byte $60 | $14, $74, $E6; Hilly Wall - Right Side
	.byte $80 | $17, $79, $83, $08; Flat Land - Hilly
	.byte $00 | $17, $79, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $18, $79, $E2; Hilly Wall - Left Side
	.byte $20 | $00, $7D, $DD; Upward Pipe (CAN'T go up)
	.byte $20 | $0C, $7D, $D8; Upward Pipe (CAN'T go up)
	.byte $20 | $15, $75, $A5; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $77, $A4; Downward Pipe (CAN'T go down)
	.byte $80 | $03, $75, $00; Small Background Cloud
	.byte $80 | $07, $74, $00; Small Background Cloud
	.byte $80 | $10, $79, $B0, $00; Ceiling - Hilly
	.byte $80 | $10, $7A, $50, $00; Hilly Fill
	.byte $80 | $0C, $83, $53, $03; Hilly Fill
	.byte $60 | $10, $83, $81; 30 Degree Hill - Up/Right
	.byte $80 | $0C, $87, $B3, $04; Ceiling - Hilly
	.byte $80 | $0C, $8E, $5E, $01; Hilly Fill
	.byte $60 | $00, $8B, $EE; Hilly Wall - Right Side
	.byte $00 | $00, $8E, $EF; Hilly Wall - Left Side
	.byte $00 | $0F, $8B, $0A; Lower Right Hill Corner
	.byte $00 | $10, $8E, $E3; Hilly Wall - Left Side
	.byte $80 | $17, $82, $53, $05; Hilly Fill
	.byte $60 | $14, $86, $62; 30 Degree Hill - Down/Left
	.byte $80 | $14, $88, $86, $05; Flat Land - Hilly
	.byte $80 | $00, $8C, $EB; Upward Pipe to End of Level
	.byte $80 | $0B, $8C, $E6; Upward Pipe to End of Level
	; Pointer on screen $03
	.byte $E0 | $03, $70 | $07, 112; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_5_W1_objects:
	.byte $70, $0E, $0F; Buzzy Beetle
	.byte $70, $11, $12; Buzzy Beetle
	.byte $70, $13, $14; Buzzy Beetle
	.byte $70, $15, $16; Buzzy Beetle
	.byte $A3, $27, $10; Red Piranha Plant (downward)
	.byte $70, $2C, $12; Buzzy Beetle
	.byte $A0, $2D, $16; Green Piranha Plant (upward)
	.byte $6C, $48, $09; Green Koopa Troopa
	.byte $6C, $4A, $0A; Green Koopa Troopa
	.byte $6C, $54, $09; Green Koopa Troopa
	.byte $6C, $6C, $0A; Green Koopa Troopa
	.byte $A6, $75, $15; Red Venus Fire Trap (upward)
	.byte $A3, $7D, $14; Red Piranha Plant (downward)
	.byte $FF
; Level_6_W1
; Object Set 4
Level_6_W1_generators:
Level_6_W1_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_10 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $04; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $19, $00, $10, $06; Wooden platform
	.byte $00 | $1A, $01, $04; Wooden Background Pole
	.byte $00 | $18, $02, $42; Background Bushes
	.byte $00 | $1A, $04, $04; Wooden Background Pole
	.byte $00 | $12, $06, $01; Large Swirly Background Cloud
	.byte $00 | $14, $0B, $01; Large Swirly Background Cloud
	.byte $00 | $17, $08, $22; Wooden block platform
	.byte $00 | $19, $09, $04; Wooden Background Pole
	.byte $00 | $15, $0E, $22; Wooden block platform
	.byte $00 | $17, $0F, $04; Wooden Background Pole
	.byte $20 | $10, $11, $82; Coins
	.byte $00 | $12, $11, $42; Background Bushes
	.byte $00 | $13, $11, $10, $02; Wooden platform
	.byte $00 | $14, $12, $04; Wooden Background Pole
	.byte $00 | $13, $17, $01; Large Swirly Background Cloud
	.byte $00 | $19, $18, $10, $02; Wooden platform
	.byte $20 | $15, $19, $01; '?' with leaf
	.byte $00 | $1A, $19, $04; Wooden Background Pole
	.byte $00 | $13, $1B, $10, $02; Wooden platform
	.byte $00 | $12, $1C, $40; Background Bushes
	.byte $00 | $14, $1C, $04; Wooden Background Pole
	.byte $00 | $17, $22, $A1; 45 Degree Platform Wire - Down/Right
	.byte $00 | $16, $22, $B1; 45 Degree Platform Wire - Up/Right
	.byte $00 | $13, $22, $A1; 45 Degree Platform Wire - Down/Right
	.byte $00 | $12, $21, $07; Blue gear
	.byte $00 | $19, $24, $07; Blue gear
	.byte $20 | $14, $27, $61; Note Blocks - movable two directions
	.byte $00 | $09, $2A, $01; Large Swirly Background Cloud
	.byte $00 | $16, $2B, $10, $03; Wooden platform
	.byte $00 | $13, $2C, $61; Green platform
	.byte $00 | $17, $2C, $04; Wooden Background Pole
	.byte $00 | $10, $2F, $01; Large Swirly Background Cloud
	.byte $20 | $17, $32, $30; Bricks with single coins
	.byte $20 | $18, $32, $10; Bricks
	.byte $20 | $13, $33, $13; Bricks
	.byte $00 | $19, $32, $66; Green platform
	.byte $20 | $13, $35, $0B; Brick with 1-up
	.byte $00 | $18, $33, $42; Background Bushes
	.byte $20 | $17, $37, $0A; Multi-Coin Brick
	.byte $20 | $18, $37, $10; Bricks
	.byte $00 | $05, $38, $01; Large Swirly Background Cloud
	.byte $00 | $19, $3B, $10, $03; Wooden platform
	.byte $00 | $16, $3C, $61; Green platform
	.byte $00 | $1A, $3C, $04; Wooden Background Pole
	.byte $00 | $12, $40, $02; Blue Background Pole A
	.byte $00 | $13, $40, $10, $07; Wooden platform
	.byte $00 | $19, $40, $10, $02; Wooden platform
	.byte $00 | $18, $41, $40; Background Bushes
	.byte $00 | $1A, $41, $04; Wooden Background Pole
	.byte $00 | $12, $47, $03; Blue Background Pole B
	.byte $00 | $11, $47, $10, $02; Wooden platform
	.byte $00 | $12, $48, $04; Wooden Background Pole
	.byte $20 | $18, $4A, $40; Wooden blocks
	.byte $00 | $10, $4B, $02; Blue Background Pole A
	.byte $00 | $11, $4B, $10, $06; Wooden platform
	.byte $00 | $10, $4D, $42; Background Bushes
	.byte $00 | $18, $4C, $07; Blue gear
	.byte $00 | $18, $4D, $87; Horizontal platform wire
	.byte $00 | $19, $55, $A0; 45 Degree Platform Wire - Down/Right
	.byte $00 | $19, $56, $82; Horizontal platform wire
	.byte $00 | $16, $5A, $E1; 60 Degree Platform Wire - Down/Left
	.byte $00 | $16, $5B, $D0; 60 Degree Platform Wire - Down/Right
	.byte $00 | $17, $5C, $B2; 45 Degree Platform Wire - Up/Right
	.byte $00 | $11, $60, $E1; 60 Degree Platform Wire - Down/Left
	.byte $00 | $10, $61, $83; Horizontal platform wire
	.byte $00 | $11, $65, $A1; 45 Degree Platform Wire - Down/Right
	.byte $00 | $10, $51, $03; Blue Background Pole B
	.byte $20 | $0A, $55, $82; Coins
	.byte $00 | $07, $56, $01; Large Swirly Background Cloud
	.byte $00 | $14, $58, $01; Large Swirly Background Cloud
	.byte $20 | $08, $5A, $82; Coins
	.byte $20 | $11, $5E, $80; Coins
	.byte $20 | $07, $5F, $82; Coins
	.byte $20 | $13, $5A, $81; Coins
	.byte $00 | $09, $60, $01; Large Swirly Background Cloud
	.byte $00 | $16, $61, $01; Large Swirly Background Cloud
	.byte $00 | $03, $66, $01; Large Swirly Background Cloud
	.byte $00 | $14, $68, $01; Large Swirly Background Cloud
	.byte $00 | $16, $6E, $00; Small Swirly Background Cloud
	.byte $20 | $13, $6A, $42; Wooden blocks
	.byte $20 | $06, $66, $82; Coins
	.byte $20 | $06, $6A, $82; Coins
	.byte $20 | $07, $6F, $82; Coins
	.byte $00 | $08, $71, $01; Large Swirly Background Cloud
	.byte $20 | $0A, $74, $82; Coins
	.byte $00 | $0F, $74, $01; Large Swirly Background Cloud
	.byte $00 | $18, $73, $00; Small Swirly Background Cloud
	.byte $00 | $10, $7B, $00; Small Swirly Background Cloud
	.byte $00 | $15, $7C, $00; Small Swirly Background Cloud
	.byte $00 | $10, $78, $07; Blue gear
	.byte $00 | $1A, $7C, $07; Blue gear
	.byte $00 | $11, $79, $A0; 45 Degree Platform Wire - Down/Right
	.byte $00 | $12, $79, $90; 1 platform wire
	.byte $00 | $13, $7A, $A0; 45 Degree Platform Wire - Down/Right
	.byte $00 | $14, $7A, $B0; 45 Degree Platform Wire - Up/Right
	.byte $00 | $15, $7A, $A3; 45 Degree Platform Wire - Down/Right
	.byte $00 | $19, $7D, $B0; 45 Degree Platform Wire - Up/Right
	.byte $00 | $13, $83, $01; Large Swirly Background Cloud
	.byte $00 | $1A, $84, $10, $1F; Wooden platform
	.byte $00 | $16, $87, $01; Large Swirly Background Cloud
	.byte $00 | $19, $87, $42; Background Bushes
	.byte $00 | $09, $08, $00; Small Swirly Background Cloud
	.byte $00 | $0A, $12, $00; Small Swirly Background Cloud
	.byte $00 | $05, $1C, $00; Small Swirly Background Cloud
	.byte $00 | $07, $24, $00; Small Swirly Background Cloud
	.byte $00 | $0A, $32, $00; Small Swirly Background Cloud
	.byte $00 | $07, $3C, $00; Small Swirly Background Cloud
	.byte $40 | $00, $8B, $09; Level Ending
	.byte $FF
Level_6_W1_objects:
	.byte $6D, $13, $12; Red Koopa Troopa
	.byte $6D, $1A, $18; Red Koopa Troopa
	.byte $3C, $21, $13; Wired platform (follows platform wires)
	.byte $6F, $30, $11; Red Koopa Paratroopa
	.byte $6C, $36, $18; Green Koopa Troopa
	.byte $44, $4D, $18; Falling Platform (falls when stepped on)
	.byte $6F, $5C, $0D; Red Koopa Paratroopa
	.byte $37, $74, $14; Wooden platform - moves back and forth (a little)
	.byte $44, $78, $12; Falling Platform (falls when stepped on)
	.byte $6F, $82, $15; Red Koopa Paratroopa
	.byte $41, $98, $15; Goal Card
	.byte $6C, $98, $18; Green Koopa Troopa
	.byte $FF
; Level_2_W2
; Object Set 3
Level_2_W2_generators:
Level_2_W2_header:
	.byte $1E; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_09; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $13; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $19, $00, $81, $04; Flat Land - Hilly
	.byte $80 | $19, $05, $51, $03; Hilly Wall
	.byte $80 | $18, $0C, $52, $04; Hilly Wall
	.byte $80 | $15, $09, $85, $03; Flat Land - Hilly
	.byte $00 | $15, $08, $63; 45 Degree Hill - Down/Left
	.byte $00 | $15, $0C, $50; 45 Degree Hill - Down/Right
	.byte $60 | $16, $0D, $51; 30 Degree Hill - Down/Right
	.byte $80 | $18, $02, $D2; Small Background Hills
	.byte $80 | $14, $09, $D1; Small Background Hills
	.byte $A0 | $11, $03, $33; Background Clouds
	.byte $60 | $18, $10, $E2; Hilly Wall - Right Side
	.byte $40 | $19, $11, $D1, $04; Normal Quicksand
	.byte $80 | $18, $16, $52, $05; Hilly Wall
	.byte $80 | $14, $1A, $86, $02; Flat Land - Hilly
	.byte $00 | $14, $19, $63; 45 Degree Hill - Down/Left
	.byte $00 | $17, $1D, $50; 45 Degree Hill - Down/Right
	.byte $00 | $18, $16, $E2; Hilly Wall - Left Side
	.byte $60 | $18, $1D, $E2; Hilly Wall - Right Side
	.byte $80 | $15, $1F, $85, $01; Flat Land - Hilly
	.byte $00 | $15, $1F, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $16, $1F, $E4; Hilly Wall - Left Side
	.byte $20 | $13, $1F, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $12, $1C, $82; Coins
	.byte $40 | $13, $1A, $05; Wooden Block with Leaf
	.byte $00 | $14, $1C, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $15, $1C, $E1; Hilly Wall - Right Side
	.byte $A0 | $14, $10, $32; Background Clouds
	.byte $80 | $18, $20, $52, $03; Hilly Wall
	.byte $60 | $18, $23, $E2; Hilly Wall - Right Side
	.byte $00 | $15, $21, $52; 45 Degree Hill - Down/Right
	.byte $80 | $17, $29, $53, $06; Hilly Wall
	.byte $80 | $13, $2C, $87, $03; Flat Land - Hilly
	.byte $60 | $13, $2C, $60; 30 Degree Hill - Down/Left
	.byte $00 | $13, $2F, $50; 45 Degree Hill - Down/Right
	.byte $00 | $14, $2B, $62; 45 Degree Hill - Down/Left
	.byte $40 | $19, $24, $D1, $04; Normal Quicksand
	.byte $00 | $17, $29, $E3; Hilly Wall - Left Side
	.byte $A0 | $13, $23, $32; Background Clouds
	.byte $80 | $16, $32, $33, $3E; Water
	.byte $80 | $14, $30, $86, $01; Flat Land - Hilly
	.byte $00 | $14, $31, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $15, $31, $E0; Hilly Wall - Right Side
	.byte $60 | $16, $31, $F1; Dark Underground Wall - Right Side
	.byte $80 | $1A, $32, $60, $03; Dark Underground Wall
	.byte $80 | $19, $32, $60, $01; Dark Underground Wall
	.byte $60 | $18, $32, $91; 30 Degree Underwater Hill - Down/Right
	.byte $80 | $1A, $36, $90, $36; Flat Land - Underwater
	.byte $20 | $11, $38, $82; Coins
	.byte $20 | $11, $3C, $82; Coins
	.byte $20 | $12, $31, $40; Wooden blocks
	.byte $A0 | $10, $38, $32; Background Clouds
	.byte $20 | $13, $31, $40; Wooden blocks
	.byte $20 | $17, $4F, $40; Wooden blocks
	.byte $20 | $11, $4D, $0F; Invisible 1-up
	.byte $20 | $12, $46, $0D; Brick with P-Switch
	.byte $20 | $12, $45, $30; Bricks with single coins
	.byte $20 | $11, $48, $83; Coins
	.byte $20 | $11, $4E, $82; Coins
	.byte $20 | $12, $50, $10; Bricks
	.byte $20 | $13, $50, $10; Bricks
	.byte $20 | $12, $54, $10; Bricks
	.byte $20 | $13, $54, $10; Bricks
	.byte $20 | $11, $58, $10; Bricks
	.byte $20 | $12, $58, $10; Bricks
	.byte $20 | $13, $58, $10; Bricks
	.byte $20 | $12, $56, $10; Bricks
	.byte $20 | $12, $5A, $10; Bricks
	.byte $20 | $13, $56, $10; Bricks
	.byte $20 | $13, $5A, $10; Bricks
	.byte $20 | $12, $5C, $10; Bricks
	.byte $20 | $13, $5C, $10; Bricks
	.byte $20 | $15, $53, $40; Wooden blocks
	.byte $20 | $18, $58, $40; Wooden blocks
	.byte $20 | $19, $54, $40; Wooden blocks
	.byte $20 | $19, $58, $40; Wooden blocks
	.byte $A0 | $10, $5B, $32; Background Clouds
	.byte $80 | $1A, $6D, $60, $04; Dark Underground Wall
	.byte $80 | $19, $6E, $60, $02; Dark Underground Wall
	.byte $80 | $18, $6F, $60, $01; Dark Underground Wall
	.byte $80 | $17, $70, $60, $00; Dark Underground Wall
	.byte $20 | $17, $60, $40; Wooden blocks
	.byte $A0 | $10, $66, $33; Background Clouds
	.byte $20 | $10, $6D, $10; Bricks
	.byte $20 | $11, $6D, $10; Bricks
	.byte $20 | $12, $6D, $10; Bricks
	.byte $20 | $13, $6D, $10; Bricks
	.byte $80 | $15, $72, $85, $01; Flat Land - Hilly
	.byte $00 | $15, $71, $64; 45 Degree Hill - Down/Left
	.byte $00 | $15, $73, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $16, $73, $E0; Hilly Wall - Right Side
	.byte $00 | $16, $70, $A3; 45 Degree Underwater Hill - Down/Left
	.byte $80 | $19, $74, $51, $0B; Hilly Wall
	.byte $80 | $19, $76, $81, $08; Flat Land - Hilly
	.byte $00 | $17, $74, $51; 45 Degree Hill - Down/Right
	.byte $00 | $0F, $7F, $E9; Hilly Wall - Left Side
	.byte $80 | $18, $77, $D2; Small Background Hills
	.byte $80 | $18, $7A, $D1; Small Background Hills
	.byte $A0 | $12, $74, $32; Background Clouds
	.byte $20 | $17, $7D, $E1; Rightward Pipe (CAN go in)
	.byte $80 | $17, $7F, $51, $00; Hilly Wall
	; Pointer on screen $07
	.byte $E0 | $07, $70 | $01, 48; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_2_W2_objects:
	.byte $D4, $00, $1E; White Mushroom House (X pos must be uneven, Y pos=amount of coins required)
	.byte $72, $0F, $15; Goomba
	.byte $A4, $13, $19; Green Venus Fire Trap (upward)
	.byte $A6, $26, $19; Red Venus Fire Trap (upward)
	.byte $77, $38, $17; Cheep-Cheep
	.byte $26, $33, $14; Still wooden platform (moves right when stepped on)
	.byte $80, $39, $13; Green Koopa Paratroopa (doesn't bounce)
	.byte $77, $48, $18; Cheep-Cheep
	.byte $77, $55, $17; Cheep-Cheep
	.byte $77, $5F, $18; Cheep-Cheep
	.byte $77, $67, $17; Cheep-Cheep
	.byte $80, $60, $13; Green Koopa Paratroopa (doesn't bounce)
	.byte $80, $69, $12; Green Koopa Paratroopa (doesn't bounce)
	.byte $FF
; Level_3_W2
; Object Set 9
Level_3_W2_generators:
Level_3_W2_header:
	.byte $1F; Next Level
	.byte LEVEL1_SIZE_09 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_09; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $09; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $18, $04, $0C; Background Pyramid
	.byte $20 | $11, $0E, $10; Bricks
	.byte $20 | $10, $0E, $20; '?' blocks with single coins
	.byte $00 | $12, $0E, $20; Medium block platforms
	.byte $00 | $14, $0C, $21; Medium block platforms
	.byte $00 | $16, $0A, $20; Medium block platforms
	.byte $00 | $18, $08, $23; Medium block platforms
	.byte $00 | $16, $12, $20; Medium block platforms
	.byte $00 | $18, $1F, $21; Medium block platforms
	.byte $20 | $11, $11, $10; Bricks
	.byte $20 | $10, $11, $01; '?' with leaf
	.byte $60 | $1A, $1A, $92; Horizontal Plain Background A (used to block out stuff)
	.byte $20 | $17, $1A, $42; Wooden blocks
	.byte $00 | $10, $27, $20; Medium block platforms
	.byte $00 | $12, $25, $21; Medium block platforms
	.byte $00 | $14, $23, $20; Medium block platforms
	.byte $00 | $16, $21, $23; Medium block platforms
	.byte $00 | $14, $2B, $20; Medium block platforms
	.byte $00 | $18, $2B, $21; Medium block platforms
	.byte $20 | $0E, $27, $20; '?' blocks with single coins
	.byte $20 | $0E, $2A, $02; '?' with star
	.byte $20 | $0F, $27, $10; Bricks
	.byte $20 | $0F, $2A, $10; Bricks
	.byte $00 | $14, $3E, $23; Medium block platforms
	.byte $00 | $16, $3C, $24; Medium block platforms
	.byte $00 | $18, $3A, $25; Medium block platforms
	.byte $20 | $17, $35, $42; Wooden blocks
	.byte $60 | $1A, $35, $92; Horizontal Plain Background A (used to block out stuff)
	.byte $00 | $0E, $44, $20; Medium block platforms
	.byte $00 | $10, $42, $21; Medium block platforms
	.byte $00 | $12, $40, $22; Medium block platforms
	.byte $20 | $0B, $45, $01; '?' with leaf
	.byte $20 | $0B, $46, $20; '?' blocks with single coins
	.byte $20 | $0C, $45, $11; Bricks
	.byte $20 | $17, $54, $42; Wooden blocks
	.byte $60 | $1A, $54, $92; Horizontal Plain Background A (used to block out stuff)
	.byte $20 | $17, $5F, $18; Bricks
	.byte $20 | $18, $5E, $1A; Bricks
	.byte $20 | $19, $5D, $1C; Bricks
	.byte $20 | $14, $62, $12; Bricks
	.byte $20 | $15, $61, $14; Bricks
	.byte $20 | $16, $60, $16; Bricks
	.byte $20 | $14, $66, $40; Wooden blocks
	.byte $20 | $14, $69, $40; Wooden blocks
	.byte $20 | $14, $6C, $40; Wooden blocks
	.byte $20 | $16, $64, $0B; Brick with 1-up
	.byte $20 | $02, $65, $0D; Brick with P-Switch
	.byte $20 | $02, $66, $10; Bricks
	.byte $20 | $05, $64, $12; Bricks
	.byte $20 | $05, $6C, $0E; Invisible Coin
	.byte $20 | $08, $6D, $0E; Invisible Coin
	.byte $20 | $0B, $6E, $0E; Invisible Coin
	.byte $40 | $0F, $6F, $00; Invisible Note Block
	.byte $20 | $15, $6F, $14; Bricks
	.byte $20 | $16, $6E, $16; Bricks
	.byte $20 | $17, $6D, $18; Bricks
	.byte $20 | $18, $6C, $1A; Bricks
	.byte $20 | $19, $6B, $1C; Bricks
	.byte $20 | $12, $7A, $10; Bricks
	.byte $20 | $13, $7A, $10; Bricks
	.byte $20 | $15, $7D, $10; Bricks
	.byte $20 | $16, $7D, $10; Bricks
	.byte $40 | $0B, $70, $00; Invisible Note Block
	.byte $20 | $08, $71, $16; Bricks
	.byte $20 | $04, $71, $80; Coins
	.byte $20 | $04, $73, $80; Coins
	.byte $20 | $04, $75, $80; Coins
	.byte $20 | $04, $77, $80; Coins
	.byte $20 | $05, $72, $80; Coins
	.byte $20 | $05, $74, $80; Coins
	.byte $20 | $05, $76, $80; Coins
	.byte $20 | $06, $71, $80; Coins
	.byte $20 | $06, $73, $80; Coins
	.byte $20 | $06, $75, $80; Coins
	.byte $20 | $06, $77, $80; Coins
	.byte $20 | $13, $71, $10; Bricks
	.byte $20 | $14, $70, $12; Bricks
	.byte $20 | $18, $80, $10; Bricks
	.byte $20 | $19, $80, $10; Bricks
	.byte $20 | $17, $85, $10; Bricks
	.byte $20 | $17, $87, $18; Bricks
	.byte $20 | $18, $83, $16; Bricks
	.byte $20 | $18, $8D, $12; Bricks
	.byte $20 | $19, $82, $1D; Bricks
	.byte $20 | $16, $86, $10; Bricks
	.byte $20 | $16, $88, $15; Bricks
	.byte $20 | $16, $8E, $10; Bricks
	.byte $20 | $15, $87, $16; Bricks
	.byte $20 | $14, $88, $10; Bricks
	.byte $20 | $14, $8A, $14; Bricks
	.byte $20 | $13, $89, $11; Bricks
	.byte $20 | $13, $8E, $30; Bricks with single coins
	.byte $20 | $14, $87, $30; Bricks with single coins
	.byte $20 | $17, $84, $30; Bricks with single coins
	.byte $20 | $16, $85, $30; Bricks with single coins
	.byte $20 | $0C, $8F, $30; Bricks with single coins
	.byte $20 | $0D, $8E, $31; Bricks with single coins
	.byte $20 | $0E, $8E, $31; Bricks with single coins
	.byte $20 | $0F, $8E, $31; Bricks with single coins
	.byte $20 | $10, $8E, $31; Bricks with single coins
	.byte $20 | $11, $8E, $31; Bricks with single coins
	.byte $20 | $12, $8E, $31; Bricks with single coins
	.byte $20 | $13, $8F, $30; Bricks with single coins
	.byte $20 | $14, $8F, $30; Bricks with single coins
	.byte $20 | $15, $8F, $30; Bricks with single coins
	.byte $20 | $16, $8F, $30; Bricks with single coins
	.byte $20 | $11, $8A, $32; Bricks with single coins
	.byte $20 | $12, $89, $30; Bricks with single coins
	.byte $20 | $13, $88, $30; Bricks with single coins
	.byte $20 | $15, $86, $30; Bricks with single coins
	.byte $20 | $16, $8B, $93; Downward Pipe (CAN go down)
	.byte $20 | $18, $83, $30; Bricks with single coins
	.byte $20 | $19, $82, $30; Bricks with single coins
	.byte $20 | $16, $8A, $0A; Multi-Coin Brick
	.byte $00 | $07, $06, $0A; Oval Background Cloud
	.byte $00 | $12, $08, $0A; Oval Background Cloud
	.byte $00 | $14, $02, $0A; Oval Background Cloud
	.byte $00 | $0A, $14, $0A; Oval Background Cloud
	.byte $00 | $14, $18, $0A; Oval Background Cloud
	.byte $00 | $07, $1E, $0A; Oval Background Cloud
	.byte $00 | $11, $1E, $0A; Oval Background Cloud
	.byte $00 | $05, $3D, $0A; Oval Background Cloud
	.byte $00 | $09, $32, $0A; Oval Background Cloud
	.byte $00 | $10, $30, $0A; Oval Background Cloud
	.byte $00 | $12, $3C, $0A; Oval Background Cloud
	.byte $00 | $05, $4A, $0A; Oval Background Cloud
	.byte $00 | $0B, $50, $0A; Oval Background Cloud
	.byte $00 | $11, $52, $0A; Oval Background Cloud
	.byte $00 | $06, $58, $0A; Oval Background Cloud
	.byte $00 | $05, $68, $0A; Oval Background Cloud
	.byte $00 | $10, $6A, $0A; Oval Background Cloud
	.byte $00 | $03, $7E, $0A; Oval Background Cloud
	.byte $00 | $0B, $74, $0A; Oval Background Cloud
	.byte $00 | $0F, $7A, $0A; Oval Background Cloud
	.byte $00 | $05, $88, $0A; Oval Background Cloud
	.byte $00 | $09, $82, $0A; Oval Background Cloud
	; Pointer on screen $08
	.byte $E0 | $08, $60 | $01, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_3_W2_objects:
	.byte $59, $0F, $13; Fire Snake
	.byte $6D, $12, $17; Red Koopa Troopa
	.byte $59, $29, $13; Fire Snake
	.byte $59, $29, $19; Fire Snake
	.byte $59, $47, $12; Fire Snake
	.byte $6C, $42, $17; Green Koopa Troopa
	.byte $6C, $48, $17; Green Koopa Troopa
	.byte $6B, $63, $13; Pile Driver Micro-Goomba
	.byte $6C, $62, $13; Green Koopa Troopa
	.byte $6C, $6F, $14; Green Koopa Troopa
	.byte $6B, $6C, $13; Pile Driver Micro-Goomba
	.byte $6B, $6C, $18; Pile Driver Micro-Goomba
	.byte $6B, $7D, $14; Pile Driver Micro-Goomba
	.byte $6B, $80, $17; Pile Driver Micro-Goomba
	.byte $6C, $8B, $13; Green Koopa Troopa
	.byte $6C, $8D, $13; Green Koopa Troopa
	.byte $FF
; Level_1_W2
; Object Set 9
Level_1_W2_generators:
Level_1_W2_header:
	.byte $20; Next Level
	.byte LEVEL1_SIZE_12 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_09; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $09; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $60 | $06, $50, $A1; Pipe Boxes A
	.byte $60 | $06, $70, $A1; Pipe Boxes A
	.byte $00 | $18, $03, $0C; Background Pyramid
	.byte $00 | $17, $08, $0C; Background Pyramid
	.byte $20 | $18, $0E, $10; Bricks
	.byte $20 | $19, $0E, $12; Bricks
	.byte $00 | $03, $02, $0A; Oval Background Cloud
	.byte $00 | $05, $0C, $0A; Oval Background Cloud
	.byte $00 | $0B, $06, $0A; Oval Background Cloud
	.byte $00 | $10, $04, $0A; Oval Background Cloud
	.byte $00 | $11, $0A, $0A; Oval Background Cloud
	.byte $20 | $17, $14, $10; Bricks
	.byte $20 | $19, $14, $10; Bricks
	.byte $20 | $18, $10, $14; Bricks
	.byte $20 | $19, $10, $10; Bricks
	.byte $20 | $19, $12, $10; Bricks
	.byte $20 | $16, $19, $10; Bricks
	.byte $20 | $17, $17, $10; Bricks
	.byte $20 | $17, $19, $10; Bricks
	.byte $20 | $17, $1C, $11; Bricks
	.byte $20 | $17, $1F, $10; Bricks
	.byte $20 | $18, $17, $18; Bricks
	.byte $20 | $19, $17, $18; Bricks
	.byte $20 | $17, $15, $01; '?' with leaf
	.byte $00 | $05, $1A, $0A; Oval Background Cloud
	.byte $00 | $07, $10, $0A; Oval Background Cloud
	.byte $00 | $09, $1C, $0A; Oval Background Cloud
	.byte $00 | $10, $14, $0A; Oval Background Cloud
	.byte $20 | $19, $24, $10; Bricks
	.byte $20 | $18, $29, $10; Bricks
	.byte $20 | $19, $29, $10; Bricks
	.byte $20 | $17, $2E, $10; Bricks
	.byte $20 | $18, $2E, $10; Bricks
	.byte $20 | $19, $2E, $10; Bricks
	.byte $00 | $09, $2C, $0A; Oval Background Cloud
	.byte $00 | $0D, $24, $0A; Oval Background Cloud
	.byte $00 | $12, $2E, $0A; Oval Background Cloud
	.byte $00 | $13, $26, $0A; Oval Background Cloud
	.byte $20 | $15, $30, $04; '?' with single coin
	.byte $20 | $15, $31, $02; '?' with star
	.byte $20 | $19, $38, $10; Bricks
	.byte $00 | $05, $38, $0A; Oval Background Cloud
	.byte $00 | $09, $3E, $0A; Oval Background Cloud
	.byte $00 | $0A, $32, $0A; Oval Background Cloud
	.byte $00 | $11, $36, $0A; Oval Background Cloud
	.byte $20 | $15, $4D, $60; Note Blocks - movable two directions
	.byte $20 | $19, $48, $07; Brick with Leaf
	.byte $00 | $05, $46, $0A; Oval Background Cloud
	.byte $00 | $0B, $46, $0A; Oval Background Cloud
	.byte $00 | $12, $40, $0A; Oval Background Cloud
	.byte $00 | $12, $4A, $0A; Oval Background Cloud
	.byte $20 | $17, $4B, $60; Note Blocks - movable two directions
	.byte $60 | $06, $50, $CF; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0A, $50, $CF; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0E, $50, $CF; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $06, $50, $BB; 1 Plain Background (used to block out stuff)
	.byte $60 | $06, $58, $BB; 1 Plain Background (used to block out stuff)
	.byte $60 | $13, $58, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $16, $59, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $00 | $17, $58, $09; Bottom post of pipe structure
	.byte $20 | $06, $50, $15; Bricks
	.byte $20 | $07, $50, $10; Bricks
	.byte $20 | $08, $50, $10; Bricks
	.byte $20 | $09, $50, $10; Bricks
	.byte $20 | $0A, $50, $10; Bricks
	.byte $20 | $0B, $50, $15; Bricks
	.byte $20 | $07, $55, $10; Bricks
	.byte $20 | $08, $55, $10; Bricks
	.byte $20 | $09, $55, $10; Bricks
	.byte $20 | $0A, $55, $10; Bricks
	.byte $20 | $0B, $51, $43; Wooden blocks
	.byte $20 | $09, $52, $91; Downward Pipe (CAN go down)
	.byte $20 | $16, $5A, $84; Coins
	.byte $20 | $12, $54, $10; Bricks
	.byte $00 | $04, $5C, $0A; Oval Background Cloud
	.byte $20 | $16, $5C, $0B; Brick with 1-up
	.byte $60 | $06, $60, $CF; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0A, $60, $CF; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0E, $60, $CF; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $06, $60, $BB; 1 Plain Background (used to block out stuff)
	.byte $60 | $06, $68, $BB; 1 Plain Background (used to block out stuff)
	.byte $60 | $13, $60, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $12, $69, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $16, $69, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $00 | $17, $60, $09; Bottom post of pipe structure
	.byte $40 | $14, $6A, $05; Wooden Block with Leaf
	.byte $20 | $14, $6E, $40; Wooden blocks
	.byte $40 | $16, $6C, $00; Invisible Note Block
	.byte $20 | $16, $64, $10; Bricks
	.byte $20 | $12, $66, $10; Bricks
	.byte $00 | $05, $64, $0A; Oval Background Cloud
	.byte $00 | $09, $6E, $0A; Oval Background Cloud
	.byte $00 | $0C, $68, $0A; Oval Background Cloud
	.byte $00 | $10, $6C, $0A; Oval Background Cloud
	.byte $60 | $06, $70, $CF; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0A, $70, $CF; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0E, $70, $CF; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $06, $70, $BB; 1 Plain Background (used to block out stuff)
	.byte $60 | $06, $78, $BB; 1 Plain Background (used to block out stuff)
	.byte $60 | $13, $78, $B2; 1 Plain Background (used to block out stuff)
	.byte $00 | $17, $78, $09; Bottom post of pipe structure
	.byte $20 | $02, $78, $43; Wooden blocks
	.byte $20 | $03, $79, $D2; Upward Pipe (CAN'T go up)
	.byte $20 | $14, $7A, $84; Coins
	.byte $20 | $12, $74, $10; Bricks
	.byte $00 | $07, $74, $0A; Oval Background Cloud
	.byte $20 | $13, $75, $84; Coins
	.byte $20 | $15, $75, $84; Coins
	.byte $20 | $13, $7F, $84; Coins
	.byte $20 | $15, $7F, $84; Coins
	.byte $60 | $06, $80, $CF; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0A, $80, $CF; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $0E, $80, $CF; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $06, $80, $BB; 1 Plain Background (used to block out stuff)
	.byte $60 | $06, $88, $BB; 1 Plain Background (used to block out stuff)
	.byte $60 | $13, $80, $B2; 1 Plain Background (used to block out stuff)
	.byte $60 | $12, $89, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $60 | $16, $89, $C6; Horizontal Plain Background B (used to block out stuff)
	.byte $00 | $17, $80, $09; Bottom post of pipe structure
	.byte $20 | $16, $84, $10; Bricks
	.byte $20 | $12, $86, $10; Bricks
	.byte $60 | $19, $88, $20; Background Coconuts
	.byte $60 | $19, $8A, $20; Background Coconuts
	.byte $00 | $03, $82, $0A; Oval Background Cloud
	.byte $00 | $07, $8E, $0A; Oval Background Cloud
	.byte $00 | $09, $88, $0A; Oval Background Cloud
	.byte $00 | $10, $86, $0A; Oval Background Cloud
	.byte $00 | $13, $8E, $0A; Oval Background Cloud
	.byte $60 | $06, $90, $BF; 1 Plain Background (used to block out stuff)
	.byte $60 | $16, $90, $B0; 1 Plain Background (used to block out stuff)
	.byte $60 | $19, $95, $20; Background Coconuts
	.byte $60 | $19, $97, $20; Background Coconuts
	.byte $20 | $17, $9E, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $03, $94, $0A; Oval Background Cloud
	.byte $00 | $09, $9A, $0A; Oval Background Cloud
	.byte $00 | $0B, $92, $0A; Oval Background Cloud
	.byte $00 | $11, $9A, $0A; Oval Background Cloud
	.byte $00 | $07, $A4, $0A; Oval Background Cloud
	.byte $00 | $14, $A2, $0A; Oval Background Cloud
	.byte $00 | $16, $8B, $04; Palm Tree
	.byte $00 | $16, $90, $04; Palm Tree
	.byte $20 | $17, $A2, $10; Bricks
	.byte $20 | $18, $A0, $10; Bricks
	.byte $20 | $18, $A2, $11; Bricks
	.byte $20 | $19, $A0, $13; Bricks
	.byte $20 | $18, $A4, $91; Downward Pipe (CAN go down)
	.byte $00 | $09, $5F, $0A; Oval Background Cloud
	.byte $40 | $00, $A8, $09; Level Ending
	; Pointer on screen $05
	.byte $E0 | $05, $40 | $02, 32; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $0A
	.byte $E0 | $0A, $40 | $02, 194; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_1_W2_objects:
	.byte $6B, $12, $17; Pile Driver Micro-Goomba
	.byte $6B, $19, $15; Pile Driver Micro-Goomba
	.byte $6B, $1F, $16; Pile Driver Micro-Goomba
	.byte $6B, $24, $18; Pile Driver Micro-Goomba
	.byte $6B, $29, $17; Pile Driver Micro-Goomba
	.byte $6B, $2E, $16; Pile Driver Micro-Goomba
	.byte $6D, $34, $19; Red Koopa Troopa
	.byte $6B, $40, $18; Pile Driver Micro-Goomba
	.byte $59, $47, $19; Fire Snake
	.byte $72, $56, $11; Goomba
	.byte $59, $5D, $19; Fire Snake
	.byte $72, $64, $11; Goomba
	.byte $59, $83, $14; Fire Snake
	.byte $A0, $9E, $17; Green Piranha Plant (upward)
	.byte $6B, $A1, $18; Pile Driver Micro-Goomba
	.byte $A0, $A4, $18; Green Piranha Plant (upward)
	.byte $6B, $B8, $19; Pile Driver Micro-Goomba
	.byte $41, $B8, $15; Goal Card
	.byte $FF
; Dungeon_W2
; Object Set 9
Dungeon_W2_generators:
Dungeon_W2_header:
	.byte $21; Next Level
	.byte LEVEL1_SIZE_12 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_11 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_09; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $09; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $00 | $0F, $00, $7F; Medium sandstone blocks
	.byte $00 | $16, $00, $61; Small sandstone blocks
	.byte $00 | $17, $00, $62; Small sandstone blocks
	.byte $00 | $18, $00, $63; Small sandstone blocks
	.byte $00 | $19, $00, $64; Small sandstone blocks
	.byte $00 | $1A, $00, $6F; Small sandstone blocks
	.byte $00 | $11, $1D, $60; Small sandstone blocks
	.byte $00 | $12, $1D, $60; Small sandstone blocks
	.byte $00 | $19, $1E, $61; Small sandstone blocks
	.byte $00 | $11, $21, $60; Small sandstone blocks
	.byte $00 | $12, $21, $60; Small sandstone blocks
	.byte $00 | $17, $2D, $62; Small sandstone blocks
	.byte $00 | $18, $2C, $63; Small sandstone blocks
	.byte $00 | $19, $2B, $64; Small sandstone blocks
	.byte $00 | $1A, $20, $6F; Small sandstone blocks
	.byte $00 | $11, $3B, $60; Small sandstone blocks
	.byte $00 | $12, $3B, $60; Small sandstone blocks
	.byte $00 | $11, $3F, $60; Small sandstone blocks
	.byte $00 | $12, $3F, $60; Small sandstone blocks
	.byte $00 | $18, $3D, $60; Small sandstone blocks
	.byte $00 | $19, $3D, $60; Small sandstone blocks
	.byte $00 | $01, $3E, $73; Medium sandstone blocks
	.byte $00 | $05, $3E, $73; Medium sandstone blocks
	.byte $00 | $09, $3E, $73; Medium sandstone blocks
	.byte $00 | $0D, $3E, $73; Medium sandstone blocks
	.byte $00 | $1A, $40, $6F; Small sandstone blocks
	.byte $00 | $00, $40, $6F; Small sandstone blocks
	.byte $00 | $03, $40, $72; Medium sandstone blocks
	.byte $00 | $03, $4C, $60; Small sandstone blocks
	.byte $00 | $04, $4C, $60; Small sandstone blocks
	.byte $00 | $07, $40, $72; Medium sandstone blocks
	.byte $00 | $07, $4C, $60; Small sandstone blocks
	.byte $00 | $08, $4C, $60; Small sandstone blocks
	.byte $00 | $0B, $40, $72; Medium sandstone blocks
	.byte $00 | $0B, $4C, $60; Small sandstone blocks
	.byte $00 | $0C, $4C, $60; Small sandstone blocks
	.byte $00 | $0F, $40, $72; Medium sandstone blocks
	.byte $00 | $0F, $4C, $60; Small sandstone blocks
	.byte $00 | $10, $4C, $60; Small sandstone blocks
	.byte $00 | $17, $4C, $61; Small sandstone blocks
	.byte $00 | $18, $4A, $62; Small sandstone blocks
	.byte $00 | $19, $48, $63; Small sandstone blocks
	.byte $40 | $09, $4E, $FA; Double-Ended Vertical Pipe
	.byte $00 | $0B, $50, $98; X-Large sandstone blocks
	.byte $00 | $0F, $50, $90; X-Large sandstone blocks
	.byte $00 | $13, $50, $90; X-Large sandstone blocks
	.byte $00 | $17, $50, $90; X-Large sandstone blocks
	.byte $00 | $01, $5E, $60; Small sandstone blocks
	.byte $00 | $02, $5E, $60; Small sandstone blocks
	.byte $00 | $07, $59, $60; Small sandstone blocks
	.byte $00 | $09, $58, $60; Small sandstone blocks
	.byte $00 | $0A, $57, $60; Small sandstone blocks
	.byte $20 | $08, $5E, $44; Wooden blocks
	.byte $60 | $0A, $59, $3F; Floor Spikes
	.byte $00 | $00, $60, $6F; Small sandstone blocks
	.byte $00 | $01, $62, $60; Small sandstone blocks
	.byte $00 | $02, $62, $60; Small sandstone blocks
	.byte $00 | $09, $68, $6F; Small sandstone blocks
	.byte $00 | $0A, $69, $6F; Small sandstone blocks
	.byte $20 | $07, $67, $40; Wooden blocks
	.byte $20 | $07, $68, $07; Brick with Leaf
	.byte $00 | $01, $74, $60; Small sandstone blocks
	.byte $00 | $02, $74, $60; Small sandstone blocks
	.byte $00 | $01, $78, $61; Small sandstone blocks
	.byte $00 | $02, $78, $60; Small sandstone blocks
	.byte $00 | $03, $78, $60; Small sandstone blocks
	.byte $00 | $01, $7C, $73; Medium sandstone blocks
	.byte $00 | $03, $7C, $60; Small sandstone blocks
	.byte $00 | $04, $7C, $60; Small sandstone blocks
	.byte $00 | $00, $80, $66; Small sandstone blocks
	.byte $00 | $01, $8C, $60; Small sandstone blocks
	.byte $00 | $02, $8C, $60; Small sandstone blocks
	.byte $00 | $03, $80, $70; Medium sandstone blocks
	.byte $00 | $03, $84, $60; Small sandstone blocks
	.byte $00 | $04, $84, $60; Small sandstone blocks
	.byte $00 | $03, $88, $60; Small sandstone blocks
	.byte $00 | $04, $88, $60; Small sandstone blocks
	.byte $00 | $03, $8A, $70; Medium sandstone blocks
	.byte $00 | $05, $80, $62; Small sandstone blocks
	.byte $00 | $06, $80, $61; Small sandstone blocks
	.byte $00 | $09, $88, $62; Small sandstone blocks
	.byte $00 | $0A, $89, $66; Small sandstone blocks
	.byte $00 | $00, $8E, $71; Medium sandstone blocks
	.byte $00 | $02, $8E, $71; Medium sandstone blocks
	.byte $00 | $04, $8E, $71; Medium sandstone blocks
	.byte $00 | $06, $8E, $71; Medium sandstone blocks
	.byte $00 | $08, $8E, $71; Medium sandstone blocks
	.byte $00 | $07, $8D, $0B; Door
	.byte $00 | $0F, $93, $90; X-Large sandstone blocks
	.byte $00 | $13, $93, $90; X-Large sandstone blocks
	.byte $00 | $17, $93, $90; X-Large sandstone blocks
	.byte $00 | $0F, $9B, $69; Small sandstone blocks
	.byte $00 | $1A, $9B, $69; Small sandstone blocks
	.byte $00 | $10, $9B, $62; Small sandstone blocks
	.byte $00 | $11, $9B, $62; Small sandstone blocks
	.byte $00 | $12, $9B, $62; Small sandstone blocks
	.byte $00 | $13, $9B, $62; Small sandstone blocks
	.byte $00 | $14, $9B, $62; Small sandstone blocks
	.byte $00 | $15, $9B, $62; Small sandstone blocks
	.byte $00 | $16, $9B, $62; Small sandstone blocks
	.byte $00 | $0F, $AF, $90; X-Large sandstone blocks
	.byte $00 | $13, $AF, $90; X-Large sandstone blocks
	.byte $00 | $17, $AF, $90; X-Large sandstone blocks
	; Pointer on screen $08
	.byte $E0 | $08, $60 | $08, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon_W2_objects:
	.byte $3F, $11, $19; Dry Bones
	.byte $3F, $1A, $19; Dry Bones
	.byte $3F, $1C, $19; Dry Bones
	.byte $8A, $1F, $11; Thwomp (normal)
	.byte $3F, $28, $19; Dry Bones
	.byte $3F, $2E, $16; Dry Bones
	.byte $8A, $3D, $11; Thwomp (normal)
	.byte $2F, $42, $12; Boo Buddy
	.byte $3F, $4C, $16; Dry Bones
	.byte $8A, $60, $01; Thwomp (normal)
	.byte $2F, $6D, $01; Boo Buddy
	.byte $8A, $76, $01; Thwomp (normal)
	.byte $8A, $7A, $02; Thwomp (normal)
	.byte $8A, $7E, $03; Thwomp (normal)
	.byte $8A, $86, $03; Thwomp (normal)
	.byte $4B, $AD, $18; Boom Boom
	.byte $FF
; Pipe_1_End_2_W2
; Object Set 14
Pipe_1_End_2_W2_generators:
Pipe_1_End_2_W2_header:
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
Pipe_1_End_2_W2_objects:
	.byte $25, $02, $01; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Pipe_1_End_1_W2
; Object Set 14
Pipe_1_End_1_W2_generators:
Pipe_1_End_1_W2_header:
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
Pipe_1_End_1_W2_objects:
	.byte $25, $02, $01; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_4_W2
; Object Set 9
Level_4_W2_generators:
Level_4_W2_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_10 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $00 | LEVEL3_TILESET_09; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $09; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $40 | $07, $0B, $84, $14; Water (still)
	.byte $00 | $04, $04, $90; X-Large sandstone blocks
	.byte $00 | $08, $03, $90; X-Large sandstone blocks
	.byte $00 | $0C, $02, $9D; X-Large sandstone blocks
	.byte $00 | $16, $05, $04; Palm Tree
	.byte $00 | $16, $0C, $04; Palm Tree
	.byte $60 | $19, $05, $20; Background Coconuts
	.byte $60 | $19, $08, $20; Background Coconuts
	.byte $60 | $19, $0A, $20; Background Coconuts
	.byte $20 | $04, $0D, $80; Coins
	.byte $20 | $04, $0F, $80; Coins
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
	.byte $20 | $0E, $00, $40; Wooden blocks
	.byte $20 | $0F, $00, $40; Wooden blocks
	.byte $20 | $10, $00, $40; Wooden blocks
	.byte $20 | $11, $00, $40; Wooden blocks
	.byte $20 | $12, $00, $40; Wooden blocks
	.byte $20 | $13, $00, $40; Wooden blocks
	.byte $20 | $14, $00, $40; Wooden blocks
	.byte $20 | $15, $00, $40; Wooden blocks
	.byte $20 | $16, $00, $40; Wooden blocks
	.byte $20 | $17, $00, $40; Wooden blocks
	.byte $20 | $18, $00, $40; Wooden blocks
	.byte $20 | $19, $00, $40; Wooden blocks
	.byte $20 | $04, $01, $10; Bricks
	.byte $20 | $05, $01, $10; Bricks
	.byte $20 | $06, $01, $10; Bricks
	.byte $20 | $07, $01, $10; Bricks
	.byte $20 | $08, $01, $10; Bricks
	.byte $20 | $09, $01, $10; Bricks
	.byte $20 | $0A, $01, $10; Bricks
	.byte $20 | $0B, $01, $10; Bricks
	.byte $20 | $0C, $01, $10; Bricks
	.byte $20 | $0D, $01, $10; Bricks
	.byte $20 | $0E, $01, $10; Bricks
	.byte $20 | $0F, $01, $10; Bricks
	.byte $20 | $06, $0C, $16; Bricks
	.byte $00 | $01, $04, $0A; Oval Background Cloud
	.byte $00 | $02, $0A, $0A; Oval Background Cloud
	.byte $00 | $11, $04, $0A; Oval Background Cloud
	.byte $00 | $12, $0E, $0A; Oval Background Cloud
	.byte $00 | $14, $08, $0A; Oval Background Cloud
	.byte $00 | $15, $02, $0A; Oval Background Cloud
	.byte $00 | $16, $1B, $04; Palm Tree
	.byte $60 | $19, $1E, $20; Background Coconuts
	.byte $20 | $06, $15, $1A; Bricks
	.byte $20 | $06, $17, $0D; Brick with P-Switch
	.byte $20 | $04, $11, $80; Coins
	.byte $20 | $04, $13, $80; Coins
	.byte $20 | $04, $15, $80; Coins
	.byte $20 | $04, $17, $80; Coins
	.byte $20 | $04, $19, $80; Coins
	.byte $20 | $04, $1B, $80; Coins
	.byte $20 | $04, $1D, $80; Coins
	.byte $60 | $1A, $16, $93; Horizontal Plain Background A (used to block out stuff)
	.byte $20 | $19, $17, $01; '?' with leaf
	.byte $20 | $17, $14, $40; Wooden blocks
	.byte $20 | $18, $14, $40; Wooden blocks
	.byte $20 | $19, $14, $40; Wooden blocks
	.byte $20 | $17, $1A, $40; Wooden blocks
	.byte $20 | $18, $1A, $40; Wooden blocks
	.byte $20 | $19, $1A, $40; Wooden blocks
	.byte $00 | $01, $18, $0A; Oval Background Cloud
	.byte $00 | $02, $12, $0A; Oval Background Cloud
	.byte $00 | $11, $1E, $0A; Oval Background Cloud
	.byte $00 | $14, $1A, $0A; Oval Background Cloud
	.byte $20 | $16, $11, $20; '?' blocks with single coins
	.byte $20 | $09, $24, $8F; Coins
	.byte $60 | $0B, $21, $2F; Background Coconuts
	.byte $00 | $08, $22, $04; Palm Tree
	.byte $00 | $08, $25, $04; Palm Tree
	.byte $00 | $08, $28, $04; Palm Tree
	.byte $00 | $08, $2B, $04; Palm Tree
	.byte $00 | $08, $2E, $04; Palm Tree
	.byte $00 | $18, $20, $70; Medium sandstone blocks
	.byte $20 | $13, $2A, $80; Coins
	.byte $20 | $14, $28, $80; Coins
	.byte $20 | $14, $2C, $80; Coins
	.byte $20 | $16, $26, $80; Coins
	.byte $20 | $16, $2E, $80; Coins
	.byte $20 | $19, $2D, $01; '?' with leaf
	.byte $60 | $1A, $26, $91; Horizontal Plain Background A (used to block out stuff)
	.byte $20 | $06, $20, $40; Wooden blocks
	.byte $20 | $07, $20, $40; Wooden blocks
	.byte $20 | $08, $20, $40; Wooden blocks
	.byte $20 | $09, $20, $40; Wooden blocks
	.byte $20 | $0A, $20, $40; Wooden blocks
	.byte $20 | $0B, $20, $40; Wooden blocks
	.byte $00 | $02, $22, $0A; Oval Background Cloud
	.byte $00 | $03, $2C, $0A; Oval Background Cloud
	.byte $00 | $05, $26, $0A; Oval Background Cloud
	.byte $00 | $12, $26, $0A; Oval Background Cloud
	.byte $20 | $09, $34, $89; Coins
	.byte $60 | $0B, $31, $2F; Background Coconuts
	.byte $00 | $08, $31, $04; Palm Tree
	.byte $00 | $08, $34, $04; Palm Tree
	.byte $00 | $08, $37, $04; Palm Tree
	.byte $00 | $08, $3A, $04; Palm Tree
	.byte $00 | $08, $3D, $04; Palm Tree
	.byte $60 | $19, $31, $2F; Background Coconuts
	.byte $00 | $16, $32, $04; Palm Tree
	.byte $00 | $16, $35, $04; Palm Tree
	.byte $00 | $16, $38, $04; Palm Tree
	.byte $00 | $16, $3B, $04; Palm Tree
	.byte $00 | $16, $3E, $04; Palm Tree
	.byte $00 | $01, $3A, $0A; Oval Background Cloud
	.byte $00 | $04, $34, $0A; Oval Background Cloud
	.byte $00 | $04, $3E, $0A; Oval Background Cloud
	.byte $00 | $11, $3C, $0A; Oval Background Cloud
	.byte $00 | $12, $30, $0A; Oval Background Cloud
	.byte $00 | $14, $36, $0A; Oval Background Cloud
	.byte $20 | $03, $44, $81; Coins
	.byte $20 | $03, $47, $81; Coins
	.byte $20 | $03, $4A, $81; Coins
	.byte $20 | $03, $4D, $81; Coins
	.byte $60 | $07, $42, $2F; Background Coconuts
	.byte $00 | $04, $42, $04; Palm Tree
	.byte $00 | $04, $45, $04; Palm Tree
	.byte $00 | $04, $48, $04; Palm Tree
	.byte $00 | $04, $4B, $04; Palm Tree
	.byte $00 | $04, $4E, $04; Palm Tree
	.byte $20 | $08, $42, $3F; Bricks with single coins
	.byte $60 | $0B, $43, $20; Background Coconuts
	.byte $60 | $0B, $46, $20; Background Coconuts
	.byte $60 | $0B, $49, $20; Background Coconuts
	.byte $60 | $0B, $4C, $20; Background Coconuts
	.byte $60 | $0B, $4F, $20; Background Coconuts
	.byte $20 | $13, $47, $83; Coins
	.byte $00 | $18, $42, $70; Medium sandstone blocks
	.byte $00 | $17, $4C, $80; Large sandstone blocks
	.byte $60 | $19, $41, $20; Background Coconuts
	.byte $60 | $1A, $47, $93; Horizontal Plain Background A (used to block out stuff)
	.byte $20 | $18, $48, $41; Wooden blocks
	.byte $00 | $01, $4E, $0A; Oval Background Cloud
	.byte $00 | $13, $42, $0A; Oval Background Cloud
	.byte $00 | $01, $44, $0A; Oval Background Cloud
	.byte $20 | $03, $50, $81; Coins
	.byte $60 | $07, $53, $20; Background Coconuts
	.byte $00 | $04, $51, $04; Palm Tree
	.byte $20 | $08, $52, $31; Bricks with single coins
	.byte $60 | $0B, $52, $20; Background Coconuts
	.byte $60 | $0B, $55, $20; Background Coconuts
	.byte $60 | $0B, $58, $20; Background Coconuts
	.byte $60 | $0B, $5D, $21; Background Coconuts
	.byte $00 | $08, $5A, $04; Palm Tree
	.byte $00 | $08, $5F, $04; Palm Tree
	.byte $60 | $19, $53, $20; Background Coconuts
	.byte $00 | $17, $5C, $80; Large sandstone blocks
	.byte $60 | $1A, $55, $94; Horizontal Plain Background A (used to block out stuff)
	.byte $20 | $17, $5B, $01; '?' with leaf
	.byte $20 | $15, $5E, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $03, $56, $0A; Oval Background Cloud
	.byte $00 | $04, $5E, $0A; Oval Background Cloud
	.byte $00 | $12, $50, $0A; Oval Background Cloud
	.byte $00 | $12, $5C, $0A; Oval Background Cloud
	.byte $00 | $14, $56, $0A; Oval Background Cloud
	.byte $20 | $04, $67, $80; Coins
	.byte $20 | $04, $6B, $80; Coins
	.byte $20 | $07, $65, $80; Coins
	.byte $20 | $07, $69, $80; Coins
	.byte $20 | $07, $6D, $80; Coins
	.byte $20 | $09, $63, $80; Coins
	.byte $20 | $09, $67, $80; Coins
	.byte $20 | $09, $6B, $80; Coins
	.byte $20 | $09, $6F, $80; Coins
	.byte $20 | $06, $6D, $0D; Brick with P-Switch
	.byte $00 | $18, $63, $70; Medium sandstone blocks
	.byte $00 | $17, $68, $80; Large sandstone blocks
	.byte $20 | $03, $67, $10; Bricks
	.byte $20 | $03, $6B, $10; Bricks
	.byte $20 | $06, $65, $10; Bricks
	.byte $20 | $06, $69, $10; Bricks
	.byte $20 | $08, $63, $10; Bricks
	.byte $20 | $08, $67, $10; Bricks
	.byte $20 | $08, $6B, $10; Bricks
	.byte $20 | $08, $6F, $10; Bricks
	.byte $20 | $0B, $65, $10; Bricks
	.byte $20 | $0B, $69, $10; Bricks
	.byte $20 | $0B, $6D, $10; Bricks
	.byte $00 | $13, $6A, $0A; Oval Background Cloud
	.byte $20 | $16, $71, $8A; Coins
	.byte $20 | $17, $71, $8A; Coins
	.byte $20 | $18, $71, $8A; Coins
	.byte $20 | $19, $71, $8A; Coins
	.byte $00 | $16, $72, $70; Medium sandstone blocks
	.byte $00 | $18, $72, $70; Medium sandstone blocks
	.byte $00 | $16, $77, $70; Medium sandstone blocks
	.byte $00 | $18, $77, $70; Medium sandstone blocks
	.byte $00 | $16, $7C, $70; Medium sandstone blocks
	.byte $00 | $18, $7C, $70; Medium sandstone blocks
	.byte $20 | $0A, $74, $60; Note Blocks - movable two directions
	.byte $20 | $0B, $77, $60; Note Blocks - movable two directions
	.byte $20 | $0C, $7A, $60; Note Blocks - movable two directions
	.byte $20 | $0D, $7D, $60; Note Blocks - movable two directions
	.byte $00 | $03, $7A, $0A; Oval Background Cloud
	.byte $00 | $06, $74, $0A; Oval Background Cloud
	.byte $00 | $10, $7A, $0A; Oval Background Cloud
	.byte $00 | $12, $7E, $0A; Oval Background Cloud
	.byte $00 | $12, $72, $0A; Oval Background Cloud
	.byte $00 | $16, $81, $70; Medium sandstone blocks
	.byte $00 | $18, $81, $70; Medium sandstone blocks
	.byte $00 | $16, $86, $04; Palm Tree
	.byte $40 | $0E, $80, $02; Note Block with Leaf
	.byte $00 | $03, $84, $0A; Oval Background Cloud
	.byte $00 | $05, $80, $0A; Oval Background Cloud
	.byte $00 | $10, $86, $0A; Oval Background Cloud
	.byte $00 | $14, $84, $0A; Oval Background Cloud
	.byte $40 | $00, $89, $09; Level Ending
	.byte $FF
Level_4_W2_objects:
	.byte $73, $11, $17; Para-Goomba
	.byte $6D, $14, $16; Red Koopa Troopa
	.byte $77, $16, $0A; Cheep-Cheep
	.byte $6D, $1A, $16; Red Koopa Troopa
	.byte $6D, $23, $17; Red Koopa Troopa
	.byte $82, $30, $18; Boomerang Brother
	.byte $6E, $3A, $19; Green Koopa Paratroopa (bounces)
	.byte $6D, $44, $17; Red Koopa Troopa
	.byte $82, $4E, $15; Boomerang Brother
	.byte $6F, $55, $04; Red Koopa Paratroopa
	.byte $6F, $58, $04; Red Koopa Paratroopa
	.byte $A4, $5E, $15; Green Venus Fire Trap (upward)
	.byte $82, $6B, $15; Boomerang Brother
	.byte $82, $95, $18; Boomerang Brother
	.byte $41, $98, $15; Goal Card
	.byte $FF
; Quicksand_W2
; Object Set 3
Quicksand_W2_generators:
Quicksand_W2_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_14 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $13; Start action | Graphic set
	.byte $80 | $08; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $1A, $00, $80, $05; Flat Land - Hilly
	.byte $80 | $1A, $06, $50, $03; Hilly Wall
	.byte $80 | $18, $0A, $82, $03; Flat Land - Hilly
	.byte $60 | $18, $08, $61; 30 Degree Hill - Down/Left
	.byte $00 | $18, $0E, $50; 45 Degree Hill - Down/Right
	.byte $60 | $19, $0E, $E1; Hilly Wall - Right Side
	.byte $40 | $1A, $0F, $D0, $0C; Normal Quicksand
	.byte $80 | $19, $02, $D2; Small Background Hills
	.byte $80 | $18, $14, $82, $02; Flat Land - Hilly
	.byte $00 | $18, $13, $60; 45 Degree Hill - Down/Left
	.byte $00 | $19, $13, $E1; Hilly Wall - Left Side
	.byte $00 | $18, $17, $50; 45 Degree Hill - Down/Right
	.byte $60 | $19, $17, $E1; Hilly Wall - Right Side
	.byte $80 | $18, $1D, $82, $0A; Flat Land - Hilly
	.byte $00 | $18, $1C, $60; 45 Degree Hill - Down/Left
	.byte $00 | $19, $1C, $E1; Hilly Wall - Left Side
	.byte $00 | $18, $27, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $19, $27, $E1; Hilly Wall - Right Side
	.byte $40 | $19, $28, $D1, $07; Normal Quicksand
	.byte $80 | $17, $20, $D2; Small Background Hills
	.byte $80 | $18, $31, $82, $01; Flat Land - Hilly
	.byte $00 | $18, $30, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $19, $30, $E1; Hilly Wall - Left Side
	.byte $80 | $1A, $33, $50, $03; Hilly Wall
	.byte $60 | $18, $33, $51; 30 Degree Hill - Down/Right
	.byte $80 | $1A, $37, $80, $68; Flat Land - Hilly
	.byte $80 | $19, $3B, $D2; Small Background Hills
	.byte $80 | $19, $40, $D2; Small Background Hills
	.byte $80 | $19, $4A, $D1; Small Background Hills
	.byte $20 | $19, $58, $17; Bricks
	.byte $20 | $19, $68, $17; Bricks
	.byte $20 | $19, $78, $17; Bricks
	.byte $20 | $19, $88, $17; Bricks
	.byte $20 | $19, $98, $16; Bricks
	.byte $80 | $1A, $A0, $50, $08; Hilly Wall
	.byte $60 | $19, $A0, $60; 30 Degree Hill - Down/Left
	.byte $00 | $19, $A2, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $1A, $A2, $E0; Hilly Wall - Right Side
	.byte $40 | $1A, $A3, $D0, $02; Normal Quicksand
	.byte $00 | $19, $A6, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $1A, $A6, $E0; Hilly Wall - Left Side
	.byte $60 | $19, $A7, $50; 30 Degree Hill - Down/Right
	.byte $80 | $1A, $A9, $80, $04; Flat Land - Hilly
	.byte $80 | $1A, $AE, $50, $01; Hilly Wall
	.byte $80 | $17, $B0, $83, $03; Flat Land - Hilly
	.byte $00 | $17, $B0, $62; 45 Degree Hill - Down/Left
	.byte $00 | $17, $B3, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $18, $B3, $E2; Hilly Wall - Right Side
	.byte $40 | $18, $B4, $D2, $06; Normal Quicksand
	.byte $80 | $17, $BB, $83, $01; Flat Land - Hilly
	.byte $80 | $1A, $BD, $50, $02; Hilly Wall
	.byte $00 | $17, $BB, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $18, $BB, $E2; Hilly Wall - Left Side
	.byte $00 | $17, $BD, $52; 45 Degree Hill - Down/Right
	.byte $80 | $1A, $C0, $80, $1F; Flat Land - Hilly
	.byte $40 | $00, $C0, $09; Level Ending
	.byte $FF
Quicksand_W2_objects:
	.byte $AF, $02, $11; The Angry Sun
	.byte $A4, $1A, $1A; Green Venus Fire Trap (upward)
	.byte $6F, $1B, $12; Red Koopa Paratroopa
	.byte $A4, $29, $19; Green Venus Fire Trap (upward)
	.byte $A4, $2C, $19; Green Venus Fire Trap (upward)
	.byte $6C, $37, $19; Green Koopa Troopa
	.byte $5D, $51, $12; Tornado
	.byte $6E, $7E, $16; Green Koopa Paratroopa (bounces)
	.byte $6E, $9E, $16; Green Koopa Paratroopa (bounces)
	.byte $41, $D8, $15; Goal Card
	.byte $FF
; Hammer_Bros_2_W2
; Object Set 9
Hammer_Bros_2_W2_generators:
Hammer_Bros_2_W2_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_09; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $09; Start action | Graphic set
	.byte $80 | $06; Time | Music
	.byte $00 | $11, $04, $0A; Oval Background Cloud
	.byte $00 | $11, $0C, $0A; Oval Background Cloud
	.byte $00 | $14, $0A, $0A; Oval Background Cloud
	.byte $00 | $16, $00, $04; Palm Tree
	.byte $00 | $16, $05, $04; Palm Tree
	.byte $00 | $16, $0D, $04; Palm Tree
	.byte $60 | $19, $00, $20; Background Coconuts
	.byte $60 | $19, $02, $23; Background Coconuts
	.byte $60 | $19, $07, $20; Background Coconuts
	.byte $00 | $18, $09, $62; Small sandstone blocks
	.byte $00 | $19, $09, $62; Small sandstone blocks
	.byte $FF
Hammer_Bros_2_W2_objects:
	.byte $81, $0B, $16; Hammer Brother
	.byte $81, $07, $18; Hammer Brother
	.byte $BA, $0D, $14; Exit on get treasure chest
	.byte $FF
; Kings_Room_W2
; Object Set 2
Kings_Room_W2_generators:
Kings_Room_W2_header:
	.byte $0A; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; Weird
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Kings_Room_W2_objects:
	.byte $D5, $0A, $16; 'The king has been transformed' message
	.byte $FF
; Level_5_W2
; Object Set 9
Level_5_W2_generators:
Level_5_W2_header:
	.byte $22; Next Level
	.byte LEVEL1_SIZE_10 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_09; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $09; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $07, $08, $0A; Oval Background Cloud
	.byte $00 | $0D, $04, $0A; Oval Background Cloud
	.byte $00 | $10, $0A, $0A; Oval Background Cloud
	.byte $20 | $18, $04, $40; Wooden blocks
	.byte $20 | $19, $04, $40; Wooden blocks
	.byte $20 | $19, $09, $40; Wooden blocks
	.byte $20 | $18, $0E, $40; Wooden blocks
	.byte $20 | $19, $0E, $40; Wooden blocks
	.byte $20 | $17, $0A, $20; '?' blocks with single coins
	.byte $20 | $17, $0B, $01; '?' with leaf
	.byte $00 | $05, $10, $0A; Oval Background Cloud
	.byte $00 | $08, $1A, $0A; Oval Background Cloud
	.byte $00 | $0D, $12, $0A; Oval Background Cloud
	.byte $00 | $12, $1A, $0A; Oval Background Cloud
	.byte $00 | $10, $11, $20; Medium block platforms
	.byte $00 | $12, $12, $20; Medium block platforms
	.byte $00 | $14, $14, $30; Large block platforms
	.byte $00 | $17, $11, $30; Large block platforms
	.byte $20 | $19, $19, $40; Wooden blocks
	.byte $20 | $12, $1E, $40; Wooden blocks
	.byte $20 | $13, $1E, $40; Wooden blocks
	.byte $20 | $17, $1E, $40; Wooden blocks
	.byte $40 | $19, $1E, $05; Wooden Block with Leaf
	.byte $20 | $17, $1F, $10; Bricks
	.byte $00 | $05, $28, $0A; Oval Background Cloud
	.byte $00 | $0A, $22, $0A; Oval Background Cloud
	.byte $00 | $11, $26, $0A; Oval Background Cloud
	.byte $00 | $15, $2C, $0A; Oval Background Cloud
	.byte $20 | $18, $20, $15; Bricks
	.byte $60 | $1A, $2A, $92; Horizontal Plain Background A (used to block out stuff)
	.byte $00 | $18, $2E, $21; Medium block platforms
	.byte $00 | $0B, $3C, $0A; Oval Background Cloud
	.byte $00 | $0C, $30, $0A; Oval Background Cloud
	.byte $00 | $10, $34, $0A; Oval Background Cloud
	.byte $00 | $11, $38, $20; Medium block platforms
	.byte $00 | $12, $3E, $21; Medium block platforms
	.byte $00 | $13, $38, $30; Large block platforms
	.byte $00 | $14, $34, $20; Medium block platforms
	.byte $00 | $14, $3E, $40; X-Large block platforms
	.byte $00 | $16, $32, $20; Medium block platforms
	.byte $00 | $16, $36, $40; X-Large block platforms
	.byte $20 | $06, $38, $41; Wooden blocks
	.byte $60 | $06, $3C, $61; Cloud Platform
	.byte $20 | $04, $38, $91; Downward Pipe (CAN go down)
	.byte $20 | $18, $3E, $41; Wooden blocks
	.byte $20 | $19, $3E, $41; Wooden blocks
	.byte $20 | $19, $34, $40; Wooden blocks
	.byte $00 | $0B, $48, $0A; Oval Background Cloud
	.byte $00 | $10, $42, $0A; Oval Background Cloud
	.byte $00 | $12, $4C, $0A; Oval Background Cloud
	.byte $00 | $13, $48, $0A; Oval Background Cloud
	.byte $00 | $12, $4F, $20; Medium block platforms
	.byte $60 | $06, $40, $61; Cloud Platform
	.byte $60 | $06, $44, $61; Cloud Platform
	.byte $60 | $06, $48, $63; Cloud Platform
	.byte $60 | $06, $4E, $63; Cloud Platform
	.byte $20 | $04, $40, $81; Coins
	.byte $20 | $04, $44, $81; Coins
	.byte $20 | $04, $49, $81; Coins
	.byte $20 | $04, $4F, $81; Coins
	.byte $20 | $14, $4F, $4B; Wooden blocks
	.byte $20 | $15, $4F, $4B; Wooden blocks
	.byte $20 | $16, $46, $47; Wooden blocks
	.byte $20 | $16, $4F, $4B; Wooden blocks
	.byte $20 | $17, $46, $49; Wooden blocks
	.byte $20 | $18, $40, $4F; Wooden blocks
	.byte $20 | $19, $40, $4F; Wooden blocks
	.byte $40 | $17, $4E, $82, $00; Water (still)
	.byte $00 | $08, $5C, $0A; Oval Background Cloud
	.byte $00 | $0B, $52, $0A; Oval Background Cloud
	.byte $00 | $10, $56, $0A; Oval Background Cloud
	.byte $00 | $11, $5F, $0A; Oval Background Cloud
	.byte $60 | $06, $55, $65; Cloud Platform
	.byte $20 | $04, $56, $83; Coins
	.byte $20 | $14, $56, $44; Wooden blocks
	.byte $20 | $15, $56, $44; Wooden blocks
	.byte $20 | $15, $5C, $44; Wooden blocks
	.byte $20 | $16, $56, $44; Wooden blocks
	.byte $20 | $16, $5C, $41; Wooden blocks
	.byte $20 | $19, $5B, $0C; Brick with Vine
	.byte $20 | $19, $5C, $11; Bricks
	.byte $20 | $15, $5F, $41; Wooden blocks
	.byte $20 | $17, $50, $4A; Wooden blocks
	.byte $20 | $17, $5C, $41; Wooden blocks
	.byte $20 | $17, $5F, $4B; Wooden blocks
	.byte $20 | $18, $50, $4A; Wooden blocks
	.byte $20 | $18, $5C, $41; Wooden blocks
	.byte $20 | $18, $5F, $41; Wooden blocks
	.byte $20 | $19, $50, $4A; Wooden blocks
	.byte $00 | $12, $57, $20; Medium block platforms
	.byte $20 | $18, $5C, $11; Bricks
	.byte $20 | $13, $56, $30; Bricks with single coins
	.byte $00 | $03, $64, $0A; Oval Background Cloud
	.byte $00 | $07, $68, $0A; Oval Background Cloud
	.byte $00 | $0B, $62, $0A; Oval Background Cloud
	.byte $00 | $0C, $6A, $0A; Oval Background Cloud
	.byte $00 | $10, $66, $0A; Oval Background Cloud
	.byte $00 | $12, $6E, $0A; Oval Background Cloud
	.byte $00 | $02, $6E, $21; Medium block platforms
	.byte $20 | $04, $6E, $D1; Upward Pipe (CAN'T go up)
	.byte $00 | $08, $6F, $21; Medium block platforms
	.byte $20 | $14, $62, $42; Wooden blocks
	.byte $20 | $15, $62, $42; Wooden blocks
	.byte $20 | $16, $62, $48; Wooden blocks
	.byte $20 | $18, $61, $4F; Wooden blocks
	.byte $20 | $19, $60, $4F; Wooden blocks
	.byte $00 | $0E, $72, $0A; Oval Background Cloud
	.byte $00 | $0E, $78, $0A; Oval Background Cloud
	.byte $00 | $14, $74, $0A; Oval Background Cloud
	.byte $00 | $02, $7A, $20; Medium block platforms
	.byte $00 | $04, $70, $22; Medium block platforms
	.byte $00 | $06, $72, $21; Medium block platforms
	.byte $20 | $19, $77, $40; Wooden blocks
	.byte $20 | $03, $76, $22; '?' blocks with single coins
	.byte $20 | $03, $79, $01; '?' with leaf
	.byte $20 | $19, $70, $40; Wooden blocks
	.byte $40 | $00, $88, $09; Level Ending
	; Pointer on screen $03
	.byte $E0 | $03, $40 | $02, 16; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_5_W2_objects:
	.byte $89, $09, $19; Chain Chomp
	.byte $89, $19, $19; Chain Chomp
	.byte $6D, $22, $17; Red Koopa Troopa
	.byte $89, $34, $19; Chain Chomp
	.byte $72, $34, $13; Goomba
	.byte $72, $35, $19; Goomba
	.byte $72, $43, $11; Goomba
	.byte $72, $43, $17; Goomba
	.byte $6D, $52, $11; Red Koopa Troopa
	.byte $6D, $52, $13; Red Koopa Troopa
	.byte $6D, $64, $13; Red Koopa Troopa
	.byte $6D, $69, $15; Red Koopa Troopa
	.byte $6D, $6F, $17; Red Koopa Troopa
	.byte $41, $98, $15; Goal Card
	.byte $89, $9A, $19; Chain Chomp
	.byte $FF
; Pyramid_Outside_Area_W2
; Object Set 9
Pyramid_Outside_Area_W2_generators:
Pyramid_Outside_Area_W2_header:
	.byte $23; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $09; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $00, $00, $67; Small sandstone blocks
	.byte $00 | $00, $10, $67; Small sandstone blocks
	.byte $00 | $00, $20, $67; Small sandstone blocks
	.byte $00 | $00, $30, $67; Small sandstone blocks
	.byte $00 | $00, $40, $67; Small sandstone blocks
	.byte $00 | $00, $50, $67; Small sandstone blocks
	.byte $00 | $00, $60, $67; Small sandstone blocks
	.byte $00 | $00, $70, $67; Small sandstone blocks
	.byte $00 | $14, $05, $0C; Background Pyramid
	.byte $00 | $10, $0E, $73; Medium sandstone blocks
	.byte $00 | $12, $0C, $73; Medium sandstone blocks
	.byte $00 | $14, $0A, $20; Medium block platforms
	.byte $00 | $14, $0F, $72; Medium sandstone blocks
	.byte $00 | $16, $08, $74; Medium sandstone blocks
	.byte $00 | $18, $06, $75; Medium sandstone blocks
	.byte $00 | $14, $0E, $0B; Door
	.byte $00 | $00, $10, $90; X-Large sandstone blocks
	.byte $00 | $04, $10, $90; X-Large sandstone blocks
	.byte $00 | $08, $10, $90; X-Large sandstone blocks
	.byte $00 | $0C, $10, $90; X-Large sandstone blocks
	.byte $00 | $00, $28, $71; Medium sandstone blocks
	.byte $00 | $02, $28, $90; X-Large sandstone blocks
	.byte $00 | $06, $28, $90; X-Large sandstone blocks
	.byte $00 | $0A, $28, $90; X-Large sandstone blocks
	.byte $00 | $0E, $28, $90; X-Large sandstone blocks
	.byte $00 | $12, $28, $90; X-Large sandstone blocks
	.byte $00 | $16, $28, $90; X-Large sandstone blocks
	.byte $20 | $18, $38, $91; Downward Pipe (CAN go down)
	.byte $20 | $11, $30, $89; Coins
	.byte $20 | $14, $30, $89; Coins
	.byte $20 | $12, $30, $19; Bricks
	.byte $20 | $15, $30, $19; Bricks
	.byte $20 | $0D, $35, $0B; Brick with 1-up
	.byte $20 | $18, $32, $0D; Brick with P-Switch
	.byte $00 | $08, $34, $60; Small sandstone blocks
	.byte $00 | $09, $34, $60; Small sandstone blocks
	.byte $00 | $08, $30, $70; Medium sandstone blocks
	.byte $00 | $08, $36, $70; Medium sandstone blocks
	.byte $00 | $00, $30, $90; X-Large sandstone blocks
	.byte $00 | $04, $30, $90; X-Large sandstone blocks
	.byte $00 | $02, $3A, $90; X-Large sandstone blocks
	.byte $00 | $06, $3A, $90; X-Large sandstone blocks
	.byte $00 | $0A, $3A, $90; X-Large sandstone blocks
	.byte $00 | $0E, $3A, $90; X-Large sandstone blocks
	.byte $00 | $12, $3A, $90; X-Large sandstone blocks
	.byte $00 | $16, $3A, $90; X-Large sandstone blocks
	.byte $00 | $00, $3A, $70; Medium sandstone blocks
	.byte $00 | $00, $58, $71; Medium sandstone blocks
	.byte $00 | $02, $58, $90; X-Large sandstone blocks
	.byte $00 | $06, $58, $90; X-Large sandstone blocks
	.byte $00 | $0A, $58, $90; X-Large sandstone blocks
	.byte $00 | $0E, $58, $90; X-Large sandstone blocks
	.byte $00 | $12, $58, $90; X-Large sandstone blocks
	.byte $00 | $16, $58, $90; X-Large sandstone blocks
	.byte $20 | $18, $63, $A1; Downward Pipe (CAN'T go down)
	.byte $40 | $00, $6A, $09; Level Ending
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $08, 32; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $03
	.byte $E0 | $03, $70 | $01, 37; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Pyramid_Outside_Area_W2_objects:
	.byte $82, $69, $18; Boomerang Brother
	.byte $41, $78, $15; Goal Card
	.byte $FF
; Hammer_Bros_1_W3
; Object Set 1
Hammer_Bros_1_W3_generators:
Hammer_Bros_1_W3_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $80 | $06; Time | Music
	.byte $00 | $12, $03, $E2; Background Clouds
	.byte $20 | $12, $07, $16; Bricks
	.byte $00 | $13, $0D, $E2; Background Clouds
	.byte $00 | $16, $01, $00; Background Hills A
	.byte $20 | $16, $07, $16; Bricks
	.byte $00 | $19, $06, $99; Background Bushes
	.byte $00 | $1A, $00, $C0, $0F; Flat Ground
	.byte $FF
Hammer_Bros_1_W3_objects:
	.byte $81, $0C, $14; Hammer Brother
	.byte $81, $09, $18; Hammer Brother
	.byte $BA, $0D, $14; Exit on get treasure chest
	.byte $FF
; Hammer_Bros_3_W3
; Object Set 1
Hammer_Bros_3_W3_generators:
Hammer_Bros_3_W3_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $00 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $80 | $06; Time | Music
	.byte $00 | $0F, $04, $E2; Background Clouds
	.byte $00 | $0F, $0D, $E2; Background Clouds
	.byte $00 | $11, $01, $E2; Background Clouds
	.byte $20 | $12, $07, $16; Bricks
	.byte $20 | $16, $07, $16; Bricks
	.byte $40 | $19, $00, $80, $0F; Water (still)
	.byte $00 | $1A, $00, $D0, $0F; Underwater Flat Ground
	.byte $20 | $16, $0A, $07; Brick with Leaf
	.byte $FF
Hammer_Bros_3_W3_objects:
	.byte $81, $0C, $14; Hammer Brother
	.byte $81, $09, $18; Hammer Brother
	.byte $BA, $0D, $14; Exit on get treasure chest
	.byte $FF
; Level_3_W3
; Object Set 1
Level_3_W3_generators:
Level_3_W3_header:
	.byte $24; Next Level
	.byte LEVEL1_SIZE_12 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	.byte $40 | $16, $00, $B4, $09; Blue X-Blocks
	.byte $40 | $16, $0E, $B4, $07; Blue X-Blocks
	.byte $00 | $15, $0F, $95; Background Bushes
	.byte $00 | $11, $05, $E2; Background Clouds
	.byte $00 | $12, $0D, $E2; Background Clouds
	.byte $00 | $13, $02, $01; Background Hills B
	.byte $00 | $15, $07, $92; Background Bushes
	.byte $40 | $16, $17, $B4, $00; Blue X-Blocks
	.byte $40 | $16, $19, $B4, $00; Blue X-Blocks
	.byte $40 | $16, $1B, $B4, $04; Blue X-Blocks
	.byte $00 | $10, $1A, $E2; Background Clouds
	.byte $00 | $12, $1B, $00; Background Hills A
	.byte $20 | $13, $12, $82; Coins
	.byte $20 | $13, $18, $82; Coins
	.byte $40 | $16, $24, $B4, $0B; Blue X-Blocks
	.byte $00 | $11, $2C, $E2; Background Clouds
	.byte $00 | $13, $20, $E2; Background Clouds
	.byte $20 | $14, $26, $40; Wooden Blocks
	.byte $20 | $15, $26, $40; Wooden Blocks
	.byte $20 | $14, $28, $19; Bricks
	.byte $40 | $14, $27, $01; Note Block with Flower
	.byte $00 | $15, $2A, $94; Background Bushes
	.byte $40 | $17, $30, $B3, $0A; Blue X-Blocks
	.byte $40 | $17, $3C, $B3, $01; Blue X-Blocks
	.byte $00 | $12, $36, $E2; Background Clouds
	.byte $00 | $16, $30, $96; Background Bushes
	.byte $20 | $15, $32, $17; Bricks
	.byte $20 | $14, $3A, $12; Bricks
	.byte $20 | $14, $30, $0D; Brick with P-Switch
	.byte $40 | $16, $42, $B4, $02; Blue X-Blocks
	.byte $40 | $16, $49, $B4, $02; Blue X-Blocks
	.byte $40 | $14, $4D, $B6, $00; Blue X-Blocks
	.byte $00 | $11, $4B, $E2; Background Clouds
	.byte $00 | $13, $42, $E2; Background Clouds
	.byte $00 | $15, $43, $90; Background Bushes
	.byte $00 | $15, $4A, $90; Background Bushes
	.byte $40 | $16, $58, $B4, $04; Blue X-Blocks
	.byte $40 | $16, $5E, $B4, $00; Blue X-Blocks
	.byte $00 | $13, $55, $E2; Background Clouds
	.byte $00 | $15, $59, $91; Background Bushes
	.byte $20 | $15, $58, $0D; Brick with P-Switch
	.byte $20 | $12, $5A, $06; Brick with Flower
	.byte $40 | $15, $5B, $E1; White Turtle Bricks
	.byte $40 | $16, $60, $B4, $03; Blue X-Blocks
	.byte $40 | $17, $6D, $B3, $01; Blue X-Blocks
	.byte $00 | $11, $64, $E2; Background Clouds
	.byte $20 | $14, $68, $11; Bricks
	.byte $20 | $14, $6C, $11; Bricks
	.byte $20 | $15, $66, $87; Coins
	.byte $40 | $16, $77, $B4, $01; Blue X-Blocks
	.byte $40 | $17, $7E, $B3, $00; Blue X-Blocks
	.byte $00 | $13, $76, $E2; Background Clouds
	.byte $20 | $11, $74, $11; Bricks
	.byte $20 | $13, $79, $11; Bricks
	.byte $20 | $14, $72, $11; Bricks
	.byte $20 | $14, $7D, $11; Bricks
	.byte $20 | $15, $70, $87; Coins
	.byte $20 | $15, $7A, $87; Coins
	.byte $40 | $15, $82, $B5, $01; Blue X-Blocks
	.byte $40 | $16, $88, $B4, $01; Blue X-Blocks
	.byte $40 | $17, $8F, $B3, $01; Blue X-Blocks
	.byte $00 | $11, $83, $E2; Background Clouds
	.byte $00 | $13, $8B, $E2; Background Clouds
	.byte $20 | $15, $84, $86; Coins
	.byte $20 | $16, $8C, $87; Coins
	.byte $40 | $15, $94, $B5, $01; Blue X-Blocks
	.byte $40 | $17, $96, $B3, $01; Blue X-Blocks
	.byte $00 | $11, $91, $E2; Background Clouds
	.byte $00 | $14, $9D, $E2; Background Clouds
	.byte $20 | $16, $96, $87; Coins
	.byte $20 | $16, $9F, $84; Coins
	.byte $20 | $11, $99, $11; Bricks
	.byte $20 | $10, $94, $81; Coins
	.byte $20 | $11, $94, $81; Coins
	.byte $40 | $18, $A5, $B2, $05; Blue X-Blocks
	.byte $40 | $14, $A5, $B4, $00; Blue X-Blocks
	.byte $00 | $11, $AB, $E2; Background Clouds
	.byte $20 | $10, $A5, $80; Coins
	.byte $20 | $11, $A5, $80; Coins
	.byte $20 | $12, $A5, $80; Coins
	.byte $20 | $13, $A5, $80; Coins
	.byte $20 | $15, $A7, $92; Downward Pipe (CAN go down)
	.byte $40 | $16, $B7, $B0, $00; Blue X-Blocks
	.byte $40 | $17, $BB, $B3, $03; Blue X-Blocks
	.byte $20 | $14, $BC, $0B; Brick with 1-up
	.byte $40 | $19, $00, $81, $7F; Water (still)
	.byte $40 | $19, $80, $81, $3F; Water (still)
	; Pointer on screen $0A
	.byte $E0 | $0A, $60 | $01, 144; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_3_W3_objects:
	.byte $D3, $00, $50; Autoscrolling
	.byte $2D, $00, $19; Boss Bass (surface)
	.byte $64, $10, $19; Surface Cheep-Cheep (jumps out of water)
	.byte $64, $1C, $19; Surface Cheep-Cheep (jumps out of water)
	.byte $43, $22, $19; Jumping Cheep-Cheep (2 jumps, down and right)
	.byte $6C, $2F, $13; Green Koopa Troopa
	.byte $43, $52, $19; Jumping Cheep-Cheep (2 jumps, down and right)
	.byte $92, $52, $15; Spinning Platform (periodical clockwise)
	.byte $6D, $63, $15; Red Koopa Troopa
	.byte $43, $6C, $19; Jumping Cheep-Cheep (2 jumps, down and right)
	.byte $43, $86, $19; Jumping Cheep-Cheep (2 jumps, down and right)
	.byte $43, $96, $19; Jumping Cheep-Cheep (2 jumps, down and right)
	.byte $92, $9E, $11; Spinning Platform (periodical clockwise)
	.byte $FF
; Level_2_W3
; Object Set 4
Level_2_W3_generators:
Level_2_W3_header:
	.byte $25; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_04; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $04; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $15, $00, $02; Blue Background Pole A
	.byte $00 | $15, $07, $03; Blue Background Pole B
	.byte $00 | $16, $00, $10, $07; Wooden platform
	.byte $00 | $11, $02, $01; Large Swirly Background Cloud
	.byte $00 | $15, $02, $43; Background Bushes
	.byte $00 | $17, $0D, $B0; 45 Degree Platform Wire - Up/Right
	.byte $00 | $15, $0C, $A1; 45 Degree Platform Wire - Down/Right
	.byte $00 | $14, $0C, $B1; 45 Degree Platform Wire - Up/Right
	.byte $00 | $11, $0C, $A1; 45 Degree Platform Wire - Down/Right
	.byte $00 | $10, $0B, $07; Blue gear
	.byte $00 | $18, $0C, $07; Blue gear
	.byte $00 | $12, $0E, $01; Large Swirly Background Cloud
	.byte $00 | $17, $11, $B1; 45 Degree Platform Wire - Up/Right
	.byte $00 | $14, $11, $A1; 45 Degree Platform Wire - Down/Right
	.byte $00 | $13, $11, $B0; 45 Degree Platform Wire - Up/Right
	.byte $00 | $12, $12, $07; Blue gear
	.byte $00 | $18, $10, $07; Blue gear
	.byte $00 | $16, $15, $02; Blue Background Pole A
	.byte $00 | $16, $19, $03; Blue Background Pole B
	.byte $00 | $17, $15, $10, $04; Wooden platform
	.byte $60 | $13, $16, $44; Donut Blocks
	.byte $20 | $13, $19, $00; '?' with flower
	.byte $00 | $11, $1E, $01; Large Swirly Background Cloud
	.byte $20 | $12, $21, $40; Wooden blocks
	.byte $40 | $13, $21, $06; Wooden Block with Star
	.byte $20 | $14, $21, $44; Wooden blocks
	.byte $00 | $13, $23, $41; Background Bushes
	.byte $00 | $10, $26, $01; Large Swirly Background Cloud
	.byte $20 | $14, $28, $82; Coins
	.byte $20 | $12, $2C, $82; Coins
	.byte $20 | $14, $2D, $20; '?' blocks with single coins
	.byte $20 | $14, $31, $82; Coins
	.byte $00 | $12, $36, $01; Large Swirly Background Cloud
	.byte $00 | $14, $3B, $00; Small Swirly Background Cloud
	.byte $00 | $10, $3C, $01; Large Swirly Background Cloud
	.byte $20 | $15, $36, $03; '?' with continuous star
	.byte $20 | $12, $40, $82; Coins
	.byte $00 | $12, $46, $01; Large Swirly Background Cloud
	.byte $60 | $16, $4E, $41; Donut Blocks
	.byte $20 | $13, $4F, $03; '?' with continuous star
	.byte $20 | $14, $52, $82; Coins
	.byte $20 | $18, $51, $40; Wooden blocks
	.byte $00 | $13, $64, $01; Large Swirly Background Cloud
	.byte $00 | $10, $68, $01; Large Swirly Background Cloud
	.byte $20 | $13, $6F, $15; Bricks
	.byte $20 | $13, $71, $0D; Brick with P-Switch
	.byte $00 | $10, $76, $01; Large Swirly Background Cloud
	.byte $20 | $10, $73, $82; Coins
	.byte $20 | $13, $7B, $92; Downward Pipe (CAN go down)
	.byte $20 | $16, $7B, $41; Wooden blocks
	.byte $20 | $13, $79, $10; Bricks
	.byte $20 | $13, $78, $0F; Invisible 1-up
	.byte $20 | $17, $78, $82; Coins
	.byte $20 | $13, $7E, $30; Bricks with single coins
	.byte $20 | $17, $7E, $00; '?' with flower
	.byte $40 | $19, $00, $81, $80; Water (still)
	.byte $00 | $16, $1D, $A0; 45 Degree Platform Wire - Down/Right
	.byte $00 | $16, $1E, $8F; Horizontal platform wire
	.byte $00 | $16, $2E, $83; Horizontal platform wire
	.byte $00 | $17, $32, $A0; 45 Degree Platform Wire - Down/Right
	.byte $00 | $17, $33, $86; Horizontal platform wire
	.byte $00 | $17, $3A, $B2; 45 Degree Platform Wire - Up/Right
	.byte $00 | $15, $3D, $A2; 45 Degree Platform Wire - Down/Right
	.byte $00 | $17, $40, $B2; 45 Degree Platform Wire - Up/Right
	.byte $00 | $15, $43, $A2; 45 Degree Platform Wire - Down/Right
	.byte $00 | $17, $46, $B0; 45 Degree Platform Wire - Up/Right
	.byte $00 | $16, $47, $82; Horizontal platform wire
	.byte $00 | $16, $4A, $B0; 45 Degree Platform Wire - Up/Right
	.byte $00 | $16, $54, $A0; 45 Degree Platform Wire - Down/Right
	.byte $00 | $16, $55, $8A; Horizontal platform wire
	.byte $00 | $17, $60, $A0; 45 Degree Platform Wire - Down/Right
	.byte $00 | $17, $61, $83; Horizontal platform wire
	.byte $00 | $17, $65, $B2; 45 Degree Platform Wire - Up/Right
	.byte $00 | $14, $68, $83; Horizontal platform wire
	.byte $00 | $15, $6C, $A2; 45 Degree Platform Wire - Down/Right
	.byte $00 | $17, $6F, $B0; 45 Degree Platform Wire - Up/Right
	.byte $00 | $16, $70, $84; Horizontal platform wire
	.byte $00 | $16, $75, $B0; 45 Degree Platform Wire - Up/Right
	; Pointer on screen $07
	.byte $E0 | $07, $50 | $02, 144; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_2_W3_objects:
	.byte $D3, $00, $60; Autoscrolling
	.byte $3B, $00, $19; Surface Cheep-Cheep (swims along surface)
	.byte $3C, $0B, $11; Wired platform (follows platform wires)
	.byte $3C, $0F, $17; Wired platform (follows platform wires)
	.byte $44, $1B, $15; Falling Platform (falls when stepped on)
	.byte $6F, $2F, $13; Red Koopa Paratroopa
	.byte $64, $37, $19; Surface Cheep-Cheep (jumps out of water)
	.byte $64, $3C, $19; Surface Cheep-Cheep (jumps out of water)
	.byte $64, $4A, $19; Surface Cheep-Cheep (jumps out of water)
	.byte $64, $4E, $19; Surface Cheep-Cheep (jumps out of water)
	.byte $64, $5C, $19; Surface Cheep-Cheep (jumps out of water)
	.byte $64, $5F, $19; Surface Cheep-Cheep (jumps out of water)
	.byte $44, $52, $15; Falling Platform (falls when stepped on)
	.byte $6F, $6B, $10; Red Koopa Paratroopa
	.byte $64, $6A, $19; Surface Cheep-Cheep (jumps out of water)
	.byte $64, $6F, $19; Surface Cheep-Cheep (jumps out of water)
	.byte $A4, $7B, $13; Green Venus Fire Trap (upward)
	.byte $FF
; Level_4_W3
; Object Set 14
Level_4_W3_generators:
Level_4_W3_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_13 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_14; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $13; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $16, $00, $83, $09; Flat Land - Hilly
	.byte $80 | $19, $0A, $50, $05; Hilly Fill
	.byte $60 | $16, $0A, $52; 30 Degree Hill - Down/Right
	.byte $80 | $15, $00, $D8; Small Background Hills
	.byte $A0 | $10, $02, $32; Background Clouds
	.byte $80 | $19, $10, $80, $15; Flat Land - Hilly
	.byte $20 | $19, $1A, $43; Wooden blocks
	.byte $20 | $1A, $1A, $43; Wooden blocks
	.byte $80 | $19, $1B, $31, $01; Water
	.byte $00 | $19, $19, $04; Upper Right Hill Corner - Hilly
	.byte $00 | $19, $1E, $01; Upper Left Hill Corner - Hilly
	.byte $80 | $18, $17, $D1; Small Background Hills
	.byte $80 | $18, $1F, $D1; Small Background Hills
	.byte $20 | $17, $14, $A1; Downward Pipe (CAN'T go down)
	.byte $A0 | $11, $1B, $32; Background Clouds
	.byte $80 | $12, $28, $87, $03; Flat Land - Hilly
	.byte $80 | $14, $26, $55, $01; Hilly Fill
	.byte $80 | $19, $2C, $50, $0F; Hilly Fill
	.byte $00 | $12, $27, $61; 45 Degree Hill - Down/Left
	.byte $60 | $12, $2C, $56; 30 Degree Hill - Down/Right
	.byte $80 | $11, $29, $D1; Small Background Hills
	.byte $00 | $14, $26, $E4; Hilly Wall - Left Side
	.byte $20 | $17, $22, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $25, $01; '?' with leaf
	.byte $80 | $19, $3A, $80, $00; Flat Land - Hilly
	.byte $00 | $18, $3B, $60; 45 Degree Hill - Down/Left
	.byte $00 | $18, $3C, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $19, $3C, $F0; Underground Wall - Right Side
	.byte $80 | $19, $3D, $31, $08; Water
	.byte $80 | $12, $46, $87, $03; Flat Land - Hilly
	.byte $00 | $12, $45, $60; 45 Degree Hill - Down/Left
	.byte $00 | $13, $45, $E5; Hilly Wall - Left Side
	.byte $00 | $19, $45, $F0; Underground Wall - Left Side
	.byte $60 | $12, $4A, $57; 30 Degree Hill - Down/Right
	.byte $20 | $13, $43, $0E; Invisible Coin
	.byte $20 | $17, $44, $0E; Invisible Coin
	.byte $80 | $19, $58, $80, $29; Flat Land - Hilly
	.byte $20 | $16, $5C, $21; '?' blocks with single coins
	.byte $80 | $18, $5D, $D2; Small Background Hills
	.byte $40 | $16, $5F, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $17, $5E, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $A0 | $11, $54, $32; Background Clouds
	.byte $20 | $00, $66, $AE; Downward Pipe (CAN'T go down)
	.byte $20 | $0E, $66, $D3; Upward Pipe (CAN'T go up)
	.byte $40 | $12, $63, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $12, $6A, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $13, $62, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $13, $65, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $13, $68, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $13, $6B, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $14, $64, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $14, $69, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $15, $60, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $15, $63, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $15, $6A, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $15, $6D, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $16, $62, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $16, $65, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $16, $68, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $16, $6B, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $16, $6E, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $17, $61, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $17, $64, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $17, $69, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $17, $6C, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $17, $6F, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $20 | $14, $61, $20; '?' blocks with single coins
	.byte $20 | $14, $6C, $00; '?' with flower
	.byte $20 | $18, $61, $40; Wooden blocks
	.byte $20 | $17, $66, $30; Bricks with single coins
	.byte $20 | $17, $67, $0D; Brick with P-Switch
	.byte $20 | $18, $6C, $40; Wooden blocks
	.byte $80 | $18, $6F, $D1; Small Background Hills
	.byte $A0 | $10, $6A, $33; Background Clouds
	.byte $20 | $16, $70, $21; '?' blocks with single coins
	.byte $40 | $15, $73, $0A; Background Hills A
	.byte $40 | $16, $7B, $0B; Background Hills B
	.byte $80 | $19, $82, $50, $06; Hilly Fill
	.byte $60 | $16, $86, $62; 30 Degree Hill - Down/Left
	.byte $00 | $16, $88, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $17, $88, $E1; Hilly Wall - Right Side
	.byte $80 | $19, $89, $80, $07; Flat Land - Hilly
	.byte $20 | $16, $89, $35; Bricks with single coins
	.byte $20 | $16, $8A, $0B; Brick with 1-up
	.byte $80 | $18, $8E, $D1; Small Background Hills
	.byte $A0 | $11, $81, $33; Background Clouds
	.byte $00 | $19, $91, $04; Upper Right Hill Corner - Hilly
	.byte $80 | $19, $96, $80, $02; Flat Land - Hilly
	.byte $00 | $19, $96, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $19, $98, $04; Upper Right Hill Corner - Hilly
	.byte $80 | $18, $9B, $81, $00; Flat Land - Hilly
	.byte $00 | $18, $9A, $60; 45 Degree Hill - Down/Left
	.byte $00 | $18, $9C, $50; 45 Degree Hill - Down/Right
	.byte $00 | $19, $9A, $E0; Hilly Wall - Left Side
	.byte $60 | $19, $9C, $E0; Hilly Wall - Right Side
	.byte $80 | $18, $9F, $81, $00; Flat Land - Hilly
	.byte $00 | $18, $9E, $60; 45 Degree Hill - Down/Left
	.byte $00 | $19, $9E, $E0; Hilly Wall - Left Side
	.byte $00 | $18, $A0, $50; 45 Degree Hill - Down/Right
	.byte $60 | $19, $A0, $E0; Hilly Wall - Right Side
	.byte $80 | $17, $A3, $83, $02; Flat Land - Hilly
	.byte $00 | $17, $A2, $60; 45 Degree Hill - Down/Left
	.byte $00 | $18, $A2, $E2; Hilly Wall - Left Side
	.byte $80 | $15, $A6, $85, $01; Flat Land - Hilly
	.byte $00 | $15, $A6, $60; 45 Degree Hill - Down/Left
	.byte $00 | $16, $A6, $E0; Hilly Wall - Left Side
	.byte $80 | $1A, $A8, $50, $09; Hilly Fill
	.byte $60 | $15, $A8, $54; 30 Degree Hill - Down/Right
	.byte $A0 | $11, $AA, $32; Background Clouds
	.byte $20 | $12, $A3, $20; '?' blocks with single coins
	.byte $20 | $12, $A4, $01; '?' with leaf
	.byte $80 | $1A, $B2, $80, $1D; Flat Land - Hilly
	.byte $40 | $12, $B3, $0C; Background Hills C
	.byte $40 | $00, $BA, $09; Level Ending
	.byte $A0 | $1A, $00, $1F; Background like at bottom of hilly level
	.byte $A0 | $1A, $10, $19; Background like at bottom of hilly level
	.byte $A0 | $1A, $1E, $1F; Background like at bottom of hilly level
	.byte $A0 | $1A, $2E, $1E; Background like at bottom of hilly level
	.byte $A0 | $1A, $45, $1F; Background like at bottom of hilly level
	.byte $A0 | $1A, $55, $1F; Background like at bottom of hilly level
	.byte $A0 | $1A, $65, $1F; Background like at bottom of hilly level
	.byte $A0 | $1A, $75, $1F; Background like at bottom of hilly level
	.byte $A0 | $1A, $85, $1C; Background like at bottom of hilly level
	.byte $A0 | $1A, $96, $12; Background like at bottom of hilly level
	.byte $A0 | $1A, $9A, $12; Background like at bottom of hilly level
	.byte $A0 | $1A, $9E, $12; Background like at bottom of hilly level
	.byte $FF
Level_4_W3_objects:
	.byte $72, $0F, $17; Goomba
	.byte $72, $11, $18; Goomba
	.byte $A2, $14, $17; Red Piranha Plant (upward)
	.byte $A6, $22, $17; Red Venus Fire Trap (upward)
	.byte $72, $34, $15; Goomba
	.byte $72, $36, $16; Goomba
	.byte $72, $38, $17; Goomba
	.byte $77, $41, $19; Cheep-Cheep
	.byte $6C, $52, $14; Green Koopa Troopa
	.byte $6C, $54, $15; Green Koopa Troopa
	.byte $6C, $56, $16; Green Koopa Troopa
	.byte $74, $65, $18; Para-Goomba with Micro-Goombas
	.byte $A5, $66, $11; Green Venus Fire Trap (downward)
	.byte $73, $6B, $18; Para-Goomba
	.byte $83, $92, $12; Lakitu
	.byte $41, $C8, $15; Goal Card
	.byte $FF
; Hammer_Bros_2_W3
; Object Set 1
Hammer_Bros_2_W3_generators:
Hammer_Bros_2_W3_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $00 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $80 | $06; Time | Music
	.byte $00 | $0F, $04, $E2; Background Clouds
	.byte $00 | $0F, $0D, $E2; Background Clouds
	.byte $00 | $11, $01, $E2; Background Clouds
	.byte $20 | $12, $07, $16; Bricks
	.byte $20 | $16, $07, $16; Bricks
	.byte $40 | $19, $00, $80, $0F; Water (still)
	.byte $00 | $1A, $00, $D0, $0F; Underwater Flat Ground
	.byte $FF
Hammer_Bros_2_W3_objects:
	.byte $81, $0C, $14; Hammer Brother
	.byte $81, $09, $18; Hammer Brother
	.byte $BA, $0D, $14; Exit on get treasure chest
	.byte $FF
; Dungeon__1_W3
; Object Set 2
Dungeon__1_W3_generators:
Dungeon__1_W3_header:
	.byte $26; Next Level
	.byte LEVEL1_SIZE_11 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $00 | $0F, $00, $4F; Dungeon background
	.byte $00 | $0F, $10, $4F; Dungeon background
	.byte $00 | $0F, $20, $45; Dungeon background
	.byte $00 | $13, $26, $44; Dungeon background
	.byte $00 | $10, $2B, $41; Dungeon background
	.byte $00 | $13, $2D, $4F; Dungeon background
	.byte $00 | $13, $3C, $4B; Dungeon background
	.byte $00 | $10, $48, $41; Dungeon background
	.byte $00 | $13, $4A, $45; Dungeon background
	.byte $00 | $13, $50, $4F; Dungeon background
	.byte $00 | $13, $60, $4A; Dungeon background
	.byte $00 | $10, $6B, $41; Dungeon background
	.byte $00 | $13, $6D, $4F; Dungeon background
	.byte $00 | $13, $7D, $45; Dungeon background
	.byte $60 | $10, $90, $38, $1F; Blank Background (used to block out stuff)
	.byte $00 | $08, $00, $E6, $AF; Horizontally oriented X-blocks
	.byte $00 | $0F, $03, $24; Bottom of background with pillars B
	.byte $00 | $13, $01, $74; Long dungeon windows
	.byte $00 | $15, $15, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $1F, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $17, $1E, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $18, $1D, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $14, $10, $02; Rotodisc block
	.byte $00 | $15, $19, $02; Rotodisc block
	.byte $00 | $15, $20, $E3, $02; Horizontally oriented X-blocks
	.byte $00 | $18, $2A, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $0F, $26, $E0, $79; Horizontally oriented X-blocks
	.byte $00 | $10, $26, $E2, $04; Horizontally oriented X-blocks
	.byte $00 | $10, $2D, $E2, $1A; Horizontally oriented X-blocks
	.byte $20 | $17, $23, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $13, $30, $25; Bottom of background with pillars B
	.byte $00 | $17, $32, $00; Door
	.byte $00 | $17, $3A, $00; Door
	.byte $00 | $10, $4A, $E2, $20; Horizontally oriented X-blocks
	.byte $00 | $17, $48, $E1, $01; Horizontally oriented X-blocks
	.byte $00 | $17, $42, $00; Door
	.byte $00 | $17, $4E, $00; Door
	.byte $00 | $13, $52, $23; Bottom of background with pillars B
	.byte $00 | $17, $58, $00; Door
	.byte $00 | $10, $6D, $E2, $15; Horizontally oriented X-blocks
	.byte $00 | $17, $61, $00; Door
	.byte $00 | $13, $76, $21; Bottom of background with pillars B
	.byte $00 | $17, $71, $00; Door
	.byte $00 | $17, $78, $00; Door
	.byte $00 | $10, $83, $E8, $0C; Horizontally oriented X-blocks
	.byte $00 | $17, $81, $00; Door
	.byte $00 | $10, $90, $E4, $0F; Horizontally oriented X-blocks
	.byte $00 | $08, $A0, $E7, $0F; Horizontally oriented X-blocks
	.byte $00 | $10, $AF, $E8, $00; Horizontally oriented X-blocks
	.byte $00 | $11, $A1, $60; Dungeon windows
	.byte $00 | $11, $AD, $60; Dungeon windows
	; Pointer on screen $03
	.byte $E0 | $03, $40 | $08, 3; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $04
	.byte $E0 | $04, $40 | $08, 177; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $05
	.byte $E0 | $05, $40 | $08, 53; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $06
	.byte $E0 | $06, $40 | $08, 34; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $07
	.byte $E0 | $07, $40 | $08, 84; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $08
	.byte $E0 | $08, $60 | $08, 118; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__1_W3_objects:
	.byte $5A, $10, $14; Single Rotodisc (rotates clockwise)
	.byte $5B, $19, $15; Single Rotodisc (rotates counterclockwise)
	.byte $3F, $14, $18; Dry Bones
	.byte $8A, $2B, $11; Thwomp (normal)
	.byte $2F, $3F, $14; Boo Buddy
	.byte $3F, $36, $18; Dry Bones
	.byte $8A, $48, $11; Thwomp (normal)
	.byte $2F, $4F, $14; Boo Buddy
	.byte $3F, $5C, $18; Dry Bones
	.byte $3F, $55, $18; Dry Bones
	.byte $8A, $6B, $11; Thwomp (normal)
	.byte $3F, $68, $18; Dry Bones
	.byte $3F, $72, $18; Dry Bones
	.byte $3F, $74, $18; Dry Bones
	.byte $3F, $7D, $18; Dry Bones
	.byte $4C, $AD, $17; Flying Boom Boom
	.byte $FF
; Level_1_W3
; Object Set 6
Level_1_W3_generators:
Level_1_W3_header:
	.byte $27; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_000; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $06; Start action | Graphic set
	.byte $00 | $02; Time | Music
	.byte $00 | $02, $00, $0D; Water - lasts whole level
	.byte $60 | $0B, $02, $59, $07; Orange Block Platform
	.byte $60 | $1A, $00, $50, $7F; Orange Block Platform
	.byte $60 | $0B, $0A, $4F; Gray platform
	.byte $00 | $06, $08, $D4; Background Aquatic Plants
	.byte $00 | $07, $0A, $D3; Background Aquatic Plants
	.byte $00 | $17, $05, $D2; Background Aquatic Plants
	.byte $00 | $17, $03, $E2; Vertically Oriented Donut Blocks
	.byte $20 | $17, $08, $00; '?' with Flower
	.byte $60 | $0B, $1A, $4F; Gray platform
	.byte $00 | $08, $11, $E2; Vertically Oriented Donut Blocks
	.byte $00 | $07, $1A, $D3; Background Aquatic Plants
	.byte $00 | $08, $1C, $D2; Background Aquatic Plants
	.byte $20 | $09, $14, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $09, $24, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $16, $2C, $E3; Vertically Oriented Donut Blocks
	.byte $00 | $17, $2E, $D2; Background Aquatic Plants
	.byte $20 | $00, $33, $DC; Upward Pipe (CAN'T go up)
	.byte $20 | $17, $33, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $00, $35, $4B; Wooden blocks
	.byte $20 | $01, $35, $4B; Wooden blocks
	.byte $20 | $02, $35, $4B; Wooden blocks
	.byte $20 | $03, $35, $4B; Wooden blocks
	.byte $20 | $04, $35, $4B; Wooden blocks
	.byte $20 | $05, $35, $4B; Wooden blocks
	.byte $20 | $06, $35, $4B; Wooden blocks
	.byte $20 | $07, $35, $4B; Wooden blocks
	.byte $20 | $08, $35, $4B; Wooden blocks
	.byte $20 | $09, $35, $4B; Wooden blocks
	.byte $20 | $0A, $35, $4B; Wooden blocks
	.byte $20 | $0B, $35, $4B; Wooden blocks
	.byte $20 | $0C, $35, $4B; Wooden blocks
	.byte $20 | $0D, $35, $4B; Wooden blocks
	.byte $20 | $0E, $35, $4B; Wooden blocks
	.byte $20 | $0F, $35, $4B; Wooden blocks
	.byte $20 | $10, $35, $4B; Wooden blocks
	.byte $20 | $11, $35, $4B; Wooden blocks
	.byte $20 | $12, $35, $43; Wooden blocks
	.byte $20 | $13, $35, $43; Wooden blocks
	.byte $20 | $12, $3D, $43; Wooden blocks
	.byte $20 | $13, $3D, $43; Wooden blocks
	.byte $20 | $12, $39, $83; Coins
	.byte $20 | $13, $39, $83; Coins
	.byte $20 | $00, $43, $44; Wooden blocks
	.byte $20 | $01, $43, $44; Wooden blocks
	.byte $20 | $02, $43, $44; Wooden blocks
	.byte $20 | $03, $43, $44; Wooden blocks
	.byte $20 | $04, $43, $44; Wooden blocks
	.byte $20 | $05, $43, $44; Wooden blocks
	.byte $20 | $06, $43, $44; Wooden blocks
	.byte $20 | $00, $4B, $47; Wooden blocks
	.byte $20 | $01, $4B, $47; Wooden blocks
	.byte $20 | $02, $4B, $47; Wooden blocks
	.byte $20 | $03, $4B, $47; Wooden blocks
	.byte $20 | $04, $4B, $47; Wooden blocks
	.byte $20 | $05, $4B, $47; Wooden blocks
	.byte $20 | $06, $4B, $47; Wooden blocks
	.byte $20 | $07, $43, $4F; Wooden blocks
	.byte $20 | $08, $43, $4F; Wooden blocks
	.byte $20 | $09, $43, $4F; Wooden blocks
	.byte $20 | $0A, $43, $4F; Wooden blocks
	.byte $20 | $0B, $43, $4F; Wooden blocks
	.byte $20 | $00, $41, $DC; Upward Pipe (CAN'T go up)
	.byte $20 | $00, $4E, $DC; Upward Pipe (CAN'T go up)
	.byte $20 | $16, $41, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $03, $49, $00; '?' with Flower
	.byte $20 | $12, $4D, $80; Coins
	.byte $20 | $14, $4B, $80; Coins
	.byte $20 | $17, $4A, $80; Coins
	.byte $20 | $14, $4E, $00; '?' with Flower
	.byte $20 | $14, $4F, $20; '?' blocks with single coins
	.byte $00 | $16, $45, $D3; Background Aquatic Plants
	.byte $00 | $15, $47, $D4; Background Aquatic Plants
	.byte $20 | $12, $50, $80; Coins
	.byte $20 | $14, $52, $80; Coins
	.byte $20 | $17, $53, $80; Coins
	.byte $60 | $0C, $58, $4B; Gray platform
	.byte $00 | $08, $5A, $D3; Background Aquatic Plants
	.byte $00 | $06, $5E, $D5; Background Aquatic Plants
	.byte $00 | $07, $60, $D4; Background Aquatic Plants
	.byte $00 | $03, $6F, $D2; Background Aquatic Plants
	.byte $60 | $04, $62, $51, $05; Orange Block Platform
	.byte $60 | $06, $6E, $52, $05; Orange Block Platform
	.byte $60 | $0C, $66, $53, $16; Orange Block Platform
	.byte $00 | $06, $64, $E2; Vertically Oriented Donut Blocks
	.byte $00 | $08, $69, $E3; Vertically Oriented Donut Blocks
	.byte $20 | $12, $66, $61; Note Blocks - movable two directions
	.byte $20 | $16, $66, $61; Note Blocks - movable two directions
	.byte $20 | $12, $6B, $60; Note Blocks - movable two directions
	.byte $20 | $14, $69, $60; Note Blocks - movable two directions
	.byte $20 | $14, $6D, $60; Note Blocks - movable two directions
	.byte $20 | $17, $6B, $60; Note Blocks - movable two directions
	.byte $60 | $10, $6D, $51, $01; Orange Block Platform
	.byte $60 | $10, $72, $51, $01; Orange Block Platform
	.byte $60 | $18, $77, $41; Gray platform
	.byte $00 | $03, $71, $D2; Background Aquatic Plants
	.byte $20 | $13, $78, $84; Coins
	.byte $20 | $14, $78, $84; Coins
	.byte $20 | $15, $78, $84; Coins
	.byte $20 | $12, $79, $82; Coins
	.byte $20 | $16, $79, $82; Coins
	.byte $20 | $12, $7D, $A7; Downward Pipe (CAN'T go down)
	.byte $20 | $00, $7C, $C4; Upward Pipe (CAN go up)
	.byte $60 | $0C, $7F, $5E, $01; Orange Block Platform
	.byte $20 | $00, $7E, $41; Wooden blocks
	.byte $20 | $01, $7E, $41; Wooden blocks
	.byte $20 | $02, $7E, $41; Wooden blocks
	.byte $20 | $03, $7E, $41; Wooden blocks
	.byte $20 | $04, $7E, $41; Wooden blocks
	.byte $20 | $05, $7E, $41; Wooden blocks
	.byte $20 | $06, $7E, $41; Wooden blocks
	.byte $20 | $14, $7A, $0B; Brick with 1-up
	.byte $20 | $12, $70, $60; Note Blocks - movable two directions
	.byte $20 | $12, $75, $60; Note Blocks - movable two directions
	.byte $20 | $14, $73, $60; Note Blocks - movable two directions
	.byte $20 | $14, $77, $60; Note Blocks - movable two directions
	.byte $20 | $17, $75, $60; Note Blocks - movable two directions
	.byte $60 | $1A, $7A, $31; Water - 2 blocks high
	; Pointer on screen $07
	.byte $E0 | $07, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_1_W3_objects:
	.byte $65, $14, $09; Upward Current
	.byte $62, $1D, $06; Bloober
	.byte $65, $24, $09; Upward Current
	.byte $62, $30, $11; Bloober
	.byte $66, $33, $0C; Downward Current
	.byte $67, $3A, $18; Lava Lotus
	.byte $67, $4E, $18; Lava Lotus
	.byte $66, $4E, $0C; Downward Current
	.byte $61, $67, $0A; Bloober (with babies)
	.byte $67, $70, $18; Lava Lotus
	.byte $62, $7B, $05; Bloober
	.byte $65, $7D, $12; Upward Current
	.byte $FF
; Hammer_Bros_4_W3
; Object Set 1
Hammer_Bros_4_W3_generators:
Hammer_Bros_4_W3_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $80 | $06; Time | Music
	.byte $00 | $12, $03, $E2; Background Clouds
	.byte $20 | $12, $07, $16; Bricks
	.byte $00 | $13, $0D, $E2; Background Clouds
	.byte $00 | $16, $01, $00; Background Hills A
	.byte $20 | $16, $07, $16; Bricks
	.byte $00 | $19, $06, $99; Background Bushes
	.byte $00 | $1A, $00, $C0, $0F; Flat Ground
	.byte $20 | $16, $0A, $07; Brick with Leaf
	.byte $FF
Hammer_Bros_4_W3_objects:
	.byte $81, $0C, $14; Hammer Brother
	.byte $81, $09, $18; Hammer Brother
	.byte $BA, $0D, $14; Exit on get treasure chest
	.byte $FF
; Pipe_1_End_2_W3
; Object Set 14
Pipe_1_End_2_W3_generators:
Pipe_1_End_2_W3_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_0F0; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_D8 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $19, $00, $51, $0F; Hilly Fill
	.byte $60 | $0F, $00, $E9; Hilly Wall - Right Side
	.byte $80 | $19, $01, $80, $04; Flat Land - Hilly
	.byte $80 | $16, $06, $82, $02; Flat Land - Hilly
	.byte $00 | $16, $06, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $17, $06, $E1; Hilly Wall - Left Side
	.byte $80 | $15, $09, $83, $02; Flat Land - Hilly
	.byte $00 | $15, $09, $01; Upper Left Hill Corner - Hilly
	.byte $80 | $13, $0C, $85, $02; Flat Land - Hilly
	.byte $00 | $13, $0C, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $14, $0C, $E0; Hilly Wall - Left Side
	.byte $80 | $13, $0F, $57, $00; Hilly Fill
	.byte $00 | $0F, $0F, $E3; Hilly Wall - Left Side
	.byte $80 | $0F, $03, $B3, $01; Ceiling - Hilly
	.byte $00 | $0F, $03, $E2; Hilly Wall - Left Side
	.byte $00 | $12, $03, $07; Lower Left Corner - Hilly
	.byte $60 | $11, $04, $E0; Hilly Wall - Right Side
	.byte $00 | $12, $04, $0A; Lower Right Hill Corner
	.byte $80 | $0F, $05, $B1, $01; Ceiling - Hilly
	.byte $00 | $10, $06, $0A; Lower Right Hill Corner
	.byte $80 | $0F, $07, $B0, $05; Ceiling - Hilly
	.byte $00 | $0F, $0C, $0A; Lower Right Hill Corner
	.byte $20 | $0F, $01, $C6; Upward Pipe (CAN go up)
	.byte $20 | $0F, $0D, $C1; Upward Pipe (CAN go up)
	.byte $FF
Pipe_1_End_2_W3_objects:
	.byte $25, $02, $12; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_5_W3
; Object Set 6
Level_5_W3_generators:
Level_5_W3_header:
	.byte $28; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_070; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $06; Start action | Graphic set
	.byte $00 | $02; Time | Music
	.byte $00 | $0A, $00, $0D; Water - lasts whole level
	.byte $60 | $19, $00, $51, $19; Orange Block Platform
	.byte $60 | $0B, $00, $45; Gray platform
	.byte $40 | $09, $00, $25; Leftward Pipe (CAN'T go in)
	.byte $60 | $0F, $09, $51, $03; Orange Block Platform
	.byte $00 | $15, $08, $E3; Vertically Oriented Donut Blocks
	.byte $20 | $16, $0A, $82; Coins
	.byte $00 | $0D, $0C, $E1; Vertically Oriented Donut Blocks
	.byte $00 | $15, $0E, $E3; Vertically Oriented Donut Blocks
	.byte $60 | $0E, $0F, $80; Jelectros
	.byte $20 | $05, $16, $4F; Wooden blocks
	.byte $20 | $06, $16, $4F; Wooden blocks
	.byte $20 | $07, $16, $4F; Wooden blocks
	.byte $20 | $08, $16, $4F; Wooden blocks
	.byte $20 | $09, $16, $4F; Wooden blocks
	.byte $20 | $0A, $16, $4F; Wooden blocks
	.byte $20 | $0B, $16, $4F; Wooden blocks
	.byte $20 | $05, $26, $42; Wooden blocks
	.byte $20 | $06, $26, $42; Wooden blocks
	.byte $20 | $07, $26, $42; Wooden blocks
	.byte $20 | $08, $26, $42; Wooden blocks
	.byte $20 | $09, $26, $42; Wooden blocks
	.byte $20 | $0A, $26, $42; Wooden blocks
	.byte $20 | $0B, $26, $42; Wooden blocks
	.byte $60 | $19, $1E, $51, $17; Orange Block Platform
	.byte $60 | $13, $11, $42; Gray platform
	.byte $20 | $0F, $17, $40; Wooden blocks
	.byte $20 | $10, $17, $40; Wooden blocks
	.byte $20 | $11, $17, $40; Wooden blocks
	.byte $20 | $12, $17, $40; Wooden blocks
	.byte $20 | $12, $18, $00; '?' with Flower
	.byte $20 | $12, $19, $21; '?' blocks with single coins
	.byte $00 | $15, $17, $D3; Background Aquatic Plants
	.byte $00 | $16, $18, $D2; Background Aquatic Plants
	.byte $20 | $13, $1B, $32; Bricks with single coins
	.byte $60 | $0E, $1D, $80; Jelectros
	.byte $60 | $0D, $17, $80; Jelectros
	.byte $20 | $17, $1E, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $03, $1F, $42; Wooden blocks
	.byte $60 | $0F, $2A, $51, $05; Orange Block Platform
	.byte $00 | $17, $21, $D1; Background Aquatic Plants
	.byte $00 | $16, $22, $D2; Background Aquatic Plants
	.byte $60 | $14, $22, $80; Jelectros
	.byte $60 | $15, $24, $41; Gray platform
	.byte $60 | $0C, $26, $80; Jelectros
	.byte $20 | $17, $28, $82; Coins
	.byte $20 | $17, $2C, $82; Coins
	.byte $00 | $0D, $2E, $E1; Vertically Oriented Donut Blocks
	.byte $20 | $04, $20, $40; Wooden blocks
	.byte $20 | $02, $20, $0A; Multi-Coin Brick
	.byte $60 | $09, $34, $52, $05; Orange Block Platform
	.byte $60 | $1A, $38, $50, $13; Orange Block Platform
	.byte $60 | $15, $39, $51, $03; Orange Block Platform
	.byte $60 | $15, $3E, $51, $08; Orange Block Platform
	.byte $60 | $17, $31, $42; Gray platform
	.byte $00 | $14, $32, $E2; Vertically Oriented Donut Blocks
	.byte $60 | $12, $34, $80; Jelectros
	.byte $20 | $0C, $36, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $14, $36, $81; Coins
	.byte $20 | $17, $36, $81; Coins
	.byte $00 | $12, $39, $E2; Vertically Oriented Donut Blocks
	.byte $00 | $13, $3A, $E1; Vertically Oriented Donut Blocks
	.byte $00 | $14, $3B, $E0; Vertically Oriented Donut Blocks
	.byte $60 | $0C, $3D, $80; Jelectros
	.byte $60 | $11, $3F, $80; Jelectros
	.byte $60 | $0D, $4E, $51, $02; Orange Block Platform
	.byte $20 | $18, $40, $86; Coins
	.byte $60 | $0E, $44, $80; Jelectros
	.byte $20 | $18, $48, $B1; Downward Pipe (CAN go down, ignores pointers)
	.byte $00 | $0B, $4E, $E1; Vertically Oriented Donut Blocks
	.byte $20 | $05, $54, $46; Wooden blocks
	.byte $20 | $06, $54, $46; Wooden blocks
	.byte $20 | $07, $54, $46; Wooden blocks
	.byte $20 | $08, $54, $46; Wooden blocks
	.byte $20 | $09, $54, $46; Wooden blocks
	.byte $20 | $0A, $54, $46; Wooden blocks
	.byte $20 | $0B, $54, $46; Wooden blocks
	.byte $60 | $19, $54, $51, $07; Orange Block Platform
	.byte $60 | $14, $51, $80; Jelectros
	.byte $20 | $12, $52, $22; '?' blocks with single coins
	.byte $20 | $12, $53, $00; '?' with Flower
	.byte $60 | $0D, $54, $80; Jelectros
	.byte $60 | $13, $56, $41; Gray platform
	.byte $60 | $10, $59, $41; Gray platform
	.byte $20 | $0C, $5E, $D6; Upward Pipe (CAN'T go up)
	.byte $20 | $15, $5F, $0F; Invisible 1-up
	.byte $20 | $05, $5D, $42; Wooden blocks
	.byte $20 | $06, $5D, $42; Wooden blocks
	.byte $20 | $07, $5D, $42; Wooden blocks
	.byte $20 | $08, $5D, $42; Wooden blocks
	.byte $20 | $09, $5D, $42; Wooden blocks
	.byte $20 | $0A, $5D, $42; Wooden blocks
	.byte $20 | $0B, $5D, $42; Wooden blocks
	.byte $20 | $05, $60, $4F; Wooden blocks
	.byte $20 | $06, $60, $4F; Wooden blocks
	.byte $20 | $07, $60, $4F; Wooden blocks
	.byte $20 | $08, $60, $4F; Wooden blocks
	.byte $20 | $09, $60, $4F; Wooden blocks
	.byte $20 | $0A, $60, $4F; Wooden blocks
	.byte $20 | $0B, $60, $4F; Wooden blocks
	.byte $60 | $19, $69, $51, $16; Orange Block Platform
	.byte $60 | $0E, $62, $80; Jelectros
	.byte $20 | $10, $63, $82; Coins
	.byte $60 | $16, $63, $80; Jelectros
	.byte $20 | $18, $64, $A2; Downward Pipe (CAN'T go down)
	.byte $60 | $13, $67, $80; Jelectros
	.byte $60 | $12, $6A, $41; Gray platform
	.byte $20 | $13, $6E, $82; Coins
	.byte $60 | $16, $6E, $42; Gray platform
	.byte $60 | $0D, $65, $80; Jelectros
	.byte $60 | $0E, $69, $80; Jelectros
	.byte $60 | $10, $67, $80; Jelectros
	.byte $20 | $03, $62, $42; Wooden blocks
	.byte $20 | $04, $63, $40; Wooden blocks
	.byte $20 | $02, $63, $0A; Multi-Coin Brick
	.byte $60 | $11, $7C, $43; Gray platform
	.byte $60 | $11, $72, $51, $03; Orange Block Platform
	.byte $60 | $11, $7C, $59, $03; Orange Block Platform
	.byte $00 | $0D, $73, $E3; Vertically Oriented Donut Blocks
	.byte $00 | $16, $77, $D2; Background Aquatic Plants
	.byte $00 | $15, $79, $D3; Background Aquatic Plants
	.byte $00 | $17, $7A, $D1; Background Aquatic Plants
	.byte $60 | $0C, $72, $80; Jelectros
	.byte $60 | $0F, $70, $80; Jelectros
	.byte $20 | $00, $7D, $42; Wooden blocks
	.byte $20 | $01, $7D, $42; Wooden blocks
	.byte $20 | $02, $7D, $42; Wooden blocks
	.byte $20 | $03, $7D, $42; Wooden blocks
	.byte $20 | $04, $7D, $42; Wooden blocks
	.byte $20 | $05, $7D, $42; Wooden blocks
	.byte $20 | $06, $7D, $42; Wooden blocks
	.byte $20 | $07, $7D, $42; Wooden blocks
	.byte $20 | $08, $7D, $42; Wooden blocks
	.byte $20 | $09, $7D, $42; Wooden blocks
	.byte $20 | $0A, $7D, $42; Wooden blocks
	.byte $20 | $0B, $7D, $42; Wooden blocks
	.byte $20 | $0C, $7D, $42; Wooden blocks
	.byte $20 | $0D, $7E, $41; Wooden blocks
	.byte $20 | $0E, $7E, $41; Wooden blocks
	.byte $20 | $0F, $7E, $E1; Rightward Pipe (CAN go in)
	; Pointer on screen $07
	.byte $E0 | $07, $50 | $03, 16; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $04
	.byte $E0 | $04, $00 | $02, 20; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_5_W3_objects:
	.byte $77, $0D, $12; Cheep-Cheep
	.byte $63, $16, $15; Big Bertha (underwater)
	.byte $65, $1E, $17; Upward Current
	.byte $62, $24, $11; Bloober
	.byte $77, $2F, $14; Cheep-Cheep
	.byte $77, $31, $0C; Cheep-Cheep
	.byte $66, $36, $0D; Downward Current
	.byte $65, $48, $18; Upward Current
	.byte $77, $49, $0D; Cheep-Cheep
	.byte $77, $5D, $0D; Cheep-Cheep
	.byte $66, $5E, $12; Downward Current
	.byte $61, $6C, $10; Bloober (with babies)
	.byte $63, $75, $15; Big Bertha (underwater)
	.byte $77, $79, $0F; Cheep-Cheep
	.byte $FF
; Pipe_3_End_1_W3
; Object Set 14
Pipe_3_End_1_W3_generators:
Pipe_3_End_1_W3_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
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
Pipe_3_End_1_W3_objects:
	.byte $25, $02, $14; Changes exit location on map (works on warp pipe levels)
	.byte $FF