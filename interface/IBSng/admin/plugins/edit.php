<?php
require_once("../../inc/init.php");
require_once("edit_funcs.php");

needAuthType(ADMIN_AUTH_TYPE);

$smarty=new IBSSmarty();

if(isInRequest("update","edit_tpl_cs","target","target_id"))
    intUpdateAttrs($smarty,$_REQUEST["target"],$_REQUEST["target_id"]);
else if(isInRequest("group_name","edit_group"))
    intEditGroup($smarty,$_REQUEST["group_name"]);
else if(isInRequest("user_id","edit_user"))
    intEditUser($smarty,$_REQUEST["user_id"]);
else
{
    $err=new error("INVALID_INPUT");
    redirectToGroupList($err->getErrorMsg());
}


?>