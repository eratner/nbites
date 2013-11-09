/**
 * Class responsible for creating, viewing, and editing a playbook.
 *
 * @author Wils Dawson
 * @date   May 2013
 */
#pragma once

#include <QtGui>
#include <QCheckBox>
#include <vector>
#include <QPixmap>

#include "PlaybookField.h"
#include "PlaybookModel.h"
#include "PlaybookConstants.h"

namespace tool{
namespace playbook{

static const int BOX_SIZE = 100;  // Size in cm for each grid box.

static const int GRID_WIDTH  = (int(FIELD_WHITE_WIDTH) / BOX_SIZE) + 2;
static const int GRID_HEIGHT = (int(FIELD_WHITE_HEIGHT)/ BOX_SIZE) + 2;

static const int KEY_LABEL_WIDTH = 50;
static const int KEY_LABEL_HEIGHT = 10;

class PlaybookCreator : public QWidget
{
    Q_OBJECT;

public:
    PlaybookCreator(QWidget* parent = 0);

protected slots:
    void updatePositions();
    void updatePositions(bool noCheck);
    void updatePositionsCheck(bool check);
    void refreshTextDefender();
    void refreshTextOffender();
    void refreshTextMiddie();
    void refreshTextChaser();
    void refreshTextBall();
    void refreshTextPriority();
    void setDefenderXPosition();
    void setDefenderYPosition();
    void setDefenderHPosition();
    void setMiddieXPosition();
    void setMiddieYPosition();
    void setMiddieHPosition();
    void setOffenderXPosition();
    void setOffenderYPosition();
    void setOffenderHPosition();
    void setChaserXPosition();
    void setChaserYPosition();
    void setChaserHPosition();
    void setBallX();
    void setBallY();
    void setOneFieldPlayer(bool checked);
    void setTwoFieldPlayers(bool checked);
    void setThreeFieldPlayers(bool checked);
    void setFourFieldPlayers(bool checked);
    void setPriorityList();
    void writeToFile(bool checked);
    void updateGoalieLock(bool checked);

protected:
    PlaybookField* fieldPainter;
    PlaybookModel* model;

    QHBoxLayout* mainLayout;
    QHBoxLayout* field;
    QVBoxLayout* settings;
    QVBoxLayout* playerSettings;

    QPushButton* undoBtn;
    QPushButton* loadBtn;
    QPushButton* saveBtn;
    QCheckBox* lockDefender;
    QCheckBox* lockMiddie;
    QCheckBox* lockOffender;
    QCheckBox* lockChaser;
    QCheckBox* lockPriority;
    QCheckBox* goalie;
    QLineEdit* editDefenderX;
    QLineEdit* editDefenderY;
    QLineEdit* editDefenderH;
    QLineEdit* editMiddieX;
    QLineEdit* editMiddieY;
    QLineEdit* editMiddieH;
    QLineEdit* editOffenderX;
    QLineEdit* editOffenderY;
    QLineEdit* editOffenderH;
    QLineEdit* editChaserX;
    QLineEdit* editChaserY;
    QLineEdit* editChaserH;
    QRadioButton* oneFieldPlayer;
    QRadioButton* twoFieldPlayers;
    QRadioButton* threeFieldPlayers;
    QRadioButton* fourFieldPlayers;
    QLineEdit* editBallX;
    QLineEdit* editBallY;
    QLineEdit* editPriority;

private:
    bool havePlaybook;
    void updateRobotPositions();
    void updateLockedPositions();
    void updateLockedPriority();
    void refreshTextAll();
};

}
}
