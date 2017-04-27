function BokeccPlayer(runtime, element, args) {
    'use strict';
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

    function bookeecc_getSWF(swfID) {
        if (window.document[swfID]) {
            return window.document[swfID];
        } else if (navigator.appName.indexOf("Microsoft") == -1) {
            if (document.embeds && document.embeds[swfID]) {
                return document.embeds[swfID];
            }
        } else {
            return document.getElementById(swfID);
        }
    }
    // The on_cc_player_init is a callback from the flash plugin
    if (typeof window.on_cc_player_init == "undefined") {
        window.on_cc_player_init = function (vid, objectId) {
            var config = {};
            // define global event functions

            window['bokecc_on_ps_'+objectId] = function() {
                var player = bookeecc_getSWF(objectId);
                log('play_video',player.getPosition());
            }
            window['bokecc_on_sk_'+objectId] = function() {
                var player = bookeecc_getSWF(objectId);
                log('seek_video','new_time');
            }
            window['bokecc_on_sv_'+objectId] = function() {
                var player = bookeecc_getSWF(objectId);
                log('stop_video',player.getPosition());
            }
            window['bokecc_on_pv_'+objectId] = function() {
                var player = bookeecc_getSWF(objectId);
                log('pause_video',player.getPosition());
            }
            config.rightmenu_enable = 0;
            config.on_player_start = 'bokecc_on_ps_'+objectId;
            config.on_player_seek = 'bokecc_on_sk_'+objectId;
            config.on_player_stop = 'bokecc_on_sv_'+objectId;
            config.on_player_pause = 'bokecc_on_pv_'+objectId;
            config.on_player_resume = 'bokecc_on_ps_'+objectId;
            var player = bookeecc_getSWF(objectId)
            player.setConfig(config);
        }
    }

}
