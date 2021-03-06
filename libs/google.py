import gspread
from oauth2client.service_account import ServiceAccountCredentials

INPUT_OPTION = 'USER_ENTERED'
SCOPES = ['https://spreadsheets.google.com/feeds']


class Sheet:

    def __init__(self, service_account_file: str, spreadsheet_id):

        creds = ServiceAccountCredentials\
            .from_json_keyfile_name(service_account_file, SCOPES)

        client = gspread.authorize(creds)

        self.spreadsheet = client.open_by_key(spreadsheet_id)

    @property
    def worksheets(self):

        return self.spreadsheet.worksheets()

    def create_worksheet(self, name):

        worksheet = self.spreadsheet.add_worksheet(name, rows=100, cols=4)
        worksheet_id = worksheet.id
        headers = ['Author', 'Phrase', 'Url']

        request_body = {
            'requests': [
                {
                    # set font's family and size
                    'repeatCell': {
                        'range': {
                            'sheetId': worksheet_id
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'textFormat': {
                                    'fontFamily': 'Calibri',
                                    'fontSize': 10
                                }
                            }
                        },
                        'fields': 'userEnteredFormat.textFormat'
                    }
                },
                {
                    # freeze first row
                    'updateSheetProperties': {
                        'properties': {
                            'sheetId': worksheet_id,
                            'gridProperties': {
                                'frozenRowCount': 1
                            }
                        },
                        'fields': 'gridProperties.frozenRowCount'
                    }
                },
                {
                    # set Author column's width
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': worksheet_id,
                            'dimension': 'COLUMNS',
                            'endIndex': 1
                        },
                        'properties': {
                            'pixelSize': 270
                        },
                        'fields': 'pixelSize'
                    }
                },
                {
                    # set Phrase column's width
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': worksheet_id,
                            'dimension': 'COLUMNS',
                            'startIndex': 1,
                            'endIndex': 2
                        },
                        'properties': {
                            'pixelSize': 850
                        },
                        'fields': 'pixelSize'
                    }
                },
                {
                    # set URL column's width
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': worksheet_id,
                            'dimension': 'COLUMNS',
                            'startIndex': 2,
                            'endIndex': 3
                        },
                        'properties': {
                            'pixelSize': 370
                        },
                        'fields': 'pixelSize'
                    }
                },
                {
                    # set last scraped id column's width
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': worksheet_id,
                            'dimension': 'COLUMNS',
                            'startIndex': 3,
                        },
                        'properties': {
                            'pixelSize': 200
                        },
                        'fields': 'pixelSize'
                    }
                }
            ]
        }

        self.spreadsheet.batch_update(body=request_body)
        self._call_func(self.spreadsheet.values_append, name, [headers])

        return worksheet

    def get_values(self, range_):

        values = self.spreadsheet.values_get(range_).get('values')
        values = [] if values is None else values

        for [value] in values:
            yield value

    def append(self, range_, request_body):

        self._call_func(self.spreadsheet.values_append, range_, request_body)

    def update(self, range_, request_body):

        self._call_func(self.spreadsheet.values_update, range_, request_body)

    def _call_func(self, spreadsheet_func, *args):

        range_, request_body = args

        spreadsheet_func(
            range_,
            params={'valueInputOption': INPUT_OPTION},
            body={'values': request_body})

    def sort(self, worksheet_name, column=0, order='ASCENDING'):
        """Sort values of the given worksheet name.

        Args:
            worksheet_name: The worksheet's name.
            column: The column where the sort should be applied to.
            order: The order of values on sort, supported orderings are:
                - ASCENDING
                - DESCENDING
        """

        worksheet_id = self.spreadsheet.worksheet(worksheet_name).id

        request_body = {
            'requests': [{
                'sortRange': {
                    'range': {
                        'sheetId': worksheet_id,
                        'startRowIndex': 1  # exclude headers
                    },
                    'sortSpecs': [
                        {
                            'dimensionIndex': column,
                            'sortOrder': order
                        }
                    ]
                }
            }]
        }

        self.spreadsheet.batch_update(body=request_body)
