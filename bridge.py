# Bridge Activity

# Copyright (C) Sugar Labs

#  This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import random
import pygame
from gi.repository import Gdk

SCALE_X = Gdk.Screen.width() * 1.5 / 1920
SCALE_Y = Gdk.Screen.height() * 1.2 / 1080


class Bridge:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.world = game.world
        self.cost = 0
        self.stress = 0
        self.capacity = 1
        self.first_train = None
        self.train_off_screen = False
        self.train_was_created = False
        self.train_exit = False
        self.level_completed = False
        self.sounds = {"wooo": loadSound("sounds/wooo.wav"),
                       "death": loadSound("sounds/death.wav"),
                       "startup": loadSound("sounds/startup.wav"),
                       "wooo1": loadSound("sounds/wooo1.wav"),
                       "wooo2": loadSound("sounds/wooo2.wav"),
                       "death1": loadSound("sounds/death1.wav"),
                       "death2": loadSound("sounds/death2.wav"),
                       "startup1": loadSound("sounds/startup1.wav")
                      }

    def restart(self):
        self.world.run_physics = False
        self.train_off_screen = False
        self.train_exit = False
        self.level_completed = False
        self.train_was_created = False

    def create_world(self):
        self.world.set_color((100, 150, 50))

        rect = pygame.Rect((-400 * SCALE_X, 825 * SCALE_Y),
                           (750 * SCALE_X, -250 * SCALE_Y))
        rect.normalize()
        pygame.draw.rect(self.screen, (100, 180, 255), rect, 3)
        self.world.add.rect(rect.center, rect.width / 2, rect.height / 2,
                            dynamic=False)
        rect = pygame.Rect((1750 * SCALE_X, 825 * SCALE_Y), (-850 * SCALE_X,
                           -250 * SCALE_Y))
        rect.normalize()
        pygame.draw.rect(self.screen, (100, 180, 255), rect, 3)
        self.world.add.rect(rect.center, rect.width / 2, rect.height / 2,
                            dynamic=False)
        self.world.reset_color()

    def add_cost(self, value):
        self.cost = self.cost + value
        print("cost now", value)

    def joint_added(self, joint):
        print("joint added!")
        self.add_cost(100)
        self.capacity += 500

    def joint_deleted(self, joint):
        print("joint deleting!")
        if self.cost > 0:
            self.add_cost(-100)
        self.capacity -= 500

    def box_added(self):
        self.add_cost(10)

    def circle_added(self):
        self.add_cost(10)

    def object_deleted(self):
        if self.cost > 0:
            self.add_cost(-10)

    def for_each_frame(self):
        self.stress = 0
        joint = self.world.world.joints
        for j in joint:
            try:
                if not j.motorEnabled:
                    force = j.GetReactionForce(30).length
                    self.stress += force

                    if force > 500:
                        print("destroy joint!")
                        self.world.world.DestroyJoint(j)
                        self.capacity -= 500
                    else:
                        vec = j.anchorA
                        coord = int(self.world.meter_to_screen(vec.x)), \
                            int(self.screen.get_height()
                                - self.world.meter_to_screen(vec.y))
                        pygame.draw.circle(self.screen,
                                           (int(force / 2), 255
                                            - int(force / 2), 0),
                                           coord, 6)
            except AttributeError:
                pass
        pos = self.first_train.position
        if pos.x < 0.0:
            self.train_exit = True
            if not self.level_completed:
                self.level_completed = True
                soundSelection = random.randint(0, 2)
                if soundSelection == 0:
                    self.sounds['wooo'].play()
                elif soundSelection == 1:
                    self.sounds['wooo1'].play()
                else:
                    self.sounds['wooo2'].play()
                
        elif pos.y < 0.0:
            if not self.train_off_screen:
                soundSelection = random.randint(0, 2)
                if soundSelection == 0:
                    self.sounds['death'].play()
                elif soundSelections == 1:
                    self.sounds['death1'].play()
                else:
                    self.sounds['death2'].play()
                print("TRAIN FELL OFF!", pos.x)
                self.train_off_screen = True

    def create_train(self, worldpoint=(int(1600 * SCALE_X),
                                       int(490 * SCALE_Y)),
                     train=(int(100 * SCALE_X), int(50 * SCALE_Y)),
                     wheelrad=int(20 * SCALE_X), cars=3,
                     force=False):
        self.train_exit = False
        if not force and self.train_was_created:
            return
        soundSelection = random.randint(0, 1)
        if soundSelection == 0:
            self.sounds['startup'].play()
        else:
            self.sounds['startup1'].play()
        self.train_was_created = True
        points = []
        self.train_off_screen = False
        for i in range(0, cars):
            startpoint = (worldpoint[0] - (train[0] + 7) * i, worldpoint[1])
            points.append(startpoint)
            rect = pygame.Rect(startpoint, train)
            rect.normalize()
            pygame.draw.rect(self.screen, (200, 50, 100), rect, 3)
            rect = self.world.add.rect(rect.center, rect.width / 2,
                                       rect.height / 2, dynamic=True,
                                       density=10.0, restitution=0.16,
                                       friction=0.5)
            if i == 0:
                self.first_train = rect

            self.world.set_color((0, 0, 0))
            rearwheel = (startpoint[0] + wheelrad, startpoint[1]
                         + train[1] - wheelrad // 2)
            pygame.draw.circle(self.screen, (0, 0, 0), rearwheel, wheelrad, 3)
            self.world.add.ball(rearwheel, wheelrad, dynamic=True,
                                density=10.0, restitution=0.16,
                                friction=0.5)

            frontwheel = (startpoint[0] + train[0] - wheelrad,
                          startpoint[1] + train[1] - wheelrad // 2)
            pygame.draw.circle(self.screen, (0, 0, 0), frontwheel, wheelrad, 3)
            self.world.add.ball(frontwheel, wheelrad, dynamic=True,
                                density=10.0, restitution=0.16,
                                friction=0.5)
            self.world.reset_color()

            rearaxle = self.world.get_bodies_at_pos(rearwheel)
            frontaxle = self.world.get_bodies_at_pos(frontwheel)
            if len(rearaxle) == 2:
                self.world.add.jointMotor(rearaxle[0], rearaxle[1], rearwheel)
            if len(frontaxle) == 2:
                self.world.add.jointMotor(
                    frontaxle[0], frontaxle[1], frontwheel)

        for i in range(1, len(points)):
            backlink = (points[i][0] + train[0] - 1,
                        points[i][1] + train[1] - 1)
            frontlink = (points[i - 1][0] + 1, points[i - 1][1] + train[1] - 1)
            btrain = self.world.get_bodies_at_pos(backlink)
            ftrain = self.world.get_bodies_at_pos(frontlink)
            if len(ftrain) and len(btrain):
                self.world.add.distanceJoint(
                    btrain[0], ftrain[0], backlink, frontlink)

# function for loading sounds (mostly borrowed from
# Pete Shinners pygame tutorial)


def loadSound(name):
    # if the mixer didn't load, then create an empty class
    # that has an empty play method. this way the program
    # will run if the mixer isn't present (sans sound)
    class NoneSound:
        def play(self):
            pass

        def set_volume(self):
            pass
    if not pygame.mixer:
        return NoneSound()
    try:
        sound = pygame.mixer.Sound(name)
    except Exception:
        print("error with sound: " + name)
        return NoneSound()
    return sound
