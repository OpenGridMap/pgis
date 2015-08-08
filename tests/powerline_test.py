from flask import Flask
from app import GisApp
import unittest
import os
from flask.ext.testing import TestCase
from flask_environments import Environments

class MyTest(TestCase):

    def create_app(self):
        env = Environments(GisApp)
        return GisApp 

    def test_serialize(self):
        response = self.client.get("/powerlines")
        self.assertEquals(response.json, [])

 
