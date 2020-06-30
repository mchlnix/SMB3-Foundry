; Bank 2

; Pipe_1_End_1_W3
; Object Set 14
Pipe_1_End_1_W3_generators:
Pipe_1_End_1_W3_header:
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
Pipe_1_End_1_W3_objects:
	.byte $25, $02, $12; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Pipe_2_End_1_W3
; Object Set 14
Pipe_2_End_1_W3_generators:
Pipe_2_End_1_W3_header:
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
Pipe_2_End_1_W3_objects:
	.byte $25, $02, $13; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_6_W3
; Object Set 4
Level_6_W3_generators:
Level_6_W3_header:
	.byte $29; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_04; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $04; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $16, $00, $2A; Wooden block platform
	.byte $00 | $15, $02, $43; Background Bushes
	.byte $00 | $18, $01, $04; Wooden Background Pole
	.byte $00 | $18, $09, $04; Wooden Background Pole
	.byte $00 | $14, $07, $01; Large Swirly Background Cloud
	.byte $00 | $17, $0C, $00; Small Swirly Background Cloud
	.byte $00 | $11, $04, $01; Large Swirly Background Cloud
	.byte $00 | $12, $0D, $00; Small Swirly Background Cloud
	.byte $60 | $14, $0E, $41; Donut Blocks
	.byte $60 | $16, $11, $43; Donut Blocks
	.byte $20 | $11, $12, $00; '?' with flower
	.byte $00 | $13, $15, $10, $03; Wooden platform
	.byte $00 | $18, $1A, $01; Large Swirly Background Cloud
	.byte $00 | $11, $1E, $01; Large Swirly Background Cloud
	.byte $00 | $14, $11, $01; Large Swirly Background Cloud
	.byte $00 | $15, $17, $00; Small Swirly Background Cloud
	.byte $00 | $13, $23, $10, $02; Wooden platform
	.byte $00 | $13, $27, $10, $06; Wooden platform
	.byte $00 | $12, $23, $41; Background Bushes
	.byte $00 | $16, $22, $00; Small Swirly Background Cloud
	.byte $00 | $19, $24, $10, $01; Wooden platform
	.byte $00 | $19, $27, $10, $05; Wooden platform
	.byte $00 | $15, $2E, $01; Large Swirly Background Cloud
	.byte $20 | $18, $29, $0A; Multi-Coin Brick
	.byte $60 | $16, $2F, $40; Donut Blocks
	.byte $60 | $18, $2D, $40; Donut Blocks
	.byte $60 | $13, $26, $40; Donut Blocks
	.byte $00 | $15, $28, $01; Large Swirly Background Cloud
	.byte $20 | $15, $2A, $82; Coins
	.byte $00 | $12, $28, $44; Background Bushes
	.byte $60 | $14, $20, $41; Donut Blocks
	.byte $00 | $13, $30, $10, $05; Wooden platform
	.byte $00 | $13, $37, $10, $05; Wooden platform
	.byte $00 | $14, $3E, $10, $03; Wooden platform
	.byte $00 | $19, $37, $10, $0A; Wooden platform
	.byte $60 | $13, $36, $40; Donut Blocks
	.byte $00 | $18, $39, $43; Background Bushes
	.byte $40 | $12, $36, $E0; White Turtle Bricks
	.byte $20 | $13, $3D, $10; Bricks
	.byte $20 | $14, $30, $40; Wooden blocks
	.byte $20 | $15, $30, $40; Wooden blocks
	.byte $20 | $16, $30, $40; Wooden blocks
	.byte $20 | $18, $3D, $07; Brick with Leaf
	.byte $20 | $10, $39, $82; Coins
	.byte $20 | $16, $39, $82; Coins
	.byte $00 | $10, $3D, $01; Large Swirly Background Cloud
	.byte $00 | $17, $31, $00; Small Swirly Background Cloud
	.byte $20 | $13, $41, $30; Bricks with single coins
	.byte $20 | $14, $49, $30; Bricks with single coins
	.byte $00 | $15, $47, $10, $02; Wooden platform
	.byte $00 | $12, $46, $01; Large Swirly Background Cloud
	.byte $00 | $18, $4D, $01; Large Swirly Background Cloud
	.byte $20 | $14, $55, $30; Bricks with single coins
	.byte $00 | $15, $50, $10, $05; Wooden platform
	.byte $00 | $14, $51, $42; Background Bushes
	.byte $00 | $1A, $54, $00; Small Swirly Background Cloud
	.byte $00 | $17, $58, $01; Large Swirly Background Cloud
	.byte $60 | $19, $5C, $41; Donut Blocks
	.byte $00 | $15, $5E, $10, $04; Wooden platform
	.byte $40 | $19, $5E, $E2; White Turtle Bricks
	.byte $00 | $12, $5F, $01; Large Swirly Background Cloud
	.byte $00 | $15, $64, $10, $01; Wooden platform
	.byte $00 | $15, $6A, $10, $04; Wooden platform
	.byte $00 | $19, $68, $10, $07; Wooden platform
	.byte $00 | $1A, $60, $10, $06; Wooden platform
	.byte $20 | $15, $63, $0B; Brick with 1-up
	.byte $20 | $14, $65, $10; Bricks
	.byte $20 | $15, $66, $13; Bricks
	.byte $20 | $16, $66, $13; Bricks
	.byte $20 | $19, $65, $0D; Brick with P-Switch
	.byte $20 | $19, $66, $11; Bricks
	.byte $00 | $14, $6E, $00; Small Swirly Background Cloud
	.byte $20 | $12, $72, $82; Coins
	.byte $60 | $15, $72, $42; Donut Blocks
	.byte $00 | $18, $77, $01; Large Swirly Background Cloud
	.byte $20 | $17, $7B, $93; Downward Pipe (CAN go down)
	.byte $00 | $14, $7E, $01; Large Swirly Background Cloud
	; Pointer on screen $07
	.byte $E0 | $07, $40 | $02, 144; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_6_W3_objects:
	.byte $D3, $00, $00; Autoscrolling
	.byte $93, $1D, $14; Spinning Platform (periodical counterclockwise)
	.byte $6D, $29, $12; Red Koopa Troopa
	.byte $6D, $3B, $12; Red Koopa Troopa
	.byte $6D, $3C, $18; Red Koopa Troopa
	.byte $6F, $44, $14; Red Koopa Paratroopa
	.byte $6D, $54, $14; Red Koopa Troopa
	.byte $6E, $6E, $14; Green Koopa Paratroopa (bounces)
	.byte $6F, $76, $12; Red Koopa Paratroopa
	.byte $93, $7A, $13; Spinning Platform (periodical counterclockwise)
	.byte $D3, $00, $00; Autoscrolling
	.byte $FF
; Level_7_W3
; Object Set 1
Level_7_W3_generators:
Level_7_W3_header:
	.byte $2A; Next Level
	.byte LEVEL1_SIZE_10 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_13; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $14; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $1A, $00, $C0, $9F; Flat Ground
	.byte $00 | $02, $0B, $07; Small Background Cloud
	.byte $00 | $05, $05, $07; Small Background Cloud
	.byte $00 | $09, $02, $07; Small Background Cloud
	.byte $00 | $0A, $0A, $07; Small Background Cloud
	.byte $00 | $11, $0A, $07; Small Background Cloud
	.byte $00 | $10, $04, $E2; Background Clouds
	.byte $20 | $11, $02, $20; '?' Blocks with single coins
	.byte $00 | $12, $04, $02; Background Hills C
	.byte $00 | $12, $0E, $34; Green Block Platform (Extends to ground)
	.byte $40 | $16, $02, $05; Wooden Block with Leaf
	.byte $00 | $16, $0A, $31; Green Block Platform (Extends to ground)
	.byte $20 | $17, $02, $40; Wooden Blocks
	.byte $00 | $17, $0B, $35; Green Block Platform (Extends to ground)
	.byte $20 | $18, $02, $40; Wooden Blocks
	.byte $20 | $19, $02, $40; Wooden Blocks
	.byte $00 | $02, $1B, $07; Small Background Cloud
	.byte $00 | $05, $15, $07; Small Background Cloud
	.byte $00 | $09, $12, $07; Small Background Cloud
	.byte $00 | $0A, $1A, $07; Small Background Cloud
	.byte $00 | $0C, $17, $07; Small Background Cloud
	.byte $00 | $11, $1A, $07; Small Background Cloud
	.byte $00 | $11, $1D, $33; Green Block Platform (Extends to ground)
	.byte $00 | $17, $1F, $33; Green Block Platform (Extends to ground)
	.byte $00 | $19, $14, $91; Background Bushes
	.byte $00 | $19, $19, $92; Background Bushes
	.byte $00 | $1A, $15, $A3; Gap
	.byte $00 | $02, $2B, $07; Small Background Cloud
	.byte $00 | $05, $25, $07; Small Background Cloud
	.byte $00 | $09, $22, $07; Small Background Cloud
	.byte $00 | $0A, $2A, $07; Small Background Cloud
	.byte $00 | $0C, $27, $07; Small Background Cloud
	.byte $00 | $11, $2A, $07; Small Background Cloud
	.byte $00 | $10, $2D, $E2; Background Clouds
	.byte $20 | $13, $27, $14; Bricks
	.byte $20 | $13, $28, $0B; Brick with 1-up
	.byte $20 | $14, $27, $14; Bricks
	.byte $20 | $15, $27, $14; Bricks
	.byte $00 | $19, $25, $92; Background Bushes
	.byte $20 | $19, $29, $40; Wooden Blocks
	.byte $00 | $02, $3B, $07; Small Background Cloud
	.byte $00 | $05, $35, $07; Small Background Cloud
	.byte $00 | $09, $32, $07; Small Background Cloud
	.byte $00 | $0A, $3A, $07; Small Background Cloud
	.byte $00 | $0C, $37, $07; Small Background Cloud
	.byte $00 | $11, $3A, $07; Small Background Cloud
	.byte $00 | $15, $32, $33; Green Block Platform (Extends to ground)
	.byte $00 | $17, $30, $37; Green Block Platform (Extends to ground)
	.byte $20 | $19, $3D, $40; Wooden Blocks
	.byte $00 | $1A, $38, $A5; Gap
	.byte $00 | $08, $31, $BF; Cloud Platform
	.byte $00 | $08, $41, $B8; Cloud Platform
	.byte $00 | $02, $4B, $07; Small Background Cloud
	.byte $00 | $05, $45, $07; Small Background Cloud
	.byte $00 | $09, $42, $07; Small Background Cloud
	.byte $00 | $0A, $4A, $07; Small Background Cloud
	.byte $00 | $0C, $47, $07; Small Background Cloud
	.byte $00 | $11, $4A, $07; Small Background Cloud
	.byte $20 | $03, $4A, $81; Coins
	.byte $00 | $05, $4A, $B1; Cloud Platform
	.byte $20 | $06, $42, $87; Coins
	.byte $20 | $06, $4C, $81; Coins
	.byte $00 | $08, $4C, $B1; Cloud Platform
	.byte $20 | $16, $48, $A3; Downward Pipe (CAN'T go down)
	.byte $00 | $17, $40, $01; Background Hills B
	.byte $20 | $19, $43, $40; Wooden Blocks
	.byte $40 | $19, $4E, $04; Wooden Block with Flower
	.byte $00 | $1A, $43, $A3; Gap
	.byte $00 | $1A, $4B, $A3; Gap
	.byte $20 | $05, $41, $0D; Brick with P-Switch
	.byte $00 | $02, $5B, $07; Small Background Cloud
	.byte $00 | $09, $52, $07; Small Background Cloud
	.byte $00 | $0A, $5A, $07; Small Background Cloud
	.byte $00 | $11, $5A, $07; Small Background Cloud
	.byte $20 | $03, $57, $40; Wooden Blocks
	.byte $20 | $04, $54, $82; Coins
	.byte $20 | $05, $50, $81; Coins
	.byte $00 | $06, $54, $B2; Cloud Platform
	.byte $00 | $07, $50, $B1; Cloud Platform
	.byte $20 | $10, $57, $0C; Brick with Vine
	.byte $20 | $10, $5A, $30; Bricks with single coins
	.byte $20 | $11, $57, $13; Bricks
	.byte $20 | $11, $58, $31; Bricks with single coins
	.byte $00 | $11, $5E, $E2; Background Clouds
	.byte $00 | $13, $51, $31; Green Block Platform (Extends to ground)
	.byte $20 | $15, $55, $10; Bricks
	.byte $20 | $15, $5B, $10; Bricks
	.byte $20 | $16, $55, $16; Bricks
	.byte $00 | $17, $50, $33; Green Block Platform (Extends to ground)
	.byte $00 | $19, $57, $92; Background Bushes
	.byte $20 | $19, $5B, $40; Wooden Blocks
	.byte $00 | $1A, $5B, $A3; Gap
	.byte $00 | $02, $6B, $07; Small Background Cloud
	.byte $00 | $05, $65, $07; Small Background Cloud
	.byte $00 | $09, $62, $07; Small Background Cloud
	.byte $00 | $0A, $6A, $07; Small Background Cloud
	.byte $00 | $0C, $67, $07; Small Background Cloud
	.byte $00 | $11, $6A, $07; Small Background Cloud
	.byte $00 | $15, $63, $32; Green Block Platform (Extends to ground)
	.byte $20 | $16, $6C, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $17, $60, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $17, $65, $33; Green Block Platform (Extends to ground)
	.byte $00 | $0C, $61, $B6; Cloud Platform
	.byte $40 | $09, $64, $07; Red Invisible Note Block
	.byte $00 | $02, $7B, $07; Small Background Cloud
	.byte $00 | $05, $75, $07; Small Background Cloud
	.byte $00 | $09, $72, $07; Small Background Cloud
	.byte $00 | $0A, $7A, $07; Small Background Cloud
	.byte $00 | $0C, $77, $07; Small Background Cloud
	.byte $00 | $11, $7A, $07; Small Background Cloud
	.byte $00 | $10, $71, $E2; Background Clouds
	.byte $20 | $13, $7A, $40; Wooden Blocks
	.byte $20 | $13, $7E, $40; Wooden Blocks
	.byte $40 | $14, $7A, $B5, $04; Blue X-Blocks
	.byte $40 | $15, $76, $04; Wooden Block with Flower
	.byte $40 | $16, $76, $B3, $03; Blue X-Blocks
	.byte $20 | $17, $72, $40; Wooden Blocks
	.byte $40 | $18, $72, $B1, $03; Blue X-Blocks
	.byte $40 | $00, $88, $09; Level Ending
	; Pointer on screen $06
	.byte $E0 | $06, $70 | $07, 80; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_7_W3_objects:
	.byte $29, $0F, $16; Spike
	.byte $29, $12, $11; Spike
	.byte $29, $1E, $10; Spike
	.byte $29, $20, $16; Spike
	.byte $29, $31, $14; Spike
	.byte $29, $33, $16; Spike
	.byte $29, $3E, $19; Spike
	.byte $6C, $41, $18; Green Koopa Troopa
	.byte $29, $51, $19; Spike
	.byte $6C, $53, $18; Green Koopa Troopa
	.byte $29, $55, $19; Spike
	.byte $29, $59, $15; Spike
	.byte $A6, $60, $17; Red Venus Fire Trap (upward)
	.byte $29, $6A, $19; Spike
	.byte $A6, $6C, $16; Red Venus Fire Trap (upward)
	.byte $29, $75, $17; Spike
	.byte $29, $79, $15; Spike
	.byte $29, $7D, $13; Spike
	.byte $6E, $7E, $11; Green Koopa Paratroopa (bounces)
	.byte $41, $98, $15; Goal Card
	.byte $29, $98, $19; Spike
	.byte $FF
; Level_8_W3
; Object Set 14
Level_8_W3_generators:
Level_8_W3_header:
	.byte $2B; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $13; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $40 | $16, $00, $B2, $07; Blue X-Blocks
	.byte $40 | $12, $06, $B3, $01; Blue X-Blocks
	.byte $80 | $15, $02, $D2; Small Background Hills
	.byte $40 | $13, $0A, $0B; Background Hills B
	.byte $40 | $16, $0A, $B3, $03; Blue X-Blocks
	.byte $40 | $16, $0F, $B2, $06; Blue X-Blocks
	.byte $20 | $0B, $0F, $40; Wooden blocks
	.byte $20 | $15, $0F, $0C; Brick with Vine
	.byte $40 | $0E, $10, $01; Note Block with Flower
	.byte $80 | $15, $10, $D2; Small Background Hills
	.byte $40 | $15, $18, $B3, $01; Blue X-Blocks
	.byte $A0 | $0D, $1B, $32; Background Clouds
	.byte $40 | $11, $1E, $B8, $02; Blue X-Blocks
	.byte $20 | $15, $15, $10; Bricks
	.byte $20 | $0E, $1F, $0A; Multi-Coin Brick
	.byte $40 | $0F, $1F, $E0; White Turtle Bricks
	.byte $40 | $10, $1F, $E0; White Turtle Bricks
	.byte $40 | $12, $25, $B7, $01; Blue X-Blocks
	.byte $40 | $14, $29, $B5, $00; Blue X-Blocks
	.byte $A0 | $0F, $27, $32; Background Clouds
	.byte $40 | $16, $2E, $B3, $03; Blue X-Blocks
	.byte $20 | $13, $2F, $82; Coins
	.byte $40 | $14, $22, $B0, $00; Blue X-Blocks
	.byte $20 | $15, $30, $0B; Brick with 1-up
	.byte $20 | $16, $34, $10; Bricks
	.byte $40 | $17, $34, $B2, $05; Blue X-Blocks
	.byte $40 | $14, $35, $0B; Background Hills B
	.byte $20 | $12, $36, $82; Coins
	.byte $20 | $0C, $39, $40; Wooden blocks
	.byte $20 | $16, $39, $0C; Brick with Vine
	.byte $A0 | $10, $3A, $32; Background Clouds
	.byte $40 | $17, $3C, $B2, $03; Blue X-Blocks
	.byte $20 | $13, $3D, $82; Coins
	.byte $20 | $16, $3D, $31; Bricks with single coins
	.byte $20 | $0F, $37, $81; Coins
	.byte $40 | $17, $42, $B3, $03; Blue X-Blocks
	.byte $20 | $0C, $43, $40; Wooden blocks
	.byte $20 | $14, $43, $0C; Brick with Vine
	.byte $80 | $16, $43, $D2; Small Background Hills
	.byte $A0 | $0B, $46, $32; Background Clouds
	.byte $40 | $13, $48, $0A; Background Hills A
	.byte $40 | $17, $48, $B2, $04; Blue X-Blocks
	.byte $40 | $15, $4D, $B4, $02; Blue X-Blocks
	.byte $20 | $0F, $41, $81; Coins
	.byte $20 | $0F, $44, $81; Coins
	.byte $A0 | $0D, $50, $32; Background Clouds
	.byte $40 | $11, $52, $B8, $01; Blue X-Blocks
	.byte $40 | $0E, $57, $B2, $03; Blue X-Blocks
	.byte $40 | $0E, $5B, $B0, $01; Blue X-Blocks
	.byte $40 | $11, $57, $B1, $00; Blue X-Blocks
	.byte $40 | $16, $57, $B2, $02; Blue X-Blocks
	.byte $40 | $15, $5A, $B3, $09; Blue X-Blocks
	.byte $80 | $0D, $58, $D1; Small Background Hills
	.byte $20 | $12, $59, $82; Coins
	.byte $40 | $0E, $5D, $B2, $02; Blue X-Blocks
	.byte $80 | $14, $5D, $D4; Small Background Hills
	.byte $20 | $12, $5F, $82; Coins
	.byte $40 | $0F, $60, $B1, $0A; Blue X-Blocks
	.byte $20 | $12, $63, $82; Coins
	.byte $80 | $0E, $64, $D3; Small Background Hills
	.byte $40 | $16, $64, $B3, $05; Blue X-Blocks
	.byte $40 | $14, $66, $08; P-Switch
	.byte $20 | $12, $67, $82; Coins
	.byte $40 | $0F, $6A, $B2, $01; Blue X-Blocks
	.byte $20 | $13, $6A, $80; Coins
	.byte $40 | $15, $6A, $B4, $01; Blue X-Blocks
	.byte $20 | $11, $6B, $13; Bricks
	.byte $40 | $13, $6C, $B6, $03; Blue X-Blocks
	.byte $20 | $0C, $69, $0B; Brick with 1-up
	.byte $20 | $0D, $69, $10; Bricks
	.byte $20 | $0E, $69, $10; Bricks
	.byte $40 | $15, $64, $B0, $05; Blue X-Blocks
	.byte $40 | $11, $70, $B8, $0F; Blue X-Blocks
	.byte $40 | $0E, $71, $0B; Background Hills B
	.byte $40 | $0D, $75, $0A; Background Hills A
	.byte $A0 | $0A, $78, $32; Background Clouds
	.byte $20 | $0F, $7B, $E2; Rightward Pipe (CAN go in)
	.byte $40 | $00, $7E, $BF, $01; Blue X-Blocks
	.byte $40 | $10, $7E, $B6, $01; Blue X-Blocks
	.byte $40 | $19, $00, $81, $80; Water (still)
	; Pointer on screen $07
	.byte $E0 | $07, $50 | $03, 48; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_8_W3_objects:
	.byte $D3, $00, $51; Autoscrolling
	.byte $D4, $01, $2C; White Mushroom House (X pos must be uneven, Y pos=amount of coins required)
	.byte $2D, $06, $19; Boss Bass (surface)
	.byte $6C, $12, $15; Green Koopa Troopa
	.byte $6C, $38, $16; Green Koopa Troopa
	.byte $3E, $54, $18; Floating platform (floats in water)
	.byte $FF
; Dungeon__2_W3
; Object Set 2
Dungeon__2_W3_generators:
Dungeon__2_W3_header:
	.byte $2C; Next Level
	.byte LEVEL1_SIZE_05 | LEVEL1_YSTART_040; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_03; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $00 | $00, $00, $E1, $0F; Horizontally oriented X-blocks
	.byte $40 | $07, $04, $83, $0B; Water (still)
	.byte $00 | $06, $00, $E1, $03; Horizontally oriented X-blocks
	.byte $00 | $08, $00, $E2, $05; Horizontally oriented X-blocks
	.byte $00 | $0B, $00, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $03, $07, $72; Long dungeon windows
	.byte $20 | $09, $0A, $91; Downward Pipe (CAN go down)
	.byte $00 | $02, $00, $4F; Dungeon background
	.byte $00 | $00, $10, $EE, $0F; Horizontally oriented X-blocks
	.byte $00 | $0F, $10, $EB, $0F; Horizontally oriented X-blocks
	.byte $00 | $19, $20, $E1, $2F; Horizontally oriented X-blocks
	.byte $40 | $18, $28, $82, $07; Water (still)
	.byte $40 | $0F, $20, $89, $11; Water (still)
	.byte $00 | $0F, $20, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $10, $20, $E0, $05; Horizontally oriented X-blocks
	.byte $00 | $12, $2C, $B5; Stretch platform
	.byte $20 | $14, $20, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $16, $29, $B5; Stretch platform
	.byte $00 | $17, $20, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $18, $20, $E0, $04; Horizontally oriented X-blocks
	.byte $40 | $18, $33, $82, $03; Water (still)
	.byte $40 | $0F, $32, $89, $0D; Water (still)
	.byte $00 | $0F, $30, $E0, $0F; Horizontally oriented X-blocks
	.byte $00 | $10, $35, $E5, $01; Horizontally oriented X-blocks
	.byte $00 | $10, $37, $E0, $08; Horizontally oriented X-blocks
	.byte $00 | $14, $39, $B5; Stretch platform
	.byte $00 | $17, $3A, $E1, $03; Horizontally oriented X-blocks
	.byte $40 | $0F, $40, $89, $0F; Water (still)
	.byte $00 | $0F, $40, $E1, $0F; Horizontally oriented X-blocks
	.byte $00 | $10, $4F, $E6, $00; Horizontally oriented X-blocks
	.byte $00 | $12, $42, $B5; Stretch platform
	.byte $20 | $14, $4D, $92; Downward Pipe (CAN go down)
	.byte $00 | $17, $41, $B5; Stretch platform
	.byte $00 | $17, $4C, $E0, $03; Horizontally oriented X-blocks
	.byte $00 | $18, $4B, $E0, $04; Horizontally oriented X-blocks
	; Pointer on screen $00
	.byte $E0 | $00, $50 | $02, 16; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $04
	.byte $E0 | $04, $40 | $02, 20; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__2_W3_objects:
	.byte $32, $2A, $17; Bottom Stretch
	.byte $32, $2D, $13; Bottom Stretch
	.byte $31, $2D, $15; Top Stretch
	.byte $31, $30, $11; Top Stretch
	.byte $32, $3A, $15; Bottom Stretch
	.byte $31, $3D, $13; Top Stretch
	.byte $32, $42, $18; Bottom Stretch
	.byte $32, $43, $13; Bottom Stretch
	.byte $31, $45, $16; Top Stretch
	.byte $FF
; Level_9_W3
; Object Set 1
Level_9_W3_generators:
Level_9_W3_header:
	.byte $2D; Next Level
	.byte LEVEL1_SIZE_09 | LEVEL1_YSTART_040; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $0B, $00, $C2, $8F; Flat Ground
	.byte $00 | $06, $00, $44; Blue Block Platform (Extends to ground)
	.byte $00 | $08, $03, $24; Orange Block Platform (Extends to ground)
	.byte $00 | $03, $04, $E4; Background Clouds
	.byte $00 | $05, $08, $E2; Background Clouds
	.byte $00 | $03, $0B, $02; Background Hills C
	.byte $00 | $08, $09, $01; Background Hills B
	.byte $20 | $08, $12, $10; Bricks
	.byte $20 | $09, $12, $10; Bricks
	.byte $20 | $0A, $12, $10; Bricks
	.byte $20 | $06, $18, $17; Bricks
	.byte $20 | $06, $1D, $07; Brick with Leaf
	.byte $20 | $00, $16, $D8; Upward Pipe (CAN'T go up)
	.byte $00 | $02, $19, $E2; Background Clouds
	.byte $00 | $0A, $14, $91; Background Bushes
	.byte $00 | $0A, $1A, $92; Background Bushes
	.byte $00 | $0A, $1E, $90; Background Bushes
	.byte $40 | $0F, $28, $8B, $67; Water (still)
	.byte $00 | $1A, $20, $D0, $12; Underwater Flat Ground
	.byte $40 | $09, $20, $31; Bullet Bill Machine
	.byte $20 | $06, $20, $19; Bricks
	.byte $00 | $03, $29, $E3; Background Clouds
	.byte $00 | $04, $20, $E2; Background Clouds
	.byte $00 | $08, $23, $E2; Background Clouds
	.byte $00 | $0A, $23, $91; Background Bushes
	.byte $00 | $0A, $26, $92; Background Bushes
	.byte $00 | $09, $2E, $33; Green Block Platform (Extends to ground)
	.byte $20 | $12, $2C, $46; Wooden Blocks
	.byte $20 | $16, $2E, $40; Wooden Blocks
	.byte $20 | $17, $2E, $40; Wooden Blocks
	.byte $20 | $18, $2E, $40; Wooden Blocks
	.byte $20 | $19, $2E, $40; Wooden Blocks
	.byte $40 | $0D, $20, $BC, $07; Blue X-Blocks
	.byte $20 | $18, $2A, $B1; Downward Pipe (CAN go down, ignores pointers)
	.byte $00 | $06, $34, $12; White Block Platform (Extends to ground)
	.byte $00 | $06, $3B, $93; Background Bushes
	.byte $00 | $0A, $3C, $92; Background Bushes
	.byte $00 | $04, $31, $E2; Background Clouds
	.byte $00 | $05, $39, $E2; Background Clouds
	.byte $20 | $03, $3B, $23; '?' Blocks with single coins
	.byte $40 | $0A, $3A, $30; Bullet Bill Machine
	.byte $20 | $07, $39, $4F; Wooden Blocks
	.byte $20 | $0D, $35, $41; Wooden Blocks
	.byte $20 | $0E, $35, $41; Wooden Blocks
	.byte $20 | $0F, $35, $41; Wooden Blocks
	.byte $20 | $10, $35, $41; Wooden Blocks
	.byte $20 | $11, $35, $41; Wooden Blocks
	.byte $20 | $12, $35, $41; Wooden Blocks
	.byte $20 | $13, $35, $41; Wooden Blocks
	.byte $20 | $14, $35, $41; Wooden Blocks
	.byte $20 | $15, $35, $41; Wooden Blocks
	.byte $20 | $16, $35, $41; Wooden Blocks
	.byte $00 | $1A, $39, $D0, $21; Underwater Flat Ground
	.byte $40 | $12, $3C, $B7, $0B; Blue X-Blocks
	.byte $00 | $03, $41, $E3; Background Clouds
	.byte $00 | $02, $47, $E2; Background Clouds
	.byte $20 | $06, $48, $40; Wooden Blocks
	.byte $20 | $05, $48, $46; Wooden Blocks
	.byte $20 | $06, $4E, $40; Wooden Blocks
	.byte $20 | $07, $4E, $40; Wooden Blocks
	.byte $20 | $08, $4E, $40; Wooden Blocks
	.byte $20 | $09, $4E, $40; Wooden Blocks
	.byte $20 | $0A, $4E, $40; Wooden Blocks
	.byte $20 | $08, $41, $10; Bricks
	.byte $20 | $09, $41, $10; Bricks
	.byte $20 | $0A, $41, $10; Bricks
	.byte $20 | $05, $49, $24; '?' Blocks with single coins
	.byte $40 | $0A, $46, $30; Bullet Bill Machine
	.byte $00 | $06, $41, $92; Background Bushes
	.byte $00 | $0A, $43, $91; Background Bushes
	.byte $00 | $0A, $49, $91; Background Bushes
	.byte $40 | $09, $4C, $F8; Double-Ended Vertical Pipe
	.byte $20 | $13, $52, $49; Wooden Blocks
	.byte $20 | $0D, $57, $40; Wooden Blocks
	.byte $20 | $0E, $57, $40; Wooden Blocks
	.byte $20 | $0F, $57, $40; Wooden Blocks
	.byte $20 | $10, $57, $40; Wooden Blocks
	.byte $20 | $11, $57, $40; Wooden Blocks
	.byte $20 | $12, $57, $40; Wooden Blocks
	.byte $20 | $17, $5C, $48; Wooden Blocks
	.byte $00 | $01, $5D, $E2; Background Clouds
	.byte $00 | $03, $58, $E2; Background Clouds
	.byte $00 | $04, $52, $E3; Background Clouds
	.byte $00 | $07, $53, $00; Background Hills A
	.byte $20 | $07, $56, $82; Coins
	.byte $40 | $07, $5C, $E0; White Turtle Bricks
	.byte $40 | $08, $5C, $E0; White Turtle Bricks
	.byte $40 | $09, $5C, $E0; White Turtle Bricks
	.byte $40 | $0A, $5C, $E0; White Turtle Bricks
	.byte $20 | $07, $5D, $62; Note Blocks - movable two directions
	.byte $40 | $07, $5E, $01; Note Block with Flower
	.byte $00 | $0A, $5D, $90; Background Bushes
	.byte $00 | $0A, $5F, $90; Background Bushes
	.byte $00 | $1A, $67, $D0, $28; Underwater Flat Ground
	.byte $20 | $0D, $6A, $41; Wooden Blocks
	.byte $20 | $0E, $6A, $41; Wooden Blocks
	.byte $20 | $0F, $6A, $41; Wooden Blocks
	.byte $20 | $10, $6A, $41; Wooden Blocks
	.byte $20 | $11, $6A, $41; Wooden Blocks
	.byte $20 | $12, $6A, $41; Wooden Blocks
	.byte $20 | $0D, $6F, $41; Wooden Blocks
	.byte $20 | $0E, $6F, $41; Wooden Blocks
	.byte $20 | $0F, $6F, $41; Wooden Blocks
	.byte $20 | $10, $6F, $41; Wooden Blocks
	.byte $20 | $11, $6F, $41; Wooden Blocks
	.byte $20 | $12, $6F, $41; Wooden Blocks
	.byte $20 | $16, $6A, $47; Wooden Blocks
	.byte $20 | $17, $6A, $47; Wooden Blocks
	.byte $20 | $18, $6A, $47; Wooden Blocks
	.byte $20 | $19, $6A, $47; Wooden Blocks
	.byte $20 | $17, $67, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $02, $66, $E3; Background Clouds
	.byte $00 | $04, $6D, $E2; Background Clouds
	.byte $00 | $03, $61, $E2; Background Clouds
	.byte $20 | $07, $66, $82; Coins
	.byte $00 | $0A, $61, $91; Background Bushes
	.byte $00 | $0A, $68, $92; Background Bushes
	.byte $00 | $08, $63, $01; Background Hills B
	.byte $40 | $07, $60, $E0; White Turtle Bricks
	.byte $40 | $08, $60, $E0; White Turtle Bricks
	.byte $40 | $09, $60, $E0; White Turtle Bricks
	.byte $40 | $0A, $60, $E0; White Turtle Bricks
	.byte $20 | $03, $6C, $40; Wooden Blocks
	.byte $20 | $04, $6C, $40; Wooden Blocks
	.byte $20 | $05, $6C, $40; Wooden Blocks
	.byte $20 | $06, $6C, $42; Wooden Blocks
	.byte $20 | $06, $6F, $0B; Brick with 1-up
	.byte $40 | $07, $6C, $E0; White Turtle Bricks
	.byte $40 | $08, $6C, $E0; White Turtle Bricks
	.byte $40 | $09, $6C, $E0; White Turtle Bricks
	.byte $20 | $0A, $6C, $40; Wooden Blocks
	.byte $20 | $12, $75, $45; Wooden Blocks
	.byte $20 | $13, $7A, $40; Wooden Blocks
	.byte $20 | $14, $7A, $40; Wooden Blocks
	.byte $20 | $15, $7A, $40; Wooden Blocks
	.byte $20 | $16, $7A, $40; Wooden Blocks
	.byte $00 | $03, $7C, $E2; Background Clouds
	.byte $00 | $03, $71, $E2; Background Clouds
	.byte $20 | $06, $73, $82; Coins
	.byte $40 | $06, $70, $E1; White Turtle Bricks
	.byte $40 | $07, $71, $E0; White Turtle Bricks
	.byte $40 | $08, $71, $E0; White Turtle Bricks
	.byte $40 | $09, $71, $E0; White Turtle Bricks
	.byte $40 | $0A, $71, $E0; White Turtle Bricks
	.byte $40 | $06, $7D, $E1; White Turtle Bricks
	.byte $40 | $07, $7C, $E0; White Turtle Bricks
	.byte $40 | $07, $7F, $E0; White Turtle Bricks
	.byte $40 | $08, $7C, $E0; White Turtle Bricks
	.byte $40 | $08, $7F, $E0; White Turtle Bricks
	.byte $00 | $03, $75, $02; Background Hills C
	.byte $00 | $08, $73, $01; Background Hills B
	.byte $00 | $0A, $70, $90; Background Bushes
	.byte $00 | $0A, $7B, $90; Background Bushes
	.byte $40 | $09, $7C, $E3; White Turtle Bricks
	.byte $40 | $0A, $7C, $E3; White Turtle Bricks
	.byte $40 | $09, $7D, $F9; Double-Ended Vertical Pipe
	.byte $40 | $00, $80, $BA, $0F; Blue X-Blocks
	.byte $20 | $0E, $8C, $C5; Upward Pipe (CAN go up)
	.byte $20 | $12, $82, $49; Wooden Blocks
	.byte $20 | $13, $82, $40; Wooden Blocks
	.byte $20 | $14, $82, $40; Wooden Blocks
	.byte $20 | $15, $82, $40; Wooden Blocks
	.byte $20 | $16, $82, $40; Wooden Blocks
	.byte $20 | $17, $8A, $40; Wooden Blocks
	.byte $20 | $18, $8A, $40; Wooden Blocks
	.byte $20 | $19, $8A, $40; Wooden Blocks
	; Pointer on screen $02
	.byte $E0 | $02, $00 | $02, 21; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $08
	.byte $E0 | $08, $60 | $01, 48; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_9_W3_objects:
	.byte $6E, $12, $07; Green Koopa Paratroopa (bounces)
	.byte $A1, $16, $08; Green Piranha Plant (downward)
	.byte $BC, $20, $09; Bullet Bills
	.byte $74, $22, $04; Para-Goomba with Micro-Goombas
	.byte $55, $2D, $0A; Bob-Omb
	.byte $55, $33, $0A; Bob-Omb
	.byte $77, $36, $18; Cheep-Cheep
	.byte $BC, $3A, $0A; Bullet Bills
	.byte $55, $3D, $0A; Bob-Omb
	.byte $55, $46, $06; Bob-Omb
	.byte $BC, $46, $0A; Bullet Bills
	.byte $55, $4E, $04; Bob-Omb
	.byte $55, $56, $0A; Bob-Omb
	.byte $55, $5A, $0A; Bob-Omb
	.byte $77, $5B, $15; Cheep-Cheep
	.byte $55, $69, $0A; Bob-Omb
	.byte $77, $6D, $14; Cheep-Cheep
	.byte $6C, $6F, $0A; Green Koopa Troopa
	.byte $6E, $7A, $0A; Green Koopa Paratroopa (bounces)
	.byte $6E, $7E, $05; Green Koopa Paratroopa (bounces)
	.byte $77, $83, $18; Cheep-Cheep
	.byte $77, $8A, $14; Cheep-Cheep
	.byte $FF
; Pipe_2_End_2_W3
; Object Set 14
Pipe_2_End_2_W3_generators:
Pipe_2_End_2_W3_header:
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
Pipe_2_End_2_W3_objects:
	.byte $25, $02, $13; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Hidden_Hammer_Bros_W3
; Object Set 3
Hidden_Hammer_Bros_W3_generators:
Hidden_Hammer_Bros_W3_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $00 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $00; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $80 | $00, $40, $13, $86; Gap
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $40 | $13, $00, $0C; Background Hills C
	.byte $40 | $17, $0C, $0B; Background Hills B
	.byte $20 | $16, $07, $16; Bricks
	.byte $80 | $1A, $00, $80, $0F; Flat Land - Hilly
	.byte $FF
Hidden_Hammer_Bros_W3_objects:
	.byte $81, $0C, $14; Hammer Brother
	.byte $81, $09, $18; Hammer Brother
	.byte $BA, $0D, $14; Exit on get treasure chest
	.byte $FF
; Kings_Room_W3
; Object Set 2
Kings_Room_W3_generators:
Kings_Room_W3_header:
	.byte $0C; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; Weird
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Kings_Room_W3_objects:
	.byte $D5, $0A, $16; 'The king has been transformed' message
	.byte $FF
; Pipe_3_End_2_W3
; Object Set 14
Pipe_3_End_2_W3_generators:
Pipe_3_End_2_W3_header:
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
Pipe_3_End_2_W3_objects:
	.byte $25, $02, $14; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Hammer_Bros_1_W4
; Object Set 11
Hammer_Bros_1_W4_generators:
Hammer_Bros_1_W4_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_11; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0B; Start action | Graphic set
	.byte $80 | $06; Time | Music
	.byte $00 | $10, $02, $10; Giant cloud platform
	.byte $00 | $11, $0D, $10; Giant cloud platform
	.byte $00 | $16, $03, $05; Background Mountain
	.byte $00 | $14, $0B, $05; Background Mountain
	.byte $00 | $19, $00, $77; Giant Ground
	.byte $FF
Hammer_Bros_1_W4_objects:
	.byte $81, $0A, $17; Hammer Brother
	.byte $BA, $0D, $14; Exit on get treasure chest
	.byte $FF
; Pipe_1_End_1_W4
; Object Set 14
Pipe_1_End_1_W4_generators:
Pipe_1_End_1_W4_header:
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
Pipe_1_End_1_W4_objects:
	.byte $25, $02, $15; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_6_W4
; Object Set 1
Level_6_W4_generators:
Level_6_W4_header:
	.byte $2E; Next Level
	.byte LEVEL1_SIZE_11 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_03; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	.byte $00 | $1A, $00, $C0, $1D; Flat Ground
	.byte $00 | $19, $00, $92; Background Bushes
	.byte $00 | $16, $06, $00; Background Hills A
	.byte $00 | $12, $0A, $02; Background Hills C
	.byte $00 | $17, $0D, $01; Background Hills B
	.byte $00 | $12, $04, $E2; Background Clouds
	.byte $00 | $19, $12, $91; Background Bushes
	.byte $00 | $19, $17, $92; Background Bushes
	.byte $00 | $11, $10, $E2; Background Clouds
	.byte $20 | $12, $13, $17; Bricks
	.byte $20 | $16, $13, $17; Bricks
	.byte $20 | $13, $13, $10; Bricks
	.byte $20 | $14, $13, $10; Bricks
	.byte $20 | $15, $13, $10; Bricks
	.byte $20 | $13, $1A, $10; Bricks
	.byte $20 | $14, $1A, $10; Bricks
	.byte $20 | $15, $1A, $10; Bricks
	.byte $20 | $15, $1F, $83; Coins
	.byte $20 | $12, $19, $0B; Brick with 1-up
	.byte $00 | $1A, $24, $C0, $3C; Flat Ground
	.byte $00 | $13, $21, $E3; Background Clouds
	.byte $00 | $11, $28, $E2; Background Clouds
	.byte $00 | $07, $2A, $E2; Background Clouds
	.byte $00 | $0B, $2C, $B9; Cloud Platform
	.byte $00 | $15, $2B, $44; Blue Block Platform (Extends to ground)
	.byte $00 | $17, $28, $24; Orange Block Platform (Extends to ground)
	.byte $00 | $18, $2A, $04; Door (CAN go in)
	.byte $20 | $08, $2D, $82; Coins
	.byte $20 | $16, $26, $A3; Downward Pipe (CAN'T go down)
	.byte $00 | $19, $31, $91; Background Bushes
	.byte $00 | $19, $3B, $91; Background Bushes
	.byte $00 | $17, $37, $01; Background Hills B
	.byte $00 | $0B, $3A, $B5; Cloud Platform
	.byte $00 | $05, $34, $E2; Background Clouds
	.byte $00 | $06, $3D, $E2; Background Clouds
	.byte $00 | $0D, $38, $E2; Background Clouds
	.byte $00 | $14, $33, $E2; Background Clouds
	.byte $00 | $15, $3B, $E3; Background Clouds
	.byte $20 | $07, $31, $81; Coins
	.byte $20 | $07, $39, $82; Coins
	.byte $20 | $09, $3E, $81; Coins
	.byte $20 | $18, $35, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $1A, $33, $A2; Gap
	.byte $20 | $16, $39, $01; '?' with Leaf
	.byte $00 | $19, $41, $92; Background Bushes
	.byte $00 | $19, $48, $92; Background Bushes
	.byte $00 | $19, $4C, $90; Background Bushes
	.byte $00 | $11, $47, $E2; Background Clouds
	.byte $00 | $13, $42, $E2; Background Clouds
	.byte $00 | $14, $4D, $E2; Background Clouds
	.byte $20 | $12, $4E, $82; Coins
	.byte $20 | $16, $46, $40; Wooden Blocks
	.byte $20 | $17, $46, $40; Wooden Blocks
	.byte $40 | $18, $47, $06; Wooden Block with Star
	.byte $20 | $19, $47, $40; Wooden Blocks
	.byte $20 | $16, $47, $16; Bricks
	.byte $20 | $19, $4E, $40; Wooden Blocks
	.byte $20 | $16, $49, $0A; Multi-Coin Brick
	.byte $00 | $16, $50, $00; Background Hills A
	.byte $00 | $19, $58, $91; Background Bushes
	.byte $00 | $19, $5C, $90; Background Bushes
	.byte $00 | $11, $53, $E3; Background Clouds
	.byte $00 | $14, $59, $E2; Background Clouds
	.byte $20 | $16, $5C, $0E; Invisible Coin
	.byte $20 | $16, $5D, $0E; Invisible Coin
	.byte $20 | $17, $56, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $5E, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $5B, $0E; Invisible Coin
	.byte $00 | $1A, $64, $C0, $15; Flat Ground
	.byte $00 | $11, $69, $33; Green Block Platform (Extends to ground)
	.byte $00 | $13, $66, $24; Orange Block Platform (Extends to ground)
	.byte $00 | $16, $67, $47; Blue Block Platform (Extends to ground)
	.byte $00 | $14, $68, $04; Door (CAN go in)
	.byte $00 | $19, $65, $90; Background Bushes
	.byte $00 | $11, $61, $E2; Background Clouds
	.byte $00 | $17, $62, $E2; Background Clouds
	.byte $00 | $12, $71, $02; Background Hills C
	.byte $00 | $19, $77, $90; Background Bushes
	.byte $00 | $10, $77, $E2; Background Clouds
	.byte $00 | $11, $70, $E2; Background Clouds
	.byte $00 | $14, $7B, $E2; Background Clouds
	.byte $20 | $17, $7D, $14; Bricks
	.byte $20 | $17, $78, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $11, $82, $E2; Background Clouds
	.byte $00 | $18, $84, $E2; Background Clouds
	.byte $00 | $16, $8A, $E2; Background Clouds
	.byte $20 | $14, $80, $14; Bricks
	.byte $20 | $14, $88, $15; Bricks
	.byte $20 | $14, $80, $31; Bricks with single coins
	.byte $20 | $17, $8E, $12; Bricks
	.byte $00 | $11, $91, $E3; Background Clouds
	.byte $00 | $14, $96, $E2; Background Clouds
	.byte $00 | $1A, $92, $C0, $1D; Flat Ground
	.byte $00 | $19, $93, $96; Background Bushes
	.byte $00 | $17, $94, $01; Background Hills B
	.byte $40 | $00, $9A, $09; Level Ending
	; Pointer on screen $02
	.byte $E0 | $02, $70 | $08, 162; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $06
	.byte $E0 | $06, $50 | $08, 134; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_6_W4_objects:
	.byte $7A, $18, $14; Giant Green Koopa Troopa
	.byte $7A, $16, $18; Giant Green Koopa Troopa
	.byte $7E, $11, $18; Giant Green Koopa Paratroopa
	.byte $7D, $26, $16; Giant Green Piranha Plant
	.byte $7A, $2D, $13; Giant Green Koopa Troopa
	.byte $7C, $30, $18; Giant Goomba
	.byte $7C, $32, $18; Giant Goomba
	.byte $7E, $42, $18; Giant Green Koopa Paratroopa
	.byte $7A, $4B, $18; Giant Green Koopa Troopa
	.byte $7C, $4A, $14; Giant Goomba
	.byte $7C, $54, $18; Giant Goomba
	.byte $7A, $5C, $18; Giant Green Koopa Troopa
	.byte $7D, $56, $17; Giant Green Piranha Plant
	.byte $7D, $5E, $16; Giant Green Piranha Plant
	.byte $7B, $69, $18; Giant Red Koopa Troopa
	.byte $7B, $6D, $14; Giant Red Koopa Troopa
	.byte $7E, $78, $15; Giant Green Koopa Paratroopa
	.byte $7D, $78, $17; Giant Green Piranha Plant
	.byte $7B, $80, $15; Giant Red Koopa Troopa
	.byte $7A, $81, $12; Giant Green Koopa Troopa
	.byte $7E, $8C, $12; Giant Green Koopa Paratroopa
	.byte $7E, $9E, $18; Giant Green Koopa Paratroopa
	.byte $41, $A8, $15; Goal Card
	.byte $FF
; Kings_Room_W4
; Object Set 2
Kings_Room_W4_generators:
Kings_Room_W4_header:
	.byte $0E; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; Weird
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Kings_Room_W4_objects:
	.byte $D5, $0A, $16; 'The king has been transformed' message
	.byte $FF
; Dungeon__2_W4
; Object Set 2
Dungeon__2_W4_generators:
Dungeon__2_W4_header:
	.byte $2F; Next Level
	.byte LEVEL1_SIZE_11 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_08; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $0A, $00, $3F, $8F; Blank Background (used to block out stuff)
	.byte $00 | $00, $00, $E9, $8F; Horizontally oriented X-blocks
	.byte $00 | $0A, $00, $E5, $0B; Horizontally oriented X-blocks
	.byte $00 | $19, $00, $E1, $0C; Horizontally oriented X-blocks
	.byte $00 | $13, $0B, $E0, $06; Horizontally oriented X-blocks
	.byte $00 | $14, $0A, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $15, $09, $E0, $03; Horizontally oriented X-blocks
	.byte $00 | $16, $08, $E0, $04; Horizontally oriented X-blocks
	.byte $00 | $17, $07, $E0, $05; Horizontally oriented X-blocks
	.byte $00 | $18, $06, $E0, $06; Horizontally oriented X-blocks
	.byte $00 | $12, $01, $71; Long dungeon windows
	.byte $60 | $1A, $0D, $40, $39; Lava
	.byte $00 | $10, $15, $71; Long dungeon windows
	.byte $60 | $16, $16, $E3; Donut Blocks
	.byte $60 | $13, $1E, $E1; Donut Blocks
	.byte $00 | $10, $24, $72; Long dungeon windows
	.byte $20 | $13, $26, $00; '?' with flower
	.byte $60 | $17, $24, $E7; Donut Blocks
	.byte $00 | $10, $35, $71; Long dungeon windows
	.byte $60 | $12, $3D, $E2; Donut Blocks
	.byte $60 | $15, $31, $E2; Donut Blocks
	.byte $60 | $17, $36, $E3; Donut Blocks
	.byte $00 | $0A, $45, $E9, $15; Horizontally oriented X-blocks
	.byte $00 | $14, $4E, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $15, $4F, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $17, $43, $E0, $07; Horizontally oriented X-blocks
	.byte $00 | $18, $47, $E0, $04; Horizontally oriented X-blocks
	.byte $00 | $19, $47, $E0, $05; Horizontally oriented X-blocks
	.byte $00 | $1A, $47, $E0, $16; Horizontally oriented X-blocks
	.byte $00 | $14, $50, $E2, $0A; Horizontally oriented X-blocks
	.byte $00 | $0A, $5B, $E5, $34; Horizontally oriented X-blocks
	.byte $00 | $13, $5E, $E7, $0F; Horizontally oriented X-blocks
	.byte $20 | $16, $5C, $0D; Brick with P-Switch
	.byte $40 | $17, $57, $52; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $18, $57, $52; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $19, $57, $52; Silver Coins (appear when you hit a P-Switch)
	.byte $00 | $18, $58, $06; Invisible Door
	.byte $00 | $1A, $57, $E0, $02; Horizontally oriented X-blocks
	.byte $60 | $13, $68, $32, $05; Blank Background (used to block out stuff)
	.byte $20 | $14, $68, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $14, $6E, $E6, $11; Horizontally oriented X-blocks
	.byte $00 | $14, $6E, $02; Rotodisc block
	.byte $00 | $11, $74, $62; Dungeon windows
	.byte $00 | $10, $8F, $E8, $00; Horizontally oriented X-blocks
	.byte $00 | $19, $80, $E1, $0F; Horizontally oriented X-blocks
	.byte $00 | $15, $82, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $15, $8B, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $16, $87, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $11, $85, $71; Long dungeon windows
	.byte $00 | $00, $90, $FF, $1A; Vertically oriented X-blocks
	.byte $00 | $00, $A0, $FF, $1A; Vertically oriented X-blocks
	.byte $60 | $02, $98, $3F, $0D; Blank Background (used to block out stuff)
	.byte $60 | $12, $98, $36, $0D; Blank Background (used to block out stuff)
	.byte $20 | $02, $99, $D3; Upward Pipe (CAN'T go up)
	.byte $20 | $16, $9C, $82; Coins
	.byte $20 | $14, $9E, $82; Coins
	.byte $20 | $16, $A0, $82; Coins
	.byte $20 | $17, $A4, $B1; Downward Pipe (CAN go down, ignores pointers)
	.byte $20 | $10, $A3, $0E; Invisible Coin
	.byte $20 | $13, $A4, $0E; Invisible Coin
	.byte $20 | $0D, $A2, $0B; Brick with 1-up
	; Pointer on screen $05
	.byte $E0 | $05, $F0 | $08, 212; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $0A
	.byte $E0 | $0A, $50 | $02, 34; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__2_W4_objects:
	.byte $3F, $2A, $16; Dry Bones
	.byte $3F, $39, $16; Dry Bones
	.byte $3F, $49, $16; Dry Bones
	.byte $3F, $54, $19; Dry Bones
	.byte $3F, $5B, $19; Dry Bones
	.byte $3F, $62, $12; Dry Bones
	.byte $3F, $63, $12; Dry Bones
	.byte $3F, $6C, $15; Dry Bones
	.byte $5B, $6E, $14; Single Rotodisc (rotates counterclockwise)
	.byte $4B, $8D, $27; Boom Boom
	.byte $FF
; Pipe_2_End_1_W4
; Object Set 14
Pipe_2_End_1_W4_generators:
Pipe_2_End_1_W4_header:
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
Pipe_2_End_1_W4_objects:
	.byte $25, $02, $16; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_5_W4
; Object Set 11
Level_5_W4_generators:
Level_5_W4_header:
	.byte $30; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0B; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $17, $0E, $64; Giant Metal Blocks
	.byte $00 | $17, $1A, $20; Giant bricks
	.byte $00 | $15, $10, $63; Giant Metal Blocks
	.byte $00 | $13, $12, $62; Giant Metal Blocks
	.byte $00 | $11, $14, $60; Giant Metal Blocks
	.byte $00 | $15, $18, $40; Giant '?' blocks with leafs
	.byte $00 | $15, $03, $05; Background Mountain
	.byte $00 | $19, $00, $74; Giant Ground
	.byte $00 | $11, $08, $10; Giant cloud platform
	.byte $00 | $19, $0C, $79; Giant Ground
	.byte $00 | $15, $22, $83; Giant Downward Pipe
	.byte $00 | $19, $22, $7D; Giant Ground
	.byte $00 | $11, $26, $10; Giant cloud platform
	.byte $00 | $15, $28, $05; Background Mountain
	.byte $40 | $17, $2C, $31; Bullet Bill Machine
	.byte $00 | $16, $2F, $05; Background Mountain
	.byte $20 | $14, $2F, $22; '?' blocks with single coins
	.byte $20 | $14, $30, $00; '?' with flower
	.byte $40 | $16, $33, $32; Bullet Bill Machine
	.byte $20 | $14, $35, $22; '?' blocks with single coins
	.byte $00 | $16, $36, $05; Background Mountain
	.byte $40 | $15, $3A, $33; Bullet Bill Machine
	.byte $40 | $17, $42, $30; Bullet Bill Machine
	.byte $20 | $18, $42, $41; Wooden blocks
	.byte $20 | $10, $43, $82; Coins
	.byte $00 | $12, $44, $10; Giant cloud platform
	.byte $00 | $18, $47, $82; Giant Downward Pipe
	.byte $20 | $19, $4C, $41; Wooden blocks
	.byte $00 | $19, $50, $7F; Giant Ground
	.byte $20 | $16, $51, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $05, $56, $40; Wooden blocks
	.byte $00 | $09, $57, $10; Giant cloud platform
	.byte $40 | $17, $55, $31; Bullet Bill Machine
	.byte $40 | $16, $56, $32; Bullet Bill Machine
	.byte $20 | $0F, $56, $0C; Brick with Vine
	.byte $20 | $03, $57, $C2; Upward Pipe (CAN go up)
	.byte $20 | $02, $57, $41; Wooden blocks
	.byte $00 | $16, $59, $05; Background Mountain
	.byte $40 | $18, $5D, $30; Bullet Bill Machine
	.byte $40 | $13, $5C, $35; Bullet Bill Machine
	.byte $20 | $16, $5B, $0E; Invisible Coin
	.byte $00 | $15, $60, $83; Giant Downward Pipe
	.byte $20 | $16, $65, $42; Wooden blocks
	.byte $40 | $14, $66, $31; Bullet Bill Machine
	.byte $40 | $17, $6A, $31; Bullet Bill Machine
	.byte $20 | $16, $6D, $42; Wooden blocks
	.byte $00 | $19, $6F, $70; Giant Ground
	.byte $40 | $11, $64, $52; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $11, $69, $52; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $13, $64, $52; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $15, $69, $52; Silver Coins (appear when you hit a P-Switch)
	.byte $00 | $19, $73, $76; Giant Ground
	.byte $00 | $15, $73, $83; Giant Downward Pipe
	.byte $00 | $16, $79, $05; Background Mountain
	.byte $40 | $14, $79, $34; Bullet Bill Machine
	.byte $00 | $11, $7A, $10; Giant cloud platform
	.byte $60 | $17, $7C, $61; Rightward Pipe to End of Level
	.byte $20 | $00, $7E, $41; Wooden blocks
	.byte $00 | $01, $7E, $50; Giant Wooden Blocks
	.byte $00 | $03, $7E, $50; Giant Wooden Blocks
	.byte $00 | $05, $7E, $50; Giant Wooden Blocks
	.byte $00 | $07, $7E, $50; Giant Wooden Blocks
	.byte $00 | $09, $7E, $50; Giant Wooden Blocks
	.byte $00 | $0B, $7E, $50; Giant Wooden Blocks
	.byte $00 | $0D, $7E, $50; Giant Wooden Blocks
	.byte $00 | $0F, $7E, $50; Giant Wooden Blocks
	.byte $00 | $11, $7E, $50; Giant Wooden Blocks
	.byte $00 | $13, $7E, $50; Giant Wooden Blocks
	.byte $00 | $15, $7E, $50; Giant Wooden Blocks
	.byte $00 | $17, $7E, $50; Giant Wooden Blocks
	.byte $40 | $06, $5A, $52; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $08, $5E, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $09, $5F, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $0A, $60, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $0C, $62, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $0D, $63, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $0E, $64, $50; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $13, $69, $52; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $17, $6D, $52; Silver Coins (appear when you hit a P-Switch)
	.byte $00 | $06, $06, $10; Giant cloud platform
	.byte $00 | $06, $10, $10; Giant cloud platform
	.byte $00 | $08, $1C, $10; Giant cloud platform
	.byte $00 | $04, $2A, $10; Giant cloud platform
	.byte $00 | $06, $3A, $10; Giant cloud platform
	.byte $00 | $08, $46, $10; Giant cloud platform
	; Pointer on screen $05
	.byte $E0 | $05, $60 | $01, 80; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_5_W4_objects:
	.byte $7A, $10, $13; Giant Green Koopa Troopa
	.byte $7E, $15, $0F; Giant Green Koopa Paratroopa
	.byte $7E, $1E, $17; Giant Green Koopa Paratroopa
	.byte $7F, $22, $15; Giant Red Piranha Plant
	.byte $BC, $2C, $17; Bullet Bills
	.byte $BD, $33, $16; Missile Bills
	.byte $BC, $3A, $15; Bullet Bills
	.byte $BD, $42, $17; Missile Bills
	.byte $7F, $47, $18; Giant Red Piranha Plant
	.byte $BC, $55, $17; Bullet Bills
	.byte $BC, $56, $16; Bullet Bills
	.byte $BC, $5D, $18; Bullet Bills
	.byte $BD, $5C, $13; Missile Bills
	.byte $A2, $51, $16; Red Piranha Plant (upward)
	.byte $7F, $60, $15; Giant Red Piranha Plant
	.byte $BD, $66, $14; Missile Bills
	.byte $BD, $6A, $17; Missile Bills
	.byte $7F, $73, $15; Giant Red Piranha Plant
	.byte $BC, $79, $14; Bullet Bills
	.byte $FF
; Pipe_2_End_2_W4
; Object Set 14
Pipe_2_End_2_W4_generators:
Pipe_2_End_2_W4_header:
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
Pipe_2_End_2_W4_objects:
	.byte $25, $02, $16; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Dungeon__1_W4
; Object Set 2
Dungeon__1_W4_generators:
Dungeon__1_W4_header:
	.byte $31; Next Level
	.byte LEVEL1_SIZE_09 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_14; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $0E, $00, $3A, $8F; Blank Background (used to block out stuff)
	.byte $00 | $0E, $00, $E1, $8F; Horizontally oriented X-blocks
	.byte $00 | $10, $00, $E5, $03; Horizontally oriented X-blocks
	.byte $00 | $14, $0A, $E0, $11; Horizontally oriented X-blocks
	.byte $00 | $15, $09, $E0, $12; Horizontally oriented X-blocks
	.byte $00 | $16, $08, $E0, $15; Horizontally oriented X-blocks
	.byte $00 | $17, $07, $E0, $16; Horizontally oriented X-blocks
	.byte $00 | $18, $06, $E0, $17; Horizontally oriented X-blocks
	.byte $00 | $11, $10, $04; Hot Foot Candle
	.byte $00 | $11, $18, $04; Hot Foot Candle
	.byte $00 | $10, $20, $E6, $0C; Horizontally oriented X-blocks
	.byte $60 | $14, $20, $31, $03; Blank Background (used to block out stuff)
	.byte $60 | $13, $27, $33, $01; Blank Background (used to block out stuff)
	.byte $60 | $15, $2A, $31, $02; Blank Background (used to block out stuff)
	.byte $00 | $14, $2F, $E4, $05; Horizontally oriented X-blocks
	.byte $60 | $14, $2F, $30, $00; Blank Background (used to block out stuff)
	.byte $60 | $15, $2F, $31, $02; Blank Background (used to block out stuff)
	.byte $00 | $15, $27, $04; Hot Foot Candle
	.byte $00 | $11, $32, $04; Hot Foot Candle
	.byte $00 | $12, $3A, $04; Hot Foot Candle
	.byte $20 | $16, $35, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $37, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $3B, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $3D, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $39, $92; Downward Pipe (CAN go down)
	.byte $00 | $10, $3F, $E2, $03; Horizontally oriented X-blocks
	.byte $00 | $16, $3F, $E2, $0A; Horizontally oriented X-blocks
	.byte $00 | $12, $45, $E3, $04; Horizontally oriented X-blocks
	.byte $00 | $10, $49, $E0, $00; Horizontally oriented X-blocks
	.byte $60 | $10, $41, $31, $01; Blank Background (used to block out stuff)
	.byte $00 | $15, $4C, $04; Hot Foot Candle
	.byte $00 | $10, $51, $E4, $03; Horizontally oriented X-blocks
	.byte $60 | $13, $52, $31, $01; Blank Background (used to block out stuff)
	.byte $20 | $11, $5A, $01; '?' with leaf
	.byte $00 | $14, $58, $E4, $05; Horizontally oriented X-blocks
	.byte $00 | $17, $5E, $E1, $05; Horizontally oriented X-blocks
	.byte $60 | $15, $5C, $31, $01; Blank Background (used to block out stuff)
	.byte $00 | $10, $60, $E4, $01; Horizontally oriented X-blocks
	.byte $20 | $14, $64, $A4; Downward Pipe (CAN'T go down)
	.byte $00 | $10, $68, $E4, $17; Horizontally oriented X-blocks
	.byte $00 | $16, $6E, $64; Dungeon windows
	.byte $00 | $15, $86, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $11, $83, $62; Dungeon windows
	.byte $00 | $10, $8F, $E8, $00; Horizontally oriented X-blocks
	; Pointer on screen $03
	.byte $E0 | $03, $00 | $02, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__1_W4_objects:
	.byte $30, $10, $10; Hot Foot
	.byte $30, $18, $10; Hot Foot
	.byte $30, $27, $14; Hot Foot
	.byte $8B, $22, $14; Thwomp (moves left)
	.byte $8B, $30, $15; Thwomp (moves left)
	.byte $30, $32, $10; Hot Foot
	.byte $30, $3A, $11; Hot Foot
	.byte $8C, $41, $10; Thwomp (moves right)
	.byte $30, $4C, $14; Hot Foot
	.byte $8A, $52, $13; Thwomp (normal)
	.byte $30, $53, $14; Hot Foot
	.byte $8C, $5C, $15; Thwomp (moves right)
	.byte $4B, $8C, $17; Boom Boom
	.byte $FF
; Level_3_Beginning_W4
; Object Set 11
Level_3_Beginning_W4_generators:
Level_3_Beginning_W4_header:
	.byte $32; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0B; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $19, $00, $7F; Giant Ground
	.byte $00 | $19, $20, $77; Giant Ground
	.byte $00 | $15, $07, $05; Background Mountain
	.byte $00 | $11, $04, $10; Giant cloud platform
	.byte $00 | $13, $12, $05; Background Mountain
	.byte $00 | $15, $18, $20; Giant bricks
	.byte $00 | $17, $18, $20; Giant bricks
	.byte $00 | $15, $23, $05; Background Mountain
	.byte $00 | $11, $20, $10; Giant cloud platform
	.byte $20 | $00, $2E, $41; Wooden blocks
	.byte $00 | $01, $2E, $50; Giant Wooden Blocks
	.byte $00 | $03, $2E, $50; Giant Wooden Blocks
	.byte $00 | $05, $2E, $50; Giant Wooden Blocks
	.byte $00 | $07, $2E, $50; Giant Wooden Blocks
	.byte $00 | $09, $2E, $50; Giant Wooden Blocks
	.byte $00 | $0B, $2E, $50; Giant Wooden Blocks
	.byte $00 | $0D, $2E, $50; Giant Wooden Blocks
	.byte $00 | $0F, $2E, $50; Giant Wooden Blocks
	.byte $00 | $11, $2E, $50; Giant Wooden Blocks
	.byte $00 | $13, $2E, $50; Giant Wooden Blocks
	.byte $00 | $15, $2E, $50; Giant Wooden Blocks
	.byte $00 | $17, $2E, $50; Giant Wooden Blocks
	.byte $00 | $19, $2E, $50; Giant Wooden Blocks
	.byte $20 | $15, $2C, $93; Downward Pipe (CAN go down)
	.byte $20 | $17, $28, $E3; Rightward Pipe (CAN go in)
	; Pointer on screen $02
	.byte $E0 | $02, $50 | $02, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_3_Beginning_W4_objects:
	.byte $86, $11, $17; Sledge Brother
	.byte $86, $25, $17; Sledge Brother
	.byte $FF
; Level_2_W4
; Object Set 11
Level_2_W4_generators:
Level_2_W4_header:
	.byte $33; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_11; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0B; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $17, $00, $62; Giant Metal Blocks
	.byte $00 | $15, $08, $83; Giant Downward Pipe
	.byte $00 | $16, $10, $82; Giant Downward Pipe
	.byte $00 | $17, $16, $81; Giant Downward Pipe
	.byte $00 | $16, $1B, $82; Giant Downward Pipe
	.byte $00 | $14, $21, $84; Giant Downward Pipe
	.byte $00 | $15, $28, $40; Giant '?' blocks with leafs
	.byte $00 | $17, $28, $60; Giant Metal Blocks
	.byte $00 | $16, $2D, $82; Giant Downward Pipe
	.byte $40 | $13, $21, $E2; White Turtle Bricks
	.byte $40 | $15, $2A, $42; Bridge
	.byte $00 | $11, $30, $10; Giant cloud platform
	.byte $40 | $15, $30, $47; Bridge
	.byte $00 | $17, $38, $60; Giant Metal Blocks
	.byte $00 | $14, $3C, $84; Giant Downward Pipe
	.byte $20 | $15, $43, $40; Wooden blocks
	.byte $20 | $16, $43, $40; Wooden blocks
	.byte $20 | $17, $43, $40; Wooden blocks
	.byte $20 | $18, $43, $40; Wooden blocks
	.byte $20 | $12, $44, $10; Bricks
	.byte $20 | $13, $44, $10; Bricks
	.byte $20 | $14, $44, $10; Bricks
	.byte $20 | $15, $44, $10; Bricks
	.byte $20 | $16, $44, $10; Bricks
	.byte $20 | $17, $44, $10; Bricks
	.byte $20 | $18, $44, $10; Bricks
	.byte $40 | $16, $45, $08; P-Switch
	.byte $20 | $17, $45, $40; Wooden blocks
	.byte $20 | $18, $45, $40; Wooden blocks
	.byte $40 | $15, $4A, $45; Bridge
	.byte $20 | $11, $4A, $02; '?' with star
	.byte $20 | $12, $4A, $13; Bricks
	.byte $00 | $16, $47, $84; Giant Downward Pipe
	.byte $00 | $14, $50, $84; Giant Downward Pipe
	.byte $40 | $15, $53, $45; Bridge
	.byte $40 | $15, $5C, $46; Bridge
	.byte $20 | $13, $54, $13; Bricks
	.byte $20 | $12, $5E, $12; Bricks
	.byte $00 | $16, $59, $82; Giant Downward Pipe
	.byte $20 | $12, $58, $80; Coins
	.byte $20 | $13, $58, $80; Coins
	.byte $20 | $14, $58, $80; Coins
	.byte $20 | $12, $62, $80; Coins
	.byte $20 | $13, $62, $80; Coins
	.byte $20 | $14, $62, $80; Coins
	.byte $00 | $10, $65, $10; Giant cloud platform
	.byte $40 | $15, $66, $47; Bridge
	.byte $00 | $16, $63, $82; Giant Downward Pipe
	.byte $00 | $13, $6E, $60; Giant Metal Blocks
	.byte $00 | $15, $6E, $60; Giant Metal Blocks
	.byte $00 | $17, $6E, $60; Giant Metal Blocks
	.byte $20 | $14, $70, $44; Wooden blocks
	.byte $00 | $15, $7A, $61; Giant Metal Blocks
	.byte $60 | $13, $7B, $62; Rightward Pipe to End of Level
	.byte $00 | $01, $7E, $60; Giant Metal Blocks
	.byte $00 | $03, $7E, $60; Giant Metal Blocks
	.byte $00 | $05, $7E, $60; Giant Metal Blocks
	.byte $00 | $07, $7E, $60; Giant Metal Blocks
	.byte $00 | $09, $7E, $60; Giant Metal Blocks
	.byte $00 | $0B, $7E, $60; Giant Metal Blocks
	.byte $00 | $0D, $7E, $60; Giant Metal Blocks
	.byte $00 | $0F, $7E, $60; Giant Metal Blocks
	.byte $00 | $11, $7E, $60; Giant Metal Blocks
	.byte $00 | $13, $7E, $60; Giant Metal Blocks
	.byte $00 | $15, $7E, $60; Giant Metal Blocks
	.byte $00 | $17, $7E, $60; Giant Metal Blocks
	.byte $00 | $19, $7E, $60; Giant Metal Blocks
	.byte $40 | $19, $00, $81, $80; Water (still)
	; Pointer on screen $07
	.byte $E0 | $07, $70 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_2_W4_objects:
	.byte $D3, $00, $52; Autoscrolling
	.byte $D4, $01, $18; White Mushroom House (X pos must be uneven, Y pos=amount of coins required)
	.byte $7B, $10, $14; Giant Red Koopa Troopa
	.byte $3B, $12, $19; Surface Cheep-Cheep (swims along surface)
	.byte $7B, $16, $15; Giant Red Koopa Troopa
	.byte $7F, $1B, $16; Giant Red Piranha Plant
	.byte $A6, $2E, $16; Red Venus Fire Trap (upward)
	.byte $A6, $3C, $14; Red Venus Fire Trap (upward)
	.byte $BB, $48, $19; Stops infinite flying or spiny Cheep-Cheeps
	.byte $7F, $50, $14; Giant Red Piranha Plant
	.byte $B4, $5C, $19; Infinite flying Cheep-Cheeps
	.byte $7F, $63, $16; Giant Red Piranha Plant
	.byte $B4, $65, $19; Infinite flying Cheep-Cheeps
	.byte $BB, $7C, $19; Stops infinite flying or spiny Cheep-Cheeps
	.byte $FF
; Level_4_W4
; Object Set 11
Level_4_W4_generators:
Level_4_W4_header:
	.byte $34; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_000; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0B; Start action | Graphic set
	.byte $00 | $02; Time | Music
	.byte $40 | $0E, $00, $8C, $7F; Water (still)
	.byte $40 | $05, $00, $8B, $16; Water (still)
	.byte $00 | $07, $00, $52; Giant Wooden Blocks
	.byte $00 | $09, $00, $52; Giant Wooden Blocks
	.byte $00 | $0B, $00, $52; Giant Wooden Blocks
	.byte $00 | $0D, $00, $52; Giant Wooden Blocks
	.byte $00 | $0F, $00, $52; Giant Wooden Blocks
	.byte $00 | $11, $00, $52; Giant Wooden Blocks
	.byte $00 | $13, $00, $52; Giant Wooden Blocks
	.byte $00 | $0B, $08, $50; Giant Wooden Blocks
	.byte $00 | $17, $0C, $51; Giant Wooden Blocks
	.byte $00 | $09, $08, $90; Giant Underwater Coral
	.byte $00 | $13, $0E, $91; Giant Underwater Coral
	.byte $00 | $19, $00, $74; Giant Ground
	.byte $00 | $19, $0C, $71; Giant Ground
	.byte $00 | $19, $12, $70; Giant Ground
	.byte $00 | $19, $16, $78; Giant Ground
	.byte $20 | $15, $02, $C1; Upward Pipe (CAN go up)
	.byte $20 | $17, $06, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $01, $16, $53; Giant Wooden Blocks
	.byte $00 | $03, $16, $53; Giant Wooden Blocks
	.byte $00 | $05, $16, $53; Giant Wooden Blocks
	.byte $00 | $07, $16, $53; Giant Wooden Blocks
	.byte $00 | $09, $16, $53; Giant Wooden Blocks
	.byte $00 | $0B, $16, $53; Giant Wooden Blocks
	.byte $00 | $0D, $16, $53; Giant Wooden Blocks
	.byte $00 | $0F, $16, $53; Giant Wooden Blocks
	.byte $00 | $11, $16, $53; Giant Wooden Blocks
	.byte $00 | $13, $16, $53; Giant Wooden Blocks
	.byte $00 | $0B, $12, $50; Giant Wooden Blocks
	.byte $00 | $0D, $12, $50; Giant Wooden Blocks
	.byte $00 | $0F, $12, $50; Giant Wooden Blocks
	.byte $00 | $11, $12, $50; Giant Wooden Blocks
	.byte $00 | $13, $12, $50; Giant Wooden Blocks
	.byte $00 | $15, $12, $50; Giant Wooden Blocks
	.byte $00 | $17, $12, $50; Giant Wooden Blocks
	.byte $20 | $0B, $11, $00; '?' with flower
	.byte $00 | $19, $2C, $77; Giant Ground
	.byte $00 | $13, $26, $50; Giant Wooden Blocks
	.byte $00 | $13, $2C, $50; Giant Wooden Blocks
	.byte $00 | $15, $20, $91; Giant Underwater Coral
	.byte $20 | $17, $24, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $19, $3E, $74; Giant Ground
	.byte $00 | $11, $3A, $50; Giant Wooden Blocks
	.byte $00 | $13, $3A, $50; Giant Wooden Blocks
	.byte $00 | $15, $3A, $50; Giant Wooden Blocks
	.byte $00 | $15, $32, $52; Giant Wooden Blocks
	.byte $00 | $13, $34, $90; Giant Underwater Coral
	.byte $00 | $11, $4C, $50; Giant Wooden Blocks
	.byte $00 | $13, $46, $50; Giant Wooden Blocks
	.byte $00 | $15, $40, $50; Giant Wooden Blocks
	.byte $00 | $15, $4C, $50; Giant Wooden Blocks
	.byte $00 | $19, $4E, $72; Giant Ground
	.byte $20 | $17, $44, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $0D, $52, $50; Giant Wooden Blocks
	.byte $00 | $11, $5C, $50; Giant Wooden Blocks
	.byte $00 | $15, $5C, $50; Giant Wooden Blocks
	.byte $00 | $17, $5C, $50; Giant Wooden Blocks
	.byte $00 | $17, $50, $90; Giant Underwater Coral
	.byte $00 | $19, $5A, $72; Giant Ground
	.byte $00 | $11, $64, $50; Giant Wooden Blocks
	.byte $00 | $13, $60, $50; Giant Wooden Blocks
	.byte $00 | $13, $68, $50; Giant Wooden Blocks
	.byte $00 | $13, $64, $50; Giant Wooden Blocks
	.byte $00 | $15, $64, $50; Giant Wooden Blocks
	.byte $00 | $0F, $64, $50; Giant Wooden Blocks
	.byte $00 | $17, $68, $50; Giant Wooden Blocks
	.byte $00 | $19, $66, $72; Giant Ground
	.byte $00 | $01, $7E, $50; Giant Wooden Blocks
	.byte $00 | $03, $7E, $50; Giant Wooden Blocks
	.byte $00 | $05, $7E, $50; Giant Wooden Blocks
	.byte $00 | $07, $7E, $50; Giant Wooden Blocks
	.byte $00 | $09, $7E, $50; Giant Wooden Blocks
	.byte $00 | $0B, $7E, $50; Giant Wooden Blocks
	.byte $00 | $0D, $7E, $50; Giant Wooden Blocks
	.byte $00 | $0F, $7E, $50; Giant Wooden Blocks
	.byte $00 | $11, $7A, $52; Giant Wooden Blocks
	.byte $00 | $13, $78, $53; Giant Wooden Blocks
	.byte $00 | $15, $76, $54; Giant Wooden Blocks
	.byte $00 | $17, $74, $55; Giant Wooden Blocks
	.byte $00 | $19, $72, $76; Giant Ground
	.byte $60 | $0F, $7C, $61; Rightward Pipe to End of Level
	; Pointer on screen $00
	.byte $E0 | $00, $70 | $01, 16; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_4_W4_objects:
	.byte $65, $06, $17; Upward Current
	.byte $83, $0F, $03; Lakitu
	.byte $B6, $16, $03; Lakitu boundary
	.byte $B6, $27, $0B; Lakitu boundary
	.byte $83, $30, $0B; Lakitu
	.byte $65, $44, $17; Upward Current
	.byte $FF
; Pipe_1_End_2_W4
; Object Set 14
Pipe_1_End_2_W4_generators:
Pipe_1_End_2_W4_header:
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
Pipe_1_End_2_W4_objects:
	.byte $25, $02, $15; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Level_1_W4
; Object Set 11
Level_1_W4_generators:
Level_1_W4_header:
	.byte $35; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_11; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0B; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $19, $00, $7F; Giant Ground
	.byte $00 | $15, $03, $05; Background Mountain
	.byte $00 | $11, $08, $10; Giant cloud platform
	.byte $00 | $16, $07, $82; Giant Downward Pipe
	.byte $00 | $16, $0C, $82; Giant Downward Pipe
	.byte $00 | $03, $0E, $50; Giant Wooden Blocks
	.byte $00 | $05, $0E, $50; Giant Wooden Blocks
	.byte $00 | $07, $0E, $50; Giant Wooden Blocks
	.byte $20 | $09, $0F, $40; Wooden blocks
	.byte $40 | $03, $10, $85, $1B; Water (still)
	.byte $40 | $03, $2C, $83, $01; Water (still)
	.byte $40 | $03, $2E, $81, $0B; Water (still)
	.byte $40 | $03, $3A, $83, $09; Water (still)
	.byte $20 | $07, $12, $91; Downward Pipe (CAN go down)
	.byte $00 | $09, $10, $5D; Giant Wooden Blocks
	.byte $00 | $15, $1E, $40; Giant '?' blocks with leafs
	.byte $00 | $13, $14, $30; Giant '?' blocks with coins
	.byte $00 | $15, $12, $05; Background Mountain
	.byte $00 | $17, $18, $20; Giant bricks
	.byte $00 | $19, $1F, $70; Giant Ground
	.byte $00 | $17, $1E, $20; Giant bricks
	.byte $00 | $17, $1A, $50; Giant Wooden Blocks
	.byte $20 | $15, $21, $82; Coins
	.byte $00 | $11, $24, $10; Giant cloud platform
	.byte $00 | $19, $23, $7F; Giant Ground
	.byte $00 | $12, $2B, $05; Background Mountain
	.byte $20 | $07, $26, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $07, $2C, $50; Giant Wooden Blocks
	.byte $00 | $05, $2E, $50; Giant Wooden Blocks
	.byte $20 | $17, $23, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $07, $2E, $40; Wooden blocks
	.byte $20 | $09, $2C, $40; Wooden blocks
	.byte $20 | $0A, $34, $10; Bricks
	.byte $00 | $11, $3E, $20; Giant bricks
	.byte $00 | $16, $38, $05; Background Mountain
	.byte $20 | $16, $3B, $10; Bricks
	.byte $20 | $17, $3B, $10; Bricks
	.byte $20 | $18, $3B, $10; Bricks
	.byte $40 | $05, $32, $67, $03; Waterfall
	.byte $40 | $11, $32, $64, $03; Waterfall
	.byte $20 | $05, $30, $41; Wooden blocks
	.byte $20 | $05, $36, $41; Wooden blocks
	.byte $00 | $05, $38, $50; Giant Wooden Blocks
	.byte $00 | $07, $38, $55; Giant Wooden Blocks
	.byte $20 | $07, $3A, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $09, $3A, $41; Wooden blocks
	.byte $20 | $16, $32, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $34, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $0D, $32, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $0D, $34, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $0F, $32, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $0F, $34, $D1; Upward Pipe (CAN'T go up)
	.byte $00 | $16, $4F, $82; Giant Downward Pipe
	.byte $00 | $14, $40, $05; Background Mountain
	.byte $00 | $19, $42, $77; Giant Ground
	.byte $20 | $15, $42, $30; Bricks with single coins
	.byte $00 | $11, $42, $40; Giant '?' blocks with leafs
	.byte $00 | $03, $44, $50; Giant Wooden Blocks
	.byte $00 | $05, $44, $50; Giant Wooden Blocks
	.byte $20 | $03, $48, $41; Wooden blocks
	.byte $00 | $0F, $48, $20; Giant bricks
	.byte $00 | $11, $48, $20; Giant bricks
	.byte $00 | $15, $48, $20; Giant bricks
	.byte $00 | $17, $48, $20; Giant bricks
	.byte $20 | $15, $5E, $82; Coins
	.byte $00 | $11, $4C, $10; Giant cloud platform
	.byte $20 | $07, $44, $40; Wooden blocks
	.byte $00 | $14, $54, $10; Giant cloud platform
	.byte $00 | $15, $58, $11; Giant cloud platform
	.byte $00 | $17, $5E, $21; Giant bricks
	.byte $00 | $13, $6A, $87; Giant Downward Pipe
	.byte $00 | $15, $64, $30; Giant '?' blocks with coins
	.byte $00 | $19, $72, $76; Giant Ground
	.byte $00 | $15, $72, $83; Giant Downward Pipe
	.byte $00 | $16, $78, $05; Background Mountain
	.byte $00 | $11, $78, $10; Giant cloud platform
	.byte $60 | $17, $7C, $61; Rightward Pipe to End of Level
	.byte $20 | $00, $7E, $41; Wooden blocks
	.byte $00 | $01, $7E, $50; Giant Wooden Blocks
	.byte $00 | $03, $7E, $50; Giant Wooden Blocks
	.byte $00 | $05, $7E, $50; Giant Wooden Blocks
	.byte $00 | $07, $7E, $50; Giant Wooden Blocks
	.byte $00 | $09, $7E, $50; Giant Wooden Blocks
	.byte $00 | $0B, $7E, $50; Giant Wooden Blocks
	.byte $00 | $0D, $7E, $50; Giant Wooden Blocks
	.byte $00 | $0F, $7E, $50; Giant Wooden Blocks
	.byte $00 | $11, $7E, $50; Giant Wooden Blocks
	.byte $00 | $13, $7E, $50; Giant Wooden Blocks
	.byte $00 | $15, $7E, $50; Giant Wooden Blocks
	.byte $00 | $17, $7E, $50; Giant Wooden Blocks
	; Pointer on screen $01
	.byte $E0 | $01, $40 | $02, 112; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_1_W4_objects:
	.byte $7F, $0C, $16; Giant Red Piranha Plant
	.byte $7C, $10, $17; Giant Goomba
	.byte $7B, $18, $15; Giant Red Koopa Troopa
	.byte $A6, $26, $07; Red Venus Fire Trap (upward)
	.byte $7E, $30, $17; Giant Green Koopa Paratroopa
	.byte $7C, $42, $0F; Giant Goomba
	.byte $7E, $46, $11; Giant Green Koopa Paratroopa
	.byte $7B, $58, $13; Giant Red Koopa Troopa
	.byte $7B, $5F, $15; Giant Red Koopa Troopa
	.byte $7B, $64, $13; Giant Red Koopa Troopa
	.byte $A6, $72, $15; Red Venus Fire Trap (upward)
	.byte $7A, $7A, $17; Giant Green Koopa Troopa
	.byte $FF
; Hammer_Bros_1_W5
; Object Set 3
Hammer_Bros_1_W5_generators:
Hammer_Bros_1_W5_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $13; Start action | Graphic set
	.byte $80 | $06; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $40 | $13, $00, $0C; Background Hills C
	.byte $40 | $17, $0C, $0B; Background Hills B
	.byte $20 | $12, $07, $16; Bricks
	.byte $20 | $16, $07, $16; Bricks
	.byte $80 | $1A, $00, $80, $0F; Flat Land - Hilly
	.byte $FF
Hammer_Bros_1_W5_objects:
	.byte $81, $0C, $14; Hammer Brother
	.byte $81, $09, $18; Hammer Brother
	.byte $BA, $0D, $14; Exit on get treasure chest
	.byte $FF
; Level_2_W5
; Object Set 14
Level_2_W5_generators:
Level_2_W5_header:
	.byte $36; Next Level
	.byte LEVEL1_SIZE_15 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_06; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_08; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0D; Sky Fill
	.byte $20 | $00, $00, $4F; Wooden blocks
	.byte $20 | $00, $10, $4F; Wooden blocks
	.byte $20 | $00, $20, $4F; Wooden blocks
	.byte $20 | $00, $30, $4F; Wooden blocks
	.byte $20 | $00, $40, $4F; Wooden blocks
	.byte $20 | $00, $50, $4F; Wooden blocks
	.byte $20 | $00, $60, $4F; Wooden blocks
	.byte $00 | $15, $07, $23; 45 Degree Aboveground Hill - Down/Left
	.byte $80 | $19, $00, $71, $03; Flat Land - Aboveground
	.byte $80 | $19, $04, $41, $03; Aboveground Fill
	.byte $80 | $15, $08, $75, $03; Flat Land - Aboveground
	.byte $80 | $00, $0C, $4F, $13; Aboveground Fill
	.byte $80 | $10, $0C, $4A, $13; Aboveground Fill
	.byte $00 | $00, $0C, $DF; Aboveground Wall - Left Side
	.byte $00 | $10, $0C, $D4; Aboveground Wall - Left Side
	.byte $60 | $15, $08, $D5; Aboveground Wall - Right Side
	.byte $00 | $15, $0B, $D5; Aboveground Wall - Left Side
	.byte $00 | $15, $08, $03; Upper Right Hill Corner - Aboveground
	.byte $00 | $15, $0B, $00; Upper Left Hill Corner - Aboveground
	.byte $20 | $12, $09, $98; Downward Pipe (CAN go down)
	.byte $80 | $10, $01, $00; Small Background Cloud
	.byte $80 | $0F, $08, $00; Small Background Cloud
	.byte $60 | $00, $1F, $DF; Aboveground Wall - Right Side
	.byte $60 | $10, $1F, $D7; Aboveground Wall - Right Side
	.byte $80 | $03, $2E, $00; Small Background Cloud
	.byte $80 | $06, $24, $00; Small Background Cloud
	.byte $80 | $09, $2A, $00; Small Background Cloud
	.byte $80 | $14, $2B, $00; Small Background Cloud
	.byte $80 | $18, $20, $72, $04; Flat Land - Aboveground
	.byte $00 | $18, $21, $03; Upper Right Hill Corner - Aboveground
	.byte $00 | $18, $24, $00; Upper Left Hill Corner - Aboveground
	.byte $60 | $19, $21, $D1; Aboveground Wall - Right Side
	.byte $00 | $19, $24, $D1; Aboveground Wall - Left Side
	.byte $20 | $17, $22, $A3; Downward Pipe (CAN'T go down)
	.byte $80 | $18, $25, $42, $0F; Aboveground Fill
	.byte $00 | $15, $25, $00; Upper Left Hill Corner - Aboveground
	.byte $00 | $16, $25, $D1; Aboveground Wall - Left Side
	.byte $80 | $15, $26, $42, $08; Aboveground Fill
	.byte $80 | $12, $26, $72, $02; Flat Land - Aboveground
	.byte $00 | $12, $26, $00; Upper Left Hill Corner - Aboveground
	.byte $00 | $13, $26, $D1; Aboveground Wall - Left Side
	.byte $60 | $12, $29, $12; 30 Degree Aboveground Hill - Down/Right
	.byte $00 | $15, $2F, $12; 45 Degree Aboveground Hill - Down/Right
	.byte $80 | $05, $37, $00; Small Background Cloud
	.byte $80 | $09, $33, $00; Small Background Cloud
	.byte $80 | $18, $32, $72, $00; Flat Land - Aboveground
	.byte $00 | $17, $33, $20; 45 Degree Aboveground Hill - Down/Left
	.byte $00 | $17, $34, $03; Upper Right Hill Corner - Aboveground
	.byte $80 | $18, $35, $72, $02; Flat Land - Aboveground
	.byte $00 | $13, $3C, $24; 45 Degree Aboveground Hill - Down/Left
	.byte $80 | $18, $38, $42, $05; Aboveground Fill
	.byte $80 | $13, $3D, $77, $00; Flat Land - Aboveground
	.byte $80 | $13, $31, $00; Small Background Cloud
	.byte $00 | $13, $3E, $16; 45 Degree Aboveground Hill - Down/Right
	.byte $80 | $1A, $3E, $40, $B1; Aboveground Fill
	.byte $80 | $17, $4D, $41, $02; Aboveground Fill
	.byte $80 | $12, $4E, $41, $04; Aboveground Fill
	.byte $00 | $15, $4D, $21; 45 Degree Aboveground Hill - Down/Left
	.byte $00 | $10, $4F, $21; 45 Degree Aboveground Hill - Down/Left
	.byte $00 | $12, $4E, $D2; Aboveground Wall - Left Side
	.byte $80 | $15, $44, $00; Small Background Cloud
	.byte $80 | $12, $4A, $00; Small Background Cloud
	.byte $20 | $17, $49, $B2; Downward Pipe (CAN go down, ignores pointers)
	.byte $80 | $1A, $45, $70, $06; Flat Land - Aboveground
	.byte $00 | $17, $4C, $D2; Aboveground Wall - Left Side
	.byte $80 | $13, $4E, $43, $01; Aboveground Fill
	.byte $00 | $12, $4E, $D2; Aboveground Wall - Left Side
	.byte $00 | $19, $46, $20; 45 Degree Aboveground Hill - Down/Left
	.byte $00 | $19, $47, $03; Upper Right Hill Corner - Aboveground
	.byte $80 | $1A, $46, $40, $01; Aboveground Fill
	.byte $80 | $1A, $49, $40, $01; Aboveground Fill
	.byte $80 | $04, $44, $00; Small Background Cloud
	.byte $80 | $19, $4D, $40, $02; Aboveground Fill
	.byte $80 | $10, $50, $79, $03; Flat Land - Aboveground
	.byte $60 | $10, $53, $D9; Aboveground Wall - Right Side
	.byte $80 | $1A, $54, $70, $04; Flat Land - Aboveground
	.byte $00 | $17, $5B, $22; 45 Degree Aboveground Hill - Down/Left
	.byte $80 | $17, $5C, $72, $04; Flat Land - Aboveground
	.byte $80 | $15, $59, $00; Small Background Cloud
	.byte $20 | $17, $56, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $13, $5D, $22; '?' blocks with single coins
	.byte $20 | $16, $5C, $20; '?' blocks with single coins
	.byte $00 | $10, $53, $03; Upper Right Hill Corner - Aboveground
	.byte $60 | $10, $53, $D9; Aboveground Wall - Right Side
	.byte $00 | $10, $53, $03; Upper Right Hill Corner - Aboveground
	.byte $00 | $17, $61, $12; 45 Degree Aboveground Hill - Down/Right
	.byte $80 | $1A, $64, $70, $01; Flat Land - Aboveground
	.byte $00 | $18, $67, $21; 45 Degree Aboveground Hill - Down/Left
	.byte $80 | $18, $68, $71, $05; Flat Land - Aboveground
	.byte $80 | $00, $6E, $4D, $09; Aboveground Fill
	.byte $80 | $0E, $6E, $44, $09; Aboveground Fill
	.byte $80 | $13, $6E, $47, $09; Aboveground Fill
	.byte $00 | $00, $6E, $DF; Aboveground Wall - Left Side
	.byte $00 | $10, $6E, $D2; Aboveground Wall - Left Side
	.byte $00 | $13, $6E, $D4; Aboveground Wall - Left Side
	.byte $80 | $00, $6C, $EF; Upward Pipe to End of Level
	.byte $80 | $0F, $6C, $E6; Upward Pipe to End of Level
	.byte $80 | $00, $78, $2D, $17; Underground Fill
	.byte $80 | $0E, $78, $2C, $77; Underground Fill
	.byte $80 | $00, $78, $5D, $0D; Hilly Fill
	.byte $80 | $0E, $78, $5B, $07; Hilly Fill
	.byte $60 | $11, $7F, $E5; Hilly Wall - Right Side
	.byte $60 | $17, $7F, $F2; Underground Wall - Right Side
	.byte $80 | $1A, $78, $50, $77; Hilly Fill
	.byte $80 | $17, $80, $32, $0B; Water
	.byte $60 | $0E, $80, $82; 30 Degree Hill - Up/Right
	.byte $60 | $06, $85, $E7; Hilly Wall - Right Side
	.byte $00 | $04, $86, $81; 45 Degree Hill - Up/Right
	.byte $60 | $00, $87, $E3; Hilly Wall - Right Side
	.byte $80 | $00, $86, $53, $00; Hilly Fill
	.byte $80 | $1A, $80, $90, $0A; Flat Land - Underwater
	.byte $00 | $19, $8B, $A0; 45 Degree Underwater Hill - Down/Left
	.byte $80 | $17, $8C, $62, $13; Underground Fill
	.byte $00 | $17, $8C, $F1; Underground Wall - Left Side
	.byte $60 | $15, $8E, $61; 30 Degree Hill - Down/Left
	.byte $80 | $00, $8A, $53, $01; Hilly Fill
	.byte $80 | $00, $8C, $5E, $03; Hilly Fill
	.byte $00 | $00, $8A, $E3; Hilly Wall - Left Side
	.byte $00 | $04, $8A, $71; 45 Degree Hill - Up/Left
	.byte $00 | $06, $8C, $E8; Hilly Wall - Left Side
	.byte $60 | $0F, $8C, $71; 30 Degree Hill - Up/Left
	.byte $20 | $00, $88, $D5; Upward Pipe (CAN'T go up)
	.byte $40 | $15, $88, $61, $01; Waterfall
	.byte $40 | $06, $88, $6F, $01; Waterfall
	.byte $80 | $00, $90, $55, $5C; Hilly Fill
	.byte $80 | $06, $90, $5A, $5C; Hilly Fill
	.byte $80 | $15, $90, $81, $0F; Flat Land - Hilly
	.byte $80 | $10, $90, $B0, $11; Ceiling - Hilly
	.byte $20 | $11, $99, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $11, $9D, $D1; Upward Pipe (CAN'T go up)
	.byte $40 | $14, $93, $E0; White Turtle Bricks
	.byte $40 | $14, $97, $E0; White Turtle Bricks
	.byte $00 | $15, $A0, $54; 45 Degree Hill - Down/Right
	.byte $80 | $1A, $A5, $80, $12; Flat Land - Hilly
	.byte $80 | $11, $A6, $B3, $09; Ceiling - Hilly
	.byte $20 | $15, $A8, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $15, $AE, $D1; Upward Pipe (CAN'T go up)
	.byte $00 | $11, $A2, $73; 45 Degree Hill - Up/Left
	.byte $40 | $19, $A8, $E0; White Turtle Bricks
	.byte $40 | $19, $AC, $E0; White Turtle Bricks
	.byte $60 | $11, $B0, $83; 30 Degree Hill - Up/Right
	.byte $80 | $10, $B8, $B0, $20; Ceiling - Hilly
	.byte $60 | $16, $BE, $63; 30 Degree Hill - Down/Left
	.byte $20 | $17, $B4, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $15, $B8, $22; '?' blocks with single coins
	.byte $80 | $16, $C0, $83, $06; Flat Land - Hilly
	.byte $80 | $1A, $CB, $80, $0A; Flat Land - Hilly
	.byte $00 | $16, $C7, $53; 45 Degree Hill - Down/Right
	.byte $20 | $15, $CC, $15; Bricks
	.byte $40 | $15, $C0, $E1; White Turtle Bricks
	.byte $40 | $19, $CC, $E1; White Turtle Bricks
	.byte $40 | $14, $CD, $E1; White Turtle Bricks
	.byte $20 | $15, $CD, $41; Wooden blocks
	.byte $40 | $15, $C5, $E0; White Turtle Bricks
	.byte $60 | $19, $D6, $60; 30 Degree Hill - Down/Left
	.byte $60 | $19, $DF, $60; 30 Degree Hill - Down/Left
	.byte $60 | $19, $D8, $50; 30 Degree Hill - Down/Right
	.byte $80 | $1A, $DA, $80, $04; Flat Land - Hilly
	.byte $80 | $11, $DB, $B1, $04; Ceiling - Hilly
	.byte $00 | $11, $D9, $71; 45 Degree Hill - Up/Left
	.byte $60 | $02, $DF, $EF; Hilly Wall - Right Side
	.byte $00 | $12, $DF, $0A; Lower Right Hill Corner
	.byte $60 | $01, $D6, $EF; Hilly Wall - Right Side
	.byte $00 | $01, $D9, $EF; Hilly Wall - Left Side
	.byte $00 | $10, $D6, $0A; Lower Right Hill Corner
	.byte $40 | $19, $D3, $E0; White Turtle Bricks
	.byte $40 | $19, $DC, $E1; White Turtle Bricks
	.byte $40 | $14, $D0, $E0; White Turtle Bricks
	.byte $20 | $00, $D7, $DF; Upward Pipe (CAN'T go up)
	.byte $20 | $0E, $D7, $D7; Upward Pipe (CAN'T go up)
	.byte $20 | $15, $D0, $41; Wooden blocks
	.byte $40 | $19, $D0, $E0; White Turtle Bricks
	.byte $80 | $10, $E0, $B0, $01; Ceiling - Hilly
	.byte $00 | $02, $E2, $EF; Hilly Wall - Left Side
	.byte $00 | $12, $E2, $07; Lower Left Corner - Hilly
	.byte $80 | $12, $E3, $B0, $05; Ceiling - Hilly
	.byte $60 | $11, $E9, $81; 30 Degree Hill - Up/Right
	.byte $60 | $00, $EC, $EF; Hilly Wall - Right Side
	.byte $60 | $10, $EC, $E0; Hilly Wall - Right Side
	.byte $00 | $00, $EF, $EF; Hilly Wall - Left Side
	.byte $00 | $10, $EF, $E6; Hilly Wall - Left Side
	.byte $60 | $17, $ED, $62; 30 Degree Hill - Down/Left
	.byte $80 | $1A, $E3, $80, $05; Flat Land - Hilly
	.byte $60 | $19, $E1, $50; 30 Degree Hill - Down/Right
	.byte $20 | $00, $E0, $DF; Upward Pipe (CAN'T go up)
	.byte $20 | $0E, $E0, $D7; Upward Pipe (CAN'T go up)
	.byte $80 | $05, $ED, $EF; Upward Pipe to End of Level
	.byte $80 | $11, $E3, $50, $05; Hilly Fill
	.byte $80 | $17, $EF, $53, $00; Hilly Fill
	; Pointer on screen $00
	.byte $E0 | $00, $80 | $02, 32; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $04
	.byte $E0 | $04, $00 | $02, 115; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_2_W5_objects:
	.byte $72, $2E, $13; Goomba
	.byte $72, $30, $15; Goomba
	.byte $72, $31, $16; Goomba
	.byte $72, $42, $16; Goomba
	.byte $72, $43, $17; Goomba
	.byte $6E, $60, $16; Green Koopa Paratroopa (bounces)
	.byte $77, $84, $18; Cheep-Cheep
	.byte $40, $95, $14; Buster Beetle
	.byte $A1, $99, $12; Green Piranha Plant (downward)
	.byte $A1, $9D, $12; Green Piranha Plant (downward)
	.byte $A5, $A8, $16; Green Venus Fire Trap (downward)
	.byte $A3, $AE, $16; Red Piranha Plant (downward)
	.byte $40, $AA, $19; Buster Beetle
	.byte $A6, $B4, $17; Red Venus Fire Trap (upward)
	.byte $40, $C4, $15; Buster Beetle
	.byte $40, $CF, $14; Buster Beetle
	.byte $40, $D2, $19; Buster Beetle
	.byte $A3, $D7, $15; Red Piranha Plant (downward)
	.byte $A3, $E0, $15; Red Piranha Plant (downward)
	.byte $40, $E0, $18; Buster Beetle
	.byte $40, $EA, $18; Buster Beetle
	.byte $FF
; Level_3_Beginning_W5
; Object Set 1
Level_3_Beginning_W5_generators:
Level_3_Beginning_W5_header:
	.byte $37; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_070; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $0B, $00, $C5, $0F; Flat Ground
	.byte $40 | $09, $00, $B1, $02; Blue X-Blocks
	.byte $00 | $0A, $05, $93; Background Bushes
	.byte $00 | $04, $02, $E2; Background Clouds
	.byte $00 | $03, $0A, $E2; Background Clouds
	.byte $00 | $05, $07, $07; Small Background Cloud
	.byte $20 | $08, $09, $92; Downward Pipe (CAN go down)
	.byte $40 | $00, $0E, $BA, $01; Blue X-Blocks
	; Pointer on screen $00
	.byte $E0 | $00, $00 | $02, 103; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_3_Beginning_W5_objects:
	.byte $FF
; Level_1_W5
; Object Set 1
Level_1_W5_generators:
Level_1_W5_header:
	.byte $39; Next Level
	.byte LEVEL1_SIZE_09 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $00, $00, $03; White Mushrooms, Flowers and Stars
	.byte $00 | $1A, $00, $C0, $19; Flat Ground
	.byte $40 | $19, $1A, $81, $41; Water (still)
	.byte $00 | $16, $02, $00; Background Hills A
	.byte $40 | $19, $08, $B0, $00; Blue X-Blocks
	.byte $20 | $19, $09, $13; Bricks
	.byte $20 | $18, $0C, $10; Bricks
	.byte $00 | $09, $07, $E2; Background Clouds
	.byte $00 | $12, $0A, $E2; Background Clouds
	.byte $40 | $04, $0C, $B0, $01; Blue X-Blocks
	.byte $20 | $05, $0C, $C2; Upward Pipe (CAN go up)
	.byte $20 | $18, $0D, $11; Bricks
	.byte $40 | $17, $0E, $05; Wooden Block with Leaf
	.byte $00 | $10, $04, $07; Small Background Cloud
	.byte $00 | $14, $08, $07; Small Background Cloud
	.byte $00 | $19, $12, $93; Background Bushes
	.byte $40 | $16, $12, $B0, $0F; Blue X-Blocks
	.byte $40 | $15, $14, $B0, $02; Blue X-Blocks
	.byte $40 | $14, $16, $B5, $00; Blue X-Blocks
	.byte $00 | $11, $14, $E2; Background Clouds
	.byte $40 | $12, $1A, $B0, $04; Blue X-Blocks
	.byte $00 | $11, $1B, $92; Background Bushes
	.byte $40 | $10, $1E, $B2, $00; Blue X-Blocks
	.byte $00 | $0A, $1C, $E2; Background Clouds
	.byte $40 | $10, $1F, $B0, $03; Blue X-Blocks
	.byte $20 | $19, $14, $40; Wooden Blocks
	.byte $20 | $15, $1A, $40; Wooden Blocks
	.byte $20 | $19, $19, $40; Wooden Blocks
	.byte $00 | $03, $12, $07; Small Background Cloud
	.byte $00 | $07, $1A, $07; Small Background Cloud
	.byte $00 | $0D, $16, $07; Small Background Cloud
	.byte $20 | $10, $20, $10; Bricks
	.byte $40 | $15, $22, $B1, $00; Blue X-Blocks
	.byte $40 | $11, $23, $B3, $00; Blue X-Blocks
	.byte $40 | $15, $23, $B0, $07; Blue X-Blocks
	.byte $20 | $13, $20, $01; '?' with Leaf
	.byte $40 | $11, $28, $B3, $00; Blue X-Blocks
	.byte $40 | $11, $29, $B0, $03; Blue X-Blocks
	.byte $40 | $0F, $2C, $B0, $03; Blue X-Blocks
	.byte $40 | $10, $2C, $B0, $00; Blue X-Blocks
	.byte $40 | $0E, $2E, $B0, $03; Blue X-Blocks
	.byte $00 | $09, $28, $E2; Background Clouds
	.byte $00 | $04, $2D, $E2; Background Clouds
	.byte $00 | $02, $26, $07; Small Background Cloud
	.byte $00 | $05, $28, $07; Small Background Cloud
	.byte $00 | $07, $21, $E3; Background Clouds
	.byte $00 | $0B, $24, $07; Small Background Cloud
	.byte $20 | $14, $27, $40; Wooden Blocks
	.byte $20 | $0A, $2C, $03; '?' with Continuous star
	.byte $20 | $06, $30, $82; Coins
	.byte $20 | $04, $34, $82; Coins
	.byte $40 | $0D, $30, $B0, $03; Blue X-Blocks
	.byte $40 | $0C, $32, $B0, $03; Blue X-Blocks
	.byte $00 | $0B, $32, $91; Background Bushes
	.byte $40 | $0B, $34, $B0, $03; Blue X-Blocks
	.byte $00 | $09, $36, $91; Background Bushes
	.byte $40 | $0A, $36, $B0, $03; Blue X-Blocks
	.byte $40 | $09, $38, $B0, $03; Blue X-Blocks
	.byte $40 | $08, $3A, $B0, $02; Blue X-Blocks
	.byte $40 | $07, $3C, $B0, $01; Blue X-Blocks
	.byte $40 | $06, $3D, $B0, $00; Blue X-Blocks
	.byte $20 | $07, $3E, $12; Bricks
	.byte $00 | $10, $3B, $E2; Background Clouds
	.byte $40 | $19, $35, $B1, $14; Blue X-Blocks
	.byte $00 | $16, $36, $01; Background Hills B
	.byte $20 | $17, $3A, $91; Downward Pipe (CAN go down)
	.byte $00 | $18, $3C, $91; Background Bushes
	.byte $00 | $02, $34, $07; Small Background Cloud
	.byte $00 | $12, $39, $07; Small Background Cloud
	.byte $00 | $14, $3F, $07; Small Background Cloud
	.byte $20 | $07, $3E, $0D; Brick with P-Switch
	.byte $20 | $15, $40, $40; Wooden Blocks
	.byte $20 | $16, $40, $40; Wooden Blocks
	.byte $20 | $16, $42, $16; Bricks
	.byte $20 | $16, $41, $0B; Brick with 1-up
	.byte $20 | $16, $43, $0B; Brick with 1-up
	.byte $20 | $16, $45, $0B; Brick with 1-up
	.byte $20 | $16, $47, $0B; Brick with 1-up
	.byte $00 | $18, $40, $97; Background Bushes
	.byte $00 | $12, $43, $E2; Background Clouds
	.byte $40 | $07, $41, $B0, $01; Blue X-Blocks
	.byte $40 | $09, $41, $B0, $05; Blue X-Blocks
	.byte $40 | $06, $43, $B2, $00; Blue X-Blocks
	.byte $40 | $09, $47, $B2, $00; Blue X-Blocks
	.byte $40 | $0B, $48, $B0, $07; Blue X-Blocks
	.byte $40 | $08, $43, $B0, $00; Blue X-Blocks
	.byte $00 | $0A, $49, $94; Background Bushes
	.byte $00 | $03, $45, $E2; Background Clouds
	.byte $20 | $06, $49, $25; '?' Blocks with single coins
	.byte $40 | $0A, $4F, $B0, $07; Blue X-Blocks
	.byte $20 | $08, $44, $40; Wooden Blocks
	.byte $20 | $06, $4C, $02; '?' with Star
	.byte $00 | $03, $4F, $07; Small Background Cloud
	.byte $40 | $06, $53, $B0, $01; Blue X-Blocks
	.byte $00 | $05, $56, $E2; Background Clouds
	.byte $40 | $0B, $56, $B2, $00; Blue X-Blocks
	.byte $20 | $0D, $57, $10; Bricks
	.byte $20 | $0E, $57, $10; Bricks
	.byte $20 | $0F, $57, $10; Bricks
	.byte $20 | $10, $57, $10; Bricks
	.byte $20 | $11, $57, $10; Bricks
	.byte $40 | $0D, $58, $B4, $00; Blue X-Blocks
	.byte $40 | $11, $59, $B0, $01; Blue X-Blocks
	.byte $40 | $12, $5A, $B3, $00; Blue X-Blocks
	.byte $40 | $15, $5B, $B0, $01; Blue X-Blocks
	.byte $40 | $16, $5C, $B3, $00; Blue X-Blocks
	.byte $00 | $1A, $5C, $C0, $33; Flat Ground
	.byte $00 | $10, $59, $91; Background Bushes
	.byte $00 | $14, $5B, $91; Background Bushes
	.byte $00 | $19, $5E, $96; Background Bushes
	.byte $20 | $09, $54, $41; Wooden Blocks
	.byte $00 | $08, $5A, $07; Small Background Cloud
	.byte $00 | $0D, $5D, $E3; Background Clouds
	.byte $00 | $11, $60, $E2; Background Clouds
	.byte $20 | $16, $62, $82; Coins
	.byte $00 | $12, $66, $02; Background Hills C
	.byte $20 | $16, $6C, $82; Coins
	.byte $00 | $19, $6D, $92; Background Bushes
	.byte $00 | $0F, $68, $07; Small Background Cloud
	.byte $00 | $13, $65, $07; Small Background Cloud
	.byte $00 | $13, $70, $E2; Background Clouds
	.byte $20 | $17, $71, $10; Bricks
	.byte $20 | $18, $71, $10; Bricks
	.byte $20 | $19, $71, $10; Bricks
	.byte $00 | $17, $72, $01; Background Hills B
	.byte $40 | $00, $7B, $09; Level Ending
	.byte $00 | $0F, $79, $07; Small Background Cloud
	.byte $00 | $11, $74, $07; Small Background Cloud
	.byte $40 | $0B, $3E, $53; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $0C, $3D, $55; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $0D, $3D, $51; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $0F, $3F, $52; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $10, $3F, $52; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $12, $3D, $51; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $13, $3D, $55; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $14, $3E, $53; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $0D, $41, $51; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $0E, $41, $51; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $11, $41, $51; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $12, $41, $51; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $0E, $4D, $53; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $0F, $4C, $55; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $10, $4C, $51; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $12, $4E, $52; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $13, $4E, $52; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $15, $4C, $51; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $16, $4C, $55; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $17, $4D, $53; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $10, $50, $51; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $11, $50, $51; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $14, $50, $51; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $15, $50, $51; Silver Coins (appear when you hit a P-Switch)
	; Pointer on screen $00
	.byte $E0 | $00, $20 | $01, 32; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $03
	.byte $E0 | $03, $50 | $02, 225; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_1_W5_objects:
	.byte $40, $0B, $18; Buster Beetle
	.byte $89, $14, $19; Chain Chomp
	.byte $89, $1A, $15; Chain Chomp
	.byte $89, $27, $14; Chain Chomp
	.byte $33, $30, $0C; Nipper Plant
	.byte $33, $34, $0A; Nipper Plant
	.byte $33, $3A, $07; Nipper Plant
	.byte $40, $3C, $06; Buster Beetle
	.byte $89, $44, $08; Chain Chomp
	.byte $89, $54, $09; Chain Chomp
	.byte $39, $63, $19; Walking Nipper Plant
	.byte $39, $68, $19; Walking Nipper Plant
	.byte $74, $6B, $0D; Para-Goomba with Micro-Goombas
	.byte $39, $6D, $19; Walking Nipper Plant
	.byte $41, $88, $15; Goal Card
	.byte $33, $88, $19; Nipper Plant
	.byte $FF
; Default_Level_180
; Object Set 14
Default_Level_180_generators:
Default_Level_180_header:
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
Default_Level_180_objects:
	.byte $25, $02, $17; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Default_Level_181
; Object Set 14
Default_Level_181_generators:
Default_Level_181_header:
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
Default_Level_181_objects:
	.byte $25, $02, $17; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Tower__Part_1__W5
; Object Set 2
Tower__Part_1__W5_generators:
Tower__Part_1__W5_header:
	.byte $3A; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_13; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $00 | $17, $00, $44; Dungeon background
	.byte $00 | $15, $05, $41; Dungeon background
	.byte $00 | $10, $07, $4F; Dungeon background
	.byte $00 | $10, $17, $4F; Dungeon background
	.byte $00 | $10, $27, $44; Dungeon background
	.byte $00 | $04, $24, $41; Dungeon background
	.byte $00 | $04, $0C, $41; Dungeon background
	.byte $00 | $00, $00, $F1, $16; Vertically oriented X-blocks
	.byte $00 | $08, $02, $F1, $0E; Vertically oriented X-blocks
	.byte $00 | $09, $04, $F0, $0D; Vertically oriented X-blocks
	.byte $00 | $0A, $05, $F0, $0A; Vertically oriented X-blocks
	.byte $00 | $0B, $06, $F0, $09; Vertically oriented X-blocks
	.byte $00 | $00, $02, $E0, $2D; Horizontally oriented X-blocks
	.byte $00 | $0B, $07, $E4, $24; Horizontally oriented X-blocks
	.byte $00 | $0A, $0C, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $17, $07, $E0, $09; Horizontally oriented X-blocks
	.byte $00 | $18, $06, $E0, $0A; Horizontally oriented X-blocks
	.byte $00 | $01, $0A, $E4, $01; Horizontally oriented X-blocks
	.byte $00 | $01, $0C, $E2, $01; Horizontally oriented X-blocks
	.byte $00 | $01, $0E, $E4, $01; Horizontally oriented X-blocks
	.byte $20 | $01, $02, $C3; Upward Pipe (CAN go up)
	.byte $00 | $04, $06, $70; Long dungeon windows
	.byte $00 | $01, $08, $20; Bottom of background with pillars B
	.byte $00 | $10, $0A, $21; Bottom of background with pillars B
	.byte $00 | $0A, $18, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $16, $1C, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $01, $12, $23; Bottom of background with pillars B
	.byte $00 | $06, $10, $61; Dungeon windows
	.byte $00 | $06, $1C, $61; Dungeon windows
	.byte $00 | $15, $14, $02; Rotodisc block
	.byte $00 | $15, $1C, $02; Rotodisc block
	.byte $00 | $0A, $24, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $10, $28, $E4, $00; Horizontally oriented X-blocks
	.byte $00 | $00, $2E, $F1, $18; Vertically oriented X-blocks
	.byte $00 | $16, $2C, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $17, $2B, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $18, $2A, $E0, $03; Horizontally oriented X-blocks
	.byte $00 | $01, $22, $E4, $01; Horizontally oriented X-blocks
	.byte $00 | $01, $24, $E2, $01; Horizontally oriented X-blocks
	.byte $00 | $01, $26, $E4, $01; Horizontally oriented X-blocks
	.byte $00 | $15, $23, $02; Rotodisc block
	.byte $00 | $15, $28, $02; Rotodisc block
	.byte $20 | $15, $23, $01; '?' with leaf
	.byte $40 | $08, $2C, $FA; Double-Ended Vertical Pipe
	; Pointer on screen $00
	.byte $E0 | $00, $50 | $01, 48; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Tower__Part_1__W5_objects:
	.byte $8A, $0C, $04; Thwomp (normal)
	.byte $5B, $14, $15; Single Rotodisc (rotates counterclockwise)
	.byte $5A, $1C, $15; Single Rotodisc (rotates clockwise)
	.byte $5B, $23, $15; Single Rotodisc (rotates counterclockwise)
	.byte $8A, $24, $04; Thwomp (normal)
	.byte $5A, $28, $15; Single Rotodisc (rotates clockwise)
	.byte $FF
; Dungeon__1_W5
; Object Set 2
Dungeon__1_W5_generators:
Dungeon__1_W5_header:
	.byte $3D; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $00, $00, $3F, $7F; Blank Background (used to block out stuff)
	.byte $60 | $10, $00, $3A, $7F; Blank Background (used to block out stuff)
	.byte $00 | $11, $00, $E0, $11; Horizontally oriented X-blocks
	.byte $00 | $16, $00, $E0, $08; Horizontally oriented X-blocks
	.byte $00 | $17, $08, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $18, $09, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $19, $0A, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $1A, $0B, $E0, $00; Horizontally oriented X-blocks
	.byte $60 | $1A, $0C, $40, $04; Lava
	.byte $00 | $11, $11, $E3, $0C; Horizontally oriented X-blocks
	.byte $60 | $11, $12, $31, $02; Blank Background (used to block out stuff)
	.byte $60 | $13, $13, $30, $01; Blank Background (used to block out stuff)
	.byte $60 | $12, $16, $32, $01; Blank Background (used to block out stuff)
	.byte $60 | $12, $19, $31, $03; Blank Background (used to block out stuff)
	.byte $60 | $11, $19, $30, $00; Blank Background (used to block out stuff)
	.byte $00 | $02, $1F, $E7, $00; Horizontally oriented X-blocks
	.byte $00 | $09, $1A, $E0, $04; Horizontally oriented X-blocks
	.byte $00 | $0A, $1A, $E6, $00; Horizontally oriented X-blocks
	.byte $00 | $19, $11, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $19, $12, $E0, $13; Horizontally oriented X-blocks
	.byte $20 | $0D, $1D, $12; Bricks
	.byte $20 | $0D, $1F, $01; '?' with leaf
	.byte $20 | $15, $1D, $13; Bricks
	.byte $00 | $14, $11, $02; Rotodisc block
	.byte $00 | $02, $20, $E0, $0A; Horizontally oriented X-blocks
	.byte $00 | $03, $2A, $E7, $00; Horizontally oriented X-blocks
	.byte $00 | $06, $22, $E4, $03; Horizontally oriented X-blocks
	.byte $00 | $0A, $26, $E0, $04; Horizontally oriented X-blocks
	.byte $00 | $0B, $22, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $0D, $20, $E7, $00; Horizontally oriented X-blocks
	.byte $00 | $0D, $20, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $14, $20, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $13, $22, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $11, $23, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $11, $23, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $0F, $25, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $0F, $25, $E0, $0A; Horizontally oriented X-blocks
	.byte $00 | $14, $29, $E0, $16; Horizontally oriented X-blocks
	.byte $00 | $15, $28, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $16, $27, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $17, $26, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $18, $25, $E0, $01; Horizontally oriented X-blocks
	.byte $60 | $07, $23, $33, $01; Blank Background (used to block out stuff)
	.byte $00 | $0F, $2A, $02; Rotodisc block
	.byte $00 | $14, $23, $02; Rotodisc block
	.byte $20 | $07, $27, $92; Downward Pipe (CAN go down)
	.byte $00 | $0B, $30, $E4, $00; Horizontally oriented X-blocks
	.byte $00 | $0B, $31, $E0, $03; Horizontally oriented X-blocks
	.byte $00 | $0B, $35, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $0F, $35, $E0, $0E; Horizontally oriented X-blocks
	.byte $00 | $15, $3F, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $0F, $3B, $02; Rotodisc block
	.byte $00 | $14, $3B, $02; Rotodisc block
	.byte $20 | $0F, $31, $07; Brick with Leaf
	.byte $20 | $0F, $34, $30; Bricks with single coins
	.byte $00 | $0B, $43, $E4, $00; Horizontally oriented X-blocks
	.byte $00 | $0B, $43, $E0, $09; Horizontally oriented X-blocks
	.byte $00 | $0B, $4C, $E6, $00; Horizontally oriented X-blocks
	.byte $00 | $0E, $4C, $E0, $03; Horizontally oriented X-blocks
	.byte $00 | $0F, $4F, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $40, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $17, $41, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $18, $42, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $16, $4C, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $4D, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $19, $43, $E0, $20; Horizontally oriented X-blocks
	.byte $20 | $0C, $45, $D4; Upward Pipe (CAN'T go up)
	.byte $00 | $15, $4C, $02; Rotodisc block
	.byte $00 | $11, $50, $E0, $0A; Horizontally oriented X-blocks
	.byte $00 | $0E, $5A, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $0E, $5A, $E0, $03; Horizontally oriented X-blocks
	.byte $00 | $0E, $5D, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $11, $5D, $E0, $12; Horizontally oriented X-blocks
	.byte $00 | $16, $5B, $E2, $01; Horizontally oriented X-blocks
	.byte $00 | $17, $5C, $02; Rotodisc block
	.byte $00 | $19, $63, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $0E, $6F, $E3, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $6A, $E2, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $6B, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $17, $6B, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $17, $6D, $E3, $00; Horizontally oriented X-blocks
	.byte $60 | $1A, $64, $40, $05; Lava
	.byte $60 | $1A, $6E, $40, $01; Lava
	.byte $00 | $0E, $70, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $0D, $72, $E4, $00; Horizontally oriented X-blocks
	.byte $00 | $0D, $72, $E0, $0C; Horizontally oriented X-blocks
	.byte $00 | $0D, $7E, $E7, $00; Horizontally oriented X-blocks
	.byte $00 | $14, $79, $E0, $05; Horizontally oriented X-blocks
	.byte $00 | $15, $78, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $16, $77, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $17, $74, $E0, $03; Horizontally oriented X-blocks
	.byte $00 | $17, $74, $E3, $00; Horizontally oriented X-blocks
	.byte $60 | $1A, $72, $40, $01; Lava
	.byte $00 | $18, $70, $E2, $01; Horizontally oriented X-blocks
	.byte $00 | $12, $7C, $00; Door
	; Pointer on screen $02
	.byte $E0 | $02, $40 | $02, 16; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $07
	.byte $E0 | $07, $60 | $08, 225; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__1_W5_objects:
	.byte $9E, $0D, $13; Podoboo (comes out of lava)
	.byte $8A, $16, $12; Thwomp (normal)
	.byte $5B, $11, $14; Single Rotodisc (rotates counterclockwise)
	.byte $5A, $23, $14; Single Rotodisc (rotates clockwise)
	.byte $5B, $2A, $0F; Single Rotodisc (rotates counterclockwise)
	.byte $8A, $32, $0D; Thwomp (normal)
	.byte $5A, $3B, $0F; Single Rotodisc (rotates clockwise)
	.byte $5A, $3B, $14; Single Rotodisc (rotates clockwise)
	.byte $2F, $49, $11; Boo Buddy
	.byte $8A, $4D, $0F; Thwomp (normal)
	.byte $5B, $4C, $15; Single Rotodisc (rotates counterclockwise)
	.byte $8A, $5B, $0F; Thwomp (normal)
	.byte $5B, $5C, $17; Single Rotodisc (rotates counterclockwise)
	.byte $8A, $70, $0F; Thwomp (normal)
	.byte $FF
; Hammer_Bros_2_W5
; Object Set 3
Hammer_Bros_2_W5_generators:
Hammer_Bros_2_W5_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $13; Start action | Graphic set
	.byte $80 | $06; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $40 | $13, $00, $0C; Background Hills C
	.byte $40 | $17, $0C, $0B; Background Hills B
	.byte $20 | $12, $07, $16; Bricks
	.byte $20 | $16, $07, $16; Bricks
	.byte $20 | $16, $0A, $07; Brick with Leaf
	.byte $80 | $1A, $00, $80, $0F; Flat Land - Hilly
	.byte $FF
Hammer_Bros_2_W5_objects:
	.byte $81, $0C, $14; Hammer Brother
	.byte $81, $09, $18; Hammer Brother
	.byte $BA, $0D, $14; Exit on get treasure chest
	.byte $FF
; Tower__Going_Down__W5
; Object Set 13
Tower__Going_Down__W5_generators:
Tower__Going_Down__W5_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_040; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_80 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $20 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $60 | $0D; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $14, $06, $02; Cloud Background A
	.byte $00 | $14, $00, $02; Cloud Background A
	.byte $00 | $10, $00, $02; Cloud Background A
	.byte $00 | $0E, $04, $02; Cloud Background A
	.byte $00 | $0C, $06, $02; Cloud Background A
	.byte $00 | $09, $05, $02; Cloud Background A
	.byte $00 | $05, $05, $02; Cloud Background A
	.byte $00 | $03, $03, $02; Cloud Background A
	.byte $00 | $00, $04, $02; Cloud Background A
	.byte $00 | $00, $02, $02; Cloud Background A
	.byte $20 | $00, $07, $D5; Upward Pipe (CAN'T go up)
	.byte $00 | $14, $01, $F2; World 6-style Cloud Platform
	.byte $20 | $16, $06, $13; Bricks
	.byte $20 | $14, $07, $92; Downward Pipe (CAN go down)
	.byte $20 | $16, $04, $0B; Brick with 1-up
	.byte $20 | $16, $0B, $10; Bricks
	.byte $20 | $17, $04, $17; Bricks
	.byte $20 | $18, $04, $17; Bricks
	.byte $20 | $19, $04, $17; Bricks
	.byte $20 | $1A, $05, $15; Bricks
	.byte $FF
Tower__Going_Down__W5_objects:
	.byte $25, $00, $80; Changes exit location on map (works on warp pipe levels)
	.byte $FF
; Hammer_Bros_3_W5
; Object Set 13
Hammer_Bros_3_W5_generators:
Hammer_Bros_3_W5_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0D; Start action | Graphic set
	.byte $80 | $06; Time | Music
	.byte $00 | $13, $04, $02; Cloud Background A
	.byte $00 | $11, $06, $02; Cloud Background A
	.byte $00 | $0F, $04, $02; Cloud Background A
	.byte $00 | $0D, $06, $02; Cloud Background A
	.byte $20 | $12, $07, $15; Bricks
	.byte $20 | $16, $08, $15; Bricks
	.byte $60 | $19, $00, $21, $0F; Clouds B
	.byte $20 | $12, $0D, $0B; Brick with 1-up
	.byte $20 | $16, $07, $0A; Multi-Coin Brick
	.byte $20 | $16, $0A, $07; Brick with Leaf
	.byte $FF
Hammer_Bros_3_W5_objects:
	.byte $81, $0C, $14; Hammer Brother
	.byte $81, $09, $18; Hammer Brother
	.byte $BA, $0D, $14; Exit on get treasure chest
	.byte $FF
; Level_5_W5
; Object Set 4
Level_5_W5_generators:
Level_5_W5_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_10 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_04; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $04; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $20 | $00, $00, $4F; Wooden blocks
	.byte $20 | $00, $10, $4F; Wooden blocks
	.byte $20 | $00, $20, $4F; Wooden blocks
	.byte $20 | $00, $30, $4F; Wooden blocks
	.byte $20 | $00, $40, $4F; Wooden blocks
	.byte $20 | $00, $50, $4F; Wooden blocks
	.byte $20 | $00, $60, $4F; Wooden blocks
	.byte $20 | $00, $70, $4F; Wooden blocks
	.byte $60 | $19, $00, $4F; Donut Blocks
	.byte $20 | $16, $02, $40; Wooden blocks
	.byte $20 | $18, $08, $40; Wooden blocks
	.byte $00 | $10, $08, $01; Large Swirly Background Cloud
	.byte $00 | $12, $0D, $00; Small Swirly Background Cloud
	.byte $00 | $13, $05, $00; Small Swirly Background Cloud
	.byte $60 | $19, $10, $4A; Donut Blocks
	.byte $60 | $17, $1B, $4D; Donut Blocks
	.byte $20 | $18, $11, $40; Wooden blocks
	.byte $40 | $16, $1A, $05; Wooden Block with Leaf
	.byte $20 | $17, $1A, $40; Wooden blocks
	.byte $20 | $18, $1A, $40; Wooden blocks
	.byte $20 | $16, $1E, $11; Bricks
	.byte $20 | $17, $1E, $A3; Downward Pipe (CAN'T go down)
	.byte $00 | $0F, $12, $00; Small Swirly Background Cloud
	.byte $00 | $12, $19, $00; Small Swirly Background Cloud
	.byte $00 | $13, $1F, $00; Small Swirly Background Cloud
	.byte $00 | $10, $1C, $01; Large Swirly Background Cloud
	.byte $00 | $13, $14, $01; Large Swirly Background Cloud
	.byte $60 | $19, $29, $4D; Donut Blocks
	.byte $20 | $16, $29, $40; Wooden blocks
	.byte $20 | $17, $29, $40; Wooden blocks
	.byte $20 | $18, $29, $40; Wooden blocks
	.byte $20 | $16, $24, $11; Bricks
	.byte $20 | $17, $24, $B3; Downward Pipe (CAN go down, ignores pointers)
	.byte $20 | $15, $2F, $01; '?' with leaf
	.byte $00 | $10, $2A, $00; Small Swirly Background Cloud
	.byte $00 | $11, $24, $00; Small Swirly Background Cloud
	.byte $00 | $13, $2D, $00; Small Swirly Background Cloud
	.byte $00 | $13, $28, $01; Large Swirly Background Cloud
	.byte $60 | $19, $39, $47; Donut Blocks
	.byte $20 | $15, $30, $22; '?' blocks with single coins
	.byte $20 | $17, $37, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $01, $30, $D9; Upward Pipe (CAN'T go up)
	.byte $20 | $0A, $30, $D7; Upward Pipe (CAN'T go up)
	.byte $00 | $10, $3A, $00; Small Swirly Background Cloud
	.byte $00 | $10, $3F, $00; Small Swirly Background Cloud
	.byte $00 | $11, $34, $00; Small Swirly Background Cloud
	.byte $00 | $14, $3D, $00; Small Swirly Background Cloud
	.byte $20 | $17, $40, $48; Wooden blocks
	.byte $20 | $18, $40, $40; Wooden blocks
	.byte $20 | $18, $48, $40; Wooden blocks
	.byte $60 | $17, $41, $46; Donut Blocks
	.byte $60 | $19, $48, $48; Donut Blocks
	.byte $20 | $15, $41, $86; Coins
	.byte $20 | $19, $41, $86; Coins
	.byte $00 | $10, $45, $00; Small Swirly Background Cloud
	.byte $00 | $10, $4E, $00; Small Swirly Background Cloud
	.byte $00 | $13, $41, $00; Small Swirly Background Cloud
	.byte $00 | $14, $4F, $00; Small Swirly Background Cloud
	.byte $00 | $12, $4A, $01; Large Swirly Background Cloud
	.byte $60 | $19, $59, $46; Donut Blocks
	.byte $20 | $18, $50, $40; Wooden blocks
	.byte $20 | $18, $59, $40; Wooden blocks
	.byte $20 | $17, $54, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $01, $5E, $DF; Upward Pipe (CAN'T go up)
	.byte $00 | $10, $53, $00; Small Swirly Background Cloud
	.byte $00 | $14, $52, $00; Small Swirly Background Cloud
	.byte $00 | $14, $5C, $00; Small Swirly Background Cloud
	.byte $00 | $12, $56, $01; Large Swirly Background Cloud
	.byte $60 | $19, $60, $4F; Donut Blocks
	.byte $20 | $12, $62, $44; Wooden blocks
	.byte $20 | $13, $62, $40; Wooden blocks
	.byte $20 | $13, $66, $40; Wooden blocks
	.byte $20 | $14, $62, $40; Wooden blocks
	.byte $20 | $14, $66, $40; Wooden blocks
	.byte $20 | $15, $62, $44; Wooden blocks
	.byte $20 | $16, $63, $42; Wooden blocks
	.byte $20 | $18, $60, $40; Wooden blocks
	.byte $40 | $18, $68, $05; Wooden Block with Leaf
	.byte $20 | $12, $64, $10; Bricks
	.byte $20 | $15, $64, $10; Bricks
	.byte $20 | $16, $64, $10; Bricks
	.byte $20 | $12, $63, $30; Bricks with single coins
	.byte $20 | $12, $65, $07; Brick with Leaf
	.byte $00 | $10, $62, $00; Small Swirly Background Cloud
	.byte $00 | $13, $69, $00; Small Swirly Background Cloud
	.byte $00 | $13, $6D, $00; Small Swirly Background Cloud
	.byte $20 | $01, $69, $DF; Upward Pipe (CAN'T go up)
	.byte $60 | $19, $70, $4F; Donut Blocks
	.byte $20 | $18, $70, $40; Wooden blocks
	.byte $20 | $18, $78, $40; Wooden blocks
	.byte $00 | $10, $79, $00; Small Swirly Background Cloud
	.byte $00 | $12, $74, $00; Small Swirly Background Cloud
	.byte $00 | $12, $7F, $00; Small Swirly Background Cloud
	.byte $00 | $14, $75, $00; Small Swirly Background Cloud
	.byte $00 | $15, $7B, $00; Small Swirly Background Cloud
	.byte $00 | $11, $70, $01; Large Swirly Background Cloud
	.byte $00 | $13, $78, $01; Large Swirly Background Cloud
	.byte $00 | $1A, $80, $10, $1F; Wooden platform
	.byte $40 | $00, $88, $09; Level Ending
	; Pointer on screen $02
	.byte $E0 | $02, $00 | $02, 23; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $07
	.byte $E0 | $07, $40 | $02, 144; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_5_W5_objects:
	.byte $D4, $00, $1C; White Mushroom House (X pos must be uneven, Y pos=amount of coins required)
	.byte $6E, $12, $15; Green Koopa Paratroopa (bounces)
	.byte $6E, $17, $15; Green Koopa Paratroopa (bounces)
	.byte $74, $14, $17; Para-Goomba with Micro-Goombas
	.byte $6E, $2D, $16; Green Koopa Paratroopa (bounces)
	.byte $A7, $30, $11; Red Venus Fire Trap (downward)
	.byte $A6, $37, $17; Red Venus Fire Trap (upward)
	.byte $74, $4E, $17; Para-Goomba with Micro-Goombas
	.byte $58, $52, $13; Fire Chomp
	.byte $A2, $54, $17; Red Piranha Plant (upward)
	.byte $A7, $69, $10; Red Venus Fire Trap (downward)
	.byte $6E, $70, $15; Green Koopa Paratroopa (bounces)
	.byte $74, $78, $17; Para-Goomba with Micro-Goombas
	.byte $41, $98, $15; Goal Card
	.byte $FF
; Hammer_Bros_4_W5
; Object Set 13
Hammer_Bros_4_W5_generators:
Hammer_Bros_4_W5_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0D; Start action | Graphic set
	.byte $80 | $06; Time | Music
	.byte $00 | $13, $04, $02; Cloud Background A
	.byte $00 | $11, $06, $02; Cloud Background A
	.byte $00 | $0F, $04, $02; Cloud Background A
	.byte $00 | $0D, $06, $02; Cloud Background A
	.byte $20 | $12, $07, $16; Bricks
	.byte $20 | $16, $07, $16; Bricks
	.byte $60 | $19, $00, $21, $0F; Clouds B
	.byte $FF
Hammer_Bros_4_W5_objects:
	.byte $81, $0C, $14; Hammer Brother
	.byte $81, $09, $18; Hammer Brother
	.byte $BA, $0D, $14; Exit on get treasure chest
	.byte $FF
; Level_4_W5
; Object Set 13
Level_4_W5_generators:
Level_4_W5_header:
	.byte $3E; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_13; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0D; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $11, $76, $02; Cloud Background A
	.byte $00 | $14, $6F, $02; Cloud Background A
	.byte $00 | $0E, $63, $02; Cloud Background A
	.byte $00 | $0D, $6C, $02; Cloud Background A
	.byte $00 | $12, $53, $02; Cloud Background A
	.byte $00 | $0F, $5A, $02; Cloud Background A
	.byte $00 | $0B, $50, $02; Cloud Background A
	.byte $00 | $0C, $47, $02; Cloud Background A
	.byte $00 | $05, $44, $02; Cloud Background A
	.byte $00 | $05, $40, $02; Cloud Background A
	.byte $00 | $05, $3C, $02; Cloud Background A
	.byte $00 | $05, $38, $02; Cloud Background A
	.byte $00 | $05, $34, $02; Cloud Background A
	.byte $00 | $05, $30, $02; Cloud Background A
	.byte $00 | $05, $2C, $02; Cloud Background A
	.byte $00 | $05, $24, $02; Cloud Background A
	.byte $00 | $05, $20, $02; Cloud Background A
	.byte $00 | $12, $13, $02; Cloud Background A
	.byte $00 | $0B, $16, $02; Cloud Background A
	.byte $00 | $05, $1C, $02; Cloud Background A
	.byte $00 | $05, $18, $02; Cloud Background A
	.byte $00 | $12, $09, $02; Cloud Background A
	.byte $00 | $0F, $00, $02; Cloud Background A
	.byte $00 | $0D, $08, $02; Cloud Background A
	.byte $60 | $14, $00, $46, $0F; White Background
	.byte $60 | $17, $10, $43, $07; White Background
	.byte $60 | $12, $18, $48, $03; White Background
	.byte $60 | $0C, $1C, $4E, $2F; White Background
	.byte $60 | $10, $4C, $4A, $0B; White Background
	.byte $60 | $14, $58, $46, $12; White Background
	.byte $60 | $13, $6B, $47, $08; White Background
	.byte $60 | $16, $74, $44, $0B; White Background
	.byte $00 | $11, $1F, $06; Cloud Background B
	.byte $00 | $14, $1A, $07; Cloud Background C
	.byte $00 | $0B, $29, $06; Cloud Background B
	.byte $00 | $0F, $28, $07; Cloud Background C
	.byte $00 | $11, $39, $07; Cloud Background C
	.byte $00 | $11, $3E, $06; Cloud Background B
	.byte $00 | $17, $30, $06; Cloud Background B
	.byte $20 | $11, $0B, $01; '?' with leaf
	.byte $00 | $15, $00, $DD; World 5-style Cloud Platform - White Background
	.byte $20 | $06, $1C, $81; Coins
	.byte $00 | $07, $1C, $DD; World 5-style Cloud Platform - White Background
	.byte $00 | $18, $14, $D5; World 5-style Cloud Platform - White Background
	.byte $20 | $06, $20, $81; Coins
	.byte $20 | $06, $24, $81; Coins
	.byte $20 | $06, $28, $81; Coins
	.byte $00 | $16, $20, $D4; World 5-style Cloud Platform - White Background
	.byte $20 | $06, $30, $81; Coins
	.byte $20 | $06, $34, $81; Coins
	.byte $20 | $06, $38, $81; Coins
	.byte $20 | $06, $3C, $81; Coins
	.byte $00 | $07, $30, $DF; World 5-style Cloud Platform - White Background
	.byte $00 | $18, $3D, $D4; World 5-style Cloud Platform - White Background
	.byte $00 | $07, $42, $D7; World 5-style Cloud Platform - White Background
	.byte $20 | $15, $46, $49; Wooden blocks
	.byte $20 | $16, $47, $47; Wooden blocks
	.byte $40 | $15, $48, $65, $05; Waterfall
	.byte $20 | $12, $51, $47; Wooden blocks
	.byte $20 | $13, $52, $45; Wooden blocks
	.byte $40 | $12, $53, $68, $03; Waterfall
	.byte $00 | $17, $77, $D8; World 5-style Cloud Platform - White Background
	.byte $20 | $16, $7D, $E2; Rightward Pipe (CAN go in)
	; Pointer on screen $07
	.byte $E0 | $07, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_4_W5_objects:
	.byte $91, $06, $12; Spinning Platform (constant)
	.byte $91, $12, $15; Spinning Platform (constant)
	.byte $91, $1C, $17; Spinning Platform (constant)
	.byte $90, $28, $13; Spinning Platform (step-activated)
	.byte $92, $2F, $15; Spinning Platform (periodical clockwise)
	.byte $91, $2F, $19; Spinning Platform (constant)
	.byte $90, $37, $17; Spinning Platform (step-activated)
	.byte $91, $44, $17; Spinning Platform (constant)
	.byte $91, $45, $05; Spinning Platform (constant)
	.byte $90, $5D, $13; Spinning Platform (step-activated)
	.byte $6F, $61, $11; Red Koopa Paratroopa
	.byte $93, $65, $15; Spinning Platform (periodical counterclockwise)
	.byte $90, $6C, $17; Spinning Platform (step-activated)
	.byte $93, $73, $19; Spinning Platform (periodical counterclockwise)
	.byte $6E, $7C, $16; Green Koopa Paratroopa (bounces)
	.byte $FF
; Dungeon__2_Beginning_End_W5
; Object Set 2
Dungeon__2_Beginning_End_W5_generators:
Dungeon__2_Beginning_End_W5_header:
	.byte $3F; Next Level
	.byte LEVEL1_SIZE_05 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $10, $20, $39, $1F; Blank Background (used to block out stuff)
	.byte $60 | $19, $00, $41, $0E; Lava
	.byte $60 | $1A, $1E, $40, $31; Lava
	.byte $00 | $0E, $00, $E1, $4F; Horizontally oriented X-blocks
	.byte $00 | $10, $0F, $EA, $0E; Horizontally oriented X-blocks
	.byte $00 | $16, $02, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $16, $08, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $18, $0B, $E2, $01; Horizontally oriented X-blocks
	.byte $00 | $12, $02, $62; Dungeon windows
	.byte $00 | $10, $00, $4E; Dungeon background
	.byte $20 | $16, $0B, $91; Downward Pipe (CAN go down)
	.byte $00 | $10, $1E, $E9, $31; Horizontally oriented X-blocks
	.byte $60 | $12, $26, $30, $06; Blank Background (used to block out stuff)
	.byte $60 | $13, $26, $30, $07; Blank Background (used to block out stuff)
	.byte $60 | $14, $26, $30, $08; Blank Background (used to block out stuff)
	.byte $60 | $15, $26, $33, $28; Blank Background (used to block out stuff)
	.byte $60 | $19, $2A, $30, $01; Blank Background (used to block out stuff)
	.byte $20 | $17, $27, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $16, $31, $63; Dungeon windows
	.byte $60 | $10, $41, $34, $0D; Blank Background (used to block out stuff)
	.byte $00 | $11, $4D, $60; Dungeon windows
	; Pointer on screen $00
	.byte $E0 | $00, $50 | $02, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__2_Beginning_End_W5_objects:
	.byte $4C, $4C, $27; Flying Boom Boom
	.byte $FF
; Kings_Room_W5
; Object Set 2
Kings_Room_W5_generators:
Kings_Room_W5_header:
	.byte $10; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; Weird
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Kings_Room_W5_objects:
	.byte $D5, $0A, $16; 'The king has been transformed' message
	.byte $FF
; Level_9_W5
; Object Set 13
Level_9_W5_generators:
Level_9_W5_header:
	.byte $3E; Next Level
	.byte LEVEL1_SIZE_10 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_13; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0D; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $0C, $97, $02; Cloud Background A
	.byte $00 | $07, $98, $02; Cloud Background A
	.byte $00 | $05, $96, $02; Cloud Background A
	.byte $00 | $03, $94, $02; Cloud Background A
	.byte $00 | $00, $93, $02; Cloud Background A
	.byte $00 | $0E, $75, $02; Cloud Background A
	.byte $00 | $0D, $72, $02; Cloud Background A
	.byte $00 | $0C, $63, $02; Cloud Background A
	.byte $00 | $0B, $6A, $02; Cloud Background A
	.byte $00 | $0A, $63, $02; Cloud Background A
	.byte $00 | $07, $62, $02; Cloud Background A
	.byte $00 | $07, $57, $02; Cloud Background A
	.byte $00 | $10, $4E, $02; Cloud Background A
	.byte $00 | $0E, $4C, $02; Cloud Background A
	.byte $00 | $0A, $4C, $02; Cloud Background A
	.byte $00 | $09, $4B, $02; Cloud Background A
	.byte $00 | $07, $4D, $02; Cloud Background A
	.byte $00 | $06, $4A, $02; Cloud Background A
	.byte $00 | $05, $49, $02; Cloud Background A
	.byte $00 | $02, $48, $02; Cloud Background A
	.byte $00 | $00, $46, $02; Cloud Background A
	.byte $00 | $13, $2C, $02; Cloud Background A
	.byte $00 | $0D, $2A, $02; Cloud Background A
	.byte $00 | $0A, $23, $02; Cloud Background A
	.byte $00 | $03, $20, $02; Cloud Background A
	.byte $00 | $0E, $15, $02; Cloud Background A
	.byte $00 | $0B, $14, $02; Cloud Background A
	.byte $00 | $09, $12, $02; Cloud Background A
	.byte $00 | $12, $0B, $02; Cloud Background A
	.byte $00 | $0D, $00, $02; Cloud Background A
	.byte $00 | $0C, $07, $02; Cloud Background A
	.byte $00 | $09, $08, $02; Cloud Background A
	.byte $00 | $02, $0B, $02; Cloud Background A
	.byte $00 | $00, $09, $02; Cloud Background A
	.byte $60 | $12, $00, $48, $0F; White Background
	.byte $60 | $00, $0D, $4D, $19; White Background
	.byte $60 | $19, $10, $41, $01; White Background
	.byte $60 | $0E, $17, $4C, $14; White Background
	.byte $60 | $0A, $27, $40, $00; White Background
	.byte $60 | $10, $2C, $4A, $04; White Background
	.byte $60 | $00, $4B, $4B, $1D; White Background
	.byte $60 | $0C, $59, $4E, $11; White Background
	.byte $60 | $0F, $6B, $4B, $07; White Background
	.byte $60 | $11, $73, $49, $09; White Background
	.byte $60 | $00, $98, $4B, $06; White Background
	.byte $00 | $15, $01, $D6; World 5-style Cloud Platform - White Background
	.byte $00 | $06, $9A, $D3; World 5-style Cloud Platform - White Background
	.byte $00 | $11, $0C, $D2; World 5-style Cloud Platform - White Background
	.byte $20 | $00, $9B, $C2; Upward Pipe (CAN go up)
	; Pointer on screen $09
	.byte $E0 | $09, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_9_W5_objects:
	.byte $D3, $00, $20; Autoscrolling
	.byte $6F, $0A, $10; Red Koopa Paratroopa
	.byte $28, $10, $11; Wooden platform - moves up and down (a lot)
	.byte $28, $14, $0D; Wooden platform - moves up and down (a lot)
	.byte $38, $18, $08; Wooden platform - moves up and down (a little)
	.byte $28, $1C, $06; Wooden platform - moves up and down (a lot)
	.byte $28, $2C, $11; Wooden platform - moves up and down (a lot)
	.byte $28, $33, $0C; Wooden platform - moves up and down (a lot)
	.byte $28, $37, $0A; Wooden platform - moves up and down (a lot)
	.byte $27, $4C, $13; Wooden platform - moves back and forth (a lot)
	.byte $28, $4E, $0F; Wooden platform - moves up and down (a lot)
	.byte $58, $56, $14; Fire Chomp
	.byte $27, $58, $07; Wooden platform - moves back and forth (a lot)
	.byte $38, $5D, $05; Wooden platform - moves up and down (a little)
	.byte $28, $74, $11; Wooden platform - moves up and down (a lot)
	.byte $28, $7A, $0A; Wooden platform - moves up and down (a lot)
	.byte $58, $7E, $14; Fire Chomp
	.byte $27, $90, $12; Wooden platform - moves back and forth (a lot)
	.byte $37, $95, $0E; Wooden platform - moves back and forth (a little)
	.byte $38, $96, $0B; Wooden platform - moves up and down (a little)
	.byte $FF
; Hammer_Bros_2_W6
; Object Set 12
Hammer_Bros_2_W6_generators:
Hammer_Bros_2_W6_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $80 | $06; Time | Music
	.byte $00 | $11, $03, $C2; Background Clouds
	.byte $20 | $12, $07, $16; Bricks
	.byte $00 | $14, $01, $C2; Background Clouds
	.byte $20 | $16, $07, $15; Bricks
	.byte $20 | $16, $0D, $07; Brick with Leaf
	.byte $60 | $1A, $00, $1F; Ice Blocks
	.byte $FF
Hammer_Bros_2_W6_objects:
	.byte $81, $0C, $14; Hammer Brother
	.byte $81, $09, $18; Hammer Brother
	.byte $BA, $0D, $14; Exit on get treasure chest
	.byte $FF
; Hammer_Bros_1_W6
; Object Set 12
Hammer_Bros_1_W6_generators:
Hammer_Bros_1_W6_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $80 | $06; Time | Music
	.byte $00 | $11, $03, $C2; Background Clouds
	.byte $20 | $12, $07, $16; Bricks
	.byte $00 | $14, $01, $C2; Background Clouds
	.byte $20 | $16, $07, $16; Bricks
	.byte $60 | $1A, $00, $1F; Ice Blocks
	.byte $FF
Hammer_Bros_1_W6_objects:
	.byte $81, $0C, $14; Hammer Brother
	.byte $81, $09, $18; Hammer Brother
	.byte $BA, $0D, $14; Exit on get treasure chest
	.byte $FF
; Kings_Room_W6
; Object Set 2
Kings_Room_W6_generators:
Kings_Room_W6_header:
	.byte $12; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_11 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; Weird
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Kings_Room_W6_objects:
	.byte $D5, $0A, $16; 'The king has been transformed' message
	.byte $FF
; Kings_Room_W7
; Object Set 2
Kings_Room_W7_generators:
Kings_Room_W7_header:
	.byte $14; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_70 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $16; Start action | Graphic set
	.byte $00 | $09; Time | Music
	.byte $00 | $00, $00, $03; Weird
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $03, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Kings_Room_W7_objects:
	.byte $D5, $0A, $16; 'The king has been transformed' message
	.byte $FF