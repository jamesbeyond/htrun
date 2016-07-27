#!/usr/bin/env python
"""
mbed SDK
Copyright (c) 2011-2016 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re
from abc import ABCMeta, abstractmethod


class BaseParser():
    __metaclass__ = ABCMeta

    def __init__(self, regex):
        self.REGEX = regex
        self.buff = str()
        self.buff_idx = 0
        self.re = re.compile(self.REGEX)

    def append(self, payload):
        """! Append stream buffer with payload """
        self.buff += payload

    def search(self):
        """! Check if there is a KV value in buffer 
        @return MatchObject or None
        """
        return self.re.search(self.buff[self.buff_idx:])

    @abstractmethod
    def get_kv(self):
        """! Check if there is a KV value in buffer """
        pass
