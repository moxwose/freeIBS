import re
import string
import time
import random
import sys
import traceback
import os	
import imp
import types
from core.ibs_exceptions import *
from core.errors import errorText

def isValidName(name):
    """
	check if "name" is valid, names can contain alphanumerics and "_" character
	return True if name is valid and False if it's not
    """
    return len(name)!=0 and re.search("[^a-zA-Z0-9_]",name)==None 

###############################
def escapeStr(_str):
    _str=str(_str)
    _str=re.sub("(['\0\"\\\\])",r'\\\1',_str)
    _str=re.sub("<(?!br( /){0,1}>)(.*?)>",r" - \1 - ",_str)
    return _str

def dbText(text):
    return "'"+escapeStr(text)+"'"

###############################
def dbNull(var):
    """
	return "null" if var is None
	else return var value
    """
    if var==None:
	return "NULL"
    return var


def requestDicToList(var):
    """
	some xml implementions return dictionaries even the unserialized data was in array.
	This function convert it to list if it's a dic
    """
    if type(var)==types.DictType:
	return var.values()
    else:
	return var

###############################
def integer(_str):
    """
	convert _str to integer, supress errors, and return 0 if _str is not a digit
    """
    _str = str(_str)
    #just remove dot in the _str
    if _str.count("."):
	_str = _str[:_str.index(".")]
    try:
	num=string.atoi(_str)
    except:
	return 0
    return num


def isInt(var):
    """
	check if "var" type is integer
	return 1 if it's an integer or 0 if it's not
    """
    if type(var)==types.IntType:
	return True
    return False


def isFloat(var):
    """
	check if "var" type is flot
	return 1 if it's an flot or 0 if it's not
    """
    if type(var)==types.FloatType:
	return True
    return False


def to_int(_str,excp):
    """
	convert _str to int, 
	excp(str or Exception instance): raise this exception if _str is not convertable to integer
    """
    try:
	_int=int(_str)
    except:
	if type(excp)==types.StringType:
	    raise GeneralException(errorText("GENERAL","INVALID_INT_VALUE")%excp)
	else:
	    raise excp
    return _int

def to_float(_str,var_name):
    """
	convert _str to float, raise an GeneralException on error with var_name
    """
    try:
	_int=float(_str)
    except:
	raise GeneralException(errorText("GENERAL","INVALID_FLOAT_VALUE")%var_name)
    return _int


def to_str(obj,var_name):
    """
	convert obj to str, raise an GeneralException on error	with var_name
    """
    try:
	_str=str(obj)
    except:
	raise GeneralException(errorText("GENERAL","INVALID_STRING_VALUE")%var_name)
    return _str


def to_list(obj,var_name):
    """
	convert obj to list, raise an GeneralException on error	with var_name
    """
    try:
	_list=list(obj)
    except:
	raise GeneralException(errorText("GENERAL","INVALID_LIST_VALUE")%var_name)
    return _list

##################################

def checkEmailAddress(email_address):
    email_address=email_address.strip()
    if email_address=="":
	return
    if re.match('^[a-zA-Z][a-zA-Z0-9\._]*@[a-zA-Z0-9_]+\.[a-zA-Z0-9\._]+$',email_address)==None:
	raise GeneralException(errorText("USER_ACTIONS","BAD_EMAIL")%email_address)


def import_module(module_name,_globals):
    """ import module_name in global scope. _globals is a dictionary that returned by globals() internal method
	it's necassary because some module import ibs_server and we can't import them 
	on top of file because they import us and we import them and python interpreter stops importing out file """
	
    (file,pathname,description)=imp.find_module(module_name)
    module_object=imp.load_module(module_name,file,pathname,description)
    _globals[module_name]=module_object


def checkDBBool(bool_var,name=""):
    """
	check if bool_var is a boolen value that can be used for db queries
	it must be "t" or "f"
	raise an exception if it isn't
	optional argument "name" is used in raised exception to identify the variable name
    """
    if bool_var != "t" and bool_var != "f":
	raise GeneralException(errorTexT("GENERAL","INVALID_BOOL_VALUE")%name)

#################################
def checkltgtOperator(op):
    if op not in ("=",">","<",">=","<="):
        raise GeneralException(errorText("USER_ACTIONS","INVALID_OPERATOR")%op)
