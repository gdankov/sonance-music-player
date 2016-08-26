import sys
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtTest import QSignalSpy
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaPlayer

from gui.widgets import PlayerControlsWidget

app = QApplication(sys.argv)


class PlayerControlsWidgetTest(unittest.TestCase):
    def setUp(self):
        self.volume = 50
        self.state = QMediaPlayer.StoppedState
        self.widget = PlayerControlsWidget(self.volume, state=self.state)

    def test_defaults(self):
        self.assertEqual(self.widget.volumeSlider.value(), self.volume)
        self.assertEqual(self.widget.playerState, self.state)
        self.assertEqual(self.widget.durationLabel.text(), '00:00')
        self.assertEqual(self.widget.currentTimestampLabel.text(), '00:00')

        playButton = self.widget.playButton
        QTest.mouseClick(playButton, Qt.LeftButton)
        self.assertEqual(self.widget.playerState, QMediaPlayer.PlayingState)

        playButton = self.widget.playButton
        QTest.mouseClick(playButton, Qt.LeftButton)
        self.assertEqual(self.widget.playerState, QMediaPlayer.PausedState)

        playButton = self.widget.playButton
        QTest.mouseClick(playButton, Qt.LeftButton)
        self.assertEqual(self.widget.playerState, QMediaPlayer.PlayingState)

        self.assertEqual(self.widget.songTimestampSlider.value(), 0)

        self.widget.volumeSlider.setValue(120)
        self.assertEqual(self.widget.volumeSlider.value(), 100)

        self.widget.volumeSlider.setValue(-2)
        self.assertEqual(self.widget.volumeSlider.value(), 0)

        playButton.clicked.connect(self.onClicked)
        QTest.mouseClick(playButton, Qt.LeftButton)
        

    def onClicked(self, boolean):
        self.assertEqual(boolean, False)


if __name__ == "__main__":
    unittest.main()
