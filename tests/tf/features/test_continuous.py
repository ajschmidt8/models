#
# Copyright (c) 2021, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pytest

from merlin_models.data.synthetic import SyntheticData
from merlin_standard_lib import Tag

ml = pytest.importorskip("merlin_models.tf")
test_utils = pytest.importorskip("merlin_models.tf.utils.testing_utils")


def test_continuous_features(tf_con_features):
    features = ["a", "b"]
    con = ml.ContinuousFeatures(features)(tf_con_features)

    assert list(con.keys()) == features


def test_continuous_features_yoochoose(testing_data: SyntheticData):
    schema = testing_data.schema.select_by_tag(Tag.CONTINUOUS)

    inputs = ml.ContinuousFeatures.from_schema(schema)
    outputs = inputs(testing_data.tf_tensor_dict)

    assert sorted(list(outputs.keys())) == sorted(schema.column_names)


def test_serialization_continuous_features(testing_data: SyntheticData):
    inputs = ml.ContinuousFeatures.from_schema(testing_data.schema)

    copy_layer = test_utils.assert_serialization(inputs)

    assert inputs.filter_features.feature_names == copy_layer.filter_features.feature_names


@pytest.mark.parametrize("run_eagerly", [True, False])
def test_continuous_features_yoochoose_model(testing_data: SyntheticData, run_eagerly):
    schema = testing_data.schema.select_by_tag(Tag.CONTINUOUS)

    inputs = ml.ContinuousFeatures.from_schema(schema, aggregation="concat")
    body = ml.SequentialBlock([inputs, ml.MLPBlock([64])])

    test_utils.assert_body_works_in_model(testing_data.tf_tensor_dict, inputs, body, run_eagerly)