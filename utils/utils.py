import copy
import datetime


class Utils:
    @staticmethod
    def format_data(value, params):
        if isinstance(value, str):
            return value.format(**params)
        return None

    @staticmethod
    def evaluate_data(value, params):
        locals().update(params)
        if isinstance(value, dict):
            for k, v in value.items():
                value[k] = eval(str(v))
        elif isinstance(value, str):
            value = eval(value)
        return value

    @staticmethod
    def datetime_serializer():
        return lambda obj: (
            obj.isoformat() if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date) else None)

    @staticmethod
    def convert_tuple_to_dict(headers, tuples):
        return [dict(zip(headers, row)) for row in tuples]

    @staticmethod
    def template_source_keys_mapping(response, keys_to_be_mapped):
        if not keys_to_be_mapped:
            return response

        results = []
        for data in response:
            locals().update(data)  # This will export the data packet for eval
            result = dict()
            for key_mapping in keys_to_be_mapped:
                result[key_mapping["destination"]] = eval(key_mapping['exp'])
            results.append(result)
        return results

    @staticmethod
    def render_template_for_consumers(data, consumers):
        result = dict()
        if not data:
            return result
        for key, value in consumers.items():
            attribute_template = value["attributes"] if value["attributes"] else dict()
            attributes = dict()
            if attribute_template:
                Utils.render_template(attribute_template, data, attributes)
            result[key] = copy.deepcopy(value)
            result[key]["attributes"] = attributes
        return result

    @classmethod
    def render_template(cls, template, data, response):
        for k, v in template.items():
            if isinstance(v, dict):
                response[k] = Utils.render_template(v, data, response.get('k', {}))
            else:
                response[k] = v.format(**data) if isinstance(v, str) else v
        return response
