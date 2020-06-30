; Bank 5

; Crappy_Ship_Boss_Room_W8
; Object Set 10
Crappy_Ship_Boss_Room_W8_generators:
Crappy_Ship_Boss_Room_W8_header:
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
Crappy_Ship_Boss_Room_W8_objects:
	.byte $4C, $0C, $27; Flying Boom Boom
	.byte $FF
; Ship_W1
; Object Set 10
Ship_W1_generators:
Ship_W1_header:
	.byte $00; Next Level
	.byte LEVEL1_SIZE_06 | LEVEL1_YSTART_0B0; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_80 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $E0 | $0A; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $00 | $0C, $04, $18; Wooden Ship Beam
	.byte $00 | $0D, $05, $17; Wooden Ship Beam
	.byte $00 | $0E, $06, $20, $1A; Wooden Ship Beam
	.byte $00 | $0F, $07, $20, $19; Wooden Ship Beam
	.byte $00 | $10, $08, $20, $18; Wooden Ship Beam
	.byte $00 | $11, $0A, $20, $3B; Wooden Ship Beam
	.byte $00 | $12, $0C, $20, $07; Wooden Ship Beam
	.byte $00 | $13, $0E, $30, $05; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $0C, $04, $03; Wooden ship beam terminus A
	.byte $00 | $0D, $05, $03; Wooden ship beam terminus A
	.byte $00 | $0E, $06, $03; Wooden ship beam terminus A
	.byte $00 | $0F, $07, $03; Wooden ship beam terminus A
	.byte $40 | $10, $08, $0A; Wooden ship beam terminus B
	.byte $40 | $11, $0A, $0A; Wooden ship beam terminus B
	.byte $40 | $12, $0C, $0A; Wooden ship beam terminus B
	.byte $40 | $13, $0D, $0B; Background wooden ship beam terminus
	.byte $00 | $0D, $09, $04; Anchor
	.byte $00 | $0C, $1E, $41; Wooden Ship Pillar
	.byte $00 | $12, $1D, $1C; Wooden Ship Beam
	.byte $00 | $13, $1E, $18; Wooden Ship Beam
	.byte $00 | $14, $1F, $30, $07; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $12, $1D, $03; Wooden ship beam terminus A
	.byte $00 | $13, $1E, $03; Wooden ship beam terminus A
	.byte $40 | $14, $1F, $0B; Background wooden ship beam terminus
	.byte $00 | $0D, $18, $06; Bullet Shooter - Up/Left
	.byte $00 | $0D, $13, $06; Bullet Shooter - Up/Left
	.byte $00 | $0C, $1E, $01; 2-Way Bullet Shooter
	.byte $00 | $13, $14, $71; Corkscrew - Left terminus
	.byte $00 | $08, $28, $20, $22; Wooden Ship Beam
	.byte $00 | $0E, $25, $62; Thick Wooden Ship Beam
	.byte $00 | $0E, $2C, $42; Wooden Ship Pillar
	.byte $00 | $14, $27, $71; Corkscrew - Left terminus
	.byte $00 | $0D, $2C, $01; 2-Way Bullet Shooter
	.byte $00 | $09, $28, $08; Bullet Shooter - Down/Left
	.byte $00 | $09, $2D, $08; Bullet Shooter - Down/Left
	.byte $00 | $10, $24, $06; Bullet Shooter - Up/Left
	.byte $20 | $0D, $35, $00; '?' with flower
	.byte $00 | $09, $3D, $1D; Wooden Ship Beam
	.byte $00 | $0A, $3D, $1D; Wooden Ship Beam
	.byte $00 | $0B, $3D, $1D; Wooden Ship Beam
	.byte $00 | $12, $31, $1C; Wooden Ship Beam
	.byte $00 | $13, $32, $18; Wooden Ship Beam
	.byte $00 | $14, $33, $30, $07; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $12, $31, $03; Wooden ship beam terminus A
	.byte $00 | $13, $32, $03; Wooden ship beam terminus A
	.byte $40 | $14, $33, $0B; Background wooden ship beam terminus
	.byte $00 | $14, $3B, $71; Corkscrew - Left terminus
	.byte $00 | $0C, $3D, $B6; Metal platform
	.byte $00 | $0C, $3D, $C4; 1 Metal Bar A
	.byte $00 | $0C, $43, $D4; 1 Metal Bar B
	.byte $00 | $09, $38, $0A; 4-Way Bullet Shooter A
	.byte $00 | $0E, $3B, $42; Wooden Ship Pillar
	.byte $00 | $12, $41, $14; Wooden Ship Beam
	.byte $00 | $13, $42, $20, $19; Wooden Ship Beam
	.byte $00 | $14, $43, $20, $17; Wooden Ship Beam
	.byte $00 | $15, $45, $30, $15; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $12, $41, $03; Wooden ship beam terminus A
	.byte $00 | $13, $42, $03; Wooden ship beam terminus A
	.byte $40 | $14, $43, $0A; Wooden ship beam terminus B
	.byte $40 | $15, $45, $0B; Background wooden ship beam terminus
	.byte $00 | $11, $4D, $41; Wooden Ship Pillar
	.byte $00 | $10, $4D, $01; 2-Way Bullet Shooter
	.byte $00 | $12, $47, $07; Bullet Shooter - Up/Right
	.byte $00 | $12, $4F, $07; Bullet Shooter - Up/Right
	.byte $00 | $0E, $54, $1A; Wooden Ship Beam
	.byte $00 | $0F, $54, $1A; Wooden Ship Beam
	.byte $00 | $10, $53, $1B; Wooden Ship Beam
	.byte $00 | $11, $52, $1B; Wooden Ship Beam
	.byte $00 | $12, $50, $1C; Wooden Ship Beam
	.byte $60 | $0D, $54, $2A; Railings
	.byte $60 | $11, $54, $63; Portholes
	.byte $00 | $15, $5B, $71; Corkscrew - Left terminus
	.byte $20 | $0C, $58, $91; Downward Pipe (CAN go down)
	; Pointer on screen $05
	.byte $E0 | $05, $00 | $02, 96; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Ship_W1_objects:
	.byte $D3, $00, $0B; Autoscrolling
	.byte $B8, $03, $09; Moving Background Clouds
	.byte $C4, $13, $0D; Bullet Shots (up/left)
	.byte $AA, $16, $13; Propeller
	.byte $C4, $18, $0D; Bullet Shots (up/left)
	.byte $BC, $1E, $0C; Bullet Bills
	.byte $C4, $24, $10; Bullet Shots (up/left)
	.byte $C6, $28, $09; Bullet Shots (down/left)
	.byte $AA, $29, $14; Propeller
	.byte $BC, $2C, $0D; Bullet Bills
	.byte $C6, $2D, $09; Bullet Shots (down/left)
	.byte $BF, $38, $0A; Cross-shaped bullet shots
	.byte $AA, $3D, $14; Propeller
	.byte $C5, $47, $12; Bullet Shots (up/right)
	.byte $BC, $4D, $10; Bullet Bills
	.byte $C5, $4F, $12; Bullet Shots (up/right)
	.byte $FF
; Anchors_Away_W2
; Object Set 10
Anchors_Away_W2_generators:
Anchors_Away_W2_header:
	.byte $0B; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
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
Anchors_Away_W2_objects:
	.byte $09, $16, $14; Ship Anchor
	.byte $FF
; Ship_W2
; Object Set 10
Ship_W2_generators:
Ship_W2_header:
	.byte $01; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_0B0; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_80 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $E0 | $0A; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $00 | $0A, $1B, $97; Corkscrew - Lower terminus
	.byte $00 | $0A, $25, $97; Corkscrew - Lower terminus
	.byte $00 | $0D, $39, $94; Corkscrew - Lower terminus
	.byte $00 | $0D, $41, $9A; Corkscrew - Lower terminus
	.byte $00 | $0D, $54, $9A; Corkscrew - Lower terminus
	.byte $00 | $0C, $04, $19; Wooden Ship Beam
	.byte $00 | $0D, $05, $19; Wooden Ship Beam
	.byte $00 | $0E, $06, $19; Wooden Ship Beam
	.byte $00 | $0F, $07, $20, $15; Wooden Ship Beam
	.byte $00 | $10, $08, $20, $14; Wooden Ship Beam
	.byte $00 | $11, $0A, $30, $0B; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $0C, $04, $03; Wooden ship beam terminus A
	.byte $00 | $0D, $05, $03; Wooden ship beam terminus A
	.byte $00 | $0E, $06, $03; Wooden ship beam terminus A
	.byte $00 | $0F, $07, $03; Wooden ship beam terminus A
	.byte $40 | $10, $08, $0A; Wooden ship beam terminus B
	.byte $40 | $11, $0A, $0B; Background wooden ship beam terminus
	.byte $00 | $0D, $09, $04; Anchor
	.byte $00 | $09, $1A, $1C; Wooden Ship Beam
	.byte $00 | $0A, $1D, $15; Wooden Ship Beam
	.byte $00 | $0B, $1E, $14; Wooden Ship Beam
	.byte $00 | $0C, $1F, $1A; Wooden Ship Beam
	.byte $00 | $09, $1A, $03; Wooden ship beam terminus A
	.byte $00 | $0A, $1D, $03; Wooden ship beam terminus A
	.byte $00 | $0B, $1E, $03; Wooden ship beam terminus A
	.byte $00 | $0C, $1F, $03; Wooden ship beam terminus A
	.byte $00 | $0D, $15, $41; Wooden Ship Pillar
	.byte $00 | $0C, $18, $42; Wooden Ship Pillar
	.byte $00 | $08, $1B, $05; Top Screw Head
	.byte $00 | $0B, $18, $01; 2-Way Bullet Shooter
	.byte $00 | $0D, $15, $01; 2-Way Bullet Shooter
	.byte $00 | $10, $24, $20, $16; Wooden Ship Beam
	.byte $00 | $11, $27, $20, $10; Wooden Ship Beam
	.byte $00 | $12, $28, $1E; Wooden Ship Beam
	.byte $00 | $13, $29, $1D; Wooden Ship Beam
	.byte $00 | $10, $24, $03; Wooden ship beam terminus A
	.byte $00 | $11, $27, $03; Wooden ship beam terminus A
	.byte $00 | $12, $28, $03; Wooden ship beam terminus A
	.byte $00 | $13, $29, $03; Wooden ship beam terminus A
	.byte $00 | $0E, $2F, $41; Wooden Ship Pillar
	.byte $00 | $08, $25, $05; Top Screw Head
	.byte $00 | $0A, $20, $0C; Metal Plated Bullet Shooter A
	.byte $00 | $0B, $29, $01; 2-Way Bullet Shooter
	.byte $00 | $0D, $25, $A0; Corkscrew - Upper terminus
	.byte $00 | $0D, $2F, $01; 2-Way Bullet Shooter
	.byte $60 | $11, $2D, $64; Portholes
	.byte $00 | $0C, $38, $1A; Wooden Ship Beam
	.byte $00 | $0D, $3B, $14; Wooden Ship Beam
	.byte $00 | $0E, $3C, $13; Wooden Ship Beam
	.byte $00 | $0C, $38, $03; Wooden ship beam terminus A
	.byte $00 | $0D, $3B, $03; Wooden ship beam terminus A
	.byte $00 | $0E, $3C, $03; Wooden ship beam terminus A
	.byte $00 | $0D, $33, $A2; Corkscrew - Upper terminus
	.byte $00 | $0B, $33, $42; Wooden Ship Pillar
	.byte $20 | $08, $3C, $00; '?' with flower
	.byte $00 | $0A, $33, $01; 2-Way Bullet Shooter
	.byte $00 | $0B, $39, $05; Top Screw Head
	.byte $00 | $0F, $36, $01; 2-Way Bullet Shooter
	.byte $00 | $13, $37, $70; Corkscrew - Left terminus
	.byte $00 | $16, $41, $20, $13; Wooden Ship Beam
	.byte $00 | $10, $41, $45; Wooden Ship Pillar
	.byte $00 | $11, $42, $44; Wooden Ship Pillar
	.byte $00 | $03, $4B, $6F; Thick Wooden Ship Beam
	.byte $00 | $0B, $41, $05; Top Screw Head
	.byte $00 | $13, $4B, $A2; Corkscrew - Upper terminus
	.byte $00 | $17, $4B, $A0; Corkscrew - Upper terminus
	.byte $60 | $0E, $44, $52; Crate
	.byte $60 | $0E, $4D, $51; Crate
	.byte $60 | $12, $43, $52; Crate
	.byte $60 | $12, $4D, $55; Crate
	.byte $60 | $12, $47, $52; Crate
	.byte $60 | $0E, $48, $52; Crate
	.byte $00 | $11, $42, $01; 2-Way Bullet Shooter
	.byte $00 | $13, $42, $01; 2-Way Bullet Shooter
	.byte $00 | $15, $42, $01; 2-Way Bullet Shooter
	.byte $00 | $0C, $54, $18; Wooden Ship Beam
	.byte $00 | $0D, $56, $16; Wooden Ship Beam
	.byte $00 | $0E, $57, $15; Wooden Ship Beam
	.byte $00 | $0F, $58, $20, $24; Wooden Ship Beam
	.byte $00 | $10, $5F, $20, $1C; Wooden Ship Beam
	.byte $00 | $0D, $56, $03; Wooden ship beam terminus A
	.byte $00 | $0E, $57, $03; Wooden ship beam terminus A
	.byte $00 | $0F, $58, $03; Wooden ship beam terminus A
	.byte $00 | $10, $5F, $03; Wooden ship beam terminus A
	.byte $00 | $10, $53, $45; Wooden Ship Pillar
	.byte $00 | $10, $54, $45; Wooden Ship Pillar
	.byte $00 | $0B, $54, $05; Top Screw Head
	.byte $00 | $10, $53, $01; 2-Way Bullet Shooter
	.byte $00 | $12, $53, $01; 2-Way Bullet Shooter
	.byte $00 | $14, $53, $01; 2-Way Bullet Shooter
	.byte $00 | $17, $54, $A0; Corkscrew - Upper terminus
	.byte $60 | $0E, $50, $52; Crate
	.byte $00 | $11, $60, $20, $1A; Wooden Ship Beam
	.byte $00 | $12, $61, $30, $19; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $11, $60, $03; Wooden ship beam terminus A
	.byte $40 | $12, $61, $0B; Background wooden ship beam terminus
	.byte $60 | $10, $63, $62; Portholes
	.byte $00 | $0D, $6E, $41; Wooden Ship Pillar
	.byte $00 | $0C, $6E, $01; 2-Way Bullet Shooter
	.byte $00 | $0B, $74, $1A; Wooden Ship Beam
	.byte $00 | $0C, $74, $1A; Wooden Ship Beam
	.byte $00 | $0D, $73, $1B; Wooden Ship Beam
	.byte $00 | $0E, $72, $1B; Wooden Ship Beam
	.byte $60 | $0A, $74, $2A; Railings
	.byte $20 | $09, $78, $91; Downward Pipe (CAN go down)
	.byte $60 | $0E, $74, $63; Portholes
	.byte $00 | $12, $7B, $70; Corkscrew - Left terminus
	.byte $00 | $0C, $71, $42; Wooden Ship Pillar
	.byte $00 | $0B, $71, $01; 2-Way Bullet Shooter
	; Pointer on screen $07
	.byte $E0 | $07, $00 | $02, 96; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Ship_W2_objects:
	.byte $D3, $00, $04; Autoscrolling
	.byte $B8, $01, $03; Moving Background Clouds
	.byte $BC, $15, $0D; Bullet Bills
	.byte $BC, $18, $0B; Bullet Bills
	.byte $C9, $21, $0A; Bullet Shots (up/right)
	.byte $BC, $29, $0B; Bullet Bills
	.byte $BC, $2F, $0D; Bullet Bills
	.byte $BC, $33, $0A; Bullet Bills
	.byte $BC, $36, $0F; Bullet Bills
	.byte $BC, $42, $11; Bullet Bills
	.byte $BC, $42, $13; Bullet Bills
	.byte $BC, $42, $15; Bullet Bills
	.byte $BC, $53, $10; Bullet Bills
	.byte $BC, $53, $12; Bullet Bills
	.byte $BE, $63, $0F; Rocky Wrench
	.byte $BE, $65, $0F; Rocky Wrench
	.byte $BE, $67, $0F; Rocky Wrench
	.byte $BC, $6E, $0C; Bullet Bills
	.byte $BC, $71, $0B; Bullet Bills
	.byte $FF
; Anchors_Away_W3
; Object Set 10
Anchors_Away_W3_generators:
Anchors_Away_W3_header:
	.byte $0D; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
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
Anchors_Away_W3_objects:
	.byte $09, $16, $14; Ship Anchor
	.byte $FF
; Ship_W3
; Object Set 10
Ship_W3_generators:
Ship_W3_header:
	.byte $02; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_0B0; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_80 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $E0 | $0A; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $00 | $0C, $48, $7F; Corkscrew - Left terminus
	.byte $00 | $0C, $58, $84; Corkscrew - Right terminus
	.byte $00 | $10, $6F, $93; Corkscrew - Lower terminus
	.byte $00 | $0C, $03, $18; Wooden Ship Beam
	.byte $00 | $0D, $04, $17; Wooden Ship Beam
	.byte $00 | $0E, $05, $1E; Wooden Ship Beam
	.byte $00 | $0F, $06, $1D; Wooden Ship Beam
	.byte $00 | $10, $07, $1C; Wooden Ship Beam
	.byte $00 | $11, $09, $20, $1D; Wooden Ship Beam
	.byte $00 | $0C, $03, $03; Wooden ship beam terminus A
	.byte $00 | $0D, $04, $03; Wooden ship beam terminus A
	.byte $00 | $0E, $05, $03; Wooden ship beam terminus A
	.byte $00 | $0F, $06, $03; Wooden ship beam terminus A
	.byte $40 | $10, $07, $0A; Wooden ship beam terminus B
	.byte $40 | $11, $09, $0A; Wooden ship beam terminus B
	.byte $00 | $09, $0F, $64; Thick Wooden Ship Beam
	.byte $00 | $0D, $09, $04; Anchor
	.byte $00 | $12, $11, $20, $15; Wooden Ship Beam
	.byte $00 | $13, $12, $20, $14; Wooden Ship Beam
	.byte $00 | $14, $13, $20, $25; Wooden Ship Beam
	.byte $00 | $12, $11, $03; Wooden ship beam terminus A
	.byte $00 | $13, $12, $03; Wooden ship beam terminus A
	.byte $00 | $14, $13, $03; Wooden ship beam terminus A
	.byte $00 | $0F, $1F, $41; Wooden Ship Pillar
	.byte $00 | $0E, $1F, $01; 2-Way Bullet Shooter
	.byte $60 | $12, $19, $62; Portholes
	.byte $00 | $0B, $27, $12; Wooden Ship Beam
	.byte $00 | $0F, $29, $18; Wooden Ship Beam
	.byte $00 | $10, $29, $18; Wooden Ship Beam
	.byte $00 | $15, $25, $20, $11; Wooden Ship Beam
	.byte $00 | $15, $25, $03; Wooden ship beam terminus A
	.byte $00 | $02, $2C, $6C; Thick Wooden Ship Beam
	.byte $00 | $0B, $25, $65; Thick Wooden Ship Beam
	.byte $00 | $0F, $23, $61; Thick Wooden Ship Beam
	.byte $00 | $0F, $29, $0D; Metal Plated Bullet Shooter B
	.byte $00 | $0F, $2C, $0D; Metal Plated Bullet Shooter B
	.byte $00 | $0F, $2F, $0D; Metal Plated Bullet Shooter B
	.byte $00 | $11, $29, $B8; Metal platform
	.byte $00 | $11, $29, $C2; 1 Metal Bar A
	.byte $00 | $11, $31, $D2; 1 Metal Bar B
	.byte $00 | $09, $3B, $18; Wooden Ship Beam
	.byte $00 | $0A, $3B, $18; Wooden Ship Beam
	.byte $00 | $10, $35, $1F; Wooden Ship Beam
	.byte $00 | $11, $35, $1F; Wooden Ship Beam
	.byte $00 | $12, $35, $20, $3A; Wooden Ship Beam
	.byte $00 | $13, $35, $13; Wooden Ship Beam
	.byte $00 | $0E, $37, $41; Wooden Ship Pillar
	.byte $00 | $09, $3B, $0C; Metal Plated Bullet Shooter A
	.byte $00 | $09, $3F, $0C; Metal Plated Bullet Shooter A
	.byte $00 | $0B, $3B, $B6; Metal platform
	.byte $00 | $0B, $3B, $C4; 1 Metal Bar A
	.byte $00 | $0B, $41, $D4; 1 Metal Bar B
	.byte $20 | $0C, $30, $01; '?' with leaf
	.byte $00 | $0E, $37, $01; 2-Way Bullet Shooter
	.byte $00 | $10, $3C, $0D; Metal Plated Bullet Shooter B
	.byte $00 | $0B, $42, $11; Wooden Ship Beam
	.byte $00 | $0C, $42, $15; Wooden Ship Beam
	.byte $00 | $0E, $4A, $63; Thick Wooden Ship Beam
	.byte $00 | $0E, $4C, $11; Wooden Ship Beam
	.byte $00 | $13, $42, $20, $2A; Wooden Ship Beam
	.byte $00 | $13, $42, $03; Wooden ship beam terminus A
	.byte $00 | $10, $40, $0D; Metal Plated Bullet Shooter B
	.byte $00 | $11, $4C, $01; 2-Way Bullet Shooter
	.byte $00 | $10, $5A, $14; Wooden Ship Beam
	.byte $00 | $11, $5A, $14; Wooden Ship Beam
	.byte $00 | $0C, $5D, $43; Wooden Ship Pillar
	.byte $00 | $0E, $5A, $63; Thick Wooden Ship Beam
	.byte $00 | $0C, $5E, $71; Corkscrew - Left terminus
	.byte $00 | $10, $57, $41; Wooden Ship Pillar
	.byte $00 | $10, $57, $01; 2-Way Bullet Shooter
	.byte $00 | $0E, $58, $63; Thick Wooden Ship Beam
	.byte $00 | $07, $63, $62; Thick Wooden Ship Beam
	.byte $00 | $0A, $62, $13; Wooden Ship Beam
	.byte $00 | $0B, $62, $13; Wooden Ship Beam
	.byte $00 | $0C, $62, $18; Wooden Ship Beam
	.byte $00 | $0D, $62, $18; Wooden Ship Beam
	.byte $00 | $0E, $62, $18; Wooden Ship Beam
	.byte $00 | $0C, $6E, $1E; Wooden Ship Beam
	.byte $00 | $0D, $6E, $1D; Wooden Ship Beam
	.byte $00 | $0E, $6E, $1C; Wooden Ship Beam
	.byte $00 | $0F, $6D, $1D; Wooden Ship Beam
	.byte $40 | $0F, $6D, $0A; Wooden ship beam terminus B
	.byte $00 | $0B, $6F, $05; Top Screw Head
	.byte $60 | $0D, $66, $62; Portholes
	.byte $00 | $0F, $62, $B8; Metal platform
	.byte $00 | $0F, $62, $C2; 1 Metal Bar A
	.byte $00 | $0F, $6A, $D2; 1 Metal Bar B
	.byte $00 | $11, $6E, $01; 2-Way Bullet Shooter
	.byte $00 | $08, $74, $1A; Wooden Ship Beam
	.byte $00 | $09, $74, $1A; Wooden Ship Beam
	.byte $00 | $0A, $73, $1B; Wooden Ship Beam
	.byte $00 | $0B, $72, $1B; Wooden Ship Beam
	.byte $60 | $07, $74, $2A; Railings
	.byte $20 | $06, $78, $91; Downward Pipe (CAN go down)
	.byte $60 | $0B, $74, $63; Portholes
	; Pointer on screen $07
	.byte $E0 | $07, $00 | $02, 96; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Ship_W3_objects:
	.byte $D3, $00, $01; Autoscrolling
	.byte $B8, $01, $03; Moving Background Clouds
	.byte $BE, $19, $11; Rocky Wrench
	.byte $BE, $1B, $11; Rocky Wrench
	.byte $BE, $1D, $11; Rocky Wrench
	.byte $BC, $1F, $0E; Bullet Bills
	.byte $C8, $29, $0F; Bullet Shots (up/left)
	.byte $CB, $2D, $10; Bullet Shots (down/right)
	.byte $CB, $30, $10; Bullet Shots (down/right)
	.byte $BC, $37, $0E; Bullet Bills
	.byte $CA, $3B, $0A; Bullet Shots (down/left)
	.byte $CA, $3F, $0A; Bullet Shots (down/left)
	.byte $C8, $3C, $10; Bullet Shots (up/left)
	.byte $C8, $40, $10; Bullet Shots (up/left)
	.byte $AE, $4B, $0C; Nut (use with corkscrew)
	.byte $B1, $4D, $11; Rightward Rocket Engine
	.byte $AC, $54, $10; Leftward Rocket Engine
	.byte $BE, $66, $0C; Rocky Wrench
	.byte $BE, $68, $0C; Rocky Wrench
	.byte $BE, $6A, $0C; Rocky Wrench
	.byte $AC, $6B, $11; Leftward Rocket Engine
	.byte $FF
; Anchors_Away_W4
; Object Set 10
Anchors_Away_W4_generators:
Anchors_Away_W4_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_03; Next Level High | X Start | Sprite Palette | Block Palette
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
Anchors_Away_W4_objects:
	.byte $09, $16, $14; Ship Anchor
	.byte $FF
; Ship_W4
; Object Set 10
Ship_W4_generators:
Ship_W4_header:
	.byte $03; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_0B0; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_80 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_03; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $E0 | $0A; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $00 | $0F, $0D, $77; Corkscrew - Left terminus
	.byte $00 | $11, $0D, $76; Corkscrew - Left terminus
	.byte $00 | $0F, $1A, $A1; Corkscrew - Upper terminus
	.byte $00 | $0D, $24, $A3; Corkscrew - Upper terminus
	.byte $00 | $0A, $25, $7C; Corkscrew - Left terminus
	.byte $00 | $0C, $36, $A5; Corkscrew - Upper terminus
	.byte $00 | $0C, $48, $A2; Corkscrew - Upper terminus
	.byte $00 | $0A, $56, $A4; Corkscrew - Upper terminus
	.byte $00 | $0F, $5A, $A5; Corkscrew - Upper terminus
	.byte $00 | $0A, $32, $70; Corkscrew - Left terminus
	.byte $00 | $0B, $02, $1D; Wooden Ship Beam
	.byte $00 | $0C, $03, $20, $14; Wooden Ship Beam
	.byte $00 | $0D, $04, $20, $12; Wooden Ship Beam
	.byte $00 | $0E, $05, $18; Wooden Ship Beam
	.byte $00 | $0F, $06, $17; Wooden Ship Beam
	.byte $00 | $10, $07, $16; Wooden Ship Beam
	.byte $00 | $11, $08, $15; Wooden Ship Beam
	.byte $00 | $12, $0A, $30, $03; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $0B, $02, $03; Wooden ship beam terminus A
	.byte $00 | $0C, $03, $03; Wooden ship beam terminus A
	.byte $00 | $0D, $04, $03; Wooden ship beam terminus A
	.byte $00 | $0E, $05, $03; Wooden ship beam terminus A
	.byte $00 | $0F, $06, $03; Wooden ship beam terminus A
	.byte $00 | $10, $07, $03; Wooden ship beam terminus A
	.byte $40 | $11, $08, $0A; Wooden ship beam terminus B
	.byte $40 | $12, $0A, $0B; Background wooden ship beam terminus
	.byte $00 | $0D, $09, $04; Anchor
	.byte $00 | $0D, $17, $45; Wooden Ship Pillar
	.byte $00 | $0E, $16, $44; Wooden Ship Pillar
	.byte $00 | $0E, $18, $12; Wooden Ship Beam
	.byte $00 | $0F, $18, $12; Wooden Ship Beam
	.byte $00 | $0D, $1F, $15; Wooden Ship Beam
	.byte $00 | $11, $1A, $17; Wooden Ship Beam
	.byte $00 | $12, $1A, $30, $19; Wooden Ship Beam with 2 strips of wood
	.byte $40 | $12, $1A, $0B; Background wooden ship beam terminus
	.byte $00 | $0D, $1A, $01; 2-Way Bullet Shooter
	.byte $00 | $0B, $13, $01; 2-Way Bullet Shooter
	.byte $20 | $07, $16, $82; Coins
	.byte $00 | $0C, $20, $13; Wooden Ship Beam
	.byte $00 | $0A, $24, $42; Wooden Ship Pillar
	.byte $00 | $11, $22, $17; Wooden Ship Beam
	.byte $00 | $11, $2A, $19; Wooden Ship Beam
	.byte $00 | $0A, $23, $80; Corkscrew - Right terminus
	.byte $00 | $10, $29, $02; Rocket Engine
	.byte $00 | $10, $2C, $02; Rocket Engine
	.byte $00 | $10, $2F, $02; Rocket Engine
	.byte $20 | $0E, $20, $83; Coins
	.byte $20 | $0F, $20, $83; Coins
	.byte $00 | $0A, $33, $42; Wooden Ship Pillar
	.byte $00 | $0B, $3A, $11; Wooden Ship Beam
	.byte $00 | $0C, $34, $1F; Wooden Ship Beam
	.byte $00 | $12, $35, $16; Wooden Ship Beam
	.byte $00 | $12, $3C, $19; Wooden Ship Beam
	.byte $00 | $13, $35, $30, $10; Wooden Ship Beam with 2 strips of wood
	.byte $40 | $13, $35, $0B; Background wooden ship beam terminus
	.byte $00 | $0A, $34, $70; Corkscrew - Left terminus
	.byte $00 | $0D, $3D, $02; Rocket Engine
	.byte $00 | $11, $38, $01; 2-Way Bullet Shooter
	.byte $20 | $09, $3E, $01; '?' with leaf
	.byte $00 | $0C, $40, $13; Wooden Ship Beam
	.byte $00 | $0B, $48, $14; Wooden Ship Beam
	.byte $00 | $0C, $48, $14; Wooden Ship Beam
	.byte $00 | $0E, $46, $41; Wooden Ship Pillar
	.byte $00 | $0F, $47, $11; Wooden Ship Beam
	.byte $00 | $11, $49, $14; Wooden Ship Beam
	.byte $00 | $12, $49, $14; Wooden Ship Beam
	.byte $00 | $13, $49, $30, $04; Wooden Ship Beam with 2 strips of wood
	.byte $40 | $13, $49, $0B; Background wooden ship beam terminus
	.byte $00 | $0A, $48, $01; 2-Way Bullet Shooter
	.byte $00 | $11, $42, $01; 2-Way Bullet Shooter
	.byte $00 | $0D, $4A, $02; Rocket Engine
	.byte $00 | $0A, $53, $13; Wooden Ship Beam
	.byte $00 | $0F, $56, $14; Wooden Ship Beam
	.byte $00 | $12, $50, $15; Wooden Ship Beam
	.byte $00 | $12, $5B, $13; Wooden Ship Beam
	.byte $00 | $13, $50, $14; Wooden Ship Beam
	.byte $00 | $13, $55, $42; Wooden Ship Pillar
	.byte $00 | $13, $5B, $42; Wooden Ship Pillar
	.byte $00 | $13, $5C, $12; Wooden Ship Beam
	.byte $00 | $14, $50, $14; Wooden Ship Beam
	.byte $00 | $15, $51, $13; Wooden Ship Beam
	.byte $00 | $15, $56, $14; Wooden Ship Beam
	.byte $00 | $16, $54, $30, $07; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $14, $50, $03; Wooden ship beam terminus A
	.byte $40 | $15, $51, $0A; Wooden ship beam terminus B
	.byte $40 | $16, $54, $0B; Background wooden ship beam terminus
	.byte $00 | $0B, $55, $02; Rocket Engine
	.byte $00 | $0E, $5A, $01; 2-Way Bullet Shooter
	.byte $00 | $11, $51, $01; 2-Way Bullet Shooter
	.byte $00 | $14, $58, $02; Rocket Engine
	.byte $00 | $15, $65, $30, $04; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $0C, $64, $44; Wooden Ship Pillar
	.byte $00 | $0C, $65, $15; Wooden Ship Beam
	.byte $00 | $11, $64, $13; Wooden Ship Beam
	.byte $00 | $14, $66, $13; Wooden Ship Beam
	.byte $00 | $15, $60, $15; Wooden Ship Beam
	.byte $00 | $16, $60, $30, $05; Wooden Ship Beam with 2 strips of wood
	.byte $40 | $16, $60, $0B; Background wooden ship beam terminus
	.byte $00 | $0C, $6E, $1A; Wooden Ship Beam
	.byte $00 | $0D, $6E, $1A; Wooden Ship Beam
	.byte $00 | $0E, $6D, $1B; Wooden Ship Beam
	.byte $00 | $0F, $6C, $1B; Wooden Ship Beam
	.byte $00 | $10, $6B, $1B; Wooden Ship Beam
	.byte $00 | $11, $6A, $1B; Wooden Ship Beam
	.byte $00 | $12, $6A, $1A; Wooden Ship Beam
	.byte $00 | $13, $6A, $30, $0A; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $0B, $6A, $01; 2-Way Bullet Shooter
	.byte $60 | $0B, $6E, $2A; Railings
	.byte $00 | $0D, $6D, $01; 2-Way Bullet Shooter
	.byte $60 | $0F, $6E, $63; Portholes
	.byte $00 | $10, $67, $01; 2-Way Bullet Shooter
	.byte $00 | $12, $64, $B1; Metal platform
	.byte $00 | $12, $64, $C2; 1 Metal Bar A
	.byte $00 | $12, $65, $D2; 1 Metal Bar B
	.byte $00 | $14, $62, $02; Rocket Engine
	.byte $00 | $13, $75, $71; Corkscrew - Left terminus
	.byte $20 | $08, $78, $01; '?' with leaf
	.byte $20 | $0A, $72, $91; Downward Pipe (CAN go down)
	; Pointer on screen $07
	.byte $E0 | $07, $00 | $02, 96; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Ship_W4_objects:
	.byte $D3, $00, $05; Autoscrolling
	.byte $B8, $01, $03; Moving Background Clouds
	.byte $B1, $14, $0B; Rightward Rocket Engine
	.byte $AA, $15, $0F; Propeller
	.byte $AA, $14, $11; Propeller
	.byte $B1, $1B, $0D; Rightward Rocket Engine
	.byte $AE, $26, $0A; Nut (use with corkscrew)
	.byte $9D, $29, $0D; Upward Rocket Engine
	.byte $9D, $2C, $0D; Upward Rocket Engine
	.byte $9D, $2F, $0D; Upward Rocket Engine
	.byte $B1, $39, $11; Rightward Rocket Engine
	.byte $AC, $3F, $11; Leftward Rocket Engine
	.byte $B2, $3D, $0E; Downward Rocket Engine
	.byte $BE, $3A, $0B; Rocky Wrench
	.byte $B2, $4A, $0E; Downward Rocket Engine
	.byte $B1, $49, $0A; Rightward Rocket Engine
	.byte $B2, $55, $0C; Downward Rocket Engine
	.byte $AC, $57, $0E; Leftward Rocket Engine
	.byte $B1, $52, $11; Rightward Rocket Engine
	.byte $9D, $58, $11; Upward Rocket Engine
	.byte $B1, $6B, $0B; Rightward Rocket Engine
	.byte $AC, $6A, $0D; Leftward Rocket Engine
	.byte $B1, $68, $10; Rightward Rocket Engine
	.byte $9D, $62, $11; Upward Rocket Engine
	.byte $AA, $77, $13; Propeller
	.byte $FF
; Anchors_Away_W5
; Object Set 10
Anchors_Away_W5_generators:
Anchors_Away_W5_header:
	.byte $11; Next Level
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
Anchors_Away_W5_objects:
	.byte $09, $16, $14; Ship Anchor
	.byte $FF
; Ship_W5
; Object Set 10
Ship_W5_generators:
Ship_W5_header:
	.byte $04; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_0B0; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_80 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $E0 | $0A; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $00 | $0C, $03, $1B; Wooden Ship Beam
	.byte $00 | $0D, $04, $1A; Wooden Ship Beam
	.byte $00 | $0E, $05, $1D; Wooden Ship Beam
	.byte $00 | $0F, $06, $1D; Wooden Ship Beam
	.byte $00 | $10, $07, $20, $11; Wooden Ship Beam
	.byte $00 | $11, $09, $20, $10; Wooden Ship Beam
	.byte $00 | $0C, $03, $03; Wooden ship beam terminus A
	.byte $00 | $0D, $04, $03; Wooden ship beam terminus A
	.byte $00 | $0E, $05, $03; Wooden ship beam terminus A
	.byte $00 | $0F, $06, $03; Wooden ship beam terminus A
	.byte $40 | $10, $07, $0A; Wooden ship beam terminus B
	.byte $40 | $11, $09, $0A; Wooden ship beam terminus B
	.byte $00 | $0D, $09, $04; Anchor
	.byte $00 | $0E, $1A, $63; Thick Wooden Ship Beam
	.byte $00 | $12, $15, $16; Wooden Ship Beam
	.byte $00 | $13, $17, $14; Wooden Ship Beam
	.byte $00 | $14, $19, $20, $15; Wooden Ship Beam
	.byte $00 | $15, $1B, $20, $10; Wooden Ship Beam
	.byte $00 | $16, $1D, $1D; Wooden Ship Beam
	.byte $00 | $17, $1F, $30, $0B; Wooden Ship Beam with 2 strips of wood
	.byte $40 | $12, $15, $0A; Wooden ship beam terminus B
	.byte $40 | $13, $17, $0A; Wooden ship beam terminus B
	.byte $40 | $14, $19, $0A; Wooden ship beam terminus B
	.byte $40 | $15, $1B, $0A; Wooden ship beam terminus B
	.byte $40 | $16, $1D, $0A; Wooden ship beam terminus B
	.byte $40 | $17, $1F, $0B; Background wooden ship beam terminus
	.byte $00 | $0D, $1B, $01; 2-Way Bullet Shooter
	.byte $00 | $0F, $17, $06; Bullet Shooter - Up/Left
	.byte $60 | $10, $1D, $52; Crate
	.byte $00 | $0D, $2D, $42; Wooden Ship Pillar
	.byte $00 | $10, $2C, $20, $1B; Wooden Ship Beam
	.byte $00 | $11, $2C, $20, $1B; Wooden Ship Beam
	.byte $00 | $12, $2C, $15; Wooden Ship Beam
	.byte $00 | $13, $2C, $15; Wooden Ship Beam
	.byte $00 | $0C, $2D, $01; 2-Way Bullet Shooter
	.byte $20 | $10, $22, $00; '?' with flower
	.byte $60 | $10, $28, $53; Crate
	.byte $00 | $15, $24, $0D; Metal Plated Bullet Shooter B
	.byte $00 | $15, $27, $0D; Metal Plated Bullet Shooter B
	.byte $00 | $17, $2B, $70; Corkscrew - Left terminus
	.byte $00 | $0B, $36, $18; Wooden Ship Beam
	.byte $00 | $0C, $36, $18; Wooden Ship Beam
	.byte $00 | $0D, $35, $19; Wooden Ship Beam
	.byte $00 | $0E, $34, $1A; Wooden Ship Beam
	.byte $00 | $0F, $33, $20, $14; Wooden Ship Beam
	.byte $60 | $05, $37, $45, $06; Metal box platform
	.byte $00 | $06, $38, $0C; Metal Plated Bullet Shooter A
	.byte $00 | $07, $3B, $0D; Metal Plated Bullet Shooter B
	.byte $60 | $0D, $38, $62; Portholes
	.byte $00 | $13, $32, $70; Corkscrew - Left terminus
	.byte $00 | $08, $49, $13; Wooden Ship Beam
	.byte $00 | $0E, $4E, $11; Wooden Ship Beam
	.byte $00 | $0F, $4C, $16; Wooden Ship Beam
	.byte $00 | $10, $4C, $20, $2F; Wooden Ship Beam
	.byte $00 | $11, $4C, $20, $2E; Wooden Ship Beam
	.byte $00 | $12, $41, $30, $39; Wooden Ship Beam with 2 strips of wood
	.byte $40 | $12, $41, $0B; Background wooden ship beam terminus
	.byte $00 | $07, $4C, $05; Top Screw Head
	.byte $00 | $09, $49, $0A; 4-Way Bullet Shooter A
	.byte $00 | $09, $4C, $B3; Metal platform
	.byte $00 | $09, $4F, $D1; 1 Metal Bar B
	.byte $00 | $0C, $4E, $0C; Metal Plated Bullet Shooter A
	.byte $00 | $0F, $44, $0D; Metal Plated Bullet Shooter B
	.byte $00 | $09, $50, $45; Wooden Ship Pillar
	.byte $00 | $0F, $5A, $20, $22; Wooden Ship Beam
	.byte $60 | $08, $5C, $46, $0F; Metal box platform
	.byte $00 | $08, $50, $05; Top Screw Head
	.byte $00 | $09, $5D, $0C; Metal Plated Bullet Shooter A
	.byte $00 | $0E, $5A, $01; 2-Way Bullet Shooter
	.byte $00 | $10, $5E, $0C; Metal Plated Bullet Shooter A
	.byte $00 | $13, $50, $A0; Corkscrew - Upper terminus
	.byte $00 | $09, $61, $0C; Metal Plated Bullet Shooter A
	.byte $00 | $09, $65, $0D; Metal Plated Bullet Shooter B
	.byte $00 | $09, $69, $0D; Metal Plated Bullet Shooter B
	.byte $00 | $10, $61, $0C; Metal Plated Bullet Shooter A
	.byte $00 | $10, $65, $0D; Metal Plated Bullet Shooter B
	.byte $00 | $10, $68, $0D; Metal Plated Bullet Shooter B
	.byte $00 | $0B, $74, $1A; Wooden Ship Beam
	.byte $00 | $0C, $74, $1A; Wooden Ship Beam
	.byte $00 | $0D, $73, $1B; Wooden Ship Beam
	.byte $00 | $0E, $72, $1B; Wooden Ship Beam
	.byte $60 | $0A, $74, $2A; Railings
	.byte $20 | $09, $78, $91; Downward Pipe (CAN go down)
	.byte $60 | $0E, $74, $63; Portholes
	.byte $00 | $12, $7B, $71; Corkscrew - Left terminus
	.byte $00 | $0C, $70, $01; 2-Way Bullet Shooter
	.byte $00 | $0D, $70, $41; Wooden Ship Pillar
	; Pointer on screen $07
	.byte $E0 | $07, $00 | $02, 96; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Ship_W5_objects:
	.byte $D3, $00, $03; Autoscrolling
	.byte $B8, $01, $03; Moving Background Clouds
	.byte $C4, $17, $0F; Bullet Shots (up/left)
	.byte $AC, $18, $0D; Leftward Rocket Engine
	.byte $C8, $24, $15; Bullet Shots (up/left)
	.byte $C8, $27, $15; Bullet Shots (up/left)
	.byte $BC, $2D, $0C; Bullet Bills
	.byte $CA, $38, $07; Bullet Shots (down/left)
	.byte $CB, $3C, $08; Bullet Shots (down/right)
	.byte $C8, $44, $0F; Bullet Shots (up/left)
	.byte $BF, $49, $0A; Cross-shaped bullet shots
	.byte $CA, $4E, $0D; Bullet Shots (down/left)
	.byte $CA, $5D, $0A; Bullet Shots (down/left)
	.byte $C9, $5F, $10; Bullet Shots (up/right)
	.byte $BC, $5A, $0E; Bullet Bills
	.byte $CA, $61, $0A; Bullet Shots (down/left)
	.byte $C9, $62, $10; Bullet Shots (up/right)
	.byte $CB, $66, $0A; Bullet Shots (down/right)
	.byte $C8, $65, $10; Bullet Shots (up/left)
	.byte $CB, $6A, $0A; Bullet Shots (down/right)
	.byte $C8, $68, $10; Bullet Shots (up/left)
	.byte $BC, $70, $0C; Bullet Bills
	.byte $FF
; Anchors_Away_W6
; Object Set 10
Anchors_Away_W6_generators:
Anchors_Away_W6_header:
	.byte $13; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
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
Anchors_Away_W6_objects:
	.byte $09, $16, $14; Ship Anchor
	.byte $FF
; Ship_W6
; Object Set 10
Ship_W6_generators:
Ship_W6_header:
	.byte $05; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_0B0; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_80 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $E0 | $0A; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $00 | $0F, $0D, $75; Corkscrew - Left terminus
	.byte $00 | $11, $0D, $73; Corkscrew - Left terminus
	.byte $00 | $0F, $16, $78; Corkscrew - Left terminus
	.byte $00 | $0D, $2B, $78; Corkscrew - Left terminus
	.byte $00 | $0F, $29, $7F; Corkscrew - Left terminus
	.byte $00 | $0F, $39, $81; Corkscrew - Right terminus
	.byte $00 | $0B, $3B, $93; Corkscrew - Lower terminus
	.byte $00 | $07, $6B, $73; Corkscrew - Left terminus
	.byte $00 | $0D, $61, $76; Corkscrew - Left terminus
	.byte $00 | $0F, $1F, $70; Corkscrew - Left terminus
	.byte $00 | $0B, $04, $1B; Wooden Ship Beam
	.byte $00 | $0C, $05, $1A; Wooden Ship Beam
	.byte $00 | $0D, $06, $1E; Wooden Ship Beam
	.byte $00 | $0E, $07, $16; Wooden Ship Beam
	.byte $00 | $0F, $08, $15; Wooden Ship Beam
	.byte $00 | $10, $09, $14; Wooden Ship Beam
	.byte $00 | $11, $0B, $30, $02; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $0B, $04, $03; Wooden ship beam terminus A
	.byte $00 | $0C, $05, $03; Wooden ship beam terminus A
	.byte $00 | $0D, $06, $03; Wooden ship beam terminus A
	.byte $00 | $0E, $07, $03; Wooden ship beam terminus A
	.byte $00 | $0F, $08, $03; Wooden ship beam terminus A
	.byte $40 | $10, $09, $0A; Wooden ship beam terminus B
	.byte $40 | $11, $0B, $0B; Background wooden ship beam terminus
	.byte $00 | $0D, $09, $04; Anchor
	.byte $00 | $0D, $15, $44; Wooden Ship Pillar
	.byte $00 | $0E, $14, $43; Wooden Ship Pillar
	.byte $00 | $0B, $25, $16; Wooden Ship Beam
	.byte $00 | $0C, $25, $16; Wooden Ship Beam
	.byte $00 | $0D, $24, $16; Wooden Ship Beam
	.byte $00 | $0E, $24, $15; Wooden Ship Beam
	.byte $00 | $0F, $20, $18; Wooden Ship Beam
	.byte $00 | $10, $20, $17; Wooden Ship Beam
	.byte $00 | $11, $20, $30, $07; Wooden Ship Beam with 2 strips of wood
	.byte $60 | $0A, $26, $25; Railings
	.byte $00 | $11, $3C, $14; Wooden Ship Beam
	.byte $00 | $12, $3C, $14; Wooden Ship Beam
	.byte $00 | $13, $3C, $16; Wooden Ship Beam
	.byte $00 | $14, $37, $1B; Wooden Ship Beam
	.byte $00 | $15, $39, $19; Wooden Ship Beam
	.byte $00 | $16, $3A, $1C; Wooden Ship Beam
	.byte $00 | $17, $3B, $1B; Wooden Ship Beam
	.byte $00 | $18, $3C, $1E; Wooden Ship Beam
	.byte $00 | $19, $3E, $30, $0D; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $0E, $3B, $46; Wooden Ship Pillar
	.byte $00 | $14, $37, $03; Wooden ship beam terminus A
	.byte $00 | $15, $39, $03; Wooden ship beam terminus A
	.byte $00 | $16, $3A, $03; Wooden ship beam terminus A
	.byte $00 | $17, $3B, $03; Wooden ship beam terminus A
	.byte $40 | $18, $3C, $0A; Wooden ship beam terminus B
	.byte $40 | $19, $3E, $0B; Background wooden ship beam terminus
	.byte $00 | $11, $3A, $80; Corkscrew - Right terminus
	.byte $00 | $04, $40, $48; Wooden Ship Pillar
	.byte $00 | $04, $41, $47; Wooden Ship Pillar
	.byte $00 | $0C, $41, $12; Wooden Ship Beam
	.byte $00 | $0C, $44, $42; Wooden Ship Pillar
	.byte $00 | $0B, $45, $43; Wooden Ship Pillar
	.byte $00 | $0F, $44, $19; Wooden Ship Beam
	.byte $00 | $0F, $4E, $1E; Wooden Ship Beam
	.byte $00 | $10, $46, $14; Wooden Ship Beam
	.byte $00 | $10, $4B, $16; Wooden Ship Beam
	.byte $00 | $11, $46, $20, $14; Wooden Ship Beam
	.byte $00 | $12, $4B, $1F; Wooden Ship Beam
	.byte $00 | $13, $43, $42; Wooden Ship Pillar
	.byte $00 | $16, $47, $42; Wooden Ship Pillar
	.byte $60 | $0B, $46, $52; Crate
	.byte $60 | $0B, $49, $52; Crate
	.byte $00 | $12, $41, $01; 2-Way Bullet Shooter
	.byte $00 | $17, $49, $02; Rocket Engine
	.byte $00 | $19, $4E, $30, $0F; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $10, $52, $1A; Wooden Ship Beam
	.byte $00 | $12, $54, $41; Wooden Ship Pillar
	.byte $00 | $12, $55, $41; Wooden Ship Pillar
	.byte $00 | $12, $56, $41; Wooden Ship Pillar
	.byte $00 | $17, $50, $41; Wooden Ship Pillar
	.byte $00 | $18, $51, $11; Wooden Ship Beam
	.byte $00 | $18, $54, $41; Wooden Ship Pillar
	.byte $00 | $18, $55, $41; Wooden Ship Pillar
	.byte $00 | $18, $56, $41; Wooden Ship Pillar
	.byte $00 | $04, $5D, $1B; Wooden Ship Beam
	.byte $00 | $05, $5F, $19; Wooden Ship Beam
	.byte $00 | $04, $5D, $03; Wooden ship beam terminus A
	.byte $00 | $05, $5F, $03; Wooden ship beam terminus A
	.byte $00 | $13, $5E, $13; Wooden Ship Beam
	.byte $00 | $14, $5E, $14; Wooden Ship Beam
	.byte $00 | $15, $5D, $11; Wooden Ship Beam
	.byte $00 | $16, $5D, $11; Wooden Ship Beam
	.byte $00 | $17, $5A, $13; Wooden Ship Beam
	.byte $00 | $18, $5A, $13; Wooden Ship Beam
	.byte $00 | $14, $55, $02; Rocket Engine
	.byte $00 | $18, $53, $02; Rocket Engine
	.byte $00 | $18, $57, $02; Rocket Engine
	.byte $20 | $0B, $5B, $01; '?' with leaf
	.byte $20 | $0B, $5C, $20; '?' blocks with single coins
	.byte $00 | $12, $60, $01; 2-Way Bullet Shooter
	.byte $00 | $06, $69, $01; 2-Way Bullet Shooter
	.byte $00 | $0D, $62, $30, $16; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $06, $60, $18; Wooden Ship Beam
	.byte $00 | $07, $61, $1A; Wooden Ship Beam
	.byte $00 | $06, $60, $03; Wooden ship beam terminus A
	.byte $00 | $07, $61, $03; Wooden ship beam terminus A
	.byte $00 | $04, $6F, $45; Wooden Ship Pillar
	.byte $00 | $0A, $6F, $1B; Wooden Ship Beam
	.byte $00 | $0B, $6D, $1C; Wooden Ship Beam
	.byte $00 | $0C, $6D, $1B; Wooden Ship Beam
	.byte $00 | $0D, $68, $14; Wooden Ship Beam
	.byte $00 | $0D, $61, $45; Wooden Ship Pillar
	.byte $00 | $0E, $62, $45; Wooden Ship Pillar
	.byte $00 | $0E, $63, $46; Wooden Ship Pillar
	.byte $00 | $06, $72, $1A; Wooden Ship Beam
	.byte $00 | $07, $72, $1A; Wooden Ship Beam
	.byte $00 | $08, $71, $1B; Wooden Ship Beam
	.byte $00 | $09, $70, $1B; Wooden Ship Beam
	.byte $00 | $07, $70, $70; Corkscrew - Left terminus
	.byte $60 | $05, $73, $29; Railings
	.byte $60 | $09, $72, $63; Portholes
	.byte $20 | $04, $76, $91; Downward Pipe (CAN go down)
	; Pointer on screen $07
	.byte $E0 | $07, $00 | $02, 96; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Ship_W6_objects:
	.byte $D3, $00, $06; Autoscrolling
	.byte $B8, $01, $03; Moving Background Clouds
	.byte $AA, $13, $0F; Propeller
	.byte $AA, $11, $11; Propeller
	.byte $AE, $18, $0F; Nut (use with corkscrew)
	.byte $AE, $2E, $0D; Nut (use with corkscrew)
	.byte $AE, $34, $0F; Nut (use with corkscrew)
	.byte $AB, $3B, $0A; MSG_NOTHING
	.byte $B1, $42, $12; Rightward Rocket Engine
	.byte $9D, $49, $14; Upward Rocket Engine
	.byte $9D, $53, $15; Upward Rocket Engine
	.byte $B2, $55, $15; Downward Rocket Engine
	.byte $9D, $57, $15; Upward Rocket Engine
	.byte $AC, $5D, $12; Leftward Rocket Engine
	.byte $B1, $6A, $06; Rightward Rocket Engine
	.byte $FF
; Anchors_Away_W7
; Object Set 10
Anchors_Away_W7_generators:
Anchors_Away_W7_header:
	.byte $15; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $C0 | $0A; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $60 | $19, $00, $3F; Ground (like on tank levels)
	.byte $60 | $19, $10, $3F; Ground (like on tank levels)
	.byte $40 | $00, $10, $0E; Corner of Airship - Lasts 32 Blocks
	.byte $60 | $19, $20, $3F; Ground (like on tank levels)
	; Pointer on screen $01
	.byte $E0 | $01, $10 | $01, 112; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Anchors_Away_W7_objects:
	.byte $09, $16, $14; Ship Anchor
	.byte $FF
; Ship_W7
; Object Set 10
Ship_W7_generators:
Ship_W7_header:
	.byte $06; Next Level
	.byte LEVEL1_SIZE_14 | LEVEL1_YSTART_040; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_80 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_10; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $E0 | $0A; Start action | Graphic set
	.byte $00 | $05; Time | Music
	.byte $00 | $06, $02, $19; Wooden Ship Beam
	.byte $00 | $07, $03, $18; Wooden Ship Beam
	.byte $00 | $08, $04, $1E; Wooden Ship Beam
	.byte $00 | $09, $05, $1D; Wooden Ship Beam
	.byte $00 | $0A, $07, $30, $0B; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $06, $02, $03; Wooden ship beam terminus A
	.byte $00 | $07, $03, $03; Wooden ship beam terminus A
	.byte $00 | $08, $04, $03; Wooden ship beam terminus A
	.byte $00 | $09, $05, $03; Wooden ship beam terminus A
	.byte $40 | $0A, $07, $0B; Background wooden ship beam terminus
	.byte $00 | $07, $09, $04; Anchor
	.byte $00 | $0A, $23, $30, $02; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $08, $13, $7F; Corkscrew - Left terminus
	.byte $00 | $0A, $13, $83; Corkscrew - Right terminus
	.byte $00 | $0A, $18, $74; Corkscrew - Left terminus
	.byte $00 | $0A, $1A, $83; Corkscrew - Right terminus
	.byte $00 | $0A, $1F, $74; Corkscrew - Left terminus
	.byte $00 | $0A, $17, $02; Rocket Engine
	.byte $00 | $0A, $1E, $02; Rocket Engine
	.byte $00 | $06, $24, $13; Wooden Ship Beam
	.byte $00 | $07, $24, $13; Wooden Ship Beam
	.byte $00 | $08, $24, $13; Wooden Ship Beam
	.byte $60 | $09, $24, $70, $03; Wooden Tank Beam
	.byte $00 | $09, $24, $11; Wooden Ship Beam
	.byte $00 | $08, $22, $81; Corkscrew - Right terminus
	.byte $00 | $0A, $22, $81; Corkscrew - Right terminus
	.byte $00 | $07, $2B, $65; Thick Wooden Ship Beam
	.byte $00 | $0D, $2E, $71; Corkscrew - Left terminus
	.byte $00 | $0D, $28, $15; Wooden Ship Beam
	.byte $00 | $0D, $28, $03; Wooden ship beam terminus A
	.byte $00 | $08, $28, $71; Corkscrew - Left terminus
	.byte $00 | $08, $29, $81; Corkscrew - Right terminus
	.byte $00 | $08, $2D, $7F; Corkscrew - Left terminus
	.byte $00 | $0B, $2D, $72; Corkscrew - Left terminus
	.byte $20 | $0A, $29, $00; '?' with flower
	.byte $00 | $08, $3D, $8F; Corkscrew - Right terminus
	.byte $00 | $0B, $30, $82; Corkscrew - Right terminus
	.byte $00 | $0B, $34, $75; Corkscrew - Left terminus
	.byte $00 | $0B, $39, $81; Corkscrew - Right terminus
	.byte $00 | $0E, $3E, $73; Corkscrew - Left terminus
	.byte $00 | $0A, $3B, $63; Thick Wooden Ship Beam
	.byte $00 | $0E, $38, $15; Wooden Ship Beam
	.byte $00 | $0E, $38, $03; Wooden ship beam terminus A
	.byte $00 | $0B, $33, $02; Rocket Engine
	.byte $00 | $0B, $3D, $00; Right Screw Head
	.byte $00 | $0E, $4E, $30, $03; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $0E, $41, $81; Corkscrew - Right terminus
	.byte $00 | $0E, $44, $79; Corkscrew - Left terminus
	.byte $00 | $0E, $4D, $81; Corkscrew - Right terminus
	.byte $00 | $0E, $43, $02; Rocket Engine
	.byte $00 | $07, $4D, $63; Thick Wooden Ship Beam
	.byte $00 | $08, $4F, $00; Right Screw Head
	.byte $00 | $0B, $4A, $17; Wooden Ship Beam
	.byte $00 | $0C, $4B, $16; Wooden Ship Beam
	.byte $00 | $0B, $4A, $03; Wooden ship beam terminus A
	.byte $60 | $0D, $4C, $70, $26; Wooden Tank Beam
	.byte $00 | $0C, $4B, $03; Wooden ship beam terminus A
	.byte $40 | $0D, $4C, $0A; Wooden ship beam terminus B
	.byte $00 | $06, $59, $13; Wooden Ship Beam
	.byte $00 | $07, $59, $15; Wooden Ship Beam
	.byte $00 | $08, $59, $16; Wooden Ship Beam
	.byte $00 | $09, $59, $16; Wooden Ship Beam
	.byte $00 | $0A, $58, $87; Corkscrew - Right terminus
	.byte $00 | $08, $60, $63; Thick Wooden Ship Beam
	.byte $00 | $0A, $68, $12; Wooden Ship Beam
	.byte $00 | $0B, $67, $14; Wooden Ship Beam
	.byte $00 | $0C, $66, $16; Wooden Ship Beam
	.byte $20 | $05, $60, $00; '?' with flower
	.byte $00 | $0A, $70, $13; Wooden Ship Beam
	.byte $00 | $0B, $70, $13; Wooden Ship Beam
	.byte $60 | $0C, $70, $70, $03; Wooden Tank Beam
	.byte $00 | $0C, $70, $11; Wooden Ship Beam
	.byte $00 | $0B, $74, $75; Corkscrew - Left terminus
	.byte $00 | $0B, $79, $81; Corkscrew - Right terminus
	.byte $00 | $0A, $7B, $62; Thick Wooden Ship Beam
	.byte $00 | $0D, $79, $14; Wooden Ship Beam
	.byte $00 | $0D, $79, $03; Wooden ship beam terminus A
	.byte $00 | $0B, $7D, $70; Corkscrew - Left terminus
	.byte $00 | $09, $89, $14; Wooden Ship Beam
	.byte $00 | $09, $89, $03; Wooden ship beam terminus A
	.byte $00 | $09, $8E, $71; Corkscrew - Left terminus
	.byte $00 | $0D, $83, $14; Wooden Ship Beam
	.byte $00 | $0D, $83, $03; Wooden ship beam terminus A
	.byte $00 | $0D, $88, $71; Corkscrew - Left terminus
	.byte $60 | $08, $8B, $00; Rocky Wrench hole
	.byte $60 | $0C, $85, $00; Rocky Wrench hole
	.byte $00 | $08, $9D, $11; Wooden Ship Beam
	.byte $00 | $08, $9D, $03; Wooden ship beam terminus A
	.byte $00 | $0A, $93, $11; Wooden Ship Beam
	.byte $00 | $0A, $93, $03; Wooden ship beam terminus A
	.byte $00 | $08, $9F, $74; Corkscrew - Left terminus
	.byte $00 | $0A, $95, $74; Corkscrew - Left terminus
	.byte $00 | $0B, $A7, $11; Wooden Ship Beam
	.byte $00 | $0B, $A7, $03; Wooden ship beam terminus A
	.byte $00 | $0B, $A9, $76; Corkscrew - Left terminus
	.byte $00 | $0A, $B2, $17; Wooden Ship Beam
	.byte $00 | $0B, $B3, $16; Wooden Ship Beam
	.byte $00 | $0C, $B4, $17; Wooden Ship Beam
	.byte $00 | $0D, $B6, $30, $05; Wooden Ship Beam with 2 strips of wood
	.byte $00 | $07, $B8, $62; Thick Wooden Ship Beam
	.byte $00 | $0A, $B2, $03; Wooden ship beam terminus A
	.byte $00 | $0B, $B3, $03; Wooden ship beam terminus A
	.byte $40 | $0C, $B4, $0A; Wooden ship beam terminus B
	.byte $40 | $0D, $B6, $0B; Background wooden ship beam terminus
	.byte $00 | $07, $BA, $75; Corkscrew - Left terminus
	.byte $00 | $0A, $BA, $79; Corkscrew - Left terminus
	.byte $00 | $0D, $BC, $73; Corkscrew - Left terminus
	.byte $00 | $09, $CF, $1D; Wooden Ship Beam
	.byte $00 | $0A, $CC, $1F; Wooden Ship Beam
	.byte $00 | $0B, $C8, $20, $11; Wooden Ship Beam
	.byte $00 | $0C, $C8, $20, $10; Wooden Ship Beam
	.byte $00 | $0D, $C8, $20, $10; Wooden Ship Beam
	.byte $00 | $04, $C8, $66; Thick Wooden Ship Beam
	.byte $00 | $07, $C0, $87; Corkscrew - Right terminus
	.byte $00 | $04, $D3, $1A; Wooden Ship Beam
	.byte $00 | $05, $D3, $1A; Wooden Ship Beam
	.byte $00 | $06, $D2, $1B; Wooden Ship Beam
	.byte $00 | $07, $D2, $1B; Wooden Ship Beam
	.byte $00 | $08, $D1, $1C; Wooden Ship Beam
	.byte $60 | $03, $D4, $29; Railings
	.byte $20 | $03, $D6, $90; Downward Pipe (CAN go down)
	.byte $00 | $08, $D3, $0E; Wooden Background Box
	.byte $00 | $08, $D6, $0E; Wooden Background Box
	.byte $00 | $08, $D9, $0E; Wooden Background Box
	.byte $00 | $0D, $D9, $71; Corkscrew - Left terminus
	; Pointer on screen $0D
	.byte $E0 | $0D, $00 | $02, 96; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Ship_W7_objects:
	.byte $D3, $00, $0C; Autoscrolling
	.byte $B8, $01, $03; Moving Background Clouds
	.byte $9D, $17, $07; Upward Rocket Engine
	.byte $9D, $1E, $07; Upward Rocket Engine
	.byte $AE, $14, $08; Nut (use with corkscrew)
	.byte $AA, $15, $0A; Propeller
	.byte $AE, $2E, $08; Nut (use with corkscrew)
	.byte $AA, $30, $0D; Propeller
	.byte $9D, $33, $08; Upward Rocket Engine
	.byte $AA, $3F, $0E; Propeller
	.byte $9D, $43, $0B; Upward Rocket Engine
	.byte $BE, $55, $0D; Rocky Wrench
	.byte $BE, $5B, $0D; Rocky Wrench
	.byte $AE, $5A, $0A; Nut (use with corkscrew)
	.byte $BE, $69, $0A; Rocky Wrench
	.byte $AE, $75, $0B; Nut (use with corkscrew)
	.byte $BE, $85, $0D; Rocky Wrench
	.byte $BE, $8B, $09; Rocky Wrench
	.byte $AA, $8A, $0D; Propeller
	.byte $AA, $90, $09; Propeller
	.byte $AE, $96, $0A; Nut (use with corkscrew)
	.byte $AE, $A0, $08; Nut (use with corkscrew)
	.byte $AE, $AA, $0B; Nut (use with corkscrew)
	.byte $AE, $BD, $0D; Nut (use with corkscrew)
	.byte $AE, $C1, $0A; Nut (use with corkscrew)
	.byte $AE, $C4, $07; Nut (use with corkscrew)
	.byte $AA, $DB, $0D; Propeller
	.byte $FF
; Coin_Ship_Boss_Room_W1
; Object Set 10
Coin_Ship_Boss_Room_W1_generators:
Coin_Ship_Boss_Room_W1_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0A; Start action | Graphic set
	.byte $00 | $06; Time | Music
	.byte $00 | $00, $00, $0F; Black boss room background
	.byte $00 | $0F, $00, $4B; Wooden Ship Pillar
	.byte $00 | $0F, $0F, $4B; Wooden Ship Pillar
	.byte $00 | $19, $01, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $03, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $05, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $07, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $09, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $0B, $61; Thick Wooden Ship Beam
	.byte $00 | $19, $0D, $61; Thick Wooden Ship Beam
	.byte $00 | $14, $01, $F1; 1 Background Pillar
	.byte $00 | $16, $0A, $F2; 1 Background Pillar
	.byte $00 | $17, $0C, $F1; 1 Background Pillar
	.byte $00 | $15, $0D, $F3; 1 Background Pillar
	.byte $60 | $16, $02, $10; Wooden Ship Background Line
	.byte $60 | $15, $04, $10; Wooden Ship Background Line
	.byte $60 | $17, $05, $10; Wooden Ship Background Line
	.byte $60 | $17, $08, $10; Wooden Ship Background Line
	.byte $60 | $16, $0B, $10; Wooden Ship Background Line
	.byte $60 | $15, $0E, $10; Wooden Ship Background Line
	.byte $00 | $16, $01, $E2; Thick Vertical Background Pillar
	.byte $00 | $15, $03, $E3; Thick Vertical Background Pillar
	.byte $00 | $17, $04, $E1; Thick Vertical Background Pillar
	.byte $00 | $17, $07, $E1; Thick Vertical Background Pillar
	.byte $20 | $0F, $07, $D1; Upward Pipe (CAN'T go up)
	.byte $FF
Coin_Ship_Boss_Room_W1_objects:
	.byte $82, $03, $17; Boomerang Brother
	.byte $82, $0C, $17; Boomerang Brother
	.byte $BA, $0F, $11; Exit on get treasure chest
	.byte $FF
; Level_1_Bonus_Area_W1
; Object Set 1
Level_1_Bonus_Area_W1_generators:
Level_1_Bonus_Area_W1_header:
	.byte $38; Next Level
	.byte LEVEL1_SIZE_02 | LEVEL1_YSTART_070; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $0F, $00, $BB, $07; Blue X-Blocks
	.byte $40 | $0F, $0A, $B0, $0B; Blue X-Blocks
	.byte $40 | $19, $08, $B1, $17; Blue X-Blocks
	.byte $20 | $0F, $08, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $11, $0E, $81; Coins
	.byte $20 | $12, $0D, $80; Coins
	.byte $20 | $12, $10, $80; Coins
	.byte $20 | $13, $10, $80; Coins
	.byte $20 | $14, $0E, $81; Coins
	.byte $20 | $16, $0D, $80; Coins
	.byte $20 | $16, $10, $80; Coins
	.byte $20 | $17, $0E, $81; Coins
	.byte $20 | $15, $10, $80; Coins
	.byte $40 | $0F, $18, $BB, $07; Blue X-Blocks
	.byte $40 | $13, $15, $B5, $02; Blue X-Blocks
	.byte $40 | $14, $14, $B4, $00; Blue X-Blocks
	.byte $40 | $15, $13, $B3, $00; Blue X-Blocks
	.byte $40 | $16, $12, $B2, $00; Blue X-Blocks
	.byte $40 | $17, $11, $B1, $00; Blue X-Blocks
	.byte $40 | $18, $10, $B0, $00; Blue X-Blocks
	.byte $20 | $0F, $16, $C1; Upward Pipe (CAN go up)
	; Pointer on screen $01
	.byte $E0 | $01, $70 | $01, 25; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_1_Bonus_Area_W1_objects:
	.byte $FF
; Level_2_Bonus_Area_W1
; Object Set 1
Level_2_Bonus_Area_W1_generators:
Level_2_Bonus_Area_W1_header:
	.byte $3A; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $B3, $0F; Blue X-Blocks
	.byte $40 | $04, $00, $B7, $03; Blue X-Blocks
	.byte $40 | $04, $0C, $B7, $03; Blue X-Blocks
	.byte $40 | $0C, $00, $BB, $00; Blue X-Blocks
	.byte $40 | $0C, $0F, $BD, $00; Blue X-Blocks
	.byte $40 | $1A, $00, $B0, $0F; Blue X-Blocks
	.byte $20 | $04, $07, $D1; Upward Pipe (CAN'T go up)
	.byte $40 | $18, $00, $11; Leftward Pipe (CAN go in)
	.byte $20 | $15, $06, $83; Coins
	.byte $20 | $16, $06, $83; Coins
	.byte $20 | $17, $06, $83; Coins
	.byte $20 | $18, $06, $83; Coins
	.byte $20 | $19, $06, $83; Coins
	; Pointer on screen $00
	.byte $E0 | $00, $50 | $01, 195; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_2_Bonus_Area_W1_objects:
	.byte $FF
; Default_Level_85
; Object Set 13
Default_Level_85_generators:
Default_Level_85_header:
	.byte $3B; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0D; Start action | Graphic set
	.byte $00 | $0A; Time | Music
	.byte $00 | $11, $09, $02; Cloud Background A
	.byte $00 | $14, $0A, $02; Cloud Background A
	.byte $00 | $03, $1D, $02; Cloud Background A
	.byte $60 | $0A, $21, $4F, $09; White Background
	.byte $20 | $15, $0C, $80; Coins
	.byte $20 | $15, $0E, $80; Coins
	.byte $20 | $16, $0B, $80; Coins
	.byte $20 | $16, $0D, $80; Coins
	.byte $20 | $16, $0F, $80; Coins
	.byte $00 | $06, $1A, $02; Cloud Background A
	.byte $00 | $08, $1C, $02; Cloud Background A
	.byte $00 | $0B, $1B, $02; Cloud Background A
	.byte $00 | $0F, $1B, $02; Cloud Background A
	.byte $00 | $11, $13, $02; Cloud Background A
	.byte $00 | $13, $11, $02; Cloud Background A
	.byte $00 | $13, $17, $02; Cloud Background A
	.byte $00 | $13, $1B, $02; Cloud Background A
	.byte $20 | $15, $10, $80; Coins
	.byte $20 | $15, $15, $80; Coins
	.byte $20 | $15, $17, $80; Coins
	.byte $20 | $15, $19, $80; Coins
	.byte $20 | $15, $1B, $80; Coins
	.byte $20 | $15, $1F, $80; Coins
	.byte $20 | $16, $11, $80; Coins
	.byte $20 | $16, $16, $80; Coins
	.byte $20 | $16, $18, $80; Coins
	.byte $20 | $16, $1A, $80; Coins
	.byte $20 | $16, $1E, $80; Coins
	.byte $00 | $06, $24, $02; Cloud Background A
	.byte $00 | $09, $25, $02; Cloud Background A
	.byte $00 | $0F, $27, $02; Cloud Background A
	.byte $00 | $0F, $2D, $02; Cloud Background A
	.byte $00 | $13, $23, $02; Cloud Background A
	.byte $00 | $13, $29, $02; Cloud Background A
	.byte $00 | $13, $2F, $02; Cloud Background A
	.byte $20 | $0B, $27, $0B; Brick with 1-up
	.byte $20 | $08, $26, $82; Coins
	.byte $20 | $09, $25, $81; Coins
	.byte $20 | $09, $28, $81; Coins
	.byte $20 | $0A, $24, $81; Coins
	.byte $20 | $0A, $29, $81; Coins
	.byte $20 | $0B, $24, $80; Coins
	.byte $20 | $0B, $2A, $80; Coins
	.byte $20 | $0C, $24, $81; Coins
	.byte $20 | $0C, $29, $81; Coins
	.byte $20 | $0D, $25, $81; Coins
	.byte $20 | $0D, $28, $81; Coins
	.byte $20 | $0E, $26, $82; Coins
	.byte $20 | $15, $21, $80; Coins
	.byte $20 | $15, $23, $80; Coins
	.byte $20 | $15, $27, $80; Coins
	.byte $20 | $15, $29, $80; Coins
	.byte $20 | $15, $2B, $80; Coins
	.byte $20 | $15, $2D, $80; Coins
	.byte $20 | $16, $20, $80; Coins
	.byte $20 | $16, $22, $80; Coins
	.byte $20 | $16, $24, $80; Coins
	.byte $20 | $16, $28, $80; Coins
	.byte $20 | $16, $2A, $80; Coins
	.byte $20 | $16, $2C, $80; Coins
	.byte $20 | $15, $31, $80; Coins
	.byte $20 | $15, $33, $80; Coins
	.byte $20 | $15, $35, $80; Coins
	.byte $20 | $16, $30, $80; Coins
	.byte $20 | $16, $32, $80; Coins
	.byte $20 | $16, $34, $80; Coins
	.byte $20 | $16, $36, $80; Coins
	.byte $60 | $19, $00, $21, $3F; Clouds B
	.byte $20 | $17, $35, $93; Downward Pipe (CAN go down)
	; Pointer on screen $03
	.byte $E0 | $03, $10 | $02, 56; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Default_Level_85_objects:
	.byte $D3, $00, $10; Autoscrolling
	.byte $FF
; Level_2_Ending_W6
; Object Set 12
Level_2_Ending_W6_generators:
Level_2_Ending_W6_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $00 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0C; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $40 | $1A, $00, $80, $07; Water (still)
	.byte $00 | $14, $03, $C2; Background Clouds
	.byte $20 | $00, $08, $D3; Upward Pipe (CAN'T go up)
	.byte $20 | $02, $08, $DE; Upward Pipe (CAN'T go up)
	.byte $00 | $1A, $08, $10, $30; Icy flat ground
	.byte $00 | $16, $0F, $73; Snowy Platform
	.byte $00 | $18, $0C, $73; Snowy Platform
	.byte $00 | $14, $10, $C2; Background Clouds
	.byte $40 | $00, $19, $09; Level Ending
	.byte $FF
Level_2_Ending_W6_objects:
	.byte $41, $28, $15; Goal Card
	.byte $FF
; Level_4_Ending_W1
; Object Set 1
Level_4_Ending_W1_generators:
Level_4_Ending_W1_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_02 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_08; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $19, $01, $91; Background Bushes
	.byte $00 | $17, $03, $01; Background Hills B
	.byte $00 | $1B, $00, $C1, $30; Flat Ground
	.byte $00 | $1A, $00, $C0, $1F; Flat Ground
	.byte $00 | $12, $03, $E2; Background Clouds
	.byte $20 | $18, $08, $A1; Downward Pipe (CAN'T go down)
	.byte $40 | $00, $0C, $09; Level Ending
	.byte $FF
Level_4_Ending_W1_objects:
	.byte $82, $02, $18; Boomerang Brother
	.byte $41, $18, $15; Goal Card
	.byte $FF
; Dungeon_Spike_Room_W1
; Object Set 2
Dungeon_Spike_Room_W1_generators:
Dungeon_Spike_Room_W1_header:
	.byte $3F; Next Level
	.byte LEVEL1_SIZE_06 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $0E, $00, $3C, $1F; Blank Background (used to block out stuff)
	.byte $00 | $00, $00, $EF, $1F; Horizontally oriented X-blocks
	.byte $00 | $19, $00, $E1, $1F; Horizontally oriented X-blocks
	.byte $00 | $10, $00, $DF; Ceiling Spikes
	.byte $60 | $0E, $09, $32, $02; Blank Background (used to block out stuff)
	.byte $60 | $19, $0D, $31, $02; Blank Background (used to block out stuff)
	.byte $00 | $10, $10, $DF; Ceiling Spikes
	.byte $00 | $17, $1D, $00; Door
	.byte $60 | $0F, $1D, $31, $00; Blank Background (used to block out stuff)
	.byte $60 | $19, $12, $31, $03; Blank Background (used to block out stuff)
	.byte $00 | $0F, $1D, $D0; Ceiling Spikes
	.byte $00 | $00, $1E, $EF, $11; Horizontally oriented X-blocks
	.byte $00 | $10, $1E, $EA, $11; Horizontally oriented X-blocks
	.byte $00 | $00, $30, $EF, $2F; Horizontally oriented X-blocks
	.byte $00 | $10, $30, $EA, $2F; Horizontally oriented X-blocks
	.byte $60 | $0F, $44, $39, $08; Blank Background (used to block out stuff)
	.byte $00 | $12, $46, $61; Dungeon windows
	.byte $00 | $0E, $09, $D2; Ceiling Spikes
	; Pointer on screen $01
	.byte $E0 | $01, $60 | $08, 183; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon_Spike_Room_W1_objects:
	.byte $D3, $01, $30; Autoscrolling
	.byte $D3, $1C, $30; Autoscrolling
	.byte $D6, $44, $0C; Puts item in treasure chest (Y pos. determines item; see docs/items.txt)
	.byte $BA, $45, $11; Exit on get treasure chest
	.byte $52, $4A, $18; Treasure Chest
	.byte $FF
; Level_5_Bonus_W1
; Object Set 13
Level_5_Bonus_W1_generators:
Level_5_Bonus_W1_header:
	.byte $41; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_14; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0D; Start action | Graphic set
	.byte $00 | $0A; Time | Music
	.byte $00 | $11, $09, $02; Cloud Background A
	.byte $00 | $14, $0A, $02; Cloud Background A
	.byte $00 | $03, $1D, $02; Cloud Background A
	.byte $60 | $0A, $21, $4F, $09; White Background
	.byte $20 | $15, $0C, $80; Coins
	.byte $20 | $15, $0E, $80; Coins
	.byte $20 | $16, $0B, $80; Coins
	.byte $20 | $16, $0D, $80; Coins
	.byte $20 | $16, $0F, $80; Coins
	.byte $00 | $06, $1A, $02; Cloud Background A
	.byte $00 | $08, $1C, $02; Cloud Background A
	.byte $00 | $0B, $1B, $02; Cloud Background A
	.byte $00 | $0F, $1B, $02; Cloud Background A
	.byte $00 | $11, $13, $02; Cloud Background A
	.byte $00 | $13, $11, $02; Cloud Background A
	.byte $00 | $13, $17, $02; Cloud Background A
	.byte $00 | $13, $1B, $02; Cloud Background A
	.byte $20 | $15, $10, $80; Coins
	.byte $20 | $15, $15, $80; Coins
	.byte $20 | $15, $17, $80; Coins
	.byte $20 | $15, $19, $80; Coins
	.byte $20 | $15, $1B, $80; Coins
	.byte $20 | $15, $1F, $80; Coins
	.byte $20 | $16, $11, $80; Coins
	.byte $20 | $16, $16, $80; Coins
	.byte $20 | $16, $18, $80; Coins
	.byte $20 | $16, $1A, $80; Coins
	.byte $20 | $16, $1E, $80; Coins
	.byte $00 | $06, $24, $02; Cloud Background A
	.byte $00 | $09, $25, $02; Cloud Background A
	.byte $00 | $0F, $27, $02; Cloud Background A
	.byte $00 | $0F, $2D, $02; Cloud Background A
	.byte $00 | $13, $23, $02; Cloud Background A
	.byte $00 | $13, $29, $02; Cloud Background A
	.byte $00 | $13, $2F, $02; Cloud Background A
	.byte $20 | $0B, $27, $0B; Brick with 1-up
	.byte $20 | $08, $26, $82; Coins
	.byte $20 | $09, $25, $81; Coins
	.byte $20 | $09, $28, $81; Coins
	.byte $20 | $0A, $24, $81; Coins
	.byte $20 | $0A, $29, $81; Coins
	.byte $20 | $0B, $24, $80; Coins
	.byte $20 | $0B, $2A, $80; Coins
	.byte $20 | $0C, $24, $81; Coins
	.byte $20 | $0C, $29, $81; Coins
	.byte $20 | $0D, $25, $81; Coins
	.byte $20 | $0D, $28, $81; Coins
	.byte $20 | $0E, $26, $82; Coins
	.byte $20 | $15, $21, $80; Coins
	.byte $20 | $15, $23, $80; Coins
	.byte $20 | $15, $27, $80; Coins
	.byte $20 | $15, $29, $80; Coins
	.byte $20 | $15, $2B, $80; Coins
	.byte $20 | $15, $2D, $80; Coins
	.byte $20 | $16, $20, $80; Coins
	.byte $20 | $16, $22, $80; Coins
	.byte $20 | $16, $24, $80; Coins
	.byte $20 | $16, $28, $80; Coins
	.byte $20 | $16, $2A, $80; Coins
	.byte $20 | $16, $2C, $80; Coins
	.byte $20 | $15, $31, $80; Coins
	.byte $20 | $15, $33, $80; Coins
	.byte $20 | $15, $35, $80; Coins
	.byte $20 | $16, $30, $80; Coins
	.byte $20 | $16, $32, $80; Coins
	.byte $20 | $16, $34, $80; Coins
	.byte $20 | $16, $36, $80; Coins
	.byte $60 | $19, $00, $21, $3F; Clouds B
	.byte $20 | $17, $35, $93; Downward Pipe (CAN go down)
	; Pointer on screen $03
	.byte $E0 | $03, $00 | $02, 197; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_5_Bonus_W1_objects:
	.byte $D3, $00, $10; Autoscrolling
	.byte $FF
; Level_2_Ending_W2
; Object Set 9
Level_2_Ending_W2_generators:
Level_2_Ending_W2_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_02 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_09; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $09; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $20 | $18, $03, $A1; Downward Pipe (CAN'T go down)
	.byte $40 | $00, $0A, $09; Level Ending
	.byte $FF
Level_2_Ending_W2_objects:
	.byte $41, $18, $15; Goal Card
	.byte $FF
; Level_3_Ending_W2
; Object Set 9
Level_3_Ending_W2_generators:
Level_3_Ending_W2_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_02 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_07; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_09; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $09; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $20 | $17, $02, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $16, $05, $04; Palm Tree
	.byte $60 | $19, $08, $20; Background Coconuts
	.byte $00 | $11, $07, $0A; Oval Background Cloud
	.byte $00 | $13, $04, $0A; Oval Background Cloud
	.byte $40 | $00, $0A, $09; Level Ending
	.byte $FF
Level_3_Ending_W2_objects:
	.byte $41, $18, $15; Goal Card
	.byte $FF
; Level_1_Bonus_Area_W2
; Object Set 9
Level_1_Bonus_Area_W2_generators:
Level_1_Bonus_Area_W2_header:
	.byte $46; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_03; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_09; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $09; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $20 | $0E, $00, $4F; Wooden blocks
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
	.byte $20 | $0F, $0F, $40; Wooden blocks
	.byte $20 | $10, $0F, $40; Wooden blocks
	.byte $20 | $11, $0F, $40; Wooden blocks
	.byte $20 | $12, $0F, $40; Wooden blocks
	.byte $20 | $13, $0F, $40; Wooden blocks
	.byte $20 | $14, $0F, $40; Wooden blocks
	.byte $20 | $15, $0F, $40; Wooden blocks
	.byte $20 | $16, $0F, $40; Wooden blocks
	.byte $20 | $17, $0F, $40; Wooden blocks
	.byte $20 | $18, $0F, $40; Wooden blocks
	.byte $20 | $19, $0F, $40; Wooden blocks
	.byte $20 | $1A, $00, $4F; Wooden blocks
	.byte $40 | $19, $07, $08; P-Switch
	.byte $40 | $15, $04, $57; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $16, $04, $57; Silver Coins (appear when you hit a P-Switch)
	.byte $20 | $0F, $02, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $18, $0B, $91; Downward Pipe (CAN go down)
	.byte $20 | $0E, $10, $4F; Wooden blocks
	.byte $20 | $0F, $10, $4F; Wooden blocks
	.byte $20 | $10, $10, $4F; Wooden blocks
	.byte $20 | $11, $10, $4F; Wooden blocks
	.byte $20 | $12, $10, $4F; Wooden blocks
	.byte $20 | $13, $10, $4F; Wooden blocks
	.byte $20 | $14, $10, $4F; Wooden blocks
	.byte $20 | $15, $10, $4F; Wooden blocks
	.byte $20 | $16, $10, $4F; Wooden blocks
	.byte $20 | $17, $10, $4F; Wooden blocks
	.byte $20 | $18, $10, $4F; Wooden blocks
	.byte $20 | $19, $10, $4F; Wooden blocks
	.byte $20 | $1A, $10, $4F; Wooden blocks
	.byte $20 | $0E, $20, $4F; Wooden blocks
	.byte $20 | $1A, $20, $4F; Wooden blocks
	.byte $20 | $0F, $20, $40; Wooden blocks
	.byte $20 | $10, $20, $40; Wooden blocks
	.byte $20 | $11, $20, $40; Wooden blocks
	.byte $20 | $12, $20, $40; Wooden blocks
	.byte $20 | $13, $20, $40; Wooden blocks
	.byte $20 | $14, $20, $40; Wooden blocks
	.byte $20 | $15, $20, $40; Wooden blocks
	.byte $20 | $16, $20, $40; Wooden blocks
	.byte $20 | $17, $20, $40; Wooden blocks
	.byte $20 | $18, $20, $40; Wooden blocks
	.byte $20 | $19, $20, $40; Wooden blocks
	.byte $20 | $0F, $2F, $40; Wooden blocks
	.byte $20 | $10, $2F, $40; Wooden blocks
	.byte $20 | $11, $2F, $40; Wooden blocks
	.byte $20 | $12, $2F, $40; Wooden blocks
	.byte $20 | $13, $2F, $40; Wooden blocks
	.byte $20 | $14, $2F, $40; Wooden blocks
	.byte $20 | $15, $2F, $40; Wooden blocks
	.byte $20 | $16, $2F, $40; Wooden blocks
	.byte $20 | $17, $2F, $40; Wooden blocks
	.byte $20 | $18, $2F, $40; Wooden blocks
	.byte $20 | $19, $2F, $40; Wooden blocks
	.byte $20 | $0F, $22, $C1; Upward Pipe (CAN go up)
	.byte $20 | $0F, $2C, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $14, $22, $41; Wooden blocks
	.byte $20 | $16, $24, $42; Wooden blocks
	.byte $20 | $18, $28, $42; Wooden blocks
	.byte $40 | $17, $29, $08; P-Switch
	.byte $20 | $0E, $30, $47; Wooden blocks
	.byte $20 | $0F, $30, $47; Wooden blocks
	.byte $20 | $10, $30, $47; Wooden blocks
	.byte $20 | $11, $30, $47; Wooden blocks
	.byte $20 | $12, $30, $47; Wooden blocks
	.byte $20 | $13, $30, $47; Wooden blocks
	.byte $20 | $14, $30, $47; Wooden blocks
	.byte $20 | $15, $30, $47; Wooden blocks
	.byte $20 | $16, $30, $47; Wooden blocks
	.byte $20 | $17, $30, $47; Wooden blocks
	.byte $20 | $18, $30, $47; Wooden blocks
	.byte $20 | $19, $30, $47; Wooden blocks
	.byte $20 | $1A, $30, $47; Wooden blocks
	; Pointer on screen $00
	.byte $E0 | $00, $10 | $02, 151; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $02
	.byte $E0 | $02, $60 | $01, 233; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_1_Bonus_Area_W2_objects:
	.byte $FF
; Dungeon_Spike_Room_W2
; Object Set 9
Dungeon_Spike_Room_W2_generators:
Dungeon_Spike_Room_W2_header:
	.byte $47; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_11 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_09; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $09; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $00 | $05, $00, $95; X-Large sandstone blocks
	.byte $00 | $19, $00, $8F; Large sandstone blocks
	.byte $20 | $15, $06, $41; Wooden blocks
	.byte $60 | $14, $06, $31; Floor Spikes
	.byte $60 | $16, $06, $41; Ceiling Spikes
	.byte $20 | $15, $0A, $44; Wooden blocks
	.byte $60 | $14, $0A, $34; Floor Spikes
	.byte $60 | $16, $0A, $44; Ceiling Spikes
	.byte $20 | $15, $11, $49; Wooden blocks
	.byte $60 | $14, $11, $39; Floor Spikes
	.byte $60 | $16, $11, $49; Ceiling Spikes
	.byte $20 | $13, $11, $40; Wooden blocks
	.byte $20 | $14, $11, $40; Wooden blocks
	.byte $20 | $13, $16, $40; Wooden blocks
	.byte $20 | $14, $16, $40; Wooden blocks
	.byte $20 | $13, $1A, $40; Wooden blocks
	.byte $20 | $14, $1A, $40; Wooden blocks
	.byte $20 | $15, $1E, $46; Wooden blocks
	.byte $60 | $14, $1E, $36; Floor Spikes
	.byte $60 | $16, $1E, $46; Ceiling Spikes
	.byte $20 | $15, $2A, $43; Wooden blocks
	.byte $60 | $14, $2A, $33; Floor Spikes
	.byte $60 | $16, $2A, $43; Ceiling Spikes
	.byte $00 | $09, $2F, $90; X-Large sandstone blocks
	.byte $00 | $0D, $2F, $90; X-Large sandstone blocks
	.byte $00 | $11, $2F, $90; X-Large sandstone blocks
	.byte $00 | $15, $2F, $90; X-Large sandstone blocks
	.byte $00 | $17, $26, $0B; Door
	.byte $20 | $13, $1E, $40; Wooden blocks
	.byte $20 | $14, $1E, $40; Wooden blocks
	.byte $20 | $13, $21, $40; Wooden blocks
	.byte $20 | $14, $21, $40; Wooden blocks
	.byte $20 | $13, $24, $40; Wooden blocks
	.byte $20 | $14, $24, $40; Wooden blocks
	.byte $60 | $09, $00, $4F; Ceiling Spikes
	.byte $60 | $09, $10, $4F; Ceiling Spikes
	.byte $60 | $09, $20, $4E; Ceiling Spikes
	; Pointer on screen $02
	.byte $E0 | $02, $70 | $08, 201; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon_Spike_Room_W2_objects:
	.byte $D3, $04, $31; Autoscrolling
	.byte $2F, $0C, $11; Boo Buddy
	.byte $2F, $1E, $11; Boo Buddy
	.byte $FF
; Level_5_Bonus_Area_W2
; Object Set 9
Level_5_Bonus_Area_W2_generators:
Level_5_Bonus_Area_W2_header:
	.byte $4F; Next Level
	.byte LEVEL1_SIZE_01 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_03; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_09; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $09; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $0F, $00, $B0, $0F; Blue X-Blocks
	.byte $40 | $0F, $00, $BB, $00; Blue X-Blocks
	.byte $40 | $1A, $00, $B0, $0F; Blue X-Blocks
	.byte $40 | $0F, $0F, $BB, $00; Blue X-Blocks
	.byte $20 | $11, $03, $10; Bricks
	.byte $20 | $11, $05, $10; Bricks
	.byte $20 | $11, $07, $10; Bricks
	.byte $20 | $11, $09, $10; Bricks
	.byte $20 | $11, $0B, $10; Bricks
	.byte $20 | $12, $04, $10; Bricks
	.byte $20 | $12, $06, $10; Bricks
	.byte $20 | $12, $08, $10; Bricks
	.byte $20 | $12, $0A, $10; Bricks
	.byte $20 | $13, $03, $10; Bricks
	.byte $20 | $13, $05, $10; Bricks
	.byte $20 | $13, $09, $10; Bricks
	.byte $20 | $13, $0B, $10; Bricks
	.byte $20 | $14, $04, $10; Bricks
	.byte $20 | $14, $06, $10; Bricks
	.byte $20 | $14, $08, $10; Bricks
	.byte $20 | $14, $0A, $10; Bricks
	.byte $20 | $15, $03, $10; Bricks
	.byte $20 | $15, $05, $10; Bricks
	.byte $20 | $15, $07, $0D; Brick with P-Switch
	.byte $20 | $15, $09, $10; Bricks
	.byte $20 | $15, $0B, $07; Brick with Leaf
	.byte $20 | $18, $07, $10; Bricks
	.byte $20 | $17, $03, $83; Coins
	.byte $20 | $17, $08, $83; Coins
	.byte $20 | $0F, $01, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $18, $0C, $92; Downward Pipe (CAN go down)
	; Pointer on screen $00
	.byte $E0 | $00, $10 | $02, 230; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_5_Bonus_Area_W2_objects:
	.byte $FF
; Pyramid_W2
; Object Set 3
Pyramid_W2_generators:
Pyramid_W2_header:
	.byte $50; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_09; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $00, $00, $BC, $1B; Ceiling
	.byte $80 | $0C, $00, $BA, $07; Ceiling
	.byte $60 | $0D, $07, $E8; Hilly Wall - Right Side
	.byte $00 | $16, $07, $0A; Lower Right Hill Corner
	.byte $80 | $19, $00, $81, $09; Flat Land - Hilly
	.byte $80 | $19, $0A, $51, $06; Hilly Wall
	.byte $60 | $13, $09, $0A; Steps A
	.byte $00 | $17, $02, $0F; Door
	.byte $60 | $09, $1C, $04; Horizontal Hill Strip
	.byte $60 | $10, $1A, $08; Triangular Hill Object A
	.byte $60 | $0E, $1C, $04; Horizontal Hill Strip
	.byte $60 | $07, $2A, $09; Triangular Hill Object B
	.byte $60 | $09, $2C, $04; Horizontal Hill Strip
	.byte $60 | $09, $34, $04; Horizontal Hill Strip
	.byte $60 | $0E, $2B, $0C; Square Hill Object
	.byte $60 | $0E, $31, $0C; Square Hill Object
	.byte $60 | $15, $24, $08; Triangular Hill Object A
	.byte $60 | $13, $26, $04; Horizontal Hill Strip
	.byte $60 | $13, $2E, $04; Horizontal Hill Strip
	.byte $80 | $00, $1C, $B7, $19; Ceiling
	.byte $60 | $08, $1B, $E2; Hilly Wall - Right Side
	.byte $80 | $13, $11, $87, $04; Flat Land - Hilly
	.byte $80 | $1A, $16, $50, $0D; Hilly Wall
	.byte $60 | $13, $16, $56; 30 Degree Hill - Down/Right
	.byte $20 | $10, $10, $10; Bricks
	.byte $20 | $11, $10, $10; Bricks
	.byte $20 | $12, $10, $10; Bricks
	.byte $20 | $10, $11, $01; '?' with leaf
	.byte $20 | $11, $14, $10; Bricks
	.byte $20 | $12, $14, $10; Bricks
	.byte $80 | $0B, $24, $81, $00; Flat Land - Hilly
	.byte $80 | $0D, $24, $B4, $02; Ceiling
	.byte $00 | $0B, $25, $51; 45 Degree Hill - Down/Right
	.byte $00 | $0D, $24, $E2; Hilly Wall - Left Side
	.byte $60 | $0D, $26, $E2; Hilly Wall - Right Side
	.byte $80 | $10, $27, $80, $07; Flat Land - Hilly
	.byte $80 | $11, $27, $B0, $07; Ceiling
	.byte $80 | $1A, $24, $80, $11; Flat Land - Hilly
	.byte $20 | $12, $2A, $10; Bricks
	.byte $20 | $13, $2A, $10; Bricks
	.byte $20 | $14, $2A, $10; Bricks
	.byte $20 | $17, $2C, $10; Bricks
	.byte $20 | $18, $2C, $10; Bricks
	.byte $20 | $19, $2C, $10; Bricks
	.byte $80 | $00, $38, $B0, $0B; Ceiling
	.byte $60 | $00, $35, $E6; Hilly Wall - Right Side
	.byte $00 | $07, $35, $0A; Lower Right Hill Corner
	.byte $00 | $00, $38, $07; Lower Left Hill Corner
	.byte $80 | $0B, $3C, $80, $04; Flat Land - Hilly
	.byte $80 | $0C, $3C, $B0, $04; Ceiling
	.byte $80 | $10, $35, $80, $07; Flat Land - Hilly
	.byte $80 | $11, $35, $B0, $07; Ceiling
	.byte $80 | $10, $3D, $8A, $03; Flat Land - Hilly
	.byte $00 | $12, $3D, $E2; Hilly Wall - Left Side
	.byte $80 | $15, $36, $85, $06; Flat Land - Hilly
	.byte $00 | $17, $36, $E2; Hilly Wall - Left Side
	.byte $20 | $04, $39, $40; Wooden blocks
	.byte $20 | $05, $39, $40; Wooden blocks
	.byte $20 | $06, $39, $40; Wooden blocks
	.byte $20 | $07, $39, $40; Wooden blocks
	.byte $20 | $08, $35, $44; Wooden blocks
	.byte $20 | $07, $3C, $0E; Invisible Coin
	.byte $80 | $15, $31, $50, $01; Hilly Wall
	.byte $20 | $0D, $38, $10; Bricks
	.byte $20 | $0E, $38, $10; Bricks
	.byte $20 | $0F, $38, $10; Bricks
	.byte $20 | $12, $35, $10; Bricks
	.byte $20 | $13, $35, $10; Bricks
	.byte $20 | $14, $35, $10; Bricks
	.byte $20 | $08, $34, $10; Bricks
	.byte $20 | $09, $34, $10; Bricks
	.byte $20 | $0A, $34, $10; Bricks
	.byte $20 | $13, $31, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $00, $36, $C5; Upward Pipe (CAN go up)
	.byte $80 | $00, $44, $55, $05; Hilly Wall
	.byte $00 | $06, $44, $75; 45 Degree Hill - Up/Left
	.byte $80 | $00, $4A, $BB, $33; Ceiling
	.byte $00 | $01, $44, $E4; Hilly Wall - Left Side
	.byte $80 | $0B, $41, $8F, $00; Flat Land - Hilly
	.byte $00 | $0D, $41, $E2; Hilly Wall - Left Side
	.byte $80 | $17, $44, $53, $09; Hilly Wall
	.byte $00 | $0B, $42, $5E; 45 Degree Hill - Down/Right
	.byte $80 | $1A, $4D, $50, $02; Hilly Wall
	.byte $60 | $1A, $50, $E0; Hilly Wall - Right Side
	.byte $80 | $10, $5D, $8A, $0E; Flat Land - Hilly
	.byte $80 | $11, $59, $89, $03; Flat Land - Hilly
	.byte $00 | $10, $5D, $01; Upper Left Hill Corner - Hilly
	.byte $80 | $16, $54, $54, $04; Hilly Wall
	.byte $00 | $11, $58, $64; 45 Degree Hill - Down/Left
	.byte $00 | $16, $54, $E4; Hilly Wall - Left Side
	.byte $20 | $18, $52, $A2; Downward Pipe (CAN'T go down)
	.byte $80 | $11, $6A, $59, $02; Hilly Wall
	.byte $00 | $10, $6C, $50; 45 Degree Hill - Down/Right
	.byte $80 | $11, $6D, $89, $06; Flat Land - Hilly
	.byte $20 | $0C, $6F, $10; Bricks
	.byte $20 | $0D, $6F, $10; Bricks
	.byte $20 | $0E, $6F, $10; Bricks
	.byte $20 | $0F, $6F, $10; Bricks
	.byte $20 | $10, $6F, $10; Bricks
	.byte $60 | $00, $7C, $EA; Hilly Wall - Right Side
	.byte $80 | $11, $72, $50, $01; Hilly Wall
	.byte $00 | $0B, $7C, $0A; Lower Right Hill Corner
	.byte $80 | $00, $7F, $5F, $00; Hilly Wall
	.byte $00 | $00, $7F, $EE; Hilly Wall - Left Side
	.byte $80 | $10, $7F, $5A, $00; Hilly Wall
	.byte $80 | $0F, $74, $8B, $0A; Flat Land - Hilly
	.byte $00 | $0F, $74, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $10, $74, $E0; Hilly Wall - Left Side
	.byte $20 | $0F, $72, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $00, $7D, $CC; Upward Pipe (CAN go up)
	; Pointer on screen $00
	.byte $E0 | $00, $50 | $08, 224; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $03
	.byte $E0 | $03, $70 | $01, 131; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $07
	.byte $E0 | $07, $70 | $01, 54; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Pyramid_W2_objects:
	.byte $70, $10, $0F; Buzzy Beetle
	.byte $70, $13, $12; Buzzy Beetle
	.byte $70, $23, $0F; Buzzy Beetle
	.byte $70, $25, $19; Buzzy Beetle
	.byte $A2, $31, $13; Red Piranha Plant (upward)
	.byte $70, $32, $0A; Buzzy Beetle
	.byte $70, $34, $19; Buzzy Beetle
	.byte $70, $3B, $14; Buzzy Beetle
	.byte $70, $40, $0F; Buzzy Beetle
	.byte $70, $4B, $13; Buzzy Beetle
	.byte $70, $4E, $16; Buzzy Beetle
	.byte $68, $63, $0C; Upside-down Buzzy Beetle
	.byte $70, $67, $0F; Buzzy Beetle
	.byte $68, $6E, $0C; Upside-down Buzzy Beetle
	.byte $A0, $72, $0F; Green Piranha Plant (upward)
	.byte $FF
; Level_3_Ending_W3
; Object Set 1
Level_3_Ending_W3_generators:
Level_3_Ending_W3_header:
	.byte $53; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_0F0; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $00 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $40 | $19, $00, $81, $0F; Water (still)
	.byte $40 | $19, $08, $B1, $03; Blue X-Blocks
	.byte $20 | $17, $09, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $13, $03, $E2; Background Clouds
	.byte $00 | $15, $0D, $E2; Background Clouds
	.byte $00 | $1A, $10, $C0, $1F; Flat Ground
	.byte $00 | $19, $11, $94; Background Bushes
	.byte $20 | $19, $10, $40; Wooden Blocks
	.byte $40 | $00, $18, $09; Level Ending
	.byte $FF
Level_3_Ending_W3_objects:
	.byte $41, $28, $15; Goal Card
	.byte $FF
; Level_2_Ending_W3
; Object Set 4
Level_2_Ending_W3_generators:
Level_2_Ending_W3_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $00 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $04; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $17, $07, $02; Blue Background Pole A
	.byte $00 | $18, $07, $10, $06; Wooden platform
	.byte $20 | $11, $09, $41; Wooden blocks
	.byte $20 | $12, $09, $D3; Upward Pipe (CAN'T go up)
	.byte $00 | $17, $0D, $10, $06; Wooden platform
	.byte $00 | $16, $0F, $42; Background Bushes
	.byte $00 | $16, $13, $03; Blue Background Pole B
	.byte $00 | $18, $13, $10, $03; Wooden platform
	.byte $00 | $17, $16, $03; Blue Background Pole B
	.byte $40 | $00, $17, $09; Level Ending
	.byte $00 | $1A, $17, $10, $30; Wooden platform
	.byte $20 | $0A, $0B, $84; Coins
	.byte $20 | $06, $0B, $80; Coins
	.byte $20 | $06, $0F, $80; Coins
	.byte $20 | $01, $09, $0F; Invisible 1-up
	.byte $00 | $03, $0A, $B0; 45 Degree Platform Wire - Up/Right
	.byte $00 | $02, $0B, $80; Horizontal platform wire
	.byte $00 | $03, $0C, $A0; 45 Degree Platform Wire - Down/Right
	.byte $00 | $03, $0D, $80; Horizontal platform wire
	.byte $00 | $03, $0E, $B0; 45 Degree Platform Wire - Up/Right
	.byte $00 | $02, $0F, $80; Horizontal platform wire
	.byte $00 | $04, $0B, $80; Horizontal platform wire
	.byte $00 | $04, $0A, $A0; 45 Degree Platform Wire - Down/Right
	.byte $00 | $05, $0C, $A0; 45 Degree Platform Wire - Down/Right
	.byte $00 | $06, $0C, $92; 1 platform wire
	.byte $00 | $08, $0D, $B0; 45 Degree Platform Wire - Up/Right
	.byte $00 | $06, $0D, $91; 1 platform wire
	.byte $00 | $05, $0E, $B0; 45 Degree Platform Wire - Up/Right
	.byte $00 | $04, $0F, $80; Horizontal platform wire
	.byte $00 | $03, $10, $A0; 45 Degree Platform Wire - Down/Right
	.byte $00 | $04, $10, $B0; 45 Degree Platform Wire - Up/Right
	.byte $40 | $1A, $00, $80, $16; Water (still)
	.byte $FF
Level_2_Ending_W3_objects:
	.byte $3C, $0B, $08; Wired platform (follows platform wires)
	.byte $64, $12, $1A; Surface Cheep-Cheep (jumps out of water)
	.byte $41, $28, $15; Goal Card
	.byte $FF
; Dungeon__1_Water_Room_W3
; Object Set 2
Dungeon__1_Water_Room_W3_generators:
Dungeon__1_Water_Room_W3_header:
	.byte $57; Next Level
	.byte LEVEL1_SIZE_08 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_03; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $00 | $10, $10, $48; Dungeon background
	.byte $00 | $0D, $19, $44; Dungeon background
	.byte $00 | $08, $1C, $45; Dungeon background
	.byte $00 | $12, $1E, $45; Dungeon background
	.byte $00 | $0D, $22, $4D; Dungeon background
	.byte $00 | $0D, $30, $4F; Dungeon background
	.byte $00 | $0D, $40, $4F; Dungeon background
	.byte $00 | $0D, $50, $45; Dungeon background
	.byte $00 | $12, $51, $42; Dungeon background
	.byte $00 | $00, $00, $FD, $18; Vertically oriented X-blocks
	.byte $00 | $00, $0E, $EC, $01; Horizontally oriented X-blocks
	.byte $00 | $15, $0E, $E3, $01; Horizontally oriented X-blocks
	.byte $20 | $0D, $0E, $C4; Upward Pipe (CAN go up)
	.byte $00 | $00, $10, $EF, $08; Horizontally oriented X-blocks
	.byte $00 | $00, $19, $EC, $02; Horizontally oriented X-blocks
	.byte $00 | $00, $1C, $E7, $05; Horizontally oriented X-blocks
	.byte $00 | $0C, $1C, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $0D, $1E, $E1, $00; Horizontally oriented X-blocks
	.byte $00 | $0F, $1E, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $10, $1E, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $11, $1E, $E0, $05; Horizontally oriented X-blocks
	.byte $00 | $0A, $1D, $00; Door
	.byte $00 | $0F, $1B, $00; Door
	.byte $20 | $12, $12, $01; '?' with leaf
	.byte $40 | $15, $10, $83, $49; Water (still)
	.byte $00 | $00, $22, $EC, $33; Horizontally oriented X-blocks
	.byte $00 | $0F, $22, $00; Door
	.byte $00 | $0F, $29, $00; Door
	.byte $00 | $0F, $30, $00; Door
	.byte $00 | $0F, $37, $00; Door
	.byte $00 | $0F, $3E, $00; Door
	.byte $20 | $0D, $33, $C6; Upward Pipe (CAN go up)
	.byte $20 | $13, $3A, $01; '?' with leaf
	.byte $00 | $0F, $45, $00; Door
	.byte $00 | $0F, $4C, $00; Door
	.byte $20 | $0D, $41, $C6; Upward Pipe (CAN go up)
	.byte $00 | $00, $56, $FF, $18; Vertically oriented X-blocks
	.byte $00 | $11, $51, $E0, $02; Horizontally oriented X-blocks
	.byte $00 | $0F, $53, $00; Door
	.byte $20 | $0E, $51, $0B; Brick with 1-up
	.byte $60 | $10, $66, $38, $0D; Blank Background (used to block out stuff)
	.byte $00 | $00, $66, $EF, $19; Horizontally oriented X-blocks
	.byte $00 | $17, $67, $00; Door
	.byte $20 | $12, $6A, $86; Coins
	.byte $20 | $14, $6A, $86; Coins
	.byte $00 | $12, $69, $E4, $00; Horizontally oriented X-blocks
	.byte $00 | $16, $69, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $16, $6C, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $16, $6F, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $12, $71, $E4, $00; Horizontally oriented X-blocks
	.byte $20 | $12, $68, $0E; Invisible Coin
	.byte $20 | $15, $67, $0E; Invisible Coin
	.byte $20 | $16, $6B, $0E; Invisible Coin
	.byte $20 | $16, $6E, $0E; Invisible Coin
	.byte $20 | $16, $70, $0E; Invisible Coin
	.byte $00 | $10, $74, $E8, $0B; Horizontally oriented X-blocks
	; Pointer on screen $00
	.byte $E0 | $00, $60 | $01, 50; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $01
	.byte $E0 | $01, $60 | $08, 41; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $02
	.byte $E0 | $02, $60 | $08, 22; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $03
	.byte $E0 | $03, $60 | $01, 50; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $04
	.byte $E0 | $04, $60 | $01, 50; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $05
	.byte $E0 | $05, $60 | $08, 133; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $06
	.byte $E0 | $06, $60 | $08, 24; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__1_Water_Room_W3_objects:
	.byte $77, $21, $17; Cheep-Cheep
	.byte $77, $3A, $17; Cheep-Cheep
	.byte $77, $4C, $17; Cheep-Cheep
	.byte $FF
; Level_2_Ending_W7
; Object Set 1
Level_2_Ending_W7_generators:
Level_2_Ending_W7_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_02 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $1A, $00, $C0, $1F; Flat Ground
	.byte $20 | $19, $00, $45; Wooden Blocks
	.byte $40 | $17, $00, $22; Leftward Pipe (CAN'T go in)
	.byte $40 | $00, $08, $09; Level Ending
	.byte $FF
Level_2_Ending_W7_objects:
	.byte $41, $18, $15; Goal Card
	.byte $FF
; Level_5_Ending_W3
; Object Set 1
Level_5_Ending_W3_generators:
Level_5_Ending_W3_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $20 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $40 | $18, $00, $82, $0F; Water (still)
	.byte $40 | $00, $00, $BF, $01; Blue X-Blocks
	.byte $40 | $10, $00, $BA, $01; Blue X-Blocks
	.byte $40 | $1A, $00, $B0, $05; Blue X-Blocks
	.byte $40 | $14, $00, $21; Leftward Pipe (CAN'T go in)
	.byte $00 | $12, $05, $E2; Background Clouds
	.byte $00 | $13, $0B, $E2; Background Clouds
	.byte $00 | $1A, $10, $C0, $20; Flat Ground
	.byte $00 | $17, $11, $01; Background Hills B
	.byte $00 | $19, $16, $91; Background Bushes
	.byte $20 | $18, $10, $40; Wooden Blocks
	.byte $20 | $19, $10, $40; Wooden Blocks
	.byte $40 | $00, $19, $09; Level Ending
	.byte $FF
Level_5_Ending_W3_objects:
	.byte $3E, $08, $17; Floating platform (floats in water)
	.byte $41, $28, $15; Goal Card
	.byte $FF
; Level_6_Ending_W3
; Object Set 4
Level_6_Ending_W3_generators:
Level_6_Ending_W3_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_140; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_01; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $04; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $20 | $0F, $09, $D1; Upward Pipe (CAN'T go up)
	.byte $00 | $17, $07, $10, $04; Wooden platform
	.byte $00 | $16, $08, $42; Background Bushes
	.byte $00 | $18, $08, $04; Wooden Background Pole
	.byte $00 | $18, $0A, $04; Wooden Background Pole
	.byte $00 | $18, $0E, $10, $05; Wooden platform
	.byte $00 | $17, $0F, $43; Background Bushes
	.byte $00 | $19, $0F, $04; Wooden Background Pole
	.byte $00 | $19, $12, $04; Wooden Background Pole
	.byte $00 | $1A, $16, $10, $20; Wooden platform
	.byte $40 | $00, $19, $09; Level Ending
	.byte $FF
Level_6_Ending_W3_objects:
	.byte $80, $10, $16; Green Koopa Paratroopa (doesn't bounce)
	.byte $41, $28, $15; Goal Card
	.byte $FF
; Level_7_Bonus_Area_W3
; Object Set 13
Level_7_Bonus_Area_W3_generators:
Level_7_Bonus_Area_W3_header:
	.byte $5F; Next Level
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
	.byte $00 | $17, $2A, $F4; World 6-style Cloud Platform
	.byte $FF
Level_7_Bonus_Area_W3_objects:
	.byte $D3, $00, $12; Autoscrolling
	.byte $D6, $2B, $07; Puts item in treasure chest (Y pos. determines item; see docs/items.txt)
	.byte $52, $2C, $16; Treasure Chest
	.byte $BA, $2D, $16; Exit on get treasure chest
	.byte $FF
; Level_8_Ending_W3
; Object Set 1
Level_8_Ending_W3_generators:
Level_8_Ending_W3_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $40 | $19, $00, $81, $15; Water (still)
	.byte $40 | $00, $00, $BF, $01; Blue X-Blocks
	.byte $40 | $10, $00, $BA, $01; Blue X-Blocks
	.byte $40 | $14, $02, $21; Leftward Pipe (CAN'T go in)
	.byte $40 | $16, $02, $4F; Bridge
	.byte $40 | $16, $12, $43; Bridge
	.byte $00 | $10, $07, $E2; Background Clouds
	.byte $00 | $11, $0D, $E2; Background Clouds
	.byte $00 | $1A, $16, $C0, $19; Flat Ground
	.byte $20 | $17, $16, $40; Wooden Blocks
	.byte $20 | $18, $16, $40; Wooden Blocks
	.byte $20 | $19, $16, $40; Wooden Blocks
	.byte $40 | $00, $18, $09; Level Ending
	.byte $FF
Level_8_Ending_W3_objects:
	.byte $41, $28, $15; Goal Card
	.byte $FF
; Dungeon__2_Water_Room_W3
; Object Set 2
Dungeon__2_Water_Room_W3_generators:
Dungeon__2_Water_Room_W3_header:
	.byte $61; Next Level
	.byte LEVEL1_SIZE_06 | LEVEL1_YSTART_0F0; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_03; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $00 | $19, $00, $E1, $5F; Horizontally oriented X-blocks
	.byte $40 | $0F, $00, $89, $0F; Water (still)
	.byte $00 | $0F, $00, $E1, $0F; Horizontally oriented X-blocks
	.byte $00 | $11, $00, $E2, $04; Horizontally oriented X-blocks
	.byte $00 | $13, $07, $E5, $02; Horizontally oriented X-blocks
	.byte $20 | $14, $01, $D1; Upward Pipe (CAN'T go up)
	.byte $00 | $16, $0A, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $17, $0A, $E0, $01; Horizontally oriented X-blocks
	.byte $00 | $18, $0A, $E0, $02; Horizontally oriented X-blocks
	.byte $40 | $0F, $10, $89, $0F; Water (still)
	.byte $00 | $0F, $10, $E1, $0F; Horizontally oriented X-blocks
	.byte $00 | $14, $11, $02; Rotodisc block
	.byte $20 | $15, $1C, $00; '?' with flower
	.byte $40 | $0F, $20, $89, $0F; Water (still)
	.byte $00 | $0F, $20, $E1, $0F; Horizontally oriented X-blocks
	.byte $00 | $14, $25, $02; Rotodisc block
	.byte $20 | $14, $2E, $92; Downward Pipe (CAN go down)
	.byte $00 | $17, $28, $E0, $07; Horizontally oriented X-blocks
	.byte $00 | $18, $27, $E0, $08; Horizontally oriented X-blocks
	.byte $00 | $0F, $30, $E9, $0F; Horizontally oriented X-blocks
	.byte $60 | $0F, $40, $3A, $1F; Blank Background (used to block out stuff)
	.byte $00 | $0F, $40, $E0, $1F; Horizontally oriented X-blocks
	.byte $00 | $0F, $44, $E5, $0C; Horizontally oriented X-blocks
	.byte $00 | $16, $45, $62; Dungeon windows
	.byte $20 | $0F, $41, $D1; Upward Pipe (CAN'T go up)
	.byte $00 | $0F, $5F, $EB, $00; Horizontally oriented X-blocks
	.byte $00 | $14, $54, $E0, $00; Horizontally oriented X-blocks
	.byte $00 | $15, $5B, $E0, $00; Horizontally oriented X-blocks
	; Pointer on screen $02
	.byte $E0 | $02, $50 | $01, 2; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__2_Water_Room_W3_objects:
	.byte $5A, $11, $14; Single Rotodisc (rotates clockwise)
	.byte $77, $17, $13; Cheep-Cheep
	.byte $77, $1F, $17; Cheep-Cheep
	.byte $5A, $25, $14; Single Rotodisc (rotates clockwise)
	.byte $77, $29, $13; Cheep-Cheep
	.byte $4C, $5C, $28; Flying Boom Boom
	.byte $FF
; Level_9_Ending_W3
; Object Set 1
Level_9_Ending_W3_generators:
Level_9_Ending_W3_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_02 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $00 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $00 | $1A, $00, $C0, $20; Flat Ground
	.byte $00 | $13, $01, $E2; Background Clouds
	.byte $00 | $12, $07, $E3; Background Clouds
	.byte $00 | $19, $00, $96; Background Bushes
	.byte $20 | $17, $03, $A2; Downward Pipe (CAN'T go down)
	.byte $00 | $17, $07, $01; Background Hills B
	.byte $40 | $00, $0C, $09; Level Ending
	.byte $FF
Level_9_Ending_W3_objects:
	.byte $41, $18, $15; Goal Card
	.byte $FF
; Level_6_Small_Side_W4
; Object Set 1
Level_6_Small_Side_W4_generators:
Level_6_Small_Side_W4_header:
	.byte $6A; Next Level
	.byte LEVEL1_SIZE_11 | LEVEL1_YSTART_180; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_03; Next Level High | X Start | Sprite Palette | Block Palette
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
	.byte $20 | $16, $15, $08; Brick with Star
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
	.byte $20 | $16, $39, $20; '?' Blocks with single coins
	.byte $20 | $08, $34, $0B; Brick with 1-up
	.byte $00 | $1A, $33, $A2; Gap
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
	.byte $00 | $16, $50, $00; Background Hills A
	.byte $00 | $19, $58, $91; Background Bushes
	.byte $00 | $19, $5C, $90; Background Bushes
	.byte $00 | $11, $53, $E3; Background Clouds
	.byte $00 | $14, $59, $E2; Background Clouds
	.byte $20 | $16, $5C, $0E; Invisible Coin
	.byte $20 | $16, $5D, $0E; Invisible Coin
	.byte $20 | $17, $56, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $5E, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $16, $5B, $0F; Invisible 1-up
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
Level_6_Small_Side_W4_objects:
	.byte $6E, $11, $16; Green Koopa Paratroopa (bounces)
	.byte $6C, $19, $19; Green Koopa Troopa
	.byte $6C, $18, $15; Green Koopa Troopa
	.byte $A0, $26, $16; Green Piranha Plant (upward)
	.byte $6C, $2E, $14; Green Koopa Troopa
	.byte $72, $32, $19; Goomba
	.byte $72, $33, $19; Goomba
	.byte $6E, $42, $19; Green Koopa Paratroopa (bounces)
	.byte $6C, $4C, $19; Green Koopa Troopa
	.byte $72, $4B, $15; Goomba
	.byte $A0, $56, $17; Green Piranha Plant (upward)
	.byte $A0, $5E, $16; Green Piranha Plant (upward)
	.byte $72, $54, $19; Goomba
	.byte $6C, $5D, $19; Green Koopa Troopa
	.byte $6D, $6D, $15; Red Koopa Troopa
	.byte $6D, $6A, $19; Red Koopa Troopa
	.byte $6E, $78, $16; Green Koopa Paratroopa (bounces)
	.byte $A0, $78, $17; Green Piranha Plant (upward)
	.byte $6C, $82, $13; Green Koopa Troopa
	.byte $6D, $81, $16; Red Koopa Troopa
	.byte $6E, $8D, $13; Green Koopa Paratroopa (bounces)
	.byte $6E, $9E, $19; Green Koopa Paratroopa (bounces)
	.byte $41, $A8, $15; Goal Card
	.byte $FF
; Dungeon__2_Pipe_Room_W4
; Object Set 8
Dungeon__2_Pipe_Room_W4_generators:
Dungeon__2_Pipe_Room_W4_header:
	.byte $6C; Next Level
	.byte LEVEL1_SIZE_05 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_VERTICAL | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $08; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $00 | $00, $00, $0C; Background for pipe levels
	.byte $20 | $00, $00, $4F; Wooden blocks
	.byte $20 | $05, $04, $91; Downward Pipe (CAN go down)
	.byte $20 | $07, $00, $47; Wooden blocks
	.byte $20 | $08, $00, $47; Wooden blocks
	.byte $20 | $09, $00, $47; Wooden blocks
	.byte $20 | $07, $0B, $44; Wooden blocks
	.byte $20 | $08, $0B, $44; Wooden blocks
	.byte $20 | $09, $0B, $44; Wooden blocks
	.byte $40 | $0D, $00, $24; Leftward Pipe (CAN'T go in)
	.byte $20 | $0D, $08, $F7; Rightward Pipe (CAN'T go in)
	.byte $00 | $04, $1C, $07; Multi-directional directional platform
	.byte $40 | $06, $10, $29; Leftward Pipe (CAN'T go in)
	.byte $20 | $06, $1C, $F3; Rightward Pipe (CAN'T go in)
	.byte $00 | $00, $21, $12; Double-ended pipe
	.byte $00 | $0E, $12, $26; Rightward pipe
	.byte $00 | $09, $21, $2C; Rightward pipe
	.byte $00 | $04, $15, $1F; Double-ended pipe
	.byte $00 | $00, $28, $1C; Double-ended pipe
	.byte $00 | $0C, $1E, $1C; Double-ended pipe
	.byte $00 | $06, $21, $13; Double-ended pipe
	.byte $00 | $05, $2B, $18; Double-ended pipe
	.byte $20 | $01, $2C, $00; '?' with Flower
	.byte $20 | $02, $36, $F9; Rightward Pipe (CAN'T go in)
	.byte $40 | $02, $30, $21; Leftward Pipe (CAN'T go in)
	.byte $20 | $01, $39, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $05, $39, $41; Wooden blocks
	.byte $00 | $06, $33, $04; Upward directional platform
	.byte $20 | $09, $33, $45; Wooden blocks
	.byte $20 | $0A, $39, $A1; Downward Pipe (CAN'T go down)
	.byte $20 | $0C, $39, $41; Wooden blocks
	.byte $00 | $0D, $3C, $07; Multi-directional directional platform
	.byte $20 | $04, $3E, $A4; Downward Pipe (CAN'T go down)
	.byte $20 | $09, $3E, $D4; Upward Pipe (CAN'T go up)
	.byte $20 | $01, $48, $46; Wooden blocks
	.byte $00 | $07, $45, $04; Upward directional platform
	.byte $00 | $08, $4D, $0A; Door
	.byte $20 | $0A, $40, $F8; Rightward Pipe (CAN'T go in)
	.byte $40 | $0A, $49, $26; Leftward Pipe (CAN'T go in)
	.byte $00 | $0E, $11, $00; Upper-left corner of curved pipe
	.byte $00 | $0E, $18, $01; Upper-right corner of curved pipe
	.byte $00 | $09, $21, $02; Lower-left corner of curved pipe
	.byte $00 | $09, $2E, $03; Lower-right corner of curved pipe
	; Pointer on screen $04
	.byte $E0 | $04, $70 | $08, 133; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $00
	.byte $E0 | $00, $10 | $02, 153; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__2_Pipe_Room_W4_objects:
	.byte $56, $08, $0D; Leftward Piranha Plant
	.byte $A2, $09, $2E; Red Piranha Plant (upward)
	.byte $A2, $09, $37; Red Piranha Plant (upward)
	.byte $56, $06, $2F; Leftward Piranha Plant
	.byte $FF
; Level_5_Bonus_Area_W4
; Object Set 1
Level_5_Bonus_Area_W4_generators:
Level_5_Bonus_Area_W4_header:
	.byte $6E; Next Level
	.byte LEVEL1_SIZE_05 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_11; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $BF, $21; Blue X-Blocks
	.byte $40 | $10, $00, $BA, $00; Blue X-Blocks
	.byte $40 | $1A, $00, $B0, $10; Blue X-Blocks
	.byte $40 | $10, $0E, $BA, $13; Blue X-Blocks
	.byte $20 | $17, $05, $92; Downward Pipe (CAN go down)
	.byte $20 | $17, $09, $13; Bricks
	.byte $40 | $19, $0D, $08; P-Switch
	.byte $00 | $1A, $20, $D0, $2F; Underwater Flat Ground
	.byte $40 | $18, $22, $22; Leftward Pipe (CAN'T go in)
	.byte $00 | $19, $27, $93; Background Bushes
	.byte $00 | $16, $2B, $00; Background Hills A
	.byte $00 | $12, $27, $E2; Background Clouds
	.byte $00 | $13, $30, $E2; Background Clouds
	.byte $00 | $19, $30, $93; Background Bushes
	.byte $40 | $00, $39, $09; Level Ending
	; Pointer on screen $00
	.byte $E0 | $00, $10 | $02, 117; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_5_Bonus_Area_W4_objects:
	.byte $98, $0A, $13; Giant '?' Block with Tanooki Suit
	.byte $41, $48, $15; Goal Card
	.byte $FF
; Dungeon__1_Underground_Room_W4
; Object Set 14
Dungeon__1_Underground_Room_W4_generators:
Dungeon__1_Underground_Room_W4_header:
	.byte $70; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_10 | LEVEL2_BGPAL_04; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $0B, $00, $8F, $09; Flat Land - Hilly
	.byte $80 | $00, $00, $5B, $01; Hilly Fill
	.byte $60 | $00, $01, $EA; Hilly Wall - Right Side
	.byte $60 | $0B, $09, $E4; Hilly Wall - Right Side
	.byte $00 | $0B, $09, $04; Upper Right Hill Corner - Hilly
	.byte $80 | $10, $0A, $8A, $25; Flat Land - Hilly
	.byte $80 | $00, $04, $B7, $08; Ceiling - Hilly
	.byte $80 | $00, $0D, $B9, $14; Ceiling - Hilly
	.byte $80 | $09, $0D, $B3, $03; Ceiling - Hilly
	.byte $00 | $00, $04, $E7; Hilly Wall - Left Side
	.byte $00 | $08, $0D, $E4; Hilly Wall - Left Side
	.byte $00 | $07, $04, $07; Lower Left Corner - Hilly
	.byte $00 | $0C, $0D, $07; Lower Left Corner - Hilly
	.byte $20 | $00, $02, $D1; Upward Pipe (CAN'T go up)
	.byte $60 | $0A, $10, $E2; Hilly Wall - Right Side
	.byte $00 | $0C, $10, $0A; Lower Right Hill Corner
	.byte $20 | $0C, $16, $25; '?' blocks with single coins
	.byte $20 | $0C, $1A, $00; '?' with flower
	.byte $80 | $00, $22, $B3, $0A; Ceiling - Hilly
	.byte $80 | $07, $25, $8A, $0A; Flat Land - Hilly
	.byte $00 | $00, $2F, $E6; Hilly Wall - Left Side
	.byte $60 | $04, $21, $E5; Hilly Wall - Right Side
	.byte $60 | $00, $2C, $E3; Hilly Wall - Right Side
	.byte $00 | $07, $25, $E8; Hilly Wall - Left Side
	.byte $00 | $09, $21, $0A; Lower Right Hill Corner
	.byte $00 | $03, $2C, $0A; Lower Right Hill Corner
	.byte $00 | $07, $25, $01; Upper Left Hill Corner - Hilly
	.byte $20 | $00, $2D, $C4; Upward Pipe (CAN go up)
	.byte $20 | $08, $23, $0E; Invisible Coin
	.byte $20 | $0C, $22, $0E; Invisible Coin
	.byte $80 | $07, $2F, $50, $00; Hilly Fill
	; Pointer on screen $02
	.byte $E0 | $02, $50 | $01, 70; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__1_Underground_Room_W4_objects:
	.byte $3F, $08, $0A; Dry Bones
	.byte $3F, $14, $0F; Dry Bones
	.byte $2F, $1D, $0A; Boo Buddy
	.byte $3F, $23, $0F; Dry Bones
	.byte $FF
; Level_3_W4
; Object Set 3
Level_3_W4_generators:
Level_3_W4_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_11 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_09 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_03; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $03; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $00, $00, $0E; Underground Fill
	.byte $80 | $00, $00, $5F, $15; Hilly Wall
	.byte $80 | $10, $00, $5A, $01; Hilly Wall
	.byte $80 | $19, $02, $81, $16; Flat Land - Hilly
	.byte $80 | $19, $09, $51, $0B; Hilly Wall
	.byte $80 | $10, $04, $B2, $11; Ceiling
	.byte $60 | $00, $01, $EF; Hilly Wall - Right Side
	.byte $60 | $10, $01, $E8; Hilly Wall - Right Side
	.byte $00 | $00, $04, $EF; Hilly Wall - Left Side
	.byte $00 | $10, $04, $E2; Hilly Wall - Left Side
	.byte $00 | $12, $04, $07; Lower Left Hill Corner
	.byte $60 | $17, $0B, $61; 30 Degree Hill - Down/Left
	.byte $80 | $17, $0D, $83, $03; Flat Land - Hilly
	.byte $20 | $06, $02, $DF; Upward Pipe (CAN'T go up)
	.byte $80 | $00, $16, $B9, $2C; Ceiling
	.byte $60 | $0A, $15, $E7; Hilly Wall - Right Side
	.byte $00 | $12, $15, $0A; Lower Right Hill Corner
	.byte $60 | $17, $11, $51; 30 Degree Hill - Down/Right
	.byte $00 | $19, $18, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $1A, $18, $E0; Hilly Wall - Right Side
	.byte $60 | $14, $1B, $0C; Square Hill Object
	.byte $60 | $14, $1F, $0C; Square Hill Object
	.byte $80 | $16, $1F, $80, $03; Flat Land - Hilly
	.byte $80 | $17, $1F, $B0, $03; Ceiling
	.byte $20 | $13, $1F, $23; '?' blocks with single coins
	.byte $80 | $17, $2C, $53, $05; Hilly Wall
	.byte $00 | $17, $2C, $E3; Hilly Wall - Left Side
	.byte $20 | $12, $26, $83; Coins
	.byte $20 | $0F, $2E, $45; Wooden blocks
	.byte $80 | $14, $32, $86, $02; Flat Land - Hilly
	.byte $60 | $14, $30, $62; 30 Degree Hill - Down/Left
	.byte $00 | $14, $34, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $15, $34, $E5; Hilly Wall - Right Side
	.byte $60 | $14, $37, $0C; Square Hill Object
	.byte $20 | $12, $3B, $01; '?' with leaf
	.byte $80 | $00, $43, $BF, $07; Ceiling
	.byte $00 | $0A, $43, $E5; Hilly Wall - Left Side
	.byte $60 | $03, $4A, $EC; Hilly Wall - Right Side
	.byte $00 | $0F, $43, $07; Lower Left Hill Corner
	.byte $00 | $0F, $4A, $0A; Lower Right Hill Corner
	.byte $80 | $00, $4B, $B2, $21; Ceiling
	.byte $80 | $17, $40, $83, $0B; Flat Land - Hilly
	.byte $00 | $17, $40, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $18, $40, $E2; Hilly Wall - Left Side
	.byte $80 | $1A, $4C, $50, $02; Hilly Wall
	.byte $60 | $1A, $4E, $E0; Hilly Wall - Right Side
	.byte $00 | $17, $4C, $52; 45 Degree Hill - Down/Right
	.byte $80 | $06, $5C, $86, $0F; Flat Land - Hilly
	.byte $80 | $0D, $5C, $B3, $05; Ceiling
	.byte $00 | $08, $5C, $E8; Hilly Wall - Left Side
	.byte $00 | $10, $5C, $07; Lower Left Hill Corner
	.byte $60 | $04, $50, $0C; Square Hill Object
	.byte $60 | $04, $54, $04; Horizontal Hill Strip
	.byte $80 | $15, $58, $85, $03; Flat Land - Hilly
	.byte $00 | $19, $54, $E1; Hilly Wall - Left Side
	.byte $80 | $19, $55, $51, $0A; Hilly Wall
	.byte $00 | $15, $57, $63; 45 Degree Hill - Down/Left
	.byte $00 | $15, $5C, $54; 45 Degree Hill - Down/Right
	.byte $20 | $04, $54, $82; Coins
	.byte $20 | $04, $58, $82; Coins
	.byte $20 | $04, $5C, $82; Coins
	.byte $00 | $06, $6B, $04; Upper Right Hill Corner - Hilly
	.byte $60 | $07, $6B, $E4; Hilly Wall - Right Side
	.byte $80 | $0C, $62, $B0, $08; Ceiling
	.byte $00 | $0C, $6B, $0A; Lower Right Hill Corner
	.byte $60 | $0D, $61, $E3; Hilly Wall - Right Side
	.byte $00 | $10, $61, $0A; Lower Right Hill Corner
	.byte $80 | $00, $6D, $BE, $1A; Ceiling
	.byte $80 | $0E, $6D, $B6, $03; Ceiling
	.byte $00 | $03, $6D, $EF; Hilly Wall - Left Side
	.byte $00 | $13, $6D, $E0; Hilly Wall - Left Side
	.byte $00 | $14, $6D, $07; Lower Left Hill Corner
	.byte $80 | $19, $69, $51, $05; Hilly Wall
	.byte $80 | $17, $6B, $81, $01; Flat Land - Hilly
	.byte $00 | $17, $6A, $61; 45 Degree Hill - Down/Left
	.byte $00 | $17, $6D, $51; 45 Degree Hill - Down/Right
	.byte $00 | $19, $69, $E1; Hilly Wall - Left Side
	.byte $80 | $19, $6F, $81, $19; Flat Land - Hilly
	.byte $60 | $1A, $60, $E0; Hilly Wall - Right Side
	.byte $20 | $04, $64, $82; Coins
	.byte $20 | $04, $68, $82; Coins
	.byte $60 | $10, $71, $0C; Square Hill Object
	.byte $60 | $10, $7E, $0C; Square Hill Object
	.byte $60 | $10, $75, $04; Horizontal Hill Strip
	.byte $60 | $10, $7A, $04; Horizontal Hill Strip
	.byte $00 | $18, $74, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $18, $75, $04; Upper Right Hill Corner - Hilly
	.byte $00 | $18, $7E, $01; Upper Left Hill Corner - Hilly
	.byte $00 | $18, $7F, $04; Upper Right Hill Corner - Hilly
	.byte $20 | $11, $71, $32; Bricks with single coins
	.byte $20 | $11, $71, $0B; Brick with 1-up
	.byte $20 | $15, $71, $41; Wooden blocks
	.byte $80 | $19, $74, $51, $01; Hilly Wall
	.byte $80 | $19, $7E, $51, $01; Hilly Wall
	.byte $60 | $0A, $87, $E3; Hilly Wall - Right Side
	.byte $00 | $0E, $87, $0A; Lower Right Hill Corner
	.byte $80 | $00, $88, $B9, $21; Ceiling
	.byte $60 | $1A, $88, $E0; Hilly Wall - Right Side
	.byte $00 | $19, $88, $04; Upper Right Hill Corner - Hilly
	.byte $80 | $16, $8F, $82, $00; Flat Land - Hilly
	.byte $80 | $18, $8D, $B0, $04; Ceiling
	.byte $00 | $16, $8E, $61; 45 Degree Hill - Down/Left
	.byte $00 | $18, $8D, $07; Lower Left Hill Corner
	.byte $20 | $16, $84, $14; Bricks
	.byte $00 | $16, $90, $51; 45 Degree Hill - Down/Right
	.byte $00 | $18, $91, $0A; Lower Right Hill Corner
	.byte $80 | $14, $96, $82, $00; Flat Land - Hilly
	.byte $00 | $14, $95, $61; 45 Degree Hill - Down/Left
	.byte $80 | $16, $94, $B0, $04; Ceiling
	.byte $00 | $16, $94, $07; Lower Left Hill Corner
	.byte $00 | $16, $98, $0A; Lower Right Hill Corner
	.byte $00 | $14, $97, $51; 45 Degree Hill - Down/Right
	.byte $00 | $12, $9F, $61; 45 Degree Hill - Down/Left
	.byte $80 | $14, $9E, $B0, $04; Ceiling
	.byte $00 | $14, $9E, $07; Lower Left Hill Corner
	.byte $20 | $11, $97, $81; Coins
	.byte $20 | $12, $92, $81; Coins
	.byte $20 | $11, $9B, $82; Coins
	.byte $20 | $12, $96, $70; Wooden Blocks - movable
	.byte $20 | $13, $96, $70; Wooden Blocks - movable
	.byte $80 | $12, $A0, $81, $00; Flat Land - Hilly
	.byte $00 | $12, $A1, $51; 45 Degree Hill - Down/Right
	.byte $00 | $14, $A2, $0A; Lower Right Hill Corner
	.byte $60 | $11, $A3, $0C; Square Hill Object
	.byte $60 | $11, $A7, $04; Horizontal Hill Strip
	.byte $80 | $13, $AF, $51, $00; Hilly Wall
	.byte $80 | $00, $AA, $BF, $02; Ceiling
	.byte $00 | $0A, $AA, $E5; Hilly Wall - Left Side
	.byte $00 | $0F, $AA, $07; Lower Left Hill Corner
	.byte $00 | $0F, $AC, $0A; Lower Right Hill Corner
	.byte $60 | $00, $AC, $EE; Hilly Wall - Right Side
	.byte $00 | $00, $AF, $EF; Hilly Wall - Left Side
	.byte $00 | $10, $AF, $E2; Hilly Wall - Left Side
	.byte $00 | $15, $AF, $E5; Hilly Wall - Left Side
	.byte $80 | $01, $AD, $EF; Upward Pipe to End of Level
	.byte $FF
Level_3_W4_objects:
	.byte $70, $12, $16; Buzzy Beetle
	.byte $70, $17, $18; Buzzy Beetle
	.byte $68, $15, $13; Upside-down Buzzy Beetle
	.byte $70, $22, $15; Buzzy Beetle
	.byte $80, $25, $14; Green Koopa Paratroopa (doesn't bounce)
	.byte $68, $33, $10; Upside-down Buzzy Beetle
	.byte $69, $48, $10; Upside-down Spiny
	.byte $70, $4B, $16; Buzzy Beetle
	.byte $6F, $50, $13; Red Koopa Paratroopa
	.byte $6F, $65, $13; Red Koopa Paratroopa
	.byte $69, $61, $11; Upside-down Spiny
	.byte $70, $71, $18; Buzzy Beetle
	.byte $70, $71, $18; Buzzy Beetle
	.byte $69, $7E, $14; Upside-down Spiny
	.byte $69, $86, $17; Upside-down Spiny
	.byte $70, $88, $15; Buzzy Beetle
	.byte $FF
; Default_Level_166
; Object Set 11
Default_Level_166_generators:
Default_Level_166_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_02 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_02; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_00; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0D; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $00, $00, $03; Weird
	.byte $40 | $00, $09, $09; Level Ending
	.byte $60 | $19, $00, $11, $1F; Weird
	.byte $40 | $17, $00, $22; Leftward Pipe (CAN'T go in)
	.byte $FF
Default_Level_166_objects:
	.byte $83, $0F, $12; Lakitu
	.byte $41, $18, $15; Goal Card
	.byte $FF
; Level_4_Bonus_Area_W4
; Object Set 1
Level_4_Bonus_Area_W4_generators:
Level_4_Bonus_Area_W4_header:
	.byte $73; Next Level
	.byte LEVEL1_SIZE_02 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_05; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_11; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $40 | $0F, $00, $8B, $05; Water (still)
	.byte $40 | $15, $06, $84, $09; Water (still)
	.byte $40 | $0F, $10, $8B, $01; Water (still)
	.byte $40 | $17, $11, $83, $0A; Water (still)
	.byte $40 | $0F, $1C, $8B, $02; Water (still)
	.byte $20 | $0F, $00, $4F; Wooden Blocks
	.byte $20 | $10, $00, $40; Wooden Blocks
	.byte $20 | $11, $00, $40; Wooden Blocks
	.byte $20 | $12, $00, $40; Wooden Blocks
	.byte $20 | $13, $00, $40; Wooden Blocks
	.byte $20 | $14, $00, $40; Wooden Blocks
	.byte $20 | $15, $00, $40; Wooden Blocks
	.byte $20 | $16, $00, $40; Wooden Blocks
	.byte $20 | $17, $00, $40; Wooden Blocks
	.byte $20 | $18, $00, $40; Wooden Blocks
	.byte $20 | $19, $00, $40; Wooden Blocks
	.byte $20 | $1A, $00, $4F; Wooden Blocks
	.byte $20 | $10, $05, $40; Wooden Blocks
	.byte $20 | $11, $05, $40; Wooden Blocks
	.byte $20 | $12, $05, $40; Wooden Blocks
	.byte $20 | $13, $05, $40; Wooden Blocks
	.byte $20 | $14, $05, $40; Wooden Blocks
	.byte $20 | $15, $05, $40; Wooden Blocks
	.byte $20 | $16, $05, $40; Wooden Blocks
	.byte $20 | $17, $05, $40; Wooden Blocks
	.byte $20 | $10, $0F, $40; Wooden Blocks
	.byte $20 | $11, $0F, $40; Wooden Blocks
	.byte $20 | $12, $0F, $40; Wooden Blocks
	.byte $20 | $13, $0F, $40; Wooden Blocks
	.byte $20 | $14, $0F, $40; Wooden Blocks
	.byte $20 | $15, $0F, $40; Wooden Blocks
	.byte $20 | $16, $0F, $40; Wooden Blocks
	.byte $20 | $17, $0F, $40; Wooden Blocks
	.byte $20 | $17, $07, $46; Wooden Blocks
	.byte $40 | $10, $06, $58; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $11, $06, $58; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $12, $06, $58; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $13, $06, $53; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $13, $0B, $53; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $14, $06, $53; Silver Coins (appear when you hit a P-Switch)
	.byte $40 | $14, $0B, $53; Silver Coins (appear when you hit a P-Switch)
	.byte $20 | $14, $0A, $0D; Brick with P-Switch
	.byte $20 | $18, $01, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $0F, $10, $4F; Wooden Blocks
	.byte $20 | $10, $1F, $40; Wooden Blocks
	.byte $20 | $11, $1F, $40; Wooden Blocks
	.byte $20 | $12, $1F, $40; Wooden Blocks
	.byte $20 | $13, $1F, $40; Wooden Blocks
	.byte $20 | $14, $1F, $40; Wooden Blocks
	.byte $20 | $15, $1F, $40; Wooden Blocks
	.byte $20 | $16, $1F, $40; Wooden Blocks
	.byte $20 | $17, $1F, $40; Wooden Blocks
	.byte $20 | $18, $1F, $40; Wooden Blocks
	.byte $20 | $19, $1F, $40; Wooden Blocks
	.byte $20 | $1A, $10, $4F; Wooden Blocks
	.byte $20 | $10, $11, $40; Wooden Blocks
	.byte $20 | $11, $11, $40; Wooden Blocks
	.byte $20 | $12, $11, $40; Wooden Blocks
	.byte $20 | $13, $11, $40; Wooden Blocks
	.byte $20 | $14, $11, $40; Wooden Blocks
	.byte $20 | $15, $11, $40; Wooden Blocks
	.byte $20 | $16, $11, $40; Wooden Blocks
	.byte $20 | $17, $11, $40; Wooden Blocks
	.byte $20 | $10, $1B, $40; Wooden Blocks
	.byte $20 | $11, $1B, $40; Wooden Blocks
	.byte $20 | $12, $1B, $40; Wooden Blocks
	.byte $20 | $13, $1B, $40; Wooden Blocks
	.byte $20 | $14, $1B, $40; Wooden Blocks
	.byte $20 | $15, $1B, $40; Wooden Blocks
	.byte $20 | $16, $1B, $40; Wooden Blocks
	.byte $20 | $17, $1B, $40; Wooden Blocks
	.byte $20 | $17, $13, $46; Wooden Blocks
	.byte $20 | $17, $16, $0D; Brick with P-Switch
	.byte $20 | $10, $12, $18; Bricks
	.byte $20 | $11, $12, $18; Bricks
	.byte $20 | $12, $12, $18; Bricks
	.byte $20 | $13, $12, $18; Bricks
	.byte $20 | $14, $12, $88; Coins
	.byte $20 | $0F, $1C, $C1; Upward Pipe (CAN go up)
	; Pointer on screen $01
	.byte $E0 | $01, $60 | $01, 66; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_4_Bonus_Area_W4_objects:
	.byte $FF
; Level_1_Bonus_Area_W4
; Object Set 11
Level_1_Bonus_Area_W4_generators:
Level_1_Bonus_Area_W4_header:
	.byte $75; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_11; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0B; Start action | Graphic set
	.byte $00 | $02; Time | Music
	.byte $40 | $12, $01, $87, $1D; Water (still)
	.byte $40 | $0F, $00, $B1, $20; Blue X-Blocks
	.byte $40 | $11, $00, $BA, $00; Blue X-Blocks
	.byte $40 | $1A, $00, $B0, $20; Blue X-Blocks
	.byte $40 | $0F, $1F, $BB, $0F; Blue X-Blocks
	.byte $20 | $0F, $07, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $0F, $1D, $C7; Upward Pipe (CAN go up)
	.byte $00 | $16, $0A, $83; Giant Downward Pipe
	.byte $20 | $17, $0D, $32; Bricks with single coins
	.byte $20 | $16, $12, $33; Bricks with single coins
	.byte $20 | $19, $1B, $30; Bricks with single coins
	.byte $20 | $16, $14, $0B; Brick with 1-up
	.byte $20 | $17, $0E, $0B; Brick with 1-up
	; Pointer on screen $01
	.byte $E0 | $01, $20 | $01, 163; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_1_Bonus_Area_W4_objects:
	.byte $63, $0F, $13; Big Bertha (underwater)
	.byte $63, $17, $17; Big Bertha (underwater)
	.byte $FF
; Level_2_Pipe_Room_W5
; Object Set 8
Level_2_Pipe_Room_W5_generators:
Level_2_Pipe_Room_W5_header:
	.byte $77; Next Level
	.byte LEVEL1_SIZE_12 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_VERTICAL | LEVEL3_TILESET_14; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $08; Start action | Graphic set
	.byte $00 | $01; Time | Music
	.byte $00 | $00, $00, $0C; Background for pipe levels
	.byte $20 | $00, $00, $40; Wooden blocks
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
	.byte $20 | $0E, $00, $40; Wooden blocks
	.byte $20 | $00, $10, $40; Wooden blocks
	.byte $20 | $01, $10, $40; Wooden blocks
	.byte $20 | $02, $10, $40; Wooden blocks
	.byte $20 | $03, $10, $40; Wooden blocks
	.byte $20 | $04, $10, $40; Wooden blocks
	.byte $20 | $05, $10, $40; Wooden blocks
	.byte $20 | $06, $10, $40; Wooden blocks
	.byte $20 | $07, $10, $40; Wooden blocks
	.byte $20 | $08, $10, $40; Wooden blocks
	.byte $20 | $09, $10, $40; Wooden blocks
	.byte $20 | $0A, $10, $40; Wooden blocks
	.byte $20 | $0B, $10, $40; Wooden blocks
	.byte $20 | $0C, $10, $40; Wooden blocks
	.byte $20 | $0D, $10, $40; Wooden blocks
	.byte $20 | $0E, $10, $40; Wooden blocks
	.byte $20 | $00, $05, $40; Wooden blocks
	.byte $20 | $01, $05, $40; Wooden blocks
	.byte $20 | $02, $05, $40; Wooden blocks
	.byte $20 | $03, $05, $40; Wooden blocks
	.byte $20 | $04, $05, $40; Wooden blocks
	.byte $20 | $05, $05, $40; Wooden blocks
	.byte $20 | $06, $05, $40; Wooden blocks
	.byte $20 | $07, $05, $40; Wooden blocks
	.byte $20 | $08, $05, $40; Wooden blocks
	.byte $20 | $09, $05, $40; Wooden blocks
	.byte $20 | $0A, $05, $40; Wooden blocks
	.byte $20 | $0B, $05, $40; Wooden blocks
	.byte $20 | $0C, $05, $40; Wooden blocks
	.byte $20 | $0D, $05, $40; Wooden blocks
	.byte $20 | $0E, $05, $40; Wooden blocks
	.byte $20 | $00, $15, $40; Wooden blocks
	.byte $20 | $01, $15, $40; Wooden blocks
	.byte $20 | $02, $15, $40; Wooden blocks
	.byte $20 | $03, $15, $40; Wooden blocks
	.byte $20 | $04, $15, $40; Wooden blocks
	.byte $20 | $05, $15, $40; Wooden blocks
	.byte $20 | $06, $15, $40; Wooden blocks
	.byte $20 | $07, $15, $40; Wooden blocks
	.byte $20 | $08, $15, $40; Wooden blocks
	.byte $20 | $09, $15, $40; Wooden blocks
	.byte $20 | $0A, $15, $40; Wooden blocks
	.byte $20 | $0B, $15, $40; Wooden blocks
	.byte $20 | $0C, $15, $40; Wooden blocks
	.byte $20 | $0D, $15, $40; Wooden blocks
	.byte $20 | $0E, $15, $40; Wooden blocks
	.byte $20 | $00, $02, $D1; Upward Pipe (CAN'T go up)
	.byte $20 | $00, $0A, $DF; Upward Pipe (CAN'T go up)
	.byte $20 | $00, $1A, $C3; Upward Pipe (CAN go up)
	.byte $20 | $02, $16, $42; Wooden blocks
	.byte $20 | $02, $1D, $42; Wooden blocks
	.byte $20 | $07, $18, $10; Bricks
	.byte $20 | $07, $1D, $10; Bricks
	.byte $20 | $08, $19, $13; Bricks
	.byte $20 | $09, $16, $10; Bricks
	.byte $20 | $0C, $17, $10; Bricks
	.byte $20 | $00, $29, $10; Bricks
	.byte $20 | $03, $2C, $12; Bricks
	.byte $20 | $05, $23, $60; Note Blocks - movable two directions
	.byte $20 | $05, $27, $10; Bricks
	.byte $20 | $07, $2A, $11; Bricks
	.byte $40 | $08, $25, $02; Note Block with Leaf
	.byte $20 | $0B, $28, $60; Note Blocks - movable two directions
	.byte $20 | $0B, $25, $40; Wooden blocks
	.byte $00 | $07, $38, $63; Rightward background pipe
	.byte $00 | $07, $3C, $72; Leftward background pipe
	.byte $00 | $0B, $3C, $59; Small Vertical background pipe
	.byte $00 | $06, $44, $4E; Downward background pipe
	.byte $00 | $01, $5C, $83; Small Horizontal background pipe
	.byte $00 | $04, $59, $84; Small Horizontal background pipe
	.byte $00 | $02, $65, $62; Rightward background pipe
	.byte $00 | $02, $6A, $72; Leftward background pipe
	.byte $00 | $0C, $58, $4A; Downward background pipe
	.byte $00 | $08, $62, $49; Downward background pipe
	.byte $00 | $02, $7A, $5B; Small Vertical background pipe
	.byte $00 | $02, $7C, $5B; Small Vertical background pipe
	.byte $00 | $07, $73, $85; Small Horizontal background pipe
	.byte $00 | $04, $8C, $4E; Downward background pipe
	.byte $00 | $0A, $82, $63; Rightward background pipe
	.byte $00 | $0A, $86, $72; Leftward background pipe
	.byte $00 | $01, $94, $56; Small Vertical background pipe
	.byte $00 | $01, $96, $56; Small Vertical background pipe
	.byte $00 | $0A, $96, $63; Rightward background pipe
	.byte $00 | $0A, $9A, $71; Leftward background pipe
	.byte $40 | $0D, $A0, $8C, $0F; Water (still)
	.byte $20 | $08, $B7, $92; Downward Pipe (CAN go down)
	.byte $20 | $0B, $B0, $4F; Wooden blocks
	.byte $20 | $06, $B3, $A4; Downward Pipe (CAN'T go down)
	.byte $20 | $07, $BD, $A3; Downward Pipe (CAN'T go down)
	.byte $20 | $08, $27, $82; Coins
	.byte $20 | $09, $49, $80; Coins
	.byte $20 | $0D, $48, $80; Coins
	.byte $20 | $02, $57, $80; Coins
	.byte $20 | $0A, $59, $80; Coins
	.byte $20 | $00, $6B, $80; Coins
	.byte $20 | $07, $6C, $80; Coins
	.byte $20 | $09, $6C, $80; Coins
	.byte $20 | $0B, $6C, $80; Coins
	.byte $20 | $00, $7A, $80; Coins
	.byte $20 | $03, $79, $80; Coins
	.byte $20 | $06, $78, $80; Coins
	.byte $20 | $02, $86, $80; Coins
	.byte $20 | $05, $87, $80; Coins
	.byte $20 | $09, $86, $80; Coins
	.byte $20 | $0D, $87, $80; Coins
	.byte $20 | $02, $A7, $81; Coins
	.byte $20 | $04, $A7, $81; Coins
	; Pointer on screen $01
	.byte $E0 | $01, $60 | $01, 34; Domain | Screen, Y Exit | Action, X Exit
	; Pointer on screen $0B
	.byte $E0 | $0B, $10 | $02, 136; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_2_Pipe_Room_W5_objects:
	.byte $6C, $0F, $10; Green Koopa Troopa
	.byte $6C, $07, $10; Green Koopa Troopa
	.byte $6C, $0E, $20; Green Koopa Troopa
	.byte $FF
; Level_3_Ending_W5
; Object Set 1
Level_3_Ending_W5_generators:
Level_3_Ending_W5_header:
	.byte $0F; Next Level
	.byte LEVEL1_SIZE_02 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte $40 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $08; Time | Music
	.byte $00 | $1A, $00, $C0, $1F; Flat Ground
	.byte $00 | $10, $08, $E2; Background Clouds
	.byte $00 | $12, $04, $E2; Background Clouds
	.byte $20 | $18, $02, $A1; Downward Pipe (CAN'T go down)
	.byte $00 | $19, $04, $96; Background Bushes
	.byte $00 | $12, $06, $02; Background Hills C
	.byte $40 | $00, $0C, $09; Level Ending
	.byte $FF
Level_3_Ending_W5_objects:
	.byte $41, $18, $15; Goal Card
	.byte $FF
; Level_1_Bonus_Area_W5
; Object Set 1
Level_1_Bonus_Area_W5_generators:
Level_1_Bonus_Area_W5_header:
	.byte $79; Next Level
	.byte LEVEL1_SIZE_07 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $20 | LEVEL3_TILESET_01; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $01; Start action | Graphic set
	.byte $00 | $00; Time | Music
	.byte $40 | $00, $00, $B9, $01; Blue X-Blocks
	.byte $40 | $00, $00, $B3, $07; Blue X-Blocks
	.byte $40 | $00, $08, $B7, $09; Blue X-Blocks
	.byte $40 | $0A, $00, $BF, $05; Blue X-Blocks
	.byte $40 | $1A, $00, $B0, $05; Blue X-Blocks
	.byte $40 | $0F, $06, $BB, $07; Blue X-Blocks
	.byte $40 | $15, $0E, $B5, $07; Blue X-Blocks
	.byte $20 | $07, $02, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $11, $0E, $0E; Invisible Coin
	.byte $40 | $00, $12, $BA, $23; Blue X-Blocks
	.byte $40 | $0C, $10, $B5, $02; Blue X-Blocks
	.byte $40 | $0C, $14, $B5, $02; Blue X-Blocks
	.byte $40 | $0C, $18, $B9, $03; Blue X-Blocks
	.byte $40 | $0C, $1C, $B7, $03; Blue X-Blocks
	.byte $40 | $19, $16, $B1, $09; Blue X-Blocks
	.byte $20 | $14, $1E, $C1; Upward Pipe (CAN go up)
	.byte $40 | $0C, $20, $BE, $10; Blue X-Blocks
	.byte $40 | $11, $31, $B8, $04; Blue X-Blocks
	.byte $40 | $00, $36, $BF, $09; Blue X-Blocks
	.byte $40 | $10, $36, $BA, $09; Blue X-Blocks
	.byte $00 | $1A, $40, $C0, $30; Flat Ground
	.byte $40 | $18, $40, $23; Leftward Pipe (CAN'T go in)
	.byte $00 | $19, $46, $92; Background Bushes
	.byte $00 | $16, $4A, $00; Background Hills A
	.byte $00 | $19, $50, $94; Background Bushes
	.byte $40 | $00, $56, $09; Level Ending
	; Pointer on screen $01
	.byte $E0 | $01, $60 | $01, 163; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Level_1_Bonus_Area_W5_objects:
	.byte $D6, $32, $0D; Puts item in treasure chest (Y pos. determines item; see docs/items.txt)
	.byte $52, $33, $0F; Treasure Chest
	.byte $BA, $34, $0F; Exit on get treasure chest
	.byte $FF
; Tower_Outside_Area__Part_1__W5
; Object Set 13
Tower_Outside_Area__Part_1__W5_generators:
Tower_Outside_Area__Part_1__W5_header:
	.byte $3B; Next Level
	.byte LEVEL1_SIZE_03 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $80 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $40 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $0D; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $00 | $00, $11, $02; Cloud Background A
	.byte $00 | $0B, $00, $02; Cloud Background A
	.byte $00 | $09, $0A, $02; Cloud Background A
	.byte $00 | $09, $06, $02; Cloud Background A
	.byte $00 | $04, $03, $02; Cloud Background A
	.byte $00 | $02, $0D, $02; Cloud Background A
	.byte $60 | $10, $00, $4A, $04; White Background
	.byte $60 | $0B, $05, $4F, $18; White Background
	.byte $60 | $09, $0F, $41, $06; White Background
	.byte $60 | $00, $16, $48, $10; White Background
	.byte $60 | $0A, $14, $46, $05; White Background
	.byte $60 | $00, $20, $4F, $0F; White Background
	.byte $60 | $10, $20, $4A, $0F; White Background
	.byte $20 | $10, $0D, $82; Coins
	.byte $20 | $11, $08, $82; Coins
	.byte $20 | $11, $0C, $80; Coins
	.byte $20 | $16, $02, $13; Bricks
	.byte $20 | $14, $03, $A2; Downward Pipe (CAN'T go down)
	.byte $20 | $15, $0C, $10; Bricks
	.byte $20 | $15, $0E, $0B; Brick with 1-up
	.byte $20 | $16, $00, $10; Bricks
	.byte $20 | $16, $07, $10; Bricks
	.byte $20 | $16, $0C, $14; Bricks
	.byte $20 | $17, $00, $17; Bricks
	.byte $20 | $17, $0C, $14; Bricks
	.byte $20 | $18, $00, $17; Bricks
	.byte $20 | $18, $0D, $12; Bricks
	.byte $20 | $19, $00, $16; Bricks
	.byte $20 | $19, $0D, $12; Bricks
	.byte $20 | $1A, $00, $16; Bricks
	.byte $20 | $1A, $0D, $12; Bricks
	.byte $20 | $00, $1A, $1C; Bricks
	.byte $20 | $01, $1A, $1C; Bricks
	.byte $20 | $02, $1A, $1C; Bricks
	.byte $20 | $03, $1A, $1C; Bricks
	.byte $20 | $04, $1A, $1C; Bricks
	.byte $20 | $05, $1A, $1C; Bricks
	.byte $20 | $06, $1A, $1C; Bricks
	.byte $20 | $07, $1A, $1C; Bricks
	.byte $20 | $08, $1A, $1C; Bricks
	.byte $20 | $09, $1A, $1C; Bricks
	.byte $20 | $0A, $1A, $1C; Bricks
	.byte $20 | $0B, $1A, $1C; Bricks
	.byte $20 | $0C, $1A, $1C; Bricks
	.byte $20 | $0D, $1A, $1C; Bricks
	.byte $20 | $0E, $1A, $1C; Bricks
	.byte $20 | $0F, $1A, $1C; Bricks
	.byte $20 | $10, $1A, $1C; Bricks
	.byte $20 | $11, $10, $80; Coins
	.byte $20 | $11, $1C, $C2; Upward Pipe (CAN go up)
	.byte $20 | $11, $1E, $18; Bricks
	.byte $20 | $12, $1E, $18; Bricks
	.byte $20 | $13, $1E, $18; Bricks
	.byte $20 | $14, $14, $10; Bricks
	.byte $20 | $14, $16, $10; Bricks
	.byte $20 | $14, $1E, $0A; Multi-Coin Brick
	.byte $20 | $14, $1F, $17; Bricks
	.byte $20 | $15, $14, $14; Bricks
	.byte $20 | $15, $1E, $0A; Multi-Coin Brick
	.byte $20 | $15, $1F, $17; Bricks
	.byte $20 | $16, $14, $14; Bricks
	.byte $20 | $16, $1E, $0A; Multi-Coin Brick
	.byte $20 | $16, $1F, $17; Bricks
	.byte $20 | $17, $15, $13; Bricks
	.byte $20 | $17, $1E, $0A; Multi-Coin Brick
	.byte $20 | $17, $1F, $17; Bricks
	.byte $20 | $18, $15, $18; Bricks
	.byte $20 | $18, $1E, $18; Bricks
	.byte $20 | $19, $15, $18; Bricks
	.byte $20 | $19, $1E, $18; Bricks
	.byte $20 | $1A, $15, $18; Bricks
	.byte $20 | $1A, $1E, $18; Bricks
	.byte $20 | $06, $2B, $0B; Brick with 1-up
	.byte $20 | $0C, $29, $0B; Brick with 1-up
	.byte $20 | $10, $2D, $0B; Brick with 1-up
	; Pointer on screen $01
	.byte $E0 | $01, $50 | $01, 32; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Tower_Outside_Area__Part_1__W5_objects:
	.byte $6B, $10, $15; Pile Driver Micro-Goomba
	.byte $6B, $18, $14; Pile Driver Micro-Goomba
	.byte $FF
; Dungeon__1_Bonus_Area_W5
; Object Set 2
Dungeon__1_Bonus_Area_W5_generators:
Dungeon__1_Bonus_Area_W5_header:
	.byte $7D; Next Level
	.byte LEVEL1_SIZE_04 | LEVEL1_YSTART_170; Screens | Y Start
	.byte $00 | LEVEL2_XSTART_18 | LEVEL2_OBJPAL_08 | LEVEL2_BGPAL_00; Next Level High | X Start | Sprite Palette | Block Palette
	.byte LEVEL3_PIPENOTEXIT | $00 | LEVEL3_TILESET_02; Pipe exit | Scroll type | Vertical | Alt object set
	.byte $00 | $02; Start action | Graphic set
	.byte $00 | $03; Time | Music
	.byte $60 | $0C, $01, $3C, $10; Blank Background (used to block out stuff)
	.byte $00 | $04, $00, $E7, $11; Horizontally oriented X-blocks
	.byte $00 | $0C, $00, $EC, $00; Horizontally oriented X-blocks
	.byte $20 | $0C, $01, $D4; Upward Pipe (CAN'T go up)
	.byte $20 | $13, $09, $80; Coins
	.byte $20 | $14, $08, $82; Coins
	.byte $20 | $15, $07, $80; Coins
	.byte $20 | $15, $09, $80; Coins
	.byte $20 | $15, $0B, $80; Coins
	.byte $20 | $16, $09, $80; Coins
	.byte $20 | $17, $09, $80; Coins
	.byte $20 | $18, $09, $80; Coins
	.byte $20 | $0E, $06, $0F; Invisible 1-up
	.byte $20 | $0E, $0C, $0F; Invisible 1-up
	.byte $20 | $0F, $09, $0F; Invisible 1-up
	.byte $00 | $04, $12, $EB, $2D; Horizontally oriented X-blocks
	.byte $00 | $10, $12, $E8, $2D; Horizontally oriented X-blocks
	.byte $20 | $16, $10, $92; Downward Pipe (CAN go down)
	.byte $60 | $15, $1C, $33, $14; Blank Background (used to block out stuff)
	.byte $60 | $10, $31, $38, $0D; Blank Background (used to block out stuff)
	.byte $00 | $16, $23, $63; Dungeon windows
	; Pointer on screen $01
	.byte $E0 | $01, $40 | $02, 84; Domain | Screen, Y Exit | Action, X Exit
	.byte $FF
Dungeon__1_Bonus_Area_W5_objects:
	.byte $4B, $3C, $17; Boom Boom
	.byte $FF