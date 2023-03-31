# SPDX-FileCopyrightText: 2023-present Stephan Uhle <stephanu@gmx.net>
#
# SPDX-License-Identifier: MIT


class Entity:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name
