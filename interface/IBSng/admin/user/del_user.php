<?php
require_once("del_user_funcs.php");

needAuthType(ADMIN_AUTH_TYPE);
$smarty=new IBSSmarty();

if(isInRequest("user_id","delete","delete_comment"))
    intDeleteUser($smarty,$_REQUEST["user_id"],$_REQUEST["delete_comment"],isInRequest("delete_connection_logs"));
else if (isInRequest("user_id"))
    intShowDeleteUserFace($smarty,$_REQUEST["user_id"]);
else
    redirectToUserSearch("");

?>