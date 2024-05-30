from ...io.surveyreader import SurveyReader

class PfsSurverReader(SurveyReader):
    def __init__(self, orig=None):
        super().__init__(orig=orig)

        if not isinstance(orig, PfsSurverReader):
            self.token = None
        else:
            self.token = orig.token

    def add_args(self, parser, config):
        super().add_args(parser, config)

    def init_from_args(self, config, args):
        super().init_from_args(config, args)