function altRows(id){
	if(document.getElementsByTagName){  
		
		var table = document.getElementById(id);  
		var rows = table.getElementsByTagName("tr"); 
		 
		for(i = 0; i < rows.length; i++){          
			if(i % 2 == 0){
				rows[i].className = "evenrowcolor";
			}else{
				rows[i].className = "oddrowcolor";
			}      
		}
	}
}
window.onload=function(){
	altRows('alternatecolor');
}
function Blank_TextField_Validator()
{
// Check the value of the element named reason from the form named edit_form
if (edit_form.reason.value == "")
{
  // If null display and alert box
   alert("Please fill in the text field.");
  // Place the cursor on the field for revision
   edit_form.reason.focus();
  // return false to stop further processing
   return (false);
}
// If reason is not null continue processing
return (true);
}


