<?php
require_once("../../inc/init.php");
require_once(IBSINC."bw_face.php");
require_once(IBSINC."bw.php");

needAuthType(ADMIN_AUTH_TYPE);

$smarty=new IBSSmarty();
if(isInRequest("add","leaf_name","protocol","filter_type","filter_value","interface_name","limit_kbits"))
    intAddLeafService($smarty,
		      $_REQUEST["interface_name"],
		      $_REQUEST["leaf_name"],
		      $_REQUEST["protocol"],
		      $_REQUEST["filter_type"],
		      $_REQUEST["filter_value"],
		      $_REQUEST["limit_kbits"]);
else if (isInRequest("add","leaf_name","interface_name"))
    addLeafServiceInterface($smarty,$_REQUEST["interface_name"],$_REQUEST["leaf_name"]);
else
    redirectToInterfaceList("Invalid Input");

function intAddLeafService(&$smarty,$interface_name,$leaf_name,$protocol,$filter_type,$filter_value,$limit_kbits)
{
    $req=new AddLeafService($leaf_name,$protocol,$filter_type . " " . $filter_value,$limit_kbits);
    $resp=$req->sendAndRecv();
    if($resp->isSuccessful())
	redirectToInterfaceInfo($interface_name);
    else
	addLeafServiceInterface($smarty,$interface_name,$leaf_name,$resp->getError());
}


function addLeafServiceInterface(&$smarty,$interface_name,$leaf_name,$err=null)
{
    intAddAssignValues($smarty,$interface_name,$leaf_name);
    if(!is_null($err))
    {
	intSetErrors($smarty,$err->getErrorKeys());
	$smarty->set_page_error($err->getErrorMsgs());
    }
    $smarty->display("admin/bw/add_leaf_service.tpl");
}

function intAddAssignValues(&$smarty,$interface_name,$leaf_name)
{
    intAssignSelectValues($smarty);
    $smarty->assign("interface_name",$interface_name);
    $smarty->assign("leaf_name",$leaf_name);
    $smarty->assign("action","add");
    $smarty->assign("action_title","Add");
    $smarty->assign("action_icon","add");
}

function intAssignSelectValues(&$smarty)
{
    $smarty->assign("protocols",array("tcp","udp"));
    $smarty->assign("protocol_selected",requestVal("protocol",""));
    $smarty->assign("filter_types",array("sport"=>"Source Port(s)","dport"=>"Destination Port(s)"));
    $smarty->assign("filter_type_selected",requestVal("filter_types",""));
}

function intSetErrors(&$smarty,$err_keys)
{
    $smarty->set_field_errs(array("limit_kbits_err"=>array("INVALID_LIMIT_KBITS"),
				  "leaf_name_err"=>array("INVALID_LEAF_NAME"),
				  "filter_err"=>array("LEAF_HAS_THIS_FILTER","INVALID_FILTER"),
				  "protocol_err"=>array("LEAF_HAS_THIS_FILTER","INVALID_PROTOCOL")
			    ),$err_keys);
}

?>