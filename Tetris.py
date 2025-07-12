import math

from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QPushButton, QVBoxLayout,QWidget,QDialog
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal,QTimer
from PyQt5.QtGui import QPainter, QColor,QMovie
import sys, random
from PyQt5 import uic

class menu(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi("./ui/menu.ui")

        self.btn_start = self.ui.pushButton
        self.btn_help = self.ui.pushButton_2

        self.btn_help.clicked.connect(self.show_help)

        self.label = self.ui.label_2
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)
        self.movie = QMovie("./img/title.gif")
        self.label.setMovie(self.movie)
        self.movie.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.pauseGif)
        self.timer.start(3000)

    def pauseGif(self):
        self.movie.stop()

    def show_help(self):
        self.help = Help()
        self.help.ui.show()

class Help(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi("./ui/help.ui")

class over(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi("./ui/over.ui")

class Tetris(QMainWindow):

    def __init__(self):
        super().__init__()

    def initUI(self):

        # 创建了一个Board类的实例，并设置为应用的中心组件
        self.tboard = Board(self)
        self.setCentralWidget(self.tboard)
        # 创建一个statusbar来显示三种信息：消除的行数，游戏暂停状态或者游戏结束状态
        # 自定义信号 用在和Board类交互
        self.statusbar = self.statusBar()
        self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)

        self.tboard.start()  # 初始化游戏

        self.resize(300, 660)  # 设置窗口大小
        # self.setGeometry(300, 300, 500, 300)
        self.center()  # 窗口居中
        self.setWindowTitle('Tetris')
        self.show()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        # 将窗口放到中间
        self.move((screen.width() - size.width()) // 2,
                  (screen.height() - size.height()) // 2)

class Board(QFrame):
    # 自定义信号 往statusbar显示信息
    msg2Statusbar = pyqtSignal(str)
    BoardWidth = 10  # 指界面宽度可以容纳10个小方块
    BoardHeight = 22  # 指界面高度可以容纳22个小方块
    Speed = 300 # 掉落速度

    def __init__(self, parent):
        super().__init__(parent)

        self.initBoard()

    def initBoard(self):
        self.timer = QBasicTimer()  # 定时器
        self.isWaitingAfterLine = False  # 表示是否在等待消除行
        #（0,0）方块
        self.curX = 0  # 目前x坐标
        self.curY = 0  # 目前y坐标
        self.numLinesRemoved = 0  # 表示消除的行数，也就是分数
        self.board = []  # 存储每个方块位置的形状，默认应该为0，下标代表方块坐标x*y

        self.setFocusPolicy(Qt.StrongFocus)  # 设置焦点，使用tab键和鼠标左键都可以获取焦点
        self.isStarted = False  # 表示游戏是否在运行状态
        self.isPaused = False  # 表示游戏是否在暂停状态
        self.clearBoard()  # 清空界面的全部方块

    # board的大小可以动态的改变。所以方格的大小也应该随之变化。squareWidth()计算并返回每个块应该占用多少像素--也即Board.BoardWidth。
    def squareWidth(self):

        return self.contentsRect().width() // Board.BoardWidth

    def squareHeight(self):
        return self.contentsRect().height() // Board.BoardHeight
    # shapeAt()决定了board里方块的的种类。
    def shapeAt(self, x, y):
        # 返回的是(x,y)坐标方块在self.board中的值
        return self.board[(y * Board.BoardWidth) + x]

    def setShapeAt(self, x, y, shape):
        # 设置方块的形状，放入self.board中
        self.board[(y * Board.BoardWidth) + x] = shape

    # 开始游戏
    def start(self):
        # 如果游戏处于暂停状态，直接返回
        if self.isPaused:
            return

        self.isStarted = True  # 将开始状态设置为True
        self.isWaitingAfterLine = False
        self.numLinesRemoved = 0  # 将分数设置为0
        self.clearBoard()  # 清空界面全部的方块
        # 状态栏显示当前有多少分
        self.msg2Statusbar.emit("score: "+ str(self.numLinesRemoved))

        self.newPiece()  # 创建一个新的方块
        self.timer.start(Board.Speed, self)  # 开始计时，每过300ms刷新一次当前的界面

    # pause()方法用来暂停游戏，停止计时并在statusbar上显示一条信息
    def pause(self):
        # 如果未处于运行状态，则直接返回
        if not self.isStarted:
            return
        # 更改游戏的状态
        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()  # 停止计时
            self.msg2Statusbar.emit(f"paused, current score is {self.numLinesRemoved}")  # 发送暂停信号,同时显示当前分数
        # 否则继续运行，显示分数
        else:
            self.timer.start(Board.Speed, self)
            self.msg2Statusbar.emit(str(self.numLinesRemoved))
        # 更新界面
        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)
        rect = self.contentsRect()  # 获取内容区域

        # print(rect)#(left,top,right,bottom)

        boardTop = rect.bottom() - Board.BoardHeight * self.squareHeight()  # 获取board中除去方块后多出来的空间
        # 渲染游戏分为两步。第一步是先画出所有已经落在最下面的的图，这些保存在self.board里。
        # 用shapeAt()查看这个这个变量。
        for i in range(Board.BoardHeight):
            for j in range(Board.BoardWidth):
                # 返回存储在self.board里面的形状
                shape = self.shapeAt(j, Board.BoardHeight - i - 1)
                # 如果形状不是空，绘制方块
                if shape != Tetrominoe.NoShape:
                    # 绘制方块，rect.left()表示Board的左边距
                    self.drawSquare(painter,
                                    rect.left() + j * self.squareWidth(),
                                    boardTop + i * self.squareHeight(), shape)
        # 第二步是画出正在下落的方块
        # 获取目前方块的形状，不能为空
        if self.curPiece.shape() != Tetrominoe.NoShape:

            for i in range(4):
                # 计算在Board上的坐标，作为方块坐标原点（单位是小方块）
                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)
                # 绘制方块
                self.drawSquare(painter, rect.left() + x * self.squareWidth(),
                                boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),
                                self.curPiece.shape())

    def keyPressEvent(self, event):

        key = event.key()

        # R代表重启游戏
        if key == Qt.Key_R:
            self.initBoard()
            self.start()

        # 如果游戏不是开始状态或者方块形状为空，直接返回
        if not self.isStarted or self.curPiece.shape() == Tetrominoe.NoShape:
            super(Board, self).keyPressEvent(event)
            return

        # P代表暂停
        if key == Qt.Key_P:
            self.pause()
            return
        # 如果游戏处于暂停状态，则不触发按键（只对按键P生效）
        if self.isPaused:
            return
        # 方向键左键代表左移一个位置，x坐标-1
        elif key == Qt.Key_Left:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)

        # 方向键右键代表右移一个位置，x坐标+1
        elif key == Qt.Key_Right:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)
        # 下方向键代表加速下落
        elif key == Qt.Key_Down:
            self.oneLineDown()
        # 上方向键是把方块顺时针旋转
        elif key == Qt.Key_Up:
            self.tryMove(self.curPiece.clockWise(), self.curX, self.curY)
        # 空格键会直接把方块放到底部
        elif key == Qt.Key_Space:
            self.dropDown()
        else:
            super(Board, self).keyPressEvent(event)

    # 在计时器事件里，要么是等一个方块下落完之后创建一个新的方块，要么是让一个方块直接落到底
    def timerEvent(self, event):
        '''handles timer event'''

        if event.timerId() == self.timer.timerId():
            # 如果在消除方块，说明方块已经下落到底部了，创建新的方块，否则下落一行
            if self.isWaitingAfterLine:
                self.isWaitingAfterLine = False
                self.newPiece()
            else:
                self.oneLineDown()

        else:
            super(Board, self).timerEvent(event)

    # clearBoard()方法通过Tetrominoe.NoShape清空broad
    def clearBoard(self):
        # 将界面每个小方块都设置为空，存储到self.board中
        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(Tetrominoe.NoShape)

    def dropDown(self):
        # 获取当前行
        newY = self.curY
        # 当方块还没落到最底部时，尝试向下移动一行，同时当前行-1
        while newY > 0:

            if not self.tryMove(self.curPiece, self.curX, newY - 1):
                break

            newY -= 1
        # 移到底部时，检查是否能够消除方块
        self.pieceDropped()

    def oneLineDown(self):
        # 调用self.tryMove()函数时，就已经表示方块下落一行了，每次下落到底部后，检查一下是否有能够消除的方块
        if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
            self.pieceDropped()

    def pieceDropped(self):
        # 将方块的形状添加到self.board中，非0代表该处有方块
        for i in range(4):
            # 获取每个小方块的坐标
            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.shape())
        # 移除满行的方块
        self.removeFullLines()
        # self.isWaitingAfterLine表示是否在等待消除行，如果不在等待就新建一个方块
        if not self.isWaitingAfterLine:
            self.newPiece()

    # 如果方块碰到了底部，就调用removeFullLines()方法，找到所有能消除的行消除它们。
    # 消除的具体动作就是把符合条件的行消除掉之后，再把它上面的行下降一行。
    # 注意移除满行的动作是倒着来的，按照重力来表现游戏的，如果不这样就有可能出现有些方块浮在空中的现象
    def removeFullLines(self):

        numFullLines = 0  # 记录消除的行数
        rowsToRemove = []  # 要消除的行列表

        for i in range(Board.BoardHeight):  # 遍历每一行

            n = 0
            for j in range(Board.BoardWidth):  # 遍历整行的方块
                # 如果self.board里面的值不为空，计数
                if not self.shapeAt(j, i) == Tetrominoe.NoShape:
                    n = n + 1
            # 如果整行都有方块，将要消除的行添加进数组中
            if n == Board.BoardWidth:
                rowsToRemove.append(i)
        # 因为是从上往下遍历，所以要倒过来消除，否则会出现方块悬空的情况
        rowsToRemove.reverse()

        for m in rowsToRemove:
            # self.shapeAt(l, k + 1)获取要消除的行的上一行的方块形状，然后替换当前方块的形状
            for k in range(m, Board.BoardHeight):
                for l in range(Board.BoardWidth):
                    self.setShapeAt(l, k, self.shapeAt(l, k + 1))

        # 更新已经消除的行数
        # numFullLines = numFullLines + len(rowsToRemove)
        # 还可以改成这样，如果连续消除，则分数翻倍。
        numFullLines = numFullLines + int(math.pow(2, len(rowsToRemove))) - 1

        if numFullLines > 0:
            # 更新分数
            self.numLinesRemoved = self.numLinesRemoved + numFullLines
            self.msg2Statusbar.emit(str(self.numLinesRemoved))  # 改变状态栏分数的值
            # 在消除后将当前方块形状设置为空，然后刷新界面
            self.isWaitingAfterLine = True
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.update()

    # newPiece()方法是用来创建形状随机的方块。如果随机的方块不能正确的出现在预设的位置，游戏结束。
    def newPiece(self):

        self.curPiece = Shape()
        self.curPiece.setRandomShape()  # 设置了一个随机的形状
        self.curX = Board.BoardWidth // 2  # 以界面中心为起点
        self.curY = Board.BoardHeight  - 1 +self.curPiece.minY()                        # 预留了一行的高度
        # 判断是否还有空位，如果没有 游戏结束
        if not self.tryMove(self.curPiece, self.curX, self.curY):
            # 将当前形状设置为空
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.timer.stop()  # 停止计时
            self.isStarted = False  # 将开始状态设置为False
            self.msg2Statusbar.emit(f"Game over, your score is {self.numLinesRemoved}")  # 状态栏显示游戏结束
            self.gameOver()

    #
    def gameOver(self):
        self.o = over()
        self.o.ui.show()
        self.btn_restart = self.o.ui.pushButton
        self.btn_restart.clicked.connect(self.restart)
        self.label = self.o.ui.label_3
        self.label.setText(f"Score: {self.numLinesRemoved}")

    def restart(self):
        self.o.ui.close()
        self.initBoard()
        self.start()




    # tryMove()是尝试移动方块的方法。
    # 如果方块已经到达board的边缘或者遇到了其他方块，就返回False。否则就把方块下落到想要的位置
    def tryMove(self, newPiece, newX, newY):

        for i in range(4):
            # newPiece是一个Shape对象，newX,newY相当于坐标原点（相对于方块而言）
            x = newX + newPiece.x(i)  # 得到每个小方块在界面上的坐标
            y = newY - newPiece.y(i)
            # 超出边界则返回False
            if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
                return False
            # 如果方块位置不为0，说明已经用过了，不允许使用，返回False
            if self.shapeAt(x, y) != Tetrominoe.NoShape:
                return False

        self.curPiece = newPiece  # 更新当前的方块形状
        self.curX = newX  # 更新当前的坐标
        self.curY = newY
        self.update()  # 更新窗口，同时调用paintEvent()函数

        return True

    def drawSquare(self, painter, x, y, shape):

        colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]
        # 为每种形状的方块设置不同的颜色
        color = QColor(colorTable[shape])
        # 参数分别为x,y,w,h,color，填充了颜色
        painter.fillRect(x + 1, y + 1, self.squareWidth() - 2,
                         self.squareHeight() - 2, color)

        painter.setPen(color.lighter())
        # 画线，从起始坐标到终点坐标，-1是为了留一点空格，看起来更有立体感
        painter.drawLine(x, y + self.squareHeight() - 1, x, y)  # 左边那条线
        painter.drawLine(x, y, x + self.squareWidth() - 1, y)  # 上边那条线
        # 让图案看起来更有立体感
        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.squareHeight() - 1,
                         x + self.squareWidth() - 1, y + self.squareHeight() - 1)  # 下边那条线
        painter.drawLine(x + self.squareWidth() - 1,
                         y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)  # 右边那条线

# Tetrominoe类保存了所有方块+NoShape的形状
class Tetrominoe(object):
    # 和Shape类里的coordsTable数组一一对应
    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7

# Shape类保存类方块内部的信息。
class Shape(object):
    # coordsTable元组保存了所有的方块形状的组成。是一个构成方块的坐标模版。
    coordsTable = (
        ((0, 0), (0, 0), (0, 0), (0, 0)),  # 空方块
        ((0, -1), (0, 0), (-1, 0), (-1, 1)),
        ((0, -1), (0, 0), (1, 0), (1, 1)),
        ((0, -1), (0, 0), (0, 1), (0, 2)),
        ((-1, 0), (0, 0), (1, 0), (0, 1)),
        ((0, 0), (1, 0), (0, 1), (1, 1)),
        ((-1, -1), (0, -1), (0, 0), (0, 1)),
        ((1, -1), (0, -1), (0, 0), (0, 1))
    )

    def __init__(self):
        # 下面创建了一个新的空坐标数组，这个数组将用来保存方块的坐标。
        self.coords = [[0, 0] for i in range(4)]  # 4x4的二维数组，每个元素代表方块的左上角坐标
        self.pieceShape = Tetrominoe.NoShape  # 方块形状，初始形状为空白

        self.setShape(Tetrominoe.NoShape)

    # 返回当前方块形状
    def shape(self):

        return self.pieceShape

    # 设置方块形状
    def setShape(self, shape):  # 初始shape为0

        table = Shape.coordsTable[shape]  # 从形状列表里取出其中一个方块的形状，为一个4x2的数组

        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]  # 赋给要使用的方块元素

        self.pieceShape = shape  # 再次获取形状

    # 设置一个随机的方块形状
    def setRandomShape(self):
        self.setShape(random.randint(1, 7))

    # 小方块的x坐标，index代表第几个方块
    def x(self, index):
        '''returns x coordinate'''

        return self.coords[index][0]

    # 小方块的y坐标
    def y(self, index):

        return self.coords[index][1]

    # 设置小方块的x坐标
    def setX(self, index, x):

        self.coords[index][0] = x

    # 设置小方块的y坐标
    def setY(self, index, y):

        self.coords[index][1] = y

    # 找出方块x min
    def minX(self):

        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])

        return m

    # 找出方块形x max
    def maxX(self):

        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])

        return m

    # 找出方块y min
    def minY(self):

        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])

        return m

    # 找出方块y max
    def maxY(self):

        m = self.coords[0][1]
        for i in range(4):
            m = max(m, self.coords[i][1])

        return m


    # 顺时针旋转，(x,y) -> (-y,x)
    def clockWise(self):

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))

        return result

if __name__ == '__main__':
    app = QApplication([])
    tetris = Tetris()
    menu = menu()
    menu.ui.show()
    menu.btn_start.clicked.connect(menu.ui.close)
    menu.btn_start.clicked.connect(tetris.initUI)
    sys.exit(app.exec_())






















