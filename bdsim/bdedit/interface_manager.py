# Library imports
import os
import json
import subprocess

# PyQt5 imports
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# BdEdit imports
from bdsim.bdedit.Icons import *
from bdsim.bdedit.interface import Interface


# Todo - update documentation for this new class, handles any edits/saves/undo/redo within interface.
#  Also handles the run related functionality now
# =============================================================================
#
#   Defining the Interface Manager Class,
#
# =============================================================================
class InterfaceWindow(QMainWindow):
    def __init__(self, resolution, debug=False):
        super().__init__()

        # The name of the current model is initially set to None, this is then
        # overwritten when the model is saved
        self.filename = None

        self.initUI(resolution, debug)

    def initUI(self, resolution, debug):
        # create node editor widget
        self.interface = Interface(resolution, debug, self)
        self.interface.scene.addHasBeenModifiedListener(self.updateApplicationName)
        self.setCentralWidget(self.interface)

        self.toolbar = QToolBar()
        self.fontSizeBox = QSpinBox()

        # Create the toolbar action items and the toolbar itself
        self.createActions()
        self.createToolbar()

        # set window properties
        # self.setWindowIcon(QIcon(":/Icons_Reference/Icons/bdsim_icon.png"))
        self.updateApplicationName()
        self.show()

    def createActions(self):
        # Creates basic actions related to saving/loading files
        self.actNew = QAction('&New', self, shortcut='Ctrl+N', toolTip="Create new model", triggered=self.newFile)
        self.actOpen = QAction('&Open', self, shortcut='Ctrl+O', toolTip="Open model", triggered=self.loadFromFile)
        self.actSave = QAction('&Save', self, shortcut='Ctrl+S', toolTip="Save model", triggered=self.saveToFile)
        self.actSaveAs = QAction('&Save As', self, shortcut='Ctrl+Shift+S', toolTip="Save model as", triggered=self.saveAsToFile)
        self.actExit = QAction('&Exit', self, shortcut='Ctrl+Q', toolTip="Exit bdedit", triggered=self.close)

        # Actions related to editing files (undo/redo)
        self.actUndo = QAction('&Undo', self, shortcut='Ctrl+Z', toolTip="Undo last action", triggered=self.editUndo)
        self.actRedo = QAction('&Redo', self, shortcut='Ctrl+Shift+Z', toolTip="Redo last action", triggered=self.editRedo)
        self.actDelete = QAction('&Delete', self, toolTip="Delete selected items", triggered=self.editDelete)
        self.actDelete.setShortcuts({ QKeySequence("Delete"), QKeySequence("Backspace") })

        # Miscelanious actions
        self.actFlipBlocks = QAction('&Flip Blocks', self, shortcut='F', toolTip="Flip selected blocks", triggered=self.miscFlip)
        self.actScreenshot = QAction('&Screenshot', self, shortcut='P', toolTip="Take and save a screenshot", triggered=self.miscScreenshot)
        self.actWireOverlaps = QAction('&Toggle Wire Overlaps', self, shortcut='I', toolTip="Toggle wire overlap mode", triggered=self.miscEnableOverlaps, checkable=True)
        self.actHideConnectors = QAction('&Toggle Connectors', self, shortcut='H', toolTip="Toggle connectors (hidden/visible)", triggered=self.miscHideConnectors, checkable=True)
        self.actDisableBackground = QAction('&Disable Background', self, shortcut='T', toolTip="Toggle backgrounds (grey & grid / white & no grid)", triggered=self.miscToggleBackground, checkable=True)
        self.actRunButton = QAction(QIcon(":/Icons_Reference/Icons/run.png"), '&Run', self, shortcut='R', toolTip="Run model", triggered=self.runButton)

        # Actions related to formatting floating text labels
        self.actAlignLeft = QAction(QIcon(":/Icons_Reference/Icons/left_align.png"), '&Left', self, toolTip="Left align floating text", triggered= lambda: self.textAlignment("AlignLeft"))
        self.actAlignCenter = QAction(QIcon(":/Icons_Reference/Icons/center_align.png"), '&Center', self, toolTip="Center align floating text", triggered= lambda: self.textAlignment("AlignCenter"))
        self.actAlignRight = QAction(QIcon(":/Icons_Reference/Icons/right_align.png"), '&Right', self,  toolTip="Right align floating text", triggered= lambda: self.textAlignment("AlignRight"))

        self.actBoldText = QAction(QIcon(":/Icons_Reference/Icons/bold.png"), '&Bold', self, shortcut='Ctrl+B', toolTip="Bold floating text", triggered=self.textBold)
        self.actUnderLineText = QAction(QIcon(":/Icons_Reference/Icons/underline.png"), '&Underline', self, shortcut='Ctrl+U', toolTip="Underline floating text", triggered=self.textUnderline)
        self.actItalicText = QAction(QIcon(":/Icons_Reference/Icons/italics.png"), '&Italicize', self, shortcut='Ctrl+I', toolTip="Italicize floating text", triggered=self.textItalicize)

        self.actFontType = QAction('&Font', self, toolTip="Choose font stype for floating text", triggered=self.textFontStyle)
        self.fontSizeBox.setValue(14); self.fontSizeBox.valueChanged.connect(self.textFontSize)
        self.actTextColor = QAction(QIcon(":/Icons_Reference/Icons/color_picker.png"), '&Text Color', self, toolTip="Choose text color", triggered=self.textColor)
        self.actRemoveFormat = QAction(QIcon(":/Icons_Reference/Icons/clear_format.png"), '&Clear Format', self, toolTip="Reset text to default format", triggered=self.removeFormat)


    def createToolbar(self):
        self.createFileMenu()
        # self.createEditMenu()
        self.createToolsMenu()
        self.createToolbarItems()

    def createFileMenu(self):
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.setToolTipsVisible(True)
        self.fileMenu.addAction(self.actNew)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actOpen)
        self.fileMenu.addAction(self.actSave)
        self.fileMenu.addAction(self.actSaveAs)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actExit)

    # def createEditMenu(self):
    #     menubar = self.menuBar()
    #     self.editMenu = menubar.addMenu('&Edit')
    #     self.editMenu.setToolTipsVisible(True)
    #     self.editMenu.addAction(self.actUndo)
    #     self.editMenu.addAction(self.actRedo)
    #     self.editMenu.addSeparator()
    #     self.editMenu.addAction(self.actDelete)

    def createToolsMenu(self):
        menubar = self.menuBar()
        self.toolsMenu = menubar.addMenu('Tools')
        self.toolsMenu.setToolTipsVisible(True)
        self.toolsMenu.addAction(self.actFlipBlocks)
        self.toolsMenu.addAction(self.actScreenshot)
        self.toolsMenu.addSeparator()
        self.toolsMenu.addAction(self.actWireOverlaps)
        self.toolsMenu.addAction(self.actHideConnectors)
        self.toolsMenu.addAction(self.actDisableBackground)
        self.toolsMenu.addSeparator()
        self.toolsMenu.addAction(self.actDelete)

    def createToolbarItems(self):
        toolbar = self.addToolBar('ToolbarItems')
        toolbar.addAction(self.actRunButton)
        toolbar.addSeparator()
        toolbar.addAction(self.actAlignLeft)
        toolbar.addAction(self.actAlignCenter)
        toolbar.addAction(self.actAlignRight)
        toolbar.addSeparator()
        toolbar.addAction(self.actBoldText)
        toolbar.addAction(self.actUnderLineText)
        toolbar.addAction(self.actItalicText)
        toolbar.addSeparator()
        toolbar.addAction(self.actFontType)
        toolbar.addWidget(self.fontSizeBox)
        toolbar.addSeparator()
        toolbar.addAction(self.actTextColor)
        toolbar.addAction(self.actRemoveFormat)

    def updateApplicationName(self):
        name = "bdedit - "
        if self.filename is None:
            name += "untitled.bd"
        else:
            name += os.path.basename(self.filename)

        if self.centralWidget().scene.has_been_modified:
            name += "*"

        self.setWindowTitle(name)

    def closeEvent(self, event):
        if self.exitingWithoutSave():
            event.accept()
        else:
            event.ignore()

    def isModified(self):
        return self.centralWidget().scene.has_been_modified

    def exitingWithoutSave(self):
        if not self.isModified():
            return True

        msg_prompt = QMessageBox.warning(self, "Exiting without saving work.",
                "The document has been modified.\nDo you want to save your changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
              )

        if msg_prompt == QMessageBox.Save:
            return self.saveToFile()
        elif msg_prompt == QMessageBox.Cancel:
            return False

        return True

    # -----------------------------------------------------------------------------
    def runButton(self):
        self.saveToFile()

        main_block_found = False

        # Go through blocks within scene, if a main block exists, extract the file_name from the main block
        for block in self.centralWidget().scene.blocks:
            if block.block_type in ["Main", "MAIN"]:
                main_block_found = True
                main_file_name = block.parameters[0][2]

                try:
                    # Check if given file_name from the main block, contains a file extension
                    file_name, extension = os.path.splitext(main_file_name)

                    if not extension:
                        main_file_name = os.path.join(main_file_name + ".py")

                    model_name = os.path.basename(self.filename)
                    subprocess.run(['python', main_file_name, model_name], shell=True)
                    print("Invoking subproces with, Python file as:", main_file_name, " | Model name as:", model_name)

                except Exception:
                    print("Detected Main block in model, but no file name was given. Subprocess cancled.")
                    return

        if not main_block_found:
            try:
                model_name = os.path.basename(self.filename)
                subprocess.run(['python', 'bdrun.py', model_name], shell=True)
                print("Model does not contain a main block. Starting bdrun as a subprocess.")
            except Exception:
                print("Bdrun cannot start without model being saved. Subprocess cancled.")
                return

    # -----------------------------------------------------------------------------
    def newFile(self):
        if self.exitingWithoutSave():
            self.centralWidget().scene.clear()
            self.filename = None
            self.updateApplicationName()

    # -----------------------------------------------------------------------------
    def loadFromFilePath(self, filepath):
        """
        This method is only used when loading a file from the command line. It will
        check if the file at the given path exists, and if so, will load its contents.
        """

        if self.exitingWithoutSave():
            # Check if file at given path exists, if so, run the deserializing method
            if os.path.isfile(filepath):
                self.centralWidget().scene.loadFromFile(filepath)
                self.filename = filepath
                self.updateApplicationName()

    # -----------------------------------------------------------------------------
    def loadFromFile(self):
        """
        This method opens a QFileDialog window, prompting the user to select a file
        to load from.
        """

        if self.exitingWithoutSave():
            # The filename of the selected file is grabbed
            fname, filter = QFileDialog.getOpenFileName(self)
            if fname == '':
                return

            # And the method for deserializing from a file is called, feeding in the
            # extracted filename from above
            if os.path.isfile(fname):
                self.centralWidget().scene.loadFromFile(fname)
                self.filename = fname
                self.updateApplicationName()

    # -----------------------------------------------------------------------------
    def saveToFile(self):
        """
        This method calls the method from within the ``Scene`` to save a copy of the
        current Scene, with all its items under a file with the current filename. If
        this is the first time a user is saving their file, they will be prompted to
        name the file and to choose where it will be saved.
        """

        if self.filename is None: return self.saveAsToFile()
        self.centralWidget().scene.saveToFile(self.filename)
        self.updateApplicationName()
        #self.statusBar().showMessage("Successfully saved %s" % self.filename)
        return True

    # -----------------------------------------------------------------------------
    def saveAsToFile(self):
        """
        This method opens a QFileDialog window, prompting the user to enter a name
        under which the current file will be saved. This file will automatically be
        given a .json file type.
        """

        # The allowable file types are defined below
        file_types = "bdedit files(*.bd);;JSON files (*.json)"
        fname, _ = QFileDialog.getSaveFileName(self, 'untitled.bd', filter=file_types)

        # The filename is extracted from the QFileDialog
        if fname == '':
            return False

        # The filename of the scene is stored as a variable inside the Interface, and
        # the self.saveToFile method is called (which will call the self.scene.saveToFile
        # method from within the Scene, which will serialize the contents of the Scene
        # into a JSON file with the provided file name).
        self.filename = fname
        self.saveToFile()
        return True

    # -----------------------------------------------------------------------------
    def editUndo(self):
        pass

    def editRedo(self):
        pass

    def editDelete(self):
        if self.interface:
            self.interface.canvasView.deleteSelected()
            self.interface.canvasView.intersectionTest()

    # -----------------------------------------------------------------------------
    def miscFlip(self):
        if self.interface:
            self.interface.canvasView.intersectionTest()
            self.interface.canvasView.flipBlockSockets()

    def miscEnableOverlaps(self):
        if self.interface:
            self.interface.scene.grScene.enable_intersections = not self.interface.scene.grScene.enable_intersections

    def miscScreenshot(self):
        if self.interface:
            if self.filename is None:
                print("Please save your model before taking a screenshot, then try again.")
                self.saveToFile()
            else:
                self.interface.save_image(self.filename)


    def miscHideConnectors(self):
        if self.interface:
            if self.actHideConnectors.isChecked():
                # Set variable for hiding connector blocks to True
                self.interface.scene.hide_connector_blocks = True
            else:
                # Set variable for hiding connector blocks to False
                self.interface.scene.hide_connector_blocks = False

    def miscToggleBackground(self):
        """
        This method is called to toggle the type of background drawn within
        the ``Scene``. The options are:

        - Enabled: light grey background with grid lines
        - Disabled: white background with no grid lines
        """

        # The mode of the Scene is called to be updated to whatever value was
        # selected from the grid_mode dropdown menu (Light, Dark, Off)
        self.interface.scene.grScene.updateMode(self.actDisableBackground.isChecked())
        # For each block within the Scene, the mode of their outline is also updated
        for eachBlock in self.interface.scene.blocks:
            # If the block has a mode (Connector Blocks do not)
            if not (eachBlock.block_type == "CONNECTOR" or eachBlock.block_type == "Connector"):
                eachBlock.grBlock.updateMode(self.actDisableBackground.isChecked())

    # -----------------------------------------------------------------------------
    def textAlignment(self, alignment):
        if self.interface.scene.floating_labels:
            # Make a map of alignment text to actual Qt alignments
            map = {
                "AlignLeft": Qt.AlignLeft,
                "AlignCenter": Qt.AlignCenter,
                "AlignRight": Qt.AlignRight,
            }

            # Iterate through each floating label item and if the label is selected,
            # then set the alignment of its contents
            for label in self.interface.scene.floating_labels:
                self.checkSelection(label)
                label.content.text_edit.setAlignment(map[alignment])

    def textBold(self):
        if self.interface.scene.floating_labels:
            for label in self.interface.scene.floating_labels:
                self.checkSelection(label)
                if label.content.text_edit.fontWeight() != QFont.Bold:
                    label.content.text_edit.setFontWeight(QFont.Bold)
                else:
                    label.content.text_edit.setFontWeight(QFont.Normal)

    def textUnderline(self):
        if self.interface.scene.floating_labels:
            for label in self.interface.scene.floating_labels:
                self.checkSelection(label)
                current_state = label.content.text_edit.fontUnderline()
                label.content.text_edit.setFontUnderline(not(current_state))

    def textItalicize(self):
        if self.interface.scene.floating_labels:
            for label in self.interface.scene.floating_labels:
                self.checkSelection(label)
                current_state = label.content.text_edit.fontItalic()
                label.content.text_edit.setFontItalic(not(current_state))

    def textFontStyle(self):
        font, ok = QFontDialog.getFont()
        if ok:
            if self.interface.scene.floating_labels:
                for label in self.interface.scene.floating_labels:
                    self.checkSelection(label)
                    label.content.text_edit.setFont(font)
                    label.content.updateText()

    def textFontSize(self):
        if self.interface.scene.floating_labels:
            for label in self.interface.scene.floating_labels:
                self.checkSelection(label)
                value = self.fontSizeBox.value()
                label.content.text_edit.setFontPointSize(value)

    def textColor(self):
        color = QColorDialog.getColor()

        if color.isValid():
            if self.interface.scene.floating_labels:
                for label in self.interface.scene.floating_labels:
                    self.checkSelection(label)
                    label.content.text_edit.setTextColor(color)

    def removeFormat(self):
        if self.interface.scene.floating_labels:
            for label in self.interface.scene.floating_labels:
                self.checkSelection(label)
                label.content.setDefaultFormatting()

    def checkSelection(self, label):
        if label.grContent.isSelected():
            label.content.text_edit.selectAll()
