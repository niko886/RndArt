
import os, random

from kivy.logger import Logger

from RndCache import RndCache

class ImageLibrary():

	def __init__(self, root):

		self._root = root
		self._bannedCategories = []
		self._cache = RndCache(dbName=":memory:")
		#self._cache.Clear()

		#`````````````````#
		# make categories #
		#_________________#

		for root, dirs, files in os.walk(self._root):
			for d in dirs:

				#```````````````````````#
				# filter empty catalogs #
				#_______________________#

				newRoot = os.path.join(root, d)

				for root2, dirs2, files2 in os.walk(newRoot):
					if not files2 and not dirs2:
						Logger.error("catalog %s is empty" % d)
					else:
						Logger.debug("adding catalog, %s to cache.." % d)

						if not self._cache.GetCatalogPath(d):

							self._cache.AddCatalog(d, newRoot)
					break
			break
		
		Logger.info('[*] categories found: %s' % (self.GetCategories()))

	def BanCategory(self, categoryName):

		if not categoryName in self._bannedCategories:

			Logger.debug("ban category - %s" % categoryName)

			self._bannedCategories.append(categoryName)

	def UnbanCategory(self, categoryName):

		if categoryName in self._bannedCategories:

			Logger.debug("unban category: %s" % categoryName)

			self._bannedCategories.remove(categoryName)


	def GetCategories(self):
		return self._cache.GetAllCatalogs()

	def GetNotBannedCategories(self):

		result = []
		possible = self.GetCategories()
		for p in possible:
			
			if p not in self._bannedCategories:
			
				result.append(p)
		return result

	def GetCategoryPath(self, category):
		return self._cache.GetCatalogPath(category)
		
	def GetRandomImageFromCategory(self, category):

		# #```````````````#
		# # get all files #
		# #_______________#

		# allImages = []
		# Logger.debug('--- dump begin --- %s' % category)
		# for root, dirs, files in os.walk(self.GetCategoryPath(category)):
		# 	for f in files:
		# 		allImages.append(os.path.join(root, f))

		# Logger.debug('[*] allimages %s' % allImages)
		# Logger.debug('--- dump end ---')

		# if not allImages:
		# 	Logger.warning("%s catalog is empty!" % category)
		# 	return None

		# return random.choice(allImages)

		res = self._cache.GetRandomFile(category)

		if not res:

			Logger.info("it seems there is no any files in cache, for category %s, fill the cache..." % category)

			for root, dirs, files in os.walk(self.GetCategoryPath(category)):

				for f in files:

					filePath = os.path.join(root, f)

					self._cache.AddFile(category, filePath)


			res = self._cache.GetRandomFile(category)


		return self._cache.GetRandomFile(category)

	def GetImageDict(self):

		notBannedCategories = self.GetNotBannedCategories()
		imageDict = {}
		for category in notBannedCategories:
			imageDict[category] = {'path': self.GetCategoryPath(category), 
				'image': self.GetRandomImageFromCategory(category)}

		return imageDict

	def GetRandomImages(self):

		images = []
		for cat in self.GetCategories():
			if cat not in self._bannedCategories:
				img = self.GetRandomImageFromCategory(cat)
				if img:
					images.append(img)

		Logger.debug('random imgs: %s' % images)
		return images