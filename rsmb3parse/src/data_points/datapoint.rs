use crate::position::Position;
use crate::types::RomAddress;
use crate::util::rom::Rom;

pub trait Datapoint {
    fn rom(&self) -> &Rom;
    fn calculate_addresses(&self);
    fn read_values(&self);
    fn write_back(&self) {
        self.write_to_rom(self.rom());
    }
    fn write_to_rom(&self, rom: &Rom);
}


pub trait HasPosition {
    fn screen_address(&self) -> RomAddress;
    fn set_screen_address(&mut self, address: RomAddress);

    fn x_address(&self) -> RomAddress;
    fn set_x_address(&mut self, address: RomAddress);

    fn y_address(&self) -> RomAddress;
    fn set_y_address(&mut self, address: RomAddress);

    fn screen(&self) -> u8;
    fn set_screen(&mut self, screen: u8);

    fn x(&self) -> u8;
    fn set_x(&mut self, x: u8);

    fn y(&self) -> u8;
    fn set_y(&mut self, y: u8);

    fn pos(&self) -> Position {
        Position::from((self.x(), self.y(), self.screen()))
    }
    fn set_from_pos(&mut self, position: Position) {
        self.set_x(position.x);
        self.set_y(position.y);
        self.set_screen(position.screen);
    }

    fn set_from_coords(&mut self, x: u8, y: u8, screen: u8) {
        self.set_x(x);
        self.set_y(y);
        self.set_screen(screen);
    }

    fn row(&self) -> u8 {
        self.y()
    }
    fn set_row(&mut self, row: u8) {
        self.set_y(row);
    }

    fn column(&self) -> u8 {
        self.x()
    }
    fn set_column(&mut self, column: u8) {
        self.set_x(column);
    }

    fn is_at_pos(&self, position: Position) -> bool {
        self.pos() == position
    }

    fn is_at_coords(&self, x: u8, y: u8, screen: u8) -> bool {
        self.pos() == Position::from((x, y, screen))
    }
}

pub trait HasIndex {
    fn index(&self) -> u8;
    fn set_index(&mut self, index: u8);

    fn change_index(&mut self, new_index: u8) {
        self.set_index(new_index);

        self.calculate_addresses();
    }

    fn calculate_addresses(&mut self);
}
