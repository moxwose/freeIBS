{* 
    Ras List
   $ras_infos: array of associative arrays containing active ras infos
   $inactive_ras_infos: array of associative arrays containing inactive ras infos

*}

{include file="admin_header.tpl" title="Ras List" selected="RAS"}
{include file="err_head.tpl"}

<center>
{if  $deactive_success}
    {headerMsg var_name="deactive_success"}Ras DeActivated Successfully.{/headerMsg}
{/if}

{if  $reactive_success}
    {headerMsg var_name="reactive_success"}Ras ReActivated Successfully.{/headerMsg}
{/if}
{listTable title="Active Rases" cols_num=4}
	{listTableHeaderIcon action="view"}
	{listTableHeaderIcon action="active" close_tr=TRUE}
	{listTR type="header"}
	    {listTD}
		ID
	    {/listTD}
	    {listTD}
		RAS IP
	    {/listTD}
	    {listTD}
		Type
	    {/listTD}
	    {listTD}
		Radius Secret
	    {/listTD}
	{/listTR}
	{foreach from=$ras_infos item=ras_info}
	{listTR type="body"}
	    {listTD}
		    {$ras_info.ras_id}
	    {/listTD}
	    {listTD}
		    {$ras_info.ras_ip}
	    {/listTD}
	    {listTD}
	    	    {$ras_info.ras_type}
	    {/listTD}
	    {listTD}
		    {$ras_info.radius_secret}
	    {/listTD}
	    {listTD icon="TRUE"}
		    <a href="/IBSng/admin/ras/ras_info.php?ras_ip={$ras_info.ras_ip|escape:"url"}">
			{listTableBodyIcon action="view" cycle_color=TRUE}
		    </a>
	    {/listTD}
	    {if $can_change}
	    {listTD icon="TRUE"}
			<a href="/IBSng/admin/ras/ras_list.php?deactive={$ras_info.ras_ip|escape:"url"}">
			    {listTableBodyIcon action="active" }
			</a> 
	    {/listTD}
	    {/if}
	{/listTR}
	{/foreach}

{/listTable}
<br>
{listTable title="Deactive Rases" cols_num=4}
	{listTableHeaderIcon action="view"}
	{listTableHeaderIcon action="deactive" close_tr=TRUE}
	{listTR type="header"}
	    {listTD}
		ID
	    {/listTD}
	    {listTD}
		RAS IP
	    {/listTD}
	    {listTD}
		Type
	    {/listTD}
	    {listTD}
		Radius Secret
	    {/listTD}
	{/listTR}
	{foreach from=$inactive_ras_infos item=ras_info}
	{listTR type="body"}
	    {listTD}
		    {$ras_info.ras_id}
	    {/listTD}
	    {listTD}
		    {$ras_info.ras_ip}
	    {/listTD}
	    {listTD}
	    	    {$ras_info.ras_type}
	    {/listTD}
	    {listTD}
		    {$ras_info.radius_secret}
	    {/listTD}
	    {listTD icon="TRUE"}
		    <a href="/IBSng/admin/ras/ras_info.php?ras_ip={$ras_info.ras_ip|escape:"url"}">
			{listTableBodyIcon action="view" cycle_color=TRUE}
		    </a>
	    {/listTD}
	    {if $can_change}
	    {listTD icon="TRUE"}
			<a href="/IBSng/admin/ras/ras_list.php?reactive={$ras_info.ras_ip|escape:"url"}">
			    {listTableBodyIcon action="deactive"}
			</a> 
	    {/listTD}
	    {/if}
	{/listTR}
	{/foreach}
{/listTable}
{addRelatedLink}
    <a href="/IBSng/admin/ras/add_new_ras.php" class="RightSide_links">
	Add New RAS
    </a>
{/addRelatedLink}

{include file="admin_footer.tpl"}