function SpecialOnEdit(event) {
  try {
    const range =  event.source.getActiveRange()

  getA1Notation()
    // var ss = event.source.getActiveSheet()
  // var r = event.source.getActiveRange()
  // Logger.log(ss)
  // Logger.log(r)
  // Logger.log(r.getA1Notation())
  // Logger.log(r.getCell(1, 1))
  // Logger.log(r.getValue())
  //var response = UrlFetchApp.fetch("http://www.google.com/");
  //Logger.log(response.getContentText());

  // r.setComment("Last modified: " + (new Date()));
  } catch (e) {
    Logger.log(e)
  }
}