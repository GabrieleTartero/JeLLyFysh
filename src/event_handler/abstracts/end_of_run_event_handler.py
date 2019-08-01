# JeLLFysh - a Python application for all-atom event-chain Monte Carlo - https://github.com/jellyfysh
# Copyright (C) 2019 The JeLLyFysh organization
# (see the AUTHORS file for the full list of authors)
#
# This file is part of JeLLyFysh.
#
# JeLLyFysh is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either > version 3 of the License, or (at your option) any
# later version.
#
# JeLLyFysh is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with JeLLyFysh in the LICENSE file.
# If not, see <https://www.gnu.org/licenses/>.
#
# If you use JeLLyFysh in published work, please cite the following reference (see [Hoellmer2019] in References.bib):
# Philipp Hoellmer, Liang Qin, Michael F. Faulkner, A. C. Maggs, Werner Krauth
# JeLLyFysh-Version1.0 -- a Python application for all-atom event-chain Monte Carlo,
# arXiv e-prints: 1907.12502 (2019), https://arxiv.org/abs/1907.12502
#
"""Module for the abstract EndOfRunEventHandler class."""
from abc import ABCMeta
from .abstracts import EventHandlerWithOutputHandler


class EndOfRunEventHandler(EventHandlerWithOutputHandler, metaclass=ABCMeta):
    """
    Abstract event handler base class used to end a run.

    This class is connected to an output handler, which gets access to the full extracted global state at the end
    of the run. Also, the mediating method for this class raises an EndOfRun exception.
    """

    def __init__(self, output_handler: str) -> None:
        """
        The constructor of the EndOfRunEventHandler class.

        Parameters
        ----------
        output_handler : str
            The name of the output handler.
        """
        super().__init__(output_handler=output_handler)
