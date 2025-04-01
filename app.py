#!/usr/bin/env python3
import os

import aws_cdk as cdk
from parser.parser import Parser



app = cdk.App()
config = app.node.try_get_context("config")
print(config)
parser = Parser(app = app,configName = config)
parser.run()


app.synth()
