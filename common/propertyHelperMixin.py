class PropertyHelperMixin(object):
	""" Helper functions for getting information on class properties.
	"""

	def getProperties(self, propertySequence=(), *propertyArguments):
		""" Returns a dictionary of property name/value pairs.
		
		If a sequence of properties is passed, just those property values
		will be returned. Otherwise, all property values will be returned.
		The sequence of properties can be a list, tuple, or plain string
		positional arguments. For instance, all of the following are
		equivilent:
			
			print self.getProperties("Caption", "FontInfo", "Form")
			print self.getProperties(["Caption", "FontInfo", "Form"])
			t = ("Caption", "FontInfo", "Form")
			print self.getProperties(t)
			print self.getProperties(*t)
		"""
		propDict = {}
		
		def _fillPropDict(_propSequence):
			for prop in _propSequence:
				propRef = eval("self.__class__.%s" % prop)
				if type(propRef) == property:
					getter = propRef.fget
					if getter is not None:
						propDict[prop] = getter(self)
					else:
						raise ValueError, "Property '%s' is not readable." % prop
				else:
					raise AttributeError, "'%s' is not a property." % prop
		if type(propertySequence) in (list, tuple):
			_fillPropDict(propertySequence)
		else:
			if type(propertySequence) in (str, unicode):
				propertyArguments = list(propertyArguments)
				propertyArguments.append(propertySequence)
				propertyArguments = tuple(propertyArguments)
		_fillPropDict(propertyArguments)
		if len(propertyArguments) == 0 and len(propertySequence) == 0:
			# User didn't send a list of properties, so return all properties:
			_fillPropDict(self.getPropertyList())
		return propDict

	
	def setProperties(self, propDict={}, **propKw):
		""" Sets a group of properties on the object all at once.
			
		You have the following options for sending the properties:
			1) Property/Value pair dictionary
			2) Keyword arguments
			3) Both
	
		The following examples all do the same thing:
		self.setProperties(FontBold=True, ForeColor="Red")
		self.setProperties({"FontBold": True, "ForeColor": "Red")
		self.setProperties({"FontBold": True}, ForeColor="Red")
		"""
		def _setProps(_propDict):
			for prop in _propDict.keys():
				propRef = eval("self.__class__.%s" % prop)
				if type(propRef) == property:
					setter = propRef.fset
					if setter is not None:
						setter(self, _propDict[prop])
					else:
						# not sure what to do here
						raise ValueError, "Property '%s' is read-only." % prop
				else:
					raise AttributeError, "'%s' is not a property." % prop
					
		# Set the props specified in the passed propDict dictionary:
		_setProps(propDict)
	
		# Set the props specified in the keyword arguments:
		_setProps(propKw)

			
	def getPropertyList(classOrInstance):
		""" Returns the list of properties for this object (class or instance).
		"""
		propList = []
		for item in dir(classOrInstance):
			if type(eval("classOrInstance.%s" % item)) == property:
				propList.append(item)
		return propList
	getPropertyList = classmethod(getPropertyList)


	def getPropertyInfo(self, name):
		""" Returns a dictionary of information about the passed property name.
		"""
		propRef = eval("self.__class__.%s" % name)
		propVal = eval("self.%s" % name)

		if type(propRef) == property:
			d = {}
			d["name"] = name

			if propRef.fget:
				d["showValueInDesigner"] = True
			else:
				d["showValueInDesigner"] = False

			if propRef.fset:
				d["editValueInDesigner"] = True
			else:
				d["editValueInDesigner"] = False

			d["doc"] = propRef.__doc__

			dataType = d["type"] = type(propVal)

			try:
				d["editorInfo"] = eval("self._get%sEditorInfo()" % name)
			except:
				# There isn't an explicit editor setup, so let's derive it:
				if dataType in (str, unicode):
					d["editorInfo"] = {"editor": "string", "len": 256}
				elif dataType == bool:
					d["editorInfo"] = {"editor": "boolean"}
				elif dataType in (int, long):
					d["editorInfo"] = {"editor": "integer", "min": -65535, "max": 65536}
				else:
					# punt
					d["editorInfo"] = {"editor": "string"}
			return d
		else:
			raise AttributeError, "%s is not a property." % name

	
