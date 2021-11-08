
/* Code.gs
 *
 * Load data from a mysql database table into google sheet
 */

const origin = 'http://127.0.0.1:8980';
const base64 = 'XXXXXXXXXXXXXXXXXXXXX';

function fillSheet1() {

  const url = origin + '/api/asset/inventory?query=true';

  const options = { method: 'GET', 
                    contentType: 'application/json', 
                    headers: { Authorization: 'Basic ' + base64 }, 
                    muteHttpExceptions: true };

  const response = UrlFetchApp.fetch(url, options);
  const data = response.getContentText("UTF-8");
  const json = JSON.parse(data);
  const gDict = {};

  for (const row of Object.keys(json)) {
    gDict[row] = json[row];
  }

  const spreadsheet = SpreadsheetApp.getActive();
  const sheet = spreadsheet.getSheetByName('Sheet1');
  sheet.clearContents();
  sheet.clearFormats(); // clear red
  
  for (const [row, item] of Object.entries(gDict)) {
    const strArr = [];
    for (const element of item) {
      //Logger.log(element);
      strArr.push(element);
    }
    sheet.appendRow(strArr);
  }

  Logger.log("fillRows Sheet1");
}



function onOpen() {

  var ui = SpreadsheetApp.getUi(); // Or DocumentApp, SlidesApp, or FormApp.
  ui.createMenu('⚙️ Admin Settings')
      .addItem('Check Last DataBase Change', 'menu.item1')
      .addSeparator()
      .addSubMenu(ui.createMenu('Sub-menu')
          .addItem('Load Data from DataBase', 'menu.item2'))
      .addToUi();
}

var menu = {
  item1: function() {
    //SpreadsheetApp.getUi().alert('You clicked: First item');
    //fillSheet1();
    probeTable();
  },
  item2: function() {
    //SpreadsheetApp.getUi().alert('You clicked: Second item');
    //probeTable();
    fillSheet1();
  }
}

// https://developers.google.com/apps-script/guides/v8-runtime  
// https://spreadsheet.dev/toast-notifications-in-google-sheets


function probeTable() {

  const url = origin + '/api/information_schema/tables/inventory?column=TABLE_NAME&fields=UPDATE_TIME';

  const options = { method: 'GET', 
                    contentType: 'application/json', 
                    headers: { Authorization: 'Basic ' + base64 }, 
                    muteHttpExceptions: true };

  const response = UrlFetchApp.fetch(url, options);
  const data = response.getContentText("UTF-8");
  const json = JSON.parse(data);
  const gDict = {};

  for (const row of Object.keys(json)) {
    gDict[row] = json[row];
  }

  const spreadsheet = SpreadsheetApp.getActive();
  const sheet = spreadsheet.getSheetByName('Sheet1');
  
  
  for (const [row, item] of Object.entries(gDict)) {
    //var strArr = [];
    //for (const element of item) {
      //Logger.log(element);
    //  strArr.push(element);
    //}
    
    //sheet.appendRow(strArr);

    Logger.log(item);
    //sheet.appendRow(item);

    let title = '⏰ Last Table Change';
    toastMessageTitle(item, title);

  }

  //sheet.appendRow(strArr);

  Logger.log("probeTable");
}

function toastMessageTitle(message=None, title=None) {

  //SpreadsheetApp.getActive().toast(message, title, 15);  // display for 15 seconds
  //SpreadsheetApp.getActive().toast(message, title);
  SpreadsheetApp.getActive().toast(message, title, 60);

}

function setBackgroundColorOnEvenLines() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  var sheet = ss.getActiveSheet();
  var totalRows = sheet.getMaxRows();
  var totalColumns = sheet.getMaxColumns()

  for (var i=2; i <= totalRows; i+=2){
      sheet.getRange(i, 1, 1, totalColumns).setBackground("#F3F3F3");
  }
}


function onEdit(e) {

  if(e.changeType == "INSERT_ROW") {
    e.range.setBackground('yellow');

  }

  if(e.oldValue && e.value && e.oldValue !== e.value){
    e.range.setBackground('red');
    //e.range.setFontColor('red');
  }

}


//Returns the offset value of the column titled "Status"
//(eg, if the 7th column is labeled "Status", this function returns 6)
function getStatusColumnOffset() {
  lastColumn = SpreadsheetApp.getActiveSheet().getLastColumn();
  var range = SpreadsheetApp.getActiveSheet().getRange(1,1,1,lastColumn);

  for (var i = 0; i < range.getLastColumn(); i++) {
    if (range.offset(0, i, 1, 1).getValue() == "Status") {
      return i;
    } 
  }
}


function toastMessageTimeout() {
  // Display the toast for 15 seconds
  SpreadsheetApp.getActive().toast("Message", "Title", 15);
}


Logger.log('start');

// https://spreadsheet.dev/toast-notifications-in-google-sheets



