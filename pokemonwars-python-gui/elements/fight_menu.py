from typing import List, Optional
from functools import partial

import pygame

from classes.player_map import Player_Map
from classes.button import Button
from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.state import State
from global_types import SURFACE
from elements.global_classes import sprite_manager, GuiSettings
from elements.fight import Fight
from elements.choose_pokemon import Choose_Pokemon


class Fight_Menu(GameStrategy):
    def __init__(self, screen: SURFACE):
        super().__init__(screen)
        self._state: Optional[State] = None
        self.current_page = 1
        self.current_player = ['name', 'address', []]
        '''
        TODO: Проходим по списку игроков и выписываем всегда онлайн
        '''
        self.online_players = [['name1', 'address1', []],
                               ['qweqra', 'address1', []],
                               ['asf', 'address1', []],
                               ['nafasfsame1', 'address1', []],
                               ['qweqra', 'address1', []],
                               ['asf', 'address1', []],
                               ['nafasfsame1', 'address1', []],
                               ['qweqra', 'address1', []],
                               ['asf', 'address1', []],
                               ['nafasfsame1', 'address1', []],
                               ['qweqra', 'address1', []],
                               ['asf', 'address1', []],
                               ['nafasfsame1', 'address1', []],
                               ['qweqra', 'address1', []],
                               ['asf', 'address1', []],
                               ['nafasfsame1', 'address1', []],
                               ['asfasf', 'address1', []]]

    def right_button(self):
        self.current_page += 1

    def left_button(self):
        self.current_page -= 1

    def go_to_choose_pokemon(self, player=None):
        self._state = State(GameState.SWITCH, Choose_Pokemon(self.screen, self.current_player, player))

    def draw_players_maps(self, buttons, events: List[pygame.event.Event]):
        if self.current_page == 1:
            if len(self.online_players) <= 12:
                for i in range(len(self.online_players)):
                    player = Player_Map(35 + 260 * (i % 6), 140 + 360 * (i // 6), 230, 330, *self.online_players[i])
                    player.draw(self.screen)
                    Button(35 + 260 * (i % 6), 140 + 360 * (i // 6), 230, 330, (0, 0, 0), GuiSettings(), "",
                           partial(self.go_to_choose_pokemon, player)).update(events)
            else:
                for i in range(12):
                    player = Player_Map(35 + 260 * (i % 6), 140 + 360 * (i // 6), 230, 330, *self.online_players[i])
                    player.draw(self.screen)
                    Button(35 + 260 * (i % 6), 140 + 360 * (i // 6), 230, 330, (0, 0, 0), GuiSettings(), "",
                           partial(self.go_to_choose_pokemon, player)).update(events)
                buttons[0].draw(self.screen)
                buttons[0].update(events)
        elif (len(self.online_players) - 1) // 12 + 1 > self.current_page > 1:
            j = 0
            for i in range((self.current_page - 1) * 12 + 1, self.current_page * 12 + 1):
                player = Player_Map(35 + 260 * (j % 6), 140 + 360 * (j // 6), 230, 330, *self.online_players[i])
                player.draw(self.screen)
                Button(35 + 260 * (i % 6), 140 + 360 * (i // 6), 230, 330, (0, 0, 0), GuiSettings(), "",
                       partial(self.go_to_choose_pokemon, player)).update(events)
                j += 1
            for i in (1, 2):
                buttons[i].draw(self.screen)
                buttons[i].update(events)
        else:
            j = 0
            for i in range((self.current_page - 1) * 12, len(self.online_players)):
                player = Player_Map(35 + 260 * (j % 6), 140 + 360 * (j // 6), 230, 330, *self.online_players[i])
                player.draw(self.screen)
                Button(35 + 260 * (j % 6), 140 + 360 * (j // 6), 230, 330, (0, 0, 0), GuiSettings(), "",
                       partial(self.go_to_choose_pokemon, player)).update(events)
                j += 1
            buttons[3].draw(self.screen)
            buttons[3].update(events)

    async def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        """Отрисовывает меню онлайн игроков

        :param events: События, собранные окном pygame
        :type events: List[pygame.event.Event]
        :param delta_time_in_milliseconds: Время между нынешним и предыдущим кадром (unused)
        :type delta_time_in_milliseconds: int
        :return: Возвращает состояние для правильной работы game_context
        """

        buttons = [
            Button(600, 850, 400, 35, (68, 68, 68), GuiSettings(), f"Next page", self.right_button),
            Button(515, 850, 250, 35, (68, 68, 68), GuiSettings(), f"Previos page", self.left_button),
            Button(825, 850, 250, 35, (68, 68, 68), GuiSettings(), f"Next page", self.right_button),
            Button(600, 850, 400, 35, (68, 68, 68), GuiSettings(), f"Previos page", self.left_button)
        ]
        self.screen.blit(pygame.transform.scale(sprite_manager.get("./sprites/img.png"),
                                                (1600, 900)), (0, 0))
        self._state = None

        pygame.font.init()
        font = pygame.font.Font("fonts/ConsolateElf.ttf", 30)
        render_line = font.render("Choose enemy", True, (244, 244, 244))
        self.screen.blit(render_line, (35, 20))

        self.draw_players_maps(buttons, events)

        for event in events:
            if event.type == pygame.QUIT:
                '''
                TODO: Статус онлайна поменять на false
                '''
                self._state = State(GameState.BACK)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    '''
                    TODO: Статус онлайна поменять на false
                    '''
                    self._state = State(GameState.BACK)

        if self._state is None:
            self._state = State(GameState.FLIP, None)
        return self._state

    def on_init(self):
        pass
