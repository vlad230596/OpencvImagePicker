import math
from dataclasses import dataclass
from pathlib import Path

import cv2
import glob

import numpy as np

# import EniPy.colors
# from EniPy import colors
# from EniPy import eniUtils

import dearpygui.dearpygui as dpg

dpg.create_context()

# callback runs when user attempts to connect attributes
def link_callback(sender, app_data):
    # app_data -> (link_id1, link_id2)
    print(f'link')
    dpg.add_node_link(app_data[0], app_data[1], parent=sender)

# callback runs when user attempts to disconnect attributes
def delink_callback(sender, app_data):
    # app_data -> link_id
    print(f'delink')
    dpg.delete_item(app_data)

def add_action():
    print(f'add_action')
    pass
with dpg.font_registry():
    default_font = dpg.add_font("fonts/OpenSans-Regular.ttf", 24)

def right_click_cb(sender, app_data):
    dpg.configure_item("right_click_menu", show=True)

with dpg.handler_registry():
    dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Right, callback=right_click_cb)
    
with dpg.window(label="Right click window", modal=True, show=False, id="right_click_menu", no_title_bar=True):
    dpg.add_text("All those beautiful files will be deleted.\nThis operation cannot be undone!")
    dpg.add_separator()
    dpg.add_checkbox(label="Don't ask me next time")
    with dpg.group(horizontal=True):
        dpg.add_button(label="OK", width=75, callback=lambda: dpg.configure_item("right_click_menu", show=False))
        dpg.add_button(label="Cancel", width=75,
                       callback=lambda: dpg.configure_item("right_click_menu", show=False))

with dpg.window(label="Tutorial", width=400, height=400):
    dpg.bind_font(default_font)
    print(f'w')
    with dpg.node_editor(callback=link_callback, delink_callback=delink_callback):
        with dpg.node(label="Node 1"):
            print(f'n1')
            with dpg.node_attribute(label="Node A1"):
                dpg.add_input_float(label="F1", width=150)

            with dpg.node_attribute(label="Node A2", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_input_float(label="F2", width=150)

        with dpg.node(label="Node 2"):
            print(f'n1')
            with dpg.node_attribute(label="Node A3"):
                dpg.add_input_float(label="F3", width=200)

            with dpg.node_attribute(label="Node A4", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_input_float(label="F4", width=200)

with dpg.window(label="Example Window"):
    dpg.add_text("Hello, world")
    with dpg.popup(dpg.last_item()):
        dpg.add_text("A popup")

    dpg.add_button(label="Add", callback=add_action)
    dpg.add_input_text(label="string", default_value="Quick brown fox")
    dpg.add_slider_float(label="float", default_value=0.273, max_value=1)


dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

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

class ScaleBlock(PipelineBlock):
    def __init__(self):
        PipelineBlock.__init__(self, 'scale')

    scale : float = 1.0
    def process(self, input):
        width = int(input.shape[1] * self.scale)
        height = int(input.shape[0] * self.scale)
        dim = (width, height)
        result = cv2.resize(input, dim, interpolation=cv2.INTER_AREA)
        return result

class BlurBlock(PipelineBlock):
    def __init__(self):
        PipelineBlock.__init__(self, 'blur')

    def process(self, input):
        # blur
        # medianblur
        result = cv2.GaussianBlur(input, (5, 5), 0)
        return result

class ThresholdBlock(PipelineBlock):
    def __init__(self):
        PipelineBlock.__init__(self, 'threshold')

    def process(self, input):
        ret, threshold = cv2.threshold(input, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return threshold
class MorphologyExBlock(PipelineBlock):
    def __init__(self):
        PipelineBlock.__init__(self, 'MorphologyEx')
    def process(self, input):
        kernel = np.ones((13, 13), np.uint8)
        result = cv2.morphologyEx(input, cv2.MORPH_CLOSE, kernel)
        return result

# class BorderBlock()cv2.copyMakeBorder
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
        executor.add(ScaleBlock())
        executor.add(GrayBlock())
        executor.add(MorphologyExBlock())
        executor.add(BlurBlock())
        executor.add(ThresholdBlock())

        final = executor.execute(original)

        contours, hierarchy = cv2.findContours(final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.imshow('original', original)
        cv2.imshow('final', final)
        cv2.waitKey()

if __name__ == '__main__':
    process('./images/')