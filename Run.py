# Copyright (c) 2018 Sean Kuo (JMingKuo)
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
from PIL import Image, ImageTk, ImageDraw
import cv2
import os

class GUI:
    def __init__(self, master, layout):
        
        self.layout = layout
        self.SpriteSheetPath = None
        self.RawSpriteSheetImg = None
        self.SpriteSheetImg = None
        self.SpriteSheetImgFG = None
        self.SpriteWidth = 32
        self.SpriteHeight = 32
        self.AnimationImg = None
        self.AnimationIdx_s = 0
        self.AnimationIdx_e = 0
        self.OutputDirPath = ''
        self.CanvasSize = None
        self.FrameIdx = 0
        self.FPS = 4
        self.SelectedIdx = None

        self.Frame_Left = tk.Frame(master, bg='gray25', width=(layout['GUI_w'] - layout['GUI_h']), height=layout['GUI_h'])
        self.Frame_Right = tk.Frame(master, bg='gray25', width=layout['GUI_w'], height=layout['GUI_h'])

        self.Frame_Left.pack(side=tk.LEFT, fill=tk.BOTH)
        self.Frame_Right.pack(side=tk.LEFT, fill=tk.BOTH)

        self.WidgetFrame = tk.Frame(self.Frame_Left, bg='gray35', width=(layout['GUI_w'] - layout['GUI_h']), height=(2 * layout['GUI_h'] - layout['GUI_w']))
        self.AnimationFrame = tk.Frame(self.Frame_Left, bg='gray45', width=(layout['GUI_w'] - layout['GUI_h']), height=(layout['GUI_w'] - layout['GUI_h']))
        self.SpriteSheetFrame = tk.Frame(self.Frame_Right, bg='gray55', width=layout['GUI_h'], height=layout['GUI_h'])

        self.WidgetFrame.pack_propagate(0)
        self.WidgetFrame.grid_propagate(0)
        self.AnimationFrame.pack_propagate(0)
        self.AnimationFrame.grid_propagate(0)
        self.SpriteSheetFrame.pack_propagate(0)
        self.SpriteSheetFrame.grid_propagate(0)

        self.WidgetFrame.pack()
        self.AnimationFrame.pack()
        self.SpriteSheetFrame.pack()

        self.WidgetFrameInit()
        self.AnimationFrameInit()
        self.SpriteSheetFrameInit()

        def KeyControl(event):
            if event.keycode == 27:
                master.destroy()
            if event.keycode == 112:
                self.LoadImage()
            if event.keycode == 113:
                self.SetOutputDir()
            if event.keycode == 114:
                self.ExportAnimation()
            if event.keycode == 116:
                self.Update()

        master.bind('<KeyPress>', KeyControl)

        def PlayAnimation():
            if self.RawSpriteSheetImg:
                self.FrameIdx = (self.FrameIdx + 1) % (self.AnimationIdx_e - self.AnimationIdx_s + 1)
                Crop_tl_x = (self.AnimationIdx_s + self.FrameIdx) % self.n_cols * self.SpriteWidth
                Crop_tl_y = (self.AnimationIdx_s + self.FrameIdx) // self.n_cols * self.SpriteHeight
                Crop_br_x = (((self.AnimationIdx_s + self.FrameIdx) % self.n_cols)+1) * self.SpriteWidth
                Crop_br_y = (((self.AnimationIdx_s + self.FrameIdx) // self.n_cols)+1) * self.SpriteHeight
                Crop_box = (Crop_tl_x, Crop_tl_y, Crop_br_x, Crop_br_y)
                self.AnimationImg = self.RawSpriteSheetImg.crop(Crop_box)
                self.AnimationCanvas = Image.new("RGB", self.AnimationImg.size, (255, 255, 255))
                self.AnimationCanvas.paste(self.AnimationImg, mask=self.AnimationImg.split()[3])
                ScaleRatio = (self.layout['GUI_w'] - self.layout['GUI_h']) / max(self.AnimationImg.size)
                self.AnimationCanvas = self.AnimationCanvas.resize((int(self.AnimationImg.size[0] * ScaleRatio), int(self.AnimationImg.size[1] * ScaleRatio)))
                self.AnimationPhotoImg = ImageTk.PhotoImage(self.AnimationCanvas)
                self.AnimationLabel.configure(image=self.AnimationPhotoImg)

            master.after(int(1000/self.FPS), PlayAnimation)
        master.after(int(1000/self.FPS), PlayAnimation)

    def WidgetFrameInit(self):
        self.LoadImageButton = tk.Button(self.WidgetFrame, text='Load Image (F1)', font=('Courier', 10, 'bold'), command=self.LoadImage)
        self.LoadImageButton.grid(row=0, column=0, sticky=tk.W+tk.E)
        self.SetOutputDirButton = tk.Button(self.WidgetFrame, text='Set Output Dir (F2)', font=('Courier', 10, 'bold'), command=self.SetOutputDir)
        self.SetOutputDirButton.grid(row=1, column=0, sticky=tk.W+tk.E)
        self.ExportSpriteButton = tk.Button(self.WidgetFrame, text='Export Sprites (F3)', font=('Courier', 10, 'bold'), command=self.ExportAnimation)
        self.ExportSpriteButton.grid(row=2, column=0, sticky=tk.W+tk.E)
        self.UpdateButton = tk.Button(self.WidgetFrame, text='Update (F5)', font=('Courier', 10, 'bold'), command=self.Update)
        self.UpdateButton.grid(row=3, column=0, sticky=tk.W+tk.E)
        self.SpriteWidthLabel = tk.Label(self.WidgetFrame, text='Sprite Width', font=('Courier', 10, 'bold'), bg='gray35', fg='gold')
        self.SpriteWidthLabel.grid(row=0, column=1, sticky=tk.W+tk.E)
        self.SpriteWidthEntry = tk.Entry(self.WidgetFrame, font=('Courier', 10, 'bold'), width=5)
        self.SpriteWidthEntry.grid(row=0, column=2, sticky=tk.W+tk.E)
        self.SpriteWidthEntry.insert(0, self.SpriteWidth)
        self.SpriteHeightLabel = tk.Label(self.WidgetFrame, text='Sprite Height', font=('Courier', 10, 'bold'), bg='gray35', fg='gold')
        self.SpriteHeightLabel.grid(row=1, column=1, sticky=tk.W+tk.E)
        self.SpriteHeightEntry = tk.Entry(self.WidgetFrame, font=('Courier', 10, 'bold'), width=5)
        self.SpriteHeightEntry.grid(row=1, column=2, sticky=tk.W+tk.E)
        self.SpriteHeightEntry.insert(0, self.SpriteHeight)
        self.StartFrameLabel = tk.Label(self.WidgetFrame, text='Start FrameIdx', font=('Courier', 10, 'bold'), bg='gray35', fg='green yellow')
        self.StartFrameLabel.grid(row=2, column=1, sticky=tk.W + tk.E)
        self.StartFrameEntry = tk.Entry(self.WidgetFrame, font=('Courier', 10, 'bold'), width=5)
        self.StartFrameEntry.insert(0, self.AnimationIdx_s)
        self.StartFrameEntry.grid(row=2, column=2, sticky=tk.W + tk.E)
        self.EndFrameLabel = tk.Label(self.WidgetFrame, text='End FrameIdx', font=('Courier', 10, 'bold'), bg='gray35', fg='green yellow')
        self.EndFrameLabel.grid(row=3, column=1, sticky=tk.W + tk.E)
        self.EndFrameEntry = tk.Entry(self.WidgetFrame, font=('Courier', 10, 'bold'), width=5)
        self.EndFrameEntry.insert(0, self.AnimationIdx_e)
        self.EndFrameEntry.grid(row=3, column=2, sticky=tk.W + tk.E)
        self.SpriteNameLabel = tk.Label(self.WidgetFrame, text='Sprite Name', font=('Courier', 10, 'bold'), bg='gray35', fg='cyan2')
        self.SpriteNameLabel.grid(row=0, column=3, sticky=tk.W + tk.E)
        self.SpriteNameEntry = tk.Entry(self.WidgetFrame, font=('Courier', 10, 'bold'), width=12)
        self.SpriteNameEntry.grid(row=0, column=4, sticky=tk.W + tk.E)
        self.AnimationNameLabel = tk.Label(self.WidgetFrame, text='Animation Name', font=('Courier', 10, 'bold'), bg='gray35', fg='cyan2')
        self.AnimationNameLabel.grid(row=1, column=3, sticky=tk.W + tk.E)
        self.AnimationNameEntry = tk.Entry(self.WidgetFrame, font=('Courier', 10, 'bold'), width=12)
        self.AnimationNameEntry.grid(row=1, column=4, sticky=tk.W + tk.E)
        self.FPSLabel = tk.Label(self.WidgetFrame, text='FPS', font=('Courier', 10, 'bold'), bg='gray35', fg='red1')
        self.FPSLabel.grid(row=2, column=3, sticky=tk.W + tk.E)
        self.FPSEntry = tk.Entry(self.WidgetFrame, font=('Courier', 10, 'bold'), width=5)
        self.FPSEntry.insert(0, self.FPS)
        self.FPSEntry.grid(row=2, column=4, sticky=tk.W + tk.E)   
        self.OutputDirLabel = tk.Label(self.WidgetFrame, text='OutputDir: ', font=('Courier', 10, 'bold'), bg='gray35', fg='yellow2')
        self.OutputDirLabel.grid(row=5, column=0, columnspan=5,sticky=tk.W + tk.E)
        self.InfoLabel = tk.Label(self.WidgetFrame, text='App Info', font=('Courier', 10, 'bold'), bg='gray35', fg='red2')
        self.InfoLabel.grid(row=6, column=0, columnspan=5,sticky=tk.W + tk.E)

    def AnimationFrameInit(self):
        self.AnimationLabel = tk.Label(self.AnimationFrame, bg='brown4')
        self.AnimationLabel.image = self.AnimationImg
        self.AnimationLabel.pack(fill="none", expand=True)

    def SpriteSheetFrameInit(self):
        self.SpriteSheetLabel = tk.Label(self.SpriteSheetFrame, bg='brown4')
        self.SpriteSheetLabel.image = self.SpriteSheetImg
        self.SpriteSheetLabel.pack(fill="none", expand=True)

    def ReShapeSpriteSheet(self, RawSpriteSheetImg):
        ForeGroundImg = Image.new("RGB", RawSpriteSheetImg.size, (128, 128, 255))
        ForeGroundImg.paste(RawSpriteSheetImg, mask=RawSpriteSheetImg.split()[3])

        SpriteSheetImg = Image.new("RGB", (self.CanvasSize * self.SpriteWidth, self.CanvasSize * self.SpriteHeight), (32, 32, 32))
        Draw = ImageDraw.Draw(SpriteSheetImg)

        idx = 0
        w = self.SpriteWidth
        h = self.SpriteHeight
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                CroppedImg = ForeGroundImg.crop((col * w, row * h, (col+1) * w, (row+1) * h))
                SpriteSheetImg.paste(CroppedImg, (idx%self.CanvasSize * w, idx//self.CanvasSize * h,
                                     ((idx%self.CanvasSize)+1) * w, ((idx//self.CanvasSize)+1) * h))
                if self.AnimationIdx_e >= idx >= self.AnimationIdx_s:
                    Draw.rectangle(((idx%self.CanvasSize * w + 1, idx//self.CanvasSize * h + 1),
                                    (((idx%self.CanvasSize)+1) * w - 1, ((idx//self.CanvasSize)+1) * h - 1)),
                                    outline="yellow")
                idx += 1

        return SpriteSheetImg

    def LoadImage(self):
        self.SpriteSheetPath = askopenfilename(initialdir=os.getcwd(), filetype=[('SpriteSheet file', '*.png')])
        
        if os.path.exists(self.SpriteSheetPath):
            self.RawSpriteSheetImg = Image.open(self.SpriteSheetPath)
            self.n_rows = self.RawSpriteSheetImg .size[1]//self.SpriteHeight
            self.n_cols = self.RawSpriteSheetImg .size[0]//self.SpriteWidth
            n_frames = self.n_rows * self.n_cols
            self.CanvasSize = int(n_frames**0.5 + 1)
            self.Update()
        else:
            self.InfoLabel.configure(text='Path for SpriteSheetPath not found')

    def SetOutputDir(self):
        self.OutputDirPath = askdirectory()
        if os.path.exists(self.OutputDirPath) and os.path.isdir(self.OutputDirPath):
            self.OutputDirLabel.configure(text='OutputDir: {}'.format(self.OutputDirPath))
            self.InfoLabel.configure(text='Set output directory success')           
        else:
            self.OutputDirPath = ''
            self.InfoLabel.configure(text='Please choose a valid directory')

    def ExportAnimation(self):
        self.Update()
        if os.path.exists(self.OutputDirPath) and os.path.isdir(self.OutputDirPath):
            SpriteName = self.SpriteNameEntry.get()
            AnimationName = self.AnimationNameEntry.get()
            if len(SpriteName) > 0 and len(AnimationName) > 0:
                SpriteDirPath = os.path.join(self.OutputDirPath, SpriteName)
                if not os.path.exists(SpriteDirPath):
                    os.mkdir(SpriteDirPath)
                AnimationDirPath = os.path.join(SpriteDirPath, AnimationName)
                if not os.path.exists(AnimationDirPath):
                    os.mkdir(AnimationDirPath)
                for FrameIdx in range(self.AnimationIdx_e - self.AnimationIdx_s + 1):
                    FrameIdx = (FrameIdx + 1) % (self.AnimationIdx_e - self.AnimationIdx_s + 1)
                    Crop_tl_x = (self.AnimationIdx_s + FrameIdx) % self.n_cols * self.SpriteWidth
                    Crop_tl_y = (self.AnimationIdx_s + FrameIdx) // self.n_cols * self.SpriteHeight
                    Crop_br_x = (((self.AnimationIdx_s + FrameIdx) % self.n_cols)+1) * self.SpriteWidth
                    Crop_br_y = (((self.AnimationIdx_s + FrameIdx) // self.n_cols)+1) * self.SpriteHeight
                    Crop_box = (Crop_tl_x, Crop_tl_y, Crop_br_x, Crop_br_y)
                    AnimationFrameImg = self.RawSpriteSheetImg.crop(Crop_box)
                    SavePath = os.path.join(AnimationDirPath, '{}_{}.png'.format(AnimationName, FrameIdx))
                    AnimationFrameImg.save(SavePath)
                self.AnimationNameEntry.delete(0, 'end')
                self.InfoLabel.configure(text='Export to {}'.format(os.path.join(AnimationDirPath)))
            else:
                self.InfoLabel.configure(text='Set SpriteName and AnimationName before export')
        else:
            self.InfoLabel.configure(text='Set output directory before export')
            
    def DrawSpriteSheet(self):
        if self.RawSpriteSheetImg:
            SpriteSheetImg = self.ReShapeSpriteSheet(self.RawSpriteSheetImg)
            SpriteSheetImg = SpriteSheetImg.resize((self.layout['GUI_h'], self.layout['GUI_h']))
            self.SpriteSheetImg = SpriteSheetImg
            self.SpriteSheetImgFG = ImageTk.PhotoImage(SpriteSheetImg, (self.layout['GUI_h'], self.layout['GUI_h']))
            self.SpriteSheetLabel.configure(image=self.SpriteSheetImgFG)
            
            self.SpriteSheetLabel.bind("<Button-1>", self.MouseLeftcallback)

    def MouseLeftcallback(self, event):
        Selected_Row = (event.y // (self.layout['GUI_h'] / self.CanvasSize))
        Selected_Col = (event.x // (self.layout['GUI_h'] / self.CanvasSize))
        if self.SelectedIdx:
            FirstIdx = self.SelectedIdx
            SecondIdx = int(Selected_Row * self.CanvasSize + Selected_Col)
            [StartIdx, EndIdx] = sorted([FirstIdx, SecondIdx])
            self.StartFrameEntry.delete(0, 'end')
            self.StartFrameEntry.insert(0, StartIdx)
            self.EndFrameEntry.delete(0, 'end')
            self.EndFrameEntry.insert(0, EndIdx)
            self.Update()
        else:
            self.SelectedIdx = int(Selected_Row * self.CanvasSize + Selected_Col)

    def Update(self):
        if self.RawSpriteSheetImg:
            self.SpriteWidth = max(0, int(self.SpriteWidthEntry.get()))
            self.SpriteHeight = max(0, int(self.SpriteHeightEntry.get()))
            EndFrameNum = min(self.CanvasSize**2 - 1, int(self.EndFrameEntry.get()))
            self.EndFrameEntry.delete(0, 'end')
            self.EndFrameEntry.insert(0, EndFrameNum)
            StartFrameNum = min(max(0, int(self.StartFrameEntry.get())), EndFrameNum)
            self.StartFrameEntry.delete(0, 'end')
            self.StartFrameEntry.insert(0, StartFrameNum)
            self.AnimationIdx_s = max(0, int(StartFrameNum))
            self.AnimationIdx_e = max(0, int(EndFrameNum))
            self.AnimationIdx_e = max(self.AnimationIdx_s, self.AnimationIdx_e)
            self.FPS = max(1, int(self.FPSEntry.get()))
            self.DrawSpriteSheet()
            self.SelectedIdx = None
            self.InfoLabel.configure(text='Update Done')
            

def main():
    layout = {'GUI_w': 1280, 'GUI_h': 720}

    root = tk.Tk()
    root.geometry('{}x{}'.format(layout['GUI_w'], layout['GUI_h']))
    root.title('SpriteSheetSlicer')

    GUI(root, layout)

    root.mainloop()


if __name__ == '__main__':
    main()