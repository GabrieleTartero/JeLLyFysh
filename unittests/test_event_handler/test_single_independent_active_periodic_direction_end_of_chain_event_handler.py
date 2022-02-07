# JeLLFysh - a Python application for all-atom event-chain Monte Carlo - https://github.com/jellyfysh
# Copyright (C) 2019, 2022 The JeLLyFysh organization
# (See the AUTHORS.md file for the full list of authors.)
#
# This file is part of JeLLyFysh.
#
# JeLLyFysh is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# JeLLyFysh is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with JeLLyFysh in the LICENSE file.
# If not, see <https://www.gnu.org/licenses/>.
#
# If you use JeLLyFysh in published work, please cite the following reference (see [Hoellmer2020] in References.bib):
# Philipp Hoellmer, Liang Qin, Michael F. Faulkner, A. C. Maggs, and Werner Krauth,
# JeLLyFysh-Version1.0 -- a Python application for all-atom event-chain Monte Carlo,
# Computer Physics Communications, Volume 253, 107168 (2020), https://doi.org/10.1016/j.cpc.2020.107168.
#
import os
import sys
from unittest import TestCase, main, mock
from jellyfysh.base.exceptions import ConfigurationError
from jellyfysh.base.node import Node
from jellyfysh.base.time import Time
from jellyfysh.base.unit import Unit
from jellyfysh.event_handler.single_independent_active_periodic_direction_end_of_chain_event_handler \
    import SingleIndependentActivePeriodicDirectionEndOfChainEventHandler
import jellyfysh.setting as setting
from jellyfysh.setting import hypercubic_setting
_unittest_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
_unittest_directory_added_to_path = False
if _unittest_directory not in sys.path:
    sys.path.append(_unittest_directory)
    _unittest_directory_added_to_path = True
# noinspection PyUnresolvedReferences
from expanded_test_case import ExpandedTestCase


def tearDownModule():
    if _unittest_directory_added_to_path:
        sys.path.remove(_unittest_directory)


class TestSingleIndependentActivePeriodicDirectionEndOfChainEventHandler(ExpandedTestCase, TestCase):
    def setUp(self) -> None:
        hypercubic_setting.HypercubicSetting(beta=1.0, dimension=3, system_length=1.0)
        self._event_handler = SingleIndependentActivePeriodicDirectionEndOfChainEventHandler(chain_time=0.7)

    def _setUpNoCompositeObjects(self):
        setting.set_number_of_node_levels(1)
        setting.set_number_of_nodes_per_root_node(1)
        setting.set_number_of_root_nodes(10)

    def _setUpCompositeObjects(self):
        setting.set_number_of_node_levels(2)
        setting.set_number_of_nodes_per_root_node(2)
        setting.set_number_of_root_nodes(10)

    def tearDown(self) -> None:
        setting.reset()

    def test_number_send_event_time_arguments_one(self):
        self.assertEqual(self._event_handler.number_send_event_time_arguments, 1)

    def test_number_send_out_state_arguments_two(self):
        self.assertEqual(self._event_handler.number_send_out_state_arguments, 2)

    @mock.patch(
        "jellyfysh.event_handler.single_independent_active_periodic_direction_end_of_chain_event_handler.randint")
    def test_leaf_unit_no_composite_objects(self, random_mock):
        self._setUpNoCompositeObjects()

        # First iteration.
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[1.0, 0.0, 0.0], time_stamp=Time.from_float(0.0)), weight=1)
        random_mock.return_value = 4
        event_time, new_active_identifiers = self._event_handler.send_event_time([active_cnode])
        self.assertAlmostEqual(event_time, Time.from_float(0.7), places=13)
        random_mock.assert_called_once_with(0, 9)
        random_mock.reset_mock()
        # First list gets unpacked by mediator
        self.assertEqual(new_active_identifiers, [[(4,)]])

        active_cnode = Node(Unit(identifier=(3,), position=[0.1, 0.2, 0.3],
                                 velocity=[1.0, 0.0, 0.0], time_stamp=Time.from_float(0.4)), weight=1)
        inactive_cnode = Node(Unit(identifier=(4,), position=[0.5, 0.6, 0.7]), weight=1)
        out_state = self._event_handler.send_out_state([active_cnode], [inactive_cnode])
        random_mock.assert_not_called()
        self.assertEqual(len(out_state), 2)
        first_cnode = out_state[0]
        self.assertIsNone(first_cnode.parent)
        self.assertEqual(first_cnode.children, [])
        self.assertEqual(first_cnode.value.identifier, (3,))
        self.assertAlmostEqualSequence(first_cnode.value.position, [0.4, 0.2, 0.3], places=13)
        self.assertEqual(first_cnode.weight, 1)
        self.assertIsNone(first_cnode.value.velocity)
        self.assertIsNone(first_cnode.value.time_stamp)
        self.assertIsNone(first_cnode.value.charge)
        second_cnode = out_state[1]
        self.assertIsNone(second_cnode.parent)
        self.assertEqual(second_cnode.children, [])
        self.assertEqual(second_cnode.value.identifier, (4,))
        self.assertAlmostEqualSequence(second_cnode.value.position, [0.5, 0.6, 0.7], places=13)
        self.assertEqual(second_cnode.weight, 1)
        self.assertEqual(second_cnode.value.velocity, [0.0, 1.0, 0.0])
        self.assertAlmostEqual(second_cnode.value.time_stamp, Time.from_float(0.7), places=13)
        self.assertIsNone(second_cnode.value.charge)

        # Second iteration.
        active_cnode = Node(Unit(identifier=(5,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.0, -0.5, 0.0], time_stamp=Time.from_float(0.7)), weight=1)
        random_mock.return_value = 6
        event_time, new_active_identifiers = self._event_handler.send_event_time([active_cnode])
        self.assertAlmostEqual(event_time, Time.from_float(1.4), places=13)
        random_mock.assert_called_once_with(0, 9)
        random_mock.reset_mock()
        # First list gets unpacked by mediator
        self.assertEqual(new_active_identifiers, [[(6,)]])

        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.0, -0.5, 0.0], time_stamp=Time.from_float(0.9)), weight=1)
        inactive_cnode = Node(Unit(identifier=(6,), position=[0.5, 0.6, 0.7]), weight=1)
        out_state = self._event_handler.send_out_state([active_cnode], [inactive_cnode])
        random_mock.assert_not_called()
        self.assertEqual(len(out_state), 2)
        first_cnode = out_state[0]
        self.assertIsNone(first_cnode.parent)
        self.assertEqual(first_cnode.children, [])
        self.assertEqual(first_cnode.value.identifier, (0,))
        self.assertAlmostEqualSequence(first_cnode.value.position, [0.1, 0.95, 0.3], places=13)
        self.assertEqual(first_cnode.weight, 1)
        self.assertIsNone(first_cnode.value.velocity)
        self.assertIsNone(first_cnode.value.time_stamp)
        self.assertIsNone(first_cnode.value.charge)
        second_cnode = out_state[1]
        self.assertIsNone(second_cnode.parent)
        self.assertEqual(second_cnode.children, [])
        self.assertEqual(second_cnode.value.identifier, (6,))
        self.assertAlmostEqualSequence(second_cnode.value.position, [0.5, 0.6, 0.7], places=13)
        self.assertEqual(second_cnode.weight, 1)
        self.assertEqual(second_cnode.value.velocity, [0.0, 0.0, -0.5])
        self.assertAlmostEqual(second_cnode.value.time_stamp, Time.from_float(1.4), places=13)
        self.assertIsNone(second_cnode.value.charge)

        # Third iteration.
        active_cnode = Node(Unit(identifier=(9,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.0, 0.0, 2.3], time_stamp=Time.from_float(1.7)), weight=1)
        random_mock.return_value = 2
        event_time, new_active_identifiers = self._event_handler.send_event_time([active_cnode])
        self.assertAlmostEqual(event_time, Time.from_float(2.1), places=13)
        random_mock.assert_called_once_with(0, 9)
        random_mock.reset_mock()
        # First list gets unpacked by mediator
        self.assertEqual(new_active_identifiers, [[(2,)]])

        active_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.0, 0.0, 2.3], time_stamp=Time.from_float(2.0)), weight=1)
        inactive_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                   velocity=[0.0, 0.0, 2.3], time_stamp=Time.from_float(2.0)), weight=1)
        out_state = self._event_handler.send_out_state([active_cnode], [inactive_cnode])
        random_mock.assert_not_called()
        self.assertEqual(len(out_state), 1)
        first_cnode = out_state[0]
        self.assertIsNone(first_cnode.parent)
        self.assertEqual(first_cnode.children, [])
        self.assertEqual(first_cnode.value.identifier, (2,))
        self.assertAlmostEqualSequence(first_cnode.value.position, [0.1, 0.2, 0.53], places=13)
        self.assertEqual(first_cnode.weight, 1)
        self.assertEqual(first_cnode.value.velocity, [2.3, 0.0, 0.0])
        self.assertAlmostEqual(first_cnode.value.time_stamp, Time.from_float(2.1), places=13)
        self.assertIsNone(first_cnode.value.charge)

    @mock.patch(
        "jellyfysh.event_handler.single_independent_active_periodic_direction_end_of_chain_event_handler.randint")
    def test_leaf_unit_composite_objects(self, random_mock):
        self._setUpCompositeObjects()

        # First iteration.
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(0.5)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.5)), weight=0.5))
        random_mock.side_effect = [4, 0]
        event_time, new_active_identifiers = self._event_handler.send_event_time([active_cnode])
        self.assertAlmostEqual(event_time, Time.from_float(0.7), places=13)
        random_mock.assert_has_calls([mock.call(0, 9), mock.call(0, 1)])
        random_mock.reset_mock()
        # First list gets unpacked by mediator
        self.assertEqual(new_active_identifiers, [[(4, 0)]])

        active_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(0.7)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.7)), weight=0.5))
        inactive_cnode = Node(Unit(identifier=(4,), position=[0.5, 0.6, 0.7]), weight=1)
        inactive_cnode.add_child(Node(Unit(identifier=(4, 0), position=[0.4, 0.5, 0.6], charge={"charge": -1.0}),
                                      weight=0.5))
        out_state = self._event_handler.send_out_state([active_cnode], [inactive_cnode])
        random_mock.assert_not_called()
        self.assertEqual(len(out_state), 2)
        first_cnode = out_state[0]
        self.assertIsNone(first_cnode.parent)
        self.assertEqual(len(first_cnode.children), 1)
        self.assertEqual(first_cnode.value.identifier, (2,))
        self.assertAlmostEqualSequence(first_cnode.value.position, [0.1, 0.2, 0.3], places=13)
        self.assertEqual(first_cnode.weight, 1)
        self.assertIsNone(first_cnode.value.velocity)
        self.assertIsNone(first_cnode.value.time_stamp)
        self.assertIsNone(first_cnode.value.charge)
        first_cnode_child = first_cnode.children[0]
        self.assertIs(first_cnode_child.parent, first_cnode)
        self.assertEqual(first_cnode_child.children, [])
        self.assertEqual(first_cnode_child.value.identifier, (2, 1))
        self.assertAlmostEqualSequence(first_cnode_child.value.position, [0.7, 0.8, 0.9], places=13)
        self.assertEqual(first_cnode_child.weight, 0.5)
        self.assertIsNone(first_cnode_child.value.velocity)
        self.assertIsNone(first_cnode_child.value.time_stamp)
        self.assertEqual(first_cnode_child.value.charge, {"charge": 1.0})
        second_cnode = out_state[1]
        self.assertIsNone(second_cnode.parent)
        self.assertEqual(len(second_cnode.children), 1)
        self.assertEqual(second_cnode.value.identifier, (4,))
        self.assertAlmostEqualSequence(second_cnode.value.position, [0.5, 0.6, 0.7], places=13)
        self.assertEqual(second_cnode.weight, 1)
        self.assertEqual(second_cnode.value.velocity, [0.0, 0.25, 0.0])
        self.assertAlmostEqual(second_cnode.value.time_stamp, Time.from_float(0.7), places=13)
        self.assertIsNone(second_cnode.value.charge)
        second_cnode_child = second_cnode.children[0]
        self.assertIs(second_cnode_child.parent, second_cnode)
        self.assertEqual(second_cnode_child.children, [])
        self.assertEqual(second_cnode_child.value.identifier, (4, 0))
        self.assertAlmostEqualSequence(second_cnode_child.value.position, [0.4, 0.5, 0.6], places=13)
        self.assertEqual(second_cnode_child.weight, 0.5)
        self.assertEqual(second_cnode_child.value.velocity, [0.0, 0.5, 0.0])
        self.assertAlmostEqual(second_cnode_child.value.time_stamp, Time.from_float(0.7), places=13)
        self.assertEqual(second_cnode_child.value.charge, {"charge": -1.0})

        # Second iteration.
        active_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(1.4)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(1.4)), weight=0.5))
        random_mock.side_effect = [3, 1]
        event_time, new_active_identifiers = self._event_handler.send_event_time([active_cnode])
        self.assertAlmostEqual(event_time, Time.from_float(1.4), places=13)
        random_mock.assert_has_calls([mock.call(0, 9), mock.call(0, 1)])
        random_mock.reset_mock()
        # First list gets unpacked by mediator
        self.assertEqual(new_active_identifiers, [[(3, 1)]])

        active_cnode = Node(Unit(identifier=(3,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.0, 1.0, 0.0], time_stamp=Time.from_float(1.0)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(3, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.0, 2.0, 0.0], time_stamp=Time.from_float(1.0)), weight=0.5))
        inactive_cnode = Node(Unit(identifier=(3,), position=[0.1, 0.2, 0.3], velocity=[0.0, 1.0, 0.0],
                                   time_stamp=Time.from_float(1.0)), weight=1)
        inactive_cnode.add_child(Node(Unit(identifier=(3, 1), position=[0.4, 0.5, 0.6], charge={"charge": -1.0}),
                                      weight=0.5))
        out_state = self._event_handler.send_out_state([active_cnode], [inactive_cnode])
        random_mock.assert_not_called()
        self.assertEqual(len(out_state), 2)
        first_cnode = out_state[0]
        self.assertIsNone(first_cnode.parent)
        self.assertEqual(len(first_cnode.children), 1)
        self.assertEqual(first_cnode.value.identifier, (3,))
        self.assertAlmostEqualSequence(first_cnode.value.position, [0.1, 0.6, 0.3], places=13)
        self.assertEqual(first_cnode.weight, 1)
        self.assertEqual(first_cnode.value.velocity, [0.0, 0.0, 1.0])
        self.assertAlmostEqual(first_cnode.value.time_stamp, Time.from_float(1.4), places=13)
        self.assertIsNone(first_cnode.value.charge)
        first_cnode_child = first_cnode.children[0]
        self.assertIs(first_cnode_child.parent, first_cnode)
        self.assertEqual(first_cnode_child.children, [])
        self.assertEqual(first_cnode_child.value.identifier, (3, 0))
        self.assertAlmostEqualSequence(first_cnode_child.value.position, [0.7, 0.6, 0.9], places=13)
        self.assertEqual(first_cnode_child.weight, 0.5)
        self.assertIsNone(first_cnode_child.value.velocity)
        self.assertIsNone(first_cnode_child.value.time_stamp)
        self.assertEqual(first_cnode_child.value.charge, {"charge": 1.0})
        second_cnode = out_state[1]
        self.assertIsNone(second_cnode.parent)
        self.assertEqual(len(second_cnode.children), 1)
        self.assertEqual(second_cnode.value.identifier, (3,))
        self.assertAlmostEqualSequence(second_cnode.value.position, [0.1, 0.6, 0.3], places=13)
        self.assertEqual(second_cnode.weight, 1)
        self.assertEqual(second_cnode.value.velocity, [0.0, 0.0, 1.0])
        self.assertAlmostEqual(second_cnode.value.time_stamp, Time.from_float(1.4), places=13)
        self.assertIsNone(second_cnode.value.charge)
        second_cnode_child = second_cnode.children[0]
        self.assertIs(second_cnode_child.parent, second_cnode)
        self.assertEqual(second_cnode_child.children, [])
        self.assertEqual(second_cnode_child.value.identifier, (3, 1))
        self.assertAlmostEqualSequence(second_cnode_child.value.position, [0.4, 0.5, 0.6], places=13)
        self.assertEqual(second_cnode_child.weight, 0.5)
        self.assertEqual(second_cnode_child.value.velocity, [0.0, 0.0, 2.0])
        self.assertAlmostEqual(second_cnode_child.value.time_stamp, Time.from_float(1.4), places=13)
        self.assertEqual(second_cnode_child.value.charge, {"charge": -1.0})

        # Third iteration.
        active_cnode = Node(Unit(identifier=(7,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.0, 0.0, -0.5], time_stamp=Time.from_float(2.0)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(7, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.0, 0.0, -1.0], time_stamp=Time.from_float(2.0)), weight=0.5))
        random_mock.side_effect = [5, 0]
        event_time, new_active_identifiers = self._event_handler.send_event_time([active_cnode])
        self.assertAlmostEqual(event_time, Time.from_float(2.1), places=13)
        random_mock.assert_has_calls([mock.call(0, 9), mock.call(0, 1)])
        random_mock.reset_mock()
        # First list gets unpacked by mediator
        self.assertEqual(new_active_identifiers, [[(5, 0)]])

        active_cnode = Node(Unit(identifier=(5,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.0, 0.0, -0.5], time_stamp=Time.from_float(1.0)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(5, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.0, 0.0, -1.0], time_stamp=Time.from_float(1.0)), weight=0.5))
        inactive_cnode = Node(Unit(identifier=(5,), position=[0.1, 0.2, 0.3], velocity=[0.0, 0.0, -0.5],
                                   time_stamp=Time.from_float(1.0)), weight=1)
        inactive_cnode.add_child(Node(Unit(identifier=(5, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                      velocity=[0.0, 0.0, -1.0], time_stamp=Time.from_float(1.0)), weight=0.5))
        out_state = self._event_handler.send_out_state([active_cnode], [inactive_cnode])
        random_mock.assert_not_called()
        self.assertEqual(len(out_state), 1)
        first_cnode = out_state[0]
        self.assertIsNone(first_cnode.parent)
        self.assertEqual(len(first_cnode.children), 1)
        self.assertEqual(first_cnode.value.identifier, (5,))
        self.assertAlmostEqualSequence(first_cnode.value.position, [0.1, 0.2, 0.75], places=13)
        self.assertEqual(first_cnode.weight, 1)
        self.assertEqual(first_cnode.value.velocity, [-0.5, 0.0, 0.0])
        self.assertAlmostEqual(first_cnode.value.time_stamp, Time.from_float(2.1), places=13)
        self.assertIsNone(first_cnode.value.charge)
        first_cnode_child = first_cnode.children[0]
        self.assertIs(first_cnode_child.parent, first_cnode)
        self.assertEqual(first_cnode_child.children, [])
        self.assertEqual(first_cnode_child.value.identifier, (5, 0))
        self.assertAlmostEqualSequence(first_cnode_child.value.position, [0.7, 0.8, 0.8], places=13)
        self.assertEqual(first_cnode_child.weight, 0.5)
        self.assertEqual(first_cnode_child.value.velocity, [-1.0, 0.0, 0.0])
        self.assertAlmostEqual(first_cnode_child.value.time_stamp, Time.from_float(2.1), places=13)
        self.assertEqual(first_cnode_child.value.charge, {"charge": 1.0})

    @mock.patch(
        "jellyfysh.event_handler.single_independent_active_periodic_direction_end_of_chain_event_handler.randint")
    def test_root_unit(self, random_mock):
        self._setUpCompositeObjects()

        # First iteration.
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(0, 1), position=[0.4, 0.5, 0.6], charge={"charge": -1.0},
                                         velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        random_mock.side_effect = [1]
        event_time, new_active_identifiers = self._event_handler.send_event_time([active_cnode])
        self.assertAlmostEqual(event_time, Time.from_float(0.7), places=13)
        random_mock.assert_called_once_with(0, 9)
        random_mock.reset_mock()
        # First list gets unpacked by mediator
        self.assertEqual(new_active_identifiers, [[(1,)]])

        active_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                 velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(2, 0), position=[0.0, 0.1, 0.2], charge={"charge": -1.0},
                                         velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        inactive_cnode = Node(Unit(identifier=(1,), position=[0.5, 0.6, 0.7]), weight=1)
        inactive_cnode.add_child(Node(Unit(identifier=(1, 0), position=[0.4, 0.5, 0.6], charge={"charge": -1.0}),
                                      weight=0.5))
        inactive_cnode.add_child(Node(Unit(identifier=(1, 1), position=[0.6, 0.7, 0.8], charge={"charge": 1.0}),
                                      weight=0.5))
        out_state = self._event_handler.send_out_state([active_cnode], [inactive_cnode])
        random_mock.assert_not_called()
        self.assertEqual(len(out_state), 2)
        first_cnode = out_state[0]
        self.assertIsNone(first_cnode.parent)
        self.assertEqual(len(first_cnode.children), 2)
        self.assertEqual(first_cnode.value.identifier, (2,))
        self.assertAlmostEqualSequence(first_cnode.value.position, [0.05, 0.2, 0.3], places=13)
        self.assertEqual(first_cnode.weight, 1)
        self.assertIsNone(first_cnode.value.velocity)
        self.assertIsNone(first_cnode.value.time_stamp)
        self.assertIsNone(first_cnode.value.charge)
        first_cnode_child_one = first_cnode.children[0]
        self.assertIs(first_cnode_child_one.parent, first_cnode)
        self.assertEqual(first_cnode_child_one.children, [])
        self.assertEqual(first_cnode_child_one.value.identifier, (2, 0))
        self.assertAlmostEqualSequence(first_cnode_child_one.value.position, [0.95, 0.1, 0.2], places=13)
        self.assertEqual(first_cnode_child_one.weight, 0.5)
        self.assertIsNone(first_cnode_child_one.value.velocity)
        self.assertIsNone(first_cnode_child_one.value.time_stamp)
        self.assertEqual(first_cnode_child_one.value.charge, {"charge": -1.0})
        first_cnode_child_two = first_cnode.children[1]
        self.assertIs(first_cnode_child_two.parent, first_cnode)
        self.assertEqual(first_cnode_child_two.children, [])
        self.assertEqual(first_cnode_child_two.value.identifier, (2, 1))
        self.assertAlmostEqualSequence(first_cnode_child_two.value.position, [0.65, 0.8, 0.9], places=13)
        self.assertEqual(first_cnode_child_two.weight, 0.5)
        self.assertIsNone(first_cnode_child_two.value.velocity)
        self.assertIsNone(first_cnode_child_two.value.time_stamp)
        self.assertEqual(first_cnode_child_two.value.charge, {"charge": 1.0})
        second_cnode = out_state[1]
        self.assertIsNone(second_cnode.parent)
        self.assertEqual(len(second_cnode.children), 2)
        self.assertEqual(second_cnode.value.identifier, (1,))
        self.assertAlmostEqualSequence(second_cnode.value.position, [0.5, 0.6, 0.7], places=13)
        self.assertEqual(second_cnode.weight, 1)
        self.assertEqual(second_cnode.value.velocity, [0.0, -0.5, 0.0])
        self.assertAlmostEqual(second_cnode.value.time_stamp, Time.from_float(0.7), places=13)
        self.assertIsNone(second_cnode.value.charge)
        second_cnode_child_one = second_cnode.children[0]
        self.assertIs(second_cnode_child_one.parent, second_cnode)
        self.assertEqual(second_cnode_child_one.children, [])
        self.assertEqual(second_cnode_child_one.value.identifier, (1, 0))
        self.assertAlmostEqualSequence(second_cnode_child_one.value.position, [0.4, 0.5, 0.6], places=13)
        self.assertEqual(second_cnode_child_one.weight, 0.5)
        self.assertEqual(second_cnode_child_one.value.velocity, [0.0, -0.5, 0.0])
        self.assertAlmostEqual(second_cnode_child_one.value.time_stamp, Time.from_float(0.7), places=13)
        self.assertEqual(second_cnode_child_one.value.charge, {"charge": -1.0})
        second_cnode_child_two = second_cnode.children[1]
        self.assertIs(second_cnode_child_two.parent, second_cnode)
        self.assertEqual(second_cnode_child_two.children, [])
        self.assertEqual(second_cnode_child_two.value.identifier, (1, 1))
        self.assertAlmostEqualSequence(second_cnode_child_two.value.position, [0.6, 0.7, 0.8], places=13)
        self.assertEqual(second_cnode_child_two.weight, 0.5)
        self.assertEqual(second_cnode_child_two.value.velocity, [0.0, -0.5, 0.0])
        self.assertAlmostEqual(second_cnode_child_two.value.time_stamp, Time.from_float(0.7), places=13)
        self.assertEqual(second_cnode_child_two.value.charge, {"charge": 1.0})

        # Second iteration.
        active_cnode = Node(Unit(identifier=(5,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.0, 1.1, 0.0], time_stamp=Time.from_float(1.4)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(5, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.0, 1.1, 0.0], time_stamp=Time.from_float(1.4)), weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(5, 1), position=[0.4, 0.5, 0.6], charge={"charge": -1.0},
                                         velocity=[0.0, 1.1, 0.0], time_stamp=Time.from_float(1.4)), weight=0.5))
        random_mock.side_effect = [0]
        event_time, new_active_identifiers = self._event_handler.send_event_time([active_cnode])
        self.assertAlmostEqual(event_time, Time.from_float(1.4), places=13)
        random_mock.assert_called_once_with(0, 9)
        random_mock.reset_mock()
        # First list gets unpacked by mediator
        self.assertEqual(new_active_identifiers, [[(0,)]])

        active_cnode = Node(Unit(identifier=(6,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.0, 1.1, 0.0], time_stamp=Time.from_float(1.4)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(6, 0), position=[0.0, 0.1, 0.2], charge={"charge": -1.0},
                                         velocity=[0.0, 1.1, 0.0], time_stamp=Time.from_float(1.4)), weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(6, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.0, 1.1, 0.0], time_stamp=Time.from_float(1.4)), weight=0.5))
        inactive_cnode = Node(Unit(identifier=(0,), position=[0.5, 0.6, 0.7]), weight=1)
        inactive_cnode.add_child(Node(Unit(identifier=(0, 0), position=[0.4, 0.5, 0.6], charge={"charge": -1.0}),
                                      weight=0.5))
        inactive_cnode.add_child(Node(Unit(identifier=(0, 1), position=[0.6, 0.7, 0.8], charge={"charge": 1.0}),
                                      weight=0.5))
        out_state = self._event_handler.send_out_state([active_cnode], [inactive_cnode])
        random_mock.assert_not_called()
        self.assertEqual(len(out_state), 2)
        first_cnode = out_state[0]
        self.assertIsNone(first_cnode.parent)
        self.assertEqual(len(first_cnode.children), 2)
        self.assertEqual(first_cnode.value.identifier, (6,))
        self.assertAlmostEqualSequence(first_cnode.value.position, [0.1, 0.2, 0.3], places=13)
        self.assertEqual(first_cnode.weight, 1)
        self.assertIsNone(first_cnode.value.velocity)
        self.assertIsNone(first_cnode.value.time_stamp)
        self.assertIsNone(first_cnode.value.charge)
        first_cnode_child_one = first_cnode.children[0]
        self.assertIs(first_cnode_child_one.parent, first_cnode)
        self.assertEqual(first_cnode_child_one.children, [])
        self.assertEqual(first_cnode_child_one.value.identifier, (6, 0))
        self.assertAlmostEqualSequence(first_cnode_child_one.value.position, [0.0, 0.1, 0.2], places=13)
        self.assertEqual(first_cnode_child_one.weight, 0.5)
        self.assertIsNone(first_cnode_child_one.value.velocity)
        self.assertIsNone(first_cnode_child_one.value.time_stamp)
        self.assertEqual(first_cnode_child_one.value.charge, {"charge": -1.0})
        first_cnode_child_two = first_cnode.children[1]
        self.assertIs(first_cnode_child_two.parent, first_cnode)
        self.assertEqual(first_cnode_child_two.children, [])
        self.assertEqual(first_cnode_child_two.value.identifier, (6, 1))
        self.assertAlmostEqualSequence(first_cnode_child_two.value.position, [0.7, 0.8, 0.9], places=13)
        self.assertEqual(first_cnode_child_two.weight, 0.5)
        self.assertIsNone(first_cnode_child_two.value.velocity)
        self.assertIsNone(first_cnode_child_two.value.time_stamp)
        self.assertEqual(first_cnode_child_two.value.charge, {"charge": 1.0})
        second_cnode = out_state[1]
        self.assertIsNone(second_cnode.parent)
        self.assertEqual(len(second_cnode.children), 2)
        self.assertEqual(second_cnode.value.identifier, (0,))
        self.assertAlmostEqualSequence(second_cnode.value.position, [0.5, 0.6, 0.7], places=13)
        self.assertEqual(second_cnode.weight, 1)
        self.assertEqual(second_cnode.value.velocity, [0.0, 0.0, 1.1])
        self.assertAlmostEqual(second_cnode.value.time_stamp, Time.from_float(1.4), places=13)
        self.assertIsNone(second_cnode.value.charge)
        second_cnode_child_one = second_cnode.children[0]
        self.assertIs(second_cnode_child_one.parent, second_cnode)
        self.assertEqual(second_cnode_child_one.children, [])
        self.assertEqual(second_cnode_child_one.value.identifier, (0, 0))
        self.assertAlmostEqualSequence(second_cnode_child_one.value.position, [0.4, 0.5, 0.6], places=13)
        self.assertEqual(second_cnode_child_one.weight, 0.5)
        self.assertEqual(second_cnode_child_one.value.velocity, [0.0, 0.0, 1.1])
        self.assertAlmostEqual(second_cnode_child_one.value.time_stamp, Time.from_float(1.4), places=13)
        self.assertEqual(second_cnode_child_one.value.charge, {"charge": -1.0})
        second_cnode_child_two = second_cnode.children[1]
        self.assertIs(second_cnode_child_two.parent, second_cnode)
        self.assertEqual(second_cnode_child_two.children, [])
        self.assertEqual(second_cnode_child_two.value.identifier, (0, 1))
        self.assertAlmostEqualSequence(second_cnode_child_two.value.position, [0.6, 0.7, 0.8], places=13)
        self.assertEqual(second_cnode_child_two.weight, 0.5)
        self.assertEqual(second_cnode_child_two.value.velocity, [0.0, 0.0, 1.1])
        self.assertAlmostEqual(second_cnode_child_two.value.time_stamp, Time.from_float(1.4), places=13)
        self.assertEqual(second_cnode_child_two.value.charge, {"charge": 1.0})

        # Third iteration.
        active_cnode = Node(Unit(identifier=(3,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.0, 0.0, 2.0], time_stamp=Time.from_float(1.4)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(3, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.0, 0.0, 2.0], time_stamp=Time.from_float(1.4)), weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(3, 1), position=[0.4, 0.5, 0.6], charge={"charge": -1.0},
                                         velocity=[0.0, 0.0, 2.0], time_stamp=Time.from_float(1.4)), weight=0.5))
        random_mock.side_effect = [9]
        event_time, new_active_identifiers = self._event_handler.send_event_time([active_cnode])
        self.assertAlmostEqual(event_time, Time.from_float(2.1), places=13)
        random_mock.assert_called_once_with(0, 9)
        random_mock.reset_mock()
        # First list gets unpacked by mediator
        self.assertEqual(new_active_identifiers, [[(9,)]])

        active_cnode = Node(Unit(identifier=(9,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.0, 0.0, 2.0], time_stamp=Time.from_float(1.4)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(9, 0), position=[0.0, 0.1, 0.2], charge={"charge": -1.0},
                                         velocity=[0.0, 0.0, 2.0], time_stamp=Time.from_float(1.4)), weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(9, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.0, 0.0, 2.0], time_stamp=Time.from_float(1.4)), weight=0.5))
        inactive_cnode = Node(Unit(identifier=(9,), position=[0.1, 0.2, 0.3],
                                   velocity=[0.0, 0.0, 2.0], time_stamp=Time.from_float(1.4)), weight=1)
        inactive_cnode.add_child(Node(Unit(identifier=(9, 0), position=[0.0, 0.1, 0.2], charge={"charge": -1.0},
                                           velocity=[0.0, 0.0, 2.0], time_stamp=Time.from_float(1.4)), weight=0.5))
        inactive_cnode.add_child(Node(Unit(identifier=(9, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                           velocity=[0.0, 0.0, 2.0], time_stamp=Time.from_float(1.4)), weight=0.5))
        out_state = self._event_handler.send_out_state([active_cnode], [inactive_cnode])
        random_mock.assert_not_called()
        self.assertEqual(len(out_state), 1)
        first_cnode = out_state[0]
        self.assertIsNone(first_cnode.parent)
        self.assertEqual(len(first_cnode.children), 2)
        self.assertEqual(first_cnode.value.identifier, (9,))
        self.assertAlmostEqualSequence(first_cnode.value.position, [0.1, 0.2, 0.7], places=13)
        self.assertEqual(first_cnode.weight, 1)
        self.assertEqual(first_cnode.value.velocity, [2.0, 0.0, 0.0])
        self.assertAlmostEqual(first_cnode.value.time_stamp, Time.from_float(2.1), places=13)
        self.assertIsNone(first_cnode.value.charge)
        first_cnode_child_one = first_cnode.children[0]
        self.assertIs(first_cnode_child_one.parent, first_cnode)
        self.assertEqual(first_cnode_child_one.children, [])
        self.assertEqual(first_cnode_child_one.value.identifier, (9, 0))
        self.assertAlmostEqualSequence(first_cnode_child_one.value.position, [0.0, 0.1, 0.6], places=13)
        self.assertEqual(first_cnode_child_one.weight, 0.5)
        self.assertEqual(first_cnode_child_one.value.velocity, [2.0, 0.0, 0.0])
        self.assertAlmostEqual(first_cnode_child_one.value.time_stamp, Time.from_float(2.1), places=13)
        self.assertEqual(first_cnode_child_one.value.charge, {"charge": -1.0})
        first_cnode_child_two = first_cnode.children[1]
        self.assertIs(first_cnode_child_two.parent, first_cnode)
        self.assertEqual(first_cnode_child_two.children, [])
        self.assertEqual(first_cnode_child_two.value.identifier, (9, 1))
        self.assertAlmostEqualSequence(first_cnode_child_two.value.position, [0.7, 0.8, 0.3], places=13)
        self.assertEqual(first_cnode_child_two.weight, 0.5)
        self.assertEqual(first_cnode_child_two.value.velocity, [2.0, 0.0, 0.0])
        self.assertAlmostEqual(first_cnode_child_two.value.time_stamp, Time.from_float(2.1), places=13)
        self.assertEqual(first_cnode_child_two.value.charge, {"charge": 1.0})

    def test_send_event_time_too_small_time_stamp_leaf_unit_no_composite_objects_raises_error(self):
        self._setUpNoCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[1.0, 0.0, 0.0], time_stamp=Time.from_float(0.0)), weight=1)
        self._event_handler.send_event_time([active_cnode])
        active_cnode = Node(Unit(identifier=(3,), position=[0.1, 0.2, 0.3],
                                 velocity=[1.0, 0.0, 0.0], time_stamp=Time.from_float(0.4)), weight=1)
        inactive_cnode = Node(Unit(identifier=(4,), position=[0.5, 0.6, 0.7]), weight=1)
        self._event_handler.send_out_state([active_cnode], [inactive_cnode])
        # Time stamp has to be between 0.7 and 1.4.
        active_cnode = Node(Unit(identifier=(5,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.0, -0.5, 0.0], time_stamp=Time.from_float(0.7 - 1.0e-13)), weight=1)
        with self.assertRaises(AssertionError):
            self._event_handler.send_event_time([active_cnode])

    def test_send_event_time_too_large_time_stamp_leaf_unit_no_composite_objects_raises_error(self):
        self._setUpNoCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[1.0, 0.0, 0.0], time_stamp=Time.from_float(0.0)), weight=1)
        self._event_handler.send_event_time([active_cnode])
        active_cnode = Node(Unit(identifier=(3,), position=[0.1, 0.2, 0.3],
                                 velocity=[1.0, 0.0, 0.0], time_stamp=Time.from_float(0.4)), weight=1)
        inactive_cnode = Node(Unit(identifier=(4,), position=[0.5, 0.6, 0.7]), weight=1)
        self._event_handler.send_out_state([active_cnode], [inactive_cnode])
        # Time stamp has to be between 0.7 and 1.4.
        active_cnode = Node(Unit(identifier=(5,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.0, -0.5, 0.0], time_stamp=Time.from_float(1.4 + 1.0e-13)), weight=1)
        with self.assertRaises(AssertionError):
            self._event_handler.send_event_time([active_cnode])

    def test_send_event_time_too_small_time_stamp_leaf_unit_composite_objects_raises_error(self):
        self._setUpCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(0.5)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.5)), weight=0.5))
        self._event_handler.send_event_time([active_cnode])
        active_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(0.7)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.7)), weight=0.5))
        inactive_cnode = Node(Unit(identifier=(4,), position=[0.5, 0.6, 0.7]), weight=1)
        inactive_cnode.add_child(Node(Unit(identifier=(4, 0), position=[0.4, 0.5, 0.6], charge={"charge": -1.0}),
                                      weight=0.5))
        self._event_handler.send_out_state([active_cnode], [inactive_cnode])
        # Time stamp has to be between 0.7 and 1.4.
        active_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(0.7 - 1.0e-13)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.7 - 1.0e-13)),
                                    weight=0.5))
        with self.assertRaises(AssertionError):
            self._event_handler.send_event_time([active_cnode])

    def test_send_event_time_too_large_time_stamp_leaf_unit_composite_objects_raises_error(self):
        self._setUpCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(0.5)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.5)), weight=0.5))
        self._event_handler.send_event_time([active_cnode])
        active_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(0.7)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.7)), weight=0.5))
        inactive_cnode = Node(Unit(identifier=(4,), position=[0.5, 0.6, 0.7]), weight=1)
        inactive_cnode.add_child(Node(Unit(identifier=(4, 0), position=[0.4, 0.5, 0.6], charge={"charge": -1.0}),
                                      weight=0.5))
        self._event_handler.send_out_state([active_cnode], [inactive_cnode])
        # Time stamp has to be between 0.7 and 1.4.
        active_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(1.4 + 1.0e-13)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(1.4 + 1.0e-13)),
                                    weight=0.5))
        with self.assertRaises(AssertionError):
            self._event_handler.send_event_time([active_cnode])

    def test_send_event_time_too_small_time_stamp_root_unit_raises_error(self):
        self._setUpCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(0, 1), position=[0.4, 0.5, 0.6], charge={"charge": -1.0},
                                         velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        self._event_handler.send_event_time([active_cnode])
        active_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                 velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(2, 0), position=[0.0, 0.1, 0.2], charge={"charge": -1.0},
                                         velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        inactive_cnode = Node(Unit(identifier=(1,), position=[0.5, 0.6, 0.7]), weight=1)
        inactive_cnode.add_child(Node(Unit(identifier=(1, 0), position=[0.4, 0.5, 0.6], charge={"charge": -1.0}),
                                      weight=0.5))
        inactive_cnode.add_child(Node(Unit(identifier=(1, 1), position=[0.6, 0.7, 0.8], charge={"charge": 1.0}),
                                      weight=0.5))
        self._event_handler.send_out_state([active_cnode], [inactive_cnode])
        # Time stamp has to be between 0.7 and 1.4.
        active_cnode = Node(Unit(identifier=(5,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.0, 1.1, 0.0], time_stamp=Time.from_float(0.7 - 1.0e-13)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(5, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.0, 1.1, 0.0], time_stamp=Time.from_float(0.7 - 1.0e-13)),
                                    weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(5, 1), position=[0.4, 0.5, 0.6], charge={"charge": -1.0},
                                         velocity=[0.0, 1.1, 0.0], time_stamp=Time.from_float(0.7 - 1.0e-13)),
                                    weight=0.5))
        with self.assertRaises(AssertionError):
            self._event_handler.send_event_time([active_cnode])

    def test_send_event_time_too_large_time_stamp_root_unit_raises_error(self):
        self._setUpCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(0, 1), position=[0.4, 0.5, 0.6], charge={"charge": -1.0},
                                         velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        self._event_handler.send_event_time([active_cnode])
        active_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                 velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(2, 0), position=[0.0, 0.1, 0.2], charge={"charge": -1.0},
                                         velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        inactive_cnode = Node(Unit(identifier=(1,), position=[0.5, 0.6, 0.7]), weight=1)
        inactive_cnode.add_child(Node(Unit(identifier=(1, 0), position=[0.4, 0.5, 0.6], charge={"charge": -1.0}),
                                      weight=0.5))
        inactive_cnode.add_child(Node(Unit(identifier=(1, 1), position=[0.6, 0.7, 0.8], charge={"charge": 1.0}),
                                      weight=0.5))
        self._event_handler.send_out_state([active_cnode], [inactive_cnode])
        # Time stamp has to be between 0.7 and 1.4.
        active_cnode = Node(Unit(identifier=(5,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.0, 1.1, 0.0], time_stamp=Time.from_float(1.4 + 1.0e-13)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(5, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.0, 1.1, 0.0], time_stamp=Time.from_float(1.4 + 1.0e-13)),
                                    weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(5, 1), position=[0.4, 0.5, 0.6], charge={"charge": -1.0},
                                         velocity=[0.0, 1.1, 0.0], time_stamp=Time.from_float(1.4 + 1.0e-13)),
                                    weight=0.5))
        with self.assertRaises(AssertionError):
            self._event_handler.send_event_time([active_cnode])

    def test_send_event_time_with_two_leaf_units_no_composite_objects_raises_error(self):
        self._setUpNoCompositeObjects()
        active_cnode_one = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                velocity=[1.0, 0.0, 0.0], time_stamp=Time.from_float(0.0)), weight=1)
        active_cnode_two = Node(Unit(identifier=(3,), position=[0.7, 0.8, 0.9],
                                     velocity=[1.0, 0.0, 0.0], time_stamp=Time.from_float(0.0)), weight=1)
        with self.assertRaises(AssertionError):
            self._event_handler.send_event_time([active_cnode_one, active_cnode_two])

    def test_send_event_time_with_two_leaf_units_composite_objects_raises_error(self):
        self._setUpCompositeObjects()
        active_cnode_one = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                     velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(0.5)), weight=1)
        active_cnode_one.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                             velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.5)), weight=0.5))
        active_cnode_two = Node(Unit(identifier=(1,), position=[0.1, 0.2, 0.3],
                                     velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(0.5)), weight=1)
        active_cnode_two.add_child(Node(Unit(identifier=(1, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                             velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.5)), weight=0.5))
        with self.assertRaises(AssertionError):
            self._event_handler.send_event_time([active_cnode_one, active_cnode_two])

    def test_send_event_time_with_two_root_units_raises_error(self):
        self._setUpCompositeObjects()
        active_cnode_one = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                     velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=1)
        active_cnode_one.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                             velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode_one.add_child(Node(Unit(identifier=(0, 1), position=[0.4, 0.5, 0.6], charge={"charge": -1.0},
                                             velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode_two = Node(Unit(identifier=(1,), position=[0.1, 0.2, 0.3],
                                     velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=1)
        active_cnode_two.add_child(Node(Unit(identifier=(1, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                             velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode_two.add_child(Node(Unit(identifier=(1, 1), position=[0.4, 0.5, 0.6], charge={"charge": -1.0},
                                             velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        with self.assertRaises(AssertionError):
            self._event_handler.send_event_time([active_cnode_one, active_cnode_two])

    def test_send_out_state_with_two_leaf_units_no_composite_objects_raises_error(self):
        self._setUpNoCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[1.0, 0.0, 0.0], time_stamp=Time.from_float(0.0)), weight=1)
        self._event_handler.send_event_time([active_cnode])
        active_cnode_one = Node(Unit(identifier=(3,), position=[0.1, 0.2, 0.3],
                                     velocity=[1.0, 0.0, 0.0], time_stamp=Time.from_float(0.4)), weight=1)
        active_cnode_two = Node(Unit(identifier=(5,), position=[0.1, 0.2, 0.3],
                                     velocity=[1.0, 0.0, 0.0], time_stamp=Time.from_float(0.4)), weight=1)
        inactive_cnode_one = Node(Unit(identifier=(4,), position=[0.5, 0.6, 0.7]), weight=1)
        inactive_cnode_two = Node(Unit(identifier=(6,), position=[0.5, 0.6, 0.7]), weight=1)
        with self.assertRaises(AssertionError):
            self._event_handler.send_out_state([active_cnode_one, active_cnode_two], [inactive_cnode_one])
        with self.assertRaises(AssertionError):
            self._event_handler.send_out_state([active_cnode_one], [inactive_cnode_one, inactive_cnode_two])
        with self.assertRaises(AssertionError):
            self._event_handler.send_out_state([active_cnode_one, active_cnode_two],
                                               [inactive_cnode_one, inactive_cnode_two])

    def test_send_out_state_with_two_leaf_units_composite_objects_raises_error(self):
        self._setUpCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(0.5)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.5)), weight=0.5))
        self._event_handler.send_event_time([active_cnode])
        active_cnode_one = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                     velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(0.7)), weight=1)
        active_cnode_one.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                             velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.7)), weight=0.5))
        active_cnode_two = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                     velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(0.7)), weight=1)
        active_cnode_two.add_child(Node(Unit(identifier=(2, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                             velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.7)), weight=0.5))
        inactive_cnode_one = Node(Unit(identifier=(4,), position=[0.5, 0.6, 0.7]), weight=1)
        inactive_cnode_one.add_child(Node(Unit(identifier=(4, 0), position=[0.4, 0.5, 0.6], charge={"charge": -1.0}),
                                          weight=0.5))
        inactive_cnode_two = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                       velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(0.7)), weight=1)
        inactive_cnode_two.add_child(Node(Unit(identifier=(2, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                               velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.7)), weight=0.5))
        with self.assertRaises(AssertionError):
            self._event_handler.send_out_state([active_cnode_one, active_cnode_two], [inactive_cnode_one])
        with self.assertRaises(AssertionError):
            self._event_handler.send_out_state([active_cnode_one], [inactive_cnode_one, inactive_cnode_two])
        with self.assertRaises(AssertionError):
            self._event_handler.send_out_state([active_cnode_one, active_cnode_two],
                                               [inactive_cnode_one, inactive_cnode_two])

    def test_send_out_state_with_two_root_units_composite_objects_raises_error(self):
        self._setUpCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(0, 1), position=[0.4, 0.5, 0.6], charge={"charge": -1.0},
                                         velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        self._event_handler.send_event_time([active_cnode])
        active_cnode_one = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                     velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=1)
        active_cnode_one.add_child(Node(Unit(identifier=(2, 0), position=[0.0, 0.1, 0.2], charge={"charge": -1.0},
                                             velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode_one.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                             velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode_two = Node(Unit(identifier=(5,), position=[0.1, 0.2, 0.3],
                                     velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=1)
        active_cnode_two.add_child(Node(Unit(identifier=(5, 0), position=[0.0, 0.1, 0.2], charge={"charge": -1.0},
                                             velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode_two.add_child(Node(Unit(identifier=(5, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                             velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        inactive_cnode_one = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                       velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=1)
        inactive_cnode_one.add_child(Node(Unit(identifier=(2, 0), position=[0.0, 0.1, 0.2], charge={"charge": -1.0},
                                               velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        inactive_cnode_one.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                               velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        inactive_cnode_two = Node(Unit(identifier=(1,), position=[0.5, 0.6, 0.7]), weight=1)
        inactive_cnode_two.add_child(Node(Unit(identifier=(1, 0), position=[0.4, 0.5, 0.6], charge={"charge": -1.0}),
                                          weight=0.5))
        inactive_cnode_two.add_child(Node(Unit(identifier=(1, 1), position=[0.6, 0.7, 0.8], charge={"charge": 1.0}),
                                          weight=0.5))
        with self.assertRaises(AssertionError):
            self._event_handler.send_out_state([active_cnode_one, active_cnode_two], [inactive_cnode_one])
        with self.assertRaises(AssertionError):
            self._event_handler.send_out_state([active_cnode_one], [inactive_cnode_one, inactive_cnode_two])
        with self.assertRaises(AssertionError):
            self._event_handler.send_out_state([active_cnode_one, active_cnode_two],
                                               [inactive_cnode_one, inactive_cnode_two])

    def test_more_than_one_velocity_component_raises_error_leaf_unit_no_composite_objects(self):
        self._setUpNoCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[1.0, 0.5, 0.0], time_stamp=Time.from_float(0.0)), weight=1)
        self._event_handler.send_event_time([active_cnode])
        active_cnode = Node(Unit(identifier=(3,), position=[0.1, 0.2, 0.3],
                                 velocity=[1.0, 0.5, 0.0], time_stamp=Time.from_float(0.4)), weight=1)
        inactive_cnode = Node(Unit(identifier=(4,), position=[0.5, 0.6, 0.7]), weight=1)
        with self.assertRaises(AssertionError):
            self._event_handler.send_out_state([active_cnode], [inactive_cnode])

    def test_more_than_one_velocity_component_raises_error_leaf_unit_composite_objects(self):
        self._setUpCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.25, 0.0, 0.3], time_stamp=Time.from_float(0.5)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.5, 0.0, 0.6], time_stamp=Time.from_float(0.5)), weight=0.5))
        self._event_handler.send_event_time([active_cnode])
        active_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.25, 0.0, 0.3], time_stamp=Time.from_float(0.7)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.5, 0.0, 0.6], time_stamp=Time.from_float(0.7)), weight=0.5))
        inactive_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                   velocity=[0.25, 0.0, 0.3], time_stamp=Time.from_float(0.7)), weight=1)
        inactive_cnode.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                           velocity=[0.5, 0.0, 0.6], time_stamp=Time.from_float(0.7)), weight=0.5))
        with self.assertRaises(AssertionError):
            self._event_handler.send_out_state([active_cnode], [inactive_cnode])

    def test_more_than_one_velocity_component_raises_error_root_unit(self):
        self._setUpCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[-0.5, 0.1, 0.0], time_stamp=Time.from_float(0.6)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[-0.5, 0.1, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(0, 1), position=[0.4, 0.5, 0.6], charge={"charge": -1.0},
                                         velocity=[-0.5, 0.1, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        self._event_handler.send_event_time([active_cnode])
        active_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                 velocity=[-0.5, 0.1, 0.0], time_stamp=Time.from_float(0.6)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(2, 0), position=[0.0, 0.1, 0.2], charge={"charge": -1.0},
                                         velocity=[-0.5, 0.1, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[-0.5, 0.1, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        inactive_cnode = Node(Unit(identifier=(1,), position=[0.5, 0.6, 0.7]), weight=1)
        inactive_cnode.add_child(Node(Unit(identifier=(1, 0), position=[0.4, 0.5, 0.6], charge={"charge": -1.0}),
                                      weight=0.5))
        inactive_cnode.add_child(Node(Unit(identifier=(1, 1), position=[0.6, 0.7, 0.8], charge={"charge": 1.0}),
                                      weight=0.5))
        with self.assertRaises(AssertionError):
            self._event_handler.send_out_state([active_cnode], [inactive_cnode])

    def test_send_event_time_with_inactive_leaf_unit_no_composite_objects_raises_error(self):
        self._setUpNoCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3]), weight=1)
        with self.assertRaises(AssertionError):
            self._event_handler.send_event_time([active_cnode])

    def test_send_out_state_with_inactive_leaf_unit_no_composite_objects_raises_error(self):
        self._setUpNoCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[1.0, 0.0, 0.0], time_stamp=Time.from_float(0.0)), weight=1)
        self._event_handler.send_event_time([active_cnode])
        active_cnode = Node(Unit(identifier=(3,), position=[0.1, 0.2, 0.3],
                                 velocity=[1.0, 0.0, 0.0], time_stamp=Time.from_float(0.4)), weight=1)
        inactive_cnode = Node(Unit(identifier=(4,), position=[0.5, 0.6, 0.7]), weight=1)
        with self.assertRaises(AssertionError):
            self._event_handler.send_out_state([inactive_cnode], [active_cnode])

    def test_send_event_time_with_inactive_leaf_unit_composite_objects_raises_error(self):
        self._setUpCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3]), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0}),
                                    weight=0.5))
        with self.assertRaises(AssertionError):
            self._event_handler.send_event_time([active_cnode])

    def test_send_out_state_with_inactive_leaf_unit_composite_objects_raises_error(self):
        self._setUpCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(0.5)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.5)), weight=0.5))
        self._event_handler.send_event_time([active_cnode])
        active_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3]), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0}),
                                    weight=0.5))
        inactive_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3],
                                   velocity=[0.25, 0.0, 0.0], time_stamp=Time.from_float(0.7)), weight=1)
        inactive_cnode.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                           velocity=[0.5, 0.0, 0.0], time_stamp=Time.from_float(0.7)), weight=0.5))
        with self.assertRaises(AssertionError):
            self._event_handler.send_out_state([active_cnode], [inactive_cnode])

    def test_send_event_time_with_inactive_root_unit_raises_error(self):
        self._setUpCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3]), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0}),
                                    weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(0, 1), position=[0.4, 0.5, 0.6], charge={"charge": -1.0}),
                                    weight=0.5))
        with self.assertRaises(AssertionError):
            self._event_handler.send_event_time([active_cnode])

    def test_send_out_state_with_inactive_root_unit_raises_error(self):
        self._setUpCompositeObjects()
        active_cnode = Node(Unit(identifier=(0,), position=[0.1, 0.2, 0.3],
                                 velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(0, 0), position=[0.7, 0.8, 0.9], charge={"charge": 1.0},
                                         velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(0, 1), position=[0.4, 0.5, 0.6], charge={"charge": -1.0},
                                         velocity=[-0.5, 0.0, 0.0], time_stamp=Time.from_float(0.6)), weight=0.5))
        self._event_handler.send_event_time([active_cnode])
        active_cnode = Node(Unit(identifier=(2,), position=[0.1, 0.2, 0.3]), weight=1)
        active_cnode.add_child(Node(Unit(identifier=(2, 0), position=[0.0, 0.1, 0.2], charge={"charge": -1.0}),
                                    weight=0.5))
        active_cnode.add_child(Node(Unit(identifier=(2, 1), position=[0.7, 0.8, 0.9], charge={"charge": 1.0}),
                                    weight=0.5))
        inactive_cnode = Node(Unit(identifier=(1,), position=[0.5, 0.6, 0.7]), weight=1)
        inactive_cnode.add_child(Node(Unit(identifier=(1, 0), position=[0.4, 0.5, 0.6], charge={"charge": -1.0}),
                                      weight=0.5))
        inactive_cnode.add_child(Node(Unit(identifier=(1, 1), position=[0.6, 0.7, 0.8], charge={"charge": 1.0}),
                                      weight=0.5))
        with self.assertRaises(AssertionError):
            self._event_handler.send_out_state([inactive_cnode], [active_cnode])

    def test_chain_time_zero_raises_error(self):
        with self.assertRaises(ConfigurationError):
            SingleIndependentActivePeriodicDirectionEndOfChainEventHandler(chain_time=0.0)

    def test_chain_time_negative_raises_error(self):
        with self.assertRaises(ConfigurationError):
            SingleIndependentActivePeriodicDirectionEndOfChainEventHandler(chain_time=-0.2)


if __name__ == '__main__':
    main()
