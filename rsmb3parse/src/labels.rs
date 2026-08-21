use crate::types::RawAddress;

pub static Labels: _Labels = _Labels::from_default();

pub struct _Labels {
    pub FortressFx_MapLocationRow: RawAddress,
    pub FortressFX_MapLocation: RawAddress,
    pub FortressFX_Patterns: RawAddress,
    pub FortressFX_MapTileReplace: RawAddress,
    pub FortressFX_MapCompIdx: RawAddress,
    pub FortressFX_VAddrH: RawAddress,
    pub FortressFX_VAddrL: RawAddress,

    pub Map_Tile_Layouts: RawAddress,
    pub Map_Tile_ColorSets: RawAddress,
    pub Map_Object_ColorSets: RawAddress,
    pub Map_Bottom_Tiles: RawAddress,
    pub Map_AnimSpeeds: RawAddress,
    pub Map_ByXHi_InitIndex: RawAddress,
    pub Map_ObjSets: RawAddress,
    pub Map_LevelLayouts: RawAddress,
    pub Map_Y_Starts: RawAddress,
    pub World_Map_Max_PanR: RawAddress,
    pub Map_Airship_Travel_BaseIdx: RawAddress,
    pub Map_Airship_Dest_XSets: RawAddress,
    pub Map_Airship_Dest_YSets: RawAddress,
    pub FortressFXBase_ByWorld: RawAddress,
    pub Airship_Layouts: RawAddress,
    pub Airship_Objects: RawAddress,
    pub CoinShip_Layouts: RawAddress,
    pub CoinShip_Objects: RawAddress,
    pub LevelJctGE_Layout: RawAddress,
    pub LevelJctGE_Objects: RawAddress,
    pub LevelJctGE_Tileset: RawAddress,
    pub LevelJctBQ_Layout: RawAddress,
    pub LevelJctBQ_Objects: RawAddress,
    pub LevelJctBQ_Tileset: RawAddress,
    pub ToadShop_Layouts: RawAddress,
    pub ToadShop_Objects: RawAddress,
    pub World_BGM: RawAddress,
    pub World_BGM_Arrival: RawAddress,
    pub Map_ByRowType: RawAddress,
    pub Map_ByScrCol: RawAddress
}

impl _Labels {
    pub const fn from_default() -> Self {
        Self {
            FortressFx_MapLocationRow: RawAddress(0x14855),
            FortressFX_MapLocation: RawAddress(0x14866),
            FortressFX_Patterns: RawAddress(0x14811),
            FortressFX_MapTileReplace: RawAddress(0x14877),
            FortressFX_MapCompIdx: RawAddress(0x147EF),
            FortressFX_VAddrH: RawAddress(0x147CD),
            FortressFX_VAddrL: RawAddress(0x147DE),

            Map_Tile_Layouts: RawAddress(0x185A8),
            Map_Tile_ColorSets: RawAddress(0x1842D),
            Map_Object_ColorSets: RawAddress(0x18436),
            Map_Bottom_Tiles: RawAddress(0x18464),
            Map_AnimSpeeds: RawAddress(0x17C11),
            Map_ByXHi_InitIndex: RawAddress(0x193DA),
            Map_ByRowType: RawAddress(0x193EC),
            Map_ByScrCol: RawAddress(0x193FE),
            Map_ObjSets: RawAddress(0x19410),
            Map_LevelLayouts: RawAddress(0x19422),
            Map_Y_Starts: RawAddress(0x3C39A),
            World_Map_Max_PanR: RawAddress(0x14F44),
            Map_Airship_Travel_BaseIdx: RawAddress(0x16291),
            Map_Airship_Dest_XSets: RawAddress(0x16FDE),
            Map_Airship_Dest_YSets: RawAddress(0x16FAE),
            FortressFXBase_ByWorld: RawAddress(0x148A8),
            Airship_Layouts: RawAddress(0x19291),
            Airship_Objects: RawAddress(0x192A1),
            CoinShip_Layouts: RawAddress(0x19337),
            CoinShip_Objects: RawAddress(0x19347),
            LevelJctGE_Layout: RawAddress(0x34B27),
            LevelJctGE_Objects: RawAddress(0x34B37),
            LevelJctGE_Tileset: RawAddress(0x34B47),
            LevelJctBQ_Layout: RawAddress(0x3491B),
            LevelJctBQ_Objects: RawAddress(0x3492B),
            LevelJctBQ_Tileset: RawAddress(0x3493B),
            ToadShop_Layouts: RawAddress(0x192F8),
            ToadShop_Objects: RawAddress(0x19308),
            World_BGM: RawAddress(0x3C424),
            World_BGM_Arrival: RawAddress(0x143CA)
        }
    }
}

