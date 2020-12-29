; Bank 3

; Level_7_W5
; Object Set 13
Level_7_W5_generators:
Level_7_W5_header:
	.byte $40; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0D; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $0A, $02, $02; Cloud Background A
	.byte $00 | $0C, $0E, $02; Cloud Background A
	.byte $00 | $0F, $03, $02; Cloud Background A
	.byte $00 | $12, $04, $02; Cloud Background A
	.byte $00 | $12, $0C, $02; Cloud Background A
	.byte $00 | $0E, $7A, $02; Cloud Background A
	.byte $00 | $11, $7D, $02; Cloud Background A
	.byte $00 | $14, $78, $02; Cloud Background A
	.byte $60 | $0F, $00, $46, $05; White Background
	.byte $60 | $16, $00, $42, $0F; White Background
	.byte $60 | $19, $00, $40, $2B; White Background
	.byte $60 | $19, $00, $21, $2B; Clouds B
	.byte $00 | $0A, $1C, $02; Cloud Background A
	.byte $00 | $0C, $1E, $02; Cloud Background A
	.byte $00 | $11, $19, $02; Cloud Background A
	.byte $00 | $11, $1F, $02; Cloud Background A
	.byte $00 | $12, $10, $02; Cloud Background A
	.byte $60 | $13, $12, $40, $01; White Background
	.byte $60 | $13, $1F, $45, $02; White Background
	.byte $60 | $17, $18, $42, $06; White Background
	.byte $20 | $15, $19, $03; '?' with continuous star
	.byte $20 | $15, $1B, $20; '?' blocks with single coins
	.byte $20 | $15, $1D, $20; '?' blocks with single coins
	.byte $20 | $17, $10, $10; Bricks
	.byte $20 | $18, $10, $10; Bricks
	.byte $20 | $19, $10, $10; Bricks
	.byte $20 | $1A, $10, $10; Bricks
	.byte $20 | $16, $14, $10; Bricks
	.byte $20 | $17, $14, $10; Bricks
	.byte $20 | $18, $14, $10; Bricks
	.byte $20 | $19, $14, $10; Bricks
	.byte $20 | $1A, $14, $10; Bricks
	.byte $20 | $19, $18, $10; Bricks
	.byte $20 | $19, $1A, $10; Bricks
	.byte $20 | $19, $1C, $10; Bricks
	.byte $20 | $19, $1E, $10; Bricks
	.byte $20 | $1A, $18, $16; Bricks
	.byte $00 | $0C, $28, $02; Cloud Background A
	.byte $00 | $0E, $28, $02; Cloud Background A
	.byte $00 | $11, $29, $02; Cloud Background A
	.byte $60 | $0F, $26, $41, $03; White Background
	.byte $60 | $16, $22, $42, $09; White Background
	.byte $60 | $11, $31, $49, $0F; White Background
	.byte $20 | $15, $25, $03; '?' with continuous star
	.byte $20 | $15, $27, $20; '?' blocks with single coins
	.byte $20 | $15, $29, $20; '?' blocks with single coins
	.byte $20 | $1A, $22, $10; Bricks
	.byte $20 | $14, $2E, $14; Bricks
	.byte $20 | $15, $2E, $14; Bricks
	.byte $20 | $16, $2C, $16; Bricks
	.byte $20 | $17, $2C, $16; Bricks
	.byte $20 | $18, $2C, $16; Bricks
	.byte $20 | $19, $2C, $16; Bricks
	.byte $20 | $1A, $2C, $16; Bricks
	.byte $20 | $18, $22, $10; Bricks
	.byte $20 | $19, $22, $10; Bricks
	.byte $40 | $17, $22, $04; Wooden Block with Flower
	.byte $00 | $0C, $32, $02; Cloud Background A
	.byte $60 | $0F, $3A, $41, $0B; White Background
	.byte $20 | $14, $33, $42; Wooden blocks
	.byte $20 | $14, $39, $43; Wooden blocks
	.byte $20 | $17, $34, $03; '?' with continuous star
	.byte $20 | $17, $33, $0B; Brick with 1-up
	.byte $20 | $17, $3A, $21; '?' blocks with single coins
	.byte $20 | $17, $3A, $03; '?' with continuous star
	.byte $20 | $1A, $34, $46; Wooden blocks
	.byte $20 | $1A, $3C, $40; Wooden blocks
	.byte $20 | $13, $3F, $10; Bricks
	.byte $20 | $15, $3D, $17; Bricks
	.byte $20 | $16, $3D, $17; Bricks
	.byte $20 | $17, $3D, $17; Bricks
	.byte $20 | $18, $3D, $17; Bricks
	.byte $20 | $19, $3D, $17; Bricks
	.byte $00 | $0E, $42, $02; Cloud Background A
	.byte $00 | $10, $4A, $02; Cloud Background A
	.byte $00 | $0A, $52, $02; Cloud Background A
	.byte $00 | $0D, $51, $02; Cloud Background A
	.byte $00 | $11, $51, $02; Cloud Background A
	.byte $00 | $11, $5B, $02; Cloud Background A
	.byte $60 | $11, $41, $43, $03; White Background
	.byte $60 | $15, $45, $45, $0F; White Background
	.byte $20 | $13, $43, $10; Bricks
	.byte $20 | $14, $3D, $17; Bricks
	.byte $20 | $1A, $3D, $1C; Bricks
	.byte $20 | $13, $50, $09; Brick with Continuous Star
	.byte $20 | $17, $45, $09; Brick with Continuous Star
	.byte $00 | $0B, $63, $02; Cloud Background A
	.byte $00 | $0F, $63, $02; Cloud Background A
	.byte $00 | $13, $65, $02; Cloud Background A
	.byte $60 | $16, $55, $44, $15; White Background
	.byte $20 | $14, $55, $10; Bricks
	.byte $20 | $1A, $5A, $1F; Bricks
	.byte $40 | $18, $60, $31; Bullet Bill Machine
	.byte $60 | $19, $6B, $21, $24; Clouds B
	.byte $40 | $17, $66, $30; Bullet Bill Machine
	.byte $20 | $18, $62, $11; Bricks
	.byte $20 | $18, $65, $11; Bricks
	.byte $20 | $18, $68, $11; Bricks
	.byte $20 | $19, $62, $18; Bricks
	.byte $20 | $1A, $6A, $10; Bricks
	.byte $20 | $18, $36, $91; Downward Pipe (CAN go down)
	.byte $20 | $17, $50, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $7D, $E2; Rightward Pipe (CAN go in)
	.byte $20 | $1A, $4C, $1B; Bricks
	; Pointer on screen $03
	.byte $E0 | $03, $10 | $02, 32; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $07
	.byte $E0 | $07, $70 | $03, 37; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_7_W5_objects:
	.byte $6C, $0B, $18; Green Koopa Troopa
	.byte $6B, $22, $16; Pile Driver Micro-Goomba
	.byte $6B, $2E, $13; Pile Driver Micro-Goomba
	.byte $6B, $30, $13; Pile Driver Micro-Goomba
	.byte $6B, $32, $13; Pile Driver Micro-Goomba
	.byte $A4, $36, $18; Green Venus Fire Trap (upward)
	.byte $6B, $3D, $13; Pile Driver Micro-Goomba
	.byte $6B, $41, $13; Pile Driver Micro-Goomba
	.byte $83, $4F, $12; Lakitu
	.byte $6B, $55, $13; Pile Driver Micro-Goomba
	.byte $BC, $60, $18; Bullet Bills
	.byte $6B, $64, $18; Pile Driver Micro-Goomba
	.byte $BC, $66, $17; Bullet Bills
	.byte $6B, $6A, $18; Pile Driver Micro-Goomba
	.byte $41, $88, $15; Goal Card
	.byte $FF
; Level_8_W5
; Object Set 13
Level_8_W5_generators:
Level_8_W5_header:
	.byte $3E; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_13; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0D; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $15, $23, $02; Cloud Background A
	.byte $00 | $13, $21, $02; Cloud Background A
	.byte $00 | $12, $24, $02; Cloud Background A
	.byte $00 | $0E, $22, $02; Cloud Background A
	.byte $00 | $15, $1B, $02; Cloud Background A
	.byte $00 | $14, $18, $02; Cloud Background A
	.byte $00 | $14, $16, $02; Cloud Background A
	.byte $00 | $14, $10, $02; Cloud Background A
	.byte $00 | $13, $1D, $02; Cloud Background A
	.byte $00 | $13, $15, $02; Cloud Background A
	.byte $00 | $0A, $10, $02; Cloud Background A
	.byte $00 | $14, $0C, $02; Cloud Background A
	.byte $00 | $12, $0C, $02; Cloud Background A
	.byte $00 | $0F, $0D, $02; Cloud Background A
	.byte $00 | $0E, $0E, $02; Cloud Background A
	.byte $00 | $0C, $0E, $02; Cloud Background A
	.byte $00 | $0C, $0C, $02; Cloud Background A
	.byte $00 | $0A, $0A, $02; Cloud Background A
	.byte $00 | $14, $5B, $02; Cloud Background A
	.byte $00 | $14, $59, $02; Cloud Background A
	.byte $00 | $14, $53, $02; Cloud Background A
	.byte $00 | $12, $5D, $02; Cloud Background A
	.byte $00 | $11, $54, $02; Cloud Background A
	.byte $00 | $11, $50, $02; Cloud Background A
	.byte $00 | $0E, $5D, $02; Cloud Background A
	.byte $00 | $0E, $5B, $02; Cloud Background A
	.byte $00 | $15, $4C, $02; Cloud Background A
	.byte $00 | $15, $40, $02; Cloud Background A
	.byte $00 | $14, $45, $02; Cloud Background A
	.byte $00 | $13, $4A, $02; Cloud Background A
	.byte $00 | $10, $41, $02; Cloud Background A
	.byte $00 | $0E, $4D, $02; Cloud Background A
	.byte $00 | $15, $3A, $02; Cloud Background A
	.byte $00 | $14, $33, $02; Cloud Background A
	.byte $00 | $11, $3C, $02; Cloud Background A
	.byte $00 | $11, $38, $02; Cloud Background A
	.byte $00 | $11, $32, $02; Cloud Background A
	.byte $00 | $0E, $31, $02; Cloud Background A
	.byte $00 | $0D, $34, $02; Cloud Background A
	.byte $00 | $14, $79, $02; Cloud Background A
	.byte $00 | $14, $71, $02; Cloud Background A
	.byte $00 | $11, $78, $02; Cloud Background A
	.byte $00 | $11, $76, $02; Cloud Background A
	.byte $00 | $11, $70, $02; Cloud Background A
	.byte $00 | $0E, $77, $02; Cloud Background A
	.byte $00 | $0C, $79, $02; Cloud Background A
	.byte $00 | $0F, $6E, $02; Cloud Background A
	.byte $00 | $18, $00, $C9; World 5-style Cloud Platform - Blue Background
	.byte $00 | $15, $0F, $D6; World 5-style Cloud Platform - White Background
	.byte $00 | $19, $0F, $D6; World 5-style Cloud Platform - White Background
	.byte $20 | $12, $11, $23; '?' blocks with single coins
	.byte $20 | $12, $13, $01; '?' with leaf
	.byte $00 | $19, $1C, $D5; World 5-style Cloud Platform - White Background
	.byte $00 | $19, $26, $D3; World 5-style Cloud Platform - White Background
	.byte $00 | $18, $2E, $C3; World 5-style Cloud Platform - Blue Background
	.byte $00 | $19, $36, $D3; World 5-style Cloud Platform - White Background
	.byte $00 | $19, $3E, $D4; World 5-style Cloud Platform - White Background
	.byte $00 | $14, $44, $D1; World 5-style Cloud Platform - White Background
	.byte $00 | $19, $48, $D5; World 5-style Cloud Platform - White Background
	.byte $00 | $15, $5A, $D1; World 5-style Cloud Platform - White Background
	.byte $00 | $19, $52, $D5; World 5-style Cloud Platform - White Background
	.byte $00 | $19, $5D, $D5; World 5-style Cloud Platform - White Background
	.byte $20 | $12, $63, $01; '?' with leaf
	.byte $00 | $14, $62, $D2; World 5-style Cloud Platform - White Background
	.byte $00 | $16, $6B, $C2; World 5-style Cloud Platform - Blue Background
	.byte $00 | $19, $66, $C4; World 5-style Cloud Platform - Blue Background
	.byte $00 | $13, $70, $DF; World 5-style Cloud Platform - White Background
	.byte $20 | $12, $7D, $E2; Rightward Pipe (CAN go in)
	; Pointer on screen $07
	.byte $E0 | $07, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_8_W5_objects:
	.byte $83, $2A, $12; Lakitu
	.byte $6D, $55, $18; Red Koopa Troopa
	.byte $6D, $60, $18; Red Koopa Troopa
	.byte $6F, $69, $14; Red Koopa Paratroopa
	.byte $6F, $75, $10; Red Koopa Paratroopa
	.byte $FF
; Level_6_W5
; Object Set 13
Level_6_W5_generators:
Level_6_W5_header:
	.byte $3E; Next Level
	.byte LEVEL1_SIZE_07 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_13; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0D; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $00, $00, $03; Sets background color to white
	.byte $60 | $19, $00, $11, $0B; Clouds A
	.byte $20 | $17, $0C, $40; Wooden blocks
	.byte $20 | $18, $0C, $40; Wooden blocks
	.byte $20 | $19, $0C, $40; Wooden blocks
	.byte $20 | $1A, $0C, $40; Wooden blocks
	.byte $00 | $18, $1A, $E2, $03; Clouds C
	.byte $00 | $19, $12, $E2, $04; Clouds C
	.byte $20 | $11, $18, $80; Coins
	.byte $20 | $11, $1A, $80; Coins
	.byte $20 | $11, $1C, $80; Coins
	.byte $00 | $19, $2A, $E2, $01; Clouds C
	.byte $20 | $12, $22, $80; Coins
	.byte $20 | $12, $24, $80; Coins
	.byte $20 | $12, $26, $80; Coins
	.byte $20 | $11, $3D, $80; Coins
	.byte $20 | $13, $3F, $80; Coins
	.byte $20 | $18, $3D, $60; Note Blocks - movable two directions
	.byte $00 | $19, $32, $E2, $01; Clouds C
	.byte $00 | $19, $3A, $E2, $01; Clouds C
	.byte $20 | $17, $32, $01; '?' with leaf
	.byte $20 | $10, $41, $80; Coins
	.byte $20 | $10, $49, $80; Coins
	.byte $20 | $11, $45, $80; Coins
	.byte $20 | $13, $43, $80; Coins
	.byte $20 | $13, $47, $80; Coins
	.byte $20 | $13, $4B, $80; Coins
	.byte $20 | $16, $4C, $16; Bricks
	.byte $20 | $16, $41, $41; Wooden blocks
	.byte $20 | $18, $45, $60; Note Blocks - movable two directions
	.byte $20 | $16, $49, $41; Wooden blocks
	.byte $20 | $16, $51, $0D; Brick with P-Switch
	.byte $20 | $12, $5E, $10; Bricks
	.byte $20 | $13, $5E, $10; Bricks
	.byte $20 | $14, $5B, $10; Bricks
	.byte $20 | $15, $5B, $10; Bricks
	.byte $20 | $16, $57, $10; Bricks
	.byte $20 | $17, $57, $10; Bricks
	.byte $20 | $1A, $51, $12; Bricks
	.byte $20 | $14, $5D, $82; Coins
	.byte $20 | $16, $5A, $82; Coins
	.byte $20 | $18, $56, $82; Coins
	.byte $20 | $13, $68, $16; Bricks
	.byte $20 | $17, $61, $13; Bricks
	.byte $20 | $16, $61, $83; Coins
	.byte $20 | $0F, $6F, $40; Wooden blocks
	.byte $20 | $10, $6F, $40; Wooden blocks
	.byte $20 | $11, $6F, $40; Wooden blocks
	.byte $20 | $12, $6F, $40; Wooden blocks
	.byte $20 | $13, $6F, $40; Wooden blocks
	.byte $20 | $14, $6F, $40; Wooden blocks
	.byte $20 | $15, $6F, $40; Wooden blocks
	.byte $20 | $16, $6F, $40; Wooden blocks
	.byte $20 | $17, $6F, $40; Wooden blocks
	.byte $20 | $18, $67, $48; Wooden blocks
	.byte $20 | $19, $6F, $40; Wooden blocks
	.byte $20 | $1A, $6F, $40; Wooden blocks
	.byte $20 | $16, $6C, $E2; Rightward Pipe (CAN go in)
	; Pointer on screen $06
	.byte $E0 | $06, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_6_W5_objects:
	.byte $D3, $00, $07; Autoscrolling
	.byte $9F, $16, $16; Para-Beetle
	.byte $9F, $18, $14; Para-Beetle
	.byte $9F, $1B, $13; Para-Beetle
	.byte $9F, $1D, $16; Para-Beetle
	.byte $9F, $20, $17; Para-Beetle
	.byte $9F, $23, $18; Para-Beetle
	.byte $9F, $26, $16; Para-Beetle
	.byte $9F, $29, $18; Para-Beetle
	.byte $9F, $2C, $17; Para-Beetle
	.byte $9F, $2E, $16; Para-Beetle
	.byte $9F, $30, $15; Para-Beetle
	.byte $9F, $33, $15; Para-Beetle
	.byte $9F, $36, $16; Para-Beetle
	.byte $6F, $37, $14; Red Koopa Paratroopa
	.byte $9F, $39, $18; Para-Beetle
	.byte $9F, $3C, $18; Para-Beetle
	.byte $9F, $3F, $18; Para-Beetle
	.byte $58, $5D, $17; Fire Chomp
	.byte $FF
; Level_2_W6
; Object Set 12
Level_2_W6_generators:
Level_2_W6_header:
	.byte $1A; Next Level
	.byte LEVEL1_SIZE_09 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_12; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $20 | $16, $00, $43; Wooden blocks
	.byte $20 | $16, $07, $43; Wooden blocks
	.byte $60 | $12, $14, $13; Ice Blocks
	.byte $60 | $18, $1F, $13; Ice Blocks
	.byte $20 | $11, $15, $82; Coins
	.byte $40 | $17, $1F, $E0; White Turtle Bricks
	.byte $20 | $17, $22, $01; '?' with Leaf
	.byte $20 | $16, $28, $43; Wooden blocks
	.byte $60 | $17, $2D, $13; Ice Blocks
	.byte $20 | $10, $29, $10; Bricks
	.byte $20 | $11, $29, $10; Bricks
	.byte $20 | $12, $29, $10; Bricks
	.byte $20 | $13, $29, $10; Bricks
	.byte $20 | $14, $29, $10; Bricks
	.byte $20 | $15, $29, $10; Bricks
	.byte $20 | $13, $2E, $82; Coins
	.byte $60 | $16, $32, $13; Ice Blocks
	.byte $20 | $16, $37, $43; Wooden blocks
	.byte $20 | $16, $3E, $43; Wooden blocks
	.byte $20 | $10, $33, $82; Coins
	.byte $20 | $13, $3B, $82; Coins
	.byte $20 | $18, $35, $82; Coins
	.byte $20 | $13, $34, $10; Bricks
	.byte $20 | $14, $34, $10; Bricks
	.byte $20 | $15, $34, $10; Bricks
	.byte $20 | $13, $39, $10; Bricks
	.byte $20 | $14, $39, $10; Bricks
	.byte $20 | $15, $39, $10; Bricks
	.byte $20 | $18, $42, $43; Wooden blocks
	.byte $20 | $19, $49, $43; Wooden blocks
	.byte $20 | $0B, $4A, $40; Wooden blocks
	.byte $20 | $0C, $4A, $40; Wooden blocks
	.byte $20 | $0D, $4A, $40; Wooden blocks
	.byte $20 | $0E, $4A, $40; Wooden blocks
	.byte $20 | $0F, $4A, $40; Wooden blocks
	.byte $20 | $10, $4A, $40; Wooden blocks
	.byte $20 | $11, $4A, $40; Wooden blocks
	.byte $20 | $12, $4A, $40; Wooden blocks
	.byte $20 | $13, $4A, $40; Wooden blocks
	.byte $20 | $14, $4A, $40; Wooden blocks
	.byte $20 | $15, $4A, $40; Wooden blocks
	.byte $20 | $16, $4A, $40; Wooden blocks
	.byte $20 | $17, $4A, $40; Wooden blocks
	.byte $20 | $18, $4A, $40; Wooden blocks
	.byte $60 | $0B, $51, $13; Ice Blocks
	.byte $20 | $08, $56, $43; Wooden blocks
	.byte $20 | $08, $5C, $43; Wooden blocks
	.byte $20 | $05, $58, $0A; Multi-Coin Brick
	.byte $40 | $06, $58, $E0; White Turtle Bricks
	.byte $40 | $07, $58, $E0; White Turtle Bricks
	.byte $60 | $0D, $68, $13; Ice Blocks
	.byte $20 | $14, $6F, $43; Wooden blocks
	.byte $20 | $10, $6E, $82; Coins
	.byte $20 | $18, $78, $43; Wooden blocks
	.byte $20 | $0D, $74, $0B; Brick with 1-up
	.byte $20 | $07, $72, $40; Wooden blocks
	.byte $20 | $08, $72, $40; Wooden blocks
	.byte $20 | $09, $72, $40; Wooden blocks
	.byte $20 | $0A, $72, $40; Wooden blocks
	.byte $20 | $0B, $72, $40; Wooden blocks
	.byte $20 | $0C, $72, $40; Wooden blocks
	.byte $20 | $0D, $72, $40; Wooden blocks
	.byte $20 | $0E, $72, $40; Wooden blocks
	.byte $20 | $0F, $72, $40; Wooden blocks
	.byte $20 | $10, $72, $43; Wooden blocks
	.byte $20 | $19, $80, $43; Wooden blocks
	.byte $20 | $17, $8A, $93; Downward Pipe (CAN go down)
	; Pointer on screen $08
	.byte $E0 | $08, $40 | $02, 128; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_2_W6_objects:
	.byte $D3, $00, $02; Autoscrolling
	.byte $2C, $0F, $18; Leftward-moving cloud platform (slow)
	.byte $2C, $14, $15; Leftward-moving cloud platform (slow)
	.byte $2C, $1C, $13; Leftward-moving cloud platform (slow)
	.byte $2C, $2A, $11; Leftward-moving cloud platform (slow)
	.byte $24, $2C, $14; Leftward-moving cloud platform (fast)
	.byte $2C, $3A, $19; Leftward-moving cloud platform (slow)
	.byte $6D, $30, $16; Red Koopa Troopa
	.byte $2C, $49, $15; Leftward-moving cloud platform (slow)
	.byte $2C, $4E, $0C; Leftward-moving cloud platform (slow)
	.byte $2C, $4D, $12; Leftward-moving cloud platform (slow)
	.byte $24, $50, $10; Leftward-moving cloud platform (fast)
	.byte $2C, $53, $0D; Leftward-moving cloud platform (slow)
	.byte $6D, $5C, $07; Red Koopa Troopa
	.byte $2C, $67, $0A; Leftward-moving cloud platform (slow)
	.byte $2C, $69, $07; Leftward-moving cloud platform (slow)
	.byte $2C, $79, $11; Leftward-moving cloud platform (slow)
	.byte $2C, $78, $15; Leftward-moving cloud platform (slow)
	.byte $2C, $88, $16; Leftward-moving cloud platform (slow)
	.byte $FF
; Pipe_1_End_2_W6
; Object Set 14
Pipe_1_End_2_W6_generators:
Pipe_1_End_2_W6_header:
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
Pipe_1_End_2_W6_objects:
	.byte $25, $02, $02; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_1_W6
; Object Set 12
Level_1_W6_generators:
Level_1_W6_header:
	.byte $41; Next Level
	.byte LEVEL1_SIZE_09 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_12; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $12, $02, $C2; Background Clouds
	.byte $00 | $1A, $00, $10, $0B; Icy flat ground
	.byte $60 | $17, $08, $13; Ice Blocks
	.byte $60 | $17, $0D, $14; Ice Blocks
	.byte $00 | $1A, $0D, $10, $25; Icy flat ground
	.byte $20 | $14, $0E, $11; Bricks
	.byte $20 | $14, $10, $00; '?' with Flower
	.byte $20 | $18, $14, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $12, $18, $C2; Background Clouds
	.byte $20 | $17, $1A, $82; Coins
	.byte $00 | $05, $1C, $C2; Background Clouds
	.byte $00 | $14, $21, $C2; Background Clouds
	.byte $00 | $07, $2B, $C2; Background Clouds
	.byte $00 | $12, $2D, $C2; Background Clouds
	.byte $20 | $17, $2A, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $05, $25, $05; Door
	.byte $20 | $07, $23, $43; Wooden blocks
	.byte $20 | $16, $2F, $03; '?' with Continuous star
	.byte $20 | $16, $32, $82; Coins
	.byte $20 | $16, $3A, $A3; Downward Pipe (CAN'T go down)
	.byte $00 | $1A, $34, $10, $03; Icy flat ground
	.byte $00 | $1A, $39, $10, $34; Icy flat ground
	.byte $00 | $03, $3A, $C2; Background Clouds
	.byte $00 | $14, $3D, $C2; Background Clouds
	.byte $00 | $12, $42, $C2; Background Clouds
	.byte $00 | $07, $49, $C2; Background Clouds
	.byte $20 | $17, $4E, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $4B, $03; '?' with Continuous star
	.byte $60 | $16, $53, $13; Ice Blocks
	.byte $00 | $11, $56, $C2; Background Clouds
	.byte $60 | $16, $58, $12; Ice Blocks
	.byte $20 | $13, $58, $82; Coins
	.byte $00 | $07, $59, $C2; Background Clouds
	.byte $60 | $16, $5D, $11; Ice Blocks
	.byte $20 | $13, $5E, $82; Coins
	.byte $20 | $13, $54, $01; '?' with Leaf
	.byte $60 | $16, $62, $12; Ice Blocks
	.byte $00 | $09, $66, $C2; Background Clouds
	.byte $00 | $13, $68, $C2; Background Clouds
	.byte $20 | $18, $6C, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $1A, $70, $10, $1F; Icy flat ground
	.byte $00 | $12, $71, $C2; Background Clouds
	.byte $40 | $00, $77, $09; Level Ending
	; Pointer on screen $02
	.byte $E0 | $02, $60 | $08, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_1_W6_objects:
	.byte $46, $14, $16; Pipe Ptooie
	.byte $2A, $24, $18; Ptooie
	.byte $A2, $2A, $17; Red Piranha Plant (upward)
	.byte $A4, $3A, $16; Green Venus Fire Trap (upward)
	.byte $2A, $46, $18; Ptooie
	.byte $2A, $4A, $18; Ptooie
	.byte $2A, $5C, $18; Ptooie
	.byte $73, $63, $19; Para-Goomba
	.byte $2A, $65, $18; Ptooie
	.byte $46, $6C, $16; Pipe Ptooie
	.byte $41, $88, $15; Goal Card
	.byte $FF
; Dungeon__1_W6
; Object Set 2
Dungeon__1_W6_generators:
Dungeon__1_W6_header:
	.byte $42; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_0F0; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $00, $00, $3F, $4F; Blank Background (used to block out stuff)
	.byte $60 | $10, $00, $3A, $4F; Blank Background (used to block out stuff)
	.byte $00 | $00, $00, $ED, $06; Horizontally oriented X-blocks
	.byte $00 | $0E, $05, $E7, $01; Horizontally oriented X-blocks
	.byte $00 | $11, $00, $E7, $02; Horizontally oriented X-blocks
	.byte $00 | $18, $03, $E0, $04; Horizontally oriented X-blocks
	.byte $00 | $00, $07, $E1, $78; Horizontally oriented X-blocks
	.byte $20 | $14, $08, $83; Coins
	.byte $60 | $16, $0A, $74; Horizontal Platform Wire
	.byte $60 | $16, $0F, $AE; 45 Degree Platform Wire - Up/Right
	.byte $60 | $1A, $00, $40, $1F; Lava
	.byte $00 | $15, $03, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $02, $1F, $E3, $1B; Horizontally oriented X-blocks
	.byte $60 | $07, $1E, $7F; Horizontal Platform Wire
	.byte $20 | $0F, $12, $81; Coins
	.byte $20 | $11, $10, $81; Coins
	.byte $20 | $0B, $17, $01; '?' with leaf
	.byte $60 | $07, $2E, $7D; Horizontal Platform Wire
	.byte $00 | $0B, $20, $EF, $1D; Horizontally oriented X-blocks
	.byte $00 | $0A, $20, $CF; Floor Spikes
	.byte $00 | $0A, $30, $CD; Floor Spikes
	.byte $00 | $05, $3E, $F4, $15; Vertically oriented X-blocks
	.byte $60 | $04, $3C, $82; 1 Platform Wire
	.byte $60 | $03, $3D, $77; Horizontal Platform Wire
	.byte $60 | $07, $3C, $A0; 45 Degree Platform Wire - Up/Right
	.byte $60 | $04, $44, $8F; 1 Platform Wire
	.byte $60 | $14, $44, $86; 1 Platform Wire
	.byte $00 | $16, $46, $E4, $08; Horizontally oriented X-blocks
	.byte $00 | $12, $4F, $E8, $10; Horizontally oriented X-blocks
	.byte $00 | $02, $47, $F7, $10; Vertically oriented X-blocks
	.byte $00 | $02, $4F, $EF, $18; Horizontally oriented X-blocks
	.byte $00 | $08, $48, $02; Rotodisc block
	.byte $00 | $0D, $41, $02; Rotodisc block
	.byte $00 | $12, $48, $02; Rotodisc block
	.byte $00 | $1A, $43, $C2; Floor Spikes
	.byte $00 | $14, $4D, $00; Door
	.byte $00 | $03, $46, $04; Hot Foot Candle
	.byte $60 | $10, $60, $38, $1F; Blank Background (used to block out stuff)
	.byte $00 | $02, $68, $ED, $17; Horizontally oriented X-blocks
	.byte $00 | $10, $60, $E4, $07; Horizontally oriented X-blocks
	.byte $00 | $16, $66, $62; Dungeon windows
	.byte $00 | $10, $68, $E4, $07; Horizontally oriented X-blocks
	.byte $00 | $10, $7F, $E8, $00; Horizontally oriented X-blocks
	.byte $00 | $11, $77, $60; Dungeon windows
	.byte $00 | $16, $74, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $7A, $E0, $00; Horizontally oriented X-blocks
	; Pointer on screen $04
	.byte $E0 | $04, $60 | $08, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__1_W6_objects:
	.byte $9E, $0C, $15; Podoboo (comes out of lava)
	.byte $3A, $09, $16; Falling Circle Block platform
	.byte $9E, $10, $13; Podoboo (comes out of lava)
	.byte $9E, $15, $0F; Podoboo (comes out of lava)
	.byte $9E, $1A, $09; Podoboo (comes out of lava)
	.byte $9E, $1D, $06; Podoboo (comes out of lava)
	.byte $30, $46, $02; Hot Foot
	.byte $5B, $48, $08; Single Rotodisc (rotates counterclockwise)
	.byte $5B, $48, $12; Single Rotodisc (rotates counterclockwise)
	.byte $5A, $41, $0D; Single Rotodisc (rotates clockwise)
	.byte $4C, $7C, $17; Flying Boom Boom
	.byte $FF
; Pipe_1_End_1_W6
; Object Set 14
Pipe_1_End_1_W6_generators:
Pipe_1_End_1_W6_header:
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
Pipe_1_End_1_W6_objects:
	.byte $25, $02, $02; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_3_W6
; Object Set 12
Level_3_W6_generators:
Level_3_W6_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_09 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $00 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $16, $00, $34; Green topped wooden platform
	.byte $00 | $18, $01, $04; Wooden Background Pole
	.byte $00 | $18, $03, $04; Wooden Background Pole
	.byte $60 | $10, $0F, $10; Ice Blocks
	.byte $60 | $11, $0F, $10; Ice Blocks
	.byte $60 | $12, $0F, $10; Ice Blocks
	.byte $60 | $13, $0F, $10; Ice Blocks
	.byte $60 | $14, $0F, $10; Ice Blocks
	.byte $60 | $15, $0F, $10; Ice Blocks
	.byte $60 | $16, $0F, $10; Ice Blocks
	.byte $20 | $16, $09, $61; Note Blocks - movable two directions
	.byte $00 | $0A, $0B, $C2; Background Clouds
	.byte $00 | $11, $07, $C2; Background Clouds
	.byte $60 | $14, $11, $12; Ice Blocks
	.byte $60 | $18, $1A, $12; Ice Blocks
	.byte $60 | $18, $1E, $10; Ice Blocks
	.byte $60 | $19, $1E, $10; Ice Blocks
	.byte $60 | $1A, $1E, $10; Ice Blocks
	.byte $20 | $15, $1F, $82; Coins
	.byte $20 | $17, $1A, $01; '?' with Leaf
	.byte $00 | $05, $14, $C2; Background Clouds
	.byte $00 | $0F, $18, $C2; Background Clouds
	.byte $60 | $18, $20, $10; Ice Blocks
	.byte $60 | $19, $20, $10; Ice Blocks
	.byte $60 | $1A, $20, $10; Ice Blocks
	.byte $60 | $18, $22, $10; Ice Blocks
	.byte $60 | $19, $22, $10; Ice Blocks
	.byte $60 | $1A, $22, $10; Ice Blocks
	.byte $60 | $18, $24, $10; Ice Blocks
	.byte $60 | $19, $24, $10; Ice Blocks
	.byte $60 | $1A, $24, $10; Ice Blocks
	.byte $60 | $18, $26, $10; Ice Blocks
	.byte $60 | $19, $26, $10; Ice Blocks
	.byte $60 | $1A, $26, $10; Ice Blocks
	.byte $60 | $18, $28, $10; Ice Blocks
	.byte $60 | $19, $28, $10; Ice Blocks
	.byte $60 | $1A, $28, $10; Ice Blocks
	.byte $60 | $18, $2A, $81; Large Ice Blocks
	.byte $20 | $13, $2C, $60; Note Blocks - movable two directions
	.byte $20 | $15, $25, $82; Coins
	.byte $00 | $05, $27, $C2; Background Clouds
	.byte $00 | $11, $27, $C2; Background Clouds
	.byte $60 | $07, $3A, $80; Large Ice Blocks
	.byte $60 | $15, $30, $10; Ice Blocks
	.byte $60 | $16, $30, $10; Ice Blocks
	.byte $60 | $17, $30, $10; Ice Blocks
	.byte $60 | $18, $30, $10; Ice Blocks
	.byte $60 | $19, $30, $15; Ice Blocks
	.byte $60 | $16, $3C, $13; Ice Blocks
	.byte $20 | $04, $3A, $B2; Downward Pipe (CAN go down, ignores pointers)
	.byte $20 | $07, $37, $40; Wooden blocks
	.byte $20 | $0B, $38, $60; Note Blocks - movable two directions
	.byte $20 | $16, $37, $0C; Brick with Vine
	.byte $00 | $06, $34, $C2; Background Clouds
	.byte $00 | $10, $38, $C2; Background Clouds
	.byte $00 | $14, $32, $C2; Background Clouds
	.byte $20 | $16, $39, $11; Bricks
	.byte $60 | $15, $45, $11; Ice Blocks
	.byte $60 | $15, $4C, $12; Ice Blocks
	.byte $60 | $19, $4F, $10; Ice Blocks
	.byte $20 | $11, $4E, $0A; Multi-Coin Brick
	.byte $00 | $07, $46, $C2; Background Clouds
	.byte $00 | $16, $44, $C2; Background Clouds
	.byte $00 | $17, $4A, $C2; Background Clouds
	.byte $60 | $19, $52, $11; Ice Blocks
	.byte $60 | $15, $59, $10; Ice Blocks
	.byte $60 | $16, $59, $10; Ice Blocks
	.byte $60 | $17, $59, $10; Ice Blocks
	.byte $60 | $18, $59, $10; Ice Blocks
	.byte $60 | $19, $5F, $11; Ice Blocks
	.byte $00 | $06, $5B, $C2; Background Clouds
	.byte $00 | $09, $55, $C2; Background Clouds
	.byte $00 | $11, $53, $C2; Background Clouds
	.byte $00 | $10, $5F, $C2; Background Clouds
	.byte $60 | $15, $60, $10; Ice Blocks
	.byte $60 | $16, $60, $10; Ice Blocks
	.byte $60 | $17, $60, $10; Ice Blocks
	.byte $60 | $18, $60, $10; Ice Blocks
	.byte $60 | $11, $67, $10; Ice Blocks
	.byte $60 | $12, $67, $10; Ice Blocks
	.byte $60 | $13, $67, $10; Ice Blocks
	.byte $60 | $14, $67, $10; Ice Blocks
	.byte $60 | $15, $67, $10; Ice Blocks
	.byte $60 | $16, $67, $10; Ice Blocks
	.byte $20 | $11, $63, $82; Coins
	.byte $20 | $15, $64, $0B; Brick with 1-up
	.byte $00 | $0F, $66, $C2; Background Clouds
	.byte $00 | $1A, $76, $7F; Snowy Platform
	.byte $00 | $1A, $86, $7F; Snowy Platform
	.byte $00 | $1A, $96, $7F; Snowy Platform
	.byte $00 | $14, $77, $C2; Background Clouds
	.byte $40 | $00, $7B, $09; Level Ending
	; Pointer on screen $03
	.byte $E0 | $03, $50 | $02, 37; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_3_W6_objects:
	.byte $27, $12, $18; Wooden platform - moves back and forth (a lot)
	.byte $6D, $13, $13; Red Koopa Troopa
	.byte $6D, $2B, $17; Red Koopa Troopa
	.byte $6D, $35, $18; Red Koopa Troopa
	.byte $27, $5A, $19; Wooden platform - moves back and forth (a lot)
	.byte $27, $6A, $18; Wooden platform - moves back and forth (a lot)
	.byte $6F, $6D, $15; Red Koopa Paratroopa
	.byte $6F, $71, $13; Red Koopa Paratroopa
	.byte $41, $88, $15; Goal Card
	.byte $FF
; Pipe_2_End_2_W6
; Object Set 14
Pipe_2_End_2_W6_generators:
Pipe_2_End_2_W6_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_D8 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $19, $00, $51, $0F; Hilly Fill
	.byte $80 | $13, $00, $55, $00; Hilly Fill
	.byte $60 | $0F, $00, $E3; Hilly Wall - Right Side
	.byte $80 | $13, $01, $85, $01; Flat Land - Hilly
	.byte $60 | $13, $03, $55; 30 Degree Hill - Down/Right
	.byte $00 | $0F, $0F, $E9; Hilly Wall - Left Side
	.byte $80 | $0F, $03, $50, $09; Hilly Fill
	.byte $00 | $0F, $03, $E0; Hilly Wall - Left Side
	.byte $80 | $0F, $0B, $B4, $01; Ceiling - Hilly
	.byte $60 | $0F, $0C, $E3; Hilly Wall - Right Side
	.byte $00 | $13, $0C, $0A; Lower Right Hill Corner
	.byte $60 | $10, $03, $73; 30 Degree Hill - Up/Left
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $0F, $0D, $C6; Upward Pipe (CAN go up)
	.byte $FF
Pipe_2_End_2_W6_objects:
	.byte $25, $02, $03; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Pipe_2_End_1_W6
; Object Set 14
Pipe_2_End_1_W6_generators:
Pipe_2_End_1_W6_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_0F0; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $19, $00, $51, $0F; Hilly Fill
	.byte $80 | $13, $00, $55, $00; Hilly Fill
	.byte $60 | $0F, $00, $E3; Hilly Wall - Right Side
	.byte $80 | $13, $01, $85, $01; Flat Land - Hilly
	.byte $60 | $13, $03, $55; 30 Degree Hill - Down/Right
	.byte $00 | $0F, $0F, $E9; Hilly Wall - Left Side
	.byte $80 | $0F, $03, $50, $09; Hilly Fill
	.byte $00 | $0F, $03, $E0; Hilly Wall - Left Side
	.byte $80 | $0F, $0B, $B4, $01; Ceiling - Hilly
	.byte $60 | $0F, $0C, $E3; Hilly Wall - Right Side
	.byte $00 | $13, $0C, $0A; Lower Right Hill Corner
	.byte $60 | $10, $03, $73; 30 Degree Hill - Up/Left
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $0F, $0D, $C6; Upward Pipe (CAN go up)
	.byte $FF
Pipe_2_End_1_W6_objects:
	.byte $25, $02, $03; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_6_Outside_Area_W6
; Object Set 12
Level_6_Outside_Area_W6_generators:
Level_6_Outside_Area_W6_header:
	.byte $43; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $1A, $00, $10, $3F; Icy flat ground
	.byte $60 | $00, $00, $1E; Ice Blocks
	.byte $60 | $16, $06, $80; Large Ice Blocks
	.byte $60 | $17, $08, $14; Ice Blocks
	.byte $60 | $18, $04, $84; Large Ice Blocks
	.byte $60 | $18, $0E, $10; Ice Blocks
	.byte $60 | $19, $0E, $10; Ice Blocks
	.byte $60 | $00, $0F, $88; Large Ice Blocks
	.byte $60 | $02, $0F, $88; Large Ice Blocks
	.byte $60 | $04, $0F, $88; Large Ice Blocks
	.byte $60 | $06, $0F, $88; Large Ice Blocks
	.byte $60 | $08, $0F, $88; Large Ice Blocks
	.byte $60 | $0A, $0F, $88; Large Ice Blocks
	.byte $60 | $0C, $0F, $88; Large Ice Blocks
	.byte $60 | $0E, $0F, $88; Large Ice Blocks
	.byte $60 | $10, $0F, $88; Large Ice Blocks
	.byte $60 | $12, $0F, $88; Large Ice Blocks
	.byte $60 | $14, $0D, $89; Large Ice Blocks
	.byte $60 | $16, $0D, $89; Large Ice Blocks
	.byte $60 | $18, $0F, $88; Large Ice Blocks
	.byte $00 | $11, $07, $C2; Background Clouds
	.byte $00 | $14, $02, $C2; Background Clouds
	.byte $20 | $15, $0B, $E1; Rightward Pipe (CAN go in)
	.byte $20 | $18, $23, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $11, $28, $C2; Background Clouds
	.byte $00 | $13, $22, $C2; Background Clouds
	.byte $00 | $16, $27, $C2; Background Clouds
	.byte $40 | $00, $2C, $09; Level Ending
	; Pointer on screen $00
	.byte $E0 | $00, $10 | $02, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_6_Outside_Area_W6_objects:
	.byte $29, $2B, $19; Spike
	.byte $41, $38, $15; Goal Card
	.byte $FF
; Dungeon__2_W6
; Object Set 12
Dungeon__2_W6_generators:
Dungeon__2_W6_header:
	.byte $44; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_12; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $0F, $00, $1F; Ice Blocks
	.byte $60 | $1A, $00, $1F; Ice Blocks
	.byte $60 | $18, $07, $84; Large Ice Blocks
	.byte $60 | $17, $08, $18; Ice Blocks
	.byte $60 | $13, $0B, $16; Ice Blocks
	.byte $60 | $16, $0E, $10; Ice Blocks
	.byte $60 | $0F, $10, $1F; Ice Blocks
	.byte $60 | $1A, $10, $1D; Ice Blocks
	.byte $60 | $17, $13, $17; Ice Blocks
	.byte $60 | $10, $15, $82; Large Ice Blocks
	.byte $60 | $12, $15, $82; Large Ice Blocks
	.byte $60 | $13, $1B, $13; Ice Blocks
	.byte $60 | $17, $1D, $12; Ice Blocks
	.byte $60 | $16, $17, $13; Ice Blocks
	.byte $60 | $14, $17, $81; Large Ice Blocks
	.byte $60 | $10, $1B, $10; Ice Blocks
	.byte $60 | $11, $1B, $10; Ice Blocks
	.byte $60 | $12, $1B, $10; Ice Blocks
	.byte $20 | $17, $1B, $01; '?' with Leaf
	.byte $60 | $12, $24, $10; Ice Blocks
	.byte $60 | $14, $28, $10; Ice Blocks
	.byte $60 | $15, $28, $10; Ice Blocks
	.byte $60 | $16, $28, $10; Ice Blocks
	.byte $60 | $0F, $20, $1F; Ice Blocks
	.byte $60 | $13, $22, $19; Ice Blocks
	.byte $60 | $1A, $2C, $1B; Ice Blocks
	.byte $60 | $17, $2D, $18; Ice Blocks
	.byte $60 | $10, $2F, $18; Ice Blocks
	.byte $60 | $11, $2F, $14; Ice Blocks
	.byte $60 | $12, $2F, $14; Ice Blocks
	.byte $60 | $13, $2D, $18; Ice Blocks
	.byte $60 | $14, $2F, $16; Ice Blocks
	.byte $60 | $17, $28, $13; Ice Blocks
	.byte $60 | $0F, $30, $1F; Ice Blocks
	.byte $60 | $13, $39, $82; Large Ice Blocks
	.byte $60 | $15, $39, $82; Large Ice Blocks
	.byte $60 | $17, $38, $18; Ice Blocks
	.byte $60 | $15, $31, $14; Ice Blocks
	.byte $60 | $16, $31, $14; Ice Blocks
	.byte $60 | $10, $3C, $10; Ice Blocks
	.byte $60 | $11, $3C, $10; Ice Blocks
	.byte $60 | $0F, $40, $1F; Ice Blocks
	.byte $60 | $17, $44, $1C; Ice Blocks
	.byte $60 | $10, $48, $80; Large Ice Blocks
	.byte $60 | $12, $48, $80; Large Ice Blocks
	.byte $60 | $13, $4A, $13; Ice Blocks
	.byte $60 | $10, $4A, $15; Ice Blocks
	.byte $60 | $11, $4A, $10; Ice Blocks
	.byte $60 | $12, $4A, $10; Ice Blocks
	.byte $20 | $13, $47, $01; '?' with Leaf
	.byte $60 | $0F, $50, $1F; Ice Blocks
	.byte $60 | $13, $51, $15; Ice Blocks
	.byte $60 | $13, $58, $1B; Ice Blocks
	.byte $60 | $12, $53, $10; Ice Blocks
	.byte $60 | $0F, $60, $19; Ice Blocks
	.byte $60 | $17, $60, $12; Ice Blocks
	.byte $60 | $16, $60, $10; Ice Blocks
	.byte $60 | $1A, $65, $1F; Ice Blocks
	.byte $60 | $10, $67, $12; Ice Blocks
	.byte $60 | $11, $67, $12; Ice Blocks
	.byte $60 | $12, $67, $12; Ice Blocks
	.byte $60 | $13, $67, $12; Ice Blocks
	.byte $60 | $14, $67, $12; Ice Blocks
	.byte $60 | $15, $69, $10; Ice Blocks
	.byte $60 | $16, $69, $10; Ice Blocks
	.byte $60 | $17, $64, $1D; Ice Blocks
	.byte $60 | $1A, $63, $11; Ice Blocks
	.byte $60 | $16, $60, $10; Ice Blocks
	.byte $60 | $15, $60, $10; Ice Blocks
	.byte $60 | $1A, $75, $1A; Ice Blocks
	.byte $60 | $0F, $6A, $8A; Large Ice Blocks
	.byte $60 | $11, $6A, $83; Large Ice Blocks
	.byte $60 | $13, $6A, $83; Large Ice Blocks
	.byte $60 | $15, $6A, $83; Large Ice Blocks
	.byte $60 | $16, $7A, $82; Large Ice Blocks
	.byte $60 | $18, $7A, $82; Large Ice Blocks
	.byte $60 | $11, $7F, $10; Ice Blocks
	.byte $60 | $12, $7F, $10; Ice Blocks
	.byte $60 | $13, $7F, $10; Ice Blocks
	.byte $60 | $14, $7F, $10; Ice Blocks
	.byte $60 | $15, $7F, $10; Ice Blocks
	.byte $00 | $14, $7D, $05; Door
	.byte $60 | $16, $76, $81; Large Ice Blocks
	.byte $60 | $18, $79, $10; Ice Blocks
	.byte $60 | $19, $79, $10; Ice Blocks
	; Pointer on screen $07
	.byte $E0 | $07, $60 | $08, 112; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__2_W6_objects:
	.byte $2F, $0E, $10; Boo Buddy
	.byte $8B, $15, $15; Thwomp (moves left)
	.byte $8C, $1C, $11; Thwomp (moves right)
	.byte $8B, $2F, $15; Thwomp (moves left)
	.byte $8C, $34, $11; Thwomp (moves right)
	.byte $60, $48, $17; Double Rotodisc (rotates clockwise)
	.byte $8C, $4B, $11; Thwomp (moves right)
	.byte $60, $57, $13; Double Rotodisc (rotates clockwise)
	.byte $2F, $57, $16; Boo Buddy
	.byte $8C, $61, $15; Thwomp (moves right)
	.byte $8B, $77, $18; Thwomp (moves left)
	.byte $FF
; Level_8_W6
; Object Set 14
Level_8_W6_generators:
Level_8_W6_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_11 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $00 | LEVEL3_TILESET_14; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $13; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $19, $00, $81, $09; Flat Land - Hilly
	.byte $80 | $13, $0B, $86, $03; Flat Land - Hilly
	.byte $80 | $19, $0A, $50, $00; Hilly Fill
	.byte $00 | $13, $0B, $60; 45 Degree Hill - Down/Left
	.byte $00 | $16, $0A, $60; 45 Degree Hill - Down/Left
	.byte $00 | $13, $0E, $50; 45 Degree Hill - Down/Right
	.byte $00 | $14, $0B, $E1; Hilly Wall - Left Side
	.byte $00 | $17, $0A, $E1; Hilly Wall - Left Side
	.byte $60 | $14, $0E, $E4; Hilly Wall - Right Side
	.byte $60 | $19, $0E, $F0; Underground Wall - Right Side
	.byte $40 | $19, $0F, $81, $03; Water (still)
	.byte $A0 | $10, $07, $32; Background Clouds
	.byte $A0 | $13, $02, $32; Background Clouds
	.byte $80 | $18, $00, $D2; Small Background Hills
	.byte $80 | $18, $04, $D1; Small Background Hills
	.byte $40 | $17, $08, $E1; White Turtle Bricks
	.byte $40 | $18, $07, $E2; White Turtle Bricks
	.byte $20 | $12, $0D, $01; '?' with leaf
	.byte $80 | $17, $13, $83, $04; Flat Land - Hilly
	.byte $00 | $17, $13, $60; 45 Degree Hill - Down/Left
	.byte $00 | $18, $13, $E0; Hilly Wall - Left Side
	.byte $00 | $19, $13, $F0; Underground Wall - Left Side
	.byte $00 | $17, $17, $04; Upper Right Hill Corner - Hilly
	.byte $80 | $18, $18, $82, $03; Flat Land - Hilly
	.byte $80 | $17, $1C, $83, $04; Flat Land - Hilly
	.byte $00 | $17, $1C, $01; Upper Left Hill Corner - Hilly
	.byte $A0 | $11, $11, $33; Background Clouds
	.byte $A0 | $13, $18, $32; Background Clouds
	.byte $80 | $16, $14, $D2; Small Background Hills
	.byte $80 | $16, $1D, $D2; Small Background Hills
	.byte $20 | $17, $10, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $19, $10, $41; Wooden blocks
	.byte $20 | $1A, $10, $41; Wooden blocks
	.byte $00 | $17, $20, $50; 45 Degree Hill - Down/Right
	.byte $80 | $18, $21, $82, $22; Flat Land - Hilly
	.byte $80 | $17, $24, $83, $04; Flat Land - Hilly
	.byte $00 | $17, $24, $60; 45 Degree Hill - Down/Left
	.byte $80 | $16, $29, $84, $05; Flat Land - Hilly
	.byte $00 | $16, $29, $60; 45 Degree Hill - Down/Left
	.byte $00 | $16, $2E, $50; 45 Degree Hill - Down/Right
	.byte $80 | $17, $2F, $83, $03; Flat Land - Hilly
	.byte $A0 | $06, $29, $32; Background Clouds
	.byte $A0 | $08, $22, $32; Background Clouds
	.byte $A0 | $0B, $2C, $32; Background Clouds
	.byte $A0 | $10, $20, $33; Background Clouds
	.byte $A0 | $10, $2B, $32; Background Clouds
	.byte $A0 | $13, $23, $32; Background Clouds
	.byte $80 | $15, $2A, $D1; Small Background Hills
	.byte $40 | $14, $25, $0B; Background Hills B
	.byte $80 | $16, $33, $84, $05; Flat Land - Hilly
	.byte $00 | $16, $33, $60; 45 Degree Hill - Down/Left
	.byte $80 | $15, $39, $85, $05; Flat Land - Hilly
	.byte $00 | $15, $39, $60; 45 Degree Hill - Down/Left
	.byte $80 | $14, $3F, $86, $04; Flat Land - Hilly
	.byte $00 | $14, $3F, $60; 45 Degree Hill - Down/Left
	.byte $A0 | $03, $31, $32; Background Clouds
	.byte $A0 | $0B, $37, $32; Background Clouds
	.byte $A0 | $11, $30, $33; Background Clouds
	.byte $A0 | $12, $3A, $32; Background Clouds
	.byte $80 | $15, $34, $D3; Small Background Hills
	.byte $00 | $14, $44, $54; 45 Degree Hill - Down/Right
	.byte $80 | $19, $44, $51, $04; Hilly Fill
	.byte $80 | $19, $49, $81, $14; Flat Land - Hilly
	.byte $A0 | $02, $4D, $32; Background Clouds
	.byte $A0 | $06, $48, $33; Background Clouds
	.byte $A0 | $09, $44, $32; Background Clouds
	.byte $A0 | $11, $43, $32; Background Clouds
	.byte $A0 | $12, $4D, $32; Background Clouds
	.byte $A0 | $14, $47, $32; Background Clouds
	.byte $80 | $13, $40, $D2; Small Background Hills
	.byte $40 | $16, $4B, $E2; White Turtle Bricks
	.byte $40 | $17, $4B, $E2; White Turtle Bricks
	.byte $40 | $18, $4B, $E2; White Turtle Bricks
	.byte $20 | $17, $4C, $01; '?' with leaf
	.byte $80 | $18, $5E, $52, $03; Hilly Fill
	.byte $60 | $18, $5E, $60; 30 Degree Hill - Down/Left
	.byte $20 | $0E, $5A, $0F; Invisible 1-up
	.byte $40 | $12, $57, $E0; White Turtle Bricks
	.byte $40 | $13, $57, $E0; White Turtle Bricks
	.byte $40 | $14, $57, $E0; White Turtle Bricks
	.byte $40 | $16, $57, $E0; White Turtle Bricks
	.byte $40 | $17, $57, $E0; White Turtle Bricks
	.byte $40 | $18, $57, $E0; White Turtle Bricks
	.byte $40 | $12, $5A, $E0; White Turtle Bricks
	.byte $40 | $13, $5A, $E0; White Turtle Bricks
	.byte $40 | $14, $5A, $E0; White Turtle Bricks
	.byte $40 | $16, $5A, $E0; White Turtle Bricks
	.byte $40 | $17, $5A, $E0; White Turtle Bricks
	.byte $40 | $18, $5A, $E0; White Turtle Bricks
	.byte $40 | $15, $57, $E3; White Turtle Bricks
	.byte $40 | $17, $51, $E0; White Turtle Bricks
	.byte $40 | $18, $50, $E2; White Turtle Bricks
	.byte $80 | $18, $53, $D2; Small Background Hills
	.byte $A0 | $10, $52, $33; Background Clouds
	.byte $A0 | $13, $5C, $32; Background Clouds
	.byte $80 | $13, $62, $87, $0B; Flat Land - Hilly
	.byte $00 | $13, $62, $60; 45 Degree Hill - Down/Left
	.byte $00 | $16, $61, $61; 45 Degree Hill - Down/Left
	.byte $80 | $19, $6E, $51, $05; Hilly Fill
	.byte $00 | $13, $6E, $55; 45 Degree Hill - Down/Right
	.byte $00 | $14, $62, $E1; Hilly Wall - Left Side
	.byte $A0 | $08, $67, $32; Background Clouds
	.byte $A0 | $0B, $6D, $32; Background Clouds
	.byte $40 | $10, $64, $0B; Background Hills B
	.byte $80 | $12, $68, $D2; Small Background Hills
	.byte $80 | $12, $6C, $D1; Small Background Hills
	.byte $80 | $19, $74, $81, $00; Flat Land - Hilly
	.byte $80 | $18, $75, $82, $01; Flat Land - Hilly
	.byte $00 | $18, $75, $60; 45 Degree Hill - Down/Left
	.byte $00 | $18, $76, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $19, $76, $E0; Hilly Wall - Right Side
	.byte $A0 | $04, $71, $32; Background Clouds
	.byte $A0 | $11, $72, $34; Background Clouds
	.byte $A0 | $11, $7D, $32; Background Clouds
	.byte $A0 | $14, $76, $32; Background Clouds
	.byte $20 | $03, $75, $1A; Bricks
	.byte $20 | $04, $75, $1A; Bricks
	.byte $20 | $05, $75, $1A; Bricks
	.byte $20 | $06, $75, $1A; Bricks
	.byte $20 | $07, $75, $1A; Bricks
	.byte $20 | $08, $75, $1A; Bricks
	.byte $20 | $09, $75, $1A; Bricks
	.byte $20 | $0A, $75, $1A; Bricks
	.byte $40 | $19, $7B, $E0; White Turtle Bricks
	.byte $40 | $19, $7D, $E0; White Turtle Bricks
	.byte $20 | $1A, $79, $46; Wooden blocks
	.byte $20 | $18, $7B, $0D; Brick with P-Switch
	.byte $20 | $19, $7C, $10; Bricks
	.byte $80 | $18, $80, $82, $0E; Flat Land - Hilly
	.byte $00 | $18, $80, $60; 45 Degree Hill - Down/Left
	.byte $00 | $19, $80, $E1; Hilly Wall - Left Side
	.byte $80 | $1A, $8F, $50, $03; Hilly Fill
	.byte $60 | $18, $8F, $51; 30 Degree Hill - Down/Right
	.byte $A0 | $06, $82, $33; Background Clouds
	.byte $A0 | $06, $8A, $32; Background Clouds
	.byte $A0 | $0B, $83, $32; Background Clouds
	.byte $A0 | $10, $88, $32; Background Clouds
	.byte $A0 | $12, $81, $32; Background Clouds
	.byte $80 | $17, $82, $D2; Small Background Hills
	.byte $40 | $14, $85, $0A; Background Hills A
	.byte $40 | $15, $8B, $0B; Background Hills B
	.byte $80 | $1A, $93, $80, $1C; Flat Land - Hilly
	.byte $40 | $16, $93, $0A; Background Hills A
	.byte $A0 | $0A, $91, $32; Background Clouds
	.byte $A0 | $10, $95, $32; Background Clouds
	.byte $A0 | $13, $91, $33; Background Clouds
	.byte $40 | $00, $99, $09; Level Ending
	.byte $A0 | $1A, $00, $1E; Background like at bottom of hilly level
	.byte $A0 | $1A, $13, $1C; Background like at bottom of hilly level
	.byte $A0 | $1A, $20, $1F; Background like at bottom of hilly level
	.byte $A0 | $1A, $30, $1F; Background like at bottom of hilly level
	.byte $A0 | $1A, $40, $1F; Background like at bottom of hilly level
	.byte $A0 | $1A, $50, $1F; Background like at bottom of hilly level
	.byte $A0 | $1A, $60, $1F; Background like at bottom of hilly level
	.byte $A0 | $1A, $70, $16; Background like at bottom of hilly level
	.byte $FF
Level_8_W6_objects:
	.byte $46, $10, $15; Pipe Ptooie
	.byte $6C, $1A, $17; Green Koopa Troopa
	.byte $33, $21, $17; Nipper Plant
	.byte $33, $23, $17; Nipper Plant
	.byte $33, $27, $16; Nipper Plant
	.byte $39, $2A, $15; Walking Nipper Plant
	.byte $39, $2F, $16; Walking Nipper Plant
	.byte $29, $37, $15; Spike
	.byte $29, $3D, $14; Spike
	.byte $29, $43, $13; Spike
	.byte $40, $4A, $18; Buster Beetle
	.byte $40, $54, $18; Buster Beetle
	.byte $40, $5D, $18; Buster Beetle
	.byte $33, $65, $12; Nipper Plant
	.byte $33, $68, $12; Nipper Plant
	.byte $33, $6B, $12; Nipper Plant
	.byte $40, $74, $18; Buster Beetle
	.byte $40, $7A, $19; Buster Beetle
	.byte $40, $7F, $19; Buster Beetle
	.byte $41, $A8, $15; Goal Card
	.byte $FF
; Level_4_W6
; Object Set 12
Level_4_W6_generators:
Level_4_W6_header:
	.byte $45; Next Level
	.byte LEVEL1_SIZE_11 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_13; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $1A, $0B, $10, $03; Icy flat ground
	.byte $00 | $17, $0C, $71; Snowy Platform
	.byte $00 | $19, $00, $35; Green topped wooden platform
	.byte $00 | $14, $01, $C2; Background Clouds
	.byte $00 | $11, $0A, $C2; Background Clouds
	.byte $00 | $05, $07, $C2; Background Clouds
	.byte $20 | $11, $04, $82; Coins
	.byte $60 | $13, $04, $42; Donut Blocks
	.byte $60 | $13, $14, $80; Large Ice Blocks
	.byte $60 | $13, $1B, $11; Ice Blocks
	.byte $60 | $13, $1E, $10; Ice Blocks
	.byte $60 | $17, $1C, $11; Ice Blocks
	.byte $60 | $14, $1E, $80; Large Ice Blocks
	.byte $60 | $16, $1F, $80; Large Ice Blocks
	.byte $00 | $18, $09, $C2; Background Clouds
	.byte $20 | $14, $18, $82; Coins
	.byte $20 | $12, $1B, $40; Wooden blocks
	.byte $60 | $15, $16, $10; Ice Blocks
	.byte $00 | $11, $17, $C2; Background Clouds
	.byte $60 | $13, $21, $13; Ice Blocks
	.byte $60 | $19, $26, $10; Ice Blocks
	.byte $60 | $17, $21, $10; Ice Blocks
	.byte $60 | $18, $22, $10; Ice Blocks
	.byte $60 | $19, $23, $11; Ice Blocks
	.byte $20 | $15, $26, $0B; Brick with 1-up
	.byte $00 | $09, $28, $C2; Background Clouds
	.byte $00 | $14, $22, $C2; Background Clouds
	.byte $60 | $13, $28, $82; Large Ice Blocks
	.byte $60 | $15, $28, $82; Large Ice Blocks
	.byte $60 | $17, $28, $82; Large Ice Blocks
	.byte $60 | $19, $28, $82; Large Ice Blocks
	.byte $00 | $09, $28, $C2; Background Clouds
	.byte $00 | $12, $2F, $95; 1 platform wire
	.byte $00 | $11, $2F, $07; Blue gear
	.byte $60 | $13, $32, $80; Large Ice Blocks
	.byte $60 | $15, $32, $80; Large Ice Blocks
	.byte $20 | $10, $32, $81; Coins
	.byte $00 | $06, $34, $C2; Background Clouds
	.byte $00 | $17, $30, $83; Horizontal platform wire
	.byte $00 | $17, $34, $B5; 45 Degree Platform Wire - Up/Right
	.byte $00 | $12, $3A, $A3; 45 Degree Platform Wire - Down/Right
	.byte $00 | $19, $3A, $B3; 45 Degree Platform Wire - Up/Right
	.byte $00 | $17, $37, $A2; 45 Degree Platform Wire - Down/Right
	.byte $00 | $16, $37, $B2; 45 Degree Platform Wire - Up/Right
	.byte $00 | $14, $3A, $A1; 45 Degree Platform Wire - Down/Right
	.byte $00 | $17, $3A, $B1; 45 Degree Platform Wire - Up/Right
	.byte $00 | $17, $39, $A0; 45 Degree Platform Wire - Down/Right
	.byte $00 | $16, $39, $B0; 45 Degree Platform Wire - Up/Right
	.byte $00 | $15, $3A, $07; Blue gear
	.byte $20 | $11, $3B, $01; '?' with Leaf
	.byte $20 | $13, $39, $81; Coins
	.byte $20 | $15, $37, $80; Coins
	.byte $20 | $15, $3C, $80; Coins
	.byte $20 | $17, $38, $80; Coins
	.byte $20 | $17, $3B, $80; Coins
	.byte $20 | $18, $39, $81; Coins
	.byte $00 | $11, $35, $C2; Background Clouds
	.byte $00 | $13, $3D, $C2; Background Clouds
	.byte $40 | $13, $34, $07; Red Invisible Note Block
	.byte $00 | $05, $44, $C2; Background Clouds
	.byte $00 | $0A, $4A, $C2; Background Clouds
	.byte $00 | $16, $4A, $E1; 60 Degree Platform Wire - Down/Left
	.byte $00 | $15, $49, $E1; 60 Degree Platform Wire - Down/Left
	.byte $00 | $15, $4F, $E1; 60 Degree Platform Wire - Down/Left
	.byte $00 | $14, $4E, $E1; 60 Degree Platform Wire - Down/Left
	.byte $00 | $15, $4A, $A0; 45 Degree Platform Wire - Down/Right
	.byte $00 | $19, $48, $A0; 45 Degree Platform Wire - Down/Right
	.byte $00 | $14, $4F, $A0; 45 Degree Platform Wire - Down/Right
	.byte $00 | $18, $4D, $A0; 45 Degree Platform Wire - Down/Right
	.byte $20 | $18, $44, $41; Wooden blocks
	.byte $00 | $11, $43, $C2; Background Clouds
	.byte $00 | $13, $4B, $C2; Background Clouds
	.byte $60 | $13, $52, $80; Large Ice Blocks
	.byte $60 | $15, $52, $80; Large Ice Blocks
	.byte $60 | $17, $52, $80; Large Ice Blocks
	.byte $60 | $19, $52, $80; Large Ice Blocks
	.byte $60 | $18, $59, $8A; Large Ice Blocks
	.byte $20 | $05, $55, $12; Bricks
	.byte $20 | $06, $56, $10; Bricks
	.byte $20 | $07, $56, $10; Bricks
	.byte $20 | $13, $56, $10; Bricks
	.byte $20 | $14, $56, $10; Bricks
	.byte $20 | $15, $56, $10; Bricks
	.byte $20 | $16, $56, $10; Bricks
	.byte $20 | $17, $56, $10; Bricks
	.byte $20 | $18, $56, $10; Bricks
	.byte $20 | $04, $56, $0A; Multi-Coin Brick
	.byte $20 | $19, $56, $40; Wooden blocks
	.byte $40 | $12, $56, $08; P-Switch
	.byte $00 | $01, $5A, $C2; Background Clouds
	.byte $00 | $07, $52, $C2; Background Clouds
	.byte $00 | $08, $59, $C2; Background Clouds
	.byte $00 | $11, $5A, $C2; Background Clouds
	.byte $00 | $05, $6C, $C2; Background Clouds
	.byte $00 | $09, $64, $C2; Background Clouds
	.byte $00 | $11, $6B, $C2; Background Clouds
	.byte $00 | $12, $63, $C2; Background Clouds
	.byte $60 | $15, $62, $10; Ice Blocks
	.byte $60 | $16, $62, $10; Ice Blocks
	.byte $60 | $16, $6B, $10; Ice Blocks
	.byte $60 | $17, $6B, $10; Ice Blocks
	.byte $20 | $17, $60, $14; Bricks
	.byte $20 | $00, $61, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $15, $6F, $81; Coins
	.byte $60 | $18, $71, $8F; Large Ice Blocks
	.byte $60 | $16, $75, $10; Ice Blocks
	.byte $60 | $17, $75, $10; Ice Blocks
	.byte $60 | $15, $7E, $10; Ice Blocks
	.byte $60 | $16, $7E, $10; Ice Blocks
	.byte $00 | $03, $7A, $C2; Background Clouds
	.byte $00 | $09, $77, $C2; Background Clouds
	.byte $00 | $0F, $74, $C2; Background Clouds
	.byte $00 | $10, $7D, $C2; Background Clouds
	.byte $20 | $07, $72, $82; Coins
	.byte $20 | $08, $72, $82; Coins
	.byte $20 | $09, $72, $82; Coins
	.byte $20 | $14, $74, $82; Coins
	.byte $20 | $08, $73, $0F; Invisible 1-up
	.byte $60 | $15, $87, $10; Ice Blocks
	.byte $60 | $16, $87, $10; Ice Blocks
	.byte $60 | $17, $87, $10; Ice Blocks
	.byte $60 | $11, $8F, $80; Large Ice Blocks
	.byte $60 | $16, $8F, $80; Large Ice Blocks
	.byte $00 | $05, $83, $C2; Background Clouds
	.byte $00 | $08, $8A, $C2; Background Clouds
	.byte $00 | $12, $8B, $C2; Background Clouds
	.byte $20 | $16, $8A, $82; Coins
	.byte $00 | $1A, $93, $10, $1C; Icy flat ground
	.byte $00 | $15, $94, $72; Snowy Platform
	.byte $40 | $00, $98, $09; Level Ending
	; Pointer on screen $03
	.byte $E0 | $03, $70 | $07, 80; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_4_W6_objects:
	.byte $92, $12, $16; Spinning Platform (periodical clockwise)
	.byte $92, $19, $18; Spinning Platform (periodical clockwise)
	.byte $72, $1E, $12; Goomba
	.byte $72, $23, $12; Goomba
	.byte $72, $24, $12; Goomba
	.byte $44, $2E, $13; Falling Platform (falls when stepped on)
	.byte $37, $3F, $19; Wooden platform - moves back and forth (a little)
	.byte $3C, $46, $18; Wired platform (follows platform wires)
	.byte $3C, $4D, $16; Wired platform (follows platform wires)
	.byte $91, $62, $15; Spinning Platform (constant)
	.byte $91, $6B, $16; Spinning Platform (constant)
	.byte $58, $77, $10; Fire Chomp
	.byte $91, $75, $16; Spinning Platform (constant)
	.byte $91, $7E, $15; Spinning Platform (constant)
	.byte $91, $87, $15; Spinning Platform (constant)
	.byte $91, $90, $16; Spinning Platform (constant)
	.byte $41, $A8, $15; Goal Card
	.byte $FF
; Level_7_W6
; Object Set 12
Level_7_W6_generators:
Level_7_W6_header:
	.byte $46; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_040; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_12; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $06, $00, $39; Green topped wooden platform
	.byte $00 | $08, $01, $04; Wooden Background Pole
	.byte $00 | $08, $07, $04; Wooden Background Pole
	.byte $00 | $03, $02, $C2; Background Clouds
	.byte $00 | $04, $0B, $C2; Background Clouds
	.byte $60 | $08, $0D, $42; Donut Blocks
	.byte $60 | $08, $13, $42; Donut Blocks
	.byte $20 | $0A, $15, $80; Coins
	.byte $20 | $0B, $15, $80; Coins
	.byte $20 | $0C, $15, $80; Coins
	.byte $00 | $07, $16, $C2; Background Clouds
	.byte $00 | $0A, $17, $34; Green topped wooden platform
	.byte $00 | $0C, $18, $04; Wooden Background Pole
	.byte $00 | $0C, $1A, $04; Wooden Background Pole
	.byte $60 | $00, $18, $17; Ice Blocks
	.byte $60 | $06, $1A, $13; Ice Blocks
	.byte $20 | $06, $19, $01; '?' with Leaf
	.byte $60 | $07, $1D, $10; Ice Blocks
	.byte $60 | $08, $1D, $10; Ice Blocks
	.byte $60 | $09, $1D, $10; Ice Blocks
	.byte $60 | $0A, $1D, $10; Ice Blocks
	.byte $60 | $06, $1E, $40; Donut Blocks
	.byte $60 | $00, $1F, $10; Ice Blocks
	.byte $60 | $01, $1F, $10; Ice Blocks
	.byte $60 | $02, $1F, $10; Ice Blocks
	.byte $60 | $03, $1F, $10; Ice Blocks
	.byte $60 | $04, $1F, $10; Ice Blocks
	.byte $60 | $05, $1F, $10; Ice Blocks
	.byte $60 | $06, $1F, $10; Ice Blocks
	.byte $00 | $10, $1C, $C2; Background Clouds
	.byte $60 | $0A, $1C, $40; Donut Blocks
	.byte $60 | $10, $1F, $40; Donut Blocks
	.byte $60 | $0D, $20, $43; Donut Blocks
	.byte $20 | $11, $22, $81; Coins
	.byte $20 | $12, $22, $81; Coins
	.byte $20 | $13, $22, $81; Coins
	.byte $00 | $17, $24, $C2; Background Clouds
	.byte $60 | $13, $26, $13; Ice Blocks
	.byte $00 | $0E, $27, $C2; Background Clouds
	.byte $20 | $12, $2C, $82; Coins
	.byte $60 | $16, $2C, $14; Ice Blocks
	.byte $00 | $19, $2D, $C2; Background Clouds
	.byte $60 | $15, $2A, $40; Donut Blocks
	.byte $20 | $16, $2A, $80; Coins
	.byte $20 | $17, $2A, $80; Coins
	.byte $20 | $18, $2A, $80; Coins
	.byte $00 | $11, $31, $C2; Background Clouds
	.byte $60 | $13, $32, $43; Donut Blocks
	.byte $60 | $17, $37, $42; Donut Blocks
	.byte $20 | $14, $38, $20; '?' blocks with single coins
	.byte $60 | $13, $3B, $42; Donut Blocks
	.byte $20 | $16, $3E, $82; Coins
	.byte $20 | $18, $39, $80; Coins
	.byte $20 | $19, $39, $80; Coins
	.byte $20 | $1A, $39, $80; Coins
	.byte $20 | $14, $35, $80; Coins
	.byte $20 | $15, $35, $80; Coins
	.byte $20 | $16, $35, $80; Coins
	.byte $60 | $17, $41, $42; Donut Blocks
	.byte $20 | $14, $42, $30; Bricks with single coins
	.byte $60 | $13, $45, $41; Donut Blocks
	.byte $20 | $15, $48, $12; Bricks
	.byte $60 | $19, $48, $13; Ice Blocks
	.byte $20 | $15, $49, $00; '?' with Flower
	.byte $00 | $12, $4B, $C2; Background Clouds
	.byte $20 | $15, $4D, $11; Bricks
	.byte $60 | $19, $4D, $12; Ice Blocks
	.byte $60 | $15, $4F, $10; Ice Blocks
	.byte $60 | $16, $4F, $10; Ice Blocks
	.byte $60 | $17, $4F, $10; Ice Blocks
	.byte $60 | $18, $4F, $10; Ice Blocks
	.byte $60 | $19, $4F, $10; Ice Blocks
	.byte $20 | $15, $46, $80; Coins
	.byte $20 | $16, $46, $80; Coins
	.byte $20 | $17, $46, $80; Coins
	.byte $20 | $18, $46, $80; Coins
	.byte $60 | $13, $51, $41; Donut Blocks
	.byte $60 | $0D, $53, $10; Ice Blocks
	.byte $60 | $0E, $53, $10; Ice Blocks
	.byte $60 | $0F, $53, $10; Ice Blocks
	.byte $60 | $10, $53, $10; Ice Blocks
	.byte $60 | $11, $53, $10; Ice Blocks
	.byte $60 | $12, $53, $10; Ice Blocks
	.byte $00 | $14, $55, $C2; Background Clouds
	.byte $60 | $19, $55, $42; Donut Blocks
	.byte $60 | $19, $58, $11; Ice Blocks
	.byte $00 | $0C, $59, $C2; Background Clouds
	.byte $60 | $19, $5D, $42; Donut Blocks
	.byte $60 | $11, $5D, $42; Donut Blocks
	.byte $60 | $15, $5F, $42; Donut Blocks
	.byte $60 | $15, $5A, $42; Donut Blocks
	.byte $60 | $19, $3C, $42; Donut Blocks
	.byte $20 | $0D, $52, $0B; Brick with 1-up
	.byte $20 | $16, $5C, $80; Coins
	.byte $20 | $17, $5C, $80; Coins
	.byte $20 | $18, $5C, $80; Coins
	.byte $20 | $19, $5C, $80; Coins
	.byte $20 | $12, $5D, $80; Coins
	.byte $20 | $13, $5D, $80; Coins
	.byte $20 | $14, $5D, $80; Coins
	.byte $00 | $12, $61, $C2; Background Clouds
	.byte $00 | $03, $66, $C2; Background Clouds
	.byte $00 | $08, $69, $35; Green topped wooden platform
	.byte $00 | $0A, $6A, $04; Wooden Background Pole
	.byte $00 | $0A, $6D, $04; Wooden Background Pole
	.byte $60 | $0D, $61, $42; Donut Blocks
	.byte $60 | $0B, $65, $42; Donut Blocks
	.byte $20 | $0E, $63, $80; Coins
	.byte $20 | $0F, $63, $80; Coins
	.byte $20 | $10, $63, $80; Coins
	.byte $20 | $04, $6A, $83; Coins
	.byte $60 | $05, $72, $40; Donut Blocks
	.byte $00 | $09, $74, $C2; Background Clouds
	.byte $60 | $04, $75, $18; Ice Blocks
	.byte $60 | $04, $77, $40; Donut Blocks
	.byte $00 | $02, $7B, $C2; Background Clouds
	.byte $20 | $10, $7C, $9A; Downward Pipe (CAN go down)
	.byte $20 | $09, $7C, $98; Downward Pipe (CAN go down)
	.byte $60 | $00, $7E, $11; Ice Blocks
	.byte $60 | $01, $7E, $11; Ice Blocks
	.byte $60 | $02, $7E, $11; Ice Blocks
	.byte $60 | $03, $7E, $11; Ice Blocks
	.byte $60 | $04, $7E, $11; Ice Blocks
	.byte $60 | $05, $7E, $11; Ice Blocks
	.byte $60 | $06, $7E, $11; Ice Blocks
	.byte $60 | $07, $7E, $11; Ice Blocks
	.byte $60 | $08, $7E, $11; Ice Blocks
	.byte $60 | $09, $7E, $11; Ice Blocks
	.byte $60 | $0A, $7E, $11; Ice Blocks
	.byte $60 | $0B, $7E, $11; Ice Blocks
	.byte $60 | $0C, $7E, $11; Ice Blocks
	.byte $60 | $0D, $7E, $11; Ice Blocks
	.byte $60 | $0E, $7E, $11; Ice Blocks
	.byte $60 | $0F, $7E, $11; Ice Blocks
	.byte $60 | $10, $7E, $11; Ice Blocks
	.byte $60 | $11, $7E, $11; Ice Blocks
	.byte $60 | $12, $7E, $11; Ice Blocks
	.byte $60 | $13, $7E, $11; Ice Blocks
	.byte $60 | $14, $7E, $11; Ice Blocks
	.byte $60 | $15, $7E, $11; Ice Blocks
	.byte $60 | $16, $7E, $11; Ice Blocks
	.byte $60 | $17, $7E, $11; Ice Blocks
	.byte $60 | $18, $7E, $11; Ice Blocks
	.byte $60 | $19, $7E, $11; Ice Blocks
	.byte $60 | $1A, $7E, $11; Ice Blocks
	.byte $20 | $0B, $7A, $61; Note Blocks - movable two directions
	.byte $60 | $07, $70, $40; Donut Blocks
	; Pointer on screen $07
	.byte $E0 | $07, $10 | $02, 128; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_7_W6_objects:
	.byte $D3, $00, $0A; Autoscrolling
	.byte $D4, $01, $4E; White Mushroom House (X pos must be uneven, Y pos=amount of coins required)
	.byte $58, $26, $0C; Fire Chomp
	.byte $58, $6F, $02; Fire Chomp
	.byte $FF
; Level_5_Outside_Area_W6
; Object Set 12
Level_5_Outside_Area_W6_generators:
Level_5_Outside_Area_W6_header:
	.byte $47; Next Level
	.byte LEVEL1_SIZE_06 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $40 | $00; Time | Music
	.byte $60 | $00, $0E, $1F; Ice Blocks
	.byte $60 | $01, $0E, $8F; Large Ice Blocks
	.byte $60 | $03, $0E, $8F; Large Ice Blocks
	.byte $60 | $05, $0E, $8F; Large Ice Blocks
	.byte $60 | $07, $0E, $8F; Large Ice Blocks
	.byte $60 | $09, $0E, $8F; Large Ice Blocks
	.byte $60 | $0B, $0E, $8F; Large Ice Blocks
	.byte $60 | $0D, $0E, $8F; Large Ice Blocks
	.byte $60 | $0F, $0E, $8F; Large Ice Blocks
	.byte $60 | $11, $0E, $86; Large Ice Blocks
	.byte $60 | $13, $0C, $87; Large Ice Blocks
	.byte $60 | $15, $06, $80; Large Ice Blocks
	.byte $60 | $15, $0A, $88; Large Ice Blocks
	.byte $60 | $17, $04, $81; Large Ice Blocks
	.byte $60 | $17, $0E, $86; Large Ice Blocks
	.byte $60 | $19, $00, $8F; Large Ice Blocks
	.byte $20 | $00, $00, $4D; Wooden blocks
	.byte $00 | $12, $01, $C2; Background Clouds
	.byte $00 | $13, $08, $C2; Background Clouds
	.byte $20 | $17, $0C, $E1; Rightward Pipe (CAN go in)
	.byte $60 | $00, $1E, $1F; Ice Blocks
	.byte $60 | $00, $2E, $1F; Ice Blocks
	.byte $60 | $01, $2E, $84; Large Ice Blocks
	.byte $60 | $03, $2E, $84; Large Ice Blocks
	.byte $60 | $05, $2E, $84; Large Ice Blocks
	.byte $60 | $07, $2E, $84; Large Ice Blocks
	.byte $60 | $09, $2E, $84; Large Ice Blocks
	.byte $60 | $0B, $2E, $84; Large Ice Blocks
	.byte $60 | $0D, $2E, $84; Large Ice Blocks
	.byte $60 | $0F, $2E, $84; Large Ice Blocks
	.byte $60 | $11, $26, $88; Large Ice Blocks
	.byte $60 | $13, $26, $88; Large Ice Blocks
	.byte $60 | $15, $26, $88; Large Ice Blocks
	.byte $60 | $17, $26, $88; Large Ice Blocks
	.byte $60 | $19, $20, $8F; Large Ice Blocks
	.byte $40 | $17, $1C, $11; Leftward Pipe (CAN go in)
	.byte $20 | $15, $20, $01; '?' with Leaf
	.byte $20 | $17, $24, $91; Downward Pipe (CAN go down)
	.byte $60 | $00, $3F, $10; Ice Blocks
	.byte $60 | $01, $38, $17; Ice Blocks
	.byte $60 | $02, $38, $17; Ice Blocks
	.byte $60 | $03, $38, $17; Ice Blocks
	.byte $60 | $04, $38, $17; Ice Blocks
	.byte $60 | $05, $38, $17; Ice Blocks
	.byte $60 | $06, $38, $17; Ice Blocks
	.byte $60 | $07, $38, $17; Ice Blocks
	.byte $60 | $08, $38, $17; Ice Blocks
	.byte $60 | $09, $38, $17; Ice Blocks
	.byte $60 | $0A, $38, $17; Ice Blocks
	.byte $60 | $0B, $38, $17; Ice Blocks
	.byte $60 | $0C, $38, $17; Ice Blocks
	.byte $60 | $0D, $38, $17; Ice Blocks
	.byte $60 | $0E, $38, $17; Ice Blocks
	.byte $60 | $0F, $38, $17; Ice Blocks
	.byte $60 | $10, $38, $17; Ice Blocks
	.byte $60 | $11, $38, $17; Ice Blocks
	.byte $60 | $12, $38, $17; Ice Blocks
	.byte $60 | $13, $38, $17; Ice Blocks
	.byte $60 | $14, $38, $17; Ice Blocks
	.byte $60 | $15, $38, $17; Ice Blocks
	.byte $60 | $16, $38, $17; Ice Blocks
	.byte $60 | $17, $38, $17; Ice Blocks
	.byte $60 | $18, $38, $17; Ice Blocks
	.byte $60 | $19, $38, $17; Ice Blocks
	.byte $00 | $1A, $38, $10, $27; Icy flat ground
	.byte $20 | $17, $41, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $13, $47, $C2; Background Clouds
	.byte $00 | $14, $43, $C2; Background Clouds
	.byte $40 | $00, $4C, $09; Level Ending
	; Pointer on screen $00
	.byte $E0 | $00, $50 | $02, 32; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $01
	.byte $E0 | $01, $60 | $04, 150; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $02
	.byte $E0 | $02, $50 | $02, 65; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_5_Outside_Area_W6_objects:
	.byte $41, $58, $15; Goal Card
	.byte $FF
; Level_9_Outside_Area_W6
; Object Set 12
Level_9_Outside_Area_W6_generators:
Level_9_Outside_Area_W6_header:
	.byte $48; Next Level
	.byte LEVEL1_SIZE_06 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $1A, $00, $10, $5F; Icy flat ground
	.byte $60 | $14, $0C, $80; Large Ice Blocks
	.byte $60 | $16, $0A, $83; Large Ice Blocks
	.byte $60 | $18, $08, $85; Large Ice Blocks
	.byte $20 | $16, $0E, $94; Downward Pipe (CAN go down)
	.byte $60 | $0E, $18, $8C; Large Ice Blocks
	.byte $60 | $10, $18, $8C; Large Ice Blocks
	.byte $60 | $12, $18, $8C; Large Ice Blocks
	.byte $60 | $14, $18, $8C; Large Ice Blocks
	.byte $60 | $16, $18, $8C; Large Ice Blocks
	.byte $60 | $18, $18, $8F; Large Ice Blocks
	.byte $20 | $0B, $25, $0B; Brick with 1-up
	.byte $40 | $0D, $23, $E0; White Turtle Bricks
	.byte $40 | $0D, $27, $E0; White Turtle Bricks
	.byte $60 | $18, $3E, $80; Large Ice Blocks
	.byte $20 | $17, $34, $A3; Downward Pipe (CAN'T go down)
	.byte $40 | $00, $48, $09; Level Ending
	; Pointer on screen $00
	.byte $E0 | $00, $00 | $02, 64; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_9_Outside_Area_W6_objects:
	.byte $6D, $26, $0D; Red Koopa Troopa
	.byte $41, $58, $15; Goal Card
	.byte $FF
; Dungeon__3_W6
; Object Set 2
Dungeon__3_W6_generators:
Dungeon__3_W6_header:
	.byte $49; Next Level
	.byte LEVEL1_SIZE_11 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $00, $00, $3F, $AF; Blank Background (used to block out stuff)
	.byte $60 | $10, $00, $38, $AF; Blank Background (used to block out stuff)
	.byte $00 | $00, $00, $FF, $13; Vertically oriented X-blocks
	.byte $00 | $14, $00, $DF; Ceiling Spikes
	.byte $00 | $16, $01, $63; Dungeon windows
	.byte $00 | $00, $10, $E5, $6F; Horizontally oriented X-blocks
	.byte $00 | $09, $15, $73; Long dungeon windows
	.byte $00 | $16, $13, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $15, $13, $02; Rotodisc block
	.byte $60 | $14, $17, $64; Conveyor Belt - moves right
	.byte $00 | $18, $14, $CF; Floor Spikes
	.byte $00 | $16, $1E, $E2, $02; Horizontally oriented X-blocks
	.byte $00 | $15, $1F, $02; Rotodisc block
	.byte $00 | $0A, $28, $63; Dungeon windows
	.byte $00 | $11, $23, $73; Long dungeon windows
	.byte $60 | $16, $25, $5B; Conveyor Belt - moves left
	.byte $00 | $18, $24, $CF; Floor Spikes
	.byte $20 | $09, $25, $0B; Brick with 1-up
	.byte $00 | $0C, $23, $E0, $03; Horizontally oriented X-blocks
	.byte $00 | $12, $38, $61; Dungeon windows
	.byte $00 | $08, $3B, $73; Long dungeon windows
	.byte $20 | $15, $39, $01; '?' with leaf
	.byte $00 | $17, $33, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $15, $3A, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $34, $B5; Stretch platform
	.byte $00 | $16, $3B, $B5; Stretch platform
	.byte $00 | $06, $49, $EB, $05; Horizontally oriented X-blocks
	.byte $00 | $15, $43, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $49, $B5; Stretch platform
	.byte $00 | $0B, $59, $E4, $03; Horizontally oriented X-blocks
	.byte $00 | $10, $59, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $10, $5C, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $54, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $11, $52, $61; Dungeon windows
	.byte $00 | $18, $55, $CA; Floor Spikes
	.byte $60 | $16, $55, $58; Conveyor Belt - moves left
	.byte $00 | $15, $54, $02; Rotodisc block
	.byte $20 | $0A, $59, $0A; Multi-Coin Brick
	.byte $20 | $0A, $5C, $0A; Multi-Coin Brick
	.byte $00 | $15, $6C, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $06, $6F, $EA, $12; Horizontally oriented X-blocks
	.byte $00 | $08, $61, $73; Long dungeon windows
	.byte $60 | $14, $65, $67; Conveyor Belt - moves right
	.byte $60 | $14, $60, $53; Conveyor Belt - moves left
	.byte $00 | $18, $60, $CB; Floor Spikes
	.byte $00 | $14, $64, $02; Rotodisc block
	.byte $00 | $16, $75, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $12, $76, $63; Dungeon windows
	.byte $00 | $18, $76, $C9; Floor Spikes
	.byte $00 | $16, $76, $B5; Stretch platform
	.byte $00 | $16, $7D, $B5; Stretch platform
	.byte $00 | $00, $82, $EB, $0D; Horizontally oriented X-blocks
	.byte $00 | $0C, $8F, $E9, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $89, $E2, $06; Horizontally oriented X-blocks
	.byte $00 | $10, $86, $71; Long dungeon windows
	.byte $00 | $18, $80, $C8; Floor Spikes
	.byte $00 | $14, $8D, $00; Door
	.byte $00 | $00, $90, $EF, $1F; Horizontally oriented X-blocks
	.byte $00 | $10, $90, $E8, $1F; Horizontally oriented X-blocks
	.byte $60 | $15, $98, $33, $08; Blank Background (used to block out stuff)
	.byte $60 | $10, $A1, $38, $0D; Blank Background (used to block out stuff)
	.byte $00 | $16, $9B, $61; Dungeon windows
	.byte $00 | $13, $A5, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $13, $AA, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $A3, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $A8, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $AC, $E0, $00; Horizontally oriented X-blocks
	; Pointer on screen $08
	.byte $E0 | $08, $10 | $08, 128; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__3_W6_objects:
	.byte $60, $13, $15; Double Rotodisc (rotates clockwise)
	.byte $51, $1F, $15; Double Rotodisc (rotates counterclockwise)
	.byte $2F, $26, $12; Boo Buddy
	.byte $2F, $2D, $12; Boo Buddy
	.byte $31, $38, $17; Top Stretch
	.byte $31, $3E, $15; Top Stretch
	.byte $32, $3E, $17; Bottom Stretch
	.byte $2F, $44, $16; Boo Buddy
	.byte $31, $4D, $15; Top Stretch
	.byte $5A, $54, $15; Single Rotodisc (rotates clockwise)
	.byte $8A, $5A, $10; Thwomp (normal)
	.byte $5B, $64, $14; Single Rotodisc (rotates counterclockwise)
	.byte $5F, $7C, $16; Double Rotodisc (rotates both ways, starting at top)
	.byte $31, $7A, $15; Top Stretch
	.byte $31, $81, $15; Top Stretch
	.byte $4B, $AC, $37; Boom Boom
	.byte $FF
; Level_10_W6
; Object Set 12
Level_10_W6_generators:
Level_10_W6_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_11 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $20 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $15, $02, $C2; Background Clouds
	.byte $60 | $19, $00, $83; Large Ice Blocks
	.byte $00 | $12, $08, $C2; Background Clouds
	.byte $60 | $18, $0A, $82; Large Ice Blocks
	.byte $60 | $1A, $0A, $15; Ice Blocks
	.byte $60 | $14, $0B, $11; Ice Blocks
	.byte $60 | $15, $0E, $14; Ice Blocks
	.byte $60 | $18, $12, $82; Large Ice Blocks
	.byte $60 | $1A, $12, $15; Ice Blocks
	.byte $00 | $13, $18, $C2; Background Clouds
	.byte $60 | $18, $1C, $81; Large Ice Blocks
	.byte $60 | $1A, $1C, $13; Ice Blocks
	.byte $20 | $18, $1A, $A2; Downward Pipe (CAN'T go down)
	.byte $60 | $1A, $29, $16; Ice Blocks
	.byte $20 | $15, $22, $16; Bricks
	.byte $60 | $19, $22, $80; Large Ice Blocks
	.byte $20 | $15, $23, $00; '?' with Flower
	.byte $00 | $05, $21, $C2; Background Clouds
	.byte $20 | $04, $26, $11; Bricks
	.byte $60 | $07, $25, $14; Ice Blocks
	.byte $20 | $03, $2A, $41; Wooden blocks
	.byte $20 | $04, $25, $0D; Brick with P-Switch
	.byte $00 | $12, $27, $C2; Background Clouds
	.byte $00 | $0A, $2C, $C2; Background Clouds
	.byte $20 | $02, $2F, $12; Bricks
	.byte $20 | $03, $2F, $12; Bricks
	.byte $20 | $04, $2F, $12; Bricks
	.byte $20 | $05, $2F, $12; Bricks
	.byte $20 | $06, $2F, $12; Bricks
	.byte $20 | $07, $2F, $12; Bricks
	.byte $20 | $08, $2F, $12; Bricks
	.byte $20 | $09, $2F, $12; Bricks
	.byte $20 | $0A, $2F, $12; Bricks
	.byte $20 | $0B, $2F, $12; Bricks
	.byte $20 | $0C, $2F, $12; Bricks
	.byte $20 | $0D, $2F, $12; Bricks
	.byte $20 | $0E, $2F, $12; Bricks
	.byte $20 | $0F, $2F, $12; Bricks
	.byte $20 | $10, $2F, $12; Bricks
	.byte $20 | $11, $2F, $12; Bricks
	.byte $20 | $12, $2F, $12; Bricks
	.byte $20 | $13, $2F, $12; Bricks
	.byte $20 | $14, $2F, $12; Bricks
	.byte $20 | $15, $2F, $12; Bricks
	.byte $20 | $16, $2F, $12; Bricks
	.byte $20 | $17, $2F, $12; Bricks
	.byte $40 | $18, $2F, $E2; White Turtle Bricks
	.byte $40 | $19, $2F, $E2; White Turtle Bricks
	.byte $20 | $18, $20, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $2A, $0C; Brick with Vine
	.byte $40 | $19, $2A, $E0; White Turtle Bricks
	.byte $40 | $19, $29, $E0; White Turtle Bricks
	.byte $20 | $18, $29, $10; Bricks
	.byte $60 | $1A, $30, $1F; Ice Blocks
	.byte $20 | $16, $36, $21; '?' blocks with single coins
	.byte $20 | $16, $38, $00; '?' with Flower
	.byte $00 | $0C, $35, $C2; Background Clouds
	.byte $60 | $19, $38, $12; Ice Blocks
	.byte $60 | $19, $3B, $22; Frozen Munchers
	.byte $00 | $12, $39, $C2; Background Clouds
	.byte $20 | $17, $3E, $A2; Downward Pipe (CAN'T go down)
	.byte $60 | $19, $3B, $32; Frozen Coins
	.byte $60 | $1A, $3B, $22; Frozen Munchers
	.byte $40 | $19, $34, $E1; White Turtle Bricks
	.byte $40 | $18, $3A, $E1; White Turtle Bricks
	.byte $60 | $1A, $40, $1F; Ice Blocks
	.byte $00 | $13, $41, $C2; Background Clouds
	.byte $00 | $14, $47, $C2; Background Clouds
	.byte $60 | $17, $46, $32; Frozen Coins
	.byte $60 | $18, $46, $32; Frozen Coins
	.byte $60 | $19, $46, $32; Frozen Coins
	.byte $60 | $16, $4A, $10; Ice Blocks
	.byte $60 | $16, $4F, $10; Ice Blocks
	.byte $60 | $17, $4A, $15; Ice Blocks
	.byte $60 | $17, $4B, $23; Frozen Munchers
	.byte $60 | $18, $4A, $82; Large Ice Blocks
	.byte $20 | $18, $4C, $B1; Downward Pipe (CAN go down, ignores pointers)
	.byte $60 | $1A, $56, $1F; Ice Blocks
	.byte $00 | $12, $52, $C2; Background Clouds
	.byte $00 | $13, $5C, $C2; Background Clouds
	.byte $60 | $18, $56, $3F; Frozen Coins
	.byte $60 | $17, $56, $30; Frozen Coins
	.byte $60 | $19, $56, $2F; Frozen Munchers
	.byte $60 | $19, $5A, $33; Frozen Coins
	.byte $40 | $17, $5A, $E3; White Turtle Bricks
	.byte $60 | $18, $66, $3F; Frozen Coins
	.byte $60 | $1A, $66, $1F; Ice Blocks
	.byte $60 | $19, $66, $2F; Frozen Munchers
	.byte $00 | $14, $66, $C2; Background Clouds
	.byte $40 | $17, $61, $E3; White Turtle Bricks
	.byte $40 | $17, $68, $E2; White Turtle Bricks
	.byte $40 | $17, $6E, $E3; White Turtle Bricks
	.byte $60 | $19, $61, $33; Frozen Coins
	.byte $60 | $19, $68, $32; Frozen Coins
	.byte $60 | $19, $6E, $33; Frozen Coins
	.byte $60 | $17, $75, $30; Frozen Coins
	.byte $00 | $11, $71, $C2; Background Clouds
	.byte $00 | $12, $7B, $C2; Background Clouds
	.byte $60 | $17, $7C, $80; Large Ice Blocks
	.byte $60 | $19, $7C, $80; Large Ice Blocks
	.byte $00 | $12, $83, $C2; Background Clouds
	.byte $60 | $17, $84, $80; Large Ice Blocks
	.byte $60 | $19, $84, $80; Large Ice Blocks
	.byte $60 | $17, $88, $80; Large Ice Blocks
	.byte $60 | $19, $88, $80; Large Ice Blocks
	.byte $00 | $14, $8B, $C2; Background Clouds
	.byte $60 | $1A, $8C, $13; Ice Blocks
	.byte $60 | $1A, $90, $1F; Ice Blocks
	.byte $40 | $00, $96, $09; Level Ending
	.byte $60 | $1A, $A0, $1F; Ice Blocks
	; Pointer on screen $04
	.byte $E0 | $04, $10 | $02, 214; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_10_W6_objects:
	.byte $6D, $0B, $13; Red Koopa Troopa
	.byte $6D, $12, $14; Red Koopa Troopa
	.byte $6D, $24, $14; Red Koopa Troopa
	.byte $6D, $26, $14; Red Koopa Troopa
	.byte $40, $33, $19; Buster Beetle
	.byte $40, $3C, $18; Buster Beetle
	.byte $73, $45, $19; Para-Goomba
	.byte $6F, $52, $17; Red Koopa Paratroopa
	.byte $40, $5E, $17; Buster Beetle
	.byte $40, $65, $17; Buster Beetle
	.byte $40, $6B, $17; Buster Beetle
	.byte $40, $74, $17; Buster Beetle
	.byte $92, $81, $15; Spinning Platform (periodical clockwise)
	.byte $6D, $84, $15; Red Koopa Troopa
	.byte $41, $A8, $15; Goal Card
	.byte $FF
; Hammer_Bros_1_W7
; Object Set 1
Hammer_Bros_1_W7_generators:
Hammer_Bros_1_W7_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $80 | $06; Time | Music
	.byte $00 | $0F, $0D, $E2; Background Clouds
	.byte $00 | $12, $02, $E2; Background Clouds
	.byte $20 | $12, $07, $16; Bricks
	.byte $00 | $16, $00, $00; Background Hills A
	.byte $20 | $16, $07, $16; Bricks
	.byte $00 | $17, $05, $01; Background Hills B
	.byte $00 | $17, $0C, $01; Background Hills B
	.byte $00 | $1A, $00, $C0, $0F; Flat Ground
	.byte $FF
Hammer_Bros_1_W7_objects:
	.byte $81, $0C, $14; Hammer Brother
	.byte $81, $09, $18; Hammer Brother
	.byte $BA, $0D, $14; Exit on get treasure chest
	.byte $FF
; Pipe_2_End_2_W7
; Object Set 14
Pipe_2_End_2_W7_generators:
Pipe_2_End_2_W7_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_D8 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $19, $00, $51, $0F; Hilly Fill
	.byte $80 | $13, $00, $55, $00; Hilly Fill
	.byte $60 | $0F, $00, $E3; Hilly Wall - Right Side
	.byte $80 | $13, $01, $85, $01; Flat Land - Hilly
	.byte $60 | $13, $03, $55; 30 Degree Hill - Down/Right
	.byte $00 | $0F, $0F, $E9; Hilly Wall - Left Side
	.byte $80 | $0F, $03, $50, $09; Hilly Fill
	.byte $00 | $0F, $03, $E0; Hilly Wall - Left Side
	.byte $80 | $0F, $0B, $B4, $01; Ceiling - Hilly
	.byte $60 | $0F, $0C, $E3; Hilly Wall - Right Side
	.byte $00 | $13, $0C, $0A; Lower Right Hill Corner
	.byte $60 | $10, $03, $73; 30 Degree Hill - Up/Left
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $0F, $0D, $C6; Upward Pipe (CAN go up)
	.byte $FF
Pipe_2_End_2_W7_objects:
	.byte $25, $02, $06; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Pipe_5_End_2_W7
; Object Set 14
Pipe_5_End_2_W7_generators:
Pipe_5_End_2_W7_header:
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
Pipe_5_End_2_W7_objects:
	.byte $25, $02, $05; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Dungeon__1_W7
; Object Set 2
Dungeon__1_W7_generators:
Dungeon__1_W7_header:
	.byte $4A; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_0B0; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $80 | $03; Time | Music
	.byte $60 | $00, $00, $3F, $4F; Blank Background (used to block out stuff)
	.byte $60 | $10, $00, $3A, $4F; Blank Background (used to block out stuff)
	.byte $20 | $01, $00, $1F; Bricks
	.byte $20 | $02, $00, $1F; Bricks
	.byte $20 | $03, $00, $1F; Bricks
	.byte $20 | $04, $00, $1F; Bricks
	.byte $20 | $05, $00, $1F; Bricks
	.byte $20 | $06, $00, $1F; Bricks
	.byte $20 | $07, $00, $1F; Bricks
	.byte $20 | $0C, $0E, $17; Bricks
	.byte $20 | $0D, $0E, $17; Bricks
	.byte $20 | $0E, $0E, $17; Bricks
	.byte $20 | $0D, $00, $17; Bricks
	.byte $20 | $0E, $00, $18; Bricks
	.byte $20 | $0F, $00, $19; Bricks
	.byte $20 | $10, $00, $19; Bricks
	.byte $20 | $11, $00, $1F; Bricks
	.byte $20 | $12, $00, $1F; Bricks
	.byte $20 | $13, $00, $1F; Bricks
	.byte $20 | $14, $00, $1F; Bricks
	.byte $20 | $15, $00, $1F; Bricks
	.byte $20 | $16, $00, $1F; Bricks
	.byte $20 | $17, $00, $1F; Bricks
	.byte $00 | $00, $00, $E0, $29; Horizontally oriented X-blocks
	.byte $00 | $1A, $00, $E0, $29; Horizontally oriented X-blocks
	.byte $00 | $0D, $0C, $E0, $01; Horizontally oriented X-blocks
	.byte $20 | $08, $13, $11; Bricks
	.byte $20 | $09, $13, $11; Bricks
	.byte $20 | $0A, $13, $11; Bricks
	.byte $20 | $0B, $13, $11; Bricks
	.byte $20 | $0D, $1B, $1E; Bricks
	.byte $20 | $0E, $1A, $1F; Bricks
	.byte $20 | $0F, $19, $16; Bricks
	.byte $20 | $10, $18, $17; Bricks
	.byte $00 | $0B, $1E, $00; Door
	.byte $20 | $0C, $11, $0D; Brick with P-Switch
	.byte $20 | $01, $10, $1F; Bricks
	.byte $20 | $02, $10, $1F; Bricks
	.byte $20 | $03, $10, $1F; Bricks
	.byte $20 | $04, $10, $1F; Bricks
	.byte $20 | $05, $10, $1F; Bricks
	.byte $20 | $06, $10, $1F; Bricks
	.byte $20 | $07, $10, $1F; Bricks
	.byte $20 | $11, $10, $1F; Bricks
	.byte $20 | $12, $10, $1F; Bricks
	.byte $20 | $13, $10, $1F; Bricks
	.byte $20 | $14, $10, $1F; Bricks
	.byte $20 | $15, $10, $1F; Bricks
	.byte $20 | $16, $10, $1F; Bricks
	.byte $20 | $17, $10, $1F; Bricks
	.byte $20 | $08, $20, $19; Bricks
	.byte $20 | $09, $20, $19; Bricks
	.byte $20 | $0A, $20, $19; Bricks
	.byte $20 | $0B, $20, $19; Bricks
	.byte $20 | $0C, $20, $19; Bricks
	.byte $00 | $18, $21, $00; Door
	.byte $00 | $00, $2A, $F9, $1A; Vertically oriented X-blocks
	.byte $20 | $01, $20, $19; Bricks
	.byte $20 | $02, $20, $19; Bricks
	.byte $20 | $03, $20, $19; Bricks
	.byte $20 | $04, $20, $19; Bricks
	.byte $20 | $05, $20, $19; Bricks
	.byte $20 | $06, $20, $19; Bricks
	.byte $20 | $07, $20, $19; Bricks
	.byte $20 | $0F, $20, $19; Bricks
	.byte $20 | $10, $20, $19; Bricks
	.byte $20 | $11, $20, $19; Bricks
	.byte $20 | $12, $20, $19; Bricks
	.byte $20 | $13, $20, $19; Bricks
	.byte $20 | $14, $20, $19; Bricks
	.byte $20 | $15, $20, $19; Bricks
	.byte $20 | $16, $20, $19; Bricks
	.byte $20 | $17, $20, $19; Bricks
	.byte $00 | $00, $34, $E1, $13; Horizontally oriented X-blocks
	.byte $00 | $19, $34, $E1, $05; Horizontally oriented X-blocks
	.byte $00 | $16, $3F, $E0, $03; Horizontally oriented X-blocks
	.byte $00 | $13, $34, $E0, $05; Horizontally oriented X-blocks
	.byte $00 | $11, $39, $E1, $00; Horizontally oriented X-blocks
	.byte $20 | $10, $36, $00; '?' with flower
	.byte $00 | $17, $35, $00; Door
	.byte $60 | $1A, $3A, $40, $0D; Lava
	.byte $00 | $0D, $44, $E0, $01; Horizontally oriented X-blocks
	.byte $20 | $12, $40, $22; '?' blocks with single coins
	.byte $20 | $0B, $46, $F1; Rightward Pipe (CAN'T go in)
	.byte $00 | $00, $48, $F7, $1A; Vertically oriented X-blocks
	.byte $60 | $10, $58, $38, $16; Blank Background (used to block out stuff)
	.byte $00 | $00, $50, $EF, $1F; Horizontally oriented X-blocks
	.byte $00 | $10, $50, $E8, $07; Horizontally oriented X-blocks
	.byte $20 | $17, $59, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $10, $58, $E4, $07; Horizontally oriented X-blocks
	.byte $00 | $11, $63, $60; Dungeon windows
	.byte $00 | $10, $6F, $E8, $00; Horizontally oriented X-blocks
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $08, 229; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $01
	.byte $E0 | $01, $60 | $08, 130; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $02
	.byte $E0 | $02, $60 | $08, 130; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $03
	.byte $E0 | $03, $60 | $08, 212; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__1_W7_objects:
	.byte $08, $0C, $0B; Invisible door (appears when you hit a P-switch)
	.byte $4C, $6C, $17; Flying Boom Boom
	.byte $FF
; Level_1_Outside_Area_W7
; Object Set 1
Level_1_Outside_Area_W7_generators:
Level_1_Outside_Area_W7_header:
	.byte $4B; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_08; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $1A, $00, $C0, $3F; Flat Ground
	.byte $40 | $00, $00, $B0, $0F; Blue X-Blocks
	.byte $00 | $13, $01, $E2; Background Clouds
	.byte $00 | $13, $0A, $E3; Background Clouds
	.byte $00 | $12, $03, $02; Background Hills C
	.byte $20 | $17, $0A, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $0C, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $0E, $A3; Downward Pipe (CAN'T go down)
	.byte $40 | $00, $10, $BF, $0F; Blue X-Blocks
	.byte $40 | $10, $10, $BA, $0F; Blue X-Blocks
	.byte $00 | $14, $10, $04; Door (CAN go in)
	.byte $00 | $13, $22, $E2; Background Clouds
	.byte $00 | $11, $26, $E2; Background Clouds
	.byte $40 | $18, $20, $21; Leftward Pipe (CAN'T go in)
	.byte $20 | $17, $25, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $15, $27, $A4; Downward Pipe (CAN'T go down)
	.byte $40 | $00, $2A, $09; Level Ending
	; Pointer on screen $00
	.byte $E0 | $00, $F0 | $08, 39; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $01
	.byte $E0 | $01, $F0 | $08, 39; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_1_Outside_Area_W7_objects:
	.byte $41, $38, $15; Goal Card
	.byte $FF
; Pipe_1_End_1_W7
; Object Set 14
Pipe_1_End_1_W7_generators:
Pipe_1_End_1_W7_header:
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
Pipe_1_End_1_W7_objects:
	.byte $25, $02, $04; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Pipe_5_End_1_W7
; Object Set 14
Pipe_5_End_1_W7_generators:
Pipe_5_End_1_W7_header:
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
Pipe_5_End_1_W7_objects:
	.byte $25, $02, $05; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Pipe_8_End_1_W7
; Object Set 14
Pipe_8_End_1_W7_generators:
Pipe_8_End_1_W7_header:
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
Pipe_8_End_1_W7_objects:
	.byte $25, $02, $09; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Piranha_Plant__1_W7
; Object Set 5
Piranha_Plant__1_W7_generators:
Piranha_Plant__1_W7_header:
	.byte $4C; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_05; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $05; Start action | Graphic set
	.byte $80 | $00; Time | Music
	.byte $20 | $19, $00, $F7; Rightward Pipe (CAN'T go in)
	.byte $20 | $19, $08, $F7; Rightward Pipe (CAN'T go in)
	.byte $20 | $14, $0A, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $17, $0A, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $14, $12, $A3; Downward Pipe (CAN'T go down)
	.byte $40 | $19, $10, $23; Leftward Pipe (CAN'T go in)
	.byte $20 | $19, $18, $F7; Rightward Pipe (CAN'T go in)
	.byte $00 | $14, $18, $01; Piranha Plant Muncher B
	.byte $20 | $17, $12, $D1; Upward Pipe (CAN'T go up)
	.byte $00 | $15, $18, $B3; Piranha Plant Small Downward Pipe B
	.byte $00 | $15, $19, $B3; Piranha Plant Small Downward Pipe B
	.byte $00 | $16, $1A, $A2; Piranha Plant Small Downward Pipe A
	.byte $00 | $16, $1B, $A2; Piranha Plant Small Downward Pipe A
	.byte $00 | $14, $1C, $B4; Piranha Plant Small Downward Pipe B
	.byte $00 | $14, $1D, $B4; Piranha Plant Small Downward Pipe B
	.byte $00 | $15, $1E, $A3; Piranha Plant Small Downward Pipe A
	.byte $00 | $15, $1F, $A3; Piranha Plant Small Downward Pipe A
	.byte $00 | $14, $19, $01; Piranha Plant Muncher B
	.byte $00 | $15, $1A, $00; Piranha Plant Muncher A
	.byte $00 | $15, $1B, $00; Piranha Plant Muncher A
	.byte $00 | $13, $1C, $01; Piranha Plant Muncher B
	.byte $00 | $13, $1D, $01; Piranha Plant Muncher B
	.byte $00 | $14, $1E, $00; Piranha Plant Muncher A
	.byte $00 | $14, $1F, $00; Piranha Plant Muncher A
	.byte $40 | $19, $20, $21; Leftward Pipe (CAN'T go in)
	.byte $40 | $19, $22, $28; Leftward Pipe (CAN'T go in)
	.byte $00 | $13, $20, $B5; Piranha Plant Small Downward Pipe B
	.byte $00 | $13, $21, $B5; Piranha Plant Small Downward Pipe B
	.byte $00 | $14, $22, $A4; Piranha Plant Small Downward Pipe A
	.byte $00 | $14, $23, $A4; Piranha Plant Small Downward Pipe A
	.byte $00 | $15, $24, $B3; Piranha Plant Small Downward Pipe B
	.byte $00 | $15, $25, $B3; Piranha Plant Small Downward Pipe B
	.byte $00 | $12, $26, $A6; Piranha Plant Small Downward Pipe A
	.byte $00 | $12, $27, $A6; Piranha Plant Small Downward Pipe A
	.byte $20 | $0B, $2C, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $0F, $2C, $D3; Upward Pipe (CAN'T go up)
	.byte $20 | $19, $2F, $F8; Rightward Pipe (CAN'T go in)
	.byte $00 | $12, $20, $01; Piranha Plant Muncher B
	.byte $00 | $12, $21, $01; Piranha Plant Muncher B
	.byte $00 | $13, $22, $00; Piranha Plant Muncher A
	.byte $00 | $13, $23, $00; Piranha Plant Muncher A
	.byte $00 | $14, $24, $01; Piranha Plant Muncher B
	.byte $00 | $14, $25, $01; Piranha Plant Muncher B
	.byte $00 | $11, $26, $00; Piranha Plant Muncher A
	.byte $00 | $11, $27, $00; Piranha Plant Muncher A
	.byte $40 | $19, $38, $27; Leftward Pipe (CAN'T go in)
	.byte $20 | $15, $31, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $13, $33, $A4; Downward Pipe (CAN'T go down)
	.byte $20 | $14, $3A, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $12, $3C, $A5; Downward Pipe (CAN'T go down)
	.byte $20 | $0B, $3E, $AC; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $37, $92; Downward Pipe (CAN go down)
	.byte $20 | $17, $31, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $17, $33, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $17, $37, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $17, $3A, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $17, $3C, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $17, $3E, $D1; Upward Pipe (CAN'T go up)
	; Pointer on screen $03
	.byte $E0 | $03, $00 | $02, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Piranha_Plant__1_W7_objects:
	.byte $A4, $0A, $14; Green Venus Fire Trap (upward)
	.byte $A4, $12, $14; Green Venus Fire Trap (upward)
	.byte $A0, $1E, $15; Green Piranha Plant (upward)
	.byte $A5, $2C, $12; Green Venus Fire Trap (downward)
	.byte $A2, $31, $15; Red Piranha Plant (upward)
	.byte $A4, $33, $13; Green Venus Fire Trap (upward)
	.byte $A4, $3A, $14; Green Venus Fire Trap (upward)
	.byte $FF
; Pipe_1_End_2_W7
; Object Set 14
Pipe_1_End_2_W7_generators:
Pipe_1_End_2_W7_header:
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
Pipe_1_End_2_W7_objects:
	.byte $25, $02, $04; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Pipe_2_End_1_W7
; Object Set 14
Pipe_2_End_1_W7_generators:
Pipe_2_End_1_W7_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_0F0; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $19, $00, $51, $0F; Hilly Fill
	.byte $80 | $13, $00, $55, $00; Hilly Fill
	.byte $60 | $0F, $00, $E3; Hilly Wall - Right Side
	.byte $80 | $13, $01, $85, $01; Flat Land - Hilly
	.byte $60 | $13, $03, $55; 30 Degree Hill - Down/Right
	.byte $00 | $0F, $0F, $E9; Hilly Wall - Left Side
	.byte $80 | $0F, $03, $50, $09; Hilly Fill
	.byte $00 | $0F, $03, $E0; Hilly Wall - Left Side
	.byte $80 | $0F, $0B, $B4, $01; Ceiling - Hilly
	.byte $60 | $0F, $0C, $E3; Hilly Wall - Right Side
	.byte $00 | $13, $0C, $0A; Lower Right Hill Corner
	.byte $60 | $10, $03, $73; 30 Degree Hill - Up/Left
	.byte $20 | $0F, $01, $C1; Upward Pipe (CAN go up)
	.byte $20 | $0F, $0D, $C6; Upward Pipe (CAN go up)
	.byte $FF
Pipe_2_End_1_W7_objects:
	.byte $25, $02, $06; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_4_Outside_Area_W7
; Object Set 1
Level_4_Outside_Area_W7_generators:
Level_4_Outside_Area_W7_header:
	.byte $4D; Next Level
	.byte LEVEL1_SIZE_05 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_06; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $1A, $00, $C0, $4F; Flat Ground
	.byte $00 | $13, $07, $E2; Background Clouds
	.byte $00 | $14, $02, $E2; Background Clouds
	.byte $00 | $14, $0B, $E2; Background Clouds
	.byte $00 | $19, $01, $92; Background Bushes
	.byte $00 | $16, $04, $00; Background Hills A
	.byte $20 | $18, $0B, $E2; Rightward Pipe (CAN go in)
	.byte $20 | $17, $0D, $92; Downward Pipe (CAN go down)
	.byte $40 | $00, $00, $B0, $23; Blue X-Blocks
	.byte $40 | $0C, $0F, $BD, $08; Blue X-Blocks
	.byte $40 | $0B, $13, $B0, $01; Blue X-Blocks
	.byte $40 | $10, $18, $B0, $00; Blue X-Blocks
	.byte $40 | $11, $18, $B8, $01; Blue X-Blocks
	.byte $40 | $13, $1A, $B6, $01; Blue X-Blocks
	.byte $40 | $15, $1C, $B4, $01; Blue X-Blocks
	.byte $40 | $00, $24, $BF, $0B; Blue X-Blocks
	.byte $40 | $10, $24, $B9, $0B; Blue X-Blocks
	.byte $20 | $12, $21, $0B; Brick with 1-up
	.byte $20 | $16, $21, $0B; Brick with 1-up
	.byte $00 | $11, $31, $E2; Background Clouds
	.byte $00 | $13, $37, $E3; Background Clouds
	.byte $00 | $15, $34, $E2; Background Clouds
	.byte $40 | $18, $30, $22; Leftward Pipe (CAN'T go in)
	.byte $00 | $19, $34, $91; Background Bushes
	.byte $00 | $16, $36, $00; Background Hills A
	.byte $40 | $00, $3C, $09; Level Ending
	; Pointer on screen $00
	.byte $E0 | $00, $50 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_4_Outside_Area_W7_objects:
	.byte $41, $48, $15; Goal Card
	.byte $FF
; Level_2_W7
; Object Set 9
Level_2_W7_generators:
Level_2_W7_header:
	.byte $27; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_070; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $09; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $40 | $16, $06, $82, $08; Water (still)
	.byte $40 | $13, $0F, $87, $36; Water (still)
	.byte $00 | $09, $00, $90; X-Large sandstone blocks
	.byte $00 | $0D, $00, $92; X-Large sandstone blocks
	.byte $00 | $11, $08, $90; X-Large sandstone blocks
	.byte $00 | $15, $0C, $70; Medium sandstone blocks
	.byte $00 | $16, $00, $80; Large sandstone blocks
	.byte $00 | $0B, $08, $74; Medium sandstone blocks
	.byte $00 | $17, $06, $70; Medium sandstone blocks
	.byte $00 | $19, $00, $7A; Medium sandstone blocks
	.byte $00 | $11, $00, $60; Small sandstone blocks
	.byte $00 | $12, $00, $60; Small sandstone blocks
	.byte $00 | $13, $00, $60; Small sandstone blocks
	.byte $00 | $14, $00, $60; Small sandstone blocks
	.byte $00 | $15, $00, $60; Small sandstone blocks
	.byte $20 | $11, $02, $85; Coins
	.byte $20 | $12, $02, $85; Coins
	.byte $20 | $13, $02, $85; Coins
	.byte $40 | $15, $03, $08; P-Switch
	.byte $00 | $03, $08, $0A; Oval Background Cloud
	.byte $00 | $09, $10, $70; Medium sandstone blocks
	.byte $00 | $0D, $18, $70; Medium sandstone blocks
	.byte $00 | $0F, $18, $70; Medium sandstone blocks
	.byte $00 | $0D, $1E, $70; Medium sandstone blocks
	.byte $00 | $0F, $1E, $73; Medium sandstone blocks
	.byte $00 | $13, $14, $60; Small sandstone blocks
	.byte $00 | $14, $14, $60; Small sandstone blocks
	.byte $00 | $17, $14, $60; Small sandstone blocks
	.byte $00 | $18, $14, $60; Small sandstone blocks
	.byte $20 | $09, $17, $00; '?' with flower
	.byte $20 | $09, $18, $20; '?' blocks with single coins
	.byte $20 | $11, $10, $17; Bricks
	.byte $20 | $12, $10, $17; Bricks
	.byte $20 | $07, $11, $A1; Downward Pipe (CAN'T go down)
	.byte $40 | $06, $11, $E1; White Turtle Bricks
	.byte $40 | $09, $1C, $F8; Double-Ended Vertical Pipe
	.byte $00 | $0B, $1E, $70; Medium sandstone blocks
	.byte $40 | $0A, $17, $E1; White Turtle Bricks
	.byte $00 | $03, $18, $0A; Oval Background Cloud
	.byte $00 | $0B, $22, $90; X-Large sandstone blocks
	.byte $00 | $09, $22, $72; Medium sandstone blocks
	.byte $00 | $03, $2A, $70; Medium sandstone blocks
	.byte $00 | $05, $2A, $70; Medium sandstone blocks
	.byte $00 | $07, $2A, $70; Medium sandstone blocks
	.byte $00 | $0B, $2A, $70; Medium sandstone blocks
	.byte $00 | $0D, $2A, $70; Medium sandstone blocks
	.byte $00 | $11, $20, $64; Small sandstone blocks
	.byte $00 | $12, $20, $64; Small sandstone blocks
	.byte $00 | $13, $20, $60; Small sandstone blocks
	.byte $00 | $16, $20, $60; Small sandstone blocks
	.byte $00 | $17, $20, $60; Small sandstone blocks
	.byte $00 | $18, $20, $60; Small sandstone blocks
	.byte $00 | $13, $28, $60; Small sandstone blocks
	.byte $00 | $14, $28, $60; Small sandstone blocks
	.byte $00 | $15, $28, $60; Small sandstone blocks
	.byte $00 | $18, $28, $60; Small sandstone blocks
	.byte $20 | $11, $22, $15; Bricks
	.byte $20 | $12, $22, $15; Bricks
	.byte $20 | $07, $22, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $05, $24, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $07, $26, $A1; Downward Pipe (CAN'T go down)
	.byte $40 | $0A, $2E, $F9; Double-Ended Vertical Pipe
	.byte $00 | $03, $30, $90; X-Large sandstone blocks
	.byte $00 | $07, $30, $90; X-Large sandstone blocks
	.byte $00 | $0B, $30, $90; X-Large sandstone blocks
	.byte $00 | $0F, $30, $71; Medium sandstone blocks
	.byte $00 | $0F, $3A, $71; Medium sandstone blocks
	.byte $00 | $19, $3A, $7F; Medium sandstone blocks
	.byte $00 | $0B, $3A, $90; X-Large sandstone blocks
	.byte $00 | $19, $30, $71; Medium sandstone blocks
	.byte $40 | $04, $38, $FF; Double-Ended Vertical Pipe
	.byte $20 | $09, $3A, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $07, $3C, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $05, $3E, $A5; Downward Pipe (CAN'T go down)
	.byte $20 | $02, $37, $40; Wooden blocks
	.byte $00 | $0B, $44, $90; X-Large sandstone blocks
	.byte $00 | $0F, $44, $76; Medium sandstone blocks
	.byte $00 | $11, $46, $70; Medium sandstone blocks
	.byte $00 | $13, $46, $70; Medium sandstone blocks
	.byte $00 | $15, $46, $71; Medium sandstone blocks
	.byte $00 | $17, $46, $70; Medium sandstone blocks
	.byte $20 | $03, $40, $A7; Downward Pipe (CAN'T go down)
	.byte $40 | $09, $42, $F9; Double-Ended Vertical Pipe
	.byte $40 | $09, $4C, $F9; Double-Ended Vertical Pipe
	.byte $40 | $03, $4E, $F8; Double-Ended Vertical Pipe
	.byte $40 | $0B, $4E, $F9; Double-Ended Vertical Pipe
	.byte $40 | $05, $42, $00; Invisible Note Block
	.byte $40 | $05, $43, $00; Invisible Note Block
	.byte $40 | $05, $44, $00; Invisible Note Block
	.byte $40 | $05, $45, $00; Invisible Note Block
	.byte $40 | $05, $46, $00; Invisible Note Block
	.byte $40 | $05, $47, $00; Invisible Note Block
	.byte $40 | $05, $48, $00; Invisible Note Block
	.byte $40 | $05, $49, $00; Invisible Note Block
	.byte $40 | $05, $4A, $00; Invisible Note Block
	.byte $40 | $05, $4B, $00; Invisible Note Block
	.byte $40 | $05, $4C, $00; Invisible Note Block
	.byte $40 | $05, $4D, $00; Invisible Note Block
	.byte $20 | $00, $48, $0F; Invisible 1-up
	.byte $20 | $12, $4A, $01; '?' with leaf
	.byte $00 | $02, $44, $0A; Oval Background Cloud
	.byte $00 | $0B, $50, $92; X-Large sandstone blocks
	.byte $00 | $14, $5E, $73; Medium sandstone blocks
	.byte $20 | $08, $50, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $06, $52, $A4; Downward Pipe (CAN'T go down)
	.byte $20 | $09, $54, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $08, $56, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $06, $58, $A4; Downward Pipe (CAN'T go down)
	.byte $20 | $03, $5A, $A7; Downward Pipe (CAN'T go down)
	.byte $20 | $07, $5C, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $05, $5E, $A5; Downward Pipe (CAN'T go down)
	.byte $20 | $18, $59, $40; Wooden blocks
	.byte $00 | $03, $56, $0A; Oval Background Cloud
	.byte $00 | $0F, $62, $70; Medium sandstone blocks
	.byte $00 | $0B, $68, $80; Large sandstone blocks
	.byte $00 | $0F, $6E, $70; Medium sandstone blocks
	.byte $00 | $11, $6E, $70; Medium sandstone blocks
	.byte $00 | $13, $6E, $70; Medium sandstone blocks
	.byte $00 | $15, $6E, $70; Medium sandstone blocks
	.byte $00 | $17, $6E, $70; Medium sandstone blocks
	.byte $20 | $09, $60, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $07, $62, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $04, $64, $A6; Downward Pipe (CAN'T go down)
	.byte $20 | $05, $66, $A5; Downward Pipe (CAN'T go down)
	.byte $20 | $07, $68, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $08, $6A, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $07, $6E, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $0F, $60, $D2; Upward Pipe (CAN'T go up)
	.byte $20 | $0F, $66, $D2; Upward Pipe (CAN'T go up)
	.byte $20 | $09, $6C, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $11, $6A, $00; '?' with flower
	.byte $00 | $0B, $6E, $90; X-Large sandstone blocks
	.byte $00 | $01, $6E, $0A; Oval Background Cloud
	.byte $00 | $0B, $78, $90; X-Large sandstone blocks
	.byte $00 | $0F, $7A, $80; Large sandstone blocks
	.byte $00 | $12, $7A, $80; Large sandstone blocks
	.byte $00 | $15, $7A, $80; Large sandstone blocks
	.byte $00 | $18, $7A, $80; Large sandstone blocks
	.byte $00 | $00, $7E, $60; Small sandstone blocks
	.byte $00 | $01, $7E, $60; Small sandstone blocks
	.byte $00 | $02, $7E, $60; Small sandstone blocks
	.byte $00 | $03, $7E, $60; Small sandstone blocks
	.byte $00 | $04, $7E, $60; Small sandstone blocks
	.byte $00 | $05, $7E, $60; Small sandstone blocks
	.byte $00 | $06, $7E, $60; Small sandstone blocks
	.byte $00 | $07, $7E, $60; Small sandstone blocks
	.byte $00 | $08, $7E, $60; Small sandstone blocks
	.byte $00 | $09, $7E, $60; Small sandstone blocks
	.byte $00 | $0A, $7E, $60; Small sandstone blocks
	.byte $20 | $05, $70, $A5; Downward Pipe (CAN'T go down)
	.byte $20 | $04, $72, $A6; Downward Pipe (CAN'T go down)
	.byte $20 | $07, $74, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $07, $78, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $05, $7A, $A5; Downward Pipe (CAN'T go down)
	.byte $20 | $07, $7C, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $17, $78, $91; Downward Pipe (CAN go down)
	.byte $40 | $09, $76, $F7; Double-Ended Vertical Pipe
	.byte $00 | $02, $7A, $0A; Oval Background Cloud
	; Pointer on screen $07
	.byte $E0 | $07, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_2_W7_objects:
	.byte $D4, $00, $2E; White Mushroom House (X pos must be uneven, Y pos=amount of coins required)
	.byte $39, $0E, $0A; Walking Nipper Plant
	.byte $33, $1D, $08; Nipper Plant
	.byte $33, $23, $06; Nipper Plant
	.byte $A6, $24, $05; Red Venus Fire Trap (upward)
	.byte $66, $2E, $13; Downward Current
	.byte $39, $36, $02; Walking Nipper Plant
	.byte $A6, $3C, $07; Red Venus Fire Trap (upward)
	.byte $6E, $49, $08; Green Koopa Paratroopa (bounces)
	.byte $39, $55, $18; Walking Nipper Plant
	.byte $39, $58, $18; Walking Nipper Plant
	.byte $A6, $5A, $03; Red Venus Fire Trap (upward)
	.byte $A6, $60, $09; Red Venus Fire Trap (upward)
	.byte $A6, $64, $04; Red Venus Fire Trap (upward)
	.byte $A1, $66, $11; Green Piranha Plant (downward)
	.byte $A6, $6A, $08; Red Venus Fire Trap (upward)
	.byte $A2, $6E, $07; Red Piranha Plant (upward)
	.byte $39, $71, $04; Walking Nipper Plant
	.byte $A6, $72, $04; Red Venus Fire Trap (upward)
	.byte $A6, $78, $07; Red Venus Fire Trap (upward)
	.byte $FF
; Pipe_3_End_1_W7
; Object Set 14
Pipe_3_End_1_W7_generators:
Pipe_3_End_1_W7_header:
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
Pipe_3_End_1_W7_objects:
	.byte $25, $02, $07; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Pipe_4_End_1_W7
; Object Set 14
Pipe_4_End_1_W7_generators:
Pipe_4_End_1_W7_header:
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
Pipe_4_End_1_W7_objects:
	.byte $25, $02, $08; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_3_W7
; Object Set 3
Level_3_W7_generators:
Level_3_W7_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_13 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $13; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $16, $00, $84, $04; Flat Land - Hilly
	.byte $80 | $16, $05, $54, $02; Hilly Wall
	.byte $00 | $13, $07, $62; 45 Degree Hill - Down/Left
	.byte $80 | $13, $08, $87, $07; Flat Land - Hilly
	.byte $80 | $15, $01, $D1; Small Background Hills
	.byte $40 | $10, $08, $0B; Background Hills B
	.byte $80 | $12, $0D, $D2; Small Background Hills
	.byte $20 | $12, $05, $02; '?' with star
	.byte $80 | $1A, $10, $50, $0D; Hilly Wall
	.byte $60 | $13, $10, $56; 30 Degree Hill - Down/Right
	.byte $80 | $1A, $1E, $80, $09; Flat Land - Hilly
	.byte $A0 | $10, $15, $32; Background Clouds
	.byte $40 | $16, $1F, $0A; Background Hills A
	.byte $00 | $1A, $28, $04; Upper Right Hill Corner - Hilly
	.byte $80 | $13, $2C, $87, $03; Flat Land - Hilly
	.byte $00 | $13, $2C, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $14, $2C, $E6; Hilly Wall - Left Side
	.byte $80 | $19, $26, $D1; Small Background Hills
	.byte $80 | $12, $2D, $D2; Small Background Hills
	.byte $20 | $13, $27, $21; '?' blocks with single coins
	.byte $20 | $16, $26, $21; '?' blocks with single coins
	.byte $20 | $16, $26, $03; '?' with continuous star
	.byte $80 | $1A, $30, $50, $0D; Hilly Wall
	.byte $60 | $13, $30, $56; 30 Degree Hill - Down/Right
	.byte $80 | $1A, $3E, $80, $07; Flat Land - Hilly
	.byte $A0 | $10, $37, $32; Background Clouds
	.byte $00 | $1A, $45, $04; Upper Right Hill Corner - Hilly
	.byte $80 | $13, $49, $87, $03; Flat Land - Hilly
	.byte $80 | $16, $4D, $54, $05; Hilly Wall
	.byte $60 | $13, $4D, $52; 30 Degree Hill - Down/Right
	.byte $00 | $14, $49, $E6; Hilly Wall - Left Side
	.byte $00 | $13, $49, $01; Upper Left Hill Corner - Hilly
	.byte $80 | $19, $41, $D1; Small Background Hills
	.byte $80 | $12, $49, $D2; Small Background Hills
	.byte $20 | $13, $44, $21; '?' blocks with single coins
	.byte $20 | $16, $43, $21; '?' blocks with single coins
	.byte $20 | $16, $43, $03; '?' with continuous star
	.byte $60 | $16, $52, $E4; Hilly Wall - Right Side
	.byte $00 | $17, $54, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $18, $54, $E2; Hilly Wall - Left Side
	.byte $80 | $1A, $55, $50, $07; Hilly Wall
	.byte $60 | $17, $55, $52; 30 Degree Hill - Down/Right
	.byte $80 | $1A, $5B, $80, $00; Flat Land - Hilly
	.byte $00 | $19, $5C, $60; 45 Degree Hill - Down/Left
	.byte $00 | $19, $5D, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $1A, $5D, $E0; Hilly Wall - Right Side
	.byte $80 | $1A, $64, $80, $09; Flat Land - Hilly
	.byte $00 | $1A, $64, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $1A, $6D, $04; Upper Right Hill Corner - Hilly
	.byte $40 | $17, $65, $0B; Background Hills B
	.byte $80 | $19, $6A, $D1; Small Background Hills
	.byte $20 | $13, $65, $00; '?' with flower
	.byte $20 | $16, $65, $09; Brick with Continuous Star
	.byte $20 | $19, $60, $A1; Downward Pipe (CAN'T go down)
	.byte $80 | $1A, $70, $80, $0F; Flat Land - Hilly
	.byte $00 | $1A, $70, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $1A, $7F, $04; Upper Right Hill Corner - Hilly
	.byte $40 | $17, $71, $0B; Background Hills B
	.byte $80 | $19, $77, $D5; Small Background Hills
	.byte $40 | $15, $74, $53; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $15, $79, $53; Silver Coins (appear when you hit a P-Switch)
	.byte $20 | $17, $78, $0D; Brick with P-Switch
	.byte $A0 | $10, $70, $32; Background Clouds
	.byte $80 | $1A, $82, $80, $01; Flat Land - Hilly
	.byte $00 | $1A, $82, $01; Upper Left Hill Corner - Hilly
	.byte $80 | $16, $84, $84, $03; Flat Land - Hilly
	.byte $00 | $16, $84, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $17, $84, $E2; Hilly Wall - Left Side
	.byte $60 | $16, $86, $50; 30 Degree Hill - Down/Right
	.byte $60 | $17, $87, $E3; Hilly Wall - Right Side
	.byte $00 | $19, $89, $E1; Hilly Wall - Left Side
	.byte $00 | $18, $89, $01; Upper Left Hill Corner - Hilly
	.byte $80 | $1A, $8A, $50, $03; Hilly Wall
	.byte $60 | $18, $8A, $51; 30 Degree Hill - Down/Right
	.byte $80 | $1A, $8E, $80, $0A; Flat Land - Hilly
	.byte $A0 | $10, $8B, $32; Background Clouds
	.byte $80 | $1A, $99, $50, $04; Hilly Wall
	.byte $00 | $18, $9D, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $19, $9D, $E1; Hilly Wall - Right Side
	.byte $60 | $18, $9B, $61; 30 Degree Hill - Down/Left
	.byte $80 | $17, $9F, $53, $03; Hilly Wall
	.byte $00 | $17, $9F, $E3; Hilly Wall - Left Side
	.byte $60 | $16, $9F, $60; 30 Degree Hill - Down/Left
	.byte $80 | $19, $8F, $D1; Small Background Hills
	.byte $20 | $17, $92, $F1; Rightward Pipe (CAN'T go in)
	.byte $40 | $17, $93, $21; Leftward Pipe (CAN'T go in)
	.byte $20 | $19, $92, $42; Wooden blocks
	.byte $20 | $15, $90, $09; Brick with Continuous Star
	.byte $20 | $15, $96, $09; Brick with Continuous Star
	.byte $80 | $16, $A1, $84, $00; Flat Land - Hilly
	.byte $00 | $16, $A2, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $17, $A2, $E3; Hilly Wall - Right Side
	.byte $00 | $17, $A4, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $17, $A5, $04; Upper Right Hill Corner - Hilly
	.byte $00 | $18, $A4, $E2; Hilly Wall - Left Side
	.byte $60 | $18, $A5, $E2; Hilly Wall - Right Side
	.byte $00 | $18, $A7, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $18, $A8, $04; Upper Right Hill Corner - Hilly
	.byte $00 | $19, $A7, $E1; Hilly Wall - Left Side
	.byte $60 | $19, $A8, $E1; Hilly Wall - Right Side
	.byte $00 | $19, $AA, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $19, $AB, $04; Upper Right Hill Corner - Hilly
	.byte $00 | $1A, $AA, $E0; Hilly Wall - Left Side
	.byte $60 | $1A, $AB, $E0; Hilly Wall - Right Side
	.byte $80 | $1A, $AE, $80, $21; Flat Land - Hilly
	.byte $00 | $1A, $AE, $01; Upper Left Hill Corner - Hilly
	.byte $80 | $19, $B0, $D2; Small Background Hills
	.byte $40 | $00, $B8, $09; Level Ending
	.byte $FF
Level_3_W7_objects:
	.byte $6C, $13, $13; Green Koopa Troopa
	.byte $6C, $17, $15; Green Koopa Troopa
	.byte $6C, $1A, $16; Green Koopa Troopa
	.byte $6C, $1E, $19; Green Koopa Troopa
	.byte $6C, $33, $13; Green Koopa Troopa
	.byte $6C, $37, $15; Green Koopa Troopa
	.byte $6E, $3C, $17; Green Koopa Paratroopa (bounces)
	.byte $6E, $3F, $18; Green Koopa Paratroopa (bounces)
	.byte $71, $51, $14; Spiny
	.byte $71, $57, $17; Spiny
	.byte $71, $59, $18; Spiny
	.byte $A6, $60, $19; Red Venus Fire Trap (upward)
	.byte $83, $65, $12; Lakitu
	.byte $C0, $92, $18; Infinite Goombas (leftward)
	.byte $C1, $94, $18; Infinite Goombas (rightward)
	.byte $6E, $B3, $17; Green Koopa Paratroopa (bounces)
	.byte $6E, $B7, $17; Green Koopa Paratroopa (bounces)
	.byte $41, $C8, $15; Goal Card
	.byte $FF
; Level_6_Outside_Area_W7
; Object Set 1
Level_6_Outside_Area_W7_generators:
Level_6_Outside_Area_W7_header:
	.byte $4E; Next Level
	.byte LEVEL1_SIZE_05 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_08; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $20 | $15, $0A, $F3; Rightward Pipe (CAN'T go in)
	.byte $40 | $15, $0B, $23; Leftward Pipe (CAN'T go in)
	.byte $40 | $17, $00, $28; Leftward Pipe (CAN'T go in)
	.byte $40 | $17, $09, $2B; Leftward Pipe (CAN'T go in)
	.byte $20 | $19, $00, $FE; Rightward Pipe (CAN'T go in)
	.byte $20 | $19, $0F, $F4; Rightward Pipe (CAN'T go in)
	.byte $40 | $16, $01, $B0, $02; Blue X-Blocks
	.byte $00 | $11, $03, $E2; Background Clouds
	.byte $00 | $12, $08, $E2; Background Clouds
	.byte $00 | $10, $0E, $E2; Background Clouds
	.byte $40 | $00, $14, $BF, $0D; Blue X-Blocks
	.byte $40 | $10, $14, $BA, $0D; Blue X-Blocks
	.byte $00 | $15, $14, $04; Door (CAN go in)
	.byte $40 | $18, $22, $27; Leftward Pipe (CAN'T go in)
	.byte $40 | $18, $2A, $2C; Leftward Pipe (CAN'T go in)
	.byte $40 | $16, $22, $2C; Leftward Pipe (CAN'T go in)
	.byte $40 | $14, $22, $21; Leftward Pipe (CAN'T go in)
	.byte $00 | $1A, $22, $C0, $30; Flat Ground
	.byte $00 | $14, $29, $E2; Background Clouds
	.byte $00 | $16, $32, $E2; Background Clouds
	.byte $40 | $00, $39, $09; Level Ending
	; Pointer on screen $01
	.byte $E0 | $01, $F0 | $08, 39; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_6_Outside_Area_W7_objects:
	.byte $41, $48, $15; Goal Card
	.byte $FF
; Level_7_Beginning_End_W7
; Object Set 1
Level_7_Beginning_End_W7_generators:
Level_7_Beginning_End_W7_header:
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
Level_7_Beginning_End_W7_objects:
	.byte $41, $38, $15; Goal Card
	.byte $FF
; Pipe_7_End_2_W7
; Object Set 14
Pipe_7_End_2_W7_generators:
Pipe_7_End_2_W7_header:
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
Pipe_7_End_2_W7_objects:
	.byte $25, $02, $0B; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Default_Level_257
; Object Set 14
Default_Level_257_generators:
Default_Level_257_header:
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
Default_Level_257_objects:
	.byte $25, $02, $0A; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Pipe_4_End_2_W7
; Object Set 14
Pipe_4_End_2_W7_generators:
Pipe_4_End_2_W7_header:
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
Pipe_4_End_2_W7_objects:
	.byte $25, $02, $08; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Pipe_7_End_1_W7
; Object Set 14
Pipe_7_End_1_W7_generators:
Pipe_7_End_1_W7_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
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
Pipe_7_End_1_W7_objects:
	.byte $25, $02, $0B; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_5_Outside_Area_W7
; Object Set 1
Level_5_Outside_Area_W7_generators:
Level_5_Outside_Area_W7_header:
	.byte $51; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $1A, $00, $C0, $3F; Flat Ground
	.byte $40 | $00, $00, $B0, $0F; Blue X-Blocks
	.byte $20 | $16, $08, $93; Downward Pipe (CAN go down)
	.byte $20 | $18, $05, $E2; Rightward Pipe (CAN go in)
	.byte $40 | $18, $0A, $12; Leftward Pipe (CAN go in)
	.byte $00 | $19, $02, $91; Background Bushes
	.byte $00 | $19, $0E, $91; Background Bushes
	.byte $00 | $12, $08, $E2; Background Clouds
	.byte $00 | $13, $02, $E2; Background Clouds
	.byte $00 | $15, $0B, $E2; Background Clouds
	.byte $40 | $00, $10, $BF, $0F; Blue X-Blocks
	.byte $40 | $10, $10, $B9, $0F; Blue X-Blocks
	.byte $00 | $19, $21, $95; Background Bushes
	.byte $20 | $17, $24, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $17, $27, $01; Background Hills B
	.byte $00 | $11, $21, $E2; Background Clouds
	.byte $00 | $12, $28, $E2; Background Clouds
	.byte $00 | $14, $25, $E2; Background Clouds
	.byte $40 | $00, $2C, $09; Level Ending
	; Pointer on screen $00
	.byte $E0 | $00, $50 | $02, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_5_Outside_Area_W7_objects:
	.byte $41, $38, $15; Goal Card
	.byte $FF
; Pipe_8_End_2_W7
; Object Set 14
Pipe_8_End_2_W7_generators:
Pipe_8_End_2_W7_header:
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
Pipe_8_End_2_W7_objects:
	.byte $25, $02, $09; Changes exit location on map (works on warp pipe levels)
	.byte $FF