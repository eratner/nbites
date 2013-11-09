/**
 * Class responsible for drawing more things on the field,
 * inherits from PaintField so that the field itself is already drawn.
 * Based on specs from the PlaybookCreator Class
 *
 * @author Wils Dawson
 * @date May 2013
 */

#pragma once

#include <QtGui>
#include <vector>

#include "FieldConstants.h"
#include "PlaybookConstants.h"

#include "common/PaintField.h"

namespace tool {
namespace playbook {

class PlaybookField : public tool_common::PaintField
{
    Q_OBJECT;

public:
    PlaybookField(int b_s, int g_w, int g_h, QWidget* parent = 0,
                  float scaleFactor_ = 1.f);

    PlaybookPosition** getRobots();
    PlaybookPosition* getRobot(int index);

    void setRobot(PlaybookPosition* robot, int index);
    void setNumActiveFieldPlayers(int num) {numActiveFieldPlayers = num;};
    void setBallX(short x) {ball_x = x;};
    void setBallY(short y) {ball_y = y;};

protected slots:
    void drawGoalie(bool on);

protected:
    void paintEvent(QPaintEvent* event);

    void paintGrid(QPaintEvent*event);

    void paintGoalie(QPaintEvent* event);
    void paintPlayers(QPaintEvent* event);
    void paintBall(QPaintEvent* event);

    static const float ROBOT_SIZE_X = 18.0f;
    static const float ROBOT_SIZE_Y = 35.0f;

    void paintRobot(QPaintEvent* event,
                    QPainter& painter,
                    int x, int y, int h,
                    Qt::GlobalColor c,
                    float sizeX = 18.0f, float sizeY = 35.0f);

private:
    bool shouldPaintGoalie;
    int numActiveFieldPlayers;
    short ball_x;
    short ball_y;

    int BOX_SIZE;
    int GRID_WIDTH;
    int GRID_HEIGHT;

    PlaybookPosition* robots[4];
};

} // namespace playbook
} // namespace tool
