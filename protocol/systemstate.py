#!/usr/bin/env python
# -*- coding utf-8 -*-

""" This module represents the system state. """

from enum import Enum   # TODO import the dependency

system_state = Enum('INIT', 'UNSAFE', 'BALANCED', 'UNBALANCED')


