from core.user import user_plugin,user_main,attribute
from core.user.attr_updater import AttrUpdater
from core.user.attr_searcher import AttrSearcher
from core.ibs_exceptions import *
from core.errors import errorText
from core.lib.general import *
from core.lib.multi_strs import MultiStr
from core.lib.password_lib import Password,getPasswords
from core.db import ibs_db
import itertools

attr_handler_name="normal user"
def init():
    user_main.getAttributeManager().registerHandler(NormalUserAttrHandler(),["normal_username","normal_password","normal_generate_password","normal_generate_password_len","normal_save_usernames"],["normal_username"],[])

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
	self.usernames=MultiStr(self.normal_username)
	if self.generate_password==0:
	    pass_multi=MultiStr(self.normal_password)
	    self.passwords=map(lambda x:Password(pass_multi[x]),range(len(self.usernames)))
	else:
	    self.passwords=getPasswords(len(self.usernames),self.generate_password,self.password_len)
	
    def checkInput(self,src,action,dargs):
	map(dargs["admin_obj"].canChangeNormalAttrs,dargs["users"].itervalues())
    
    def __checkUserExistence(self,usernames,users):
	
	def usernameNotChanged(_tuple):
	    username,loaded_user=_tuple
	    return not ( loaded_user.hasAttr("normal_username") and username==loaded_user.getUserAttrs()["normal_username"])
	
	usernames=filter(usernameNotChanged,itertools.izip(usernames,users.itervalues()))
	exists=user_main.getActionManager().normalUsernameExists([m[0] for m in usernames])
	if len(exists):
	    raise GeneralException(errorText("USER_ACTIONS","NORMAL_USERNAME_EXISTS")%",".join(exists))

    def __changeCheckInput(self,users,admin_obj):
	if len(self.usernames)!=len(users):
	    raise GeneralException(errorText("USER_ACTIONS","NORMAL_COUNT_NOT_MATCH")%(len(users),len(self.usernames)))
	
	map(lambda password:password.checkPasswordChars(),self.passwords)
	map(user_main.getActionManager().checkNormalUsernameChars,self.usernames)
	if self.password_len<0 or self.password_len>30:
	    raise GeneralException(errorText("USER_ACTIONS","INVALID_PASSWORD_LENGTH")%self.password_len)
	self.__checkUserExistence(self.usernames,users)

    def changeQuery(self,ibs_query,src,action,**args):
	admin_obj=args["admin_obj"]
	users=args["users"]
	
	self.__parseNormalAttrs()
	self.__changeCheckInput(users,admin_obj)
	
	i=0
	for user_id in users:
	    loaded_user=users[user_id]
	    if loaded_user.hasAttr("normal_username"):
		ibs_query+=self.updateNormalUserAttrsQuery(user_id,
							   self.usernames[i],
							   self.passwords[i].getPassword())
	    else:
		ibs_query+=self.insertNormalUserAttrsQuery(user_id,
							   self.usernames[i],
							   self.passwords[i].getPassword())
	    i+=1

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


    def insertNormalUserAttrsQuery(self,user_id,normal_username,normal_password):
	"""
	    insert user normal attributes in "normal_users" table
	"""
	return ibs_db.createInsertQuery("normal_users",{"normal_username":dbText(normal_username),
							"normal_password":dbText(normal_password),
							"user_id":user_id}
					)

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
	