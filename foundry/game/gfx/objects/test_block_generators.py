"""Tests block generators and their functionality"""

import unittest
import random
from foundry.game.gfx.objects.LevelGeneratorBase import BlockGeneratorHandler, BlockGeneratorBase, \
    get_object_definition_index_from_data
from foundry.game.ObjectDefinitions import get_tileset_offset, OBJECT_SET_TO_DEFINITION, get_definition_of, \
    object_metadata, get_generator_from_domain_and_index, get_type, from_type


class TestObjectDefinitions(unittest.TestCase):

    def test_getting_tileset_offset(self):
        """Tests if we are actually getting the right offset"""
        assert get_tileset_offset(0) == OBJECT_SET_TO_DEFINITION[0]

    def test_get_definition_of(self):
        """Tests if we are getting the correct definition of objects"""
        assert object_metadata[0][0] == get_definition_of(0, 0)  # test if it runs
        assert object_metadata[1][0] == get_definition_of(1, 0)  # tests if tilesets work
        assert object_metadata[1][1] == get_definition_of(1, 1)  # test if typing work
        assert object_metadata[4][0] == get_definition_of(2, 0)  # tests if tileset offsets work

    def test_get_generator_from_domain_and_index(self):
        """Tests if it is getting the correct definition from the domain and index"""
        assert get_definition_of(1, 0) == get_generator_from_domain_and_index(1, 0, 0)  # test if it runs
        assert get_definition_of(4, 0) == get_generator_from_domain_and_index(4, 0, 0)  # test tileset offsets
        assert get_definition_of(1, 16) == get_generator_from_domain_and_index(1, 0, 0x10)  # test type converting
        assert get_definition_of(1, 17) == get_generator_from_domain_and_index(1, 0, 0x2F)  # test type converting

    def test_get_type(self):
        """Tests if we are getting the type"""
        assert 0 == get_type(0, 0)  # test base functionality
        assert 0x1F == get_type(1, 0)  # test domain conversion
        assert 0x1E == get_type(0, 0xFF)  # test type converting
        assert 0x10 == get_type(0, 0x10) == get_type(0, 0x1F)  # test type converting

    def test_from_type(self):
        """Test if we can convert from type"""
        assert 0 == from_type(0)  # test base functionality
        assert 0x100 == from_type(0x1F)  # test domain conversion
        assert 0xF0 == from_type(0x1E)  # test index conversion
        assert 0x10 == from_type(0x10)  # test index conversion
        assert 0x101 == from_type(0x20)  # test domain with small index conversion
        assert 0x1F0 == from_type(0x3D)  # test domain with big index conversion


class TestBlockGenerator(unittest.TestCase):

    def test_get_object_definition_index_from_data(self):
        """Tests if the function successfully converts to the corresponding index"""
        assert 0 == get_object_definition_index_from_data(0, bytearray([0, 0, 0, 0]))  # test functionality
        assert 0b1000_0000_0000 == get_object_definition_index_from_data(1, bytearray([0, 0, 0, 0]))  # test tileset

    def test_generator_from_bytes(self):
        """Tests if the level block generator loads and saves properly"""
        for _ in range(0x1000):
            tileset, data = random.randrange(1, 16), bytearray([random.randrange(0, 0xFF) for _ in range(4)])
            result = BlockGeneratorBase.generator_from_bytes(tileset, data)
            assert get_object_definition_index_from_data(*result.to_bytes()) == \
                get_object_definition_index_from_data(tileset, data)









if __name__ == '__main__':
    unittest.main()