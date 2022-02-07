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
"""Module for the SingleActiveCellOccupancy class."""
import logging
from typing import List, Iterable, Sequence, Tuple
from jellyfysh.base.exceptions import ConfigurationError
from jellyfysh.base.logging import log_init_arguments
from jellyfysh.base.node import Node, yield_nodes_on_level_below
import jellyfysh.setting as setting
from jellyfysh.state_handler.tree_state_handler import StateId
from .cell_occupancy import CellOccupancy
from .cell_occupancy.cells import Cells, Cell


class SingleActiveCellOccupancy(CellOccupancy):
    """
    Cell-occupancy system that maps identifiers of the global state onto cells in the underlying cell system.
    This cell-occupancy system can consider at most one relevant active unit (see below for a definition of a relevant
    unit).

    This class is designed to work together with the TreeStateHandler. A global state identifier is then a tuple of
    integers, where the tuple can have different lengths (see StateId in state_handler.tree_state_handler.py). This
    cell-occupancy system has a cell_level attribute that determines the length of the relevant global state identifiers
    that are stored in this internal state. All other global state identifiers are ignored.
    For the TreeStateHandler, both the extracted global state, and the extracted active global state (that are used to
    initialize and update this internal state, respectively) are sequences of branches of cnodes containing units.

    Besides the cell_level attribute, this cell-occupancy system can include a charge to further restrict the relevant
    global state identifiers that are stored in this cell-occupancy system. Here, only global state identifiers of units
    with this charge unequal zero are stored.

    On initialization, this cell-occupancy system receives a maximum number of global state identifiers that can be
    possibly stored for each cell, and which are returned by the __getitem__ method. All additional global state
    identifiers, which would be mapped onto a cell that has reached its maximum number of occupants, are treated as
    surplus identifiers that are generated by the yield_surplus method. Note that it is also possible to choose an
    infinite upper bound on the number of occupants. In this case, there are never any surplus identifiers.

    This cell-occupancy system can track at most one relevant active unit. The identifier of the active unit is not
    stored in the cell-occupancy system itself (i.e., it is not returned by the __getitem__ and yield_surplus methods),
    but it is stored separately so that it can be efficiently generated in the yield_active_cells_method.
    """

    def __init__(self, cells: Cells, cell_level: int, maximum_number_occupants: int = 1, charge: str = None) -> None:
        """
        The constructor of the SingleActiveCellOccupancy class.

        Parameters
        ----------
        cells : activator.internal_state.cell_occupancy.cells.Cells
            The underlying cell system.
        cell_level : int
            The length of the global state identifiers which should be stored in this internal state.
        maximum_number_occupants : int, optional
            The maximum number of allowed occupants per cell. If this number is smaller than or equal to zero, this
            class allows for an infinite number of occupants per cell.
        charge : str or None, optional
            The charge of the unit that must be unequal zero in order for the corresponding identifier to be stored.
            If the charge is None, all global state identifiers with the correct length are stored.

        Raises
        ------
        base.exceptions.ConfigurationError
            If the cell_level corresponds to composite point objects which cannot have a charge but the charge is set.
        """
        log_init_arguments(logging.getLogger(__name__).debug, self.__class__.__name__, cells=cells.__class__.__name__,
                           cell_level=cell_level, maximum_number_occupants=maximum_number_occupants, charge=charge)
        super().__init__(cells, cell_level, maximum_number_occupants)
        if cell_level < setting.number_of_node_levels and charge is not None:
            raise ConfigurationError("Chosen cell level stores composite point objects which cannot have a charge!")
        self._surplus = {}
        self._occupants = {cell: [] for cell in self._cells.yield_cells()}
        self._active_unit_identifier = None
        self._is_relevant_unit = (lambda unit: unit.charge[charge] != 0) if charge is not None else lambda unit: True
        self._active_cell = None

    def initialize(self, extracted_global_state: Sequence[Node]) -> None:
        """
        Initialize the internal state based on the full extracted global state from the tree state handler.

        Extends the initialize method of the InternalState class. Use this method once in the beginning of the run to
        initialize the internal state. Only after a call of this method, other public methods of this class can be
        called without raising an error.

        For the tree state handler, the full extracted global state is a sequence of cnodes of all root nodes that are
        stored in the global state.

        Parameters
        ----------
        extracted_global_state : Sequence[base.node.Node]
            The full extracted global state from the tree state handler.
        """
        super().initialize(extracted_global_state)
        for root_cnode in extracted_global_state:
            for relevant_cnode in yield_nodes_on_level_below(root_cnode, self._cell_level - 1):
                unit = relevant_cnode.value
                if self._is_relevant_unit(unit):
                    cell = self._cells.position_to_cell(unit.position)
                    if (len(self._occupants[cell]) < self._maximum_number_occupants
                            or self._number_occupants_not_bounded):
                        self._occupants[cell].append(unit.identifier)
                    else:
                        self._surplus.setdefault(cell, []).append(unit.identifier)

    def __getitem__(self, internal_state_identifier: Cell) -> List[StateId]:
        """
        Return a list of the stored global state identifiers that are stored for the given cell.

        The number of entries in the list of the global state identifiers that are associated to the given cell is at
        most the maximum number of allowed occupants per cell of this cell-occupancy system. If no global state
        identifier is associated with the given cell, this method returns an empty list.

        If this cell-occupancy system associates more global state identifiers to the given cell than the maximum number
        of allowed occupants, surplus global state identifiers are generated by the yield_surplus method.

        A relevant active global state identifier that is also associated with the given cell is not returned by this
        method.

        Parameters
        ----------
        internal_state_identifier : activator.internal_state.cell_occupancy.cells.Cell
            The cell.

        Returns
        -------
        List[state_handler.tree_state_handler.StateId]
           The global state identifiers associated with the cell.
        """
        return self._occupants[internal_state_identifier]

    def update(self, extracted_active_global_state: Sequence[Node]) -> None:
        """
        Update the internal state based on the extracted active global state.
        
        Use this method to keep the internal state consistent with the global state. For the tree state handler, the
        extracted active global state is a sequence of cnodes of root cnodes where each cnode branch only contains
        active units.

        This method extracts the active units on the cell level of this class. This class assumes that there is only one
        such active unit. If the active unit identifier has changed, this method updates the cell-occupancy system. If
        the active unit has not changed, only the active cell is determined again.

        Parameters
        ----------
        extracted_active_global_state : Sequence[base.node.Node]
            The extracted active global state from the tree state handler.

        Raises
        ------
        AssertionError
            If the extracted active global state does not include exactly one active unit on the cell_level of this
            cell-occupancy system.
        """
        active_units_on_cell_level = [cnode.value for root_cnode in extracted_active_global_state
                                      for cnode in yield_nodes_on_level_below(root_cnode, self.cell_level - 1)]
        assert len(active_units_on_cell_level) == 1
        new_active_unit = active_units_on_cell_level[0]
        if new_active_unit.identifier != self._active_unit_identifier:
            if self._active_unit_identifier is not None:
                if (len(self._occupants[self._active_cell]) < self._maximum_number_occupants
                        or self._number_occupants_not_bounded):
                    self._occupants[self._active_cell].append(self._active_unit_identifier)
                else:
                    self._surplus.setdefault(self._active_cell, []).append(self._active_unit_identifier)

            if self._is_relevant_unit(new_active_unit):
                self._active_cell = self._cells.position_to_cell(new_active_unit.position)
                self._active_unit_identifier = new_active_unit.identifier
                try:
                    self._occupants[self._active_cell].remove(new_active_unit.identifier)
                    # Possibly move identifier from surplus list into occupants list.
                    # Use get because the surplus dictionary might not have active cell key.
                    if not self._surplus.get(self._active_cell, True):
                        self._occupants[self._active_cell].append(self._surplus[self._active_cell].pop())
                except ValueError:
                    # New active unit is in surplus list.
                    self._surplus[self._active_cell].remove(new_active_unit.identifier)
                # Delete surplus list if it is now empty.
                if not self._surplus.get(self._active_cell, True):
                    del self._surplus[self._active_cell]
            else:
                self._active_unit_identifier = None
                self._active_cell = None
        else:
            self._active_cell = self._cells.position_to_cell(new_active_unit.position)

    def yield_surplus(self) -> Iterable[StateId]:
        """
        Generate all surplus identifiers of this cell-occupancy system.

        Surplus global state identifiers are present if the number of global state identifiers associated to any cell
        exceeds the maximum number of allowed occupants per cell. This method generates the surplus global state
        identifiers of all cells.

        A relevant active global state identifier is never generated by this method.

        Yields
        ------
        state_handler.tree_state_handler.StateId
            The surplus global state identifier.
        """
        for value in self._surplus.values():
            yield from value

    def yield_active_cells(self) -> Iterable[Tuple[Cell, StateId]]:
        """
        Generate the cell and the global state identifier of the relevant active unit on the cell level of this
        cell-occupancy system.

        If this cell-occupancy system only stores global state identifiers of units with a given charge, the active unit
        might be None and this method does not generate anything.

        Yields
        ------
        (Cell, StateId)
            The cell, the global state identifier of the active unit.
        """
        if self._active_cell is not None:
            yield self._active_cell, self._active_unit_identifier
