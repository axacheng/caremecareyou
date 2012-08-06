/* Search function 
 * jqueryUI autocomplete cannot included in $(document).ready!
 */
$(function(){
	$('#search_input').autocomplete({
    minLength: 1,
		source: function(inputString, server_return){
        $.ajax({
          url: "/search/?",
          type: "GET",
          data: inputString,
          dataType:"html",
          success: function(server_return) {
              // If server is no result back to client then show error mesg.
              //alert(server_return.length)
              if (server_return.length <= 2){
                $('.show_result_ok').hide()
                $('.show_result_error').fadeIn().delay(1000).fadeOut()
                return false
              }
        
              // Show content of search_result.html to #result div
        	  $('#result').html(server_return)

        	  // Search input from user:
        	  search_input = $('input#search_input').val()
        	  
          }, //sucess end
        }) // $.ajax end
        
        
        	  


        // Clean up/Remove result after search is completed.
        // CANNOT REMOVE OUT!
        $('.show_line').empty().remove();
        $('.search_result').empty().remove();

  		}//source
  	}); //.autocomplete
  }); // search function end
