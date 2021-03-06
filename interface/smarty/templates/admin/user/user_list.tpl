<script language="javascript">
    var user_ids=new CheckBoxContainer();
</script>

{listTable no_header=TRUE} 
    {listTableHeader cols_num=30 type="left"}
	List of Users
    {/listTableHeader}
    {listTableHeader type="right"}
	Total Results:  <font color="#9a1111">{$result_count}</font> 
    {/listTableHeader}
    {listTR type="header" }
    {if $can_change}
	{listTD}
	    <input type=checkbox name="check_all_users"> 
	    <script language="javascript">
		user_ids.setCheckAll("search_user","check_all_users");
	    </script>
	{/listTD}
    {/if}	

	{listTD}
	    User ID
	{/listTD}
    {if isInRequest("show__normal_username")}
	{listTD}
	    Normal Username
	{/listTD}
    {/if}

    {if isInRequest("show__voip_username")}
	{listTD}
	    VoIP Username
	{/listTD}
    {/if}
    
    {if isInRequest("show__credit")}
	{listTD}
	    Credit
	{/listTD}
    {/if}

    {if isInRequest("show__group")}
	{listTD}
	    Group
	{/listTD}
    {/if}

    {if isInRequest("show__owner")}
	{listTD}
	    Owner
	{/listTD}
    {/if}

    {if isInRequest("show__creation_date")}
	{listTD}
	    Creation Date
	{/listTD}
    {/if}

    {if isInRequest("show__rel_exp_date")}
	{listTD}
	    Rel Exp Date
	{/listTD}
    {/if}

    {if isInRequest("show__abs_exp_date")}
	{listTD}
	    Abs Exp Date
	{/listTD}
    {/if}

    {if isInRequest("show__multi_login")}
	{listTD}
	    Multi Login
	{/listTD}
    {/if}

    {if isInRequest("show__normal_charge")}
	{listTD}
	    Normal Charge
	{/listTD}
    {/if}

    {if isInRequest("show__voip_charge")}
	{listTD}
	    Normal Charge
	{/listTD}
    {/if}

    {if isInRequest("show__lock")}
	{listTD}
	    Locked
	{/listTD}
    {/if}

    {/listTR}

    {foreach from=$user_ids item=user_id}
	{assign var="user_info" value=`$user_infos.$user_id`}
	{listTR type="body" cycle_color=TRUE hover_location="/IBSng/admin/user/user_info.php?user_id=`$user_id`"}
	    {if $can_change}
		{listTD extra="onClick='event.cancelBubble=true;'"}
	    	    <input type=checkbox name="edit_user_id_{$user_id}" value="{$user_id}"> 
		    <script language="javascript">
			user_ids.addByName("search_user","edit_user_id_{$user_id}");
		    </script>
	        {/listTD}	
	    {/if}
	    {listTD}
		{$user_id}
	    {/listTD}	
	
	    {if isInRequest("show__normal_username")}
	    	{searchUserTD attr_name="normal_username" user_id=$user_id attr_type="attrs"}{/searchUserTD}
	    {/if}

	    {if isInRequest("show__voip_username")}
	    	{searchUserTD attr_name="voip_username" user_id=$user_id attr_type="attrs"}{/searchUserTD}
	    {/if}
    
	    {if isInRequest("show__credit")}
		{searchUserTD attr_name="credit" user_id=$user_id attr_type="basic"}{$search_value|price}{/searchUserTD}
	    {/if}

	    {if isInRequest("show__group")}
		{searchUserTD attr_name="group_name" user_id=$user_id attr_type="basic"}{/searchUserTD}
	    {/if}

	    {if isInRequest("show__owner")}
		{searchUserTD attr_name="owner_name" user_id=$user_id attr_type="basic"}{/searchUserTD}
	    {/if}

	    {if isInRequest("show__creation_date")}
		{searchUserTD attr_name="creation_date" user_id=$user_id attr_type="basic"}{/searchUserTD}
	    {/if}

	    {if isInRequest("show__rel_exp_date")}
	    	{searchUserTD attr_name="rel_exp_date,rel_exp_date_unit" user_id=$user_id attr_type="attrs"}{/searchUserTD}
	    {/if}

	    {if isInRequest("show__abs_exp_date")}
	    	{searchUserTD attr_name="abs_exp_date" user_id=$user_id attr_type="attrs"}{/searchUserTD}
	    {/if}

	    {if isInRequest("show__multi_login")}
	    	{searchUserTD attr_name="multi_login" user_id=$user_id attr_type="attrs"}{/searchUserTD}
	    {/if}

	    {if isInRequest("show__normal_charge")}
	    	{searchUserTD attr_name="normal_charge" user_id=$user_id attr_type="attrs"}{/searchUserTD}
	    {/if}

	    {if isInRequest("show__voip_charge")}
	    	{searchUserTD attr_name="voip_charge" user_id=$user_id attr_type="attrs"}{/searchUserTD}
	    {/if}

	    {if isInRequest("show__lock")}
	    	{searchUserTD attr_name="lock" user_id=$user_id attr_type="attrs"}Yes{/searchUserTD}
	    {/if}
	    
	{/listTR}	
    {/foreach}
{/listTable}
