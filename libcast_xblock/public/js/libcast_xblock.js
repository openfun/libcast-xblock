function LibcastXBlock(runtime, element, args) {
  'use strict';
  var require = require || RequireJS.require;
  require(['libcast'], function(libcast) {

    var videoPlayerElement = $(element).find('.videoplayer');
    var transcriptElement = videoPlayerElement.find(".transcript");
    var player = libcast(videoPlayerElement.find('video')[0]);

    // Configure transcripts
    player.one('loadedmetadata', function() {
      var tracks = player.textTracks();

      // Change track
      tracks.addEventListener('change', function() {

        var enableTranscript = false;
        for (var t = 0; t < this.length; t++) {
          var track = this[t];
          if (track.mode === 'showing') {
            showTranscript(track);
            enableTranscript = true;
          }
        }
        if (!enableTranscript) {
          disableTranscript();
        }
      });

      // Highlight current cue
      // TODO
      for (var t = 0; t < tracks.length; t++) {
        tracks[t].addEventListener('cuechange', oncuechange);
      }
    });

    var showTranscript = function(track) {
      var cues = track.cues;

      // We need to check whether the track is still the one currently showing.
      if (track.mode !== "showing") {
        return;
      }

      // Cues may not be loaded yet. If not, wait until they are. This is
      // suboptimal, but there is no other event to help us determine whether a
      // track was correctly loaded.
      if (!cues || cues.length === 0) {
        window.setTimeout(function() { showTranscript(track); }, 2);
      }

      var htmlContent = "";
      for (var c = 0; c < cues.length; c++) {
        var cue = cues[c];
        htmlContent += "<span class='cue' begin='" + cue.startTime + "'>&nbsp;-&nbsp;" + cue.text + "</span><br/>\n";
      }

      player.width("61%");
      videoPlayerElement.addClass("transcript-enabled");
      transcriptElement.html(htmlContent);

      // Go to time on cue click
      transcriptElement.find(".cue").click(function() {
          player.currentTime($(this).attr('begin'));
      });
    };

    var disableTranscript = function() {
      videoPlayerElement.removeClass("transcript-enabled");
      player.width("100%");
    };

    var oncuechange = function() {
      transcriptElement.find(".current.cue").removeClass("current");
      var cueElement;
      for (var c = 0; c < this.activeCues.length; c++) {
        cueElement = transcriptElement.find(".cue[begin='" + this.activeCues[c].startTime + "']");
        cueElement.addClass("current");
      }
      if (cueElement) {
        // Scroll to cue
        var newtop = transcriptElement.scrollTop() - transcriptElement.offset().top + cueElement.offset().top;
        transcriptElement.animate({
            scrollTop: newtop
        }, 500);
      }
    };

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
