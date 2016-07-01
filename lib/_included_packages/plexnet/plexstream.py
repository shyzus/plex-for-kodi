import plexobjects


class PlexStream(plexobjects.PlexObject):
    # Constants
    TYPE_UNKNOWN = 0
    TYPE_VIDEO = 1
    TYPE_AUDIO = 2
    TYPE_SUBTITLE = 3
    TYPE_LYRICS = 4

    # We have limited font support, so make a very modest effort at using
    # English names for common unsupported languages.

    SAFE_LANGUAGE_NAMES = {
        'ara': "Arabic",
        'arm': "Armenian",
        'bel': "Belarusian",
        'ben': "Bengali",
        'bul': "Bulgarian",
        'chi': "Chinese",
        'cze': "Czech",
        'gre': "Greek",
        'heb': "Hebrew",
        'hin': "Hindi",
        'jpn': "Japanese",
        'kor': "Korean",
        'rus': "Russian",
        'srp': "Serbian",
        'tha': "Thai",
        'ukr': "Ukrainian",
        'yid': "Yiddish"
    }

    def reload(self):
        pass

    def getTitle(self):
        title = self.getLanguageName()
        streamType = self.streamType.asInt()

        if streamType == self.TYPE_VIDEO:
            title = self.getCodec() or "Unknown"
        elif streamType == self.TYPE_AUDIO:
            codec = self.getCodec()
            channels = self.getChannels()

            if codec != "" and channels != "":
                title += " ({0} {1})".format(codec, channels)
            elif codec != "" or channels != "":
                title += " ({0}{1})".format(codec, channels)
        elif streamType == self.TYPE_SUBTITLE:
            extras = []

            codec = self.getCodec()
            if codec:
                extras.append(codec)

            if not self.key:
                extras.append("Embedded")

            if self.forced.asBool():
                extras.append("Forced")

            if len(extras) > 0:
                title += " ({0})".format('/'.join(extras))
        elif streamType == self.TYPE_LYRICS:
            title = "Lyrics"
            if self.format:
                title += " ({0})".format(self.format)

        return title

    def getCodec(self):
        codec = self.codec or ''

        if codec == "dca":
            codec = "DTS"
        else:
            codec = codec.upper()

        return codec

    def getChannels(self):
        channels = self.channels.asInt()

        if channels == 1:
            return "Mono"
        elif channels == 2:
            return "Stereo"
        elif channels > 0:
            return "{0}.1".format(channels - 1)
        else:
            return ""

    def getLanguageName(self):
        code = self.languageCode

        if not code:
            return "Unknown"

        return self.SAFE_LANGUAGE_NAMES.get(code) or self.language or "Unknown"

    def getSubtitlePath(self):
        query = "?encoding=utf-8"

        if self.codec == "smi":
            query += "&format=srt"

        return self.key + query

    def isSelected(self):
        return self.selected.asInt() == 1

    def setSelected(self, selected):
        self.selected = plexobjects.PlexValue(selected and '1' or '0')

    def __str__(self):
        return self.getTitle()

    def __eq__(self, other):
        if not other:
            return False

        if self.__class__ != other.__class__:
            return False

        for attr in ("streamType", "language", "codec", "channels", "index"):
            if getattr(self, attr) != getattr(other, attr):
                return False


# Synthetic subtitle stream for 'none'

class NoneStream(PlexStream):
    def __init__(self, *args, **kwargs):
        PlexStream.__init__(self, None, *args, **kwargs)
        self.id = plexobjects.PlexValue("0")
        self.streamType = plexobjects.PlexValue(str(self.TYPE_SUBTITLE))

    def getTitle(self):
        return "None"