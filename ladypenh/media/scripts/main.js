var daySlide;
var detailsSlide;
var detailsVisible = true;
var selectedEvent = "";
var selectedDay = "";
var tmpContentDetails = "";
var openday = "";
var openevent = "";

function winpop(url){
    var left = (screen.width/2)-185;
    var top = (screen.height/2)-185;
    var pop = window.open(url , 'details', 'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=yes, resizable=yes, copyhistory=no, width=400, height=300, top='+top+', left='+left);
    pop.focus();
}


function slidedetails(tog, content){
    if (selectedEvent != "")
        $(selectedEvent).removeClass('selected');    
    if (tog != "")
        $(tog).addClass('selected');
    selectedEvent = tog;
    detailsVisible = false;
    detailsSlide.slideOut();
    tmpContentDetails = content;
    detailsSlide.addEvent('complete', function(e) {
            if (detailsVisible) return;
            $("detailsslider").innerHTML = $(tmpContentDetails).innerHTML;
            detailsVisible = true;
            detailsSlide.slideIn();
        });
}

function slideday(day, openalso){
    if (day == selectedDay){
        slidedetails('', 'ol'+day);
        return;
    }
    if (selectedDay != ""){
        $('tog'+selectedDay).removeClass('selected');
        daysliders[selectedDay].slideOut();
    }
    $('tog'+day).addClass('selected');
    selectedDay = day;
    daysliders[day].slideIn();
    if (openalso)
        slidedetails('', 'ol'+day);
}

function openandselect(day, event){
    var toggler = 'tog'+day;
    var eventDiv = 'ev'+event;
    if (!$(toggler) || !$(eventDiv)){
        return;
    }
    slideday(day, false);
    slidedetails(eventDiv, 'details-'+event);
}


function getParameter ( queryString, parameterName ) {
   var parameterName = parameterName + "=";
   if ( queryString.length > 0 ) {
      begin = queryString.indexOf ( parameterName );
      if ( begin != -1 ) {
         begin += parameterName.length;
         end = queryString.indexOf ( "&" , begin );
      if ( end == -1 ) {
         end = queryString.length
      }
      return unescape ( queryString.substring ( begin, end ) );
   }
   return "null";
   }
}


window.addEvent('domready', function() {
        if (!$('detailsslider')) return;
        detailsSlide = new Fx.Slide('detailsslider');
        var queryString = window.top.location.search.substring(1);
        openday = getParameter(queryString, "openday");
        openevent = getParameter(queryString, "openevent");
        if (openday == null || openday.length != 10)            
            slideday(defaultday, true);
        else
            openandselect(openday, openevent);
    });
