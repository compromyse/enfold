var hostIP = "https://app.ecourts.gov.in/ecourt_mobile_DC/";
var netConnectCnt = 0;
var isOnline = true;
var isConnErrorMsgShown = false;
var casesCountArr;
//localization global variables
var global_language = "English";
var globalLanguageJSONObj = null;
var globalServerLabelsJSONObj = null;
var complexes = "";
var bilingual_flag = 0;
var cnrNumbersFromLocalStorage = window.localStorage.getItem("CNR Numbers");
var labelsarr = window.sessionStorage.GLOBAL_LABELS != null ? JSON.parse(window.sessionStorage.GLOBAL_LABELS) : null;
var totalNoOfEstLabel = labelsarr ? labelsarr[390] : "Total Number of Establishments in Court Complex";
var totalNoOfCasesLabel = labelsarr ? labelsarr[83] : "Total Number of Cases";
var partyNameLabel = labelsarr ? labelsarr[30] : "Party Name";
var srNoLabel = labelsarr ? labelsarr[84] : "Sr.No";
var caseNoLabel = labelsarr ? labelsarr[9] : "Case Number";
var courtComplexSelectLabel = labelsarr ? labelsarr[268] : "Select Court Complex";
var globaliv = "4B6250655368566D";
var randomiv = "";
var jwttoken = "";
var regenerateWebserviceCallFlag = false;

//Fetch parameter passed to url of html.
function getParameterByName(name, url) {
  if (!url)
    url = window.location.href;
  name = name.replace(/[\[\]]/g, "\\$&");
  var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
    results = regex.exec(url);
  if (!results)
    return null;
  if (!results[2])
    return '';
  return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function checkDeviceOnlineStatus() {
  var condition = navigator.onLine ? "online" : "offline";
  if (condition == "offline") {
    isOnline = false;
    if (!isOnline) {
      // showErrorMessage("Please check your internet connection and Try again");
      showErrorMessage(labelsarr[717]);
    }
  } else {
    netConnectCnt = 0;
    isOnline = true;
    isConnErrorMsgShown = false;
  }
}

function displayConnErrorMsg() {
  if (!isConnErrorMsgShown) {
    isConnErrorMsgShown = true;
    showErrorMessage(labelsarr[717]);
    // showErrorMessage("Please check your internet connection and Try again");
  }
}

function ChangeUrl(title, url) {
  if (typeof (history.pushState) != "undefined") {
    var obj = { Title: title, Url: url };
    history.pushState(obj, obj.Title, obj.Url);
  } else {
    show("Browser does not support HTML5.");
  }
}
//Fetches court complexes data from web service
function populateCourtComplexes() {
  var state_code_data = window.localStorage.state_code;
  var district_code_data = window.localStorage.district_code;

  $select = $('#court_codec');
  $select_pages = $('#court_code');

  // if(complexes == "" || window.localStorage.SESSION_COURT_CODE == null || window.localStorage.SESSION_SELECTED_COMPLEX_CODE == null){
  if (complexes == "") {
    var courtComplexWebServiceUrl = hostIP + "courtEstWebService.php";

    var encrypted_data1 = ("fillCourtComplex");
    var encrypted_data2 = (state_code_data);
    var encrypted_data3 = (district_code_data);

    var data = { action_code: encrypted_data1.toString(), state_code: encrypted_data2.toString(), dist_code: encrypted_data3.toString() };

    //web service call to get court complexes
    callToWebService(courtComplexWebServiceUrl, data, courtComplexWebServiceResult);
    function courtComplexWebServiceResult(data) {
      var obj = (data.courtComplex);
      myApp.hidePleaseWait();
      if (obj != null) {
        complexes = obj;
        // window.sessionStorage.setItem("SESSION_COMPLEXES", data.courtComplex);                    
        populateComplexes(obj);
      } else {
        $('#court_codec').append('<option id="" value="">' + courtComplexSelectLabel + '</option>');
        $('#court_code').append('<option id="" value="">' + courtComplexSelectLabel + '</option>');
      }

    }
  }
  else {
    // var obj = decodeResponse(complexes);
    populateComplexes(complexes);
  }


}

//Fills court complex select box
function populateComplexes(obj) {
  $('#court_codec').empty();
  $('#court_code').empty();

  //        $select.append('<option id="" value="">Select Court Complex</option>');
  $('#court_codec').append('<option id="" value="">' + courtComplexSelectLabel + '</option>');
  $('#court_code').append('<option id="" value="">' + courtComplexSelectLabel + '</option>');
  var txt_court_complex_name = null;
  $.each(obj, function (key, val) {

    if (bilingual_flag == 0) {
      txt_court_complex_name = val.court_complex_name;

      $('#court_codec').append('<option id="' + val.njdg_est_code + '" value="' + val.njdg_est_code + '" complex_code="' + val.complex_code + '">' + txt_court_complex_name + '</option>');
      $('#court_code').append('<option id="' + val.njdg_est_code + '" value="' + val.njdg_est_code + '" complex_code="' + val.complex_code + '">' + txt_court_complex_name + '</option>');

    } else {
      if (val.lcourt_complex_name != "") {
        txt_court_complex_name = val.lcourt_complex_name;
        $('#court_codec').append('<option id="' + val.njdg_est_code + '" value="' + val.njdg_est_code + '" complex_code="' + val.complex_code + '">' + txt_court_complex_name + '</option>');
        $('#court_code').append('<option id="' + val.njdg_est_code + '" value="' + val.njdg_est_code + '" complex_code="' + val.complex_code + '">' + txt_court_complex_name + '</option>');
      }
    }
  });

  if (window.localStorage.SESSION_COURT_CODE != null) {
    $('#court_codec').val(window.localStorage.SESSION_COURT_CODE);
    if ($('#court_code')) {
      $('#court_code').val(window.localStorage.SESSION_COURT_CODE);
    }
  }
}

//show case history for selected case
$(document).on('click', '.case_history_link', function (e) {
  e.preventDefault();

  var case_number = $(this).attr("case_no");
  var court_code = $(this).attr("court_code");

  var caseHistoryWsUrl = hostIP + "caseHistoryWebService.php";
  var state_code_data = window.localStorage.state_code;
  var district_code_data = window.localStorage.district_code;

  var encrypted_data4 = (localStorage.LANGUAGE_FLAG);
  // var  encrypted_data5=0;
  // if(localStorage.LANGUAGE_FLAG=="english"){
  //      encrypted_data5 = ("0");
  // }else{
  //      encrypted_data5 = ("1");
  // }

  encrypted_data5 = (bilingual_flag.toString());

  var data = { state_code: (state_code_data), dist_code: (district_code_data), case_no: (case_number), court_code: (court_code), language_flag: encrypted_data4.toString(), bilingual_flag: encrypted_data5.toString() };

  // $('#loading').modal('show');

  //web service call to get case history
  callToWebService(caseHistoryWsUrl, data, caseHistoryWebServiceResult);
  function caseHistoryWebServiceResult(data) {
    // $('#loading').modal('hide');
    myApp.hidePleaseWait();

    if (data.history != null) {
      if (CheckBrowser()) {
        window.sessionStorage.setItem("case_history", JSON.stringify((data.history)));
      }
      if (window.localStorage.getItem("SELECTED_COURT") === "DC") {
        // window.location = 'case_history.html';
        $.ajax({
          type: "GET",
          url: "case_history.html"
        }).done(function (data) {
          //                                $("#caseHistoryModal").show();
          $("#historyData").html(data);
          $("#caseHistoryModal").modal('show');
          $("#case_history_label").focus();

        });
      }
      else if (window.localStorage.getItem("SELECTED_COURT") === "HC") {
        //    window.location = 'case_history_hc.html';

        $.ajax({
          type: "GET",
          url: "case_history_hc.html"
        }).done(function (data) {
          $("#caseHistoryModal_hc").show();
          $("#historyData_hc").html(data);
          $("#caseHistoryModal_hc").modal();
        });

      }
    } else {
      showErrorMessage(labelsarr[718]);
      // $('#loading').modal('hide');
      myApp.hidePleaseWait();
    }

  }

});

//show filing case history for selected case
$(document).on('click', '.filing_case_history_link', function (e) {
  e.preventDefault();

  var case_number = $(this).attr("case_no");
  var court_code = $(this).attr("court_code");

  var filingCaseHistoryWsUrl = hostIP + "filingCaseHistory.php";
  var state_code_data = window.localStorage.state_code;
  var district_code_data = window.localStorage.district_code;

  var encrypted_data4 = (localStorage.LANGUAGE_FLAG);
  var encrypted_data5 = 0;
  // if(localStorage.LANGUAGE_FLAG=="english"){
  //      encrypted_data5 = ("0");
  // }else{
  //      encrypted_data5 = ("1");
  // }
  encrypted_data5 = (bilingual_flag.toString());
  var data = { state_code: (state_code_data), dist_code: (district_code_data), case_no: (case_number), court_code: (court_code), language_flag: encrypted_data4.toString(), bilingual_flag: encrypted_data5.toString() };

  // $('#loading').modal('show');

  //web service call to get filing case history
  callToWebService(filingCaseHistoryWsUrl, data, filingCaseHistoryResult);
  function filingCaseHistoryResult(data) {
    if (data.history != null) {
      if (CheckBrowser()) {
        window.sessionStorage.setItem("filing_case_history", JSON.stringify((data.history)));
      }

      // window.location = 'filing_case_history.html';
      $.ajax({
        type: "GET",
        url: "filing_case_history.html"
      }).done(function (data) {
        // $("#caseHistoryModal").show();
        $("#historyData").html(data);
        $("#caseHistoryModal").modal();
      });

      // $('#loading').modal('hide');
      myApp.hidePleaseWait();
    } else {
      showErrorMessage(labelsarr[718]);
      // $('#loading').modal('hide');
      myApp.hidePleaseWait();
    }
  }
});



//check if browser supports localstorage
function CheckBrowser() {
  if ('localStorage' in window && window['localStorage'] !== null) {
    // we can use localStorage object to store data
    return true;
  } else {
    return false;
  }
}


/*get data from web service. Called when there is no data in local storage for selected search*/
function displayCasesTable(url, request_data) {
  arrCourtEstCodes = [];
  arrCourtEstCodes = window.localStorage.SESSION_COURT_CODE.split(',');
  total_Cases = '';
  $("#headers").empty();


  var headerArray = [];
  headerArray.push('<a style="color:#212529;" href="#" id="total_est_header">' + totalNoOfEstLabel + ':<span id="totalEstablishmentsSpanId"></span> </a></div>');
  headerArray.push('<br>');
  headerArray.push('<label>' + totalNoOfCasesLabel + ': <span id="totalcasesId"></span></label></div>');
  $("#headers").append(headerArray);

  var state_code_data = window.localStorage.state_code;
  var district_code_data = window.localStorage.district_code;
  $("#accordion_search").empty();
  //Total number of establishments (comma separated values of court codes)
  var establishments_count = arrCourtEstCodes.length;
  //count used to check if data fetched for all the establishments.
  var count1 = 0;
  // $('#loading').modal('show');
  myApp.showPleaseWait();
  var jsonData = {};


  /* for (var i = 0; i <= arrCourtEstCodes.length - 1; i++) {
      if(arrCourtEstCodes[i] != ","){*/

  var encrypted_data1 = state_code_data;
  var encrypted_data2 = district_code_data;
  var encrypted_data3 = arrCourtEstCodes;
  var encrypted_data4 = (localStorage.LANGUAGE_FLAG);
  // var encrypted_data5=null;
  // if(localStorage.LANGUAGE_FLAG=="english"){
  //      encrypted_data5 = ("0");
  // }else{
  //      encrypted_data5 = ("1");
  // }
  encrypted_data5 = (bilingual_flag.toString());


  var data1 = { state_code: encrypted_data1.toString(), dist_code: encrypted_data2.toString(), court_code_arr: encrypted_data3.toString(), language_flag: encrypted_data4.toString(), bilingual_flag: encrypted_data5.toString() };

  var data = $.extend({}, data1, request_data);

  //Establishment name appears on each panel    
  var establishment_name;

  //Id for panels of each establishement
  var collapseid = 0;

  //populate the result table with court establishment as collapse field
  callToWebService(url, data, caseStatusSearchResult);
  function caseStatusSearchResult(responseData) {
    var obj_caseNos = null;
    if (responseData != null) {
      if (responseData.msg) {
        if ((responseData.status) == 'fail') {
          myApp.hidePleaseWait();
          showErrorMessage((responseData.msg));
        }
      } else {
        for (const val in responseData) {
          var data = responseData[val];

          obj_caseNos = (data.caseNos);
          if (obj_caseNos != null) {
            var obj_courtcode = (data.court_code);

            var obj_establishment_name = (data.establishment_name);

            jsonData[JSON.stringify(obj_courtcode)] = JSON.stringify(data);
            // window.sessionStorage.setItem("SET_RESULT", JSON.stringify(jsonData));
            window.sessionStorage.setItem("SET_RESULT", true);


            var panel_body = [];
            var totalCases = obj_caseNos.length;
            total_Cases = Number(totalCases) + Number(total_Cases);
            var trHTML = '';
            var court_code = obj_courtcode;

            panel_id = 'card' + state_code_data + district_code_data + court_code;


            establishment_name = obj_establishment_name;
            establishment_name = establishment_name + " : " + totalCases;

            panel_body.push('<div class="card" id=' + panel_id + '">');
            panel_body.push('<div class="card-header"><h4 class="panel-title"><a  class="card-link collapsed panel-title-a" data-toggle="collapse" data-target="#' + panel_id + '" href="#' + panel_id + '">' + establishment_name + '</a></h4></div>');
            panel_body.push("<div id=" + panel_id + " class='collapse'><div class='card-body'><table class='table tbl-result'><thead><tr><th>" + srNoLabel + "</th><th>" + caseNoLabel + "</th><th>" + partyNameLabel + "</th></tr></thead><tbody>");

            collapseid++;
            var index = 0;
            var txt_type_name = null;
            $.each(obj_caseNos, function (key, val) {
              index++;
              // if(localStorage.LANGUAGE_FLAG=="english"){
              if (bilingual_flag != "1") {
                txt_type_name = val.type_name;
              } else {
                txt_type_name = val.ltype_name;
              }
              var petresName = val.petnameadArr;
              var case_type_number = txt_type_name + '/' + val.case_no2 + '/' + val.reg_year;

              var casehistorylink = '';
              var case_no_ = val.case_no;
              if (val.case_no == null) {
                case_no_ = val.filing_no;
                casehistorylink = 'filing_case_history_link';
              } else {
                casehistorylink = 'case_history_link';
              }

              var hrefurl = "<a style='color:#03A8D8;text-decoration:underline;' href='#' class='" + casehistorylink + "  'court_code='" + court_code + "'cino='" + val.cino + "'case_no='" + case_no_ + "'>" + case_type_number + '</a>';

              trHTML += "<tr><td>" + index + "</td><td>" + hrefurl + "</td><td>" + petresName + "</td></tr>";
              panel_body.push("<tr><td>" + index + "</td><td>" + hrefurl + "</td><td>" + petresName + "</td></tr>");
            });

            panel_body.push("</tbody></table></div></div>");
            count1++;
            panel_body.push('</div>');
            if (Number(totalCases) != 0) {
              $("#accordion_search").append(panel_body.join(""));
            }

            document.getElementById('totalcasesId').innerHTML = total_Cases;
            document.getElementById('totalEstablishmentsSpanId').innerHTML = establishments_count;

          } else {
            document.getElementById('totalEstablishmentsSpanId').innerHTML = establishments_count;

          }
        }
      }

    } else {
      //establishments_count -= 1;
      document.getElementById('totalEstablishmentsSpanId').innerHTML = establishments_count;

    }
    if (count1 == establishments_count) {
      // $('#loading').modal('hide');

      //                        $('#goButton').prop('autofocus');
      //                        $('#total_est_header').attr('style','background:red');
      myApp.hidePleaseWait();
      $('#goButton').focus();
    }


  }




  /* }else {
       /*If connection to establishment fails, reduce the total number of establishments*/
  /*establishments_count -= 1;
  document.getElementById('totalEstablishmentsSpanId').innerHTML = establishments_count;

}
}*/
}
/*function to display header for all forms, case history , view business and writ info*/
function second_header() {
  // $("#header").load("header.html", function (response, status, xhr) {

  //     $('#go_back_link').on('click', function (event) {
  //         event.preventDefault();
  //         window.location = "index.html";                
  //     });

  // });

  $("#header_srchpage").load("header.html", function (response, status, xhr) {

    $('#go_back_link').on('click', function (event) {
      backButtonHistory.pop();
      window.sessionStorage.removeItem("SET_RESULT");
      $("#searchPageModal").modal('hide');
      var prev_selected_btn = window.sessionStorage.getItem("Selected_screen");
      $("." + prev_selected_btn).focus();
    });

    $("#open_close1").on('click', function (event) {
      if ($("#mySidenav1").is(':visible')) {
        closeNav1();
      } else {
        openNav1();
      }
    });
  });
}

/*To Export saved cases from local storage to myCases.txt file from device internal storage*/
function backupContent(socialSharing, savetodatadir, showSuccessAlert) {
  //var cnrNumbersStr = window.localStorage.getItem("CNR Numbers");
  var cnrNumbersStr = 0;
  var cnrNumbersArr_parsed;
  var CNR_array = localStorage.getItem("CNR Numbers");
  if (CNR_array) {
    cnrNumbersArrLength = JSON.parse(CNR_array).length;
    cnrNumbersArr_parsed = JSON.parse(CNR_array);
  }

  if (CNR_array && cnrNumbersArr_parsed.length != 0) {
    cnrNumbersStr = CNR_array;
    var fileName = '';
    if (!showSuccessAlert) {
      fileName = 'myCases.txt';
    } else {
      fileName = 'myCases_backup.txt';
    }

    var data = cnrNumbersStr;
    if (socialSharing === "drive") {
      myApp.showPleaseWait();
      window.plugins.googleplus.login(
        {
          // 'scopes' : 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/drive.appdata https://www.googleapis.com/auth/drive.apps.readonly https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/drive.metadata https://www.googleapis.com/auth/drive.scripts',

          'scopes': 'https://www.googleapis.com/auth/drive.file',
          'webClientId': '658126779023-qls50eu22l3r5dipb8a4jm6kirdcrg83.apps.googleusercontent.com', // optional clientId of your Web application from Credentials settings of your project - On Android, this MUST be included to get an idToken. On iOS, it is not required.
          'offline': true, // optional, but requires the webClientId - if set to true the plugin will also return a serverAuthCode, which can be used to grant offline access to a non-Google server
        },
        function (obj) {
          var access_token = obj.accessToken;
          var boundary = "foo_bar_baz";
          const delimiter = "\r\n--" + boundary + "\r\n";
          const close_delim = "\r\n--" + boundary + "--";
          var fileContent = cnrNumbersStr; // As a sample, upload a text file.
          var tmpfile = new Blob([fileContent], { type: 'text/plain' });
          var contentType = 'text/plain';

          var metadata = {
            "name": 'myCases.txt',
            "mimeType": 'text/plain'
          };

          var multipartRequestBody =
            delimiter + 'Content-Type: application/json\r\n\r\n' +
            JSON.stringify(metadata) +
            delimiter + 'Content-Type: ' + contentType + '\r\n' + '\r\n' +
            cnrNumbersStr +
            close_delim;

          //var fileId = window.localStorage.getItem("FILE_ID");

          $.ajax({
            type: "GET",
            beforeSend: function (request) {
              request.setRequestHeader("Authorization", "Bearer" + " " + access_token);
            },
            url: "https://www.googleapis.com/drive/v3/files?q=(name = 'myCases.txt')",

            success: function (data) {
              //alert(JSON.stringify(data));
              if (data.files.length == 1) {
                var fileId = data.files[0].id;
                $.ajax({
                  type: "PATCH",
                  beforeSend: function (request) {
                    request.setRequestHeader("Authorization", "Bearer" + " " + access_token);
                    request.setRequestHeader("Content-Type", 'multipart/related; boundary="' + boundary + '"');

                  },
                  url: "https://www.googleapis.com/upload/drive/v3/files/" + fileId + "/?uploadType=multipart",

                  success: function (data) {
                    alert(labelsarr[676]);
                    myApp.hidePleaseWait();
                    localStorage.setItem("LAST_MyCASES_EXPORT", new Date());
                    $("#exportCasesWarning").hide();
                    $("#my_cases_text").show();

                  },
                  error: function (error) {
                    alert(error);
                    myApp.hidePleaseWait();
                    //alert('error'+JSON.stringify(error));
                  },
                  async: true,
                  data: multipartRequestBody,
                  cache: false,
                  contentType: false,
                  processData: false,
                  crossDomain: true
                });
              } else if (data.files.length == 0) {
                $.ajax({
                  type: "POST",
                  beforeSend: function (request) {
                    request.setRequestHeader("Authorization", "Bearer" + " " + access_token);
                    request.setRequestHeader("Content-Type", 'multipart/related; boundary="' + boundary + '"');

                  },
                  url: "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",

                  success: function (data) {
                    alert(labelsarr[677]);
                    myApp.hidePleaseWait();
                    localStorage.setItem("LAST_MyCASES_EXPORT", new Date());
                    $("#exportCasesWarning").hide();
                    $("#my_cases_text").show();

                  },
                  error: function (error) {
                    //alert('error'+JSON.stringify(error));
                    alert(labelsarr[705]);
                    myApp.hidePleaseWait();
                  },
                  async: true,
                  data: multipartRequestBody,
                  cache: false,
                  contentType: false,
                  processData: false,
                  crossDomain: true
                });
              } else if (data.files.length > 1) {
                alert(labelsarr[671]);
                myApp.hidePleaseWait();
              }

            },
            error: function (error) {
              myApp.hidePleaseWait();
              alert(labelsarr[705]);
            }
          });
        },
        function (msg) {
          myApp.hidePleaseWait();
          alert(labelsarr[705]);
        }

      );
    } else if (socialSharing === "telegram") {
      window.resolveLocalFileSystemURL(cordova.file.externalRootDirectory, function (directoryEntry) {
        directoryEntry.getFile(fileName, { create: true }, function (fileEntry) {
          fileEntry.createWriter(function (fileWriter) {
            fileWriter.onwriteend = function (result) {
              window.plugins.socialsharing.shareVia('telegram', 'Message via telegram', fileName, cordova.file.externalRootDirectory + fileName, function (e) { alert(e) }, function (e) { alert(e) });
            };
            fileWriter.onerror = function (error) {
              showErrorMessage(error);
            };
            fileWriter.write(data);
          }, function (error) {
            showErrorMessage(error);
          });
        }, function (error) {
          showErrorMessage(error);
        });
      }, function (error) {
        showErrorMessage(error);
      });

    } else if (socialSharing === "email") {
      var storageLocation;
      switch (device.platform) {
        case "Android":
          if (savetodatadir) {
            storageLocation = cordova.file.externalDataDirectory;
          } else {
            storageLocation = cordova.file.externalRootDirectory + "Download/";
          }
          break;

        case "iOS":
          storageLocation = cordova.file.documentsDirectory;
          break;
      }

      window.resolveLocalFileSystemURL(storageLocation, function (directoryEntry) {
        directoryEntry.getFile(fileName, { create: true }, function (fileEntry) {
          fileEntry.createWriter(function (fileWriter) {
            fileWriter.onwriteend = function (result) {
              window.plugins.socialsharing.shareViaEmail('Message',
                'Subject',
                null,
                null,
                null,
                [storageLocation + fileName],
                function (e) { },
                function (e) {
                  localStorage.setItem("LAST_MyCASES_EXPORT", new Date());
                  $("#exportCasesWarning").hide();
                  $("#my_cases_text").show();
                });
            };
            fileWriter.onerror = function (error) {
              if (savetodatadir) {
                showErrorMessage("error1 " + error.code, error.code);
              }
            };
            fileWriter.write(data);
          }, function (error) {
            if (savetodatadir) {
              showErrorMessage("error2 " + error.code, error.code);
            }
          });
        }, function (error) {
          if (savetodatadir) {
            showErrorMessage("error3 " + error.code, error.code);
          }
        });
      }, function (error) {
        if (savetodatadir) {
          showErrorMessage("error4 " + error.code, error.code);
        }
      });
      if (!savetodatadir) {
        backupContent(socialSharing, true);
      }

    } else if (socialSharing === "device") {

      myApp.showPleaseWait();
      var storageLocation;
      switch (device.platform) {
        case "Android":
          if (savetodatadir) {
            storageLocation = cordova.file.externalDataDirectory;
          } else {
            storageLocation = cordova.file.externalRootDirectory + "Download/";
          }
          break;

        case "iOS":
          storageLocation = cordova.file.documentsDirectory;
          break;
      }

      //			 window.resolveLocalFileSystemURL(cordova.file.externalRootDirectory, function (directoryEntry) {
      window.resolveLocalFileSystemURL(storageLocation, function (directoryEntry) {
        directoryEntry.getFile(fileName, { create: true, exclusive: false }, function (fileEntry) {
          fileEntry.createWriter(function (fileWriter) {
            fileWriter.onwriteend = function (result) {
              myApp.hidePleaseWait();
              if (savetodatadir && !showSuccessAlert) {
                alert(labelsarr[678]);
              }

              if (!showSuccessAlert) {
                localStorage.setItem("LAST_MyCASES_EXPORT", new Date());
                $("#exportCasesWarning").hide();
                $("#my_cases_text").show();
              }
            };
            fileWriter.onerror = function (error) {
              myApp.hidePleaseWait();
              if (savetodatadir) {
                showErrorMessage("error1 " + error.code, error.code);
              }
            };
            fileWriter.write(data);
          }, function (error) {
            myApp.hidePleaseWait();
            if (savetodatadir) {
              showErrorMessage("error2 " + error.code, error.code);
            }
          });
        }, function (error) {
          myApp.hidePleaseWait();
          if (savetodatadir) {
            showErrorMessage("error3 " + error.code, error.code);
          }
        });
      }, function (error) {
        myApp.hidePleaseWait();
        if (savetodatadir) {
          showErrorMessage("error4 " + error.code, error.code);
        }
      });
      if (!savetodatadir) {
        backupContent(socialSharing, true);
      }

    }
  } else {
    myApp.hidePleaseWait();
    if (savetodatadir && !showSuccessAlert) {
      showErrorMessage(labelsarr[836]);
    }
  }

}



/*To Import cases from myCases.txt file from device internal storage to local storage and display in My Cases */
function importFileFrom(socialSharing, readFromDataDir, showSuccsAlrt) {
  var fileName = '';  // your file name
  if (!showSuccsAlrt) {
    fileName = 'myCases.txt';
  } else {
    fileName = 'myCases_backup.txt';
  }

  if (socialSharing === "device") {
    myApp.showPleaseWait();
    /*$.get('test.txt', function(data) {
        backupcnrNumbersArray = JSON.parse(data);
         if (backupcnrNumbersArray.length > 0) {
             myApp.hidePleaseWait();
             localStorage.setItem("CNR Numbers", JSON.stringify(backupcnrNumbersArray));
             $("#showCaseDiv").show();
//                    resetDatePicker(); 
             clearSearchText();
             $("#searchCasesButton").click();  
             $("#allCasesBtn").addClass("active");
             $("#todaysCasesBtn").removeClass("active"); 
             
             updateAllCasesAcordion(backupcnrNumbersArray);                    
             setCalendarCountArr(backupcnrNumbersArray);
             document.getElementById("mycases_span_id").innerHTML = backupcnrNumbersArray.length;
         } else {
             myApp.hidePleaseWait();
             showErrorMessage("No cases found");
         }
     }, 'text');*/
    var storageLocation;
    switch (device.platform) {
      case "Android":
        if (readFromDataDir) {
          storageLocation = cordova.file.externalDataDirectory;
        } else {
          storageLocation = cordova.file.externalRootDirectory + "Download";
        }
        break;

      case "iOS":
        storageLocation = cordova.file.documentsDirectory;
        break;
    }

    window.resolveLocalFileSystemURL(storageLocation, function (directoryEntry) {

      directoryEntry.getFile(fileName, { create: false }, function (fileEntry) {

        fileEntry.file(function (file) {

          var reader = new FileReader();
          reader.onloadend = function (e) {
            if (reader.result == null) {
              myApp.hidePleaseWait();
              //showErrorMessage(labelsarr[672]+" "+fileName+" "+labelsarr[673]);
              if (!readFromDataDir) {
                importFileFrom(socialSharing, true);
              } else if (!showSuccsAlrt) {
                showErrorMessage(labelsarr[672] + " " + fileName + " " + labelsarr[673]);
              }
            } else {
              backupcnrNumbersArray = JSON.parse(reader.result);
              if (backupcnrNumbersArray.length > 0) {
                if (showSuccsAlrt) {
                  $("#importCasesDialog").modal();
                } else {
                  localStorage.setItem("CNR Numbers", JSON.stringify(backupcnrNumbersArray));

                  $("#showCaseDiv").show();
                  //resetDatePicker();
                  clearSearchText();
                  $("#searchCasesButton").click();
                  $("#allCasesBtn").addClass("active");
                  $("#todaysCasesBtn").removeClass("active");

                  setCalendarCountArr(backupcnrNumbersArray);

                  updateAllCasesAcordion();
                  document.getElementById("mycases_span_id").innerHTML = backupcnrNumbersArray.length;
                  myApp.hidePleaseWait();
                  if (!showSuccsAlrt) {
                    alert(labelsarr[669]);
                  }
                }
                $("#btnYes").click(function () {
                  localStorage.setItem("CNR Numbers", JSON.stringify(backupcnrNumbersArray));

                  $("#showCaseDiv").show();
                  //resetDatePicker();
                  clearSearchText();
                  $("#searchCasesButton").click();
                  $("#allCasesBtn").addClass("active");
                  $("#todaysCasesBtn").removeClass("active");

                  setCalendarCountArr(backupcnrNumbersArray);

                  updateAllCasesAcordion();
                  document.getElementById("mycases_span_id").innerHTML = backupcnrNumbersArray.length;
                  myApp.hidePleaseWait();
                  if (!showSuccsAlrt) {
                    alert(labelsarr[669]);
                  }
                  $("#importCasesDialog").hide();
                });
                $("#btnCancle").click(function () {
                  $("#importCasesDialog").hide();
                  return;
                });

              } else {
                myApp.hidePleaseWait();
                //showErrorMessage(labelsarr[681]);
                if (!readFromDataDir) {
                  importFileFrom(socialSharing, true);
                } else if (!showSuccsAlrt) {
                  showErrorMessage(labelsarr[681]);
                }
              }
            }
          }

          reader.readAsText(file);
        }, errorHandler);
      }, onErrorCreateFile);
    });
    function errorHandler() {
      myApp.hidePleaseWait();
      if (!readFromDataDir) {
        importFileFrom(socialSharing, true);
      } else if (!showSuccsAlrt) {
        showErrorMessage(labelsarr[672] + " " + fileName + " " + labelsarr[673]);
      }
    }
    function onErrorCreateFile() {
      myApp.hidePleaseWait();
      if (!readFromDataDir) {
        importFileFrom(socialSharing, true);
      } else if (!showSuccsAlrt) {
        showErrorMessage(labelsarr[672] + " " + fileName + " " + labelsarr[673]);
      }
    }

  } else if (socialSharing === "drive") {
    myApp.showPleaseWait();
    window.plugins.googleplus.login(
      {
        //'scopes' : 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/drive.appdata https://www.googleapis.com/auth/drive.apps.readonly https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/drive.metadata https://www.googleapis.com/auth/drive.scripts',

        'scopes': 'https://www.googleapis.com/auth/drive.file',
        'webClientId': '658126779023-qls50eu22l3r5dipb8a4jm6kirdcrg83.apps.googleusercontent.com', // optional clientId of your Web application from Credentials settings of your project - On Android, this MUST be included to get an idToken. On iOS, it is not required.
        'offline': true, // optional, but requires the webClientId - if set to true the plugin will also return a serverAuthCode, which can be used to grant offline access to a non-Google server
      },
      function (obj) {
        var access_token = obj.accessToken;
        var contentType = 'text/plain';

        $.ajax({
          type: "GET",
          dataType: "json",
          beforeSend: function (request) {
            request.setRequestHeader("Authorization", "Bearer" + " " + access_token);
          },
          url: "https://www.googleapis.com/drive/v3/files?q=(name = 'myCases.txt')",

          success: function (data) {

            myApp.hidePleaseWait();
            if (data.files.length == 1) {
              var fileId = data.files[0].id;
              $.ajax({
                type: "GET",
                beforeSend: function (request1) {
                  request1.setRequestHeader("Authorization", "Bearer" + " " + access_token);
                },
                url: "https://www.googleapis.com/drive/v3/files/" + fileId + "?alt=media",

                success: function (data) {

                  backupcnrNumbersArray = JSON.parse(data);
                  if (backupcnrNumbersArray.length > 0) {
                    localStorage.setItem("CNR Numbers", JSON.stringify(backupcnrNumbersArray));

                    $("#showCaseDiv").show();
                    //resetDatePicker();
                    clearSearchText();
                    $("#searchCasesButton").click();
                    $("#allCasesBtn").addClass("active");
                    $("#todaysCasesBtn").removeClass("active");

                    setCalendarCountArr(backupcnrNumbersArray);

                    updateAllCasesAcordion();
                    document.getElementById("mycases_span_id").innerHTML = backupcnrNumbersArray.length;
                    alert(labelsarr[669]);
                    myApp.hidePleaseWait();
                  } else {
                    myApp.hidePleaseWait();
                    showErrorMessage(labelsarr[681]);
                  }
                },
                error: function (error) {
                  myApp.hidePleaseWait();
                  alert(labelsarr[705]);
                  //alert('error'+JSON.stringify(error));
                }
              });
            } else if (data.files.length == 0) {
              myApp.hidePleaseWait();
              alert(labelsarr[670]);
            } else if (data.files.length > 1) {
              myApp.hidePleaseWait();
              alert(labelsarr[671]);
            }
          },
          error: function (error) {
            myApp.hidePleaseWait();
            alert(labelsarr[705]);
            //alert(JSON.stringify(error));                        
          }

        });
      });
  }
}


/*$.get('test.txt', function(data) {
       
       backupcnrNumbersArray = JSON.parse(data);
        if (backupcnrNumbersArray.length > 0) {
            localStorage.setItem("CNR Numbers", JSON.stringify(backupcnrNumbersArray));
            $("#showCaseDiv").show();
//                    resetDatePicker(); 
            clearSearchText();
            $("#searchCasesButton").click();  
            $("#allCasesBtn").addClass("active");
            $("#todaysCasesBtn").removeClass("active"); 
            
            updateAllCasesAcordion(backupcnrNumbersArray);                    
            setCalendarCountArr(backupcnrNumbersArray);
            document.getElementById("mycases_span_id").innerHTML = backupcnrNumbersArray.length;
        } else {
            showErrorMessage("No cases found");
        }
    }, 'text');  */

// function ConfirmDialog(message) {
//     $('<div></div>').appendTo('body')
//         .html('<div><h6>' + message + '?</h6></div>')
//         .dialog({
//         modal: true,
//         title: 'Delete message',
//         zIndex: 10000,
//         autoOpen: true,
//         width: 'auto',
//         resizable: false,
//         buttons: {
//             Yes: function() {
//             $('body').append('<h1>Confirm Dialog Result: <i>Yes</i></h1>');            
//             $(this).dialog("close");
//             },
//             No: function() {
//             $('body').append('<h1>Confirm Dialog Result: <i>No</i></h1>');            
//             $(this).dialog("close");
//             }
//         },
//         close: function(event, ui) {
//             $(this).remove();
//         }
//         });
//     };

//below code to import language string files for localization...
function importLanguageFile() {
  var getAllLabelsWebServiceUrl = hostIP + "getAllLabelsWebService.php";

  var encrypted_data1 = (localStorage.getItem("LANGUAGE_FLAG"));
  if (localStorage.LANGUAGE_FLAG == "english") {
    var encrypted_data2 = ("0");
  } else {
    var encrypted_data2 = ("1");
  }

  /* */
  // var bilingual_flag1 = "1";
  // var encrypted_data2 = (bilingual_flag1.toString());        

  // var encrypted_data2 = (bilingual_flag.toString());
  var data = { language_flag: encrypted_data1.toString(), bilingual_flag: encrypted_data2.toString() };

  //web service call to get court complexes
  callToWebService(getAllLabelsWebServiceUrl, data, getAllLabelsWebServiceResult);
  function getAllLabelsWebServiceResult(data) {
    var obj = (data.allLabels);

    if (window.sessionStorage.LANGUAGES_AVAILABLE == null) {
      var languages = (data.languages_available);
      window.sessionStorage.setItem("LANGUAGES_AVAILABLE", JSON.stringify(languages));
      populateLabelsRadioButtons(languages);
    } else {
      populateLabelsRadioButtons(JSON.parse(window.sessionStorage.LANGUAGES_AVAILABLE));
    }
    myApp.hidePleaseWait();
    if (obj != null) {
      resetLabelsOnIndexPage(obj);
      resetAllTabPanels();
    } else {
      showErrorMessage(labelsarr[675]);
    }
  }
}

//variable to save cause list result in session storage(To avoid repeat ajax calls once result is retrieved)
var CAUSE_LIST_RESULT = '';

/*setter for cause list result called after getting the result for cause
list seatch
*@cause_list_result : stringified cases json object
*/
function setCauseListResult(cause_list_result) {
  CAUSE_LIST_RESULT = cause_list_result;
}

//getter for cause list result called to get cause list search result after page reload
function getCauseListResult() {
  return CAUSE_LIST_RESULT;
}

//function to retain state of collapse fields after page reload
$(document).on("show.bs.collapse", ".collapse", function (event) {
  var active = $(this).attr('id');
  var panels = localStorage.panels === undefined ? new Array() : JSON.parse(localStorage.panels);
  if ($.inArray(active, panels) == -1) //check that the element is not in the array
    panels.push(active);
  localStorage.panels = JSON.stringify(panels);
});

//function to retain state of collapse fields after page reload
$(document).on("hidden.bs.collapse", ".collapse", function (event) {
  var active = $(this).attr('id');
  var panels = localStorage.panels === undefined ? new Array() : JSON.parse(localStorage.panels);
  var elementIndex = $.inArray(active, panels);
  if (elementIndex !== -1) //check the array
  {
    panels.splice(elementIndex, 1); //remove item from array
  }
  localStorage.panels = JSON.stringify(panels); //save array on localStorage
});


function setRandomIv(riv) {
  randomiv = riv;
}

function getRandomIv() {
  return randomiv;
}


/*
*function to decrypt response
*@result : encrypted result
*/
function decodeResponse(result) {
  var key = CryptoJS.enc.Hex.parse('3273357638782F413F4428472B4B6250');
  var iv_random = CryptoJS.enc.Hex.parse(result.trim().slice(0, 32));
  var result_split = result.trim().slice(32);
  var bytes = CryptoJS.AES.decrypt(result_split.trim(), key, { iv: iv_random }, { mode: CryptoJS.mode.CBC });
  var plaintext = bytes.toString(CryptoJS.enc.Utf8);
  s = plaintext;
  s = s.replace(/\\n/g, "\\n")
    .replace(/\\'/g, "\\'")
    .replace(/\\"/g, '\\"')
    .replace(/\\&/g, "\\&")
    .replace(/\\r/g, "\\r")
    .replace(/\\t/g, "\\t")
    .replace(/\\b/g, "\\b")
    .replace(/\\f/g, "\\f");
  // remove non-printable and other non-valid JSON chars
  s = s.replace(/[\u0000-\u0019]+/g, "");
  return s;
}


//Function to generate random hex number
function genRanHex(size) {
  var hex = [...Array(size)]
    .map(() => Math.floor(Math.random() * 16).toString(16)).join('');
  return hex;
}

//common code for spinner
var myApp;
myApp = myApp || (function () {

  var pleaseWaitDiv = $('<div class="modal" id="pleaseWaitDialog" data-backdrop="static"data-keyboard="false"><div class="modal-content" style="margin-top:50%;"><div class="modal-body text-center"><i class="fa fa-spinner fa-spin fa-3x fa-fw"></i><h3 style="color:#FFF;font-weight: bold;" >loading...</h3></div></div></div>');

  return {
    showPleaseWait: function () {
      pleaseWaitDiv.modal('show');
    },
    hidePleaseWait: function () {
      pleaseWaitDiv.modal('hide');
    },

  };
})();
//spinner code ends

//common function to show error messages
function showErrorMessage(message) {
  $.bootstrapGrowl(message, {
    ele: 'body', // which element to append to
    type: 'danger', // (null, 'info', 'danger', 'success')
    offset: { from: 'bottom', amount: 20 }, // 'top', or 'bottom'
    align: 'center', // ('left', 'right', or 'center')
    width: 'auto', // (integer, or 'auto')
    delay: 2000, // Time while the message will be displayed. It's not equivalent to the *demo* timeOut!
    allow_dismiss: false, // If true then will display a cross to close the popup.
    stackup_spacing: 10 // spacing between consecutively stacked growls.
  });
}

//common function to show info messages
function showInfoMessage(message) {
  $.bootstrapGrowl(message, {
    ele: 'body', // which element to append to
    type: 'info', // (null, 'info', 'danger', 'success')
    offset: { from: 'bottom', amount: 20 }, // 'top', or 'bottom'
    align: 'center', // ('left', 'right', or 'center')
    width: 'auto', // (integer, or 'auto')
    delay: 2000, // Time while the message will be displayed. It's not equivalent to the *demo* timeOut!
    allow_dismiss: false, // If true then will display a cross to close the popup.
    stackup_spacing: 10 // spacing between consecutively stacked growls.
  });
}


function getCalendarCountArr() {
  return casesCountArr;
}

function setCalendarCountArr(cnrNumbersArr) {

  if (cnrNumbersArr && cnrNumbersArr.length > 0) {
    calendarDates = cnrNumbersArr.reduce(function (calendarDates, current) {

      var caseInfo = JSON.parse(current);

      /*let dtNextStr = "";
      let dtLastStr = "";
      let dtDecStr = "";*/

      var dtNextStr = "";
      var dtLastStr = "";
      var dtDecStr = "";

      if (caseInfo.date_next_list) {
        dtNext = caseInfo.date_next_list.split('-');
        dtNextStr = (dtNext[2] + "-" + dtNext[1] + "-" + dtNext[0]);
      }

      if (caseInfo.date_last_list) {
        dtLast = caseInfo.date_last_list.split('-');
        dtLastStr = (dtLast[2] + "-" + dtLast[1] + "-" + dtLast[0]);
      }

      if (caseInfo.date_of_decision) {
        dtDec = caseInfo.date_of_decision.split('-');
        dtDecStr = (dtDec[2] + "-" + dtDec[1] + "-" + dtDec[0]);
      }

      if (dtNextStr) {
        calendarDates[dtNextStr] = calendarDates[dtNextStr] || [];
        calendarDates[dtNextStr].push(current);
      }

      if (dtLastStr) {
        if ((dtNextStr != dtLastStr) && (dtNextStr != dtDecStr) && (dtLastStr != dtDecStr)) {
          calendarDates[dtLastStr] = calendarDates[dtLastStr] || [];
          calendarDates[dtLastStr].push(current);
        }
      }

      if (dtDecStr) {
        if ((dtNextStr != dtLastStr) && (dtNextStr != dtDecStr)) {
          calendarDates[dtDecStr] = calendarDates[dtDecStr] || [];
          calendarDates[dtDecStr].push(current);
        }
      }

      return calendarDates;

    }, {});
    var calendarCntArr = {};
    $.each(calendarDates, function (index, value) {
      //let length = calendarDates[index].length;                    
      var length = calendarDates[index].length;
      calendarCntArr[index] = length;
    });
    casesCountArr = calendarCntArr;
  } else {
    casesCountArr = null;
  }
}

function mapMarkerClicked() {
  // window.location = 'map.html?navigation_link=case_history.html&state_code='+state_code+'&dist_code='+district_code+'&court_code='+court_code+'&complex_code='+complex_code;

  $.ajax({
    type: "GET",
    url: "map.html?navigation_link=home"
  }).done(function (data) {
    // $("#caseHistoryModal").show();
    document.getElementById("mySidenav").style.display = "none";
    $("#mapData").html(data);
    $("#mapModal").modal();
  });

}

//checks connection
function checkConnection() {
  var networkState = navigator.connection && navigator.connection.type;
  if ((networkState == 'offline') || (networkState == 'none')) {

    netConnectCnt = netConnectCnt + 1;
    if (netConnectCnt <= 1) {
      showErrorMessage(labelsarr[717]);
      // showErrorMessage("Please check your internet connection and Try again");
    }
    isOnline = false;
  } else {
    isOnline = true;
  }
}

function callToWebService(url, data, callback) {
  var data1 = encryptData(data);
  header = {
    'Authorization': 'Bearer ' + encryptData(jwttoken)
  };

  cordova.plugin.http.setRequestTimeout(180);
  cordova.plugin.http.get(url, {
    params: data1
  }, header, function (response) {

    var responseDecoded = JSON.parse(decodeResponse(response.data));

    if (responseDecoded.token) {
      jwttoken = responseDecoded.token;
    }

    if (responseDecoded.status && responseDecoded.status == 'N') {
      if (responseDecoded.status_code == '401') {
        if (!regenerateWebserviceCallFlag) {
          regenerateWebserviceCallFlag = true;
          cordova.getAppVersion.getPackageName(function (pkgname) {
            var uidObj = {
              "uid": "324456" + ":" + pkgname
            };
            data = {
              ...data,
              ...uidObj
            };
            callToWebService(url, data, callback);
          });
        } else {
          showErrorMessage("Session expired !");
        }
      }
      if (responseDecoded.msg)
        showErrorMessage(responseDecoded.msg);
    } else {
      callback(responseDecoded);
      regenerateWebserviceCallFlag = false;
    }
  }, function (response) {
    //showErrorMessage(labelsarr[705]);
    myApp.hidePleaseWait();
    regenerateWebserviceCallFlag = false;
  });


  function encryptData(data) {
    var dataEncoded = JSON.stringify(data);
    generateGlobalIv();
    var randomiv = genRanHex(16);
    var key = CryptoJS.enc.Hex.parse('4D6251655468576D5A7134743677397A');
    var iv = CryptoJS.enc.Hex.parse(globaliv + randomiv);
    var encrypted = CryptoJS.AES.encrypt((dataEncoded), key, {
      iv: iv
    });
    var encrypted_data = encrypted.ciphertext.toString(CryptoJS.enc.Base64);
    encrypted_data = randomiv + globalIndex + encrypted_data;
    return encrypted_data;
  }

  function generateGlobalIv() {
    var a = ["556A586E32723575", "34743777217A2543", "413F4428472B4B62", "48404D635166546A", "614E645267556B58", "655368566D597133"];
    var test_arr = [0, 1, 2, 3, 4, 5];
    shuffle(test_arr);

    function shuffle(array) {
      var i = 0,
        j = 0,
        temp = null

      for (i = array.length - 1; i > 0; i -= 1) {
        j = Math.floor(Math.random() * (i + 1))
        temp = array[i]
        array[i] = array[j]
        array[j] = temp
      }
    }
    globaliv = a[test_arr[0]].toString();
    globalIndex = test_arr[0];
  }
}
