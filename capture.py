#对后台窗口截图
import win32gui, win32ui, win32con
import cv2
import numpy



def capture(hWnd):
    try:
        #获取句柄窗口的大小信息
        left, top, right, bot = win32gui.GetWindowRect(hWnd)
        width = right - left
        height = bot - top
        #返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
        hWndDC = win32gui.GetWindowDC(hWnd)
        #创建设备描述表
        mfcDC = win32ui.CreateDCFromHandle(hWndDC)
        #创建内存设备描述表
        saveDC = mfcDC.CreateCompatibleDC()
        #创建位图对象准备保存图片
        saveBitMap = win32ui.CreateBitmap()
        #为bitmap开辟存储空间
        saveBitMap.CreateCompatibleBitmap(mfcDC,width,height)
        #将截图保存到saveBitMap中
        saveDC.SelectObject(saveBitMap)
        #保存bitmap到内存设备描述表
        saveDC.BitBlt((0,0), (width,height), mfcDC, (0, 0), win32con.SRCCOPY)

        ##方法三（第一部分）：opencv+numpy保存
        ###获取位图信息
        signedIntsArray = saveBitMap.GetBitmapBits(True)
        ##方法三（后续转第二部分）

        #内存释放
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hWnd,hWndDC)

        ##方法三（第二部分）：opencv+numpy保存
        ###PrintWindow成功，保存到文件，显示到屏幕
        im_opencv = numpy.frombuffer(signedIntsArray, dtype = 'uint8')
        im_opencv.shape = (height, width, 4)
        image_array = cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2RGB)
        image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)

    except:

        image_array = numpy.zeros((720, 1280, 3), numpy.uint8)

    return image_array


if __name__ == "__main__":
    while True:
        img = capture(787448)
        img_cvt = img[170:580,130:600]
        cv2.imshow('test',img)
        if cv2.waitKey(1) & 0xFF == 27:
            cv2.destroyAllWindows()
            break
