MEM_LevelStartA = 0x61
MEM_LevelStartB = 0x62

MEM_Player_Y = 0x0075
MEM_Player_Screen = 0x0077
MEM_Player_X = 0x0079

MEM_PAGE_C000 = 0x071F
MEM_PAGE_A000 = 0x0720

MEM_Level_TileSet = 0x070A
MEM_Player_Current = 0x0726
MEM_World_Num = 0x0727

MEM_Object_Palette = 0x073A
MEM_Enemy_Palette = 0x073B
MEM_Random_Pool_Start = 0x0781

MEM_Screen_Memory_Start = 0x6000
MEM_Screen_Memory_End = 0x7950

MEM_Graphics_Set = 0x7EBD

MEM_Screen_Start_AddressL = 0x8000
MEM_Screen_Start_AddressH = 0x8001

ROM_Level_Load_Entry = 0x891A  # From World Map Position
ROM_EndObjectParsing = 0x9934
ROM_LevelLoad_By_TileSet = 0x9A1D  # Directly By Address


MEM_ADDRESS_LABELS = {
    "00": "TempVar_01",
    "01": "TempVar_02",
    "02": "TempVar_03",
    "03": "TempVar_04",
    "04": "TempVar_05",
    "05": "TempVar_06",
    "06": "TempVar_07",
    "07": "TempVar_08",
    "08": "TempVar_09",
    "09": "TempVar_10",
    "0A": "TempVar_11",
    "0B": "TempVar_12",
    "0C": "TempVar_13",
    "0D": "TempVar_14",
    "0E": "TempVar_15",
    "0F": "TempVar_16",
    "61": "LevelStartA",  # "Level_LayPtr_AddrL",
    "62": "LevelStartB",  # "Level_LayPtr_AddrH",
    "63": "Map_Tile_AddrL (ScreenStart)",
    "64": "Map_Tile_AddrH (ScreenStart)",
    "03DE": "Level_JctCtl",
    "0700": "TileAddr_Off (InScreenOffset)",
    "0706": "LL_ShapeDef",
    "070A": "Level_TileSet",
    "0726": "Player_Current",
    "0727": "World_Num",
    "0739": "Clear_Pattern",
    "0781": "MEM_Random_Pool_Start",
    "7DFE": "JumpAddressA",
    "7DFF": "JumpAddressB",
    "7E00": "JumpEnemiesA",
    "7E01": "JumpEnemiesB",
    "97B7": "LevelLoad",
    "991E": "ObjectNotAJump",
    "992E": "JumpToFixed",
    "9934": "EndObjectParsing",
    "9935": "LoadLevel_Set_TileMemAddr",
    "9A1D": "LevelLoad By TileSet",
    "9A49": "LeveLoad_DynSizeGens",
    "9A75": "LeveLoad_FixedSizeGens",
    "9B73": "Scroll_Update",
    "B0FF": "Map PrepareLevel",
    "D2F8": "LL_RunGroundTopTiles",
    "D2FE": "LL_RunGroundMidTiles",
    "FE92": "DynJump",
    "FFBF": "PRG_Change_Both",
    "FFD1": "PRG_Change_C000",
}
