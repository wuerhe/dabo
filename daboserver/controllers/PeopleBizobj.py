#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dabo

class PeopleBizobj(dabo.biz.RemoteBizobj):
	def defineConnection(self):
		self.setConnectionParams(
				dbType="MySQL", 
				database="webtest", 
				host="dabodev.com",
				user="webuser",
				plainTextPassword="foxrocks")


	def validateRecord(self):
		"""Place record validation code here"""
		pass
			
