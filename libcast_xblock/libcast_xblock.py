"""XBlock for videos stored by Youtube."""

import logging
import random
import string

import pkg_resources

from django.template import Context, Template
from django.contrib.staticfiles.storage import staticfiles_storage
# TODO actually translate the app
from django.utils.translation import ugettext_lazy
# from django.utils.translation import ugettext as _
import webob

from xblock.core import XBlock
from xblock.fields import Boolean, Scope, String
from xblock.fragment import Fragment
from xblockutils.studio_editable import StudioEditableXBlockMixin


logger = logging.getLogger(__name__)


@XBlock.needs('settings')
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

    video_id = String(
        scope=Scope.settings,
        help=ugettext_lazy('Fill this with the ID of the video found in the video uploads dashboard'),
        default="",
        display_name=ugettext_lazy('Video ID')
    )

    is_youtube_video = Boolean(
        help=ugettext_lazy("Is this video stored on Youtube?"),
        display_name=ugettext_lazy("Video storage"),
        scope=Scope.settings,
        default=False # Stored on Videofront by default
    )

    allow_download = Boolean(
        help=ugettext_lazy("Allow students to download this video."),
        display_name=ugettext_lazy("Video download allowed"),
        scope=Scope.settings,
        default=True
    )

    adways_id = String(
        scope=Scope.settings,
        help=ugettext_lazy(""),
        default="",
        display_name=ugettext_lazy('Adways ID')
    )


    editable_fields = ('display_name', 'video_id', 'adways_id', 'is_youtube_video', 'allow_download', )

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
        IE11 and Microsoft Edge:
        http://stackoverflow.com/questions/35138642/ms-edge-video-cross-origin-subtitles-fail
        As a consequence, we need to download the subtitle file server-side.
        """
        from videoproviders.subtitles import get_vtt_content

        subtitle_url = request.GET.get('url')
        if not subtitle_url:
            return webob.Response(status=404)
        caps = get_vtt_content(subtitle_url) or ""
        return webob.Response(caps, content_type='text/vtt')

    def get_icon_class(self):
        """CSS class to be used in courseware sequence list."""
        return 'video'

    def is_studio(self):
        studio = False
        try:
            studio = self.runtime.is_author_mode
        except AttributeError:
            pass
        return studio

    def student_view(self, context=None):
        fragment = Fragment()
        if self.is_youtube_video and self.video_id:
            self.get_youtube_content(fragment)
        else:
            self.get_videofront_content(fragment)
        return fragment

    def get_videofront_content(self, fragment):
        from videoproviders.api import videofront

        template_content = self.resource_string("public/html/videofront.html")
        template = Template(template_content)
        messages = []# tuple list
        context = {
            'display_name': self.display_name,
            'video_id': self.resource_slug,
            'messages': messages,
            'allow_download': self.allow_download,
            'downloads': [],
            'sources': [],
            'subtitles': [],
            'thumbnail_url': '',
            'transcript_root_url': self.transcript_root_url(),
        }
        if self.resource_slug:
            try:
                videofront_client = videofront.Client(self.course_key_string)
                video = videofront_client.get_video_with_subtitles(self.resource_slug)
                context['subtitles'] = video['subtitles']
                context['thumbnail_url'] = video['thumbnail_url']

                # Sort video sources by decreasing resolution
                video_sources = sorted(video['video_sources'], key=lambda s: -s['res'])

                # Streaming sources
                source_labels = {
                    'HD': '1080p',
                    'SD': '720p',
                    'LD': '480p',
                }
                context['sources'] = [
                    {
                        'url': source['url'],
                        'label': source_labels.get(source['label'], source['label']),
                        'res': source['res'],
                    }
                    for source in video_sources
                ]

                # Download links
                download_labels = {
                    'HD': 'Haute (1080p)',
                    'SD': 'Normale (720p)',
                    'LD': 'Mobile (480p)',
                }
                context['downloads'] = [
                    {
                        'url': source['url'],
                        'label': download_labels.get(source['label'], source['label'])
                    }
                    for source in video_sources
                ]

            except videofront.MissingCredentials as e:
                messages.append(('error', e.verbose_message))
            except videofront.ClientError as e:
                # Note that we may not log an exception here, because unicode
                # messages cannot be encoded by the logger
                logger.error(e.message)
                messages.append(('error', ugettext_lazy("An unexpected error occurred.")))
        else:
            messages.append(('warning', ugettext_lazy(
                "You need to define a valid video ID. "
                "Video IDs for your course can be found in the video upload"
                " dashboard."
            )))

        content = template.render(Context(context))
        fragment.add_content(content)

        fragment.add_css(self.resource_string("public/css/style.css"))
        # Load video-js stylesheet from FUN; if this becomes a problem, we can
        # always copy the stylesheet to the xblock.
        fragment.add_css_url(staticfiles_storage.url("fun/js/vendor/videojs/video-js.min.css"))
        fragment.add_javascript(self.resource_string("public/js/videofront.js"))

        fragment.initialize_js("VideoXBlock", json_args={
            'course_id': self.course_key_string,
            'video_id': self.resource_slug,
            'adways_id': self.adways_id,
        })

    def get_youtube_content(self, fragment):
        # iframe element id
        element_id = ''.join([random.choice(string.ascii_lowercase) for _ in range(0, 20)])

        # Add html code
        template_content = self.resource_string("public/html/youtube.html")
        template = Template(template_content)
        context = {
            'display_name': self.display_name,
            'video_id': self.resource_slug,
            'element_id': element_id
        }
        content = template.render(Context(context))
        fragment.add_content(content)

        # Add youtube event logger
        fragment.add_javascript(self.resource_string("public/js/youtube.js"))
        fragment.initialize_js("YoutubePlayer", json_args={
            'course_id': self.course_key_string,
            'video_id': self.resource_slug,
            'element_id': element_id
        })

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")
