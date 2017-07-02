from kivy.app import App

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scatter import Scatter

from kivy.logger import Logger

from kivy.lang import Builder

import logging

import random, os

from ImageLib import ImageLibrary

Builder.load_string('''
<CategoryWidget>:
	orientation: 'horizontal'

    CheckBox:
    	id: chb
    	active: True
    Label:
    	id: label
    	text: '<Make name>'
        

<CategoryPanel>
	orientation: 'vertical'

''')


class CategoryWidget(BoxLayout):
	pass

class CategoryPanel(BoxLayout):
	pass

class ImageBox(GridLayout):


	def __init__(self,  imageLibrary=None, **kwargs):

		super(ImageBox, self).__init__(**kwargs)
		#self.RandomImages(app=kwargs['app'])

		self.rows = 2
		self.add_widget(Label(text="There is no images yet, please set \"settings\" -> \"Image root\""))

	def AddImageAndCategories(self, imageDict, clb=None):

		self.clear_widgets()
		
		l = len(imageDict.keys())
		if l % 2:
			self.rows = l / 2 + 1
		else:
			self.rows = l / 2

		categories = imageDict.keys()

		if len(categories) > 1:
			random.shuffle(categories)

		for category in categories:

			img = Image(source=imageDict[category]['image'])
			img.name = category

			if clb:
				img.bind(on_touch_down=clb)

			img = self.add_widget(img)



class MyLayout(FloatLayout):

	def __init__(self, **kwargs):

		super(MyLayout, self).__init__(**kwargs)
		
		imagebox = ImageBox(size_hint=(.8, 1), pos_hint={'x':.2}, id='ImageBox')

		self.add_widget(imagebox)

		button = Button(text='randomize', size_hint=(.18, .18), pos_hint={'y':.81, 'x':.01}, background_color=(0,2,0,1), id='RandomBtn')
		self.add_widget(button)

		button = Button(text='options', size_hint=(.18, .18), pos_hint={'y':.01, 'x':.01}, id='SettingsBtn')
		self.add_widget(button)


		categoryPanel = CategoryPanel(size_hint=(.15, .6), pos_hint={'y':.2}, id='CategoryPanel')
		

		self.add_widget(categoryPanel)


	def AddCategoryCheckbox(self, categories, clb=None):

		categoryPanel = self.GetWidgetById('CategoryPanel')
		categoryPanel.clear_widgets()

		idx = 1
		for cat in categories:

			box = CategoryWidget()
			box.ids['label'].text = cat
			#box.checkbox.active = False

			if clb:
				box.ids['chb'].bind(active=clb)
				box.ids['chb'].name = cat
			
			categoryPanel.add_widget(box)


	def GetWidgetById(self, widgetId):

		for widg in self.walk():
			
			if widg.id == widgetId:
				Logger.debug('found widget {0}, id = {1}'.format(widg, widgetId))
				return widg

class RndArtApp(App):


	def on_randomize_button(self, instance):

		Logger.debug('The button <%s> is being pressed' % instance.text)

		imageDict = self._imglib.GetImageDict()
		imgbox = self._layout.GetWidgetById('ImageBox')
		imgbox.AddImageAndCategories(imageDict, clb=self.on_my_touch_down)

	def on_options_button(self, instance):

		Logger.debug('The button <%s> is being pressed' % instance.text)

		self.open_settings()

	def on_my_touch_down(self, instance, touch):

		isX = 0
		isY = 0

		if touch.x > instance.x and touch.x < instance.x + instance.width:
			isX = 1
		if touch.y > instance.y and touch.y < instance.y + instance.height:
			isY = 1

		

		if isX and isY:
			Logger.info('on_my_touch_down: %s' % instance.name)
			instance.source = self._imglib.GetRandomImageFromCategory(instance.name)


	def on_checkbox_active(self, checkbox, value):
		if value:
			Logger.debug('The checkbox {0} is active'.format(checkbox.name))
			
			self._imglib.UnbanCategory(checkbox.name)
		else:
			Logger.debug('The checkbox {0} is inactive'.format(checkbox.name))
			self._imglib.BanCategory(checkbox.name)

		imageDict = self._imglib.GetImageDict()
		imgbox = self._layout.GetWidgetById('ImageBox')
		imgbox.AddImageAndCategories(imageDict, clb=self.on_my_touch_down)

	def __init__(self, **arg):
		super(RndArtApp, self).__init__(**arg)

		# ... or
		# App.__init__(self, **arg)
		

	def build_config(self, config):

		config.setdefaults('ImageLib', 
			{'root': 'images/lib'})


	def build_settings(self, settings):

		json = '''
			[

			    {
			        "type": "string",
			        "title": "Image root",
			        "desc": "Choose the root image directory",
			        "section": "ImageLib",
			        "key": "root"
			    }

			]'''

		settings.add_json_panel('Options', self.config, data=json)

	def on_config_change(self, config, section, key, value):

		# Logger.info("main.py: App.on_config_change: {0}, {1}, {2}, {3}".format(
		# 	config, section, key, value))

		if section in 'ImageLib':

			if key in 'root':

				imglib = ImageLibrary(value)

				imageDict = imglib.GetImageDict()

				self._layout.GetWidgetById('ImageBox').AddImageAndCategories(imageDict, clb=self.on_my_touch_down)	

				self._layout.AddCategoryCheckbox(imglib.GetCategories(), self.on_checkbox_active)

				self._imglib = imglib

	def GetBannedCategoriesFromConfig(self):

		logging.debug("GetBannedCategoriesFromConfig()")

		result = []

		res = self.config.get('ImageLib', 'unchecked_categoreis')

		if res:

			[configRoot, unchecked] = res.split("*")	

			if configRoot == self._imglib._root:
				unchecked = unchecked.split(',')

				logging.debug("found unchecked categories %s" % ' '.join(unchecked))
				return unchecked

		return result

	def UncheckCheckBoxes(self):

		categories = self.GetBannedCategoriesFromConfig()

		if categories:

			for widget in self._layout.GetWidgetById('CategoryPanel').children:

				if widget.ids['chb'].name in categories:

					logging.info("unchecking category")

					widget.ids['chb'].active = False


	def build(self):

		#````````````#
		# Initialize #
		#____________#

		root = self.config.get('ImageLib', 'root')
		imglib = ImageLibrary(root)

		self._imglib = imglib

		layout = MyLayout()

		self._layout = layout

		#````````````````#
		# fill with data #
		#________________#

		for category in self.GetBannedCategoriesFromConfig():
			self._imglib.BanCategory(category)

		imageDict = imglib.GetImageDict()

		layout.GetWidgetById('ImageBox').AddImageAndCategories(imageDict, clb=self.on_my_touch_down)		

		layout.AddCategoryCheckbox(self._imglib.GetCategories(), self.on_checkbox_active)
		self.UncheckCheckBoxes()

		layout.GetWidgetById('RandomBtn').bind(on_press=self.on_randomize_button)
		layout.GetWidgetById('SettingsBtn').bind(on_press=self.on_options_button)


		return layout

	def on_stop(self):

		logging.debug("saving checked directory state...")

		unchecked = []

		res = ''

		for widget in self._layout.GetWidgetById('CategoryPanel').children:
			if not widget.ids['chb'].active:
				logging.debug("found unchecked category: %s" % widget.ids['chb'].name)
				unchecked.append(widget.ids['chb'].name)

		if unchecked:			 	

			res = self._imglib._root + '*' + ','.join(unchecked)

		else:
			logging.debug("there is no unchecked boxes")		

		self.config.set("ImageLib", "unchecked_categoreis", res)
		self.config.write()


if __name__ == "__main__":

	Logger.setLevel(logging.DEBUG)


	RndArtApp().run()
	