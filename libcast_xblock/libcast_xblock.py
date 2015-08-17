"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

# TODO actually translate the app
from django.utils.translation import ugettext_lazy
# from django.utils.translation import ugettext as _

from xblock.core import XBlock
from xblock.fields import Boolean, Scope, String
from xblock.fragment import Fragment


class LibcastXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
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

    allow_download = Boolean(
        help=ugettext_lazy("Allow students to download this video."),
        display_name=ugettext_lazy("Video download allowed"),
        scope=Scope.settings,
        default=True
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the LibcastXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/libcast_xblock.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/libcast_xblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/libcast_xblock.js"))
        frag.initialize_js('LibcastXBlock')
        return frag
