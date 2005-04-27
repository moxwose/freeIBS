from core.user import user_main,normal_user,loading_user,user
from core.event import event,periodic_events
from core.ibs_exceptions import *
from core.errors import errorText
from core.ras.msgs import RasMsg
from core.ras import ras_main
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
    
    def getOnlineUsersByRas(self):
	return copy.copy(self.ras_onlines)

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
	self.loading_user.loadingStart(user_id)
	try:
	    user_obj=self.getUserObj(user_id)
	    if user_obj==None:
		toLog("Reload User called while user is not online for user_id: %s"%user_id,LOG_ERROR)
	    else:
		user_obj._reload()
		self.recalcNextUserEvent(user_obj.getUserID(),True)
	finally:
	    self.loading_user.loadingEnd(user_id)

##############################################
    def updateUser(self,ras_msg):
	user_obj=self.getUserObjByUniqueID(ras_msg.getRasID(),ras_msg.getUniqueIDValue())
	if user_obj==None:
	    toLog("Update User called while user is not online for ras_id: %s unique_id_value:%s"%(ras_msg.getRasID(),ras_msg.getUniqueIDValue()),LOG_ERROR)
	    return None
	self.loading_user.loadingStart(user_obj.getUserID())
	try:
	    recalc_event=user_obj.update(ras_msg)
	    if recalc_event:
		self.recalcNextUserEvent(user_obj.getUserID(),user_obj.instances>1 or (user_obj.instances==1 and not ras_msg.hasAttr("start_accounting")))
	finally:
	    self.loading_user.loadingEnd(user_obj.getUserID())

    
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
	event.removeEvent(self.recalcNextUserEvent,[user_id,False],True)

    def __setNextUserEvent(self,result,user_id):
	next_evt=result.getEventTime()
#	toLog("Next Evt:%s"%next_evt,LOG_DEBUG)
	if next_evt!=0:
	    event.addEvent(next_evt,self.recalcNextUserEvent,[user_id,False])

    def __killUsersInCanStayOnlineResult(self,user_obj,result):
	kill_dic=result.getKillDic()
	for instance in kill_dic:
	    user_obj.setKillReason(instance,kill_dic[instance])
	    user_obj.getTypeObj().killInstance(instance)
#############################################
    def checkOnlines(self):
	"""
	    check ibs current list of online users, by asking ras to say if user is online or not
	"""
	for user_id in self.user_onlines.keys():
	    self.loading_user.loadingStart(user_id)
	    try:
		if user_id in self.user_onlines:
		    user_obj=self.user_onlines[user_id]
		    for instance in range(1,user_obj.instances+1):
			instance_info=user_obj.getInstanceInfo(instance)
			user_msg=user_obj.createUserMsg(instance,"IS_ONLINE")
			if user_msg.send():
			    instance_info["check_online_fails"]=0
			else:
			    instance_info["check_online_fails"]+=1
			    if instance_info["check_online_fails"]==defs.CHECK_ONLINE_MAX_FAILS:
				toLog("Maximum Check Online Fails Reached for user %s"%user_id,LOG_DEBUG)
				self.__forceLogoutUser(user_obj,instance,errorText("USER_LOGIN","MAX_CHECK_ONLINE_FAILS_REACHED",False))
	    except:
		logException(LOG_ERROR)
	    self.loading_user.loadingEnd(user_id)

	
################################################
    def __forceLogoutUser(self,user_obj,instance,kill_reason,no_commit=False):
	"""
	    force logout "instance" of "user_obj"
	    This is done by creating a fake ras_msg and send it to appropiate logout method
	"""
	ras_msg=self.__createForceLogoutRasMsg(user_obj,instance)
	method=self.__populateRasMsg(user_obj,instance,ras_msg)
	if method==None:
	    toLog("Don't know how to force logout user %s instance %s"%(self.user_obj.getUserID(),instance),LOG_ERROR|LOG_DEBUG)
	    return
	user_obj.setKillReason(instance,kill_reason)
	
	if no_commit:
	    ras_msg["no_commit"]=True
	    
	return apply(method,[ras_msg])

    def __createForceLogoutRasMsg(self,user_obj,instance):
	instance_info=user_obj.getInstanceInfo(instance)
	ras_msg=RasMsg(None,None,ras_main.getLoader().getRasByID(instance_info["ras_id"]))
	return ras_msg
    
    def __populateRasMsg(self,user_obj,instance,ras_msg):
	"""
	    should set necessary ras_msg attribute and return the logout method
	"""
	instance_info=user_obj.getInstanceInfo(instance)
	ras_msg["unique_id"]=instance_info["unique_id"]
	ras_msg[instance_info["unique_id"]]=instance_info["unique_id_val"]
	ras_msg["user_id"]=user_obj.getUserID()
	if user_obj.isNormalUser():
	    ras_msg["username"]=user_obj.getUserAttrs()["normal_username"]
	    if user_obj.getTypeObj().isPersistentLanClient(instance):
		ras_msg.setAction("PERSISTENT_LAN_STOP")
		return self.persistentLanStop
	    else:
	        ras_msg.setAction("INTERNET_STOP")
		return self.internetStop

	elif user_obj.isVoIPUser():
	    ras_msg["voip_username"]=user_obj.getUserAttrs()["normal_username"]
	    ras_msg.setAction("VOIP_STOP")
	    return self.voipStop
#############################################
    def clearUser(self,user_obj,instance,kill_reason):
	"""
	    clear user from online, without deducting credit
	"""
	self.loading_user.loadingStart(user_obj.getUserID())
	try:
	    self.__forceLogoutUser(user_obj,instance,kill_reason,True)
	finally:
	    self.loading_user.loadingEnd(user_obj.getUserID())

#############################################
    def internetAuthenticate(self,ras_msg):
	loaded_user=user_main.getUserPool().getUserByNormalUsername(ras_msg["username"],True)
	self.loading_user.loadingStart(loaded_user.getUserID())
	try:
	    user_obj=None
	    try:
	        user_obj=self.getUserObj(loaded_user.getUserID())

		if user_obj==None:
		    user_obj=self.__loadUserObj(loaded_user,"Normal")
		elif not user_obj.isNormalUser():
		    raise GeneralException(errorText("USER_LOGIN","CANT_USE_MORE_THAN_ONE_SERVICE"))
		    
	        user_obj.login(ras_msg)
		self.__authenticateSuccessfull(user_obj,ras_msg)
	    except:
		if user_obj!=None and user_obj.instances==0:
	    	    loaded_user.setOnlineFlag(False)
		raise
	finally:
	    self.loading_user.loadingEnd(loaded_user.getUserID())
	    
    def __authenticateSuccessfull(self,user_obj,ras_msg):
	self.__addToOnlines(user_obj)
	if ras_msg.hasAttr("start_accounting"):
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
		toLog(errorText("USER","CANT_FIND_INSTANCE")%(loaded_user.getUserID(),ras_msg.getRasID(),ras_msg.getUniqueIDValue()),LOG_DEBUG)
		return

	    global_unique_id=user_obj.getGlobalUniqueID(user_obj.instances)
	    user_obj.logout(instance,ras_msg)
	    self.__logoutRecalcEvent(user_obj,global_unique_id)
	finally:
	    self.loading_user.loadingEnd(loaded_user.getUserID())


    def __logoutRecalcEvent(self,user_obj,global_unique_id):
	    if user_obj.instances==0:
		self.__removePrevUserEvent(user_obj.getUserID())
		user_obj.getLoadedUser().setOnlineFlag(False)
		user_main.getUserPool().userChanged(user_obj.getUserID())
		self.__removeFromOnlines(user_obj,global_unique_id)
	    else:
		self.recalcNextUserEvent(user_obj.getUserID(),True)

#########################################################
    def persistentLanAuthenticate(self,ras_msg):
	loaded_user=user_main.getUserPool().getUserByID(ras_msg["user_id"],True)
	self.loading_user.loadingStart(loaded_user.getUserID())
	try:
	    user_obj=None
	    try:
	        user_obj=self.getUserObj(loaded_user.getUserID())
		if user_obj==None:
	    	    user_obj=self.__loadUserObj(loaded_user,"Normal")
		elif not user_obj.isNormalUser():
		    raise GeneralException(errorText("USER_LOGIN","CANT_USE_MORE_THAN_ONE_SERVICE"))
		    
	        user_obj.login(ras_msg)
		self.__authenticateSuccessfull(user_obj,ras_msg)
	    except:
		if user_obj!=None and user_obj.instances==0:
	    	    loaded_user.setOnlineFlag(False)
		raise
	finally:
	    self.loading_user.loadingEnd(loaded_user.getUserID())

    def persistentLanStop(self,ras_msg):
	loaded_user=user_main.getUserPool().getUserByID(ras_msg["user_id"])
	self.loading_user.loadingStart(loaded_user.getUserID())
	try:
	    user_obj=self.getUserObj(loaded_user.getUserID())
	    if user_obj==None:
		toLog("Got persistent lan stop for user %s, but he's not online"%ras_msg["user_id"],LOG_DEBUG)
	        return
	    instance=user_obj.getInstanceFromRasMsg(ras_msg)
	    if instance==None:
		toLog(errorText("USER","CANT_FIND_INSTANCE")%(loaded_user.getUserID(),ras_msg.getRasID(),ras_msg.getUniqueIDValue()))
		return

	    global_unique_id=user_obj.getGlobalUniqueID(user_obj.instances)
	    user_obj.logout(instance,ras_msg)
	    self.__logoutRecalcEvent(user_obj,global_unique_id)
	finally:
	    self.loading_user.loadingEnd(loaded_user.getUserID())
#########################################################
    def voipAuthenticate(self,ras_msg):
	loaded_user=user_main.getUserPool().getUserByVoIPUsername(ras_msg["voip_username"])
	self.loading_user.loadingStart(loaded_user.getUserID())
	try:
	    user_obj=None
	    try:
	        user_obj=self.getUserObj(loaded_user.getUserID())
		if user_obj==None:
		    user_obj=self.__loadUserObj(loaded_user,"VoIP")
		elif not user_obj.isVoIPUser():
		    raise GeneralException(errorText("USER_LOGIN","CANT_USE_MORE_THAN_ONE_SERVICE"))

	        user_obj.login(ras_msg)
		self.__authenticateSuccessfull(user_obj,ras_msg)

	    except:
		if user_obj!=None and user_obj.instances==0:
	    	    loaded_user.setOnlineFlag(False)
		raise
	finally:
	    self.loading_user.loadingEnd(loaded_user.getUserID())



    def voipStop(self,ras_msg):
	loaded_user=user_main.getUserPool().getUserByVoIPUsername(ras_msg["voip_username"])
	self.loading_user.loadingStart(loaded_user.getUserID())
	try:
	    user_obj=self.getUserObj(loaded_user.getUserID())
	    if user_obj==None:
		toLog("Got VoIP stop for user %s, but he's not online"%ras_msg["voip_username"],LOG_DEBUG)
	        return
	    instance=user_obj.getInstanceFromRasMsg(ras_msg)
	    if instance==None:
		toLog(errorText("USER","CANT_FIND_INSTANCE")%(loaded_user.getUserID(),ras_msg.getRasID(),ras_msg.getUniqueIDValue()),LOG_DEBUG)
		return

	    global_unique_id=user_obj.getGlobalUniqueID(user_obj.instances)
	    user_obj.logout(instance,ras_msg)
	    self.__logoutRecalcEvent(user_obj,global_unique_id)
	finally:
	    self.loading_user.loadingEnd(loaded_user.getUserID())
	
class OnlineCheckPeriodicEvent(periodic_events.PeriodicEvent):
    def __init__(self):
	periodic_events.PeriodicEvent.__init__(self,"Online Check",defs.CHECK_ONLINE_INTERVAL,[],0)

    def run(self):
	user_main.getOnline().checkOnlines()



	