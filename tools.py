try:
    import faker, random, time, datetime, os, selenium, threading, pickle, sys, mysql.connector, json, re, curses, traceback, string, imaplib, email, pytz, subprocess, socket, io, requests, winreg, hashlib, inspect, shutil, importlib
    import tkinter as tk
    from tkinter import filedialog
    from typing import Optional
    from selenium.webdriver.remote.webelement import WebElement
    from pathlib import Path
    from os import system
    from functools import wraps
    from dotenv import load_dotenv
    from dotenv import set_key
    from selenium import webdriver
    from fake_useragent import UserAgent
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import (
        TimeoutException,
        NoSuchElementException,
        ElementNotVisibleException,
        ElementNotInteractableException,
        StaleElementReferenceException,
        WebDriverException,
        NoSuchWindowException,
        NoSuchFrameException,
        ElementNotSelectableException,
        ElementClickInterceptedException,
    )
    from unidecode import unidecode
    from colorama import *
    from datetime import timedelta
    from selenium.webdriver.common.action_chains import ActionChains
    from twocaptcha import TwoCaptcha
    from faker import Faker
    from collections import OrderedDict
except ModuleNotFoundError as e:
    try:
        import subprocess
        import os
        import sys

        subprocess.run([sys.executable, "-m", "venv", ".env"])

        # Activer l'environnement virtuel
        if os.name == 'nt':  # Pour Windows
            activate_script = ".\\.env\\Scripts\\activate.bat"

        # Cette commande change le shell actuel et ne retourne pas, donc toutes les commandes suivantes doivent être exécutées dans un script shell.
        os.system(f"source {activate_script}")

        if os.path.exists("requirements.txt"):
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        else:
            print("Le fichier requirements.txt n'existe pas, veuillez installer les dépendances manuellement")

        print("Les dépendances ont été installées, merci de relancer le programme")
    except Exception as e:
        print("Erreur: " + str(e))

    exit()

# Récupérer les variables d'environnement
load_dotenv()

def timezone():
    default_tz_name = "Europe/Paris"
    tz_name = os.getenv("timezone", default_tz_name)
    try:
        return pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        return pytz.timezone(default_tz_name)

def stop():
    t = input("Appuyez sur une touche pour quitter")
    sys.exit()

def print_msg(msg, color):
    colors = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "cyan": Fore.CYAN,
        "blue": Fore.BLUE,
        "yellow": Fore.YELLOW
    }
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if color in colors:
        print(f"{Style.BRIGHT}{colors[color]} {date} | {msg} {Style.RESET_ALL}")
    else:
        print(f"{Style.BRIGHT}{Fore.WHITE} {date} | {msg} {Style.RESET_ALL}")


def serialize_to_json(data, fallback=None):
    """
    Sérialise les données en JSON.

    :param data: Données à sérialiser
    :param fallback: Valeur de repli si la sérialisation échoue
    :return: Données sérialisées en JSON ou valeur de repli
    """
    try:
        return json.dumps(data)
    except:
        return fallback

def deserialize_from_json(data, fallback=None):
    """
    Désérialise les données JSON.

    :param data: Données à désérialiser
    :param fallback: Valeur de repli si la désérialisation échoue
    :return: Données désérialisées ou valeur de repli
    """
    try:
        return json.loads(data)
    except:
        return fallback