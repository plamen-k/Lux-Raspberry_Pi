var piAuto = "samuel";  //  Holds the auto/manual state
var calibrationComplete;  //  Used for the windmill animation
var selectedThreshold = -1111;  // remembers the state of the selection menu and sets it to it
var refreshRate = 5 
 $(document).ready(function () {

  $("#question").click(function(){
    $("#help-page").slideToggle(900);

  });
  $("#help-page").click(function(){$(this).slideToggle(900)});



  // ============== Advanced settings value checking ===============

  $("#swipe").click(function(){$("#advanced_settings").slideToggle("slow")});
  $("#close_button").click(function(){
    if((!isNaN($( "#refresh_input" ).val())) && (!isNaN($( "#threshold_input" ).val()))){
      $("#refresh_input").css("border","none");
      $("#threshold_input").css("border","none");

      $("#advanced_settings").slideToggle("slow");$("#calibrateButton").toggle("slow");
      $('#threshold_form').submit();
      
    }

    else{
      $("#refresh_input").css("border","1px solid red");
      $("#threshold_input").css("border","1px solid red");
      var answer = confirm('Exit advanced settings?');
        if (answer)
        {
          $("#advanced_settings").slideToggle("slow");$("#calibrateButton").toggle("slow");
        }
    }

    // ============== Advanced settings value checking ===============

  });




  var date = new Date();
  var changeDate = date.getHours();
  console.log(changeDate);
  if(changeDate<7 || changeDate>20){
    $("#sun").attr("id","moon");
  }

  logoSpin();
 });
webiopi().ready(function () {    // execute when the server/client script has loaded
   
  // =========================== Initiations  ====================================



  $("#swipe").click(function () { // when you click the arrow, shows the calibrate button
    $("#calibrateButton").toggle("slow");

  });

  $("#poss button:nth-child(1)").click(function(){
    setLightType(2);
  });

   $("#poss button:nth-child(2)").click(function(){
    setLightType(120);
  });

  $("#switch").click(function(){slider()});
  formThreshold();
  formRefresh();
  getThreshold();     //  assigns selectedThreshold to the server's light sensitivity
  getLuminosity();    //  This macro continiously asks the server for the brigtness inside and displays it
  setServerState();   //  Very important, asks the server if controls are manual/auto and sets them for the client
  calibrateButton();  //  Creates the button that will trigger the calibration + animation
  lightTypeToggle();  //  toggles the led button controls
  getRefresh();

  var checkedState = 0;
  $("#change_threshold input[name='thresholdSetter']").change(function(){
     //setThreshold($("#change_threshold").val()); //  The parameter is the "brightness", jquery returns the selected predefined value
     
     checkedState = $(this).val();
     console.log(checkedState + "checkedState");
     console.log(parseInt($("#change_threshold").val()) + " value of radio button");
     console.log(selectedThreshold + " function response");
     setThreshold(checkedState);

  });


  $("#calibrateButton").click(function () {          // When clicked, the button shows the "loading calibration" screen
      // var answer = confirm('Are you sure you want to calibrate?');
      //   if (answer)
      //   {
      //         $("#windmill").slideToggle("slow", function () {  
      //           calibrating();                                // trigers the turbine spin and forces the server to calibrate the lights
      //         });
      //   } else {
      //     console.log("calibration rejected");
      //   }
        $("#windmill").slideToggle("slow", function () {  
                 calibrating();
      // trigers the turbine spin and forces the server to calibrate the lights
        });
  });

  //  ==================  WEBIOPI SETUP   =====================
  //       (Comunication between the server and the client)

  var manualMode = webiopi().createButton("deselected_button", "MANUAL", function () {  // Creates the button for manual mode   
    webiopi().callMacro("dAutomaticControl");        
  });

  var autoMode = webiopi().createButton("deselected_button", "AUTO", function () {        // Creates the button for auto mode                            
    webiopi().callMacro("eAutomaticControl");        
  });
  
  $("#switch").append(manualMode);    // Adds the lightbulbs to the controls  
  $("#switch").append(autoMode);       
  var button0 = webiopi().createGPIOButton(04, "");
  var button1 = webiopi().createGPIOButton(17, "");
  var button2 = webiopi().createGPIOButton(18, "");
  var button3 = webiopi().createGPIOButton(22, "");     
  $("#light_container").append(button0);
  $("#light_container").append(button1);
  $("#light_container").append(button2);
  $("#light_container").append(button3);


  $("#light_container button").click(function(){
    $(this).fadeIn();
    console.log("executed click");
  });

  // Refresh GPIO buttons
  $('link[rel=stylesheet][href~="/webiopi.css"]').remove();                
  // pass true to refresh repeatedly of false to refresh once
  webiopi().refreshGPIO(true);   


   
  // =========================  Custom methods for talking to the pi


function setThreshold(value) { //   Call with a parameter to change the sensitivity [lux]
  var setThresholdVar = function (macro, args, response) {}   // 
  var getBrightness = webiopi().callMacro("changeThreshold", parseInt(value), setThresholdVar);
}

function getRefresh() {
   webiopi().callMacro("returnRefresh", [], macroCallback);
}

function macroCallback(macro, arg, data) {
  refreshRate = data;

      // ================ Progressbar ==============//

  $("#switch button").click(function(){
    $("#progressbar").css("width",0);
    $("#progress-container").fadeIn(1500);
    $("#progressbar").animate({"width": (99)+"%"},refreshRate*1000, function(){
      $("#progress-container").fadeOut(1500);
      
    });
    setInterval(setServerState, refreshRate*1000);
    setInterval(getThreshold, refreshRate*1000);
    console.log(refreshRate);

  });

  // ================/Progressbar ==============//
  

}

function setServerState() {                 //  Changes the css to the server control mode when opening for the first time
  var pythonVar2 = function (macro, args, response) {
    JSON.stringify(response);               //  Parse the server response so that it is js readable
    if (response == "yay") piAuto = true; else  piAuto = false;  
    // console.log("piAuto State " + piAuto);
    if (piAuto) {                           // Where most of the styling takes place
      $('#switch button:nth-child(2)').attr("id","selected_button"); 
      $('#switch button:first-child').attr("id","deselected_button");
      $("#light_container").animate({opacity : "0.3"},1000);
      $("#light_container button").prop("disabled",true);
      $('#light_container button').attr('title', 'Chose manual mode for controls.');
    } 
      else { 
      $('#switch button:nth-child(2)').attr("id","deselected_button"); 
      $('#switch button:first-child').attr("id","selected_button");
      $("#light_container").animate({opacity : "1"},1000);
      $("#light_container button").prop("disabled",false);
      
    }
  }
  var callWebiopi2 = webiopi().callMacro("getAutomaticControl", [], pythonVar2);  //  Webiopi works backwards so here it will execute all above in the func
}



function getThreshold() {      //   Updates selectedThreshold variable to the server's lux threshold
  var getTrs = webiopi().callMacro("getThreshold", [], function (macro, args, response) {   // getTrs gets the state
    JSON.stringify(response);
    selectedThreshold = parseInt(response);   // updates the variable (whole purpouse of the function)
      $("#change_threshold input[value=" + selectedThreshold + "]").attr('checked',true);
      
      //  selectedThreshold knows the server value so it sets it as a default selected when refreshing the page
  });
}


function getLuminosity() {    // used to update luminosity, called constantly for proper indication
  var brightness = function (macro, args, response) {
    $("#text_luminosity").html("Luminosity: " + parseFloat(response).toFixed(1) + " lux");   // when called itself, updates the text in the client's browser
    setTimeout(getLuminosity, 1000); // repeat infinetly
  }
  var getBrightness = webiopi().callMacro("getLuminosity", [], brightness);
}


function calibrating() {    // Triggers animation and forces the algorithm to recalibrate
   console.log("debugg called me");
   $("#calibrate button").prop("disabled",true);
    $("#calibrate button").animate({opacity:"0.1"},1000);
  gravity();    // Calls js animation
  
  var calib = function (macro, args, response) {
    var ssds = webiopi().callMacro("dAutomaticControl"); 
    calibrationComplete = response;
    console.log(calibrationComplete);
    $("#loading").html("Have Fun ^^ !");
    setTimeout(function () {
      calibrationComplete = false;
      $("#calibrate button").prop("disabled",false);
      $("#calibrate button").animate({opacity:"1"},1000);
          // Resets the values and waits for new calibration
      $("#loading").html("Calibrating");
      $("#windmill").slideToggle("slow");

    }, 200);
    var an = webiopi().callMacro("eAutomaticControl"); 
  }

  var calibResult = webiopi().callMacro("calibReady", [], calib);
  getRefresh(); 
}


function calibrateButton() {    // Creates the calibrate button
  var calibrateButton = webiopi().createButton("calibrateButton", "CALIBRATE", function () {          
    // this disables automatic control       
    webiopi().callMacro("calibrate");   //calibrate      
  });
  $("#calibrate").append(calibrateButton);
}

function setUpdateRefresh(value){
    var setRefresh = function (macro, args, response) {
    refreshRate = parseFloat(response).toFixed(1);
    console.log("value received " + value);
    getRefresh();

  }

  var calibResult = webiopi().callMacro("setTimeSleep", value, setRefresh);
}





function setLightType(value){
  var lightTimeout = function (macro, args, response) {

}

  var calibResult = webiopi().callMacro("calibrationSleep", value, lightTimeout);
}


function formThreshold(){
  $( "#threshold_form" ).submit(function( event ) {

  if ( parseInt($( "input:first" ).val()) ) {
    setThreshold(parseInt($( "input:first" ).val()));
    
  }
  event.preventDefault();

  });
}

function formRefresh(){
  $( "#threshold_form" ).submit(function( event ) {
    console.log("refresh form clicked");

  console.log(parseFloat($( "#refresh_input" ).val()) + " refresh input");

  if ( parseInt($( "#refresh_input" ).val()) ) {
    setUpdateRefresh(parseFloat($( "#refresh_input" ).val()));
  }
  event.preventDefault();
});

}


$("#reset_default").click(function(){
    var answer = confirm('Do you want to reset to default?');
    if (answer)
    {
          setUpdateRefresh(5);
          setThreshold(200);
    }
  });

  setInterval(setServerState, refreshRate*1000);
  setInterval(getThreshold, refreshRate*1000);





});   // <------ webiopi ready function ends here


 // =========== Animation and UI Javascript functions ============= 

function gravity() {
 

  //  ==========  http://stackoverflow.com/questions/7936396/jquery-rotate-transform 
  $("#calibrateButton button").prop("disabled",true);
  var degree=10;
  var fixedSpeed = 800;
  $(function() {
       var $elie = $("#blade");
       rotate(degree);
       function rotate(degree) {

           // For webkit browsers: e.g. Chrome
           $elie.css({ WebkitTransform: 'rotate(' + degree + 'deg)'});
           // For Mozilla browser: e.g. Firefox
           $elie.css({ '-moz-transform': 'rotate(' + degree + 'deg)'});
           if(calibrationComplete){
            return false;
          }
           // Animate rotation with a recursive call
           
           setTimeout(function() { if(degree>800){
            
            rotate(fixedSpeed+=100);
          }else{
            rotate(degree*1.012);
          }},60);
       }
    });
}

function logoSpin(){

    var degree=0;
  $(function() {
       var $elie = $("#sun");
       rotate(degree);
       function rotate(degree) {

           // For webkit browsers: e.g. Chrome
           $elie.css({ WebkitTransform: 'rotate(' + degree + 'deg)'});
           // For Mozilla browser: e.g. Firefox
           $elie.css({ '-moz-transform': 'rotate(' + degree + 'deg)'});
           // Animate rotation with a recursive call
           setTimeout(function() { rotate(++degree % 360); },50);
       }
    });
}


function slider(){
      $("#switch button").click(function(){
      $("#switch button").css({"background-color":"#f0f1f2","color":"#d6d6d6"});
      $(this).css({"background-color":"#74a5f7","color":"white"});
    });
}

function lightTypeToggle(){
  $("#poss button:nth-child(2)").click(function(){
    $("#poss button:nth-child(1)").attr("id","inactive");
    $("#poss button:nth-child(2)").attr("id","poss_active");
  });

  $("#poss button:nth-child(1)").click(function(){
      $("#poss button:nth-child(1)").attr("id","poss_active");
      $("#poss button:nth-child(2)").attr("id","inactive");
  });
}


console.log(refreshRate + " end of file");