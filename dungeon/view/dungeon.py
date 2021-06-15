import random
from typing import List

import discord
from discord import Embed
from discordmenu.embed.base import Box
from discordmenu.emoji.emoji_cache import emoji_cache
from discordmenu.embed.components import EmbedMain, EmbedField
from discordmenu.embed.view import EmbedView
from tsutils import embed_footer_with_state

from dungeon.safe_dict import SafeDict
from dungeon.enemy_skills_pb2 import MonsterBehavior
from dungeon.processors import process_monster
from padinfo.common.config import UserConfig
from padinfo.view.components.view_state_base import ViewStateBase


class DungeonViewState(ViewStateBase):
    def __init__(self, original_author_id, menu_type, raw_query, color, pm,
                 sub_dungeon_id, num_floors, floor, num_spawns, floor_index, technical, database, page=0, verbose=False,
                 reaction_list: List[str] = None):
        super().__init__(original_author_id, menu_type, raw_query, reaction_list=reaction_list)
        self.pm = pm
        self.sub_dungeon_id = sub_dungeon_id
        self.num_floors = num_floors
        self.floor = floor
        self.floor_index = floor_index
        self.technical = technical
        self.color = color
        self.database = database
        self.num_spawns = num_spawns
        self.page = page
        self.verbose = verbose

    def serialize(self):
        ret = super().serialize()
        ret.update({
            'sub_dungeon_id': self.sub_dungeon_id,
            'num_floors': self.num_floors,
            'floor': self.floor,
            'floor_index': self.floor_index,
            'technical': self.technical,
            'pane_type': DungeonView.VIEW_TYPE,
            'verbose': self.verbose,
            'page': self.page
        })
        return ret

    @classmethod
    async def deserialize(cls, dgcog, color, ims: dict, inc_floor: int = 0, inc_index: int = 0,
                          verbose_toggle: bool = False, page: int = 0, reset_spawn: bool = False):
        original_author_id = ims['original_author_id']
        menu_type = ims['menu_type']
        raw_query = ims.get('raw_query')
        sub_dungeon_id = ims.get('sub_dungeon_id')
        num_floors = ims.get('num_floors')
        floor = ims.get('floor') + inc_floor
        floor_index = ims.get('floor_index') + inc_index
        technical = ims.get('technical')
        verbose = ims.get('verbose')
        # check if we are on final floor/final monster of the floor
        if floor > num_floors:
            floor = 1

        if floor < 1:
            floor = num_floors

        # toggle verbose
        if verbose_toggle:
            verbose = not verbose

        # get encounter models for the floor
        floor_models = dgcog.database.dungeon.get_floor_from_sub_dungeon(sub_dungeon_id, floor)

        # check if we are on final monster of the floor
        if floor_index >= len(floor_models):
            floor_index = 0

        if floor_index < 0:
            floor_index = len(floor_models) + floor_index

        # check if we reset the floor_index
        if reset_spawn:
            floor_index = 0

        encounter_model = floor_models[floor_index]

        return cls(original_author_id, menu_type, raw_query, color, encounter_model, sub_dungeon_id,
                   num_floors, floor, len(floor_models), floor_index,
                   technical, dgcog.database, verbose=verbose,
                   reaction_list=ims.get('reaction_list'), page=page)


class DungeonView:
    VIEW_TYPE = 'DungeonText'

    egg_text = [
        "But nobody came...",
        "Come again later",
        "Tsubaki loves you",
        "Remember 100 turn Hera stalling?",
        "Odin x Mermaid are the OG heroes",
        "Never forget 10 minute stamina",
        "Another 3*...",
        "Nice!",
        "Maybe one day DBZ will come",
        "Special thanks to the PADX team and tactical_retreat!"
    ]

    @staticmethod
    def indent(level):
        """
        Helper function that indents text for the embed
        """
        ret = ""
        for l in range(level):
            if l == 0:
                ret += "> "
            else:
                ret += "\u200b \u200b \u200b \u200b \u200b "
        return ret

    @staticmethod
    def embed_helper(level, names, values, line):
        """
        Adds a line in such a way to maximize discord embed limits.

        We first try to add it to the most recent name part of the name/value pair.
        If that fails we try to add it to the corresponding value. If that fails,
        we create another name/value pair.
        @param level: how many indents the line needs
        @param names: an existing list (a list of strings that will be placed in "name fields"
        @param values: an existing list (a list of strings that will be placed in the value part of the name/value field
        @param line: the line of text we want to add
        """

        current_index = len(names) - 1
        indents = DungeonView.indent(level)
        if len(names[current_index]) + len(line) + len(indents) <= 255 and len(names[current_index]) == 0:
            names[current_index] += "\n{}{}".format(indents, line)
        elif len(values[current_index]) + len(line) + len(indents) <= 1023:
            values[current_index] += "\n{}{}".format(indents, line)
        else:
            names.append("")
            values.append("")
            DungeonView.embed_helper(level, names, values, line)

    @staticmethod
    def embed(state: DungeonViewState):
        fields = []
        mb = MonsterBehavior()
        encounter_model = state.pm
        if (encounter_model.enemy_data is not None) and (encounter_model.enemy_data.behavior is not None):
            mb.ParseFromString(encounter_model.enemy_data.behavior)
        else:
            mb = None
        monster = process_monster(mb, encounter_model, state.database)
        monster_embed: Embed = \
            DungeonView.make_embed(monster, verbose=state.verbose, spawn=[state.floor_index + 1, state.num_spawns],
                               floor=[state.floor, state.num_floors], technical=state.technical)[state.page]
        hp = f'{monster.hp:,}'
        atk = f'{monster.atk:,}'
        defense = f'{monster.defense:,}'
        turns = f'{monster.turns:,}'

        title = monster_embed.title
        desc = monster_embed.description
        me_fields = monster_embed.fields
        for f in me_fields:
            fields.append(
                EmbedField(f.name, Box(*[f.value]))
            )
        return EmbedView(
            EmbedMain(
                title=title,
                description=desc,
            ),
            embed_fields=fields,
            embed_footer=embed_footer_with_state(state)
        )

    @staticmethod
    def make_embed(dungeon_monster, verbose: bool = False, spawn: "list[int]" = None, floor: "list[int]" = None,
                   technical: int = None):
        """
        When called this generates an embed that displays the encounter (what is seen in dungeon_info).
        @param dungeon_monster: the processed monster to make an embed for
        @param verbose: whether or not to display effect text
        @param spawn: used to show what spawn this is on a floor [spawn, max] -> "spawn/max"
        @param floor: used to show what floor this is [current floor, number of floors]
        @param technical: if the dungeon is a technical dungeon we don't display skills
        """

        embeds = []

        desc = ""

        # We create two pages as monsters at max will only ever require two pages of embeds
        if spawn is not None:
            embed = discord.Embed(
                title="Enemy:{} at Level: {} Spawn:{}/{} Floor:{}/{} Page:".format(dungeon_monster.name, dungeon_monster.level, spawn[0],
                                                                                   spawn[1],
                                                                                   floor[0], floor[1]),
                description="HP:{} ATK:{} DEF:{} TURN:{}{}".format(f'{dungeon_monster.hp:,}', f'{dungeon_monster.atk:,}', f'{dungeon_monster.defense:,}',
                                                                   f'{dungeon_monster.turns:,}', desc)
            )
        else:
            embed = discord.Embed(
                title="Enemy:{} at Level: {}".format(dungeon_monster.name, dungeon_monster.level),
                description="HP:{} ATK:{} DEF:{} TURN:{}{}".format(f'{dungeon_monster.hp:,}', f'{dungeon_monster.atk:,}', f'{dungeon_monster.defense:,}',
                                                                   f'{dungeon_monster.turns:,}', desc)
            )

        embeds.append(embed)
        embeds.append(embed.copy())

        if technical == 0:
            embeds[0].title += " 1/1"
            embeds[1].title += " 2/1"
            return embeds
        embeds[0].title += " 1/"
        embeds[1].title += " 2/"
        # We collect text from the skills and groups of skills
        lines = []
        for group in dungeon_monster.groups:
            group.give_string2(lines, 0, verbose)

        # We add the lines using embed_helper
        names = [""]
        values = [""]
        fields = 0
        current_embed = 0
        length = len(embed.title) + len(embed.description) + 1
        first = None
        for l in lines:
            for comp in l[1]:
                DungeonView.embed_helper(l[0], names, values, comp)

        # We add the name/value pairs to the actual embed. If needed we go to the second page
        if len(values[len(values) - 1]) == 0:
            values[len(values) - 1] = '\u200b'
        for index in range(len(names)):
            name = names[index]
            value = values[index]
            if len(name) > 0:
                temp_length = length + len(name) + len(value)
                if temp_length > 6000:
                    current_embed += 1
                    length = len(embed.title) + len(embed.description)
                embeds[current_embed].add_field(name=name, value=value, inline=False)
                length += len(name) + len(value)
                fields += 1
            # embed.add_field(name=k, value=content, inline=False)

        if current_embed == 0:
            embeds[0].title += '1'
            embeds[1].title += '1'

            # for fun
            random_index = random.randint(0, len(DungeonView.egg_text) - 1)
            embeds[1].add_field(name=DungeonView.egg_text[random_index], value="Come back when you see 1/2 for page!")
        else:
            embeds[0].title += '2'
            embeds[1].title += '2'
        return embeds

    @staticmethod
    async def make_preempt_embed(dungeon_monster, spawn: "list[int]" = None, floor: "list[int]" = None, technical: int = None):
        """
        Currently unused: when called it creates an embed that only contains embed information.
        """
        skills = await dungeon_monster.collect_skills()
        desc = ""
        for s in skills:
            if "Passive" in s.type or "Preemptive" in s.type:
                desc += "\n{}".format(s.give_string(verbose=True))
        if technical == 0:
            desc = ""
        if spawn is not None:
            embed = discord.Embed(
                title="Enemy:{} at Level: {} Spawn:{}/{} Floor:{}/{}".format(dungeon_monster.name, dungeon_monster.level, spawn[0], spawn[1],
                                                                             floor[0], floor[1]),
                description="HP:{} ATK:{} DEF:{} TURN:{}{}".format(f'{dungeon_monster.hp:,}', f'{dungeon_monster.atk:,}', f'{dungeon_monster.defense:,}',
                                                                   f'{dungeon_monster.turns:,}', desc))
        else:
            embed = discord.Embed(
                title="Enemy:{} at Level: {}".format(dungeon_monster.name, dungeon_monster.level),
                description="HP:{} ATK:{} DEF:{} TURN:{}{}".format(f'{dungeon_monster.hp:,}', f'{dungeon_monster.atk:,}', f'{dungeon_monster.defense:,}',
                                                                   f'{dungeon_monster.turns:,}', desc))
        return [embed, discord.Embed(title="test", desc="test")]