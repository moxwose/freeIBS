{userViewTemplate edit_tpl_name="exp_date.tpl"}
  {userInfoTable title="User Expiration Date"} 
    {userInfoTD type="user_left"}
	Relative Expiration Date:
    {/userInfoTD}

    {userInfoTD type="user_right"}
	{ifHasAttr var_name="rel_exp_date" object="user"}
	    {$user_attrs.rel_exp_date} {$user_attrs.rel_exp_date_unit}
	{/ifHasAttr}
    {/userInfoTD}

    {userInfoTD type="group"}
	{ifHasAttr var_name="rel_exp_date" object="group"}
	    {$group_attrs.rel_exp_date} {$group_attrs.rel_exp_date_unit}
	{/ifHasAttr}
    {/userInfoTD}

  {/userInfoTable}
{/userViewTemplate}