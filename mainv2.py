'''
Program: Basic Paint
Author: Sean Mauk
Version: 0.2
Last Updated: 2/4/2019

Notes:
	Currently the functions must find perfect matches so if there
	are any misspellings the checks won't catch them.
	
	To Do:
		Add documentation
		Change popup coding
		Add more features
		Make it pretty
'''

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder

from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from kivy.graphics import Color, Ellipse, Line, Rectangle

def btn(rgba, function):
		base = Button(background_normal = '', background_color = rgba, size_hint = (None,None), size = (100,100))
		base.bind(on_release=function)
		return base

def colorgrid(function):
	color_grid = GridLayout(rows=3, spacing = [10], padding = [10,10,10,10])
	color_grid.add_widget(btn(rgba = [1,0,0,1], function = function))
	color_grid.add_widget(btn(rgba = [0,1,0,1], function = function))
	color_grid.add_widget(btn(rgba = [0,0,1,1], function = function))
	color_grid.add_widget(btn(rgba = [1,1,0,1], function = function))
	color_grid.add_widget(btn(rgba = [1,0,1,1], function = function))
	color_grid.add_widget(btn(rgba = [0,1,1,1], function = function))
	color_grid.add_widget(btn(rgba = [1,1,1,1], function = function))
	color_grid.add_widget(btn(rgba = [0,0,0,1], function = function))
	return color_grid

class ColorWidget(Widget):
	def __init__(self, rgba, **kwargs):
		super(ColorWidget, self).__init__()
		self.colors = rgba
		with self.canvas:
			Color(self.colors)
			Rectangle(pos = self.pos, size = self.size)
			
class PaintWidget(Widget):
	Window.clearcolor = (1, 1, 0.95, 1)
	
	def __init__(self, **kwargs):
		super(PaintWidget,self).__init__()
		self.rad = 10. #Line Width / Radius
		self.colors = [0,0,0,1]
		self.drawable = False
	
	def on_touch_down(self, touch):
		color = self.colors
		with self.canvas:
			if self.collide_point(*touch.pos):
				self.drawable = True
				Color(*color)
				Ellipse(pos=(touch.x - self.rad, touch.y - self.rad),size=(self.rad*2,self.rad*2))
				touch.ud['line'] = Line(points=(touch.x, touch.y), width = self.rad)
	
	def on_touch_move(self, touch):
		if self.collide_point(*touch.pos) and self.drawable:
			touch.ud['line'].points += [touch.x, touch.y]
		
	def on_touch_up(self, touch):
		if self.collide_point(*touch.pos) and self.drawable:
			with self.canvas:
				Ellipse(pos=(touch.x - self.rad, touch.y - self.rad),size=(self.rad*2,self.rad*2))
			self.drawable = False
	
class AllPopups(Popup):
	
	@classmethod
	def save_popup(cls, function):
		popup = cls(title='Save File', title_align = 'center', size_hint = (None, None), size = (200, 200))
		popup.tin = TextInput(size_hint=(1, 0.3), pos_hint={'x':0, 'y':0.5}, focus=True)
		
		can_btn = Button(text='Cancel', size_hint=(0.49, 0.3), pos_hint={'x':0, 'y':0.05})
		can_btn.bind(on_release=popup.dismiss)
		
		save_btn = Button(text='Save', size_hint=(0.49, 0.3), pos_hint={'x':0.51, 'y':0.05})
		save_btn.bind(on_release=function)
		
		popup.content = RelativeLayout()
		popup.content.add_widget(popup.tin)		
		popup.content.add_widget(can_btn)
		popup.content.add_widget(save_btn)
		
		return popup
		
	@classmethod
	def stroke_popup(cls, painter, function):
		popup = cls(title='Set Stroke Size',title_align='center', size_hint = (None, None), size = (400, 200))
		
		slider = Slider(value = painter.rad, value_track=True, value_track_color=[1,0,1,1], size_hint = (1.1, 1))	
		slider.range = (5, 50)
		slider.bind(on_touch_up=function)
		
		popup.add_widget(slider)
		
		return popup
	
	@classmethod
	def color_popup(cls, function):
		popup = cls(title='Choose a color', title_align='center', size_hint = (None, None), size = (400, 450))
		color_grid = colorgrid(function)
		popup.content = color_grid	
		return popup

class PaintApp(App):
	def build(self):
		application = BoxLayout()
				
		application.orientation='vertical'
		self.menu.orientation='horizontal'
		application.add_widget(self.painter)
		application.add_widget(self.menu)
		self.menu.size_hint = (1, 0.07)
		
		return application
		
	def menu(self):
		self.menu = BoxLayout()
		self.painter = PaintWidget()
		
		stroke_popup = AllPopups.stroke_popup(self.painter,self.resize_brush)
		save_popup = AllPopups.save_popup(self.save_func)
		color_popup = AllPopups.color_popup(self.change_color)
		
		clear_btn = Button(text = 'Clear')
		clear_btn.bind(on_release=self.clear_canvas)		
		
		exit_btn = Button(text = 'Exit')
		exit_btn.bind(on_release=self.stop)
		
		stroke_btn = Button(text = 'Stroke')
		stroke_btn.bind(on_release = stroke_popup.open)
		
		save_btn = Button(text = 'Save')
		save_btn.bind(on_release=save_popup.open)
		
		color_btn = Button(text = 'Color')
		color_btn.bind(on_release = color_popup.open)
		
		self.menu.add_widget(exit_btn)
		self.menu.add_widget(save_btn)
		self.menu.add_widget(clear_btn)
		self.menu.add_widget(color_btn)
		self.menu.add_widget(stroke_btn)
			
	def save_func(self, obj):
		if obj.parent.parent.tin.text:
			f_name = obj.parent.parent.tin.text + '.png'
		else:
			f_name = 'untitled.png'
			
		self.painter.export_to_png(f_name)
		print('File saved')
		obj.parent.parent.dismiss()
		
	def resize_brush(self, obj, touch):
		self.painter.rad = obj.value
		obj.parent.parent.parent.dismiss()
		
	def change_color(self, obj):
		self.painter.colors = obj.background_color
		obj.parent.parent.parent.parent.dismiss()
		
				
	def clear_canvas(self, obj):
		self.painter.canvas.clear()

if __name__ == "__main__":
	interactive = True
	application = PaintApp()
	if interactive:
		application.menu()
		application.run()
	else: 
		print("Inactive")
		
		
		