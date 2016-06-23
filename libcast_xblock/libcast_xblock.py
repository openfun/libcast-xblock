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
        default=ugettext_lazy("New video"),
        scope=Scope.settings
    )

    # The video ID is actually the resource ID, as defined by the libcast API
    video_id = String(
        scope=Scope.settings,
        help=ugettext_lazy('Fill this with the ID of the video found in the video uploads dashboard'),
        default="",
        display_name=ugettext_lazy('Video ID')
    )

    is_youtube_video = Boolean(
        help=ugettext_lazy("Is this video stored on youtube?"),
        display_name=ugettext_lazy("Youtube video"),
        scope=Scope.settings,
        default=False
    )

    allow_download = Boolean(
        help=ugettext_lazy("Allow students to download this video."),
        display_name=ugettext_lazy("Video download allowed"),
        scope=Scope.settings,
        default=True
    )

    editable_fields = ('display_name', 'video_id', 'is_youtube_video', 'allow_download', )


    def __init__(self, *args, **kwargs):
        super(LibcastXBlock, self).__init__(*args, **kwargs)

    @property
    def course_key_string(self):
        return unicode(self.location.course_key)

    @property
    def resource_slug(self):
        return None if self.video_id is None else self.video_id.strip()

    def transcript_root_url(self):
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
        if not subtitle_id or not self.resource_slug:
            return webob.Response(status=404)
        caps = libcast.get_vtt_content(self.course_key_string, self.resource_slug, subtitle_id) or ""
        return webob.Response(caps, content_type='text/vtt')

    def get_icon_class(self):
        """CSS class to be used in courseware sequence list."""
        return 'video'

    def student_view(self, context=None):
        fragment = Fragment()
        if self.is_youtube_video:
            self.get_youtube_content(fragment)
        else:
            self.get_libcast_content(fragment)
        return fragment

    def get_libcast_content(self, fragment):
        template_content = self.resource_string("public/html/libcast.html")
        template = Template(template_content)
        messages = []# tuple list
        context = {
            'display_name': self.display_name,
            'video_id': self.resource_slug,
            'transcript_root_url': self.transcript_root_url(),
            'messages': messages,
            'resource': {}, # To be provided by libcast
        }
        if not self.resource_slug:
            messages.append(('warning', ugettext_lazy(
                "You need to define a valid video ID. "
                "Video IDs for your course can be found in the video upload"
                " dashboard."
            )))
        else:
            try:
                context['resource'] = libcast.get_cached_resource_dict(self.course_key_string, self.resource_slug)
                if not self.allow_download:
                    context['resource'].pop('downloadable_files')
            except libcast.MissingCredentials as e:
                messages.append(('error', e.verbose_message))
            except libcast.ClientError as e:
                # Note that we may not log an exception here, because unicode
                # messages cannot be encoded by the logger
                logger.error(e.message)
                messages.append(('error', ugettext_lazy("An unexpected error occurred.")))

        content = template.render(Context(context))
        fragment.add_content(content)

        fragment.add_css(self.resource_string("public/css/style.css"))
        # This hack requires us to hardcode the url to the css file.
        # see no other way to proceed.  Loading static files directly from
        # fun-apps/edx-platform is unconventional. It would be great to find a
        # workaround.
        fragment.add_css_url("/static/fun/js/vendor/videojs/video-js.min.css")
        fragment.add_javascript(self.resource_string("public/js/libcast_xblock.js"))

        fragment.initialize_js("LibcastXBlock", json_args={
            'course_id': self.course_key_string,
            'video_id': self.resource_slug,
        })

    def get_youtube_content(self, fragment):
        template_content = self.resource_string("public/html/youtube.html")
        template = Template(template_content)
        context = {
            'display_name': self.display_name,
            'video_id': self.resource_slug,
        }
        content = template.render(Context(context))
        fragment.add_content(content)

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")
