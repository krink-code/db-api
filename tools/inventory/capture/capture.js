

/* 
    https://developer.mozilla.org/en-US/docs/Web/API/Navigator
    https://developer.mozilla.org/en-US/docs/Web/API/Navigator/getUserMedia
 */

// This is a deprecated method. Use navigator.mediaDevices.getUserMedia() instead

const version = 'navigator.getUserMedia.v1';

(function() {
  var video = document.getElementById('video'),
      canvas = document.getElementById('canvas'),
      context = canvas.getContext('2d'),
      photo = document.getElementById('photo'),
      vendorUrl = window.URL || window.webkitURL;

  navigator.getMedia = navigator.getUserMedia ||
                       navigator.webkitGetUserMedia ||
                       navigator.mozGetUserMedia ||
                       navigator.msGetUserMedia;

  navigator.getMedia({
    video: true,
    audio: false
  }, function(stream) {
      // success
      //video.src = vendorUrl.createObjectURL(stream);
      video.srcObject = stream;
      video.play();
  }, function(error) {
      // an error
      // error.code
  });

  document.getElementById('capture').addEventListener('click', function() {
    context.drawImage(video, 0, 0, 400, 300);

    // manipulate image

    photo.setAttribute('src', canvas.toDataURL('image/png'));
  });

})();


