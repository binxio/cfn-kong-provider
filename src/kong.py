import os
import logging
import cfn_kong_api_provider
import cfn_kong_plugin_provider
import cfn_kong_consumer_provider

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))


def handler(request, context):
    if request['ResourceType'] == 'Custom::KongAPI':
        return cfn_kong_api_provider.handler(request, context)
    elif request['ResourceType'] == 'Custom::KongPlugin':
        return cfn_kong_plugin_provider.handler(request, context)
    else:
        return cfn_kong_consumer_provider.handler(request, context)
