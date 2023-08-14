from typing import List, Optional

import pygame

from classes.button import Button
from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.state import State
from global_types import SURFACE
from elements.global_classes import sprite_manager, GuiSettings
from classes.pokemon_map import Pokemon_Map


class Profile(GameStrategy):
    def __init__(self, screen: SURFACE):
        super().__init__(screen)
        self._state: Optional[State] = None
        self.name = 'Your name: ' + 'Namsdgdsgse'
        '''
        TODO: Проходить по владельцев в Game и брать от туда всех покемонов игрока
        '''
        self.pokemons = [
            [1, 'Venusaurus', 100, 100, 100, True, 'Grass', '40', '30'],
            [2, 'Charizard', 100, 100, 100, True, 'Fire', '40', '30'],
            [3, 'Blastosis', 25, 100, 100, True, 'Water', '40', '30'],
            [4, 'Butterfrey', 100, 100, 100, True, 'Fly', '40', '30'],
            [5, 'Bidrill', 75, 100, 100, True, 'Poison', '40', '30'],
            [6, 'Pidgit', 75, 100, 100, True, 'Fly', '40', '30'],
            [7, 'Spirou', 75, 100, 100, True, 'Fly', '40', '30'],
            [8, 'Erbok', 75, 100, 100, True, 'Poison', '40', '30'],
            [9, 'Pikachu', 75, 100, 100, True, 'Electric', '40', '30'],
            [10, 'Nidorina', 75, 100, 100, True, 'Poison', '40', '30'],
            [11, 'Nidorino', 75, 100, 100, True, 'Poison', '40', '30'],
            [12, 'Clefable', 75, 100, 100, True, 'Magical', '40', '30'],
            [13, 'Jiglipaf', 75, 100, 100, True, 'Magical', '40', '30'],
            [14, 'Golbat', 75, 100, 100, True, 'Fly', '40', '30'],
            [15, 'Wilplum', 75, 100, 100, True, 'Grass', '40', '30'],
            [16, 'Venonate', 75, 100, 100, True, 'Poison', '40', '30'],
            [17, 'Dagtrio', 75, 100, 100, True, 'Ground', '40', '30'],
            [18, 'Psydak', 75, 100, 100, True, 'Water', '40', '30'],
            [19, 'Primape', 75, 100, 100, True, 'Ground', '40', '30'],
            [20, 'Polyvag', 75, 100, 100, True, 'Water', '40', '30'],
            # pokemon info
        ]
        self.current_page = 1

    def right_button(self):
        self.current_page += 1

    def left_button(self):
        self.current_page -= 1

    def draw_pokemon_maps(self, buttons, events: List[pygame.event.Event]):
        if self.current_page == 1:
            if (len(self.pokemons) <= 12):
                for i in range(len(self.pokemons)):
                    pokemon = Pokemon_Map(35 + 260 * (i % 6), 140 + 360 * (i // 6), *self.pokemons[i])
                    pokemon.draw(self.screen, pygame.mouse.get_pos())
            else:
                for i in range(12):
                    pokemon = Pokemon_Map(35 + 260 * (i % 6), 140 + 360 * (i // 6), *self.pokemons[i])
                    pokemon.draw(self.screen, pygame.mouse.get_pos())
                buttons[0].draw(self.screen)
                buttons[0].update(events)
        elif (len(self.pokemons) - 1) // 12 + 1 > self.current_page > 1:
            j = 0
            for i in range((self.current_page - 1) * 12 + 1, self.current_page * 12 + 1):
                pokemon = Pokemon_Map(35 + 260 * (j % 6), 140 + 360 * (j // 6), *self.pokemons[i])
                pokemon.draw(self.screen, pygame.mouse.get_pos())
                j += 1
            for i in (1, 2):
                buttons[i].draw(self.screen)
                buttons[i].update(events)
        else:
            j = 0
            for i in range((self.current_page - 1) * 12, len(self.pokemons)):
                pokemon = Pokemon_Map(35 + 260 * (j % 6), 140 + 360 * (j // 6), *self.pokemons[i])
                pokemon.draw(self.screen, pygame.mouse.get_pos())
                j += 1
            buttons[3].draw(self.screen)
            buttons[3].update(events)

    async def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        """Отрисовывает интерфейс загрузчика и обрабатывает все события

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
        self.screen.blit(pygame.transform.scale(sprite_manager.get("./sprites/img.jpg")
                                                , (1600, 900)), (0, 0))
        self._state = None

        pygame.font.init()
        font = pygame.font.Font("fonts/ConsolateElf.ttf", 30)
        render_line = font.render(self.name, True, (244, 244, 244))
        self.screen.blit(render_line, (35, 20))

        render_line = font.render(f"You have {len(self.pokemons)} pokemons:", True, (244, 244, 244))
        self.screen.blit(render_line, (35, 70))

        self.draw_pokemon_maps(buttons, events)

        for event in events:
            if event.type == pygame.QUIT:
                self._state = State(GameState.BACK)
                '''
                TODO: Статус онлайна поменять на false
                '''
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
