import logging
import random
import sqlite3
import os
import sys

# try:
# 	os.remove('rndcache.db')
# except:
# 	pass 

try:
	os.remove('rndcache.log')
except:
	pass

logging.basicConfig(
	filename = "rndcache.log",
	format = "%(levelname)-10s %(asctime)s %(message)s",
	level = logging.DEBUG)

log = logging.getLogger("cache")


class RndCache():


	def __init__(self, dbName='rndcache.db'):

		self._dbName = dbName

		self._connect = sqlite3.connect(self._dbName)

		self._connect.execute("PRAGMA foreign_keys = ON;")

		self._connect.execute("""create table if not exists catalog(
			id integer primary key, 
			name varchar unique, 
			path varchar unique)""")

		self._connect.execute("""create table if not exists file(
			id integer primary key, 	
			file varchar unique,
			catalogid integer foreing key,
			FOREIGN KEY(catalogid) REFERENCES catalog(id))""")

		log.debug("tables created or asserted: %s" % dbName)

	def GetAllCatalogs(self):

		catalogs = []

		res = self._connect.execute("""select name from catalog""")
		for r in res.fetchall():
			catalogs.append(r[0])

		log.debug("all catalogs: %s" % ' '.join(catalogs))

		return catalogs


	def AddCatalog(self, catalog, path):

		self._connect.execute("""insert into catalog(name, path) values (?, ?)""", 
			(catalog, path))

		self._connect.commit()

		log.debug("catalog added (%s) %s" % (catalog, path))

	def GetCatalogPath(self, catalog):

		res = self._connect.execute("""select path from catalog where name=?""", (catalog,))

		try:
			filePath = res.fetchall()[0][0]
		except IndexError:
			filePath = ''

		log.debug("catalog path %s = %s" % (catalog, filePath))

		return filePath

	def _GetCatalogId(self, catalog):

		res = self._connect.execute("""select id from catalog where name=?""", (catalog,))
		try:
			catalogId = res.fetchall()[0][0]
		except IndexError:
			catalogId = ''

		log.debug("catalog id = %s (%s)" % (catalog, catalogId))

		return catalogId

	def AddFile(self, catalog, filePath):
		
		catalogId = self._GetCatalogId(catalog)	

		self._connect.execute("""insert into file(file, catalogid) values (?, ?)""",
			(filePath, catalogId))		

		self._connect.commit()

		log.debug("file added (%s) %s" % (catalog, filePath))

		
	def GetRandomFile(self, catalog):

		catalogId = self._GetCatalogId(catalog)

		res = self._connect.execute("""select file from file where catalogid=?""", (catalogId,))

		entries = res.fetchall()
		random.shuffle(entries)
		
		try:
			filePath = entries[0][0]
		except IndexError:
			filePath = ''

		log.debug("random file (%s): %s" % (catalog, filePath))

		return filePath

	def Clear(self):

		self._connect.execute("""delete from file""")
		self._connect.execute("""delete from catalog""")
		self._connect.commit()

		log.info("tables dropped")


if __name__ == "__main__":

	if sys.argv[1] == 'test':

		c = RndCache(':memory:')
		
		c.AddCatalog("foo", "c:\\foo")
		c.AddCatalog("bar", "c:\\bar")
		
		isException = 0
		try:
			c.AddCatalog("foo", "c:\\bar2")
		except BaseException as e:
			isException = 1
			assert 'UNIQUE constraint failed: catalog.name' == e.message
		assert isException

		isException = 0
		try:
			c.AddCatalog("foo2", "c:\\bar")
		except BaseException as e:
			isException = 1
			assert 'UNIQUE constraint failed: catalog.path' == e.message
		assert isException

		assert c.GetCatalogPath("foo") == "c:\\foo"
		assert c.GetCatalogPath("bar") == "c:\\bar"

		filesFoo = ["c:\\foo\\1.txt", "c:\\foo\\2.txt", "c:\\foo\\3.txt"]
		filesBar = ["c:\\bar\\1.txt", "c:\\bar\\2.txt", "c:\\bar\\3.txt"]

		c.AddFile("foo", filesFoo[0])
		c.AddFile("bar", filesBar[0])

		assert c.GetRandomFile("foo") == filesFoo[0]
		assert c.GetRandomFile("bar") == filesBar[0]

		assert not c.GetRandomFile("foo2")
		assert not c.GetRandomFile("2bar")

		for f in filesFoo[1:]:
			c.AddFile("foo", f)

		for f in filesBar[1:]:
			c.AddFile("bar", f)

		log.debug("[~] range test started")

		for i in range(0, 100):

			log.debug("range entry:")

			f2 = c.GetRandomFile("foo")
			f3 = c.GetRandomFile("bar")

			assert f2 in filesFoo
			assert f3 in filesBar

		log.debug("[~] GetAllCatalogs test...")

		for f in c.GetAllCatalogs():
			assert f in ['foo', 'bar']

		c.Clear()

		assert not c.GetRandomFile("foo")
		assert not c.GetRandomFile("bar")
