$(function() {
  $("#jDash").jDashboard({ columns: 3 });
});


$(document).ready(function(){
  $('.carousel').carousel();
  interval: 2000
});


//datepicker for calendar
$(function() {
   $( "#date_report_minding, #date_report_period, #date_report_medicine, \
       #date_report_exam,    #date_report_photo,  #date_report_addcondition" ).datepicker();
});


$(function(){
  $('#add_medicine_disease_name, #add_exam_disease_name, #add_picture_disease_name').tagsInput({
      'defaultText':'請選擇一種您要記錄的症狀',
  });

})


$(function() {
  $( "#add_new_disease_name" ).autocomplete({
      source: "/search_disease/?"
  }); //autocomplete
});

$(function() {
  $( "#search_medicine1, #search_medicine2, #search_medicine3, #search_medicine4 \
      #search_medicine5, #search_medicine6, #search_medicine7, #search_medicine8 \
      #search_medicine9, #search_medicine10,#search_medicine11,#search_medicine12" ).autocomplete({
      source: "/search_medicine/?"
  }); //autocomplete
});

$(function() {
  $( "#search_side_effect" ).autocomplete({
      source: "/search_side_effect/?"
  }); //autocomplete
});        


$( "#search_medicine" )
  // don't navigate away from the field on tab when selecting an item
  .bind( "keydown", function( event ) {
    if ( event.keyCode === $.ui.keyCode.TAB &&
        $( this ).data( "autocomplete" ).menu.active ) {
      event.preventDefault();
    }
  })
  .autocomplete({
    source: function( request, response ) {
      $.getJSON( "/search_medicine/?", {
        term: extractLast( request.term )
      }, response );
    },
    search: function() {
      // custom minLength
      var term = extractLast( this.value );
      if ( term.length < 1 ) {
        return false;
      }
    },
    focus: function() {
      // prevent value inserted on focus
      return false;
    },
    select: function( event, ui ) {
      var terms = split( this.value );
      // remove the current input
      terms.pop();
      // add the selected item
      terms.push( ui.item.value );
      // add placeholder to get the comma-and-space at the end
      terms.push( "" );
      this.value = terms.join( ", " );
      return false;
    }
  }); //end autocomplete


$(function() {
  function split( val ) {
    return val.split( /,\s*/ );
  }
  function extractLast( term ) {
    return split( term ).pop();
  }

  $( "#search_side_effect" )
    // don't navigate away from the field on tab when selecting an item
    .bind( "keydown", function( event ) {
      if ( event.keyCode === $.ui.keyCode.TAB &&
          $( this ).data( "autocomplete" ).menu.active ) {
        event.preventDefault();
      }
    })

    .autocomplete({
      source: function( request, response ) {
        $.getJSON( "/search_side_effect/?", {
          term: extractLast( request.term )
        }, response );
      },
      search: function() {
        // custom minLength
        var term = extractLast( this.value );
        if ( term.length < 1 ) {
          return false;
        }
      },
      focus: function() {
        // prevent value inserted on focus
        return false;
      },
      select: function( event, ui ) {
        var terms = split( this.value );
        // remove the current input
        terms.pop();
        // add the selected item
        terms.push( ui.item.value );
        // add placeholder to get the comma-and-space at the end
        terms.push( "" );
        this.value = terms.join( ", " );
        return false;
      }
    }); //end autocomplete
});



$(document).ready(function(){
    $('.togglemenuleft').click(function(){
        $('#menu-left').toggleClass('span1');
        $('#menu-left').toggleClass('icons-only');
        $('#menu-left').toggleClass('span3');
        
        $('#content').toggleClass('span6');
        $('#content').toggleClass('span8');
        
        $(this).find('i').toggleClass('icon-circle-arrow-right');
        $(this).find('i').toggleClass('icon-circle-arrow-left');
        $('#menu-left').find('span').toggle();
        $('#menu-left').find('.dropdown').toggle();
    });

    $('#menu-left a').click(function(){
        $('#menu-left').find('a').removeClass('active');
        $(this).addClass('active');
    });
    // tool tip
    $('a').tooltip('hide');

    // switch style 
    $('a.style').click(function(){
        var style = $(this).attr('href');
        $('.links-css').attr('href','css/' + style);
        return false;
    });
   


    $(".switcher").click(function(){
        if($(this).find('i').hasClass('icon-circle-arrow-right'))
        $('.theme').animate({left:'0px'},500);
        else
        $('.theme').animate({left:'-89'},500);

        $(this).find('i').toggleClass('icon-circle-arrow-right');
        $(this).find('i').toggleClass('icon-circle-arrow-left');
    });

});