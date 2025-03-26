#!/usr/bin/env python3
import os

import aws_cdk as cdk
from parser.parser import Parser



app = cdk.App()
parser = Parser(app = app)
parser.run()


app.synth()
