use crate::types::Index;
use crate::util::rom::Rom;

pub trait Datapoint {
    fn calculate_addresses(&mut self, rom: &Rom);
    fn read_values(&mut self, rom: &Rom);
    fn write_to_rom(&self, rom: &mut Rom);
}

pub trait HasIndex: Datapoint {
    fn index(&self) -> Index;
    fn set_index(&mut self, index: Index);

    fn change_index(&mut self, new_index: Index, rom: &Rom) {
        self.set_index(new_index);

        self.calculate_addresses(rom);
    }

}
