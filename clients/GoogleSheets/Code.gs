
/* Code.gs
 *
 * Load data from a mysql database table into google sheet
 */

const origin = 'http://127.0.0.1:8980';
const base64 = 'XXXXXXXXXXXXXXXXXXXXX';


function fillSheet1() {

  const url = origin + '/api/example/table1?query=true';

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
  sheet.clearFormats();
  
  for (const [row, item] of Object.entries(gDict)) {
    const strArr = [];
    for (const element of item) {
      strArr.push(element);
    }
    sheet.appendRow(strArr);
  }

  Logger.log("Filled Sheet1");
}

function onEdit(e) {
  if(e.oldValue && e.value && e.oldValue !== e.value) {
    e.range.setBackground('red');
    
  }
}

function createAdminMenu() {
   var menu = SpreadsheetApp.getUi().createMenu("⚙️ Admin Settings");
   menu.addItem("Load Data", "fillSheet1");
   menu.addToUi();
}

Logger.log('run');


