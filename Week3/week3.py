import sqlite3

import streamlit as st
from pydantic import BaseModel
import streamlit_pydantic as sp

con = sqlite3.connect("addnote.sqlite", isolation_level=None)
cur = con.cursor()

cur.execute

