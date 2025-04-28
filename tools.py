# ==================================================================
#                           Physics.activity
#                              Tool Classes
#                           By Alex Levenson
# ==================================================================

import pygame
import Box2D as box2d
import pygame.locals
import helpers
from inspect import getmro
import math
from gettext import gettext as _


def distance(pt1, pt2):
    return math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)


def distance2(pt1, pt2, amount):
    if amount == float('inf'):
        return True
    return ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) <= (amount ** 2)

# tools that can be used superclass


class Tool(object):
    name = "Tool"
    icon = "icon"
    toolTip = "Tool Tip"

    def __init__(self, gameInstance):
        self.game = gameInstance
        self.name = "Tool"

    def handleEvents(self, event, bridge):
        handled = True
        # default event handling
        if event.type == pygame.QUIT:
            # bye bye! Hope you had fun!
            self.game.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # space pauses
                self.game.bridge.create_train()
                self.game.world.run_physics = not self.game.world.run_physics
            elif event.key == pygame.K_r:
                if bridge.train_off_screen:
                    self.game.bridge.restart()
            elif event.key == pygame.K_t:
                # t creates a new train only after one train exits
                if self.game.bridge.train_exit:
                    self.game.bridge.create_train(force=True)
            elif event.key == pygame.K_b:
                self.game.setTool("girder")
            elif event.key == pygame.K_c:
                self.game.setTool("circle")
            elif event.key == pygame.K_j:
                self.game.setTool("bridgejoint")
            elif event.key == pygame.K_g:
                self.game.setTool("grab")
            elif event.key == pygame.K_d:
                self.game.setTool("destroy")
        elif event.type == pygame.USEREVENT:
            if hasattr(event, "action"):
                if event.action in self.game.toolList:
                    self.game.setTool(event.action)
        # elif event.type == MOUSEBUTTONDOWN and event.button == 1:
        # self.game._pygamecanvas.canvas.grab_focus()
        # handled = False
        else:
            handled = False
        return handled

    def draw(self):
        # default drawing method is don't draw anything
        pass

    def cancel(self):
        # default cancel doesn't do anything
        pass

    def to_b2vec(self, pt):
        return self.game.world.add.to_b2vec(pt)

# The circle creation tool


class CircleTool(Tool):
    name = "circle"
    icon = "circle"
    toolTip = _("Circle")

    def __init__(self, gameInstance):
        self.game = gameInstance
        self.name = "Circle"
        self.pt1 = None
        self.radius = None

    def handleEvents(self, event, bridge):
        # look for default events, and if none are
        # handled then try the custom events
        if not super(CircleTool, self).handleEvents(event, bridge):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.pt1 = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.radius > 1:  # elements doesn't like tiny shapes :(
                        self.game.world.add.ball(
                            self.pt1, self.radius, dynamic=True, density=1.0,
                            restitution=0.16, friction=0.5)
                    self.game.bridge.circle_added()
                    self.pt1 = None
                    self.radius = None

    def draw(self):
        # draw a circle from pt1 to mouse
        if self.pt1 is not None:
            mouse_pos = pygame.mouse.get_pos()
            self.radius = helpers.distance(self.pt1, mouse_pos)
            if self.radius > 3:
                thick = 3
            else:
                thick = 0
            pygame.draw.circle(self.game.screen, (100, 180, 255), self.pt1,
                               int(self.radius), thick)
            pygame.draw.line(self.game.screen, (100, 180, 255), self.pt1,
                             mouse_pos, 1)

    def cancel(self):
        self.pt1 = None
        self.radius = None

# The Girder creation tool


class GirderTool(Tool):
    name = "girder"
    icon = "box"
    toolTip = _("Girder")

    def __init__(self, gameInstance):
        self.game = gameInstance
        self.name = "Box"
        self.pt1 = None
        self.pt2 = None
        self.theta = None
        self.thickness = 30
        self.max = 300
        self.min = 100
        self.red = 20
        self.green = 20
        self.blue = 20
        self.colordiff = 20

    def handleEvents(self, event, bridge):
        # look for default events, and if none are
        # handled then try the custom events
        if not super(GirderTool, self).handleEvents(event, bridge):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.pt1 = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.pt2 is not None:
                        self.game.world.set_color(
                            (self.red, self.green, self.blue))
                        self.red += self.colordiff
                        self.green += self.colordiff
                        self.blue += self.colordiff
                        if self.red > 200:
                            self.colordiff *= -1
                        elif self.red < 20:
                            self.colordiff *= -1
                        print(self.theta, math.degrees(self.theta))
                        self.game.world.add.rect(((self.pt1[0]
                                                   + self.pt2[0]) / 2,
                                                  (self.pt1[1]
                                                   + self.pt2[1]) / 2),
                                                 helpers.distance(
                                                     self.pt1, self.pt2) / 2,
                                                 self.thickness / 2,
                                                 angle=math.degrees(
                                                     self.theta),
                                                 dynamic=True, density=1.0,
                                                 restitution=0.16,
                                                 friction=0.5)
                        self.game.bridge.box_added()
                        self.game.world.reset_color()
                    self.pt1 = None

    def draw(self):
        # draw a box from pt1 to mouse
        if self.pt1 is not None:
            self.pt2 = pygame.mouse.get_pos()
            self.theta = helpers.getAngle(self.pt1, self.pt2)
            if distance2(self.pt1, self.pt2, self.min):
                # too small! force length
                self.pt2 = (self.pt1[0] + self.min * math.cos(self.theta),
                            self.pt1[1] - self.min * math.sin(self.theta))
            elif not distance2(self.pt1, self.pt2, self.max):
                # too big
                self.pt2 = (self.pt1[0] + (self.max * math.cos(self.theta)),
                            self.pt1[1] - (self.max * math.sin(self.theta)))
            pygame.draw.line(self.game.screen, (255, 255, 255),
                             self.pt1, self.pt2, 30)

    def cancel(self):
        self.pt1 = None
        self.rect = None

# The grab tool


class GrabTool(Tool):
    name = "grab"
    icon = "grab"
    toolTip = _("Grab")

    def __init__(self, gameInstance):
        self.game = gameInstance
        self.name = "Grab"

    def handleEvents(self, event, bridge):
        # look for default events, and if none
        # are handled then try the custom events
        if not super(GrabTool, self).handleEvents(event, bridge) \
           and bridge.cost > 0:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # grab the first object at the mouse pointer
                    bodylist = self.game.world.get_bodies_at_pos(
                        event.pos, include_static=False)
                    if bodylist and len(bodylist) > 0:
                        self.game.world.add.mouseJoint(bodylist[0], event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                # let it go
                if event.button == 1:
                    self.game.world.add.remove_mouseJoint()
            # use box2D mouse motion
            elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                self.game.world.mouse_move(event.pos)

    def cancel(self):
        self.game.world.add.remove_mouseJoint()


# The destroy tool
class DestroyTool(Tool):
    name = "destroy"
    icon = "destroy"
    toolTip = _("Destroy")

    def __init__(self, gameInstance):
        self.game = gameInstance
        self.name = "Destroy"
        self.vertices = None

    def handleEvents(self, event, bridge):
        # look for default events, and if none
        # are handled then try the custom events
        if not super(DestroyTool, self).handleEvents(event, bridge):
            if pygame.mouse.get_pressed()[0]:
                if not self.vertices:
                    self.vertices = []
                self.vertices.append(pygame.mouse.get_pos())
                if len(self.vertices) > 10:
                    self.vertices.pop(0)
                tokill = self.game.world.get_bodies_at_pos(
                    pygame.mouse.get_pos())
                if tokill:
                    joints = tokill[0].joints
                    if len(joints) > 0:
                        for joint in joints:
                            self.game.bridge.joint_deleted(joint)
                    self.game.world.world.DestroyBody(tokill[0])
                    self.game.bridge.object_deleted()
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.cancel()

    def draw(self):
        # draw the trail
        if self.vertices:
            if len(self.vertices) > 1:
                pygame.draw.lines(self.game.screen, (255, 0, 0),
                                  False, self.vertices, 3)

    def cancel(self):
        self.vertices = None

# The joint tool


class BridgeJointTool(Tool):
    name = "bridgejoint"
    icon = "joint"
    toolTip = _("Bridge Joint")

    def __init__(self, gameInstance):
        self.game = gameInstance
        self.name = "Bridge Joint"
        self.jb1 = self.jb2 = self.jb1pos = self.jb2pos = None

    def handleEvents(self, event, bridge):
        # look for default events, and if none
        # are handled then try the custom events
        if super(BridgeJointTool, self).handleEvents(event, bridge):
            return
        if event.type != pygame.MOUSEBUTTONUP or event.button != 1:
            return

        bodies = self.game.world.get_bodies_at_pos(event.pos,
                                                   include_static=True)
        if not bodies or len(bodies) > 2:
            return

        jointDef = box2d.b2RevoluteJointDef()
        if len(bodies) == 1:
            if not bodies[0].type == box2d.b2_staticBody:
                if event.pos[1] > 550 and (
                        event.pos[0] < 350 or event.pos[0] > 850):
                    jointDef.Initialize(self.game.world.world.groundBody,
                                        bodies[0], self.to_b2vec(event.pos))
                else:
                    return
            else:
                return
        elif len(bodies) == 2:
            if bodies[0].type == box2d.b2_staticBody:
                jointDef.Initialize(self.game.world.world.groundBody,
                                    bodies[1], self.to_b2vec(event.pos))
            elif bodies[1].type == box2d.b2_staticBody:
                jointDef.Initialize(self.game.world.world.groundBody,
                                    bodies[0], self.to_b2vec(event.pos))
            else:
                jointDef.Initialize(
                    bodies[0], bodies[1], self.to_b2vec(event.pos))
        joint = self.game.world.world.CreateJoint(jointDef)
        self.game.bridge.joint_added(joint)

    def draw(self):
        return

    def cancel(self):
        self.jb1 = self.jb2 = self.jb1pos = self.jb2pos = None


def getAllTools():
    this_mod = __import__(__name__)
    all_tools = [val for val in list(this_mod.__dict__.values())
                 if isinstance(val, type)]
    allTools = []
    for a in all_tools:
        if getmro(a).__contains__(Tool) and a != Tool:
            allTools.append(a)
    return allTools


allTools = getAllTools()
