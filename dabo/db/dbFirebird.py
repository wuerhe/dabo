# -*- coding: utf-8 -*-
import datetime
import re
import dabo
from dabo.dLocalize import _
from dBackend import dBackend
from dCursorMixin import dCursorMixin


class Firebird(dBackend):
	"""Class providing Firebird connectivity. Uses kinterbasdb."""

	# Firebird treats quotes names differently than unquoted names. This
	# will turn off the effect of automatically quoting all entities in Firebird; 
	# if you need quotes for spaces and bad names, you'll have to supply 
	# them yourself.
	nameEnclosureChar = ""

	def __init__(self):
		dBackend.__init__(self)
		self.dbModuleName = "kinterbasdb"
		self.fieldPat = re.compile("([A-Za-z_][A-Za-z0-9-_]+)\.([A-Za-z_][A-Za-z0-9-_]+)")
		import kinterbasdb
		initialized = getattr(kinterbasdb, "initialized", None)
		if not initialized:
			if initialized is None:
				# type_conv=200 KeyError with the older versions. User will need 
				# mxDateTime installed as well:
				kinterbasdb.init()
			else:
				# Use Python's Decimal and datetime types:
				kinterbasdb.init(type_conv=200)
			if initialized is None:
				# Older versions of kinterbasedb didn't have this attribute, so we write
				# it ourselves:
				kinterbasdb.initialized = True
		
		self.dbapi = kinterbasdb


	def getConnection(self, connectInfo, **kwargs):
		port = connectInfo.Port
		if not port:
			port = 3050
		# kinterbasdb will barf with unicode strings:
		host = str(connectInfo.Host)
		user = str(connectInfo.User)
		password = str(connectInfo.revealPW())
		database = str(connectInfo.Database)
		
		self._connection = self.dbapi.connect(host=host, user=user, 
				password=password, database=database, **kwargs)
		return self._connection
		

	def getDictCursorClass(self):
		return self.dbapi.Cursor
		

	def noResultsOnSave(self):
		""" Firebird does not return the number of records updated, so
		we just have to ignore this, since we can't tell a failed save apart 
		from a successful one.
		"""
		return
	
	
	def noResultsOnDelete(self):
		""" Firebird does not return the number of records deleted, so
		we just have to ignore this, since we can't tell a failed delete apart 
		from a successful one.
		"""
		return
		

	def processFields(self, txt):
		""" Firebird requires that all field names be surrounded 
		by double quotes.
		"""
		return self.dblQuoteField(txt)


	def escQuote(self, val):
		# escape backslashes and single quotes, and
		# wrap the result in single quotes
		sl = "\\"
		qt = "\'"
		return qt + val.replace(sl, sl+sl).replace(qt, qt+qt) + qt
	
	
	def formatDateTime(self, val):
		""" We need to wrap the value in quotes. """
		sqt = "'"		# single quote
		return "%s%s%s" % (sqt, str(val), sqt)


	def getTables(self, cursor, includeSystemTables=False):
		if includeSystemTables:
			whereClause = ''
		else:
			whereClause = "where rdb$relation_name not starting with 'RDB$' "
			
		cursor.execute("select rdb$relation_name from rdb$relations "
			"%s order by rdb$relation_name" % whereClause)
		rs = tempCursor.getDataSet()
		tables = []
		for record in rs:
			tables.append(record[0].strip())
		return tuple(tables)
		
		
	def getTableRecordCount(self, tableName, cursor):
		cursor.execute("select count(*) as ncount from %s where 1=1" % tableName)
		return tempCursor.getDataSet()[0][0]


	def getFields(self, tableName, cursor):
		# Get the PK
		sql = """ select inseg.rdb$field_name
		from rdb$indices idxs join rdb$index_segments inseg
			on idxs.rdb$index_name = inseg.rdb$index_name
			where idxs.rdb$relation_name = '%s'
	and idxs.rdb$unique_flag = 1 """ % tableName.upper()
		cursor.execute(sql)
		rs = cursor.getDataSet(rows=1)
		try:
			pkField = rs[0].strip()
		except:
			pkField = None
		
		# Now get the field info
		sql = """  SELECT b.RDB$FIELD_NAME, d.RDB$TYPE_NAME,
 c.RDB$FIELD_LENGTH, c.RDB$FIELD_SCALE, b.RDB$FIELD_ID
 FROM RDB$RELATIONS a
 INNER JOIN RDB$RELATION_FIELDS b
 ON a.RDB$RELATION_NAME = b.RDB$RELATION_NAME
 INNER JOIN RDB$FIELDS c
 ON b.RDB$FIELD_SOURCE = c.RDB$FIELD_NAME
 INNER JOIN RDB$TYPES d
 ON c.RDB$FIELD_TYPE = d.RDB$TYPE
 WHERE a.RDB$SYSTEM_FLAG = 0
 AND d.RDB$FIELD_NAME = 'RDB$FIELD_TYPE'
 AND a.RDB$RELATION_NAME = '%s'
 ORDER BY b.RDB$FIELD_ID """ % tableName.upper()
 
		cursor.execute(sql)
		rs = cursor.getDataSet()
		fields = []
		for r in rs:
			name = r[0].strip()

			ftype = r[1].strip().lower()
			if ftype == "text":
				ft = "C"
			elif ftype == "varying":
				if r[2] > 64:
					ft = "M"
				else:
					ft = "C"
			elif ftype in ("long", "short", "int64", "double"):
				# Can be either integers or float types, depending on column 3
				if r[3] == 0:
					# integer
					ft = "I"
				else:
					ft = "N"
			elif ftype == "float":
				ft = "N"
			elif ftype == "date":
				ft = "D"
			elif ftype == "time":
				# Default it to character for now
				ft = "C"
			elif ftype == "timestamp":
				ft = "T"
			elif ftype == "blob":
				ft = "L"
			else:
				ft = "?"
			
			if pkField is None:
				# No pk defined for the table
				pk = False
			else:
				pk = (name.lower() == pkField.lower() )
			
			fields.append((name.strip().lower(), ft, pk))
		return tuple(fields)

	
	def beginTransaction(self, cursor):
		""" Begin a SQL transaction."""
		if not self._connection._has_transaction():
			self._connection.begin()
			dabo.dbActivityLog.write("SQL: begin")

		
	def flush(self, cursor):
		""" Firebird requires an explicit commit in order to have changes
		to the database written to disk.
		"""
		self._connection.commit()
		dabo.dbActivityLog.write("SQL: commit")

	
	def getLimitWord(self):
		""" Override the default 'limit', since Firebird doesn't use that. """
		return "first"
		

	def formSQL(self, fieldClause, fromClause, joinClause,
				whereClause, groupByClause, orderByClause, limitClause):
		""" Firebird wants the limit clause before the field clause.	"""
		clauses =  (limitClause, fieldClause, fromClause, joinClause, 
				whereClause, groupByClause, orderByClause)
		sql = "SELECT " + "\n".join( [clause for clause in clauses if clause] )
		return sql


	def massageDescription(self, cursor):
		"""Force all the field names to lower case."""
		dd = cursor.descriptionClean = cursor.description
		if dd:
			cursor.descriptionClean = tuple([(elem[0].lower(), elem[1], elem[2], 
					elem[3], elem[4], elem[5], elem[6]) 
					for elem in dd])
	

	def pregenPK(self, cursor):
		"""Determines the generator for which a 'before-insert' trigger
		is associated with the cursor's table. If one is found, get its 
		next value and return it. If not, return None.
		"""
		ret = None
		sql = """select rdb$depended_on_name as genname
				from rdb$dependencies
				where rdb$dependent_type = 2
				and rdb$depended_on_type = 14
				and rdb$dependent_name =
				(select rdb$trigger_name from rdb$triggers
				where rdb$relation_name = '%s'
				and rdb$trigger_type = 1 )""" % cursor.Table.upper()
		cursor.execute(sql)
		if cursor.RowCount:
			gen = cursor.getFieldVal("genname").strip()
			sql = """select GEN_ID(%s, 1) as nextval 
					from rdb$database""" % gen
			cursor.execute(sql)
			ret = cursor.getFieldVal("nextval")
		dabo.dbActivityLog.write("SQL: result of pregenPK: %d" % ret)
		return ret
	

	def setSQL(self, sql):
		return self.dblQuoteField(sql)
	def setFieldClause(self, clause, autoQuote=True):
		if autoQuote:
			clause = self.dblQuoteField(clause)
		return clause
	def setFromClause(self, clause, autoQuote=True):
		if autoQuote:
			clause = self.dblQuoteField(clause)
		return clause
	def setWhereClause(self, clause, autoQuote=True):
		if autoQuote:
			clause = self.dblQuoteField(clause)
		return clause
	def setChildFilterClause(self, clause, autoQuote=True):
		if autoQuote:
			clause = self.dblQuoteField(clause)
		return clause
	def setGroupByClause(self, clause, autoQuote=True):
		if autoQuote:
			clause = self.dblQuoteField(clause)
		return clause
	def setOrderByClause(self, clause, autoQuote=True):
		if autoQuote:
			clause = self.dblQuoteField(clause)
		return clause


	def dblQuoteField(self, txt):
		""" Takes a string and returns the same string with
		all occurrences of xx.yy replaced with xx."YY".
		In other words, wrap the field name in double-quotes,
		and change it to upper case.
		"""
		def qtField(mtch):
			tbl = mtch.groups()[0]
			fld = mtch.groups()[1].upper()
			return "%s.\"%s\"" % (tbl, fld)
		return self.fieldPat.sub(qtField, txt)


# Test method for all the different field structures, just 
# like dblQuoteField().
# def q(txt):
# 	def qtField(mtch):
# 		tbl = mtch.groups()[0]
# 		fld = mtch.groups()[1].upper()
# 		return "%s.\"%s\"" % (tbl, fld)
# 	return pat.sub(qtField, txt)
# 		
