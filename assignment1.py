from vtkmodules.all import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QAction, QMdiSubWindow,\
    QToolBar, QLabel, QPushButton, QDockWidget, QGridLayout, QVBoxLayout, QLineEdit, QTextEdit, QWidget, QToolBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import Qt
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import sys
import vtk


class MainWindow(QMainWindow):
    count = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("background-color: cornflowerblue;")
        self.setWindowIcon(QtGui.QIcon('envproject\project\Assignment\Assignment1\icons\icons8-icons-64.png'))
        self.setWindowTitle("Scientific Data Visualizer")

        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)
        self.resize(1200, 800)

        self.MenuBar()
        self.ToolBar()
        self.DockerWidget()
        self.show()

    #ADD MENU BAR FUNCTION
    def MenuBar(self):
        Bar = self.menuBar()
        File = Bar.addMenu('File')
        FileNew = self.CreateAction('New', 'envproject\project\Assignment\Assignment1\icons\photo_lbjq9qty042w_32.png', 'Ctrl+N', self.OpenFile)
        FileExit = self.CreateAction('Exit', 'envproject\project\Assignment\Assignment1\icons\exit_cl2hxz63ygau_32.png', 'Ctrl+Q', self.close)
        self.AddAction(File, (FileNew, FileExit))

        View = Bar.addMenu('View')
        ViewShortcut = self.CreateAction('Show Navigation', 'envproject\project\Assignment\Assignment1\icons\editor_d7asq04macik_32.png', 'F2', self.ToolBar)
        ViewVariable = self.CreateAction('Show Tools', 'envproject\project\Assignment\Assignment1\icons\settings.png', 'F4', self.DockerWidget)
        ViewTile = self.CreateAction('Tiled Mode', 'envproject\project\Assignment\Assignment1\icons\squares-couple-overlapped-shapes.png', 'Ctrl+T', self.ShowTile)
        self.AddAction(View, (ViewShortcut, ViewVariable, ViewTile))

    #ADD TOOL BAR FUNCTION
    def ToolBar(self):
        naviBar = self.addToolBar("Navigation")
        newAction = self.CreateAction('New', 'envproject\project\Assignment\Assignment1\icons\photo_lbjq9qty042w_32.png', 'Ctrl+N', self.OpenFile)
        tileAction = self.CreateAction('Tiled Mode', 'envproject\project\Assignment\Assignment1\icons\squares-couple-overlapped-shapes.png', 'Ctrl+T', self.ShowTile)
        toolAction = self.CreateAction('Show Tools', 'envproject\project\Assignment\Assignment1\icons\settings.png', 'F4', self.DockerWidget)
        boxAction = self.CreateAction('3D Box','envproject\project\Assignment\Assignment1\icons\cube.png', 'F1', self.Box)
        axisAction = self.CreateAction('3D Axis','envproject\project\Assignment\Assignment1\icons\icons8-move-on-axis-48.png', 'F7', self.Axis)
        zoomiAction = self.CreateAction('Zoom In','envproject\project\Assignment\Assignment1\icons\zoom_in_udmmewm4z1vl_32.png', 'F3', self.ZoomIn)
        zoomoAction = self.CreateAction('Zoom Out','envproject\project\Assignment\Assignment1\icons\zoom_out_e5holzooscia_32.png', 'F5', self.ZoomOut)
        self.AddAction(naviBar, (newAction, tileAction, toolAction, boxAction, axisAction, zoomiAction, zoomoAction))
        naviBar.setFloatable(False)

    #CREATE ACTION FOR THE FUNCTION
    def CreateAction(self, text, icon = None, shortcut = None, implement = None, signal = 'triggered'):
        action = QtWidgets.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if implement is not None:
            getattr(action, signal).connect(implement)
        return action

    #ACTION FOR THE FUNCTION
    def AddAction(self, dest, actions):
        for action in actions:
            if action is None:
                dest.addSeperator()
            else:
                dest.addAction(action)

    #APPLY TILE MODE FOR THE IMAGE
    def ShowTile(self):
        self.mdi.tileSubWindows()

    #OPEN FILE
    def OpenFile(self):
        MainWindow.count = MainWindow.count + 1
        self.filename = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')

        if self.filename:
            self.vtk(self.filename)

    #OPEN VTK IMAGE WINDOW
    def vtk(self, filename):
        self.sub = QMdiSubWindow()
        self.frame = Qt.QFrame()

        self.addDataset(filename)
        self.vtkWidget = QVTKRenderWindowInteractor (self.frame)
        self.sub.setWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.2, 0.2, 0.2)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        #SET TITLEBAR
        self.sub.setWindowTitle("Dataset " + str(MainWindow.count))

        self.imageData = vtk.vtkImageData()
        self.reader = vtk.vtkDICOMImageReader()

        self.volumeMapper = vtk.vtkSmartVolumeMapper()
        self.volumeProperty = vtk.vtkVolumeProperty()
        self.gradientOpacity = vtk.vtkPiecewiseFunction()
        self.scalarOpacity = vtk.vtkPiecewiseFunction()
        self.color = vtk.vtkColorTransferFunction()
        self.volume = vtk.vtkVolume()
        self.reader.SetDirectoryName(filename)
        self.reader.SetDataScalarTypeToUnsignedShort()
        self.reader.UpdateWholeExtent()
        self.reader.Update()
        self.imageData.ShallowCopy(self.reader.GetOutput())

        self.volumeMapper.SetBlendModeToComposite()
        self.volumeMapper.SetRequestedRenderModeToGPU()
        self.volumeMapper.SetInputData(self.imageData)
        self.volumeProperty.ShadeOn()
        self.volumeProperty.SetInterpolationTypeToLinear()
        self.volumeProperty.SetAmbient(0.1)
        self.volumeProperty.SetDiffuse(0.9)
        self.volumeProperty.SetSpecular(0.2)
        self.volumeProperty.SetSpecularPower(10.0)
        self.gradientOpacity.AddPoint(0.0, 0.0)
        self.gradientOpacity.AddPoint(2000.0, 1.0)
        self.volumeProperty.SetGradientOpacity(self.gradientOpacity)
        self.scalarOpacity.AddPoint(-800.0, 0.0)
        self.scalarOpacity.AddPoint(-750.0, 1.0)
        self.scalarOpacity.AddPoint(-350.0, 1.0)
        self.scalarOpacity.AddPoint(-300.0, 0.0)
        self.scalarOpacity.AddPoint(-200.0, 0.0)
        self.scalarOpacity.AddPoint(-100.0, 1.0)
        self.scalarOpacity.AddPoint(1000.0, 0.0)
        self.scalarOpacity.AddPoint(2750.0, 0.0)
        self.scalarOpacity.AddPoint(2976.0, 1.0)
        self.scalarOpacity.AddPoint(3000.0, 0.0)
        self.volumeProperty.SetScalarOpacity(self.scalarOpacity)
        self.color.AddRGBPoint(-750.0, 0.08, 0.05, 0.03)
        self.color.AddRGBPoint(-350.0, 0.39, 0.25, 0.16)
        self.color.AddRGBPoint(-200.0, 0.80, 0.80, 0.80)
        self.color.AddRGBPoint(2750.0, 0.70, 0.70, 0.70)
        self.color.AddRGBPoint(3000.0, 0.35, 0.35, 0.35)
        self.volumeProperty.SetColor(self.color)
        self.volume.SetMapper(self.volumeMapper)
        self.volume.SetProperty(self.volumeProperty)
        self.ren.AddVolume(self.volume)
        self.ren.ResetCamera()

        outline = vtk.vtkOutlineFilter()
        outline.SetInputConnection(self.reader.GetOutputPort())

        outlineMapper = vtk.vtkPolyDataMapper()
        outlineMapper.SetInputConnection(outline.GetOutputPort())

        self.outlineActor = vtk.vtkActor()
        self.outlineActor.SetMapper(outlineMapper)
        self.outlineActor.GetProperty().SetColor(1, 1, 1)
        self.ren.AddActor(self.outlineActor)
        self.ren.ResetCamera()
        self.outlineActor.VisibilityOff()

        self.mdi.addSubWindow(self.sub)
        self.sub.show()
        self.iren.Initialize()
        self.iren.Start()

    #ADD DOCKER WIDGET FUNCTION
    def DockerWidget(self):
        dockWid = QDockWidget('Tools', self)
        layout = QGridLayout()
        styleSheet = """
                        QToolBox::tab {
                            border: 1px solid #C4C4C4;
                            border-bottom-color: RGB(0, 0, 225);
                        }
                        QToolBox::tab:selected {
                            background-color: #4E14C2;
                            color: white;
                            border-bottom-color: none;
                        }
        """

        toolbox = QToolBox()
        layout.addWidget(toolbox, 0, 0)

        #SET TRANSFORMATION TAB
        w1 = QWidget()
        scale = QLabel('Scale')
        sx_coord = QLabel('X')
        sy_coord = QLabel('Y')
        sz_coord = QLabel('Z')
        rotate = QLabel('Rotate')
        rx_coord = QLabel('X')
        ry_coord = QLabel('Y')
        rz_coord = QLabel('Z')
        translate = QLabel('Translate')
        tx_coord = QLabel('X')
        ty_coord = QLabel('Y')
        tz_coord = QLabel('Z')

        self.scaleX = QLineEdit(self)
        self.scaleY = QLineEdit(self)
        self.scaleZ = QLineEdit(self)
        self.scaleX.setStyleSheet("QLineEdit" "{" "background : lightcyan;" "}")
        self.scaleY.setStyleSheet("QLineEdit" "{" "background : lightcyan;" "}")
        self.scaleZ.setStyleSheet("QLineEdit" "{" "background : lightcyan;" "}")
        scalee = QPushButton('Apply', self)
        scalee.setStyleSheet("background-color : mediumvioletred; color: white;")
        scalee.clicked.connect(self.ScaleXYZ)
        self.scaleX.setFixedWidth(30)
        self.scaleY.setFixedWidth(30)
        self.scaleZ.setFixedWidth(30)
        self.rotateX = QLineEdit(self)
        self.rotateY = QLineEdit(self)
        self.rotateZ = QLineEdit(self)
        self.rotateX.setStyleSheet("QLineEdit" "{" "background : lightcyan;" "}")
        self.rotateY.setStyleSheet("QLineEdit" "{" "background : lightcyan;" "}")
        self.rotateZ.setStyleSheet("QLineEdit" "{" "background : lightcyan;" "}")
        rotatee = QPushButton('Apply', self)
        rotatee.setStyleSheet("background-color : mediumvioletred; color: white;")
        rotatee.clicked.connect(self.RotateXYZ)
        self.rotateX.setFixedWidth(30)
        self.rotateY.setFixedWidth(30)
        self.rotateZ.setFixedWidth(30)
        self.translateX = QLineEdit(self)
        self.translateY = QLineEdit(self)
        self.translateZ = QLineEdit(self)
        self.translateX.setStyleSheet("QLineEdit" "{" "background : lightcyan;" "}")
        self.translateY.setStyleSheet("QLineEdit" "{" "background : lightcyan;" "}")
        self.translateZ.setStyleSheet("QLineEdit" "{" "background : lightcyan;" "}")
        translatee = QPushButton('Apply', self)
        translatee.setStyleSheet("background-color : mediumvioletred; color: white;")
        translatee.clicked.connect(self.TranslateXYZ)
        self.translateX.setFixedWidth(30)
        self.translateY.setFixedWidth(30)
        self.translateZ.setFixedWidth(30)

        #SET POSITION COORDINATE FOR THE TRANSFORMATION TOOLS
        grid = QGridLayout()
        grid.setSpacing(5)

        grid.addWidget(scale, 1, 0)
        grid.addWidget(sx_coord, 1, 1)
        grid.addWidget(self.scaleX, 1, 2)
        grid.addWidget(sy_coord, 1, 3)
        grid.addWidget(self.scaleY, 1, 4)
        grid.addWidget(sz_coord, 1, 5)
        grid.addWidget(self.scaleZ, 1, 6)
        grid.addWidget(scalee, 1, 7)

        grid.addWidget(rotate, 2, 0)
        grid.addWidget(rx_coord, 2, 1)
        grid.addWidget(self.rotateX, 2, 2)
        grid.addWidget(ry_coord, 2, 3)
        grid.addWidget(self.rotateY, 2, 4)
        grid.addWidget(rz_coord, 2, 5)
        grid.addWidget(self.rotateZ, 2, 6)
        grid.addWidget(rotatee, 2, 7)

        grid.addWidget(translate, 3, 0)
        grid.addWidget(tx_coord, 3, 1)
        grid.addWidget(self.translateX, 3, 2)
        grid.addWidget(ty_coord, 3, 3)
        grid.addWidget(self.translateY, 3, 4)
        grid.addWidget(tz_coord, 3, 5)
        grid.addWidget(self.translateZ, 3, 6)
        grid.addWidget(translatee, 3, 7)
        w1.setLayout(grid)

        toolbox.addItem(w1, 'Transformation Tool')

        #SET DATASET TAB
        w2 = QWidget()
        self.grid_d = QGridLayout()
        self.grid_d.setSpacing(5)

        filename = 'Unknown'
        self.addDataset(filename)

        w2.setLayout(self.grid_d)
        toolbox.addItem(w2, 'Dataset')

        toolbox.setCurrentIndex(0)
        self.setStyleSheet(styleSheet)
        self.setLayout(layout)

        dockWid.setWidget(toolbox)
        dockWid.setFloating(False)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dockWid)

    #ADD DATASET FUNCTION
    def addDataset(self, filename):
        file_loc = QLabel('File Location ' + str(MainWindow.count) + ': ')
        location = QLabel(filename)

        self.grid_d.addWidget(file_loc, MainWindow.count, 0)
        self.grid_d.addWidget(location, MainWindow.count, 1)

        return self.grid_d

    #ZOOM IN FUNCTION
    def ZoomIn(self):
        self.ren.GetActiveCamera().Zoom(1.5)

    #ZOOM OUT FUNCTION
    def ZoomOut(self):
        self.ren.GetActiveCamera().Zoom(0.8)

    #ADD 3D AXIS FUNCTION
    def Axis(self):
        axesActor = vtk.vtkAxesActor()
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(axesActor)
        self.axes.SetInteractor(self.iren)
        self.axes.EnabledOn()
        self.axes.InteractiveOn()
        self.ren.ResetCamera()

    #ADD 3D BOX FUNCTION
    def Box(self):
        outline = vtk.vtkOutlineFilter()
        outline.SetInputConnection(self.reader.GetOutputPort())

        outlineMapper = vtk.vtkPolyDataMapper()
        outlineMapper.SetInputConnection(outline.GetOutputPort())

        self.outlineActor = vtk.vtkActor()
        self.outlineActor.SetMapper(outlineMapper)
        self.outlineActor.GetProperty().SetColor(1, 1, 1)
        self.ren.AddActor(self.outlineActor)
        self.ren.ResetCamera()

    #SCALE IMAGE FUNCTION
    def ScaleXYZ(self):
        x = int(self.scaleX.text())
        y = int(self.scaleY.text())
        z = int(self.scaleZ.text())
        self.volume.SetOrientation(x, y, z)
        self.ren.Render()
        self.ren.EraseOff()
        self.outlineActor.SetScale(x, y, z)
        self.volume.SetScale(x, y, z)
        self.ren.Render()
        self.ren.EraseOn()

    #ROTATE IMAGE FUNCTION
    def RotateXYZ(self):
        x = int(self.rotateX.text())
        y = int(self.rotateY.text())
        z = int(self.rotateZ.text())
        self.outlineActor.SetOrientation(x, y, z)
        self.volume.SetOrientation(x, y, z)
        self.ren.Render()
        self.ren.EraseOff()

        self.volume.RotateX(x)
        self.volume.RotateY(y)
        self.volume.RotateZ(z)
        self.outlineActor.RotateX(x)
        self.outlineActor.RotateY(y)
        self.outlineActor.RotateZ(z)
        self.ren.Render()
        self.ren.EraseOn()

    #TRANSLATE IMAGE FUNCTION
    def TranslateXYZ(self):
        x = int(self.translateX.text())
        y = int(self.translateY.text())
        z = int(self.translateZ.text())
        self.ren.Render()
        self.ren.EraseOff()
        self.outlineActor.SetPosition(x, y, z)
        self.volume.SetPosition(x, y, z)
        self.ren.Render()
        self.ren.EraseOn()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    appwin = MainWindow()
    sys.exit(app.exec())