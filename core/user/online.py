from core.user import user_main,normal_user,loading_user,user
from core.event import event
from core.ibs_exceptions import *
import copy

class OnlineUsers:
    def __init__(self):
	self.user_onlines={}#user_id=>user_obj
	self.ras_onlines={}#(ras_id,unique_id)=>user_obj
	self.loading_user=loading_user.LoadingUser()

    def __loadUserObj(self,loaded_user,obj_type):
	return user.User(loaded_user,obj_type)

##############################################
    def __addToOnlines(self,user_obj):
	self.user_onlines[user_obj.getUserID()]=user_obj
	self.ras_onlines[user_obj.getGlobalUniqueID(user_obj.instances)]=user_obj

    def __removeFromOnlines(self,user_obj,global_unique_id):
	del(self.user_onlines[user_obj.getUserID()])
	del(self.ras_onlines[global_unique_id])
	

############################################
    def getOnlineUsers(self):
	return copy.copy(self.user_onlines)


############################################
    def isUserOnline(self,user_id):
	return self.user_onlines.has_key(user_id)

    def getUserObj(self,user_id):
	"""
	    return User instance of online user, or None if no user is online
	"""
	try:
	    return self.user_onlines[user_id]
	except KeyError:
	    return None

    def getUserObjByUniqueID(self,ras_id,unique_id_val):
	"""
	    return User instance of online user, or None if no user is online
	"""
	try:
	    return self.ras_onlines[(ras_id,unique_id_val)]
	except KeyError:
	    return None
	


############################################
    def reloadUser(self,user_id):
	self.loading_user.loadingStart(loaded_user.getUserID())
	try:
	    user_obj=getUserObj(user_id)
	    if user_obj==None:
		toLog("Reload User called while user is not online for user_id: %s"%user_id,LOG_ERROR)
	    else:
		user_obj._reload()
	finally:
	    self.loading_user.loadingEnd(loaded_user.getUserID())

##############################################
    def updateUser(self,ras_msg):
	user_obj=self.getUserObjByUniqueID(ras_msg.getRasID(),ras_msg.getUniqueIDValue())
	if user_obj==None:
	    toLog("Update User called while user is not online for ras_id: %s unique_id_value:%s"%(ras_msg.getRasID(),ras_msg.getUniqueIDValue()),LOG_ERROR)
	    return None
	self.loading_user.loadingStart(user_obj.getUserID())
	try:
	    user_obj.update(ras_msg)
	finally:
	    self.loading_user.loadingEnd(user_obj.getUserID())

#############################################
    def internetAuthenticate(self,ras_msg):
	loaded_user=user_main.getUserPool().getUserByNormalUsername(ras_msg["username"],True)
	self.loading_user.loadingStart(loaded_user.getUserID())
	try:
	    try:
	        user_obj=self.getUserObj(loaded_user.getUserID())
		if user_obj==None:
		    user_obj=self.__loadUserObj(loaded_user,"Normal")
	        user_obj.login(ras_msg)
		self.internetAuthenticateSuccessfull(user_obj)
	    except:
		loaded_user.setOnlineFlag(False)
		raise
	finally:
	    self.loading_user.loadingEnd(loaded_user.getUserID())
	    
    def internetAuthenticateSuccessfull(self,user_obj):
	self.__addToOnlines(user_obj)
	self.recalcNextUserEvent(user_obj.getUserID(),user_obj.instances>1)
############################################
    def internetStop(self,ras_msg):
	loaded_user=user_main.getUserPool().getUserByNormalUsername(ras_msg["username"])
	self.loading_user.loadingStart(loaded_user.getUserID())
	try:
	    user_obj=self.getUserObj(loaded_user.getUserID())
	    if user_obj==None:
		toLog("Got internet stop for user %s, but he's not online"%ras_msg["username"],LOG_DEBUG)
	        return
	    instance=user_obj.getInstanceFromRasMsg(ras_msg)
	    if instance==None:
		raise LoginException(errorText("USER","CANT_FIND_INSTANCE")%(loaded_user.getUserID(),ras_msg.getRasID(),ras_msg.getUniqueIDValue()))

	    global_unique_id=user_obj.getGlobalUniqueID(user_obj.instances)
	    user_obj.logout(instance,ras_msg)
	    if user_obj.instances==0:
		self.__removeFromOnlines(user_obj,global_unique_id)
		self.__removePrevUserEvent(user_obj.getUserID())
		loaded_user.setOnlineFlag(False)
	    else:
		self.recalcNextUserEvent(user_obj.getUserID(),True)
	finally:
	    self.loading_user.loadingEnd(loaded_user.getUserID())
    
############################################
    def recalcNextUserEvent(self,user_id,remove_prev_event=False):
	"""
	    recalculates user next event.
	    user_id(int): id of user we recalculate event
	    remove_prev_event(bool): Remove user previous event. This flag should be set by reload method
	"""
	self.loading_user.loadingStart(user_id)
	try:
	    user_obj=self.getUserObj(user_id)
	    if user_obj==None:
		toLog("recalcNextUserEvent Called for user id %s while he's not online"%user_id,LOG_DEBUG)
		return
	    if remove_prev_event:
		self.__removePrevUserEvent(user_id)
	    result=user_obj.canStayOnline()
	    self.__killUsersInCanStayOnlineResult(user_obj,result)
	    self.__setNextUserEvent(result,user_id)
	finally:
	    self.loading_user.loadingEnd(user_id)

    def __removePrevUserEvent(self,user_id):
	event.removeEvent(self.recalcNextUserEvent,[user_id,False])

    def __setNextUserEvent(self,result,user_id):
	next_evt=result.getEventTime()
	toLog("Next Evt:%s"%next_evt,LOG_DEBUG)
	if next_evt!=0:
	    event.addEvent(next_evt,self.recalcNextUserEvent,[user_id,False])

    def __killUsersInCanStayOnlineResult(self,user_obj,result):
	kill_dic=result.getKillDic()
	for instance in kill_dic:
	    user_obj.setKillReason(instance,kill_dic[instance])
	    user_obj.getTypeObj().killInstance(instance)
		