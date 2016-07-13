var player;
function YoutubePlayer(runtime, element, args) {
    'use strict';

    // Insert youtube script
    // We need to do this even if the script was already inserted, in order to
    // handle multiple video xblocks in the same page.
    var tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    var firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

    // This function gets called after the youtube script was inserted
    window.onYouTubeIframeAPIReady = function() {
        var onPlayerReady = function(e) {
            log('video_player_ready');
        };

        var onPlayerStateChanged = function(e) {
            // Note that there is no event for seeking in the video
            if (e.data == YT.PlayerState.UNSTARTED) {
                log('load_video');
            } else if (e.data == YT.PlayerState.ENDED) {
                log('stop_video');
            } else if (e.data == YT.PlayerState.PLAYING) {
                log('play_video', {currentTime: player.getCurrentTime()});
            } else if (e.data == YT.PlayerState.PAUSED) {
                log('pause_video', {currentTime: player.getCurrentTime()});
            } else if (e.data == YT.PlayerState.BUFFERING) {
            } else if (e.data == YT.PlayerState.CUED) {
            }
        };

        player = new YT.Player(args.element_id, {
           events: {
               'onReady': onPlayerReady,
               'onStateChange': onPlayerStateChanged
           }
        });
    };

    // Event logging
    function log(eventName, data) {
        var logInfo = {
          course_id: args.course_id,
          video_id: args.video_id,
        };
        if (data) {
          $.extend(logInfo, data);
        }
        Logger.log(eventName, logInfo);
    }
}
