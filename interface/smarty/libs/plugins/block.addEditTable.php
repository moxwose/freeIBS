<?php

function smarty_block_addEditTable($params,$content,&$smarty,&$repeat)
{
/*
    create header and footer of an Add Edit Style table
    parameter title(string,optional): Title of table that will be printed on top of table
    parameter table_width(string,optional): width of table, if not set, defaults are used
    parameter double(boolean,optional): Set Double table, double tables has two usable areas in 
			each row. Also Double TR s should be used for content
    parameter action_icon(boolean,optional): Tells which icon to use for form submit
					     Can be on of "edit" "delete" "add" or "ok"
					     default is "ok"

    parameter color(string,optional): Set color of table header, default is red

*/
    if(!is_null($content))
    {
	$title=isset($params["title"])?$params["title"]:"";
	if(isset($params["double"]) and $params["double"]=="TRUE")
	{
	    $table_width_default=480;
	    $colspans=9;
	}
	else
	{
	    $table_width_default=280;
	    $colspans=4;
	}

	if(isset($params["color"]))
	    $color=$params["color"];
	else
	    $color="red";

	$action_icon="ok";
	if(isset($params["action_icon"]) and in_array($params["action_icon"],array("edit","delete","add","ok")))
	    $action_icon=$params["action_icon"];

	$table_width=isset($params["table_width"])?$params["table_width"]:$table_width_default;

	$header=<<<END

<table class="Form_Main" width="{$table_width}" border="0" cellspacing="0" bordercolor="#000000" cellpadding="0">
	<tr>
		<td colspan="{$colspans}">
		<!-- Form Title Table -->
		<table border="0" cellspacing="0" cellpadding="0" class="Form_Title">
			<tr>
				<td class="Form_Title_Begin"><img border="0" src="/IBSng/images/begin_form_title_{$color}.gif"></td>
				<td class="Form_Title_{$color}">	{$title} <img border="0" src="/IBSng/images/arrow_orange.gif"></td>
				<td class="Form_Title_End"><img border="0" src="/IBSng/images/end_form_title_{$color}.gif"></td>
			</tr>
			</table>
		<!-- End Form Title Table  -->
		</td>
	</tr>
	<tr>
		<td colspan="{$colspans}" class="Form_Content_Row_Space"></td>
	</tr>

END;
	$footer=<<<END
	
	<tr>
		<td colspan="{$colspans}">
			<table border="0" cellspacing="0" cellpadding="0" class="Form_Foot">
				<tr>
					<td class="Form_Foot_Begin_Line_{$color}"></td>
					<td rowspan="2" class="Form_Foot_End"><img border="0" src="/IBSng/images/end_of_line_bottom_of_table.gif"></td>
					<td rowspan="2" class="Form_Foot_Buttons"><input type=image src="/IBSng/images/{$action_icon}.gif"></td>
				</tr>
				<tr>
					<td class="Form_Foot_Below_Line_{$color}"></td>
				</tr>
			</table>
			<!-- End Form Foot Table -->
		</td>
	</tr>
</table>
<br>
END;
    return $header.$content.$footer;    
    }
    
}
?>