<?php

function smarty_block_ifHasAttr($params,$content,&$smarty,&$repeat)
{
/*
    return some dashes "---" if attribute doesn't exists in attributes array.
    attributes array are selected based on "object" parameter is one of "group_attrs" or "user_attrs"    

    parameter object(string,required): can be "user" or "group"
    parameter var_name(string,required): variable name that will be checked that if exists
					 and set !== FALSE , we suppose we have the attribute 

*/
    if(is_null($content))
    {
	if(hasAttr($params,$smarty))
	    $repeat=TRUE;
	else
	{
	    $repeat=FALSE;
	    print "<center>---------------";    
	}
    }
    else
	return $content;
    
}

function hasAttr(&$params,&$smarty)
{
	$attrs=getAttrsArray($params,$smarty);
	return (isset($attrs[$params["var_name"]]) and $attrs[$params["var_name"]]!==FALSE);
}

function getAttrsArray(&$params,&$smarty)
{
    if($params["object"]=="user")
        return $smarty->get_assigned_value("user_attrs");
    else if ($params["object"]=="group")
        return $smarty->get_assigned_value("group_attrs");
}
?>