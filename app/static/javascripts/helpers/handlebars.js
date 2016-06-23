function registerHandleBarHelpers() {
  Handlebars.registerHelper('json', function(context) {
    return JSON.stringify(context, null, 4);
  });
}
