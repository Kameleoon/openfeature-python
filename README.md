# Kameleoon OpenFeature provider for Python

The Kameleoon OpenFeature provider for Python allows you to connect your OpenFeature Python implementation to Kameleoon without installing the Python Kameleoon SDK.

> [!WARNING]
> This is a beta version. Breaking changes may be introduced before general release.

## Supported Python versions

This version of the SDK is built for the following targets:

* Python 3.8 and above.

## Get started

This section explains how to install, configure, and customize the Kameleoon OpenFeature provider.

### Install dependencies

First, install the required dependencies in your application.

* Run `pip install -r requirements.txt`

### Usage

The following example shows how to use the Kameleoon provider with the OpenFeature SDK.

```python
from openfeature import api
from openfeature.evaluation_context import EvaluationContext
from kameleoon_openfeature.kameleoon_provider import KameleoonProvider, KameleoonClientConfig


client_config = KameleoonClientConfig(
    'clientId',
    'clientSecret',
    top_level_domain='topLevelDomain'
)

provider = KameleoonProvider('siteCode', config=client_config)

api.set_provider(provider)
client = api.get_client()

values = {
    'variableKey': 'variableKey'
}

eval_context = EvaluationContext(attributes=values, targeting_key='visitorCode')

number_of_recommended_products = client.get_integer_value(flag_key='featureKey', default_value=5,
                                               evaluation_context=eval_context)

print(f"Number of recommended products: {number_of_recommended_products}")
```

#### Customize the Kameleoon provider

You can customize the Kameleoon provider by changing the `KameleoonClientConfig` object that you passed to the constructor above. For example:

```python
from kameleoon_openfeature.kameleoon_provider import KameleoonProvider, KameleoonClientConfig

client_config = KameleoonClientConfig(
    'clientId',
    'clientSecret',
    top_level_domain='topLevelDomain',
    refresh_interval_minute=1,    # Optional field
    session_duration_minute=5,    # Optional field
)

provider = KameleoonProvider('siteCode', config=client_config)
```
> [!NOTE]
> For additional configuration options, see the [Kameleoon documentation](https://developers.kameleoon.com/feature-management-and-experimentation/web-sdks/python-sdk/#example-code).

## EvaluationContext and Kameleoon Data

Kameleoon uses the concept of associating `Data` to users, while the OpenFeature SDK uses the concept of an `EvaluationContext`, which is a dictionary of string keys and values. The Kameleoon provider maps the `EvaluationContext` to the Kameleoon `Data`.

> [!NOTE]
> To get the evaluation for a specific visitor, set the `targeting_key` value for the `EvaluationContext` to the visitor code (user ID). If the value is not provided, then the `defaultValue` parameter will be returned.

```python
from openfeature.evaluation_context import EvaluationContext

eval_context = EvaluationContext(targeting_key='userId')
```

The Kameleoon provider provides a few predefined parameters that you can use to target a visitor from a specific audience and track each conversion. These are:

| Parameter               | Description                                                                                                                                                             |
|-------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Data.Type.CUSTOM_DATA` | The parameter is used to set [`CustomData`](https://developers.kameleoon.com/feature-management-and-experimentation/web-sdks/python-sdk/#customdata) for a visitor.     |
| `Data.Type.CONVERSION`  | The parameter is used to track a [`Conversion`](https://developers.kameleoon.com/feature-management-and-experimentation/web-sdks/python-sdk/#conversion) for a visitor. |

### Data.Type.CUSTOM_DATA

Use `Data.Type.CUSTOM_DATA` to set [`CustomData`](https://developers.kameleoon.com/feature-management-and-experimentation/web-sdks/python-sdk/#customdata) for a visitor. The `Data.Type.CUSTOM_DATA` field has the following parameters:

| Parameter                    | Type | Description                                                       |
|------------------------------|------|-------------------------------------------------------------------|
| `Data.CustomDataType.INDEX`  | int  | Index or ID of the custom data to store. This field is mandatory. |
| `Data.CustomDataType.VALUES` | str  | Value of the custom data to store. This field is mandatory.       |

#### Example

```python
from openfeature.evaluation_context import EvaluationContext
from kameleoon_openfeature.types import Data

custom_data_dictionary = {
    Data.Type.CUSTOM_DATA: {
        Data.CustomDataType.INDEX: 1,
        Data.CustomDataType.VALUES: '10'
    }
}

eval_context = EvaluationContext(attributes=custom_data_dictionary , targeting_key='userId')
```

### Data.Type.CONVERSION

Use `Data.Type.CONVERSION` to track a [`Conversion`](https://developers.kameleoon.com/feature-management-and-experimentation/web-sdks/python-sdk/#conversion) for a visitor. The `Data.Type.CONVERSION` field has the following parameters:

| Parameter                     | Type  | Description                                                     |
|-------------------------------|-------|-----------------------------------------------------------------|
| `Data.ConversionType.GOAL_ID` | int   | Identifier of the goal. This field is mandatory.                |
| `Data.ConversionType.REVENUE` | float | Revenue associated with the conversion. This field is optional. |

#### Example

```python
from openfeature.evaluation_context import EvaluationContext
from kameleoon_openfeature.types import Data

conversion_dictionary = {
    Data.Type.CONVERSION: {
        Data.ConversionType.GOAL_ID: 1,
        Data.ConversionType.REVENUE: 200
    }
}

eval_context = EvaluationContext(attributes=conversion_dictionary, targeting_key='userId')
```

### Use multiple Kameleoon Data types

You can provide many different kinds of Kameleoon data within a single `EvaluationContext` instance.

For example, the following code provides one `Data.Type.CONVERSION` instance and two `Data.Type.CUSTOM_DATA` instances.

```python
from openfeature.evaluation_context import EvaluationContext
from kameleoon_openfeature.types import Data

data_dictionary = {
    Data.Type.CONVERSION: {
        Data.ConversionType.GOAL_ID: 1,
        Data.ConversionType.REVENUE: 200
    },
    Data.Type.CUSTOM_DATA: [
        {
            Data.CustomDataType.INDEX: 1,
            Data.CustomDataType.VALUES: ['10', '30']
        },
        {
            Data.CustomDataType.INDEX: 2,
            Data.CustomDataType.VALUES: '20'
        }
    ]
}

eval_context = EvaluationContext(attributes=data_dictionary, targeting_key='userId')
```
