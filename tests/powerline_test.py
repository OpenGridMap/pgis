from flask import Flask
from app import GisApp
import unittest
from flask.ext.testing import TestCase

class MyTest(TestCase):

    def create_app(self):
        GisApp.config['TESTING'] = True
        # Default port is 5000
        GisApp.config['LIVESERVER_PORT'] = 8943
        return GisApp 

    def test_serialize(self):
        response = self.client.get("/powerlines")
        self.assertEquals(response.json, [])

 
