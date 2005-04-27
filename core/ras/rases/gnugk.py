from core.ras.ras import UpdateUsersRas
from core.ras.voip_ras import VoIPRas
from core.ras import ras_main
from core import defs
from core.ibs_exceptions import *
from core.user import user_main
import os,time,copy

def init():
    ras_main.getFactory().register(GnuGKRas,"GnuGk")

class GnuGKRas(UpdateUsersRas,VoIPRas):
    type_attrs={"gnugk_multiple_login":0,"gnugk_acct_update_interval":60}

    def __init__(self,ras_ip,ras_id,ras_type,radius_secret,ports,ippools,attributes):
	UpdateUsersRas.__init__(self,ras_ip,ras_id,ras_type,radius_secret,ports,ippools,attributes,self.type_attrs)
	self.onlines={} #conf-id=>last_update_time

####################################
    def killUser(self,user_msg):
	pass
	
####################################
    def getOnlines(self):
	pass
####################################    
    def generalUpdate(self):
	pass
    
    def updateUserList(self):
	min_last_update=time.time()-self.getAttribute("gnugk_acct_update_interval")
	for h323_conf_id in self.onlines.keys():
	    if self.onlines[h323_conf_id]<min_last_update:
		del(self.onlines[h323_conf_id])
####################################
    def isOnline(self,user_msg):
	return self.onlines.has_key(user_msg["h323_conf_id"])

    def __updateOnlines(self,ras_msg):
        self.onlines[self.getH323AttrValue("H323-conf-id",ras_msg.getRequestPacket())]=time.time()
	

####################################
    def _handleRadAuthPacket(self,request,reply):
	if request.has_key("H323-conf-id"): #ARQ, Authorization Request
	    return UpdateUsersRas._handleRadAuthPacket(self,request,reply)
	    
	else: #RRQ, Authentication Request
	    return self.__rrqAuth(request,reply)
	    
###################################
    def __rrqAuth(self,request,reply):
	"""
	    do the RRQ Auth. We do it by just checking the username and password
	    other checkings will be done in authorization request.
	"""
	try:
	    loaded_user=user_main.getUserPool().getUserByVoIPUsername(request["User-Name"][0])
	except GeneralException:
	    return False

	if not request.checkChapPassword(loaded_user.getUserAttrs()["voip_password"]):
	    return False

	return True


###################################
    def __addUniqueIdToRasMsg(self,ras_msg):
	ras_msg["unique_id"] = "h323_conf_id"
	ras_msg["h323_conf_id"] = self.__getH323ConfID(ras_msg)

    def __getH323ConfID(self,ras_msg):
	return self.getH323AttrValue("H323-conf-id",ras_msg.getRequestPacket())

###################################
    def handleRadAuthPacket(self,ras_msg):
	self.__addUniqueIdToRasMsg(ras_msg)

	ras_msg.setInAttrs({"User-Name":"voip_username",
			    "CHAP-Password":"voip_chap_password",
			    "Framed-IP-Address":"caller_ip",
			    "Called-Station-Id":"called_number"})
			    
	ras_msg.setInAttrsIfExists({"Calling-Station-Id":"caller_id"})

	if not self.getAttribute("gnugk_multiple_login"):
	    ras_msg["multi_login"]=False
	    ras_msg["single_session_h323"]=True

	ras_msg.setAction("VOIP_AUTHENTICATE")

####################################
    def handleRadAcctPacket(self,ras_msg):
	status_type = ras_msg.getRequestAttr("Acct-Status-Type")[0]
	self.__addUniqueIdToRasMsg(ras_msg)

	if status_type=="Start":
	    ras_msg["called_ip"]=self.getH323AttrValue("H323-remote-address",ras_msg.getRequestPacket())
	    ras_msg["start_accounting"]=True
	    ras_msg["update_attrs"]=["start_accounting","called_ip"]
	    self.__updateOnlines(ras_msg)
	    ras_msg.setAction("VOIP_UPDATE")
	    
	elif status_type=="Stop":
	    ras_msg.setInAttrs({"User-Name":"voip_username",
				"Acct-Session-Time":"duration","Acct-Session-Id":"session_id"})
				
	    self.setH323TimeInAttrs(ras_msg,{"H323-disconnect-time":"disconnect_time"})
	    
	    if ras_msg.getRequestPacket().has_key("H323-connect-time"):
		self.setH323TimeInAttrs(ras_msg,{"H323-connect-time":"connect_time"})
	    else:
		ras_msg["connect_time"]=ras_msg["disconnect_time"]
	
	    ras_msg["disconnect_cause"]=self.getH323AttrValue("H323-disconnect-cause",ras_msg.getRequestPacket())
	    
	    ras_msg.setAction("VOIP_STOP")
	elif status_type=="Alive":
	    self.__updateOnlines(ras_msg)
	else:
	    self.toLog("handleRadAcctPacket: invalid status_type %s"%status_type,LOG_ERROR)
######################################
    def setSingleH323CreditTime(self,reply_pkt,credit_time):
	"""
	    set H323-credit-time in packet
	"""
	reply_pkt["H323-credit-time"]=str(int(credit_time))
		