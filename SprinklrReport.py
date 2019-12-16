class ReportBuilder:
    def __init__(self):
        self.engine = None
        self.name = None
        self.page = 0
        self.start_time = None  # Unix time in ms
        self.end_time = None    # Unix time in ms
        self.time_zone = None   # UTC is default
        self.page_size = 10     # Rows to be returned per call - default is 10, max is 2000
        self.page = 0           # page to request - default is 0 (first)
        self.projections = []
        self.group_bys = []
        self.group_by_projections = []
        self.group_by_sorts = []
        self.group_by_filters = []
        self.columns = []
        self.request = None
        self.filters = []
        self.projection_decorations = []
        self.last_error = None

    def set_engine(self, engine_name):
        if engine_name.upper() in {"AD", "PLATFORM", "INBOUND_MESSAGE", "LISTENING"}:
            self.engine = engine_name.upper()
            return True
        else:
            return False

    def set_name(self, name):
        self.name = name
        return True

    def set_page(self, page):
        if page > 0:
            self.page = page
            return True
        else:
            self.page = 0
            return False

    def set_start_time(self, start_time):
        self.start_time = start_time
        return True

    def set_end_time(self, end_time):
        self.end_time = end_time
        return True

    def set_time_zone(self, time_zone):
        self.time_zone = time_zone
        return True

    def set_page_size(self, page_size):
        self.page_size = page_size
        return True

    # {"heading": "HIERARCHY_PATH", "dimensionName": "HIERARCHY_PATH", "groupType": "FIELD", "details": {}
    # Valid group_types: DATE_HISTOGRAM, TIME_OF_DAY, DAY_OF_WEEK, MONTH_OF_YEAR, FIELD

    def add_group_by(self, heading, dimension_name, group_type, details=None):
        self.group_bys.append({
            "heading": heading,
            "dimensionName": dimension_name,
            "groupType": group_type,
            "details": details,
            })


    # {"filterType": "IN", "dimensionName": "HIERARCHY_ID", "values": ["5c3db128e4b0dcecf6fa1c73"], "details": {}}
    # based on report_engine, different filter_types are valid.
    # for PLATFORM and INBOUND_MESSAGE, the following are valid:
    #    IN, GT, GTE, LT, LTE, NIN, BETWEEN, STARTS_WITH, CONTAINS, EQUALS , FILTER, EXISTS
    def add_filter(self, filter_type, dimension_name, values, details=None):
        self.filters.append({
            "filterType": filter_type,
            "dimensionName": dimension_name,
            "values": values,
            "details": details
        })

    # {"heading": "MENTIONS_COUNT", "measurementName": "MENTIONS_COUNT", "aggregateFunction": "SUM" }
    # Valid aggregate_function parameters: SUM, AVG, MIN, MAX, STATS
    def add_column(self, heading, measurement_name, aggregate_function, details=None):
        self.columns.append({
            "heading": heading,
            "measurementName": measurement_name,
            "aggregateFunction": aggregate_function,
            "details": details
        })
    
    def build_report_request(self):
        try:
            self.request = {
                "reportingEngine": self.engine,
                "report": self.name,
                "startTime": self.start_time,
                "endTime": self.end_time,
                "timeZone": self.time_zone,
                "page": self.page,
                "pageSize": self.page_size,
                "groupBys": self.group_bys,
                "filters": self.filters,
                "projections": self.columns,
                }
        except ValueError as ex:
            self.last_error = ex
            return False

        return True