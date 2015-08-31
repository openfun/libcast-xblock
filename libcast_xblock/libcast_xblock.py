"""XBlock for videos stored by Libcast."""

import logging
import pkg_resources
import webob

from django.template import Context, Template
# TODO actually translate the app
from django.utils.translation import ugettext_lazy
# from django.utils.translation import ugettext as _

from xblock.core import XBlock
from xblock.fields import Boolean, Scope, String
from xblock.fragment import Fragment
from xblockutils.studio_editable import StudioEditableXBlockMixin

from videoproviders.api import libcast
import videoproviders.subtitles


logger = logging.getLogger(__name__)


class LibcastXBlock(StudioEditableXBlockMixin, XBlock):
    """
    Play videos based on a modified videojs player. This XBlock supports
    subtitles and multiple resolutions.
    """
    display_name = String(
        help=ugettext_lazy("The name students see. This name appears in "
                           "the course ribbon and as a header for the video."),
        display_name=ugettext_lazy("Component Display Name"),
        default=ugettext_lazy("Libcast video"),
        scope=Scope.settings
    )

    # The video ID is actually the resource ID, as defined by the libcast API
    video_id = String(
        scope=Scope.settings,
        help=ugettext_lazy('Fill this with the ID of the video found in the video uploads dashboard'),
        default="",
        display_name=ugettext_lazy('Video ID')
    )

    allow_download = Boolean(
        help=ugettext_lazy("Allow students to download this video."),
        display_name=ugettext_lazy("Video download allowed"),
        scope=Scope.settings,
        default=True
    )

    editable_fields = ('video_id',)


    def __init__(self, *args, **kwargs):
        super(LibcastXBlock, self).__init__(*args, **kwargs)
        self._libcast_client = None

    @property
    def libcast_client(self):
        if self._libcast_client is None:
            try:
                self._libcast_client = libcast.Client(self.course_key_string)
            except (libcast.ClientError, libcast.MissingCredentials) as e:
                logger.exception(e)
                return libcast.Client("")
        return self._libcast_client

    @property
    def course_key_string(self):
        return unicode(self.location.course_key)

    def video_sources(self):
        if not self.video_id:
            return []
        return self.libcast_client.video_sources(self.video_id)

    def downloadable_files(self):
        if not self.video_id:
            return []
        return self.libcast_client.downloadable_files(self.video_id)

    def thumbnail_url(self):
        if not self.video_id:
            return ""
        return self.libcast_client.urls.thumbnail_url(self.video_id)

    def subtitles(self):
        if not self.video_id:
            return []
        try:
            return self.libcast_client.get_video_subtitles(self.video_id)
        except (libcast.ClientError, libcast.MissingCredentials) as e:
            logger.exception(e)
            return []

    def track_src(self):
        url = self.runtime.handler_url(self, 'transcript')
        # url is suffixed with '?' in preview mode
        return url.strip('?')

    @XBlock.handler
    def transcript(self, request, dispatch):
        """
        Proxy view for downloading subtitle files

        <track> elements that point to external resources are not supported by
        Chrome: https://code.google.com/p/chromium/issues/detail?id=472300
        As a consequence, we need to download the subtitle file server-side.

        Because srt subtitles are unsupported by Chrome, we need to convert
        them to vtt format.
        """
        subtitle_id = request.GET.get('id')
        if subtitle_id and self.video_id:
            url = self.libcast_client.urls.subtitle_href(self.video_id, subtitle_id)
            caps = videoproviders.subtitles.get_vtt_content(url) or ""
            return webob.Response(caps, content_type='text/vtt')
        return webob.Response(status=404)


    def student_view(self, context=None):
        fragment = self.get_content()
        fragment.initialize_js("LibcastXBlock", json_args={
            'course_id': self.course_key_string,
            'video_id': self.video_id,
        })
        return fragment

    def get_content(self):
        fragment = Fragment()
        template_content = self.resource_string("public/html/video.html")
        template = Template(template_content)
        content = template.render(Context({"self": self}))
        fragment.add_content(content)

        fragment.add_css(self.resource_string("public/css/style.css"))
        # This hack requires us to hardcode the url to the css file.
        # see no other way to proceed.  Loading static files directly from
        # fun-apps/edx-platform is unconventional. It would be great to find a
        # workaround.
        fragment.add_css_url("/static/fun/js/vendor/videojs/video-js.min.css")
        fragment.add_javascript(self.resource_string("public/js/libcast_xblock.js"))

        return fragment

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")
