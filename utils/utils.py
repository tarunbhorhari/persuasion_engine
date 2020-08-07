import datetime


class Utils:
    @staticmethod
    def query_builder(query, query_param, source):
        if source in ["es", "mysql"]:
            return query.format(**query_param)
        return None

    @staticmethod
    def initialize_mapping(value, data):
        locals().update(data)
        for k, v in value.items():
            value[k] = eval(str(v))

    @staticmethod
    def datetime_serializer():
        return lambda obj: (
            obj.isoformat() if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date) else None)

    @staticmethod
    def convert_tuple_to_dict(headers, tuples):
        results = []
        for row in tuples:
            results.append(dict(zip(headers, row)))
        return results

    @staticmethod
    def template_source_keys_mapping(response, keys_to_be_mapped):
        results = []
        for data in response:
            locals().update(data)  # This will export the data packet for eval
            result = dict()
            # TODO - if keys to be mapped is empty
            for key_mapping in keys_to_be_mapped:
                result[key_mapping["destination"]] = eval(key_mapping['exp'])
            results.append(result)
        return results

    @staticmethod
    def render_template_for_wf_consumers(data, consumers):
        result = dict()
        for key, value in consumers.items():
            attribute_template = value["attributes"][0] if value["attributes"] else dict()
            attributes = []
            if attribute_template:
                for row_data in data:
                    attribute = dict()
                    Utils.update_data_dynamically(attribute_template, row_data, attribute)
                    attributes.append(attribute)
            value["attributes"] = attributes
            result[key] = value
        return result

    @classmethod
    def update_data_dynamically(cls, attribute_template, data, attribute):
        for k, v in attribute_template.items():
            if isinstance(v, dict):
                attribute[k] = Utils.update_data_dynamically(v, data, attribute.get('k', {}))
            else:
                attribute[k] = v.format(**data) if isinstance(v, str) else v
        return attribute
