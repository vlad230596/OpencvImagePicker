import math
from dataclasses import dataclass
from pathlib import Path

# import numpy as np
import cv2
import glob

import tkinter as tk
import tkinter.ttk as ttk

from tkinter import filedialog

# import EniPy.colors
# from EniPy import colors
# from EniPy import eniUtils

class PipelineBlock:
    def __init__(self, name, enabled=True):
        self.name = name
        self.enabled = enabled
    def build(self, input):
        print(f'build of {self.name}')
        result = input
        if self.enabled:
            result = self.process(input)
        return result
    def process(self, input):
        return input

class GrayBlock(PipelineBlock):
    def __init__(self):
        PipelineBlock.__init__(self, 'gray')

    def process(self, input):
        result = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)
        return result

class BlurBlock(PipelineBlock):
    def __init__(self):
        PipelineBlock.__init__(self, 'blur')

    def process(self, input):
        result = cv2.GaussianBlur(input, (5, 5), 0)
        return result

class ThresholdBlock(PipelineBlock):
    def __init__(self):
        PipelineBlock.__init__(self, 'threshold')

    def process(self, input):
        ret, threshold = cv2.threshold(input, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return threshold
class PipelineExecutor:
    def __init__(self):
        self.stages = []
    def add(self, stage):
        self.stages.append(stage)
    def execute(self, image):
        currentImage = image
        for stage in self.stages:
            currentImage = stage.build(currentImage)
        return currentImage

def process(path):
    imagesPath = glob.glob(f'{path}/*.jpg')
    for imagePath in imagesPath:
        print(f'\nProcessed: {imagePath}')
        original = cv2.imread(imagePath)
        
        executor = PipelineExecutor()
        executor.add(GrayBlock())
        executor.add(BlurBlock())
        executor.add(ThresholdBlock())

        final = executor.execute(original)

        contours, hierarchy = cv2.findContours(final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.imshow('original', original)
        cv2.imshow('final', final)
        cv2.waitKey()

if __name__ == '__main__':
    process('./images/')