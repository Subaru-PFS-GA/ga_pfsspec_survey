from pfs.ga.pfsspec.survey.pfs.io import PfsSurveyDownloader

DOWNLOAD_CONFIGURATIONS = {
    'survey': {
        'pfs': {
            'type': PfsSurveyDownloader
        },
    }
}

IMPORT_CONFIGURATIONS = {
#     'survey': {
#         'segue': SdssSegueSurveyReader
}

TRAIN_CONFIGURATIONS = {
    # 'reg': {
    #     'sdss': {
    #         'augmenter': SdssAugmenter
    #     },
    # },
}