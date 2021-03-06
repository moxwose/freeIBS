from core.user import user_plugin,user_main,attribute
from core.user.attr_updater import AttrUpdater
from core.user.attr_searcher import AttrSearcher
from core.ibs_exceptions import *
from core.errors import errorText
from core.lib.general import *
from core.lib.multi_strs import MultiStr
from core.lib.password_lib import Password,getPasswords
from core.db import ibs_db,db_main
from core.db.ibs_query import IBSQuery
from core.server import handler,handlers_manager

import itertools

attr_handler_name="normal user"

def init():
    user_main.getAttributeManager().registerHandler(NormalUserAttrHandler(),["normal_username","normal_password","normal_generate_password","normal_generate_password_len","normal_save_usernames"],["normal_username"],[])
    handlers_manager.getManager().registerHandler(NormalUserHandler())


######################################################
check_username_pattern=re.compile("[^A-Za-z0-9_\-\.]")
def _checkNormalUsernameChars(username):
    if not len(username) or username[0] not in string.letters:
        return False
    if check_username_pattern.search(username) != None:
        return False
    return True
	    
def checkNormalUsernameChars(username):
    if not _checkNormalUsernameChars(username):
        raise GeneralException(errorText("USER_ACTIONS","BAD_NORMAL_USERNAME")%username)


##########################################################
def normalUsernameExists(normal_username):
    """
        check if normal_username currently exists
        normal_username(iterable object can be multistr or list): username that will be checked
        return a list of exists usernames
        NOTE: This is not thread safe 
        XXX: test & check where_clause length
    """
    if len(normal_username)==0:
        return []
    where_clause=" or ".join(map(lambda username:"normal_username=%s"%dbText(username),normal_username))
    users_db=db_main.getHandle().get("normal_users",where_clause,0,-1,"",["normal_username"])
    return [m["normal_username"] for m in users_db]
#########################################################


class NormalUserAttrUpdater(AttrUpdater):

    def __init__(self):
	AttrUpdater.__init__(self,attr_handler_name)

    def changeInit(self,normal_username,normal_password,generate_password,password_len,normal_save):
	"""
	    generate_passwd is an integer, 0 means don't generate password and use normal_passwords instead
	    positive values are same as password_lib.getPasswords _type, see function comments
	    
	    normal_save(str): tells if we should save this username passwords in database so
				username/passwords can be seen later, 
				If set to False or empty string it means don't save
				else it'll be passed as comment
				
	"""
	self.registerQuery("user","change",self.changeQuery,[])
	self.normal_username=normal_username
	self.normal_password=normal_password
	self.generate_password=generate_password
	self.password_len=to_int(password_len,"Password Length")
	self.normal_save=normal_save

    def deleteInit(self):
	self.registerQuery("user","delete",self.deleteQuery,[])

    def __parseNormalAttrs(self):
	self.usernames=map(None,MultiStr(self.normal_username))
	if self.generate_password==0:
	    pass_multi=MultiStr(self.normal_password)
	    self.passwords=map(lambda x:Password(pass_multi[x]),range(len(self.usernames)))
	else:
	    self.passwords=getPasswords(len(self.usernames),self.generate_password,self.password_len)
	
    ###############################################
    def checkInput(self,src,action,dargs):
	map(dargs["admin_obj"].canChangeNormalAttrs,dargs["users"].itervalues())
    
    def __changeCheckInput(self,users,admin_obj):
	self.__checkUsernames(users)
	self.__checkPasswords()

    def __checkPasswords(self):
	map(lambda password:password.checkPasswordChars(),self.passwords)
	if self.password_len < 0 or self.password_len > 30:
	    raise GeneralException(errorText("USER_ACTIONS","INVALID_PASSWORD_LENGTH")%self.password_len)


    def __checkUsernames(self,users):
	if len(self.usernames) != len(users):
	    raise GeneralException(errorText("USER_ACTIONS","NORMAL_USER_COUNT_NOT_MATCH")%(len(users),len(self.usernames)))
	
	cur_normal_usernames = []
	for loaded_user in users.itervalues():
	    if loaded_user.getUserAttrs().hasAttr("normal_username"):
	        cur_normal_usernames.append(loaded_user.getUserAttrs()["normal_username"])
	
	to_check_usernames = [] #check users for exitence
	for username in self.usernames:
	    checkNormalUsernameChars(username)

	    if self.usernames.count(username) > 1:
		raise GeneralException(errorText("USER_ACTIONS","DUPLICATE_USERNAME") % (username))

	    if username not in cur_normal_usernames:
		to_check_usernames.append(username)    
	
	exists=normalUsernameExists(to_check_usernames)
	if exists:
	    raise GeneralException(errorText("USER_ACTIONS","VOIP_USERNAME_EXISTS")%",".join(exists))

    ###############################################

    def changeQuery(self,ibs_query,src,action,**args):
	admin_obj=args["admin_obj"]
	users=args["users"]
	
	self.__parseNormalAttrs()
	self.__changeCheckInput(users,admin_obj)
	
	null_queries = IBSQuery()
	real_queries = IBSQuery()
	
	i=0
	for user_id in users:
	    loaded_user=users[user_id]
	    if loaded_user.hasAttr("normal_username"):
		null_queries += self.updateNormalUserAttrsToNullQuery(user_id)
		real_queries += self.updateNormalUserAttrsQuery(user_id,
							   self.usernames[i],
							   self.passwords[i].getPassword())
	    else:
		real_queries +=self.insertNormalUserAttrsQuery(user_id,
							   self.usernames[i],
							   self.passwords[i].getPassword())
	    i+=1

	ibs_query += null_queries
	ibs_query += real_queries
	
	if self.normal_save:
	    user_main.getAddUserSaveActions().newAddUser(ibs_query,
							 users.keys(),
							 self.usernames,
							 self.passwords,
							 admin_obj.getAdminID(),
							 "Normal",
							 "")
	return ibs_query

    def deleteQuery(self,ibs_query,src,action,**args):
	users=args["users"]

	for user_id in users:
	    ibs_query+=self.deleteNormalUserAttrsQuery(user_id)
	return ibs_query


####################################################
    def insertNormalUserAttrsQuery(self,user_id,normal_username,normal_password):
	"""
	    insert user normal attributes in "normal_users" table
	"""
	return ibs_db.createInsertQuery("normal_users",{"normal_username":dbText(normal_username),
							"normal_password":dbText(normal_password),
							"user_id":user_id}
					)


    def updateNormalUserAttrsToNullQuery(self,user_id):
	"""
	    update normal_username to null, we run into unique constraint violation, when updating multiple
	    users. So we update them to null and then update to new username
	"""
	return ibs_db.createUpdateQuery("normal_users",{"normal_username":"NULL"}
						       ,"user_id=%s"%user_id)
    
    def updateNormalUserAttrsQuery(self,user_id,normal_username,normal_password):
	"""
	    update user normal attributes in "normal_users" table
	"""
	return ibs_db.createUpdateQuery("normal_users",{"normal_username":dbText(normal_username),
							"normal_password":dbText(normal_password),
							},"user_id=%s"%user_id
					)
    def deleteNormalUserAttrsQuery(self,user_id):
	"""
	    delete user normal attributes from "normal_users" table
	"""
	return ibs_db.createDeleteQuery("normal_users","user_id=%s"%user_id)
	


#########################################################



class NormalUserAttrSearcher(AttrSearcher):
    def run(self):
	normal_table=self.getSearchHelper().getTable("normal_users")
	normal_table.likeStrSearch(self.getSearchHelper(),
			           "normal_username",
		    		   "normal_username_op",
				   "normal_username",
			           MultiStr
				  )

class NormalUserAttrHandler(attribute.AttributeHandler):
    def __init__(self):
	attribute.AttributeHandler.__init__(self,attr_handler_name)
	self.registerAttrUpdaterClass(NormalUserAttrUpdater,
				      ["normal_username",
				      "normal_password",
				      "normal_generate_password",
				      "normal_generate_password_len",
				      "normal_save_usernames"])
	self.registerAttrSearcherClass(NormalUserAttrSearcher)
#############################################################
class NormalUserHandler(handler.Handler):

    def __init__(self):
	handler.Handler.__init__(self,"normal_user")
	self.registerHandlerMethod("checkNormalUsernameForAdd")


    ############################################################
    def checkNormalUsernameForAdd(self,request):
	"""
	    check if normal_username multi str arg is exists, and doesn't contain invalid characters
	    current_username shows current usernames, so we don't run into situation that we print an error
	    for username that belongs to this username
	"""
	request.needAuthType(request.ADMIN)
	request.checkArgs("normal_username","current_username")
	request.getAuthNameObj().canDo("CHANGE NORMAL USER ATTRIBUTES")
	usernames=self.__filterCurrentUsernames(request)
	bad_usernames=filter(lambda username: not _checkNormalUsernameChars(username),usernames)
	exist_usernames=normalUsernameExists(usernames)
	return self.__createCheckAddReturnDic(bad_usernames,exist_usernames)

    def __filterCurrentUsernames(self,request):
	username=MultiStr(request["normal_username"])
	current_username=MultiStr(request["current_username"])
	return filter(lambda username: username not in current_username,username)

    def __createCheckAddReturnDic(self,bad_usernames,exist_usernames):
	ret={}
	if len(bad_usernames)!=0:
	    ret[errorText("USER_ACTIONS","BAD_NORMAL_USERNAME",False)%""]=bad_usernames
	if len(exist_usernames)!=0:
	    ret[errorText("USER_ACTIONS","NORMAL_USERNAME_EXISTS",False)%""]=exist_usernames
	return ret
	