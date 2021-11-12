
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
    probeTable();
  },
  item2: function() {
    //SpreadsheetApp.getUi().alert('You clicked: Second item');
    fillSheet1();
  }
}

// https://developers.google.com/apps-script/guides/v8-runtime  
// https://spreadsheet.dev/toast-notifications-in-google-sheets

function probeTable() {

  const url = origin + '/api/information_schema/tables/inventory?column=TABLE_NAME&fields=TABLE_ROWS,UPDATE_TIME';

  const options = { method: 'GET', 
                    contentType: 'application/json', 
                    headers: { Authorization: 'Basic ' + base64 }, 
                    muteHttpExceptions: true };

  const response = UrlFetchApp.fetch(url, options);
  const data = response.getContentText("UTF-8");
  const json = JSON.parse(data);

  const spreadsheet = SpreadsheetApp.getActive();
  const sheet = spreadsheet.getSheetByName('Sheet1');
  
  let title = '⏰ Last Table Change';
  toastMessageTitle(json, title);

  Logger.log("probeTable");
}

function toastMessageTitle(message=None, title=None) {

  //SpreadsheetApp.getActive().toast(message, title);
  SpreadsheetApp.getActive().toast(message, title, 60); // display for 60 seconds

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

Logger.log('run');

// https://spreadsheet.dev/toast-notifications-in-google-sheets

