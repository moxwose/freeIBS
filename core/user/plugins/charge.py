from core.user import user_plugin,user_main,attribute
from core.charge import charge_main
from core.errors import *
from core.ibs_exceptions import *

def init():
    user_main.getUserPluginManager().register("charge",ChargeUserPlugin,6)
    
class ChargeUserPlugin(user_plugin.UserPlugin):
    def __init__(self,user_obj):
	user_plugin.UserPlugin.__init__(self,user_obj)
	self.charge_defined=True
	self.charge_initialized=False
	try:
	    if user_obj.isNormalUser():
	    	self.charge_id=int(user_obj.getUserAttrs()["normal_charge"])
	    
	except GeneralException:
	    self.charge_defined=False
	    
	if self.charge_defined:
	    self.charge_obj=charge_main.getLoader().getChargeByID(self.charge_id)

 
    def login(self,ras_msg):
	if not self.charge_defined:
	    raise GeneralException(errorText("USER_LOGIN","NO_CHARGE_DEFINED")%self.user_obj.getType())
	self.__initCharge()
	if ras_msg.hasAttr("start_accounting"):
	    self.__startAccounting(ras_msg)

	    
    def __initCharge(self):
	self.charge_obj.initUser(self.user_obj)
	self.charge_initialized=True
	
    def __startAccounting(self,ras_msg):
	self.charge_obj.startAccounting(self.user_obj,self.user_obj.getInstanceFromRasMsg(ras_msg))

    def update(self,ras_msg):
	if ras_msg.hasAttr("start_accounting"):
	    self.__startAccounting(ras_msg)
	    return True

    def logout(self,instance,ras_msg):
	if self.charge_initialized:
	    self.charge_obj.logout(self.user_obj,instance)

    def canStayOnline(self):
	if self.charge_initialized:
	    return self.charge_obj.checkLimits(self.user_obj)
	return self.createCanStayOnlineResult()

    def calcCreditUsage(self):
	if self.charge_initialized:
	    return self.charge_obj.calcCreditUsage(self.user_obj)
	return 0

    def calcInstanceCreditUsage(self,instance):
	if self.charge_initialized:
    	    return self.charge_obj.calcInstanceCreditUsage(self.user_obj,instance)
	return 0
