from core.ibs_exceptions import *
from core.errors import errorText
from core.ras import ras_main,ras
from core.lib import ip
from core.lib.general import *
from core.db import db_main,ibs_db
from core.charge import charge_main

class RasActions:

    def __getRasInfoDB(self,ras_ip):
	"""
	    return information of ras with ip "ras_ip" from db
	    return value is the same as ibs_db.get,it a list of dics
	    so it may be zero length or has a zero index, that the dic of info
	    [] or [{ras_info}]
	"""
	return db_main.getHandle().get("ras","ras_ip=%s"%dbText(ras_ip))

    def __rasIPExistsInDB(self,ras_ip):
	"""	
	    return True if ras with ip "ras_ip" exists in "ras" table.
	    it's useful for checking for inactive rases, as they aren't in memory
	"""
	return db_main.getHandle().getCount("ras","ras_ip=%s"%dbText(ras_ip))
#########################################
    def getInActiveRases(self):
	"""
	    return a list of inactive rases
	"""
	return db_main.getHandle().get("ras","active='f'",0,-1,"ras_ip")

#########################################
    def getRasPortInfo(self,ras_ip,port_names):
	"""
	    ras_ip(string): ip of ras
	    port_names(Multistr instance): port names, we'll 
	    return a dic of port info
	    {"port_name":port_name,"phone":phone_no,"type":type,"comment":comment}	    
	"""
	ras_obj=ras_main.getLoader().getRasByIP(ras_ip)
	if not ras_obj.hasPort(port_names[0]):
	    raise GeneralException(errorText("RAS","RAS_DONT_HAVE_PORT")%port_names[0])
	return ras_obj.getPorts()[port_names[0]]
	    

#########################################
    def addNewRas(self,ras_ip,ras_type,radius_secret):
	"""
	    ras_ip(string): ip of ras
	    ras_type(string): type of ras, this should perviously registered
	    radius_secret(string): 
	"""
	self.__addNewRasCheckInput(ras_ip,ras_type,radius_secret)
	ras_id=self.__getNewRasID()
	self.__addNewRasDB(ras_id,ras_ip,ras_type,radius_secret)
	ras_main.getLoader().loadRas(ras_id)
	return ras_id
	
    def __addNewRasCheckInput(self,ras_ip,ras_type,radius_secret):
	if not ip.checkIPAddrWithoutMask(ras_ip):
	    raise GeneralException(errorText("RAS","INVALID_RAS_IP")%ras_ip)

	if ras_main.getLoader().rasIPExists(ras_ip):
	    raise GeneralException(errorText("RAS","RAS_IP_ALREADY_EXISTS")%ras_ip)

	if self.__rasIPExistsInDB(ras_ip):
	    raise GeneralException(errorText("RAS","RAS_IS_INACTIVE")%ras_ip)


	if not ras_main.getFactory().hasType(ras_type):
	    raise GeneralException(errorText("RAS","RAS_TYPE_NOT_REGISTERED")%ras_type)


    def __getNewRasID(self):
	"""
	    return a new unique ras id
	"""
	return db_main.getHandle().seqNextVal("ras_id_seq")

    def __addNewRasDB(self,ras_id,ras_ip,ras_type,radius_secret):
	db_main.getHandle().transactionQuery(self.__addNewRasQuery(ras_id,ras_ip,ras_type,radius_secret))

    def __addNewRasQuery(self,ras_id,ras_ip,ras_type,radius_secret):
	"""
	    return query for adding new ras
	"""
	return ibs_db.createInsertQuery("ras",{"ras_id":ras_id,
					       "ras_ip":dbText(ras_ip),
					       "ras_type":dbText(ras_type),
					       "radius_secret":dbText(radius_secret)
					      })
#######################################
    def updateRas(self,ras_id,ras_ip,ras_type,radius_secret):
	"""
	    update ras info, notice that ras_ip is changable
	    ras_id(integer): ras_id that we want to change properties
	    ras_ip(string): ras_ip
	    ras_type(string): type of ras
	    radius_secret(string): 
	"""
	self.__updateRasCheckInput(ras_id,ras_ip,ras_type,radius_secret)
	self.__updateRasDB(ras_id,ras_ip,ras_type,radius_secret)
	ras_main.getLoader().unloadRas(ras_id)
	ras_main.getLoader().loadRas(ras_id)
	
    def __updateRasCheckInput(self,ras_id,ras_ip,ras_type,radius_secret):
	ras_obj=ras_main.getLoader()[ras_id]
	if ras_obj.getRasIP()!=ras_ip:
	    if not ip.checkIPAddrWithoutMask(ras_ip):
		raise GeneralException(errorText("RAS","INVALID_RAS_IP")%ras_ip)

	    if ras_main.getLoader().rasIPExists(ras_ip):
		raise GeneralException(errorText("RAS","RAS_IP_ALREADY_EXISTS"%ras_ip))

	    if self.__rasIPExistsInDB(ras_ip):
		raise GeneralException(errorText("RAS","RAS_IS_INACTIVE")%ras_ip)
	    
	if not ras_main.getFactory().hasType(ras_type):
	    raise GeneralException(errorText("RAS","RAS_TYPE_NOT_REGISTERED")%ras_type)

    def __updateRasDB(self,ras_id,ras_ip,ras_type,radius_secret):
	db_main.getHandle().transactionQuery(self.__updateRasQuery(ras_id,ras_ip,ras_type,radius_secret))

    def __updateRasQuery(self,ras_id,ras_ip,ras_type,radius_secret):
	"""
	    return query for updating ras with id "ras_id"
	"""
	return ibs_db.createUpdateQuery("ras",{"ras_ip":dbText(ras_ip),
					       "ras_type":dbText(ras_type),
					       "radius_secret":dbText(radius_secret)
					      },"ras_id=%s"%ras_id)
###########################################################
    def deActiveRas(self,ras_ip):
	"""
	    DeActive ras, by setting it's active flag to false
	    Inactive rases, won't load into memory, they are just keep there because other table
	    reference to em
	"""
	self.__deActiveRasCheckInput(ras_ip)
	ras_obj=ras_main.getLoader().getRasByIP(ras_ip)
	self.__checkRasInCharges(ras_obj)
	self.__deActiveRasDB(ras_obj)
	ras_main.getLoader().unloadRas(ras_obj.getRasID())

    def __deActiveRasCheckInput(self,ras_ip):
	ras_main.getLoader().checkRasIP(ras_ip)

    def __checkRasInCharges(self,ras_obj):
	"""
	    check if this ras, is used in any charge rule, if so tell the user to go and
	    delete the rule before deleting this ras
	"""
	def checkRasUsageInRules(charge_obj):
	    rulez=charge_obj.getRules()
	    for rule_obj in rulez.values():
		if rule_obj.getRasID()==ras_obj.getRasID():
		    raise GeneralException(errorText("RAS","RAS_USED_IN_RULE")%rule_obj)
	charge_main.getLoader().runOnAllCharges(checkRasUsageInRules)

    def __deActiveRasDB(self,ras_obj):
	db_main.getHandle().transactionQuery(self.__deActiveRasQuery(ras_obj.getRasID()))

    def __deActiveRasQuery(self,ras_id):
	return ibs_db.createUpdateQuery("ras",{"active":dbText("f")},"ras_id=%s"%ras_id)

###########################################################
    def reActiveRas(self,ras_ip):
	"""
	    ReActive ras, by setting it's active flag to true
	"""
	ras_info=self.__reActiveRasCheckInput(ras_ip)
	self.__reActiveRasDB(ras_info)
	ras_main.getLoader().loadRas(ras_info["ras_id"])

    def __reActiveRasCheckInput(self,ras_ip):
	ras_info=self.__getRasInfoDB(ras_ip)
	if not len(ras_info):
	    raise GeneralException(errorText("RAS","NO_SUCH_INACTIVE_RAS")%ras_ip)
	return ras_info[0]

    def __reActiveRasDB(self,ras_info):
	db_main.getHandle().transactionQuery(self.__reActiveRasQuery(ras_info["ras_id"]))

    def __reActiveRasQuery(self,ras_id):
	return ibs_db.createUpdateQuery("ras",{"active":dbText("t")},"ras_id=%s"%ras_id)
#######################################
    def addPort(self,ras_ip,ports,_type,phones,comments):
	self.__addPortCheckInput(ras_ip,ports,phones,_type,comments)
	ras_obj=ras_main.getLoader().getRasByIP(ras_ip)	
	self.__addPortDB(ras_obj,ports,phones,_type,comments)
	ras_main.getLoader().loadRas(ras_obj.getRasID())

    def __addPortCheckInput(self,ras_ip,port_names,phones,_type,comments):
	ras_obj=ras_main.getLoader().getRasByIP(ras_ip)	

    	def checkPort(port_name):
	    if not len(port_name):
		raise GeneralException(errorText("RAS","INVALID_PORT_NAME")%port_name)

	    if ras_obj.hasPort(port_name):
		raise GeneralException(errorText("RAS","RAS_ALREADY_HAS_PORT")%port_name)

	map(checkPort,port_names)
	
	if _type not in ras.PORT_TYPES:
	    raise GeneralException(errorText("RAS","INVALID_PORT_TYPE")%_type)

    def __addPortDB(self,ras_obj,port_names,phones,_type,comments):
	query=""
	for _index in range(len(port_names)):
	    query+=self.__addPortQuery(ras_obj.getRasID(),port_names[_index],phones[_index],_type,comments[_index])
	db_main.getHandle().transactionQuery(query)

    def __addPortQuery(self,ras_id,port_name,phone,_type,comment):
	return ibs_db.createInsertQuery("ras_ports",{"ras_id":ras_id,
						     "port_name":dbText(port_name),
						     "phone":dbText(phone),
						     "type":dbText(_type),
						     "comment":dbText(comment)
						     })

##########################################
    def delPort(self,ras_ip,port_names):
	self.__delPortCheckInput(ras_ip,port_names)
	ras_obj=ras_main.getLoader().getRasByIP(ras_ip)	
	self.__delPortsDB(ras_obj,port_names)
	ras_main.getLoader().loadRas(ras_obj.getRasID())

	
    def __delPortCheckInput(self,ras_ip,port_names):
	ras_obj=ras_main.getLoader().getRasByIP(ras_ip)	
    	def checkPort(port_name):
	    if not ras_obj.hasPort(port_name):
		raise GeneralException(errorText("RAS","RAS_DONT_HAVE_PORT")%port_name)
	    
	map(checkPort,port_names)
    
    def __delPortsDB(self,ras_obj,port_names):
	query=""
	for port_name in port_names:
	    query+=self.__delPortQuery(ras_obj.getRasID(),port_name)
	db_main.getHandle().transactionQuery(query)

    def __delPortQuery(self,ras_id,port_name):
	return ibs_db.createDeleteQuery("ras_ports","ras_id=%s and port_name=%s"%(ras_id,dbText(port_name)))
###########################################
    def updatePort(self,ras_ip,port_names,phones,_type,comments):
	self.__updatePortCheckInput(ras_ip,port_names,phones,_type,comments)
	ras_obj=ras_main.getLoader().getRasByIP(ras_ip)	
	self.__updatePortDB(ras_obj,port_names,phones,_type,comments)
	ras_main.getLoader().loadRas(ras_obj.getRasID())

    def __updatePortCheckInput(self,ras_ip,port_names,phones,_type,comments):
	ras_obj=ras_main.getLoader().getRasByIP(ras_ip)	
    	def checkPort(port_name):
	    if not ras_obj.hasPort(port_name):
		raise GeneralException(errorText("RAS","RAS_DONT_HAVE_PORT")%port_name)

	    if not len(port_name):
		raise GeneralException(errorText("RAS","INVALID_PORT_NAME")%port_name)


	map(checkPort,port_names)
	if _type not in ras.PORT_TYPES:
	    raise GeneralException(errorText("RAS","INVALID_PORT_TYPE")%_type)
	
    def __updatePortDB(self,ras_obj,port_names,phones,_type,comments):
	query=""
	for _index in range(len(port_names)):
	    query+=self.__updatePortQuery(ras_obj.getRasID(),port_names[_index],phones[_index],_type,comments[_index])
	db_main.getHandle().transactionQuery(query)

    def __updatePortQuery(self,ras_id,port_name,phone,_type,comment):
	return ibs_db.createUpdateQuery("ras_ports",{"port_name":dbText(port_name),
						     "phone":dbText(phone),
						     "type":dbText(_type),
						     "comment":dbText(comment)
						    },"ras_id=%s and port_name=%s"%(ras_id,dbText(port_name)))
#############################################
    def updateAttribute(self,ras_ip,attrs):
	self.__updateAttributeCheckInput(ras_ip,attrs)
	ras_obj=ras_main.getLoader().getRasByIP(ras_ip)	
	self.__updateAttributeDB(ras_obj,attrs)
	ras_main.getLoader().loadRas(ras_obj.getRasID())

    def __updateAttributeCheckInput(self,ras_ip,attrs):
	ras_obj=ras_main.getLoader().getRasByIP(ras_ip)
	all_attrs=ras_obj.getAllAttributes()
	for attr_name in attrs:
	    if attr_name not in all_attrs :
		raise GeneralException(errorText("RAS","RAS_DONT_HAVE_ATTR")%attr_name)

	    if type(all_attrs[attr_name]) == types.IntType:
		attrs[attr_name]=to_int(attrs[attr_name],"%s Attribute Value"%attr_name)

    def __updateAttributeDB(self,ras_obj,attrs):
	all_attrs=ras_obj.getAllAttributes()
	query=""
	for attr_name in attrs:
	    if attrs[attr_name]!=all_attrs[attr_name]:
		if ras_obj.hasAttribute(attr_name):
		    query+=self.__updateAttributeQuery(ras_obj.getRasID(),attr_name,attrs[attr_name])
		else:
		    query+=self.__addAttributeQuery(ras_obj.getRasID(),attr_name,attrs[attr_name])
	
	db_main.getHandle().transactionQuery(query)

    def __updateAttributeQuery(self,ras_id,attr_name,attr_value):
	return ibs_db.createUpdateQuery("ras_attrs",{"attr_value":dbText(attr_value)},
						     "ras_id=%s and attr_name=%s"%(ras_id,dbText(attr_name)))

    def __addAttributeQuery(self,ras_id,attr_name,attr_value):
	return ibs_db.createInsertQuery("ras_attrs",{"ras_id":ras_id,
						     "attr_name":dbText(attr_name),
						     "attr_value":dbText(attr_value)
						     })

##############################################
    def delAttributes(self,ras_ip):
	"""
	    delete all attributes of ras with ip "ras_ip"
	    this is reset to default, as it means ras doesn't have any specific attribute
	"""
	self.__delAttributesCheckInput(ras_ip)
	ras_obj=ras_main.getLoader().getRasByIP(ras_ip)
	self.__delAttributesDB(ras_obj)
	ras_main.getLoader().loadRas(ras_obj.getRasID())    

    def __delAttributesCheckInput(self,ras_ip):
	ras_obj=ras_main.getLoader().getRasByIP(ras_ip)

    def __delAttributesDB(self,ras_obj):
	db_main.getHandle().transactionQuery(self.__delAttributesQuery(ras_obj.getRasID()))	

    def __delAttributesQuery(self,ras_id):
	return ibs_db.createDeleteQuery("ras_attrs","ras_id=%s"%ras_id)
##############################################

####################################### UNUSED CODE
    def deleteRas(self,ras_ip):
	"""
	    UNUSED
	    
	    it's supposed to delete a ras, but we don't need it because we should active/deactive it
	    this is only useful if we check other tables, and if they don't have any reference, we let it 
	    delete
	"""
	self.__deleteRasCheckInput(ras_ip)
	ras_obj=ras_main.getLoader().getRasByIP(ras_ip)
	self.__checkRasInCharges(ras_obj)
	self.__deleteRasLogicallyDB(ras_obj)
	ras_main.getLoader().unloadRas(ras_obj.getRasID())


    def __deleteRasCheckInput(self,ras_ip):
	ras_main.getLoader().checkRasIP(ras_ip)
    
    def __deleteRasDB(self,ras_obj):
	query=self.__deleteRasAttrsQuery(ras_obj.getRasID())
	query+=self.__deleteRasPortsQuery(ras_obj.getRasID())
	query+=self.__deleteRasLogicallyQuery(ras_obj.getRasID())
	
    def __deleteRasAttrsQuery(self,ras_id):
	return ibs_db.createDeleteQuery("ras_attrs","ras_id=%s"%ras_id)

    def __deleteRasPortsQuery(self,ras_id):
	return ibs_db.createDeleteQuery("ras_ports","ras_id=%s"%ras_id)
	
    def __deleteRasQuery(self,ras_id):
	return ibs_db.createDeleteQuery("ras","ras_id=%s"%ras_id)	

