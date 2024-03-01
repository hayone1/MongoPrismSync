import argparse
import asyncio
import base64
from collections import defaultdict
from dataclasses import dataclass
import json, yaml
import aiofiles
import os
import pathlib
import re
import tempfile
from typing import Self
from mongocd.Core import utils
from pydantic import BaseModel
from mongocd import logger
from pymongo import MongoClient, database

class TemplatesFiles:
    getCollectionData = 'get-data.js'
    functions = 'functions.js'
    copyIndices = 'copy-indices.js'
    deepCompareCopy = 'deep-compare-copy.js'
    duplicateCollection = 'duplicate-collection.js'
    copyData = 'copy-data.js'
    backup_suffix = '_cd_backup'
    init_script = 'init_script.js'
    main_script = 'main.js'
    post_script = 'post_script.js'
    cleanupDuplicateCollection = 'delete-duplicate-collection.js'