import time
from objects import RelRobotLocation
from ..navigator import Navigator as nav
from ..util import Transition
import VisualGoalieStates as VisualStates
from .. import SweetMoves
from ..headTracker import HeadMoves
import GoalieConstants as constants
import math

SAVING = True

def gameInitial(player):
    if player.firstFrame():
        player.inKickingState = False
        player.gameState = player.currentState
        player.returningFromPenalty = False
        player.brain.fallController.enabled = False
        player.stand()
        player.zeroHeads()
        player.isSaving = False
        player.lastStiffStatus = True

    # If stiffnesses were JUST turned on, then stand up.
    if player.lastStiffStatus == False and player.brain.interface.stiffStatus.on:
        player.stand()
    # Remember last stiffness.
    player.lastStiffStatus = player.brain.interface.stiffStatus.on

    return player.stay()

def gameReady(player):
    if player.firstFrame():
        player.inKickingState = False
        player.brain.fallController.enabled = True
        player.gameState = player.currentState
        player.penaltyKicking = False
        player.stand()
        player.brain.tracker.lookToAngle(0)
        if player.lastDiffState != 'gameInitial':
            return player.goLater('spinToWalkOffField')

    # Wait until the sensors are calibrated before moving.
    if(not player.brain.motion.calibrated):
        return player.stay()

    return player.stay()

def gameSet(player):
    if player.firstFrame():
        player.inKickingState = False
        player.brain.fallController.enabled = False
        player.gameState = player.currentState
        player.returningFromPenalty = False
        player.penaltyKicking = False
        player.stand()
        player.brain.interface.motionRequest.reset_odometry = True
        player.brain.interface.motionRequest.timestamp = int(player.brain.time * 1000)

        # The ball will be right in front of us, for sure
        player.brain.tracker.lookToAngle(0)

    # The goalie always gets manually positioned, so reset loc to there.
    player.brain.resetGoalieLocalization()

    # Wait until the sensors are calibrated before moving.
    if (not player.brain.motion.calibrated):
        return player.stay()

    return player.stay()

def gamePlaying(player):
    if player.firstFrame():
        player.inKickingState = False
        player.brain.fallController.enabled = True
        player.gameState = player.currentState
        player.penaltyKicking = False
        player.brain.nav.stand()

    # Wait until the sensors are calibrated before moving.
    if (not player.brain.motion.calibrated):
        return player.stay()

    if (player.lastDiffState == 'gamePenalized' and
        player.lastStateTime > 10):
        return player.goLater('afterPenalty')

    if player.lastDiffState == 'afterPenalty':
        return player.goLater('walkToGoal')

    if player.lastDiffState == 'fallen':
        return player.goLater('spinAtGoal')

    return player.goLater('watch')

def gamePenalized(player):
    if player.firstFrame():
        player.inKickingState = False
        player.brain.fallController.enabled = False
        player.gameState = player.currentState
        player.stopWalking()
        player.penalizeHeads()

    if player.lastDiffState == '':
        # Just started up! Need to calibrate sensors
        player.brain.nav.stand()

    # Wait until the sensors are calibrated before moving.
    if (not player.brain.motion.calibrated):
        return player.stay()

    return player.stay()

def gameFinished(player):
    if player.firstFrame():
        player.inKickingState = False
        player.brain.fallController.enabled = False
        player.gameState = player.currentState
        player.stopWalking()
        player.zeroHeads()
        player.executeMove(SweetMoves.SIT_POS)
        return player.stay()

    if player.brain.nav.isStopped():
        player.gainsOff()

    return player.stay()

##### EXTRA METHODS

def fallen(player):
    player.inKickingState = False
    return player.stay()

def spinToWalkOffField(player):
    if player.firstFrame():
        player.brain.tracker.lookToAngle(0)
        player.brain.nav.goTo(RelRobotLocation(0, 0, 90))

    return Transition.getNextState(player, spinToWalkOffField)

def bookIt(player):
    if player.firstFrame():
        player.brain.nav.goTo(RelRobotLocation(100, 0, 0), avoidObstacles = True)

    return Transition.getNextState(player, bookIt)

def standStill(player):
    if player.firstFrame():
        player.brain.nav.stop()

    return player.stay()

def watchWithCornerChecks(player):
    if player.firstFrame():
        # This is dumb, but...
        if player.lastDiffState not in ['fixMyself',
                                        'moveForward',
                                        'moveBackwards']:
            watchWithCornerChecks.numFixes = 0
        else:
            watchWithCornerChecks.numFixes += 1

        if watchWithCornerChecks.numFixes > 6:
            return player.goLater('watch')

        watchWithCornerChecks.looking = False
        watchWithCornerChecks.lastLook = constants.RIGHT
        player.homeDirections = []
        player.brain.tracker.trackBall()
        player.brain.nav.stand()
        player.returningFromPenalty = False

    if player.counter > 200:
        return player.goLater('watch')

    if (player.brain.ball.vis.frames_on > constants.BALL_ON_SAFE_THRESH
        and
        player.brain.ball.distance > constants.BALL_SAFE_DISTANCE_THRESH
        and not watchWithCornerChecks.looking):
        watchWithCornerChecks.looking = True
        if watchWithCornerChecks.lastLook is constants.RIGHT:
            player.brain.tracker.lookToAngle(constants.EXPECTED_LEFT_CORNER_BEARING_FROM_CENTER)
            watchWithCornerChecks.lastLook = constants.LEFT
        else:
            player.brain.tracker.lookToAngle(constants.EXPECTED_RIGHT_CORNER_BEARING_FROM_CENTER)
            watchWithCornerChecks.lastLook = constants.RIGHT

    if player.brain.tracker.isStopped():
        watchWithCornerChecks.looking = False
        player.brain.tracker.trackBall()

    return Transition.getNextState(player, watchWithCornerChecks)

def watch(player):
    if player.firstFrame():
        player.brain.tracker.trackBall()
        player.brain.nav.stand()
        player.returningFromPenalty = False

    return Transition.getNextState(player, watch)

def average(locations):
    x = 0.0
    y = 0.0
    h = 0.0

    for item in locations:
        x += item.relX
        y += item.relY
        h += item.relH

    return RelRobotLocation(x/len(locations),
                            y/len(locations),
                            h/len(locations))

def correct(destination):
    if math.fabs(destination.relX) < constants.STOP_NAV_THRESH:
        destination.relX = 0.0
    if math.fabs(destination.relY) < constants.STOP_NAV_THRESH:
        destination.relY = 0.0
    if math.fabs(destination.relH) < constants.STOP_NAV_THRESH:
        destination.relH = 0.0

    destination.relX = destination.relX / constants.OVERZEALOUS_ODO
    destination.relY = destination.relY / constants.OVERZEALOUS_ODO
    destination.relH = destination.relH / constants.OVERZEALOUS_ODO

    return destination

def fixMyself(player):
    if player.firstFrame():
        player.brain.tracker.trackBall()
        dest = correct(average(player.homeDirections))
        player.brain.nav.walkTo(dest)

    return Transition.getNextState(player, fixMyself)

def moveForward(player):
    if player.firstFrame():
        player.brain.tracker.trackBall()
        player.brain.nav.walkTo(RelRobotLocation(30, 0, 0))

    return Transition.getNextState(player, moveForward)

def moveBackwards(player):
    if player.firstFrame():
        player.brain.tracker.trackBall()
        player.brain.nav.walkTo(RelRobotLocation(-30, 0, 0))

    return Transition.getNextState(player, moveBackwards)

def kickBall(player):
    """
    Kick the ball
    """
    if player.firstFrame():
        # save odometry if this was your first kick
        if player.lastDiffState == 'clearIt':
            VisualStates.returnToGoal.kickPose = \
                RelRobotLocation(player.brain.interface.odometry.x,
                                 player.brain.interface.odometry.y,
                                 player.brain.interface.odometry.h)
        #otherwise add to previously saved odo
        else:
            VisualStates.returnToGoal.kickPose.relX += \
                player.brain.interface.odometry.x
            VisualStates.returnToGoal.kickPose.relY += \
                player.brain.interface.odometry.y
            VisualStates.returnToGoal.kickPose.relH += \
                player.brain.interface.odometry.h

        player.brain.tracker.trackBall()
        player.brain.nav.stop()

    if player.counter is 20:
        player.executeMove(player.kick.sweetMove)

    if player.counter > 30 and player.brain.nav.isStopped():
            return player.goLater('didIKickIt')

    return player.stay()

def saveCenter(player):
    if player.firstFrame():
        player.brain.fallController.enabled = False
        player.brain.tracker.lookToAngle(0)
        if SAVING:
            player.executeMove(SweetMoves.GOALIE_SQUAT)
        else:
            player.executeMove(SweetMoves.GOALIE_TEST_CENTER_SAVE)

    if player.counter > 80:
        if SAVING:
            player.executeMove(SweetMoves.GOALIE_SQUAT_STAND_UP)
            return player.goLater('upUpUP')
        else:
            return player.goLater('watch')

    return player.stay()

def upUpUP(player):
    if player.firstFrame():
        player.brain.fallController.enabled = True
        player.upDelay = 0

    if player.brain.nav.isStopped():
        return player.goLater('watchWithCornerChecks')
    return player.stay()

def saveRight(player):
    if player.firstFrame():
        player.brain.fallController.enabled = False
        player.brain.tracker.lookToAngle(0)
        if SAVING:
            player.executeMove(SweetMoves.GOALIE_DIVE_RIGHT)
            player.brain.tracker.performHeadMove(HeadMoves.OFF_HEADS)
        else:
            player.executeMove(SweetMoves.GOALIE_TEST_DIVE_RIGHT)

    if player.counter > 80:
        if SAVING:
            player.executeMove(SweetMoves.GOALIE_ROLL_OUT_RIGHT)
            return player.goLater('rollOut')
        else:
            return player.goLater('watch')

    return player.stay()

def saveLeft(player):
    if player.firstFrame():
        player.brain.fallController.enabled = False
        player.brain.tracker.lookToAngle(0)
        if SAVING:
            player.executeMove(SweetMoves.GOALIE_DIVE_LEFT)
            player.brain.tracker.performHeadMove(HeadMoves.OFF_HEADS)
        else:
            player.executeMove(SweetMoves.GOALIE_TEST_DIVE_LEFT)

    if player.counter > 80:
        if SAVING:
            player.executeMove(SweetMoves.GOALIE_ROLL_OUT_LEFT)
            return player.goLater('rollOut')
        else:
            return player.goLater('watch')

    return player.stay()

def rollOut(player):
    if player.brain.nav.isStopped():
        player.brain.fallController.enabled = True
        return player.goLater('fallen')

    return player.stay()

# ############# PENALTY SHOOTOUT #############

def penaltyShotsGameSet(player):
    if player.firstFrame():
        player.inKickingState = False
        player.gameState = player.currentState
        player.returningFromPenalty = False
        player.brain.fallController.enabled = False
        player.stand()
        player.brain.tracker.trackBall()
        player.side = constants.LEFT
        player.isSaving = False
        player.penaltyKicking = True

    return player.stay()

def penaltyShotsGamePlaying(player):
    if player.firstFrame():
        player.inKickingState = False
        player.gameState = player.currentState
        player.returningFromPenalty = False
        player.brain.fallController.enabled = False
        player.stand()
        player.zeroHeads()
        player.isSaving = False
        player.lastStiffStatus = True

    return player.goLater('waitForPenaltySave')

def waitForPenaltySave(player):
    if player.firstFrame():
        player.brain.tracker.trackBall()
        player.brain.nav.stop()

    return Transition.getNextState(player, waitForPenaltySave)

def doDive(player):
    if player.firstFrame():
        player.brain.fallController.enabled = False
        player.brain.tracker.performHeadMove(HeadMoves.OFF_HEADS)
        if doDive.side == constants.RIGHT:
            player.executeMove(SweetMoves.GOALIE_DIVE_RIGHT)
        elif doDive.side == constants.LEFT:
            player.executeMove(SweetMoves.GOALIE_DIVE_LEFT)
        else:
            player.executeMove(SweetMoves.GOALIE_SQUAT)
    return player.stay()

def squat(player):
    if player.firstFrame():
        player.brain.fallController.enabled = False
        player.executeMove(SweetMoves.GOALIE_SQUAT)

    return player.stay()
