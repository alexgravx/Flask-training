from flask import Flask
from .views import app
from . import models

@app.cli.command("init_db")
def init_db():
    models.init_db()