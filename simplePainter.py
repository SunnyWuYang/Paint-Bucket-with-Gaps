import cv2
import numpy as np
from floodfill import floodfill_with_gap


class Painter:
    """
    默认情况下，程序为绘画模式，即按下鼠标左键后并拖动可以进行绘制。
    -进入笔刷模式按'b'， 在该模式下按下鼠标左键进行拖动可产生线条
    -进入橡皮擦模式按'e'，在该模式下按下鼠标左键进行拖动可进行擦除
    -进入种子点选择模式按's‘，在该模式下点击鼠标左键即运行floodfill算法，并保存结果
    -点击'+'或'-'，增粗笔刷或减细笔刷
    -退出按'q'   

    """

    def __init__(self, img_size=(600, 800, 3), circle_radius=8, win_name='my Drawing Board', save_path=None, color=(1, 1, 255), gap=10):
        """
        :param img_size：画板大小，若指定background则忽略此参数
        :param circle_radius：‘circle'模式下圆形的半径
        :param win_name：窗口名
        :param save_path：绘图结果保存地址
        :param color：画笔颜色

        """
        self.win_name = win_name
        self.save_path = save_path
        self.brush_color = color
        self.circle_radius = circle_radius
        self.gap = gap
        self.erase_color = (255, 255, 255)
        self.img_size = img_size

        self.layer_back = np.zeros(
            img_size, dtype=np.uint8)

        self.layer_tmp = np.zeros(img_size, dtype=np.uint8)  # 临时显示画笔层

        self.layer_show = np.ones(img_size, dtype=np.uint8)*255

        self.brushed = False  # 当前是否为笔刷模式
        self.erased = False  # 当前是否为橡皮模式
        self.pressed = False  # 当前鼠标是否为按下模式
        self.seed = False  # 当前是否为种子点选择模式

        self.last_x = -1
        self.last_y = -1

    def mouseEvent(self, event, x, y, flag, param):
        if self.brushed == True:
            if event == cv2.EVENT_LBUTTONDOWN:
                self.pressed = True
                cv2.circle(self.layer_back, (x, y),
                           self.circle_radius, self.brush_color, -1)  # 实心圆

            if event == cv2.EVENT_MOUSEMOVE and self.pressed:
                cv2.circle(self.layer_back, (x, y),
                           self.circle_radius, self.brush_color, -1)  # 实心圆

            if event == cv2.EVENT_LBUTTONUP:
                self.pressed = False

            if event == cv2.EVENT_MOUSEMOVE and self.pressed == False:  # 临时显示画笔层
                cv2.circle(self.layer_tmp, (self.last_x, self.last_y),
                           self.circle_radius, self.erase_color, -1)
                # 每执行一步这个操作，imgsMerge、imshow就会立马执行，因此之前的消去不会起作用
                cv2.circle(self.layer_tmp, (x, y),
                           self.circle_radius, self.brush_color, -1)
                self.last_x = x
                self.last_y = y

        elif self.erased == True:

            if event == cv2.EVENT_LBUTTONDOWN:
                self.pressed = True
                cv2.circle(self.layer_back, (x, y),
                           self.circle_radius, self.erase_color, -1)

            elif event == cv2.EVENT_MOUSEMOVE and self.pressed == True:
                cv2.circle(self.layer_back, (x, y),
                           self.circle_radius, self.erase_color, -1)
            elif event == cv2.EVENT_LBUTTONUP:
                self.pressed = False

        elif self.seed == True:
            if event == cv2.EVENT_LBUTTONUP:
                result = floodfill_with_gap(self.layer_show, y, x, 10)
                cv2.imwrite(self.save_path, result)
                cv2.displayStatusBar(self.win_name, "Result has been saved!")

    @staticmethod
    def imgsMerge(img1, img2, color_list):
        mask = np.zeros(shape=img1.shape, dtype=bool)
        for color in color_list:
            curr_mask = (img2[:, :] == np.array(
                color)).all(axis=2)  # shape(w,h)
            curr_mask = curr_mask[..., np.newaxis]  # shape(w,h,1)
            curr_mask = np.repeat(curr_mask, repeats=3,
                                  axis=-1)  # shape(w,h,3)
            mask = mask | curr_mask
        np.copyto(dst=img1, src=img2, where=mask)

    def main(self):
        cv2.namedWindow(self.win_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.win_name, self.mouseEvent)  # 鼠标事件回调函数

        while True:
            cv2.imshow(self.win_name, self.layer_show)
            key = cv2.waitKey(1)
            # 这两个顺序一定不要弄反！！否则临时画笔层无法显示在擦除层上！
            self.imgsMerge(self.layer_show, self.layer_back,  # 永久绘画与擦除层
                           color_list=[self.brush_color, self.erase_color])
            self.imgsMerge(self.layer_show, self.layer_tmp,  # 临时显示画笔层
                           color_list=[self.brush_color, self.erase_color])

            # 一定要注意，layer_back不能清空，否则临时显示画笔便成了橡皮擦的效果
            self.layer_tmp = np.zeros(
                self.img_size, dtype=np.uint8)

            if key == ord('b'):  # brush
                self.brushed = not self.brushed
                self.erased = False
                self.seed = False

            elif key == ord('e'):  # erase
                # 需要去除临时显示画笔层 最后鼠标停留时留下的圆圈
                cv2.circle(self.layer_tmp, (self.last_x, self.last_y),
                           self.circle_radius, (255, 255, 255), -1)
                self.erased = not self.erased
                self.brushed = False
                self.seed = False

            elif key == ord('-'):  # decrease brush size
                self.circle_radius = self.circle_radius - 2
                if self.circle_radius < 2:
                    self.circle_radius = 2
                    print('minus', self.circle_radius)

            elif key == ord('+'):  # increase brush size
                self.circle_radius = self.circle_radius + 2
                print('increase', self.circle_radius)

            elif key == ord('s'):
                # 需要去除临时显示画笔层 最后鼠标停留时留下的圆圈
                cv2.circle(self.layer_tmp, (self.last_x, self.last_y),
                           self.circle_radius, (255, 255, 255), -1)
                self.seed = not self.seed
                self.brushed = False
                self.erased = False

            elif key == ord('q'):
                print("The windows are destroyed")
                break

        cv2.destroyAllWindows()


if __name__ == '__main__':
    painter = Painter(img_size=(150, 200, 3),
                      circle_radius=4,
                      save_path='result.png',
                      color=(0, 0, 255),
                      gap=10)

    painter.main()
