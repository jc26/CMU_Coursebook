function makeProfileCircleImage(imgClass) {
  var obj = $('.' + imgClass + '-img img');
  var width = obj.width();
  var height = obj.height();
  if (width < height) {
    obj.css('width', '100%');
    obj.css('height', 'auto');
  } else {
    obj.css('width', 'auto');
    obj.css('height', '100%');
    obj.css('margin-left', '-20px');
  }
}
