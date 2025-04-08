#!/usr/bin/env python3
import os

import aws_cdk as cdk
from parser.parser import Parser



app = cdk.App()
config = app.node.try_get_context("config")
default_config_path = "default_config.yaml"
parser = Parser(app=app, configName=config, defaultConfigPath=default_config_path)
#parser.run()


app.synth()
