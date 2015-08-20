function LibcastXBlock(runtime, element, args) {
  'use strict';
  var require = require || RequireJS.require;
  require(['libcast'], function(libcast) {
    var video = $(element).find('video')[0];
    var player = libcast(video);

    // Load tracks
    // TODO
    //var tracks = player.textTracks();
    //for (var i = 0; i < tracks.length; i++) {
        //tracks[i].on('loaded', function() {
            //trackload[this.id()]=this.cues();
            //showCues(this.cues());
        //});
    //}

    // TODO
    //// Listen to events
    //var listenToTime = function(eventName, logEventName) {
      //player.on(event_name, function(){
          //log(logEventName, {'new_time': parseInt(player.currentTime())});
      //});
    //};
    //var listenTo = function(eventName, logEventName) {
      //player.on(event_name, function(){
          //log(logEventName);
      //});
    //};
    //function log(eventName, data) {
        //var logInfo = {
          //course_id: args.course_id,
          //video_id: args.video_id,
        //};
        //if (data) {
          //$.extend(logInfo, data);
        //}
        //Logger.log(eventName, logInfo);
    //}
    //listenToTime('seeked', 'seek_video');
    //listenToTime('ended', 'stop_video');
    //listenToTime('pause', 'pause_video');
    //listenToTime('play', 'play_video');
    //listenTo('loadstart', 'load_video');
  });
}
