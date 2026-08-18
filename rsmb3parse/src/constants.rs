use std::collections::HashMap;
use std::sync::RwLock;
use crate::types::RomAddress;

static Constants: RwLock<_Constants> = RwLock::new(_Constants::new());

struct _Constants {
    internal_values: HashMap<String, RomAddress>
}

impl  _Constants {
    fn new() -> _Constants {
        _Constants {
            internal_values: HashMap::new()
        }
    }
}

